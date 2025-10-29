# product_model.py

def create_product_table():
    """Creates the Products table if it does not exist."""
    # Import locally to avoid circular dependency
    from app import get_db_connection 
    
    conn = get_db_connection()
    if conn is None:
        print("FATAL: Could not connect to DB for table creation.")
        return False

    cur = conn.cursor()
    try:
        # SQL to create the Products table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Products (
                product_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                sku VARCHAR(50) UNIQUE NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                quantity INT NOT NULL DEFAULT 0,
                supplier_id INT,
                status VARCHAR(20) DEFAULT 'Active',
                description TEXT,
                -- ADD THIS LINE: Foreign Key link to the Suppliers table
                FOREIGN KEY (supplier_id) REFERENCES Suppliers(supplier_id)
                    ON DELETE SET NULL
            );
        """)
        conn.commit()
        print("SUCCESS: Products table created (or already existed).")
        return True
    except Exception as e:
        print(f"ERROR: Failed to execute table creation SQL: {e}")
        return False
    finally:
        cur.close()
        conn.close()
