from decimal import Decimal

import pandas as pd
import streamlit as st
from sqlalchemy import select

from finance.classifier import classify_transactions
from finance.db import get_session
from finance.models import Category, Counterparty, Transaction

st.title("Гүйлгээ ангилах")
rerun_requested = False
kind_labels = {"income": "Орлого", "expense": "Зарлага", "transfer": "Шилжүүлэг"}

try:
	with get_session() as session:
		categories = session.scalars(select(Category).order_by(Category.kind, Category.name)).all()
		unclassified = session.scalars(
			select(Transaction).where(Transaction.category_source == "unclassified")
		).all()
		category_options = [
			f"{kind_labels.get(category.kind, category.kind)}: {category.name}"
			for category in categories
		]
		category_by_label = {
			f"{kind_labels.get(category.kind, category.kind)}: {category.name}": category.id
			for category in categories
		}
		counterparty_ids = {txn.counterparty_id for txn in unclassified if txn.counterparty_id}
		counterparties = {
			item.id: item
			for item in session.scalars(
				select(Counterparty).where(Counterparty.id.in_(counterparty_ids or {-1}))
			)
		}
		transactions_by_counterparty: dict[int, list[Transaction]] = {}
		for txn in unclassified:
			if txn.counterparty_id is not None:
				transactions_by_counterparty.setdefault(txn.counterparty_id, []).append(txn)

		st.sidebar.metric("Ангилаагүй гүйлгээ", len(unclassified))
		if not unclassified:
			st.success("Бүх гүйлгээ ангилагдсан байна.")
		elif not transactions_by_counterparty:
			st.info("Ангилаагүй гүйлгээнд харилцагч тодорхойгүй байна. Хуулгаа дахин импортлох эсвэл дараа нь ангилна уу.")
		else:
			records = []
			for counterparty_id, transactions in transactions_by_counterparty.items():
				counterparty = counterparties[counterparty_id]
				descriptions = list(dict.fromkeys(txn.description or "" for txn in transactions))[:3]
				incoming = sum((txn.amount for txn in transactions if txn.amount > 0), Decimal("0.00"))
				outgoing = sum((abs(txn.amount) for txn in transactions if txn.amount < 0), Decimal("0.00"))
				selected_category = next(
					(
						f"{kind_labels.get(category.kind, category.kind)}: {category.name}"
						for category in categories
						if category.id == counterparty.default_category_id
					),
					"",
				)
				records.append(
					{
						"counterparty_id": counterparty.id,
						"match_key": counterparty.match_key,
						"sample descriptions": "\n".join(descriptions),
						"txns": len(transactions),
						"in MNT": incoming,
						"out MNT": outgoing,
						"display_name": counterparty.display_name or "",
						"category": selected_category,
						"own account": bool(counterparty.is_own_account),
						"ask per txn": bool(counterparty.ask_per_txn),
					}
				)
			records.sort(key=lambda item: item["in MNT"] + item["out MNT"], reverse=True)
			frame = pd.DataFrame(records)

			with st.form("review-counterparties"):
				edited = st.data_editor(
					frame,
					key="counterparty-review-editor",
					hide_index=True,
					disabled=[
						"counterparty_id",
						"match_key",
						"sample descriptions",
						"txns",
						"in MNT",
						"out MNT",
					],
					column_config={
						"counterparty_id": None,
						"match_key": st.column_config.TextColumn("Таних түлхүүр"),
						"sample descriptions": st.column_config.TextColumn("Жишээ гүйлгээний утга"),
						"txns": st.column_config.NumberColumn("Гүйлгээний тоо", format="%d"),
						"in MNT": st.column_config.NumberColumn("Орлого (₮)", format="%.2f ₮"),
						"out MNT": st.column_config.NumberColumn("Зарлага (₮)", format="%.2f ₮"),
						"display_name": st.column_config.TextColumn("Харуулах нэр"),
						"category": st.column_config.SelectboxColumn(
							"Ангилал", options=[""] + category_options
						),
						"own account": st.column_config.CheckboxColumn("Өөрийн данс"),
						"ask per txn": st.column_config.CheckboxColumn("Гүйлгээ бүрээр асуух"),
					},
					alt="Ангилаагүй харилцагчид болон үндсэн ангиллын тохиргоо",
				)
				submitted = st.form_submit_button("Хадгалаад ангилах", type="primary")

			if submitted:
				changed_ids: list[int] = []
				edited_rows = edited.set_index("counterparty_id").to_dict("index")
				for counterparty_id, values in edited_rows.items():
					counterparty = counterparties[int(counterparty_id)]
					selected = values["category"] or ""
					counterparty.display_name = values["display_name"] or None
					counterparty.default_category_id = category_by_label.get(selected)
					counterparty.is_own_account = bool(values["own account"])
					counterparty.ask_per_txn = bool(values["ask per txn"])
					changed_ids.extend(
						session.scalars(
							select(Transaction.id).where(
								Transaction.counterparty_id == counterparty.id
							)
						).all()
					)
				classify_transactions(session, changed_ids)
				st.success("Харилцагчдын тохиргоог хадгалж, гүйлгээг дахин ангиллаа.")
				rerun_requested = True
except Exception as error:
	st.error(f"Харилцагчдыг ачаалж чадсангүй: {error}")

if rerun_requested:
	st.rerun()
