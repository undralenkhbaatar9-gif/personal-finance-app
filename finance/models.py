import sqlite3
import os

DB_PATH = "finance.db"

def get_connection():
    # Файлын зам алдагдахаас сэргийлж бүтэн замыг автоматаар үүсгэнэ
    db_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Гүйлгээний хүснэгт
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            type TEXT NOT NULL,
            category TEXT DEFAULT 'Ангилаагүй',
            bank_name TEXT DEFAULT 'Үндсэн банк'
        )
    ''')
    
    # Төсвийн хүснэгт
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT UNIQUE NOT NULL,
            monthly_limit REAL NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

# Загвар классууд
class Category:
    def __init__(self, name=""):
        self.name = name

class Transaction:
    pass

class Budget:
    pass

init_db()