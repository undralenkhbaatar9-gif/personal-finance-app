from datetime import date, datetime, timedelta
from decimal import Decimal
from io import BytesIO

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import func, select

from finance.db import get_session
from finance.models import Budget, Category, Transaction
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
budget_start = today.replace(day=1)
budget_end = (
	date(budget_start.year + 1, 1, 1)
	if budget_start.month == 12
	else date(budget_start.year, budget_start.month + 1, 1)
)
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
			budget_categories = session.scalars(
				select(Category).where(Category.kind == "expense").order_by(Category.name)
			).all()
			budgets = session.scalars(select(Budget)).all()
			budget_category_ids = [category.id for category in budget_categories]
			spending_rows = session.execute(
				select(Transaction.category_id, func.sum(func.abs(Transaction.amount)))
				.where(
					Transaction.category_id.in_(budget_category_ids or [-1]),
					Transaction.amount < 0,
					Transaction.txn_datetime >= budget_start,
					Transaction.txn_datetime < budget_end,
				)
				.group_by(Transaction.category_id)
			).all()
			budget_by_category = {
				budget.category_id: budget.monthly_limit for budget in budgets
			}
			spent_by_category = {
				category_id: amount or Decimal("0.00")
				for category_id, amount in spending_rows
			}
			budget_frame = pd.DataFrame(
				[
					{
						"category_id": category.id,
						"category": category.name,
						"monthly_limit": budget_by_category.get(category.id, Decimal("0.00")),
						"spent": spent_by_category.get(category.id, Decimal("0.00")),
					}
					for category in budget_categories
				],
				columns=["category_id", "category", "monthly_limit", "spent"],
			)
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

	st.subheader("Сарын төсөв ба ахиц")
	st.caption(f"{today.year} оны {today.month}-р сарын зарлагын төсвөө ангилал тус бүрээр тохируулна уу.")
	with st.form("monthly-budget-form"):
		edited_budgets = st.data_editor(
			budget_frame,
			key="monthly-budget-editor",
			hide_index=True,
			disabled=["category_id", "category", "spent"],
			column_config={
				"category_id": None,
				"category": st.column_config.TextColumn("Ангилал"),
				"monthly_limit": st.column_config.NumberColumn(
					"Сарын төсөв (₮)", min_value=0.0, step=10000.0, format="%.2f ₮"
				),
				"spent": st.column_config.NumberColumn("Энэ сард зарцуулсан (₮)", format="%.2f ₮"),
			},
			alt="Ангилал бүрийн сарын төсөв болон тухайн сарын зарлага",
		)
		budget_submitted = st.form_submit_button("Төсөв хадгалах", type="primary")
	if budget_submitted:
		with st.spinner("Сарын төсвийг хадгалж байна..."):
			with get_session() as session:
				for row in edited_budgets.to_dict("records"):
					category_id = int(row["category_id"])
					limit_value = Decimal(str(row["monthly_limit"] or 0)).quantize(Decimal("0.01"))
					budget = session.scalar(
						select(Budget).where(Budget.category_id == category_id)
					)
					if limit_value > 0:
						if budget is None:
							session.add(Budget(category_id=category_id, monthly_limit=limit_value))
						else:
							budget.monthly_limit = limit_value
					elif budget is not None:
						session.delete(budget)
		st.toast("Сарын төсвийг амжилттай хадгаллаа.")
		budget_frame = edited_budgets.copy()

	configured_budgets = budget_frame[budget_frame["monthly_limit"] > 0]
	if configured_budgets.empty:
		st.info("Ангиллын сарын төсөв хараахан тохируулаагүй байна.")
	else:
		for budget_row in configured_budgets.to_dict("records"):
			limit_value = Decimal(str(budget_row["monthly_limit"]))
			spent_value = Decimal(str(budget_row["spent"]))
			usage_percent = spent_value / limit_value * Decimal("100")
			with st.container(border=True):
				st.markdown(f"**{budget_row['category']}**")
				st.progress(
					min(float(usage_percent / Decimal("100")), 1.0),
					text=f"{spent_value:,.2f} ₮ / {limit_value:,.2f} ₮ · {usage_percent:.0f}%",
				)
				if usage_percent > 100:
					st.error("Төсвийн хязгаарыг давлаа.")
				elif usage_percent >= 80:
					st.warning("Төсвийн 80 хувьд хүрсэн байна.")
				else:
					st.success("Төсвийн зарцуулалт хэвийн байна.")

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
