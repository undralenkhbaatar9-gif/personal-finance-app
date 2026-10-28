from datetime import date, timedelta
import streamlit as st
from finance.db import get_session
from finance.reports import monthly_summary, transactions_export
from finance.ui import apply_global_styles, render_footer

apply_global_styles()

st.title("Санхүүгийн хяналтын самбар")
st.write("Таны орлого, зарлага болон санхүүгийн ерөнхий дүр зураг.")

today = date.today()
date_from = today - timedelta(days=365)
date_to = today

try:
    with get_session() as session:
        # Гүйлгээг төрлөөр нь яг таг шүүж авах
        df = transactions_export(session, date_from, date_to, include_transfers=False)
        
        if not df.empty and "kind" in df.columns:
            # Зөвхөн орлогын төрөлтэй гүйлгээг нтлөх
            total_income = df[df["kind"] == "income"]["amount"].sum() if not df[df["kind"] == "income"].empty else 0
            # Зөвхөн зарлагын төрөлтэй гүйлгээг шүүж тухайн дүнг авах
            total_expense = df[df["kind"] == "expense"]["amount"].abs().sum() if not df[df["kind"] == "expense"].empty else 0
        else:
            total_income = 0
            total_expense = 0

        net_balance = total_income - total_expense

        # Метрик хэсэг
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("НИЙТ ОРЛОГО", f"{float(total_income):,.2f} ₮")
        with col2:
            st.metric("НИЙТ ЗАРЛАГА", f"{float(total_expense):,.2f} ₮")
        with col3:
            st.metric("ЦЭВЭР ҮЛДЭГДЭЛ", f"{float(net_balance):,.2f} ₮", delta=f"{float(net_balance):,.2f} ₮")

        st.markdown("---")
        
        # Сарын тайлан болон график
        st.subheader("Сарын орлого, зарлагын тойм")
        monthly_df = monthly_summary(session, date_from, date_to, include_transfers=False)
        
        if not monthly_df.empty:
            # Графикийн датаг баталгаажуулах
            st.bar_chart(monthly_df.set_index("month")[["income", "expense"]])
        else:
            st.info("📌 Одоогоор сарын мэдээлэл байхгүй байна.")

except Exception as error:
    st.error(f"Мэдээлэл ачаалахад алдаа гарлаа: {error}")

render_footer()