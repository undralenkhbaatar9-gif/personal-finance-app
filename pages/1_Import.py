import streamlit as st

# Загварыг илүү цэвэрхэн болгох Custom CSS
st.markdown(
    """
    <style>
    /* File uploader хэсгийн харагдах байдлыг сайжруулах */
    .stFileUploader {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 15px;
    }
    
    /* Browse files товчны өнгийг илүү зохицохуйц болгох */
    .stFileUploader section button {
        background-color: #2b2d31 !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
    }
    
    .stFileUploader section button:hover {
        background-color: #35383f !important;
        border-color: #4e5058 !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)