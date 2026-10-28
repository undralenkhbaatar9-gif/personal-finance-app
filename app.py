from datetime import date, timedelta
import streamlit as st
from finance.db import get_session
from finance.reports import (
    monthly_summary,
    expense_by_category,
    income_by_category,
    top_counterparties,
    transactions_export
)
from finance.ui import apply_global_styles, render_footer

apply_global_styles()

# Загварын цэвэрлэх CSS
st.markdown("""
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .metric-container {
        background-color: #1e293b;
        border: 1px solid #334155;
        padding: 15px;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("## 📊 Санхүүгийн хяналтын самбар")
st.markdown("Таны орлого, зарлага болон санхүүгийн ерөнхий гүйцэтгэл.")
st.markdown("---")

today = date.today()
date_from = today - timedelta(days=365)
date_to = today

try:
    with get_session() as session:
        # 1. Ерөнхий дүнгүүдийг шүүж авах
        df = transactions_export(session, date_from, date_to, include_transfers=False)
        
        if not df.empty and "kind" in df.columns:
            total_income = df[df["kind"] == "income"]["amount"].sum() if not df[df["kind"] == "income"].empty else 0
            total_expense = df[df["kind"] == "expense"]["amount"].abs().sum() if not df[df["kind"] == "expense"].empty else 0
        else:
            total_income = 0
            total_expense = 0

        net_balance = total_income - total_expense

        # Метрик картууд (Дээд хэсэг)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("НИЙТ ОРЛОГО", f"{float(total_income):,.2f} ₮")
        with col2:
            st.metric("НИЙТ ЗАРЛАГА", f"{float(total_expense):,.2f} ₮")
        with col3:
            st.metric("ЦЭВЭР ҮЛДЭГДЭЛ", f"{float(net_balance):,.2f} ₮", delta=f"{float(net_balance):,.2f} ₮")

        st.markdown("###")

        # 2. Сарын тойм график болон дата
        st.subheader("📅 Сарын орлого, зарлагын тайлан")
        monthly_df = monthly_summary(session, date_from, date_to, include_transfers=False)
        
        if not monthly_df.empty:
            # Хүснэгт болон графикийг зэрэгцүүлж эсвэл цэвэрхэн харуулах
            st.dataframe(
                monthly_df.rename(columns={"month": "Сар", "income": "Орлого (₮)", "expense": "Зарлага (₮)"}),
                use_container_width=True,
                hide_index=True
            )
            st.bar_chart(monthly_df.set_index("month")[["income", "expense"]], use_container_width=True)
        else:
            st.info("📌 Одоогоор сарын мэдээлэл бүртгэгдээгүй байна.")

        st.markdown("---")

        # 3. Ангилал болон харилцагчийн мэдээлэл (Цэвэрхэн хүснэгт хэлбэрээр)
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("🏷️ Зардлын ангилал")
            exp_cat_df = expense_by_category(session, date_from, date_to, include_transfers=False)
            if not exp_cat_df.empty:
                st.dataframe(
                    exp_cat_df.rename(columns={"category": "Ангилал", "amount": "Дүн (₮)"}),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Зарлагын ангилал одоогоор алга.")

        with col_right:
            st.subheader("🏆 Гол харилцагчид")
            cp_df = top_counterparties(session, date_from, date_to, include_transfers=False, n=5)
            if not cp_df.empty:
                # Counterparty багануудыг цэвэрлэх
                cp_df["counterparty"] = cp_df["counterparty"].fillna("Тодорхойгүй")
                st.dataframe(
                    cp_df.rename(columns={"counterparty": "Харилцагч", "amount": "Дүн (₮)"}),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Харилцагчийн мэдээлэл байхгүй байна.")

except Exception as error:
    st.error(f"Мэдээлэл ачаалахад алдаа гарлаа: {error}")

render_footer()