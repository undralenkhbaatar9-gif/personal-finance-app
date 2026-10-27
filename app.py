import streamlit as st
import sqlite3
import os
import pandas as pd

st.set_page_config(
    page_title="Хувийн санхүү",
    page_icon="💰",
    layout="wide"
)

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
    /* File uploader styling fix */
    [data-testid="stFileUploader"] {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 10px;
        padding: 15px;
    }
    [data-testid="stFileUploader"] section {
        background-color: transparent;
    }
    [data-testid="stFileUploader"] span, [data-testid="stFileUploader"] small, [data-testid="stFileUploader"] div {
        color: #ffffff !important;
    }
    /* Upload button explicit color fix */
    [data-testid="stFileUploader"] button {
        color: #000000 !important;
        background-color: #f8fafc !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

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

st.title("💸 Хувийн санхүү")
st.markdown("Банкны хуулгаа импортолж, ангилж, тайлангаа хялбар бөгөөд ойлгомжтойгоор хянаарай.")

try:
    if 'menu' not in st.session_state:
        st.session_state.menu = "Нүүр"

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("📄 Хуулга импортлох", use_container_width=True):
            st.session_state.menu = "Импорт"
    with col2:
        if st.button("🗂️ Гүйлгээ ангилах", use_container_width=True):
            st.session_state.menu = "Ангилах"
    with col3:
        if st.button("📊 Бүх гүйлгээ", use_container_width=True):
            st.session_state.menu = "Гүйлгээ"
    with col4:
        if st.button("📈 Тайлан мэдээ", use_container_width=True):
            st.session_state.menu = "Тайлан"
        
    st.markdown("---")

    if st.session_state.menu == "Нүүр":
        st.markdown("""
            <div class="glass-card">
                <h3>📌 Ашиглах зөвлөмж</h3>
                <p>Дээрх товчлууруудыг ашиглан банкны хуулгаа оруулж, орлого зарлагаа хянаж, сарын тайлангаа хараарай.</p>
            </div>
        """, unsafe_allow_html=True)

    elif st.session_state.menu == "Импорт":
        st.markdown("### 📄 Банкны хуулга импортлох")
        bank = st.selectbox("Банк сонгох", ["Хаан банк", "Голомт банк", "Хас банк", "Төрийн банк"])
        uploaded_file = st.file_uploader(f"{bank}-ны хуулгаа сонгоно уу (Excel, CSV)", type=["xlsx", "csv"])
        
        if uploaded_file is not None:
            st.success(f"📂 Файл амжилттай орж ирлээ: {uploaded_file.name}")
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.write("📋 Уншсан файлын мэдээлэл (Урьдчилсан харагдац):")
                st.dataframe(df.head(), use_container_width=True)
                
                if st.button("💾 Өгөгдлийн санд хадгалах"):
                    st.success("✅ Хуулга амжилттай өгөгдлийн санд хадгалагдлаа!")
            except Exception as ex:
                st.error(f"Файлыг унших явцад алдаа гарлаа: {ex}")

    elif st.session_state.menu == "Ангилах":
        st.markdown("### 🗂️ Гүйлгээ ангилах")
        st.info("Орлого болон зарлагын гүйлгээг категориор ангилах хэсэг.")

    elif st.session_state.menu == "Гүйлгээ":
        st.markdown("### 📊 Бүх гүйлгээний жагсаалт")
        conn = get_connection()
        df_trans = pd.read_sql("SELECT * FROM transactions", conn)
        conn.close()
        if not df_trans.empty:
            st.dataframe(df_trans, use_container_width=True)
        else:
            st.info("Өгөгдлийн санд одоогоор гүйлгээ бүртгэгдээгүй байна.")

    elif st.session_state.menu == "Тайлан":
        st.markdown("### 📈 Санхүүгийн тайлан мэдээ")
        st.info("Сарын орлого, зарлагын график болон нэгдсэн тайлан харах хэсэг.")

except Exception as e:
    st.error(f"⚠️ Аппликейшн ажиллахад алдаа гарлаа: {e}")