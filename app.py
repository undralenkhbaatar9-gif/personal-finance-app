from datetime import date, timedelta
from decimal import Decimal

import plotly.express as px
import streamlit as st
from sqlalchemy import func, select, text

from finance.db import get_session
from finance.models import Category, Transaction
from finance.reports import expense_by_category, monthly_summary
from finance.ui import apply_global_styles, render_footer

st.set_page_config(page_title="Санхүү", page_icon=":material/account_balance_wallet:", layout="wide")


def dashboard() -> None:
	apply_global_styles()
	st.title("Хувийн санхүү")
	st.caption("Банкны хуулгаа импортолж, ангилж, тайлангаа хянаарай.")

	navigation = st.columns(4, vertical_alignment="center")
	navigation[0].page_link(page_import, label="Хуулга импортлох", icon=":material/upload_file:")
	navigation[1].page_link(page_review, label="Гүйлгээ ангилах", icon=":material/rule:")
	navigation[2].page_link(page_txns, label="Бүх гүйлгээ", icon=":material/list_alt:")
	navigation[3].page_link(page_reports, label="Тайлан мэдээ", icon=":material/monitoring:")

	today = date.today()
	month_start = today - timedelta(days=179)
	recent_start = today - timedelta(days=29)
	try:
		with st.spinner("Хянах самбарын мэдээллийг ачаалж байна..."):
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
		with st.container(key="finance-dashboard-kpis", horizontal=True):
			st.metric("Орлого (Сүүлийн 30 день)", f"{income:,.2f} ₮", border=True)
			st.metric("Зарлага (Сүүлийн 30 день)", f"{expense:,.2f} ₮", border=True)
			st.metric("Цэвэр ашиг / Мөнгөн урсгал", f"{net:,.2f} ₮", border=True)
			st.metric("Ангилах шаардлагатай", f"{unclassified:,}", border=True)

		chart_column, category_column = st.columns(2, gap="large")
		with chart_column:
			st.subheader("Сар бүрийн мөнгөн урсгал")
			if monthly.empty:
				st.info("Сар бүрийн орлого, зарлагыг харахын тулд банкийн хуулгаа импортлоорой.")
			else:
				chart_data = monthly.rename(
					columns={"income": "Орлого", "expense": "Зарлага"}
				)
				chart = px.bar(
					chart_data,
					x="month",
					y=["Орлого", "Зарлага"],
					barmode="group",
					labels={"month": "Сар", "value": "₮", "variable": "Орлого, зарлага"},
					color_discrete_map={"Орлого": "#16876f", "Зарлага": "#d2644b"},
				)
				chart.update_layout(
					margin=dict(l=8, r=8, t=12, b=8),
					legend_title_text="",
					paper_bgcolor="rgba(0,0,0,0)",
					plot_bgcolor="rgba(0,0,0,0)",
					font=dict(family="Aptos, Segoe UI, sans-serif", color="#5f6580", size=12),
					hoverlabel=dict(bgcolor="#24264a", bordercolor="#7770d4", font=dict(color="#ffffff")),
					hovermode="x unified",
				)
				chart.update_xaxes(showgrid=False, linecolor="rgba(75,81,125,0.18)")
				chart.update_yaxes(gridcolor="rgba(75,81,125,0.1)", zerolinecolor="rgba(75,81,125,0.16)")
				st.plotly_chart(chart, alt="Сүүлийн зургаан сарын орлого ба зарлагын харьцуулалт")

		with category_column:
			st.subheader("Ангиллаарх зарлага")
			if category_expenses.empty:
				st.info("Сүүлийн 6 сард ангилагдсан зарлагын гүйлгээ одоогоор алга байна.")
			else:
				chart_data = category_expenses.head(8).copy()
				chart = px.bar(
					chart_data.sort_values("amount"),
					x="amount",
					y="category",
					orientation="h",
					labels={"amount": "Дүн (₮)", "category": "Ангилал"},
					color_discrete_sequence=["#4b7f73"],
				)
				chart.update_layout(
					margin=dict(l=8, r=8, t=12, b=8),
					yaxis_title="",
					paper_bgcolor="rgba(0,0,0,0)",
					plot_bgcolor="rgba(0,0,0,0)",
					font=dict(family="Aptos, Segoe UI, sans-serif", color="#5f6580", size=12),
					hoverlabel=dict(bgcolor="#24264a", bordercolor="#168c83", font=dict(color="#ffffff")),
				)
				chart.update_xaxes(gridcolor="rgba(75,81,125,0.1)", zerolinecolor="rgba(75,81,125,0.16)")
				chart.update_yaxes(showgrid=False)
				st.plotly_chart(chart, alt="Сүүлийн зургаан сарын зарлага ангиллаар")
	except Exception as error:
		st.error(
			"Мэдээллийн сантай холбогдож чадсангүй. DATABASE_URL болон өгөгдлийн сангийн эхлүүлэлтийг шалгана уу.",
			title="Өгөгдлийн сангийн алдаа",
		)

	render_footer()


page_dashboard = st.Page(
	dashboard,
	title="Хянах самбар",
	icon=":material/home:",
	default=True,
)
page_import = st.Page(
	"pages/1_Import.py",
	title="Хуулга импортлох",
	icon=":material/upload_file:",
)
page_review = st.Page(
	"pages/2_Review.py",
	title="Гүйлгээ ангилах",
	icon=":material/rule:",
)
page_txns = st.Page(
	"pages/3_Transactions.py",
	title="Бүх гүйлгээ",
	icon=":material/list_alt:",
)
page_reports = st.Page(
	"pages/4_Reports.py",
	title="Тайлан мэдээ",
	icon=":material/monitoring:",
)
page_settings = st.Page(
	"pages/5_Settings.py",
	title="Тохиргоо",
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
