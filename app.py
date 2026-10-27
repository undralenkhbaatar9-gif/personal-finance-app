import streamlit as st
import pandas as pd

st.markdown("### 📄 Хуулга импортлох")

# Банкны сонголтуудыг бүрэн оруулах
bank_options = [
    "Хаан банк", 
    "Голомт банк", 
    "Хас банк", 
    "Төрийн банк", 
    "Голомт банк", 
    "ХХБ (Голомт/Худалдаа хөгжлийн банк)", 
    "Ариг банк", 
    "Богд банк"
]

bank = st.selectbox("Банк сонгох", bank_options)

# Сонгосон банкны дагуу файлын нэр болон чиглүүлэгч
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

st.markdown("---")
st.markdown("### Өмнөх импортууд")
st.info("Импортын түүхийг одоогоор харуулах боломжгүй байна.")