import sqlite3
from datetime import datetime

DB_PATH = "finance.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Банкны мэдээлэл болон ангилалтай гүйлгээний хүснэгт
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            type TEXT NOT NULL, -- 'Income' or 'Expense'
            category TEXT DEFAULT 'Ангилаагүй',
            bank_name TEXT DEFAULT 'Үндсэн банк'
        )
    ''')
    
    # Төсөв төлөвлөгөөний хүснэгт (Budget)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT UNIQUE NOT NULL,
            monthly_limit REAL NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

# Эхлүүлж шалгах
init_db()