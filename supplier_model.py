# supplier_model.py

# DO NOT import get_db_connection here globally

def create_supplier_table():
    """Creates the Suppliers table if it does not exist."""
    # Import locally to break the circular dependency
    from app import get_db_connection 
    
    conn = get_db_connection()
    if conn is None:
        return "Database connection failed."

    cur = conn.cursor()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Suppliers (
                supplier_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                contact_person VARCHAR(100),
                phone VARCHAR(20),
                email VARCHAR(100),
                address TEXT
            )
        """)
        conn.commit()
        return "Suppliers table ensured to exist."
    except Exception as e:
        print(f"Error creating Suppliers table: {e}")
        return f"Error creating Suppliers table: {e}"
    finally:
        cur.close()
        conn.close()
