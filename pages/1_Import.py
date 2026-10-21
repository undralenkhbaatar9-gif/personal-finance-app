import streamlit as st

st.title("📥 Банкны хуулга оруулах")
st.write("Хан банк болон бусад банкны `.xlsx` хуулгаа энд оруулна уу.")
st.file_uploader("Банкны хуулга сонгох", type=["xlsx", "csv"])
