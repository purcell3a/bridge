import os
import sqlite3

# Define the database path in the .data directory for persistence on Heroku
DATABASE_URL = os.path.join(os.getcwd(), ".data", "database.db")

# Function to initialize the SQLite database
def init_db():
    # Ensure the .data directory exists
    os.makedirs(os.path.dirname(DATABASE_URL), exist_ok=True)
    
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()

    # Drop existing tables if they exist (only for development, can be removed for production)
    cursor.execute('DROP TABLE IF EXISTS symptoms')
    cursor.execute('DROP TABLE IF EXISTS users')

    # Create Symptoms Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS symptoms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        symptom TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    ''')

    # Create Users Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE
    );
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
