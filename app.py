import streamlit as st
import sqlite3
import os
import pandas as pd

st.set_page_config(
    page_title="Хувийн санхүү / Personal Finance",
    page_icon="💰",
    layout="wide"
)

# 🌐 Хэл сонгох хэсэг (Sidebar дээр байрлуулна)
st.sidebar.markdown("### 🌐 Хэл / Language")
selected_lang = st.sidebar.selectbox("Сонгох / Choose", ["Монгол", "English"])

# 📖 Хэлний үгсийн сан (Translations dictionary)
translations = {
    "Монгол": {
        "title": "💸 Хувийн санхүү",
        "desc": "Банкны хуулгаа импортолж, ангилж, тайлангаа хялбар бөгөөд ойлгомжтойгоор хянаарай.",
        "btn_import": "📄 Хуулга импортлох",
        "btn_review": "🗂️ Гүйлгээ ангилах",
        "btn_trans": "📊 Бүх гүйлгээ",
        "btn_report": "📈 Тайлан мэдээ",
        "select_bank": "Банк сонгох",
        "upload_prompt": "-ны хуулгаа сонгоно уу (Excel, CSV)",
        "save_db": "💾 Өгөгдлийн санд хадгалах",
        "success_upload": "📂 Файл амжилттай орж ирлээ: ",
        "success_save": "✅ Хуулга амжилттай өгөгдлийн санд хадгалагдлаа!",
        "no_data": "Өгөгдлийн санд одоогоор гүйлгээ бүртгэгдээгүй байна."
    },
    "English": {
        "title": "💸 Personal Finance",
        "desc": "Import bank statements, categorize, and track your financial reports easily.",
        "btn_import": "📄 Import Statement",
        "btn_review": "🗂️ Categorize",
        "btn_trans": "📊 All Transactions",
        "btn_report": "📈 Reports",
        "select_bank": "Select Bank",
        "upload_prompt": " statement file (Excel, CSV)",
        "save_db": "💾 Save to Database",
        "success_upload": "📂 File uploaded successfully: ",
        "success_save": "✅ Statement saved successfully to database!",
        "no_data": "No transactions recorded in the database yet."
    }
}

# Тухайн сонгосон хэлний үгсийг авах
t = translations[selected_lang]

# 🌙 Харанхуй шилэн (Dark Glassmorphism) загварууд
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
    [data-testid="stFileUploader"] button {
        color: #0f172a !important;
        background-color: #ffffff !important;
        font-weight: 700 !important;
        border: 1px solid #cbd5e1 !important;
    }
</style>
""", unsafe_allow_html=True)

# Өгөгдлийн сангийн зам
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

# Гарчиг болон тайлбар (Сонгосон хэлээр гарна)
st.title(t["title"])
st.markdown(t["desc"])

try:
    if 'menu' not in st.session_state:
        st.session_state.menu = "Нүүр"

    # Удирдлагын товчлуурууд
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button(t["btn_import"], use_container_width=True):
            st.session_state.menu = "Импорт"
    with col2:
        if st.button(t["btn_review"], use_container_width=True):
            st.session_state.menu = "Ангилах"
    with col3:
        if st.button(t["btn_trans"], use_container_width=True):
            st.session_state.menu = "Гүйлгээ"
    with col4:
        if st.button(t["btn_report"], use_container_width=True):
            st.session_state.menu = "Тайлан"
        
    st.markdown("---")

    if st.session_state.menu == "Нүүр":
        st.markdown(f"""
            <div class="glass-card">
                <h3>📌 Info</h3>
                <p>{t["desc"]}</p>
            </div>
        """, unsafe_allow_html=True)

    elif st.session_state.menu == "Импорт":
        st.markdown(f"### {t['btn_import']}")
        bank = st.selectbox(t["select_bank"], ["Хаан банк / Khan Bank", "Голомт банк / Golomt Bank", "Хас банк / XacBank", "Төрийн банк / State Bank"])
        uploaded_file = st.file_uploader(f"{bank}{t['upload_prompt']}", type=["xlsx", "csv"])
        
        if uploaded_file is not None:
            st.success(f"{t['success_upload']}{uploaded_file.name}")
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.dataframe(df.head(), use_container_width=True)
                
                if st.button(t["save_db"]):
                    st.success(t["success_save"])
            except Exception as ex:
                st.error(f"Error: {ex}")

    elif st.session_state.menu == "Ангилах":
        st.markdown(f"### {t['btn_review']}")
        st.info("Categorization section...")

    elif st.session_state.menu == "Гүйлгээ":
        st.markdown(f"### {t['btn_trans']}")
        conn = get_connection()
        df_trans = pd.read_sql("SELECT * FROM transactions", conn)
        conn.close()
        if not df_trans.empty:
            st.dataframe(df_trans, use_container_width=True)
        else:
            st.info(t["no_data"])

    elif st.session_state.menu == "Тайлан":
        st.markdown(f"### {t['btn_report']}")
        st.info("Reports section...")

except Exception as e:
    st.error(f"Error: {e}")