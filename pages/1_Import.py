import os
import sqlite3
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Хуулга импортлох", page_icon="📄", layout="wide"
)

# --- ХЭЛ СОНГОГЧ (Sidebar) ---
st.sidebar.markdown("### 🌐 Дэлгэцийн хэл / Language")
lang = st.sidebar.selectbox(
    "Хэл сонгох", ["Монгол", "English"], label_visibility="collapsed"
)

# 🌙 Dark Glassmorphism загвар
st.markdown(
    """
<style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    /* Sidebar-ыг хар өнгөтэй байлгах */
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
    
    /* File Uploader загвар */
    [data-testid="stFileUploader"] {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px;
        padding: 20px;
    }
    [data-testid="stFileUploader"] section {
        background-color: transparent !important;
    }
    [data-testid="stFileUploader"] div, 
    [data-testid="stFileUploader"] span, 
    [data-testid="stFileUploader"] small, 
    [data-testid="stFileUploader"] p {
        color: #ffffff !important;
    }
    [data-testid="stFileUploader"] button {
        color: #ffffff !important;
        background-color: #1e222d !important;
        font-weight: 600 !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
    }
    [data-testid="stFileUploader"] button:hover {
        background-color: #2b2d31 !important;
        border-color: #10B981 !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# --- ОРЧУУЛГА ---
if lang == "Монгол":
  title_text = "📄 Банкны хуулга импортлох"
  bank_label = "Банк сонгох"
  file_label_text = "{bank}-ны хуулгаа сонгоно уу (Excel, CSV)"
  success_file = "📂 Файл амжилттай орж ирлээ: "
  preview_text = "📋 Уншсан файлын мэдээлэл (Урьдчилсан харагдац):"
  save_btn = "💾 Өгөгдлийн санд хадгалах"
  save_success = (
      "✅ Нийт {count} гүйлгээ амжилттай өгөгдлийн санд хадгалагдлаа!"
  )
  prev_imports = "Өмнөх импортууд"
  no_history = "Импортын түүхийг одоогоор харуулах боломжгүй байна."
else:
  title_text = "📄 Import Bank Statement"
  bank_label = "Select Bank"
  file_label_text = "Select {bank} statement file (Excel, CSV)"
  success_file = "📂 File successfully loaded: "
  preview_text = "📋 File Preview:"
  save_btn = "💾 Save to Database"
  save_success = "✅ Total {count} transactions successfully saved!"
  prev_imports = "Previous Imports"
  no_history = "Import history is currently unavailable."

# Database path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "finance.db")


def get_connection():
  conn = sqlite3.connect(DB_PATH)
  conn.row_factory = sqlite3.Row
  return conn


st.markdown(f"### {title_text}")

bank_options = [
    "Хаан банк",
    "Голомт банк",
    "Хас банк",
    "Төрийн банк",
    "ХХБ (Худалдаа хөгжлийн банк)",
    "Ариг банк",
    "Богд банк",
]

bank = st.selectbox(bank_label, bank_options)

uploaded_file = st.file_uploader(file_label_text.format(bank=bank), type=["xlsx", "csv"])

if uploaded_file is not None:
  st.success(f"{success_file}{uploaded_file.name}")
  try:
    if uploaded_file.name.endswith(".csv"):
      df = pd.read_csv(uploaded_file)
    else:
      df = pd.read_excel(uploaded_file)

    st.markdown(f"#### {preview_text}")
    st.dataframe(df.head(), use_container_width=True)

    if st.button(save_btn):
      conn = get_connection()
      cursor = conn.cursor()

      saved_count = 0
      for _, row in df.iterrows():
        date_val = str(row.iloc[0]) if len(row) > 0 else "2026-01-01"
        desc_val = str(row.iloc[1]) if len(row) > 1 else "Гүйлгээ"
        amount_val = (
            float(row.iloc[2])
            if len(row) > 2 and pd.notnull(row.iloc[2])
            else 0.0
        )
        tx_type = "Зарлага" if amount_val < 0 else "Орлого"

        cursor.execute(
            """
                INSERT INTO transactions (date, description, amount, type, category, bank_name)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                date_val,
                desc_val,
                abs(amount_val),
                tx_type,
                "Импортлогдсон",
                bank,
            ),
        )
        saved_count += 1

      conn.commit()
      conn.close()
      st.success(save_success.format(count=saved_count))

  except Exception as ex:
    st.error(f"Error: {ex}")

st.markdown("---")
st.markdown(f"### {prev_imports}")
st.info(no_history)