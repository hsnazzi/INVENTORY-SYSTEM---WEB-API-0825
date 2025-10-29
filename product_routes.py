from flask import Blueprint, request, jsonify


product_bp = Blueprint('product_routes', __name__, url_prefix='/api/products')


def get_db_connection_local():
    """Import and return connection function locally to avoid circular import issues."""
    from app import get_db_connection
    return get_db_connection()


@product_bp.route('/', methods=['GET'])
def get_products():
    """Retrieves the master list of all products, optionally filtered by low stock."""
    conn = get_db_connection_local()
    if conn is None:
        return jsonify({'error': 'Database connection failed.'}), 500
    
    cur = conn.cursor(dictionary=True)
    
    
    low_stock_filter = request.args.get('filter')
    
    base_sql = "SELECT * FROM Products"
    where_clause = ""
    
    
    if low_stock_filter == 'low_stock': 
        where_clause = " WHERE quantity <= 10" 
    
    try:
        cur.execute(base_sql + where_clause)
        products = cur.fetchall()
        return jsonify(products), 200
    except Exception as e:
        return jsonify({'error': 'Could not fetch products.', 'details': str(e)}), 500
    finally:
        cur.close()
        conn.close()


@product_bp.route('/', methods=['POST'])
def add_product():
    """Adds a new product record to the database."""
    data = request.get_json()
    
    required_fields = ['name', 'sku', 'price', 'quantity']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields (name, sku, price, quantity).'}), 400

    conn = get_db_connection_local()
    if conn is None:
        return jsonify({'error': 'Database connection failed.'}), 500
        
    cur = conn.cursor()
    try:
        sql = """INSERT INTO Products (name, sku, price, quantity, supplier_id, status, description) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        
        values = (
            data['name'], 
            data['sku'], 
            data['price'], 
            data['quantity'], 
            data.get('supplier_id'), 
            data.get('status', 'Active'),
            data.get('description')
        )
        
        cur.execute(sql, values)
        conn.commit()
        
        return jsonify({'message': 'Product created successfully', 'id': cur.lastrowid}), 201
    except Exception as e:
        
        return jsonify({'error': 'Failed to add product.', 'details': str(e)}), 500
    finally:
        cur.close()
        conn.close()


@product_bp.route('/<int:product_id>', methods=['PUT'])
def update_product_details(product_id):
    """Updates product details (status, price, description, etc.)."""
    data = request.get_json()
    
    conn = get_db_connection_local()
    if conn is None:
        return jsonify({'error': 'Database connection failed.'}), 500

    cur = conn.cursor()
    try:
        fields_to_update = []
        values = []

        
        if 'status' in data:
            fields_to_update.append("status = %s")
            values.append(data['status'])
        
       
        if 'price' in data:
            fields_to_update.append("price = %s")
            values.append(data['price'])
        if 'quantity' in data:
            fields_to_update.append("quantity = %s")
            values.append(data['quantity'])
        if 'description' in data:
            fields_to_update.append("description = %s")
            values.append(data['description'])

        if not fields_to_update:
            return jsonify({'error': 'No valid fields provided for update.'}), 400

        sql = f"UPDATE Products SET {', '.join(fields_to_update)} WHERE product_id = %s"
        values.append(product_id)
        
        cur.execute(sql, values)
        
        if cur.rowcount == 0:
            return jsonify({'message': 'Product not found or no changes made.'}), 404
            
        conn.commit()
        return jsonify({'message': f'Product {product_id} updated successfully.'}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to update product.', 'details': str(e)}), 500
    finally:
        cur.close()
        conn.close()



@product_bp.route('/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Deletes a product record."""
    conn = get_db_connection_local()
    if conn is None:
        return jsonify({'error': 'Database connection failed.'}), 500

    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM Products WHERE product_id = %s", [product_id])
        
        if cur.rowcount == 0:
            return jsonify({'message': 'Product not found.'}), 404
            
        conn.commit()
        return jsonify({'message': f'Product {product_id} deleted successfully.'}), 204 # 204 No Content
    except Exception as e:
        return jsonify({'error': 'Failed to delete product.', 'details': str(e)}), 500
    finally:
        cur.close()
        conn.close()
