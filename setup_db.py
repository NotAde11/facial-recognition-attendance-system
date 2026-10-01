import psycopg2
from psycopg2 import sql

def setup_postgres():
    db_params = {
        "user": "postgres",
        "password": "Psalm91^&",
        "host": "localhost",
        "port": "5433"
    }
    
    conn = None
    
    try:
        # STEP 1: Create Database
        conn = psycopg2.connect(dbname="postgres", **db_params)
        conn.autocommit = True
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'facial_recognition_db'")
        if not cursor.fetchone():
            cursor.execute("CREATE DATABASE facial_recognition_db")
            print("Successfully created database: facial_recognition_db")
            
        cursor.close()
        conn.close()

        # STEP 2: Create Tables with VARCHAR IDs
        conn = psycopg2.connect(dbname="facial_recognition_db", **db_params)
        cursor = conn.cursor()
        
        # We use VARCHAR(20) to hold "22CG031807"
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id VARCHAR(20) PRIMARY KEY,
                name VARCHAR(100) NOT NULL
                CONSTRAINT student_id_format CHECK (id ~ '^[0-9]{2}[A-Z]{2}[0-9]{6}$')
            );
        ''')

        # Also create daily_attendance to ensure student_id matches the new type
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_attendance (
                student_id VARCHAR(20) REFERENCES students(id),
                date DATE,
                presence VARCHAR(20),
                time_marked TIME,
                PRIMARY KEY (student_id, date)
            );
        ''')
        
        conn.commit()
        print("Successfully created/verified tables with Alphanumeric ID support!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    setup_postgres()