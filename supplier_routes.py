from flask import Blueprint, request, jsonify
# REMOVED: from app import get_db_connection (to fix circular import)

supplier_bp = Blueprint('supplier_routes', __name__, url_prefix='/api/suppliers')

# --- Helper function to ensure consistent connection logic ---
def get_db_connection_local():
    """Import and return connection function locally to avoid circular import issues."""
    # The actual import happens only when this function is called, avoiding the startup loop.
    from app import get_db_connection
    return get_db_connection()

# --------------------
# R (Read) - GET SUPPLIER LIST WITH NESTED PRODUCTS (Member 2's Report Logic)
# --------------------
@supplier_bp.route('/', methods=['GET'])
def get_suppliers():
    """
    Retrieves all suppliers and nests a list of their associated products 
    (showing only ID and Name) within each supplier record.
    """
    conn = get_db_connection_local()
    if conn is None:
        return jsonify({'error': 'Database connection failed.'}), 500
    
    # 1. Fetch all suppliers
    cur = conn.cursor(dictionary=True)
    try:
        # We don't need to commit, just read
        cur.execute("SELECT * FROM Suppliers")
        suppliers = cur.fetchall()

        # 2. Loop through each supplier and fetch their products
        for supplier in suppliers:
            supplier_id = supplier['supplier_id']
            
            # **MODIFIED QUERY HERE:** Only select product_id and name
            product_query = """
                SELECT product_id, name 
                FROM Products 
                WHERE supplier_id = %s
            """
            
            # Use a new cursor or execute sequentially
            product_cur = conn.cursor(dictionary=True)
            product_cur.execute(product_query, (supplier_id,))
            
            # Nest the simplified product list inside the supplier object
            supplier['products'] = product_cur.fetchall()
            
            product_cur.close()

        return jsonify(suppliers), 200
        
    except Exception as e:
        return jsonify({'error': 'Could not fetch suppliers or related products.', 'details': str(e)}), 500
    finally:
        cur.close()
        conn.close()

# --------------------
# C (Create) - POST NEW SUPPLIER
# --------------------
@supplier_bp.route('/', methods=['POST'])
def add_supplier():
    """Adds a new supplier record to the database."""
    data = request.get_json()
    
    required_fields = ['name', 'contact_person', 'phone']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required supplier fields (name, contact_person, phone).'}), 400

    conn = get_db_connection_local()
    if conn is None:
        return jsonify({'error': 'Database connection failed.'}), 500
        
    cur = conn.cursor()
    try:
        sql = """INSERT INTO Suppliers (name, contact_person, phone, email, address) 
                 VALUES (%s, %s, %s, %s, %s)"""
        
        values = (
            data['name'], 
            data['contact_person'], 
            data['phone'], 
            data.get('email'),
            data.get('address')
        )
        
        cur.execute(sql, values)
        conn.commit()
        
        return jsonify({'message': 'Supplier created successfully', 'id': cur.lastrowid}), 201
    except Exception as e:
        return jsonify({'error': 'Failed to add supplier.', 'details': str(e)}), 500
    finally:
        cur.close()
        conn.close()

# --------------------
# U (Update) - PUT SUPPLIER DETAILS
# --------------------
@supplier_bp.route('/<int:supplier_id>', methods=['PUT'])
def update_supplier(supplier_id):
    """Updates supplier contact details."""
    data = request.get_json()
    
    conn = get_db_connection_local()
    if conn is None:
        return jsonify({'error': 'Database connection failed.'}), 500

    cur = conn.cursor()
    try:
        # Simple update logic: only update fields provided in the JSON body
        fields_to_update = []
        values = []
        
        if 'name' in data:
            fields_to_update.append("name = %s")
            values.append(data['name'])
        if 'contact_person' in data:
            fields_to_update.append("contact_person = %s")
            values.append(data['contact_person'])
        if 'phone' in data:
            fields_to_update.append("phone = %s")
            values.append(data['phone'])
        if 'email' in data:
            fields_to_update.append("email = %s")
            values.append(data['email'])
        if 'address' in data:
            fields_to_update.append("address = %s")
            values.append(data['address'])

        if not fields_to_update:
            return jsonify({'error': 'No valid fields provided for update.'}), 400

        sql = f"UPDATE Suppliers SET {', '.join(fields_to_update)} WHERE supplier_id = %s"
        values.append(supplier_id)
        
        cur.execute(sql, values)
        
        if cur.rowcount == 0:
            return jsonify({'message': 'Supplier not found or no changes made.'}), 404
            
        conn.commit()
        return jsonify({'message': f'Supplier {supplier_id} updated successfully.'}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to update supplier.', 'details': str(e)}), 500
    finally:
        cur.close()
        conn.close()

# --------------------
# D (Delete) - DELETE SUPPLIER
# --------------------
@supplier_bp.route('/<int:supplier_id>', methods=['DELETE'])
def delete_supplier(supplier_id):
    """Deletes a supplier record."""
    conn = get_db_connection_local()
    if conn is None:
        return jsonify({'error': 'Database connection failed.'}), 500

    cur = conn.cursor()
    try:
        # Note: Due to the FOREIGN KEY ON DELETE SET NULL constraint in the Products table,
        # deleting a supplier will automatically set the supplier_id field to NULL 
        # for any related products, ensuring data integrity.
        cur.execute("DELETE FROM Suppliers WHERE supplier_id = %s", [supplier_id])
        
        if cur.rowcount == 0:
            return jsonify({'message': 'Supplier not found.'}), 404
            
        conn.commit()
        return jsonify({'message': f'Supplier {supplier_id} deleted successfully.'}), 204 # 204 No Content
    except Exception as e:
        return jsonify({'error': 'Failed to delete supplier.', 'details': str(e)}), 500
    finally:
        cur.close()
        conn.close()
