from datetime import date, timedelta
import streamlit as st
from finance.db import get_session
from finance.reports import monthly_summary
from finance.ui import apply_global_styles, render_footer

apply_global_styles()

st.title("Санхүүгийн хяналтын самбар")
st.write("Таны орлого, зарлага болон санхүүгийн ерөнхий дүр зураг.")

# Сүүлийн 6 сарын хугацаагаар тооцоолох
today = date.today()
date_from = today - timedelta(days=180)
date_to = today

try:
    with get_session() as session:
        # Сарын тайлангийн функцээс датаг татаж авах
        monthly_df = monthly_summary(session, date_from, date_to, include_transfers=False)
        
        if not monthly_df.empty:
            total_income = monthly_df["income"].sum()
            total_expense = monthly_df["expense"].sum()
            net_balance = total_income - total_expense
        else:
            total_income = 0
            total_expense = 0
            net_balance = 0

        # Метрик хэсэг (Орлого, Зарлага, Үлдэгдэл)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("НИЙТ ОРЛОГО", f"{total_income:,.2f} ₮")
        with col2:
            st.metric("НИЙТ ЗАРЛАГА", f"{total_expense:,.2f} ₮")
        with col3:
            st.metric("ЦЭВЭР ҮЛДЭГДЭЛ", f"{net_balance:,.2f} ₮")

        st.markdown("---")
        
        # График хэсэг
        st.subheader("Сарын орлого, зарлагын тойм")
        if not monthly_df.empty:
            st.bar_chart(monthly_df.set_index("month")[["income", "expense"]])
        else:
            st.info("📌 **Тавтай морилно уу!**\n\nЗүүн талын цэсээс хуулга импортлох хэсгийг сонгож банкны хуулгаа оруулж эхэлнэ үү.")

except Exception as error:
    st.error(f"Мэдээлэл ачаалахад алдаа гарлаа: {error}")

render_footer()