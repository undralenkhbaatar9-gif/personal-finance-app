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
from finance.ui import apply_global_styles, render_footer, style_plotly_chart

apply_global_styles()
st.title("Тайлан мэдээ")
today = date.today()
with st.sidebar:
	date_range = st.date_input(
		"Хугацааны хүрээ",
		value=(today - timedelta(days=180), today),
		key="reports-date-range",
	)
	include_transfers = st.toggle("Шилжүүлгийг оруулах")
	include_unclassified = st.toggle("Ангилаагүй гүйлгээг татах файлд оруулах")

if isinstance(date_range, tuple) and len(date_range) == 2:
	date_from, date_to = date_range
else:
	date_from = date_to = date_range

try:
	with st.spinner("Тайлангийн мэдээллийг тооцоолж байна..."):
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
	export = export.rename(
		columns={
			"id": "Гүйлгээний дугаар",
			"date": "Огноо",
			"amount": "Дүн",
			"description": "Гүйлгээний утга",
			"note": "Тэмдэглэл",
			"category_source": "Ангилсан арга",
			"category_id": "Ангиллын дугаар",
			"kind": "Ангиллын төрөл",
			"category": "Ангилал",
			"counterparty": "Харилцагч",
			"match_key": "Таних түлхүүр",
			"account": "Дансны нэр",
			"account_no": "Дансны дугаар",
		}
	)
	if "Ангиллын төрөл" in export.columns:
		export["Ангиллын төрөл"] = export["Ангиллын төрөл"].map(
			{"income": "Орлого", "expense": "Зарлага", "transfer": "Шилжүүлэг"}
		)
	if "Ангилсан арга" in export.columns:
		export["Ангилсан арга"] = export["Ангилсан арга"].map(
			{
				"manual": "Гараар ангилсан",
				"transfer": "Шилжүүлэг",
				"counterparty": "Харилцагчийн тохиргоо",
				"rule": "Дүрмээр ангилсан",
				"unclassified": "Ангилаагүй",
			}
		)

	income_total = sum(monthly["income"], Decimal("0.00")) if not monthly.empty else Decimal("0.00")
	expense_total = sum(monthly["expense"], Decimal("0.00")) if not monthly.empty else Decimal("0.00")
	net_total = income_total - expense_total
	savings_rate = (net_total / income_total * 100) if income_total else Decimal("0.00")
	with st.container(horizontal=True):
		st.metric("Орлого", f"{income_total:,.2f} ₮")
		st.metric("Зарлага", f"{expense_total:,.2f} ₮")
		st.metric("Цэвэр мөнгөн урсгал", f"{net_total:,.2f} ₮")
		st.metric("Хуримтлалын хувь", f"{savings_rate:.1f}%")
	if unclassified:
		st.warning(f"Энэ хугацаанд ангилаагүй гүйлгээний нийт дүн {unclassified:,.2f} ₮ байна.")

	st.subheader("Сар бүрийн орлого ба зарлага")
	if monthly.empty:
		st.info("Энэ хугацаанд ангилсан орлого, зарлагын гүйлгээ алга байна.")
	else:
		chart_data = monthly.melt(
			id_vars="month", value_vars=["income", "expense"],
			var_name="type", value_name="amount",
		)
		chart_data["type"] = chart_data["type"].map({"income": "Орлого", "expense": "Зарлага"})
		chart_data["amount"] = chart_data["amount"].map(float)
		chart = px.bar(
			chart_data,
			x="month",
			y="amount",
			color="type",
			barmode="group",
			color_discrete_map={"Орлого": "#55e39f", "Зарлага": "#ff789b"},
			labels={"month": "Сар", "amount": "Дүн (₮)", "type": "Гүйлгээний төрөл"},
		)
		st.plotly_chart(style_plotly_chart(chart), alt="Сар бүрийн орлого ба зарлагын харьцуулалт")

	st.subheader("Ангиллаарх зарлага")
	if expenses.empty:
		st.info("Энэ хугацаанд ангилсан зарлагын гүйлгээ алга байна.")
	else:
		expense_chart = expenses.copy()
		expense_chart["amount"] = expense_chart["amount"].map(float)
		chart = px.bar(
			expense_chart,
			x="amount",
			y="category",
			orientation="h",
			color_discrete_sequence=["#36e2cc"],
			labels={"amount": "Дүн (₮)", "category": "Ангилал"},
		)
		st.plotly_chart(style_plotly_chart(chart), alt="Ангилал тус бүрийн зарлагын дүн")
		st.dataframe(
			expenses.rename(columns={"category": "Ангилал", "amount": "Дүн"}).assign(
				Дүн=expenses["amount"].map(lambda amount: f"{amount:,.2f} ₮")
			),
			hide_index=True,
			alt="Ангилал тус бүрийн зарлагын нийлбэр",
		)

	st.subheader("Их дүнтэй харилцагчид")
	st.dataframe(
		counterparties.rename(columns={"counterparty": "Харилцагч", "amount": "Дүн"}).assign(
			Дүн=counterparties["amount"].map(lambda amount: f"{amount:,.2f} ₮")
		),
		hide_index=True,
		alt="Гүйлгээний дүнгээр эрэмбэлсэн харилцагчид",
	)

	csv_data = export.to_csv(index=False).encode("utf-8-sig")
	xlsx_buffer = BytesIO()
	with pd.ExcelWriter(xlsx_buffer, engine="openpyxl") as writer:
		export.to_excel(writer, index=False, sheet_name="Гүйлгээнүүд")
	with st.container(horizontal=True):
		st.download_button("Текстэн файл татах", csv_data, "гүйлгээ.csv", mime="text/csv")
		st.download_button(
			"Хүснэгтэн файл татах",
			xlsx_buffer.getvalue(),
			"гүйлгээ.xlsx",
			mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
		)
except Exception as error:
	st.error("Тайланг ачаалж чадсангүй. Хугацаа болон өгөгдлийн сангийн холболтыг шалгана уу.")

render_footer()
