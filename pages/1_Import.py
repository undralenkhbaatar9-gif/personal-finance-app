import pandas as pd
import streamlit as st

# Хуудасны тохиргоо (Монгол нэр, еможи болон өргөн layout)
st.set_page_config(
    page_title="Хуулга импортлох", page_icon="📄", layout="wide"
)

# 🌙 Dark Glassmorphism болон Sidebar албаар хар болгох CSS
st.markdown(
    """
<style>
    /* Үндсэн дэвсгэр */
    .stApp {
        background-color: #0f1117;
        color: #ffffff;
    }
    
    /* Зүүн талын цэс (Sidebar) дэвсгэрийг хар өнгөтэй болгох */
    [data-testid="stSidebar"] {
        background-color: #1e222d !important;
    }
    
    /* Sidebar доторх бүх текст болон линкүүдийг цагаан болгох */
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] a {
        color: #ffffff !important;
    }
    
    /* File Uploader үндсэн контейнер */
    [data-testid="stFileUploader"] {
        background-color: rgba(30, 34, 45, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 14px;
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
    
    /* Browse files товчлуур */
    [data-testid="stFileUploader"] button {
        color: #ffffff !important;
        background-color: #1e222d !important;
        font-weight: 600 !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
    }
    
    [data-testid="stFileUploader"] button:hover {
        background-color: #35383f !important;
        border-color: #10B981 !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Гарчиг
st.markdown("### 📄 Хуулга импортлох")

# 🏦 Банкны сонголтууд
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

# Файл оруулах хэсэг
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

    st.write("📋 Уншсан файлын мэдээлэл (Урьдчилсан харагдац):")
    st.dataframe(df.head(), use_container_width=True)

    if st.button("💾 Өгөгдлийн санд хадгалах"):
      st.success("✅ Хуулга амжилттай өгөгдлийн санд хадгалагдлаа!")
  except Exception as ex:
    st.error(f"Файлыг унших явцад алдаа гарлаа: {ex}")

st.markdown("---")
st.markdown("### Өмнөх импортууд")
st.info("Импортын түүхийг одоогоор харуулах боломжгүй байна.")