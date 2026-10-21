from datetime import date, timedelta
from decimal import Decimal

import plotly.express as px
import streamlit as st
from sqlalchemy import func, select, text

from finance.db import get_session
from finance.models import Category, Transaction
from finance.reports import expense_by_category, monthly_summary

st.set_page_config(page_title="Санхүү", page_icon=":material/account_balance_wallet:", layout="wide")


def dashboard() -> None:
	st.title("Хувийн санхүү")
	st.caption("Банкны хуулгаа импортолж, ангилж, тайлангаа хянаарай.")
	st.markdown(
		"""
		<style>
		:root {
			--finance-ink: #202344;
			--finance-muted: #727791;
			--finance-indigo: #4f46c8;
			--finance-violet: #7963df;
			--finance-teal: #168c83;
			--finance-border: rgba(83, 91, 145, 0.13);
		}

		[data-testid="stAppViewContainer"] {
			background: linear-gradient(135deg, #f7f8ff 0%, #f5f8fc 48%, #f1f8f7 100%);
		}

		[data-testid="stHeader"] {
			background: rgba(247, 248, 255, 0.76);
		}

		.main .block-container {
			max-width: 1500px;
			padding-top: 2rem;
			padding-bottom: 3rem;
		}

		[data-testid="stSidebar"] {
			background: linear-gradient(180deg, #202344 0%, #29264f 58%, #263d50 100%);
		}

		[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
		[data-testid="stSidebar"] [data-testid="stPageLink"] {
			color: #eef0ff;
		}

		h1, h2, h3 {
			color: var(--finance-ink);
			font-family: "Aptos", "Segoe UI", sans-serif;
			letter-spacing: 0;
		}

		.main h1 {
			font-weight: 760;
			margin-bottom: 0.25rem;
		}

		.main [data-testid="stCaptionContainer"] {
			color: var(--finance-muted);
			font-size: 1rem;
		}

		[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) [data-testid="stMetric"] {
			position: relative;
			min-height: 132px;
			padding: 1.15rem 1.25rem 1rem;
			border: 1px solid var(--finance-border);
			border-radius: 18px;
			background: linear-gradient(145deg, rgba(255, 255, 255, 0.98), rgba(246, 246, 255, 0.96));
			box-shadow: 0 10px 30px rgba(43, 47, 91, 0.08), 0 2px 7px rgba(43, 47, 91, 0.035);
			transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease;
		}

		[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) [data-testid="stMetric"]:hover {
			transform: translateY(-2px);
			border-color: rgba(93, 83, 204, 0.28);
			box-shadow: 0 15px 34px rgba(43, 47, 91, 0.12), 0 3px 9px rgba(43, 47, 91, 0.05);
		}

		[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) [data-testid="stColumn"]:nth-child(1) [data-testid="stMetric"] {
			border-top: 3px solid #5c52d6;
			background: linear-gradient(145deg, #ffffff 8%, #f1f0ff 100%);
		}

		[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) [data-testid="stColumn"]:nth-child(2) [data-testid="stMetric"] {
			border-top: 3px solid #d36e78;
			background: linear-gradient(145deg, #ffffff 8%, #fff3f4 100%);
		}

		[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) [data-testid="stColumn"]:nth-child(3) [data-testid="stMetric"] {
			border-top: 3px solid #168c83;
			background: linear-gradient(145deg, #ffffff 8%, #edf9f7 100%);
		}

		[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) [data-testid="stColumn"]:nth-child(4) [data-testid="stMetric"] {
			border-top: 3px solid #9872d8;
			background: linear-gradient(145deg, #ffffff 8%, #f7f1ff 100%);
		}

		[data-testid="stMetric"]::after {
			position: absolute;
			top: 0.9rem;
			right: 1rem;
			padding: 0.22rem 0.58rem;
			border: 1px solid rgba(97, 86, 196, 0.14);
			border-radius: 999px;
			background: rgba(239, 237, 255, 0.84);
			color: #554bb4;
			content: "30 өдөр";
			font-size: 0.68rem;
			font-weight: 700;
			line-height: 1.35;
		}

		[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) [data-testid="stColumn"]:nth-child(2) [data-testid="stMetric"]::after {
			border-color: rgba(201, 92, 107, 0.18);
			background: #fff0f1;
			color: #a94f5c;
			content: "30 өдөр";
		}

		[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) [data-testid="stColumn"]:nth-child(3) [data-testid="stMetric"]::after {
			border-color: rgba(22, 140, 131, 0.2);
			background: #e8f7f4;
			color: #11756e;
			content: "Орлого − зарлага";
		}

		[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) [data-testid="stColumn"]:nth-child(4) [data-testid="stMetric"]::after {
			border-color: rgba(129, 95, 199, 0.2);
			background: #f2edff;
			color: #7050b2;
			content: "Хяналт";
		}

		[data-testid="stMetricLabel"] {
			padding-right: 5.5rem;
			color: #626985;
			font-size: 0.86rem;
			font-weight: 650;
		}

		[data-testid="stMetricValue"] {
			margin-top: 0.55rem;
			color: var(--finance-ink);
			font-size: 1.7rem;
			font-weight: 760;
			line-height: 1.2;
		}

		[data-testid="stPageLink"] a,
		.stButton > button {
			border: 1px solid rgba(87, 79, 183, 0.2);
			border-radius: 12px;
			background: linear-gradient(135deg, #ffffff, #f5f3ff);
			color: #403a9a;
			font-weight: 650;
			transition: transform 150ms ease, box-shadow 150ms ease, border-color 150ms ease;
		}

		[data-testid="stPageLink"] a:hover,
		.stButton > button:hover {
			transform: translateY(-1px);
			border-color: rgba(87, 79, 183, 0.45);
			box-shadow: 0 7px 18px rgba(57, 55, 123, 0.1);
			color: #302878;
		}

		[data-testid="stPlotlyChart"] {
			padding: 0.5rem;
			border: 1px solid var(--finance-border);
			border-radius: 18px;
			background: rgba(255, 255, 255, 0.82);
			box-shadow: 0 8px 25px rgba(43, 47, 91, 0.055);
		}

		@media (max-width: 760px) {
			.main .block-container {
				padding: 1.25rem 1rem 2rem;
			}

			[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) [data-testid="stMetric"] {
				min-height: 118px;
				padding: 1rem;
				border-radius: 15px;
			}

			[data-testid="stMetricValue"] {
				font-size: 1.35rem;
			}

			[data-testid="stMetric"]::after {
				top: 0.7rem;
				right: 0.7rem;
			}
		}
		</style>
		""",
		unsafe_allow_html=True,
	)

	navigation = st.columns(4, vertical_alignment="center")
	navigation[0].page_link(page_import, label="Хуулга импортлох", icon=":material/upload_file:")
	navigation[1].page_link(page_review, label="Гүйлгээ ангилах", icon=":material/rule:")
	navigation[2].page_link(page_txns, label="Бүх гүйлгээ", icon=":material/list_alt:")
	navigation[3].page_link(page_reports, label="Тайлан мэдээ", icon=":material/monitoring:")

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
			f"Мэдээллийн сантай холбогдож чадсангүй. Тохиргоо болон сангийн эхлүүлэлтийг шалгана уу. ({error})",
		title="Өгөгдлийн сангийн алдаа",
		)


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
