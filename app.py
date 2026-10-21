from datetime import date, timedelta
from decimal import Decimal

import streamlit as st
from sqlalchemy import func, select, text

from finance.db import get_session
from finance.models import Category, Transaction

st.set_page_config(page_title="Finance", page_icon=":material/account_balance_wallet:", layout="wide")
st.title("Хувийн санхүү")
st.caption("Банкны хуулгаа импортолж, ангилж, тайлангаа хянаарай.")

with st.container(horizontal=True):
	st.page_link("pages/1_Import.py", label="Import statement", icon=":material/upload_file:")
	st.page_link("pages/2_Review.py", label="Review transactions", icon=":material/rule:")
	st.page_link("pages/3_Transactions.py", label="Transactions", icon=":material/list_alt:")
	st.page_link("pages/4_Reports.py", label="Reports", icon=":material/monitoring:")

today = date.today()
start_date = today - timedelta(days=29)
try:
	with get_session() as session:
		session.execute(text("SELECT 1"))
		st.success("Database connected")
		income = session.scalar(
			select(func.coalesce(func.sum(Transaction.amount), 0))
			.join(Category, Category.id == Transaction.category_id)
			.where(
				Transaction.txn_datetime >= start_date,
				Transaction.amount > 0,
				Category.kind == "income",
				Category.in_reports.is_(True),
			)
		) or Decimal("0.00")
		expense = session.scalar(
			select(func.coalesce(func.sum(func.abs(Transaction.amount)), 0))
			.join(Category, Category.id == Transaction.category_id)
			.where(
				Transaction.txn_datetime >= start_date,
				Transaction.amount < 0,
				Category.kind == "expense",
				Category.in_reports.is_(True),
			)
		) or Decimal("0.00")
		unclassified = session.scalar(
			select(func.count()).select_from(Transaction).where(Transaction.category_id.is_(None))
		) or 0
	with st.container(horizontal=True):
		st.metric("Income, last 30 days", f"{income:,.2f} ₮")
		st.metric("Expense, last 30 days", f"{expense:,.2f} ₮")
		st.metric("Unclassified transactions", f"{unclassified:,}")
except Exception as error:
	st.error(f"Database unavailable: {error}", title="Check DATABASE_URL and initialize the database")
