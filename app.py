import sqlite3
import os

# Өгөгдлийн сангийн үнэн зөв замыг зааж өгөх
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "finance.db")

def check_db_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()
        return True, tables
    except Exception as e:
        return False, str(e)