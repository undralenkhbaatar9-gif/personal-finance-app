import streamlit as st
import sqlite3
import os

# Хуудасны ерөнхий тохиргоо (Dark Mode)
st.set_page_config(
    page_title="Хувийн санхүү",
    page_icon="💰",
    layout="wide"
)

# 🌙 Харанхуй шилэн (Dark Glassmorphism) загварууд
st.markdown("""
<style>
    /* Үндсэн дэвсгэр өнгө */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    /* Шилэн эффекттэй картууд */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    /* Товчлууруудын загвар */
    .stButton>button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        opacity: 0.9;
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# Өгөгдлийн сангийн найдвартай зам
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "finance.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Гарчиг болон тайлбар
st.title("💸 Хувийн санхүү")
st.markdown("Банкны хуулгаа импортолж, ангилж, тайлангаа хялбар бөгөөд ойлгомжтойгоор хянаарай.")

# Өгөгдлийн сантай холбогдох болон шалгах
try:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()
    
    st.success("✅ Өгөгдлийн сантай амжилттай холбогдлоо!")
    
    # Үндсэн удирдлагын товчлуурууд
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("📄 Хуулга импортлох", use_container_width=True):
            st.info("Хуулга импортлох хэсэг рүү шилжиж байна...")
    with col2:
        if st.button("🗂️ Гүйлгээ ангилах", use_container_width=True):
            st.info("Гүйлгээ ангилах хэсэг рүү шилжиж байна...")
    with col3:
        if st.button("📊 Бүх гүйлгээ", use_container_width=True):
            st.info("Бүх гүйлгээний жагсаалт руу шилжиж байна...")
    with col4:
        if st.button("📈 Тайлан мэдээ", use_container_width=True):
            st.info("Тайлан мэдээлэл рүү шилжиж байна...")
        
    st.markdown("---")
    
    # Зааварчилгаа болон мэдээллийн шилэн карт
    st.markdown("""
        <div class="glass-card">
            <h3>📌 Ашиглах зөвлөмж</h3>
            <p>Та дээрх товчлууруудыг ашиглан банкны хуулгаа оруулж, орлого зарлагаа ангилан, сарын санхүүгийн нэгдсэн тайлангаа нарийвчлан хараарай.</p>
        </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"⚠️ Өгөгдлийн сантай холбогдож чадсангүй. Алдаа: {e}")