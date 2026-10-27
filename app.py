import os
import sqlite3
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Хувийн санхүү - Хяналтын самбар", page_icon="💰", layout="wide"
)

# 🌙 Dark Glassmorphism загвар болон UI стилиуд
st.markdown(
    """
<style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    .metric-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }
</style>
""",
    unsafe_allow_html=True,
)

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
    # Хүснэгт байхгүй бол үүсгэнэ
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                type TEXT NOT NULL,
                category TEXT DEFAULT 'Ангилаагүй',
                bank_name TEXT DEFAULT 'Үндсэн банк'
            )
        """)
    conn.commit()
    conn.close()
  except Exception as e:
    print(f"DB Error: {e}")


init_db()

# --- HEADER SECTION ---
st.title("💸 Санхүүгийн хяналтын самбар")
st.markdown("Таны орлого, зарлага болон санхүүгийн ерөнхий дүр зураг.")
st.markdown("---")

# Өгөгдлийн санзраас мэдээлэл татаж авах
try:
  conn = get_connection()
  df = pd.read_sql("SELECT * FROM transactions", conn)
  conn.close()
except Exception:
  df = pd.DataFrame()

# Нийт орлого, зарлага болон үлдэгдлийг тооцоолох
total_income = 0.0
total_expense = 0.0

if not df.empty and "amount" in df.columns and "type" in df.columns:
  total_income = df[df["type"] == "Орлого"]["amount"].sum()
  total_expense = df[df["type"] == "Зарлага"]["amount"].sum()

balance = total_income - total_expense

# --- KPI METRIC CARDS ---
col1, col2, col3 = st.columns(3)

with col1:
  st.markdown(
      f"""
    <div class="metric-card">
        <p style="color: #94a3b8; font-size: 14px; margin-bottom: 5px;">НИЙТ ОРЛОГО</p>
        <h2 style="color: #34d399; margin-top: 0; font-weight: 700;">{total_income:,.0f} ₮</h2>
    </div>
    """,
      unsafe_allow_html=True,
  )

with col2:
  st.markdown(
      f"""
    <div class="metric-card">
        <p style="color: #94a3b8; font-size: 14px; margin-bottom: 5px;">НИЙТ ЗАРЛАГА</p>
        <h2 style="color: #f87171; margin-top: 0; font-weight: 700;">{total_expense:,.0f} ₮</h2>
    </div>
    """,
      unsafe_allow_html=True,
  )

with col3:
  st.markdown(
      f"""
    <div class="metric-card">
        <p style="color: #94a3b8; font-size: 14px; margin-bottom: 5px;">ЦЭВЭР ҮЛДЭГДЭЛ</p>
        <h2 style="color: #60a5fa; margin-top: 0; font-weight: 700;">{balance:,.0f} ₮</h2>
    </div>
    """,
      unsafe_allow_html=True,
  )

st.markdown("<br>", unsafe_allow_html=True)

# --- VISUAL ANALYTICS & TABLES ---
if not df.empty and "type" in df.columns:
  chart_col, table_col = st.columns([1.2, 1.8])

  with chart_col:
    st.markdown(
        """<div class="glass-card">
        <h4>📊 Зардлын ангилал</h4>""",
        unsafe_allow_html=True,
    )
    expense_df = df[df["type"] == "Зарлага"]
    if not expense_df.empty and "category" in expense_df.columns:
      cat_sum = expense_df.groupby("category")["amount"].sum()
      st.bar_chart(cat_sum)
    else:
      st.info("Зардлын мэдээлэл одоогоор алга байна.")
    st.markdown("</div>", unsafe_allow_html=True)

  with table_col:
    st.markdown(
        """<div class="glass-card">
        <h4>🕒 Сүүлд хийгдсэн гүйлгээ</h4>""",
        unsafe_allow_html=True,
    )
    available_cols = [
        col
        for col in ["date", "bank_name", "description", "amount", "type"]
        if col in df.columns
    ]
    st.dataframe(
        df[available_cols].tail(5), use_container_width=True, hide_index=True
    )
    st.markdown("</div>", unsafe_allow_html=True)
else:
  st.markdown(
      """
        <div class="glass-card" style="text-align: center; padding: 40px;">
            <h3>👋 Тавтай морилно уу!</h3>
            <p style="color: #94a3b8;">Одоогоор өгөгдлийн сан хоосон эсвэл шинэчлэгдсэн байна. Зүүн талын цэснээс <b>1_📄_Хуулга_импортлох</b> хэсгийг сонгож банкны хуулгаа оруулж эхлэнэ үү.</p>
        </div>
    """,
      unsafe_allow_html=True,
  )