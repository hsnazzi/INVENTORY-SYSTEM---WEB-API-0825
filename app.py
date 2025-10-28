from flask import Flask, jsonify
import mysql.connector 

# --- 1. Flask App Initialization (MUST come first) ---
app = Flask(__name__)

# --- 2. App Configuration ---
app.config['SECRET_KEY'] = 'a_very_secret_key_for_sessions'

# --- 3. Database Connection Function ---
def get_db_connection():
    """Returns a new MySQL connection object using the root user and the set password."""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            port=3306,               
            user='root',
            password='webAPI0825',  
            database='UPTM_InventoryDB' 
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Database Connection Error: {err}")
        return None

# --- TEMPORARY SETUP: CALL TABLE CREATION FUNCTION ONCE ---
from product_model import create_product_table
create_product_table()
print("Temporary setup script executed.")
# ---------------------------------------------------------

# --- 4. Import and Register Blueprints (MUST come after 'app' is created) ---
from product_routes import product_bp 
app.register_blueprint(product_bp)

# --- 5. Test Route (Verification) ---
@app.route('/status', methods=['GET'])
def status_check():
    conn = get_db_connection()
    if conn:
        try:
            conn.close() 
            return jsonify({'message': 'API is running and successfully connected to MySQL as root!'}), 200
        except Exception as e:
            return jsonify({'message': 'API running, but MySQL connection failed during test.', 'error': str(e)}), 500
    else:
        return jsonify({'message': 'API running, but MySQL server is unreachable.'}), 500

if __name__ == '__main__':
    app.run(debug=True)

