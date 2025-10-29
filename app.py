from flask import Flask, jsonify
import mysql.connector
from flask_cors import CORS  



app = Flask(__name__)
CORS(app)  


app.config['SECRET_KEY'] = 'a_very_secret_key_for_sessions'
app.url_map.strict_slashes = False 


def get_db_connection():
    """Returns a new MySQL connection object using the root user and the set password."""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='webAPI0825',  #PASS NEED TO BE THE SAME FOR EVERYONE
            database='UPTM_InventoryDB'
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Database Connection Error: {err}")
        return None


@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "message": "Welcome to the Inventory API! Please access the frontend index.html file to view the application, or use /api/products for raw data."
    }), 200


from product_routes import product_bp
from supplier_routes import supplier_bp

app.register_blueprint(product_bp)
app.register_blueprint(supplier_bp)


@app.route('/status', methods=['GET'])
def status_check():
    conn = get_db_connection()
    if conn:
        try:
            conn.close()
            return jsonify({'message': 'API is running and successfully connected to MySQL as root!'}), 200
        except Exception as e:
            return jsonify({
                'message': 'API running, but MySQL connection failed during test.',
                'error': str(e)
            }), 500
    else:
        return jsonify({'message': 'API running, but MySQL server is unreachable.'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
