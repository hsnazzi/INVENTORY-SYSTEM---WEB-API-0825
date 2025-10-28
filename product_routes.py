# product_routes.py

from flask import Blueprint, request, jsonify # Only essential imports at the top

product_bp = Blueprint('product_routes', __name__, url_prefix='/api/products')

# --------------------
# R (Read) - MASTER LIST (Your View Report Page)
# --------------------
@product_bp.route('/', methods=['GET'])
def get_products():
    from app import get_db_connection # Import locally to prevent circular error
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed.'}), 500
    
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT * FROM Products")
        products = cur.fetchall()
        return jsonify(products), 200
    except Exception as e:
        return jsonify({'error': 'Could not fetch products.', 'details': str(e)}), 500
    finally:
        cur.close()
        conn.close()

# --------------------
# C (Create) - NEW PRODUCT ENTRY (Your Form Page 1)
# --------------------
@product_bp.route('/', methods=['POST'])
def add_product():
    from app import get_db_connection # Import locally
    """Adds a new product to the database."""
    data = request.get_json()
    
    required_fields = ['name', 'sku', 'price', 'quantity']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields (name, sku, price, quantity).'}), 400

    conn = get_db_connection()
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
            data.get('supplier_id'), # Optional
            data.get('status', 'Active'),
            data.get('description') # Optional
        )
        
        cur.execute(sql, values)
        conn.commit()
        
        return jsonify({'message': 'Product created successfully', 'id': cur.lastrowid}), 201
    except Exception as e:
        return jsonify({'error': 'Failed to add product.', 'details': str(e)}), 500
    finally:
        cur.close()
        conn.close()

# --------------------
# U (Update) - PRODUCT STATUS (Your Form Page 2)
# --------------------
@product_bp.route('/<int:product_id>', methods=['PUT'])
def update_product_status(product_id):
    from app import get_db_connection # Import locally
    """Updates the product status (e.g., Active/Discontinued)."""
    data = request.get_json()
    status = data.get('status')
    
    if not status:
        return jsonify({'error': 'Missing status field for update.'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed.'}), 500

    cur = conn.cursor()
    try:
        sql = "UPDATE Products SET status = %s WHERE product_id = %s"
        cur.execute(sql, (status, product_id))
        
        if cur.rowcount == 0:
            return jsonify({'message': 'Product not found or status already updated.'}), 404
            
        conn.commit()
        return jsonify({'message': f'Product {product_id} status updated to {status}.'}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to update product status.', 'details': str(e)}), 500
    finally:
        cur.close()
        conn.close()


# --------------------
# D (Delete) - PRODUCT DELETION
# --------------------
@product_bp.route('/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    from app import get_db_connection # Import locally
    """Deletes a product record."""
    conn = get_db_connection()
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
