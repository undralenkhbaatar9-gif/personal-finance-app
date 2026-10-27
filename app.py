import streamlit as st
import sqlite3
import os
import pandas as pd

st.set_page_config(
    page_title="Хувийн санхүү",
    page_icon="💰",
    layout="wide"
)

# 🌙 Dark Glassmorphism загвар болон сайжруулсан Dashboard CSS
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    .metric-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(168, 85, 247, 0.1) 100%);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 14px;
        padding: 20px;
        text-align: center;
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
st.markdown("---")

# Өгөгдлийн санзраас мэдээлэл татаж авах
try:
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM transactions", conn)
    conn.close()
except:
    df = pd.DataFrame()

# KPI Metric картууд
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <div class="metric-card">
            <h4 style="color: #94a3b8; margin-bottom: 5px;">Нийт орлого</h4>
            <h2 style="color: #34d399; margin-top: 0;">0 ₮</h2>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="metric-card">
            <h4 style="color: #94a3b8; margin-bottom: 5px;">Нийт зарлага</h4>
            <h2 style="color: #f87171; margin-top: 0;">0 ₮</h2>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class="metric-card">
            <h4 style="color: #94a3b8; margin-bottom: 5px;">Үлдэгдэл</h4>
            <h2 style="color: #60a5fa; margin-top: 0;">0 ₮</h2>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
    <div class="glass-card">
        <h3>📌 Тавтай морилно уу!</h3>
        <p>Зүүн талын цэснээс <b>1_📄_Хуулга_импортлох</b> хэсгийг сонгож банкны хуулгаа оруулж эхлэнэ үү.</p>
    </div>
""", unsafe_allow_html=True)