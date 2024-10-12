import sqlite3

# Function to initialize the SQLite database
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Create Symptoms Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS symptoms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        symptom TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
