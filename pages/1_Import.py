import os
import sqlite3
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Хуулга импортлох", page_icon="📄", layout="wide"
)

# 🌙 Dark Glassmorphism загвар
st.markdown(
    """
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
    
    /* File Uploader styling */
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

# Өгөгдлийн сангийн холболт (Үндсэн фолдер доторх finance.db рүү зөв заах)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "finance.db")


def get_connection():
  conn = sqlite3.connect(DB_PATH)
  conn.row_factory = sqlite3.Row
  return conn


st.markdown("### 📄 Банкны хуулга импортлох")

bank_options = [
    "Хаан банк",
    "Голомт банк",
    "Хас банк",
    "Төрийн банк",
    "ХХБ (Худалдаа хөгжлийн банк)",
    "Ариг банк",
    "Богд банк",
]

bank = st.selectbox("Банк сонгох", bank_options)

uploaded_file = st.file_uploader(
    f"{bank}-ны хуулгаа сонгоно уу (Excel, CSV)", type=["xlsx", "csv"]
)

if uploaded_file is not None:
  st.success(f"📂 Файл амжилттай орж ирлээ: {uploaded_file.name}")
  try:
    if uploaded_file.name.endswith(".csv"):
      df = pd.read_csv(uploaded_file)
    else:
      df = pd.read_excel(uploaded_file)

    st.markdown("#### 📋 Уншсан файлын мэдээлэл (Урьдчилсан харагдац)")
    st.dataframe(df.head(), use_container_width=True)

    if st.button("💾 Өгөгдлийн санд хадгалах"):
      conn = get_connection()
      cursor = conn.cursor()

      saved_count = 0
      for _, row in df.iterrows():
        # Файлын эхний багануудыг өгөгдлийн сантай автоматаар холбох
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
      st.success(
          f"✅ Нийт {saved_count} гүйлгээ амжилттай өгөгдлийн санд хадгалагдлаа!"
      )

  except Exception as ex:
    st.error(f"Файлыг унших болон хадгалах явцад алдаа гарлаа: {ex}")

st.markdown("---")
st.markdown("### Өмнөх импортууд")
st.info("Импортын түүхийг одоогоор харуулах боломжгүй байна.")