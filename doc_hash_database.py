import duckdb
import os
import shutil

# Database path
DB_DIR = 'Data_Base'
DB_PATH = 'Data_Base/AGENT_DB.duckdb'

# Create directory if it doesn't exist
os.makedirs(DB_DIR, exist_ok=True)

# Clean up corrupted database files
def cleanup_database():
    files_to_remove = [
        DB_PATH,
        f'{DB_PATH}.wal',
        f'{DB_PATH}.tmp'
    ]
    for file in files_to_remove:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"Removed corrupted file: {file}")
            except Exception as e:
                print(f"Could not remove {file}: {e}")

# Try to connect, if it fails, cleanup and retry
try:
    con = duckdb.connect(DB_PATH)
except Exception as e:
    print(f"Database connection failed: {e}")
    print("Cleaning up and creating fresh database...")
    cleanup_database()
    con = duckdb.connect(DB_PATH)

def create_tables():
    # Drop existing tables if they exist
    con.execute("DROP TABLE IF EXISTS documents_db")
    con.execute("DROP TABLE IF EXISTS users_duckdb")
    
    # Drop sequences if they exist
    con.execute("DROP SEQUENCE IF EXISTS user_id_seq")
    con.execute("DROP SEQUENCE IF EXISTS doc_id_seq")
    
    # Create users_duckdb table (no sequences, no DEFAULT)
    con.execute("""
        CREATE TABLE users_duckdb (
            user_id INTEGER PRIMARY KEY,
            username VARCHAR,
            email VARCHAR,
            Password VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create documents_db table (no sequences, no DEFAULT)
    con.execute("""
        CREATE TABLE documents_db (
            doc_id INTEGER PRIMARY KEY,
            Document_Hash VARCHAR,
            user_id INTEGER,
            title VARCHAR,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users_duckdb(user_id)
        )
    """)

def new_user(username, password, email):
    # Get the next available user_id
    result = con.execute("SELECT COALESCE(MAX(user_id), 0) + 1 FROM users_duckdb").fetchone()
    new_user_id = result[0]
    
    # Insert with explicit user_id
    con.execute("""
        INSERT INTO users_duckdb (user_id, username, Password, email) 
        VALUES (?, ?, ?, ?)
    """, [new_user_id, username, password, email])
    
    return new_user_id

def add_document(doc_hash, user_id, title, content):
    # Get the next available doc_id
    result = con.execute("SELECT COALESCE(MAX(doc_id), 0) + 1 FROM documents_db").fetchone()
    new_doc_id = result[0]
    
    # Insert with explicit doc_id
    con.execute("""
        INSERT INTO documents_db (doc_id, Document_Hash, user_id, title, content) 
        VALUES (?, ?, ?, ?, ?)
    """, [new_doc_id, doc_hash, user_id, title, content])
    
    return new_doc_id

def get_user_documents(user_id):
    """Get all documents for a specific user"""
    return con.execute("""
        SELECT doc_id, Document_Hash, title, content, created_at 
        FROM documents_db 
        WHERE user_id = ?
    """, [user_id]).fetchall()

def get_user_document_hashes(user_id):
    """Get all document hashes for a specific user"""
    result = con.execute("""
        SELECT Document_Hash 
        FROM documents_db 
        WHERE user_id = ?
    """, [user_id]).fetchall()
    
    return [row[0] for row in result]