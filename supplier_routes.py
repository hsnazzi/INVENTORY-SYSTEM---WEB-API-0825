from flask import Blueprint, request, jsonify


supplier_bp = Blueprint('supplier_routes', __name__, url_prefix='/api/suppliers')


def get_db_connection_local():
    """Import and return connection function locally to avoid circular import issues."""
    
    from app import get_db_connection
    return get_db_connection()


@supplier_bp.route('/', methods=['GET'])
def get_suppliers():
    """
    Retrieves all suppliers and nests a list of their associated products 
    (showing only ID and Name) within each supplier record.
    """
    conn = get_db_connection_local()
    if conn is None:
        return jsonify({'error': 'Database connection failed.'}), 500
    
    
    cur = conn.cursor(dictionary=True)
    try:
        
        cur.execute("SELECT * FROM Suppliers")
        suppliers = cur.fetchall()

        
        for supplier in suppliers:
            supplier_id = supplier['supplier_id']
            
            
            product_query = """
                SELECT product_id, name 
                FROM Products 
                WHERE supplier_id = %s
            """
            
           
            product_cur = conn.cursor(dictionary=True)
            product_cur.execute(product_query, (supplier_id,))
            
            
            supplier['products'] = product_cur.fetchall()
            
            product_cur.close()

        return jsonify(suppliers), 200
        
    except Exception as e:
        return jsonify({'error': 'Could not fetch suppliers or related products.', 'details': str(e)}), 500
    finally:
        cur.close()
        conn.close()


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


@supplier_bp.route('/<int:supplier_id>', methods=['PUT'])
def update_supplier(supplier_id):
    """Updates supplier contact details."""
    data = request.get_json()
    
    conn = get_db_connection_local()
    if conn is None:
        return jsonify({'error': 'Database connection failed.'}), 500

    cur = conn.cursor()
    try:
        
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


@supplier_bp.route('/<int:supplier_id>', methods=['DELETE'])
def delete_supplier(supplier_id):
    """Deletes a supplier record."""
    conn = get_db_connection_local()
    if conn is None:
        return jsonify({'error': 'Database connection failed.'}), 500

    cur = conn.cursor()
    try:
        
        cur.execute("DELETE FROM Suppliers WHERE supplier_id = %s", [supplier_id])
        
        if cur.rowcount == 0:
            return jsonify({'message': 'Supplier not found.'}), 404
            
        conn.commit()
        return jsonify({'message': f'Supplier {supplier_id} deleted successfully.'}), 204 
    except Exception as e:
        return jsonify({'error': 'Failed to delete supplier.', 'details': str(e)}), 500
    finally:
        cur.close()
        conn.close()
