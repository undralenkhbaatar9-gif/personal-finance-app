from datetime import date, timedelta

import pandas as pd
import streamlit as st
from sqlalchemy import or_, select

from finance.db import get_session
from finance.models import Account, Category, Counterparty, Rule, Transaction

st.title("Transactions")
rerun_requested = False
today = date.today()
with st.sidebar:
	date_range = st.date_input(
		"Date range",
		value=(today - timedelta(days=180), today),
		key="transaction-date-range",
	)
	search_text = st.text_input("Search description or counterparty", type="search")
	unclassified_only = st.checkbox("Unclassified only")

if isinstance(date_range, tuple) and len(date_range) == 2:
	date_from, date_to = date_range
else:
	date_from = date_to = date_range

try:
	with get_session() as session:
		accounts = session.scalars(select(Account).order_by(Account.account_no)).all()
		categories = session.scalars(select(Category).order_by(Category.kind, Category.name)).all()
		account_options = {"All accounts": None}
		account_options.update(
			{
				f"{account.nickname or account.account_no}": account.id
				for account in accounts
			}
		)
		category_options = {"All categories": None, "Unclassified": -1}
		category_options.update(
			{
				f"{category.kind}: {category.name}": category.id
				for category in categories
			}
		)
		selected_account = st.sidebar.selectbox("Account", list(account_options))
		selected_category = st.sidebar.selectbox("Category", list(category_options))

		query = (
			select(Transaction, Account, Category, Counterparty)
			.join(Account, Account.id == Transaction.account_id)
			.outerjoin(Category, Category.id == Transaction.category_id)
			.outerjoin(Counterparty, Counterparty.id == Transaction.counterparty_id)
			.where(
				Transaction.txn_datetime >= date_from,
				Transaction.txn_datetime < date_to + timedelta(days=1),
			)
		)
		if account_options[selected_account] is not None:
			query = query.where(Transaction.account_id == account_options[selected_account])
		if unclassified_only or category_options[selected_category] == -1:
			query = query.where(Transaction.category_id.is_(None))
		elif category_options[selected_category] is not None:
			query = query.where(Transaction.category_id == category_options[selected_category])
		if search_text:
			pattern = f"%{search_text}%"
			query = query.where(
				or_(
					Transaction.description.ilike(pattern),
					Counterparty.display_name.ilike(pattern),
					Counterparty.match_key.ilike(pattern),
				)
			)
		rows = session.execute(
			query.order_by(Transaction.txn_datetime.desc()).limit(2000)
		).all()
		category_labels = {
			category.id: f"{category.kind}: {category.name}" for category in categories
		}
		editor_rows = [
			{
				"txn_id": txn.id,
				"date": txn.txn_datetime,
				"account": account.nickname or account.account_no,
				"amount": txn.amount,
				"description": txn.description or "",
				"counterparty": cp.display_name if cp and cp.display_name else cp.match_key if cp else "",
				"match_key": cp.match_key if cp else "",
				"category": category_labels.get(txn.category_id, "Unclassified"),
				"source": txn.category_source,
				"note": txn.note or "",
				"make rule": False,
			}
			for txn, account, _category, cp in rows
		]
		original = {row["txn_id"]: row for row in editor_rows}
		frame = pd.DataFrame(
			editor_rows,
			columns=[
				"txn_id", "date", "account", "amount", "description", "counterparty",
				"match_key", "category", "source", "note", "make rule",
			],
		)
		category_labels_list = ["Unclassified"] + list(category_labels.values())

		with st.form("transaction-editor"):
			edited = st.data_editor(
				frame,
				key="transactions-editor",
				hide_index=True,
				num_rows="fixed",
				disabled=["txn_id", "date", "account", "amount", "description", "counterparty", "match_key", "source"],
				column_config={
					"txn_id": None,
					"date": st.column_config.DatetimeColumn("Date"),
					"amount": st.column_config.NumberColumn("Amount", format="%.2f ₮"),
					"category": st.column_config.SelectboxColumn("Category", options=category_labels_list),
					"source": st.column_config.TextColumn("Source"),
					"note": st.column_config.TextColumn("Note"),
					"make rule": st.column_config.CheckboxColumn("Make rule"),
					"match_key": None,
				},
				alt="Transactions with editable category, note, and rule action",
			)
			submitted = st.form_submit_button("Save changes", type="primary")

		if submitted:
			saved = 0
			rules_added = 0
			for row in edited.to_dict("records"):
				txn_id = int(row["txn_id"])
				previous = original[txn_id]
				transaction = session.get(Transaction, txn_id)
				if transaction is None:
					continue
				category_label = row["category"]
				category_id = next(
					(key for key, label in category_labels.items() if label == category_label),
					None,
				)
				if category_id != transaction.category_id:
					transaction.category_id = category_id
					transaction.category_source = "manual"
					saved += 1
				if (row["note"] or "") != (previous["note"] or ""):
					transaction.note = row["note"] or None
					saved += 1
				match_key = row["match_key"]
				if row["make rule"] and match_key and category_id is not None:
					existing_rule = session.scalar(
						select(Rule.id).where(
							Rule.field == "match_key",
							Rule.match_type == "equals",
							Rule.pattern == match_key,
							Rule.category_id == category_id,
							Rule.active.is_(True),
						)
					)
					if existing_rule is None:
						session.add(
							Rule(
								priority=50,
								field="match_key",
								match_type="equals",
								pattern=match_key,
								category_id=category_id,
								active=True,
							)
						)
						rules_added += 1
			st.success(f"Saved {saved} transaction changes and created {rules_added} rules.")
			rerun_requested = True
except Exception as error:
	st.error(f"Could not load transactions: {error}")

if rerun_requested:
	st.rerun()
