from datetime import date, timedelta
from decimal import Decimal
from io import BytesIO

import pandas as pd
import plotly.express as px
import streamlit as st

from finance.db import get_session
from finance.reports import (
	expense_by_category,
	monthly_summary,
	top_counterparties,
	transactions_export,
	unclassified_total,
)

st.title("Reports")
today = date.today()
with st.sidebar:
	date_range = st.date_input(
		"Date range",
		value=(today - timedelta(days=180), today),
		key="reports-date-range",
	)
	include_transfers = st.toggle("Include transfers")
	include_unclassified = st.toggle("Include unclassified in downloads")

if isinstance(date_range, tuple) and len(date_range) == 2:
	date_from, date_to = date_range
else:
	date_from = date_to = date_range

try:
	with get_session() as session:
		monthly = monthly_summary(session, date_from, date_to, include_transfers)
		expenses = expense_by_category(session, date_from, date_to, include_transfers)
		counterparties = top_counterparties(session, date_from, date_to, include_transfers)
		export = transactions_export(
			session,
			date_from,
			date_to,
			include_transfers,
			include_unclassified,
		)
		unclassified = unclassified_total(session, date_from, date_to)

	income_total = sum(monthly["income"], Decimal("0.00")) if not monthly.empty else Decimal("0.00")
	expense_total = sum(monthly["expense"], Decimal("0.00")) if not monthly.empty else Decimal("0.00")
	net_total = income_total - expense_total
	savings_rate = (net_total / income_total * 100) if income_total else Decimal("0.00")
	with st.container(horizontal=True):
		st.metric("Income", f"{income_total:,.2f} ₮")
		st.metric("Expense", f"{expense_total:,.2f} ₮")
		st.metric("Net", f"{net_total:,.2f} ₮")
		st.metric("Savings rate", f"{savings_rate:.1f}%")
	if unclassified:
		st.warning(f"Unclassified transactions total {unclassified:,.2f} ₮ in this date range.")

	st.subheader("Monthly income and expense")
	if monthly.empty:
		st.info("No classified income or expenses in this date range.")
	else:
		chart_data = monthly.melt(
			id_vars="month", value_vars=["income", "expense"],
			var_name="type", value_name="amount",
		)
		chart_data["amount"] = chart_data["amount"].map(float)
		chart = px.bar(chart_data, x="month", y="amount", color="type", barmode="group")
		st.plotly_chart(chart, alt="Monthly income compared with expenses")

	st.subheader("Expenses by category")
	if expenses.empty:
		st.info("No categorized expenses in this date range.")
	else:
		expense_chart = expenses.copy()
		expense_chart["amount"] = expense_chart["amount"].map(float)
		chart = px.bar(expense_chart, x="amount", y="category", orientation="h")
		st.plotly_chart(chart, alt="Expenses grouped by category")
		st.dataframe(
			expenses.assign(amount=expenses["amount"].map(lambda amount: f"{amount:,.2f} ₮")),
			hide_index=True,
			alt="Expense totals by category",
		)

	st.subheader("Top counterparties")
	st.dataframe(
		counterparties.assign(amount=counterparties["amount"].map(lambda amount: f"{amount:,.2f} ₮")),
		hide_index=True,
		alt="Top counterparties by transaction amount",
	)

	csv_data = export.to_csv(index=False).encode("utf-8-sig")
	xlsx_buffer = BytesIO()
	with pd.ExcelWriter(xlsx_buffer, engine="openpyxl") as writer:
		export.to_excel(writer, index=False, sheet_name="Transactions")
	with st.container(horizontal=True):
		st.download_button("Download CSV", csv_data, "transactions.csv", mime="text/csv")
		st.download_button(
			"Download XLSX",
			xlsx_buffer.getvalue(),
			"transactions.xlsx",
			mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
		)
except Exception as error:
	st.error(f"Could not load reports: {error}")
