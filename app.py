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

st.markdown("## 💳 Санхүүгийн хяналтын самбар")
st.markdown("Таны орлого, зарлага болон санхүүгийн ерөнхий дүр зураг.")

today = date.today()
date_from = today - timedelta(days=365)
date_to = today

try:
    with get_session() as session:
        # 1. Ерөнхий дүнгүүд
        df = transactions_export(session, date_from, date_to, include_transfers=False)
        
        if not df.empty and "kind" in df.columns:
            total_income = df[df["kind"] == "income"]["amount"].sum() if not df[df["kind"] == "income"].empty else 0
            total_expense = df[df["kind"] == "expense"]["amount"].abs().sum() if not df[df["kind"] == "expense"].empty else 0
        else:
            total_income = 0
            total_expense = 0

        net_balance = total_income - total_expense

        # Метрик картууд
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🟢 НИЙТ ОРЛОГО", f"{float(total_income):,.2f} ₮")
        with col2:
            st.metric("🔴 НИЙТ ЗАРЛАГА", f"{float(total_expense):,.2f} ₮")
        with col3:
            st.metric("🔵 ЦЭВЭР ҮЛДЭГДЭЛ", f"{float(net_balance):,.2f} ₮", delta=f"{float(net_balance):,.2f} ₮")

        st.markdown("---")
        
        # 2. Сарын орлого, зарлагын харьцуулсан график
        st.subheader("📈 Сарын орлого, зарлагын тойм график")
        monthly_df = monthly_summary(session, date_from, date_to, include_transfers=False)
        
        if not monthly_df.empty:
            st.bar_chart(monthly_df.set_index("month")[["income", "expense"]], use_container_width=True)
        else:
            st.info("📌 Одоогоор сарын мэдээлэл байхгүй байна.")

        st.markdown("---")

        # 3. Ангилал болон харилцагчийн график/хүснэгтүүд (Хоёр баганаар зэрэгцүүлж харуулах)
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("🏷️ Ангиллаарх зарлага")
            exp_cat_df = expense_by_category(session, date_from, date_to, include_transfers=False)
            if not exp_cat_df.empty:
                # Зардлын ангилал тус бүрээр бар чарт гаргах
                st.bar_chart(exp_cat_df.set_index("category")["amount"], use_container_width=True)
            else:
                st.info("Зарлагын ангилал одоогоор алга.")

        with col_right:
            st.subheader("🏆 Гол харилцагчид (Top Counterparties)")
            cp_df = top_counterparties(session, date_from, date_to, include_transfers=False, n=5)
            if not cp_df.empty:
                st.dataframe(cp_df, use_container_width=True)
            else:
                st.info("Харилцагчийн мэдээлэл байхгүй байна.")

except Exception as error:
    st.error(f"Мэдээлэл ачаалахад алдаа гарлаа: {error}")

render_footer()