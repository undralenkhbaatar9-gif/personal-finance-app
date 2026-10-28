from datetime import date, timedelta
import streamlit as st
from finance.db import get_session
from finance.reports import monthly_summary, transactions_export
from finance.ui import apply_global_styles, render_footer

# Глобал стилийг ачаалах
apply_global_styles()

# Нэмэлт glassmorphism болон карт дизайны CSS сайжруулалт
st.markdown("""
    <style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0px;
    }
    .sub-title {
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">💳 Санхүүгийн хяналтын самбар</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Таны орлого, зарлага болон санхүүгийн ерөнхий дүр зураг.</p>', unsafe_allow_html=True)

today = date.today()
date_from = today - timedelta(days=365)
date_to = today

try:
    with get_session() as session:
        # Гүйлгээг төрлөөр нь шүүж авах
        df = transactions_export(session, date_from, date_to, include_transfers=False)
        
        if not df.empty and "kind" in df.columns:
            total_income = df[df["kind"] == "income"]["amount"].sum() if not df[df["kind"] == "income"].empty else 0
            total_expense = df[df["kind"] == "expense"]["amount"].abs().sum() if not df[df["kind"] == "expense"].empty else 0
        else:
            total_income = 0
            total_expense = 0

        net_balance = total_income - total_expense

        # Сайхан харагдах метрик картууд
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🟢 НИЙТ ОРЛОГО", f"{float(total_income):,.2f} ₮")
        with col2:
            st.metric("🔴 НИЙТ ЗАРЛАГА", f"{float(total_expense):,.2f} ₮")
        with col3:
            st.metric("🔵 ЦЭВЭР ҮЛДЭГДЭЛ", f"{float(net_balance):,.2f} ₮", delta=f"{float(net_balance):,.2f} ₮")

        st.markdown("---")
        
        # Сарын тайлан болон график хэсэг
        st.subheader("📊 Сарын орлого, зарлагын тойм график")
        monthly_df = monthly_summary(session, date_from, date_to, include_transfers=False)
        
        if not monthly_df.empty:
            chart_data = monthly_df.set_index("month")[["income", "expense"]]
            st.bar_chart(chart_data, use_container_width=True)
        else:
            st.info("📌 Одоогоор сарын мэдээлэл байхгүй байна. Зүүн талын цэсээс хуулга оруулж эхлэнэ үү.")

except Exception as error:
    st.error(f"Мэдээлэл ачаалахад алдаа гарлаа: {error}")

render_footer()