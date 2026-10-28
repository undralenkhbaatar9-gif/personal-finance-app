from datetime import date, timedelta
import streamlit as st
from finance.db import get_session
from finance.ui import apply_global_styles, render_footer
from finance.reports import (
    monthly_summary,
    expense_by_category,
    income_by_category,
    top_counterparties,
    unclassified_total
)

apply_global_styles()
st.title("Тайлан мэдээ & Dashboard")

today = date.today()
with st.sidebar:
    date_range = st.date_input(
        "Огнооны хүрээ",
        value=(today - timedelta(days=180), today),
        key="report-date-range"
    )
    include_transfers = st.checkbox("Шилжүүлэг оруулах", value=False)

if isinstance(date_range, tuple) and len(date_range) == 2:
    date_from, date_to = date_range
else:
    date_from = date_to = date_range

try:
    with get_session() as session:
        # Ангилаагүй гүйлгээний дүн
        unclass_amt = unclassified_total(session, date_from, date_to)
        st.metric("Ангилаагүй гүйлгээний нийт дүн", f"{unclass_amt:,.2f} ₮")

        st.subheader("Сарын орлого болон зарлагын график (Monthly Summary)")
        monthly_df = monthly_summary(session, date_from, date_to, include_transfers)
        if not monthly_df.empty:
            st.bar_chart(monthly_df.set_index("month")[["income", "expense"]])
        else:
            st.info("Сарын мэдээлэл одоогоор алга байна.")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Ангиллаар зарлага")
            exp_df = expense_by_category(session, date_from, date_to, include_transfers)
            if not exp_df.empty:
                st.bar_chart(exp_df.set_index("category")["amount"])
            else:
                st.info("Зарлагын ангиллаар мэдээлэл алга.")

        with col2:
            st.subheader("Ангиллаар орлого")
            inc_df = income_by_category(session, date_from, date_to, include_transfers)
            if not inc_df.empty:
                st.bar_chart(inc_df.set_index("category")["amount"])
            else:
                st.info("Орлогын ангиллаар мэдээлэл алга.")

        st.subheader("Гол харилцагчид (Top Counterparties)")
        cp_df = top_counterparties(session, date_from, date_to, include_transfers, n=10)
        if not cp_df.empty:
            st.dataframe(cp_df, use_container_width=True)
        else:
            st.info("Харилцагчийн мэдээлэл алга.")

except Exception as error:
    st.error(f"Тайлангийн мэдээлэл ачаалахад алдаа гарлаа: {error}")

render_footer()