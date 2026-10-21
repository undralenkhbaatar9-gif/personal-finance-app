from datetime import date, timedelta
from decimal import Decimal

import plotly.express as px
import streamlit as st
from sqlalchemy import func, select, text

from finance.db import get_session
from finance.models import Category, Transaction
from finance.reports import expense_by_category, monthly_summary

st.set_page_config(page_title="Finance", page_icon=":material/account_balance_wallet:", layout="wide")


def dashboard() -> None:
	st.title("Хувийн санхүү")
	st.caption("Банкны хуулгаа импортолж, ангилж, тайлангаа хянаарай.")

	navigation = st.columns(4, vertical_alignment="center")
	navigation[0].page_link(page_import, label="Import statement", icon=":material/upload_file:")
	navigation[1].page_link(page_review, label="Review transactions", icon=":material/rule:")
	navigation[2].page_link(page_txns, label="Transactions", icon=":material/list_alt:")
	navigation[3].page_link(page_reports, label="Reports", icon=":material/monitoring:")

	today = date.today()
	month_start = today - timedelta(days=179)
	recent_start = today - timedelta(days=29)
	try:
		with get_session() as session:
			session.execute(text("SELECT 1"))
			income = session.scalar(
				select(func.coalesce(func.sum(Transaction.amount), 0))
				.join(Category, Category.id == Transaction.category_id)
				.where(
					Transaction.txn_datetime >= recent_start,
					Transaction.amount > 0,
					Category.kind == "income",
					Category.in_reports.is_(True),
				)
			) or Decimal("0.00")
			expense = session.scalar(
				select(func.coalesce(func.sum(func.abs(Transaction.amount)), 0))
				.join(Category, Category.id == Transaction.category_id)
				.where(
					Transaction.txn_datetime >= recent_start,
					Transaction.amount < 0,
					Category.kind == "expense",
					Category.in_reports.is_(True),
				)
			) or Decimal("0.00")
			unclassified = session.scalar(
				select(func.count()).select_from(Transaction).where(Transaction.category_id.is_(None))
			) or 0
			monthly = monthly_summary(session, month_start, today)
			category_expenses = expense_by_category(session, month_start, today)

		net = income - expense
		with st.container(horizontal=True):
			st.metric("Income (30 days)", f"{income:,.2f} ₮", border=True)
			st.metric("Expenses (30 days)", f"{expense:,.2f} ₮", border=True)
			st.metric("Net (30 days)", f"{net:,.2f} ₮", border=True)
			st.metric("Needs review", f"{unclassified:,}", border=True)

		chart_column, category_column = st.columns(2, gap="large")
		with chart_column:
			st.subheader("Monthly cash flow")
			if monthly.empty:
				st.info("Import a statement to see monthly income and expenses.")
			else:
				chart_data = monthly.copy()
				chart = px.bar(
					chart_data,
					x="month",
					y=["income", "expense"],
					barmode="group",
					labels={"month": "Month", "value": "MNT", "variable": "Flow"},
					color_discrete_map={"income": "#16876f", "expense": "#d2644b"},
				)
				chart.update_layout(margin=dict(l=8, r=8, t=12, b=8), legend_title_text="")
				st.plotly_chart(chart, alt="Monthly income and expense for the last six months")

		with category_column:
			st.subheader("Spending by category")
			if category_expenses.empty:
				st.info("No categorized expenses in the last six months.")
			else:
				chart_data = category_expenses.head(8).copy()
				chart = px.bar(
					chart_data.sort_values("amount"),
					x="amount",
					y="category",
					orientation="h",
					labels={"amount": "MNT", "category": "Category"},
					color_discrete_sequence=["#4b7f73"],
				)
				chart.update_layout(margin=dict(l=8, r=8, t=12, b=8), yaxis_title="")
				st.plotly_chart(chart, alt="Top spending categories over the last six months")
	except Exception as error:
		st.error(f"Database unavailable: {error}", title="Check DATABASE_URL and initialize the database")


page_dashboard = st.Page(
	dashboard,
	title="Dashboard",
	icon=":material/home:",
	default=True,
)
page_import = st.Page(
	"pages/1_Import.py",
	title="Import statement",
	icon=":material/upload_file:",
)
page_review = st.Page(
	"pages/2_Review.py",
	title="Review transactions",
	icon=":material/rule:",
)
page_txns = st.Page(
	"pages/3_Transactions.py",
	title="Transactions",
	icon=":material/list_alt:",
)
page_reports = st.Page(
	"pages/4_Reports.py",
	title="Reports",
	icon=":material/monitoring:",
)
page_settings = st.Page(
	"pages/5_Settings.py",
	title="Settings",
	icon=":material/settings:",
)

pg = st.navigation(
	[
		page_dashboard,
		page_import,
		page_review,
		page_txns,
		page_reports,
		page_settings,
	],
	position="sidebar",
)
pg.run()
