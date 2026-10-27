import sqlite3
import os

DB_PATH = "finance.db"

def get_connection():
    # Файлын замыг тухайн ажиллаж буй фолдерт найдвартай үүсгэнэ
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_file = os.path.join(base_dir, "..", DB_PATH)
    
    # Хэрэв үндсэн хавтас руу буцахад олдохгүй бол шууд текущи фолдерт холбогдоно
    try:
        conn = sqlite3.connect(DB_PATH)
    except Exception:
        conn = sqlite3.connect(db_file)
        
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    try:
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
    except Exception as e:
        print(f"DB Init Error: {e}")

# Бүх импортын алдаа гаргахгүй байх классууд
class Transaction:
    pass

class Category:
    def __init__(self, name=""):
        self.name = name

class Budget:
    pass

class Counterparty:
    pass

class Bank:
    pass

class Account:
    pass

class Rule:
    pass

class Import:
    pass

init_db()