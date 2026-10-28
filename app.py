from datetime import date, timedelta

import streamlit as st

from finance.db import get_session
from finance.reports import (
    expense_by_category,
    monthly_summary,
    top_counterparties,
    transactions_export,
)
from finance.ui import apply_global_styles, render_footer, render_lang_toggle

lang = render_lang_toggle(location="top")

t = {
    "mn": {
        "page_title": "Санхүүгийн самбар",
        "title": "📊 Санхүүгийн хяналтын самбар",
        "subtitle": "Таны орлого, зарлага болон санхүүгийн ерөнхий гүйцэтгэл.",
        "total_income": "НИЙТ ОРЛОГО",
        "total_expense": "НИЙТ ЗАРЛАГА",
        "net": "ЦЭВЭР ҮЛДЭГДЭЛ",
        "monthly_title": "📅 Сарын орлого, зарлагын тайлан",
        "no_monthly": "📌 Одоогоор сарын мэдээлэл бүртгэгдээгүй байна.",
        "expense_cat": "🏷️ Зардлын ангилал",
        "no_exp_cat": "Зарлагын ангилал одоогоор алга.",
        "top_cp": "🏆 Гол харилцагчид",
        "no_cp": "Харилцагчийн мэдээлэл байхгүй байна.",
        "unknown": "Тодорхойгүй",
        "error": "Мэдээлэл ачаалахад алдаа гарлаа",
        "month": "Сар",
        "income": "Орлого (₮)",
        "expense": "Зарлага (₮)",
        "category": "Ангилал",
        "amount": "Дүн (₮)",
        "counterparty": "Харилцагч",
    },
    "en": {
        "page_title": "Finance Dashboard",
        "title": "📊 Finance Dashboard",
        "subtitle": "Overview of your income, expenses and net balance.",
        "total_income": "TOTAL INCOME",
        "total_expense": "TOTAL EXPENSE",
        "net": "NET BALANCE",
        "monthly_title": "📅 Monthly Income & Expense",
        "no_monthly": "📌 No monthly data yet.",
        "expense_cat": "🏷️ Expenses by Category",
        "no_exp_cat": "No expense categories yet.",
        "top_cp": "🏆 Top Counterparties",
        "no_cp": "No counterparty data yet.",
        "unknown": "Unknown",
        "error": "Error loading data",
        "month": "Month",
        "income": "Income (₮)",
        "expense": "Expense (₮)",
        "category": "Category",
        "amount": "Amount (₮)",
        "counterparty": "Counterparty",
    },
}[st.session_state["lang"]]

st.set_page_config(page_title=t["page_title"], page_icon="📊", layout="wide")
apply_global_styles()

st.markdown(f"## {t['title']}")
st.markdown(t["subtitle"])
st.markdown("---")

today = date.today()
date_from = today - timedelta(days=365)
date_to = today

try:
    with get_session() as session:
        df = transactions_export(session, date_from, date_to, include_transfers=False)

        if not df.empty and "kind" in df.columns:
            total_income = df[df["kind"] == "income"]["amount"].sum() if not df[df["kind"] == "income"].empty else 0
            total_expense = df[df["kind"] == "expense"]["amount"].abs().sum() if not df[df["kind"] == "expense"].empty else 0
        else:
            total_income = 0
            total_expense = 0

        net_balance = total_income - total_expense

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(t["total_income"], f"{float(total_income):,.2f} ₮")
        with col2:
            st.metric(t["total_expense"], f"{float(total_expense):,.2f} ₮")
        with col3:
            st.metric(t["net"], f"{float(net_balance):,.2f} ₮", delta=f"{float(net_balance):,.2f} ₮")

        st.markdown("###")
        st.subheader(t["monthly_title"])
        monthly_df = monthly_summary(session, date_from, date_to, include_transfers=False)

        if not monthly_df.empty:
            st.dataframe(
                monthly_df.rename(columns={"month": t["month"], "income": t["income"], "expense": t["expense"]}),
                use_container_width=True,
                hide_index=True,
            )
            st.bar_chart(monthly_df.set_index("month")[["income", "expense"]], use_container_width=True)
        else:
            st.info(t["no_monthly"])

        st.markdown("---")

        col_left, col_right = st.columns(2)
        with col_left:
            st.subheader(t["expense_cat"])
            exp_cat_df = expense_by_category(session, date_from, date_to, include_transfers=False)
            if not exp_cat_df.empty:
                st.dataframe(
                    exp_cat_df.rename(columns={"category": t["category"], "amount": t["amount"]}),
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info(t["no_exp_cat"])

        with col_right:
            st.subheader(t["top_cp"])
            cp_df = top_counterparties(session, date_from, date_to, include_transfers=False, n=5)
            if not cp_df.empty:
                cp_df = cp_df.copy()
                cp_df["counterparty"] = cp_df["counterparty"].fillna(t["unknown"])
                st.dataframe(
                    cp_df.rename(columns={"counterparty": t["counterparty"], "amount": t["amount"]}),
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info(t["no_cp"])
except Exception as error:
    st.error(f"{t['error']}: {error}")

render_footer()
