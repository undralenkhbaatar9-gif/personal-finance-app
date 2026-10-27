import streamlit as st
import sqlite3
import os
import pandas as pd

st.set_page_config(
    page_title="Personal Finance / Хувийн санхүү",
    page_icon="💰",
    layout="wide"
)

# --- CUBAAGOL DEMNGAL (Language Selector) e Sidebar ---
st.sidebar.markdown("### 🌐 Ɗemngal / Language")
lang = st.sidebar.selectbox("Select Language", ["Монгол", "English"], label_visibility="collapsed")

# 🌙 Dark Glassmorphism CSS (Ngam laabtinde sidebar e background fof ɓaleejo)
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    /* Sidebar daneejo o huppitugo ɓaleejo */
    [data-testid="stSidebar"] {
        background-color: #1e222d !important;
    }
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] a {
        color: #ffffff !important;
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
""", unsafe_allow_html=True)

# --- ƊEMNGAL (Text translations based on selection) ---
if lang == "Монгол":
    title_text = "💸 Санхүүгийн хяналтын самбар"
    sub_text = "Таны орлого, зарлага болон санхүүгийн ерөнхий дүр зураг."
    income_label = "НИЙТ ОРЛОГО"
    expense_label = "НИЙТ ЗАРЛАГА"
    balance_label = "ЦЭВЭР ҮЛДЭГДЭЛ"
    welcome_title = "📌 Тавтай морилно уу!"
    welcome_desc = "Зүүн талын цэснээс хуулга импортлох хэсгийг сонгож банкны хуулгаа оруулж эхлэнэ үү."
else:
    title_text = "💸 Financial Dashboard"
    sub_text = "Your income, expenses, and overall financial overview."
    income_label = "TOTAL INCOME"
    expense_label = "TOTAL EXPENSE"
    balance_label = "NET BALANCE"
    welcome_title = "📌 Welcome!"
    welcome_desc = "Select the import section from the sidebar to upload your bank statement."

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "finance.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Header
st.title(title_text)
st.markdown(sub_text)
st.markdown("---")

# Fetch data
try:
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM transactions", conn)
    conn.close()
except Exception:
    df = pd.DataFrame()

total_income = 0.0
total_expense = 0.0

if not df.empty and "amount" in df.columns and "type" in df.columns:
    total_income = df[df["type"] == "Орлого"]["amount"].sum()
    total_expense = df[df["type"] == "Зарлага"]["amount"].sum()

balance = total_income - total_expense

# KPI Cards
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <p style="color: #94a3b8; font-size: 14px; margin-bottom: 5px;">{income_label}</p>
        <h2 style="color: #34d399; margin-top: 0; font-weight: 700;">{total_income:,.0f} ₮</h2>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <p style="color: #94a3b8; font-size: 14px; margin-bottom: 5px;">{expense_label}</p>
        <h2 style="color: #f87171; margin-top: 0; font-weight: 700;">{total_expense:,.0f} ₮</h2>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <p style="color: #94a3b8; font-size: 14px; margin-bottom: 5px;">{balance_label}</p>
        <h2 style="color: #60a5fa; margin-top: 0; font-weight: 700;">{balance:,.0f} ₮</h2>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

if not df.empty and "type" in df.columns:
    chart_col, table_col = st.columns([1.2, 1.8])

    with chart_col:
        st.markdown(f"""<div class="glass-card">
        <h4>📊 {"Зардлын ангилал" if lang=="Монгол" else "Expense Categories"}</h4>""", unsafe_allow_html=True)
        expense_df = df[df["type"] == "Зарлага"]
        if not expense_df.empty and "category" in expense_df.columns:
            cat_sum = expense_df.groupby("category")["amount"].sum()
            st.bar_chart(cat_sum)
        else:
            st.info("No expense data available." if lang=="English" else "Зардлын мэдээлэл одоогоор алга байна.")
        st.markdown("</div>", unsafe_allow_html=True)

    with table_col:
        st.markdown(f"""<div class="glass-card">
        <h4>🕒 {"Сүүлд хийгдсэн гүйлгээ" if lang=="Монгол" else "Recent Transactions"}</h4>""", unsafe_allow_html=True)
        available_cols = [col for col in ["date", "bank_name", "description", "amount", "type"] if col in df.columns]
        st.dataframe(df[available_cols].tail(5), use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)
else:
    st.markdown(f"""
        <div class="glass-card" style="text-align: center; padding: 40px;">
            <h3>{welcome_title}</h3>
            <p style="color: #94a3b8;">{welcome_desc}</p>
        </div>
    """, unsafe_allow_html=True)