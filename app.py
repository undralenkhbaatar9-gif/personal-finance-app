import streamlit as st
import sqlite3
import os
import pandas as pd

st.set_page_config(
    page_title="Хувийн санхүү",
    page_icon="💰",
    layout="wide"
)

# 🌙 Dark Glassmorphism загвар
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Өгөгдлийн сангийн холболт
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "finance.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    try:
        conn = get_connection()
        cursor = conn.cursor()
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
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"DB Error: {e}")

init_db()

# 📊 Dashboard (Нүүр хуудас)
st.title("💸 Хувийн санхүү - Хяналтын самбар")
st.markdown("Банкны хуулгаа импортолж, орлого зарлагаа хялбар бөгөөд ойлгомжтойгоор хянаарай.")

st.markdown("""
    <div class="glass-card">
        <h3>📌 Тавтай морилно уу!</h3>
        <p>Зүүн талын цэснээс <b>Хуулга импортлох</b> болон бусад хэсгийг сонгон ажиллана уу.</p>
    </div>
""", unsafe_allow_html=True)