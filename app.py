from datetime import date, timedelta
import streamlit as st
from finance.db import get_session
from finance.reports import monthly_summary, transactions_export
from finance.ui import apply_global_styles, render_footer

apply_global_styles()

st.title("Санхүүгийн хяналтын самбар")
st.write("Таны орлого, зарлага болон санхүүгийн ерөнхий дүр зураг.")

# Хугацааны хүрээ (Сүүлийн 1 жил эсвэл илүү өргөнөөр харах)
today = date.today()
date_from = today - timedelta(days=365)
date_to = today

try:
    with get_session() as session:
        # Бүх гүйлгээнээс орлого, зарлагыг шууд нарийвчлан шүүж авах
        df = transactions_export(session, date_from, date_to, include_transfers=False)
        
        if not df.empty and "kind" in df.columns:
            total_income = df[df["kind"] == "income"]["amount"].sum() or 0
            # Зарлага хасагдсан утгатай эсвэл absolute байж болох тул ABS ашиглана
            total_expense = df[df["kind"] == "expense"]["amount"].abs().sum() or 0
        else:
            total_income = 0
            total_expense = 0

        net_balance = total_income - total_expense

        # Метрик хэсэг (Орлого, Зарлага, Үлдэгдэл)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("НИЙТ ОРЛОГО", f"{total_income:,.2f} ₮")
        with col2:
            st.metric("НИЙТ ЗАРЛАГА", f"{total_expense:,.2f} ₮")
        with col3:
            st.metric("ЦЭВЭР ҮЛДЭГДЭЛ", f"{net_balance:,.2f} ₮", delta=f"{net_balance:,.2f} ₮")

        st.markdown("---")
        
        # Сарын тайлан болон график
        st.subheader("Сарын орлого, зарлагын тойм")
        monthly_df = monthly_summary(session, date_from, date_to, include_transfers=False)
        
        if not monthly_df.empty:
            # Графикийг илүү ойлгомжтой харуулахын тулд index-ийг month болгоно
            chart_data = monthly_df.set_index("month")[["income", "expense"]]
            st.bar_chart(chart_data)
        else:
            st.info("📌 Одоогоор сарын мэдээлэл байхгүй байна.")

except Exception as error:
    st.error(f"Мэдээлэл ачаалахад алдаа гарлаа: {error}")

render_footer()