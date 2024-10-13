import sqlite3

# SQLite connection function
def get_db_connection():
    conn = sqlite3.connect('database.db')
    return conn
