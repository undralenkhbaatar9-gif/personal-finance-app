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

# --- БАНКНЫ БРЭНД ӨНГӨНИЙ ТОХИРГОО ---
bank_styles = {
    "Хаан банк": {
        "color": "#006A4E",
        "bg_glow": "rgba(0, 106, 78, 0.15)",
    },
    "Голомт банк": {
        "color": "#004B87",
        "bg_glow": "rgba(0, 75, 135, 0.15)",
    },
    "Хас банк": {
        "color": "#FF6B00",
        "bg_glow": "rgba(255, 107, 0, 0.15)",
    },
    "Төрийн банк": {
        "color": "#009EE0",
        "bg_glow": "rgba(0, 158, 224, 0.15)",
    },
    "ХХБ (Худалдаа хөгжлийн банк)": {
        "color": "#0072CE",
        "bg_glow": "rgba(0, 114, 206, 0.15)",
    },
    "Ариг банк": {
        "color": "#8E44AD",
        "bg_glow": "rgba(142, 68, 173, 0.15)",
    },
    "Богд банк": {
        "color": "#D4AC0D",
        "bg_glow": "rgba(212, 172, 13, 0.15)",
    },
}

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
  col_error = (
      "⚠️ Файлаас 'Огноо', 'Утга' эсвэл 'Дүн' багануудыг олоход алдаа гарлаа."
      " Баганын нэрээ шалгана уу."
  )
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
  col_error = (
      "⚠️ Could not find 'Date', 'Description', or 'Amount' columns in the"
      " file. Please check column headers."
  )

st.markdown(f"### {title_text}")

bank_options = list(bank_styles.keys())
bank = st.selectbox(bank_label, bank_options)

selected_bank_info = bank_styles.get(
    bank, {"color": "#10B981", "bg_glow": "rgba(16, 185, 129, 0.15)"}
)
bank_color = selected_bank_info["color"]
bank_glow = selected_bank_info["bg_glow"]

# 🌙 CSS загвар
st.markdown(
    f"""
<style>
    .stApp {{
        background-color: #0e1117;
        color: #ffffff;
    }}
    [data-testid="stSidebar"] {{
        background-color: #1e222d !important;
    }}
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] a {{
        color: #ffffff !important;
    }}
    
    .stSelectbox label p, label {{
        color: #ffffff !important;
    }}
    
    div[data-baseweb="select"] > div {{
        background-color: #1e222d !important;
        color: #ffffff !important;
        border-color: {bank_color} !important;
        box-shadow: 0 0 10px {bank_glow} !important;
    }}
    
    div[data-baseweb="select"] span {{
        color: #ffffff !important;
    }}

    div[data-baseweb="popover"], div[role="listbox"] {{
        background-color: #1e222d !important;
        color: #ffffff !important;
    }}
    
    div[role="option"] {{
        background-color: #1e222d !important;
        color: #ffffff !important;
    }}
    div[role="option"]:hover {{
        background-color: #35383f !important;
    }}

    .bank-banner {{
        background: linear-gradient(135deg, {bank_glow} 0%, rgba(30, 34, 45, 0.6) 100%);
        border-left: 5px solid {bank_color};
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 16px;
        box-shadow: 0 4px 20px {bank_glow};
    }}
    .bank-color-dot {{
        width: 18px;
        height: 18px;
        background-color: {bank_color};
        border-radius: 50%;
        box-shadow: 0 0 12px {bank_color};
    }}

    [data-testid="stFileUploader"] {{
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 2px dashed {bank_color} !important;
        border-radius: 14px;
        padding: 20px;
    }}
    [data-testid="stFileUploader"] section {{
        background-color: transparent !important;
    }}
    [data-testid="stFileUploader"] div, 
    [data-testid="stFileUploader"] span, 
    [data-testid="stFileUploader"] small, 
    [data-testid="stFileUploader"] p {{
        color: #ffffff !important;
    }}
    [data-testid="stFileUploader"] button {{
        color: #ffffff !important;
        background-color: {bank_color} !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 8px !important;
    }}
    [data-testid="stFileUploader"] button:hover {{
        opacity: 0.85 !important;
    }}
</style>
""",
    unsafe_allow_html=True,
)

banner_html = f"""
<div class="bank-banner">
    <div class="bank-color-dot"></div>
    <div>
        <h3 style="margin: 0; color: #ffffff; font-size: 18px;">{bank}</h3>
        <p style="margin: 0; color: #94a3b8; font-size: 12px;">{"Банкны хуулга импортлох хэсэг" if lang=="Монгол" else "Bank Statement Import Section"}</p>
    </div>
</div>
"""
st.markdown(banner_html, unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    file_label_text.format(bank=bank), type=["xlsx", "csv"]
)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "finance.db")


def get_connection():
  conn = sqlite3.connect(DB_PATH)
  conn.row_factory = sqlite3.Row
  return conn


if uploaded_file is not None:
  st.success(f"{success_file}{uploaded_file.name}")
  try:
    if uploaded_file.name.endswith(".csv"):
      df = pd.read_csv(uploaded_file)
    else:
      df = pd.read_excel(uploaded_file)

    st.markdown(f"#### {preview_text}")
    st.dataframe(df.head(), use_container_width=True)

    # --- УХААЛАГ БАГАНА ТАНИХ ЛОГИК ---
    cols_lower = [str(c).strip().lower() for c in df.columns]


    # Туслах функц: түлхүүр үгээр багана олох
    def find_col(keywords):
      for kw in keywords:
        for idx, col in enumerate(cols_lower):
          if kw in col:
            return df.columns[idx]
      return None


    date_col = find_col(["огноо", "date", "ognoo"])
    desc_col = find_col(["утга", "гүйлгээний утга", "description", "desc", "utga"])
    amount_col = find_col(["дүн", "amount", "dun", "үнэ", "гүйлгээний дүн"])

    # Хэрэв толгой мөрөөс олдохгүй бол индексээр нь авна (fallback)
    if date_col is None and len(df.columns) > 0:
      date_col = df.columns[0]
    if desc_col is None and len(df.columns) > 1:
      desc_col = df.columns[1]
    if amount_col is None and len(df.columns) > 2:
      amount_col = df.columns[2]

    if st.button(save_btn):
      if date_col is not None and desc_col is not None and amount_col is not None:
        conn = get_connection()
        cursor = conn.cursor()

        saved_count = 0
        for _, row in df.iterrows():
          try:
            date_val = str(row[date_col]) if pd.notnull(row[date_col]) else "2026-01-01"
            desc_val = str(row[desc_col]) if pd.notnull(row[desc_col]) else "Гүйлгээ"
            
            # Дүн цэвэрлэх (ком болон зай арилгах)
            raw_amt = str(row[amount_col]).replace(",", "").replace("₮", "").strip()
            amount_val = float(raw_amt) if pd.notnull(raw_amt) and raw_amt != "" else 0.0

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
          except Exception:
            continue

        conn.commit()
        conn.close()
        st.success(save_success.format(count=saved_count))
      else:
        st.error(col_error)

  except Exception as ex:
    st.error(f"Error: {ex}")

st.markdown("---")
st.markdown(f"### {prev_imports}")
st.info(no_history)