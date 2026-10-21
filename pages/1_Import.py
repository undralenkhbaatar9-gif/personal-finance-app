from dataclasses import asdict
from pathlib import Path
from tempfile import TemporaryDirectory

import streamlit as st
from sqlalchemy import select

from finance.db import get_session
from finance.importer import DuplicateFileError, ValidationError, import_statement, validate
from finance.models import Import
from finance.parsers import PARSERS

st.title("Import statement")
bank_code = st.selectbox(
	"Bank",
	options=list(PARSERS),
	format_func=lambda code: PARSERS[code].name,
)
uploaded_file = st.file_uploader("Bank statement", type=["xlsx", "csv"])

if uploaded_file is not None:
	suffix = Path(uploaded_file.name).suffix.lower()
	with TemporaryDirectory() as temporary_folder:
		temporary_path = Path(temporary_folder) / f"statement{suffix}"
		temporary_path.write_bytes(uploaded_file.getvalue())
		try:
			info, transactions = PARSERS[bank_code].parse(temporary_path)
			errors = validate(info, transactions)
			st.subheader("Statement details")
			st.table(
				{
					"Account": info.account_no,
					"IBAN": info.iban or "",
					"Currency": info.currency,
					"Period from": info.period_from,
					"Period to": info.period_to,
					"Rows parsed": len(transactions),
					"Credit total": f"{info.total_credit:,.2f} ₮" if info.total_credit is not None else "Not provided",
					"Debit total": f"{info.total_debit:,.2f} ₮" if info.total_debit is not None else "Not provided",
				},
				alt="Statement account, period, and totals",
			)
			preview = [
				{
					"Date": txn.txn_datetime,
					"Amount": f"{txn.amount:,.2f} ₮",
					"Balance before": f"{txn.balance_before:,.2f} ₮" if txn.balance_before is not None else "",
					"Balance after": f"{txn.balance_after:,.2f} ₮" if txn.balance_after is not None else "",
					"Description": txn.description,
					"Counterparty account": txn.counterparty_account or "",
					"Branch": txn.branch_code or "",
				}
				for txn in transactions[:20]
			]
			st.subheader("Transaction preview")
			st.dataframe(preview, hide_index=True, alt="First 20 transactions from the selected statement")
			if errors:
				st.error("The statement failed validation")
				for message in errors:
					st.write(f"- {message}")
			else:
				st.success("Balance chain and statement totals are valid")
				if st.button("Confirm import", type="primary", disabled=bool(errors)):
					try:
						result = import_statement(
							temporary_path,
							uploaded_file.name,
							bank_code,
						)
						st.success(
							f"Imported {result.rows_new} new transactions; "
							f"{result.rows_duplicate} duplicates skipped."
						)
						st.page_link("pages/2_Review.py", label="Review unclassified transactions", icon=":material/rule:")
					except DuplicateFileError as error:
						st.warning(str(error))
					except ValidationError as error:
						st.error(str(error))
		except Exception as error:
			st.error(f"Could not parse this statement: {error}")

st.subheader("Past imports")
try:
	with get_session() as session:
		imports = session.scalars(
			select(Import).order_by(Import.imported_at.desc()).limit(100)
		).all()
		st.dataframe(
			[
				{
					"File": item.file_name,
					"Imported": item.imported_at,
					"Period from": item.period_from,
					"Period to": item.period_to,
					"Read": item.rows_read,
					"New": item.rows_new,
					"Duplicates": item.rows_duplicate,
				}
				for item in imports
			],
			hide_index=True,
			alt="Recently imported statements",
		)
except Exception as error:
	st.info(f"Import history is unavailable: {error}")
