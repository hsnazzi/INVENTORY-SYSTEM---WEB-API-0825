from flask import Flask, jsonify
import mysql.connector 
from flask_cors import CORS # Needed for browser security fix

# --- 1. Flask App Initialization (MUST come first) ---
app = Flask(__name__)
CORS(app) # <--- Apply CORS to allow your HTML frontend to connect

# --- 2. App Configuration ---
app.config['SECRET_KEY'] = 'a_very_secret_key_for_sessions'
app.url_map.strict_slashes = False # Fixes the 'Not Found' error for different slash endings

# --- 3. Database Connection Function ---
def get_db_connection():
    """Returns a new MySQL connection object using the root user and the set password."""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            port=3306,               
            user='root',
            password='webAPI0825',  # Use the password you successfully set/reset
            database='UPTM_InventoryDB' 
        )
        return conn
    except mysql.connector.Error as err:
        # This will print the error if the connection fails (e.g., server is down)
        print(f"Database Connection Error: {err}")
        return None

# --- NEW: Root Route (Handles the 404) ---
@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Welcome to the Inventory API! Please access the frontend index.html file to view the application, or use /api/products for raw data."}), 200

# --- 4. Import and Register Blueprints ---
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
    # Running with host='0.0.0.0' allows external access (for your groupmates) and better CORS handling.
    app.run(debug=True, host='0.0.0.0')
