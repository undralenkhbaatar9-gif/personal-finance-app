import streamlit as st

# Хуудасны нэр болон тохиргоо (Энэ нь зүүн талын цэсийг буцааж гаргана)
st.set_page_config(
    page_title="Хуулга импортлох", page_icon="📄", layout="wide"
)

# Dark Glassmorphism Custom CSS загвар
st.markdown(
    """
    <style>
    /* Ерөнхий дэвсгэр болон фонт */
    .stApp {
        background-color: #0f1117;
        color: #ffffff;
    }
    
    /* Гарчиг болон текстүүд */
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #ffffff !important;
    }

    /* Selectbox (Банк сонгох) загвар */
    .stSelectbox div[data-baseweb="select"] {
        background-color: #1e222d !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
    }

    /* File uploader хэсгийн дизайн */
    .stFileUploader {
        background: rgba(30, 34, 45, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 14px;
        padding: 20px;
    }
    
    /* Browse files товч */
    .stFileUploader section button {
        background-color: #2b2d31 !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
    }
    
    .stFileUploader section button:hover {
        background-color: #35383f !important;
        border-color: #10B981 !important;
    }

    /* Өмнөх импорт хэсгийн контейнер */
    .import-history-box {
        background: rgba(30, 34, 45, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 20px;
        margin-top: 20px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- UI Layout ---

st.markdown("<h1>📄 Хуулга импортлох</h1>", unsafe_allow_html=True)
st.write("")

# Банк сонгох хэсэг
bank_choice = st.selectbox(
    "Банк сонгох",
    ["Хаан банк", "Голомт банк", "Хас банк", "Төрийн банк"],
    label_visibility="collapsed",
)

st.write("")

# Файл оруулах хэсэг
uploaded_file = st.file_uploader(
    f"{bank_choice}-ны хуулгаа сонгоно уу (Excel, CSV)", type=["xlsx", "csv"]
)

if uploaded_file is not None:
    st.success(
        f"Файл амжилттай орж ирлээ: **{uploaded_file.name}**", icon="✅"
    )

st.write("")
st.markdown("---")

# Өмнөх импортууд хэсэг
st.markdown("<h3>Өмнөх импортууд 🔗</h3>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="import-history-box">
        <p style="color: #9ca3af !important; margin: 0;">Импортын түүхийг одоогоор харуулах боломжгүй байна.</p>
    </div>
""",
    unsafe_allow_html=True,
)