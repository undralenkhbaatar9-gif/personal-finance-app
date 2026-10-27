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

# --- БАНКНЫ АЛБАН ЁСНЫ ӨНГӨ БОЛОН ВЕКТОР ЛОГОНУУД ---
bank_styles = {
    "Хаан банк": {
        "color": "#006A4E",
        "bg_glow": "rgba(0, 106, 78, 0.15)",
        "svg_logo": '<svg width="36" height="36" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="10" fill="#006A4E"/><path d="M12 6c-2 0-4 2-4 4s2 4 4 4 4-2 4-4-2-4-4-4zm0 11c-3.87 0-7-3.13-7-7s3.13-7 7-7 7 3.13 7 7-3.13 7-7 7z" fill="white"/></svg>'
    },
    "Голомт банк": {
        "color": "#004B87",
        "bg_glow": "rgba(0, 75, 135, 0.15)",
        "svg_logo": '<svg width="36" height="36" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><rect width="24" height="24" rx="4" fill="#004B87"/><path d="M7 7h10v3H10v4h7v3H7V7z" fill="#FFD100"/></svg>'
    },
    "Хас банк": {
        "color": "#FF6B00",
        "bg_glow": "rgba(255, 107, 0, 0.15)",
        "svg_logo": '<svg width="36" height="36" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><rect width="24" height="24" rx="4" fill="#001F5B"/><path d="M12 4l2.5 5.5L20 12l-5.5 2.5L12 20l-2.5-5.5L4 12l5.5-2.5L12 4z" fill="#FF6B00"/></svg>'
    },
    "Төрийн банк": {
        "color": "#009EE0",
        "bg_glow": "rgba(0, 158, 224, 0.15)",
        "svg_logo": '<svg width="36" height="36" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><rect width="24" height="24" rx="6" fill="#009EE0"/><path d="M12 6v12M9 9h6" stroke="white" stroke-width="2" stroke-linecap="round"/></svg>'
    },
    "ХХБ (Худалдаа хөгжлийн банк)": {
        "color": "#0072CE",
        "bg_glow": "rgba(0, 114, 206, 0.15)",
        "svg_logo": '<svg width="36" height="36" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="10" fill="#0072CE"/><path d="M8 12h8M12 8v8" stroke="white" stroke-width="2.5" stroke-linecap="round"/></svg>'
    },
    "Ариг банк": {
        "color": "#8E44AD",
        "bg_glow": "rgba(142, 68, 173, 0.15)",
        "svg_logo": '<svg width="36" height="36" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="10" fill="#8E44AD"/><path d="M8 14L12 8L16 14H8Z" fill="white"/></svg>'
    },
    "Богд банк": {
        "color": "#D4AC0D",
        "bg_glow": "rgba(212, 172, 13, 0.15)",
        "svg_logo": '<svg width="36" height="36" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><rect width="24" height="24" rx="6" fill="#D4AC0D"/><path d="M12 7L15 12H9L12 7Z" fill="white"/></svg>'
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
    save_success = "✅ Нийт {count} гүйлгээ амжилттай өгөгдлийн санд хадгалагдлаа!"
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

st.markdown(f"### {title_text}")

bank_options = list(bank_styles.keys())
bank = st.selectbox(bank_label, bank_options)

selected_bank_info = bank_styles.get(bank, {"color": "#10B981", "bg_glow": "rgba(16, 185, 129, 0.15)", "svg_logo": ""})
bank_color = selected_bank_info["color"]
bank_glow = selected_bank_info["bg_glow"]
bank_svg = selected_bank_info["svg_logo"]

# 🌙 Dark Glassmorphism + Dynamic Bank Theme CSS
st.markdown(f"""
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

    /* Bank Banner Header */
    .bank-banner {{
        background: linear-gradient(135deg, {bank_glow} 0%, rgba(30, 34, 45, 0.6) 100%);
        border: 1px solid {bank_color};
        border-radius: 14px;
        padding: 18px 22px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 20px;
        box-shadow: 0 4px 20px {bank_glow};
    }}
    .bank-logo-container {{
        background: rgba(255, 255, 255, 0.08);
        padding: 8px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }}

    /* File Uploader styling */
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
""", unsafe_allow_html=True)

# --- БАНКНЫ БАННЕР (Нэг мөрөөр бичсэн SVG логогоор) ---
banner_html = f"""
<div class="bank-banner">
    <div class="bank-logo-container">
        {bank_svg}
    </div>
    <div>
        <h3 style="margin: 0; color: #ffffff; font-size: 20px;">{bank}</h3>
        <p style="margin: 0; color: #94a3b8; font-size: 13px;">{"Банкны хуулга импортлох хэсэг" if lang=="Монгол" else "Bank Statement Import Section"}</p>
    </div>
</div>
"""
st.markdown(banner_html, unsafe_allow_html=True)

uploaded_file = st.file_uploader(file_label_text.format(bank=bank), type=["xlsx", "csv"])

# Database path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "finance.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

if uploaded_file is not None:
    st.success(f"{success_file}{uploaded_file.name}")
    try:
        if uploaded_file.name.endswith('.csv'):
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
                amount_val = float(row.iloc[2]) if len(row) > 2 and pd.notnull(row.iloc[2]) else 0.0
                tx_type = "Зарлага" if amount_val < 0 else "Орлого"
                
                cursor.execute("""
                    INSERT INTO transactions (date, description, amount, type, category, bank_name)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (date_val, desc_val, abs(amount_val), tx_type, "Импортлогдсон", bank))
                saved_count += 1
                
            conn.commit()
            conn.close()
            st.success(save_success.format(count=saved_count))
            
    except Exception as ex:
        st.error(f"Error: {ex}")

st.markdown("---")
st.markdown(f"### {prev_imports}")
st.info(no_history)