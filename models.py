import sqlite3

# Function to initialize the SQLite database
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Drop existing tables if they exist
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


    # Create table for storing user details
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
