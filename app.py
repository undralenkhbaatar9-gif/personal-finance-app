import streamlit as st
import sqlite3
import os

# Хуудасны ерөнхий тохиргоо (Glassmorphism загвар)
st.set_page_config(
    page_title="Хувийн санхүү",
    page_icon="💰",
    layout="wide"
)

# Өгөгдлийн сангийн зам
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "finance.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Гарчиг болон дизайн
st.title("💸 Хувийн санхүү")
st.write("Банкны хуулгаа импортолж, ангилж, тайлангаа хянаарай.")

# Өгөгдлийн сантай холбогдож байгаа эсэхийг шалгах хэсэг
try:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()
    
    st.success("✅ Өгөгдлийн сантай амжилттай холбогдлоо!")
    
    # Товчлуурууд болон үндсэн хэсэг
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.button("📄 Хуулга импортлох", use_container_width=True)
    with col2:
        st.button("🗂️ Гүйлгээ ангилах", use_container_width=True)
    with col3:
        st.button("📊 Бүх гүйлгээ", use_container_width=True)
    with col4:
        st.button("📈 Тайлан мэдээ", use_container_width=True)
        
    st.markdown("---")
    st.info("Та зүүн талын цэснээс (эсвэл дээрх товчлууруудаас) хүссэн хэсгээ сонгон санхүүгээ удирдаарай.")

except Exception as e:
    st.error(f"⚠️ Өгөгдлийн сантай холбогдож чадсангүй. Алдаа: {e}")