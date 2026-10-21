from datetime import datetime
import os
from pathlib import Path
import shutil
import subprocess

import pandas as pd
import streamlit as st
from sqlalchemy import func, select
from sqlalchemy.engine import make_url

from finance.classifier import classify_transactions, test_rule
from finance.config import DATABASE_URL
from finance.db import get_session
from finance.models import Account, Category, Counterparty, Rule, Transaction

st.title("Settings")
rerun_requested = False
accounts_tab, categories_tab, rules_tab, backup_tab = st.tabs(
	["Accounts", "Categories", "Rules", "Backup"],
	key="settings-tabs",
	on_change="rerun",
)

if accounts_tab.open:
	with accounts_tab:
		try:
			with get_session() as session:
				accounts = session.scalars(select(Account).order_by(Account.account_no)).all()
				frame = pd.DataFrame(
					[
						{
							"id": account.id,
							"account": account.account_no,
							"nickname": account.nickname or "",
							"own account": account.is_own,
						}
						for account in accounts
					]
				)
				edited = st.data_editor(
					frame,
					key="settings-accounts",
					hide_index=True,
					disabled=["id", "account"],
					column_config={
						"id": None,
						"account": st.column_config.TextColumn("Account"),
						"nickname": st.column_config.TextColumn("Nickname"),
						"own account": st.column_config.CheckboxColumn("Own account"),
					},
					alt="Account nicknames and own-account settings",
				)
				if st.button("Save account settings", key="save-account-settings"):
					for row in edited.to_dict("records"):
						account = session.get(Account, int(row["id"]))
						if account is not None:
							account.nickname = row["nickname"] or None
							account.is_own = bool(row["own account"])
					classify_transactions(session, None)
					st.success("Account settings saved.")
					rerun_requested = True
		except Exception as error:
			st.error(f"Could not load accounts: {error}")

if categories_tab.open:
	with categories_tab:
		try:
			with get_session() as session:
				categories = session.scalars(
					select(Category).order_by(Category.kind, Category.name)
				).all()
				original = {category.id: category.name for category in categories}
				frame = pd.DataFrame(
					[
						{
							"id": category.id,
							"kind": category.kind,
							"name": category.name,
							"in reports": category.in_reports,
						}
						for category in categories
					]
				)
				edited = st.data_editor(
					frame,
					key="settings-categories",
					hide_index=True,
					disabled=["id", "kind"],
					column_config={
						"id": None,
						"kind": st.column_config.TextColumn("Kind"),
						"name": st.column_config.TextColumn("Name", required=True),
						"in reports": st.column_config.CheckboxColumn("Include in reports"),
					},
					alt="Category names and report inclusion settings",
				)
				if st.button("Save category changes", key="save-category-changes"):
					for row in edited.to_dict("records"):
						category = session.get(Category, int(row["id"]))
						if category is not None:
							category.name = row["name"].strip()
							category.in_reports = bool(row["in reports"])
					st.success("Category changes saved.")
					rerun_requested = True

				with st.form("add-category", border=False):
					kind = st.selectbox("Kind", ["income", "expense", "transfer"])
					name = st.text_input("Category name")
					in_reports = st.checkbox("Include in reports", value=kind != "transfer")
					add_category = st.form_submit_button("Add category", icon=":material/add:")
				if add_category:
					if not name.strip():
						st.error("Enter a category name.")
					elif session.scalar(
						select(Category.id).where(
							Category.kind == kind, Category.name == name.strip()
						)
					) is not None:
						st.error("That category already exists for this kind.")
					else:
						session.add(
							Category(kind=kind, name=name.strip(), in_reports=in_reports)
						)
						st.success("Category added.")
						rerun_requested = True

				removable = [
					f"{category.kind}: {category.name} (id {category.id})"
					for category in categories
				]
				selected_delete = st.selectbox(
					"Category to remove", options=[""] + removable, key="category-delete-select"
				)
				if selected_delete and st.button("Delete category", key="delete-category"):
					category_id = int(selected_delete.rsplit("id ", 1)[1].rstrip(")"))
					used_by_transaction = session.scalar(
						select(func.count()).select_from(Transaction).where(Transaction.category_id == category_id)
					)
					used_by_counterparty = session.scalar(
						select(func.count()).select_from(Counterparty).where(Counterparty.default_category_id == category_id)
					)
					used_by_rule = session.scalar(
						select(func.count()).select_from(Rule).where(Rule.category_id == category_id)
					)
					used_as_parent = session.scalar(
						select(func.count()).select_from(Category).where(Category.parent_id == category_id)
					)
					if used_by_transaction or used_by_counterparty or used_by_rule or used_as_parent:
						st.error("This category is in use and cannot be deleted.")
					else:
						category = session.get(Category, category_id)
						if category is not None:
							session.delete(category)
						st.success("Category deleted.")
						rerun_requested = True
		except Exception as error:
			st.error(f"Could not load categories: {error}")

if rules_tab.open:
	with rules_tab:
		try:
			with get_session() as session:
				categories = session.scalars(
					select(Category).order_by(Category.kind, Category.name)
				).all()
				category_labels = {
					category.id: f"{category.kind}: {category.name}" for category in categories
				}
				category_ids = {label: category_id for category_id, label in category_labels.items()}
				rules = session.scalars(select(Rule).order_by(Rule.priority, Rule.id)).all()
				rule_rows = [
					{
						"id": rule.id,
						"priority": rule.priority,
						"field": rule.field,
						"match_type": rule.match_type,
						"pattern": rule.pattern,
						"amount_sign": "Any" if rule.amount_sign is None else str(rule.amount_sign),
						"category": category_labels.get(rule.category_id, ""),
						"active": bool(rule.active),
					}
					for rule in rules
				]
				edited_rules = st.data_editor(
					pd.DataFrame(rule_rows),
					key="settings-rules",
					hide_index=True,
					num_rows="dynamic",
					disabled=["id"],
					column_config={
						"id": None,
						"priority": st.column_config.NumberColumn("Priority", min_value=0, step=1),
						"field": st.column_config.SelectboxColumn(
							"Field", options=["description", "counterparty_account", "branch_code", "match_key"]
						),
						"match_type": st.column_config.SelectboxColumn(
							"Match type", options=["equals", "contains", "regex"]
						),
						"pattern": st.column_config.TextColumn("Pattern", required=True),
						"amount_sign": st.column_config.SelectboxColumn(
							"Amount sign", options=["Any", "-1", "1"]
						),
						"category": st.column_config.SelectboxColumn(
							"Category", options=list(category_ids), required=True
						),
						"active": st.column_config.CheckboxColumn("Active"),
					},
					alt="Editable transaction classification rules",
				)
				if st.button("Save rules", key="save-rules"):
					edited_rows = edited_rules.to_dict("records")
					kept_ids = {
						int(row["id"])
						for row in edited_rows
						if pd.notna(row.get("id"))
					}
					for rule in rules:
						if rule.id not in kept_ids:
							session.delete(rule)
					for row in edited_rows:
						category_id = category_ids.get(row.get("category"))
						if category_id is None or not row.get("pattern"):
							continue
						rule_id = int(row["id"]) if pd.notna(row.get("id")) else None
						rule = session.get(Rule, rule_id) if rule_id else Rule()
						if rule is None:
							continue
						rule.priority = int(row["priority"] or 100)
						rule.field = row["field"]
						rule.match_type = row["match_type"]
						rule.pattern = row["pattern"]
						rule.amount_sign = (
							int(row["amount_sign"])
							if row["amount_sign"] in ("-1", "1", -1, 1)
							else None
						)
						rule.category_id = category_id
						rule.active = bool(row["active"])
						if rule_id is None:
							session.add(rule)
					st.success("Rules saved.")
					st.rerun()

				with st.form("add-rule"):
					priority = st.number_input("Priority", min_value=0, value=100, step=1)
					field = st.selectbox("Field", ["description", "counterparty_account", "branch_code", "match_key"])
					match_type = st.selectbox("Match type", ["equals", "contains", "regex"])
					pattern = st.text_input("Pattern")
					amount_sign_label = st.selectbox("Amount sign", ["Any", "Income (+)", "Expense (-)"])
					category_label = st.selectbox("Category", list(category_ids))
					active = st.checkbox("Active", value=True)
					add_rule = st.form_submit_button("Add rule", icon=":material/add:")
				if add_rule:
					if not pattern:
						st.error("Enter a match pattern.")
					else:
						sign = {"Any": None, "Income (+)": 1, "Expense (-)": -1}[amount_sign_label]
						session.add(
							Rule(
								priority=int(priority),
								field=field,
								match_type=match_type,
								pattern=pattern,
								amount_sign=sign,
								category_id=category_ids[category_label],
								active=active,
							)
						)
						st.success("Rule added.")
						rerun_requested = True

				if rules:
					preview_labels = {
						f"{rule.id}: {rule.field} {rule.match_type} {rule.pattern}": rule
						for rule in rules
					}
					chosen = st.selectbox("Rule preview", list(preview_labels))
					selected_rule = preview_labels[chosen]
					preview = test_rule(
						session,
						{
							"field": selected_rule.field,
							"match_type": selected_rule.match_type,
							"pattern": selected_rule.pattern,
							"amount_sign": selected_rule.amount_sign,
						},
					)
					st.caption(f"Would match {len(preview)} past transactions")
					st.dataframe(preview, hide_index=True, alt="Transactions matched by the selected rule")
				if st.button("Re-classify all", key="reclassify-all"):
					classify_transactions(session, None)
					st.success("Transactions reclassified; manual categories were preserved.")
					rerun_requested = True
		except Exception as error:
			st.error(f"Could not load rules: {error}")

if backup_tab.open:
	with backup_tab:
		folder = st.text_input("Backup folder", value=str(Path.home() / "finance-backups"))
		if st.button("Create backup", type="primary", icon=":material/backup:"):
			pg_dump = shutil.which("pg_dump")
			if pg_dump is None:
				st.error("pg_dump was not found on PATH. Install PostgreSQL client tools and try again.")
			elif not DATABASE_URL:
				st.error("DATABASE_URL must be configured before creating a backup.")
			else:
				try:
					database_url = make_url(DATABASE_URL)
					output_folder = Path(folder).expanduser()
					output_folder.mkdir(parents=True, exist_ok=True)
					output_path = output_folder / f"finance_{datetime.now():%Y%m%d_%H%M}.dump"
					command = [
						pg_dump,
						"-Fc",
						"-h",
						database_url.host or "localhost",
						"-p",
						str(database_url.port or 5432),
						"-U",
						database_url.username or "",
						"-d",
						database_url.database or "",
						"-f",
						str(output_path),
					]
					environment = os.environ.copy()
					if database_url.password:
						environment["PGPASSWORD"] = database_url.password
					result = subprocess.run(
						command,
						check=False,
						capture_output=True,
						text=True,
						env=environment,
					)
					if result.returncode:
						st.error(result.stderr.strip() or "pg_dump failed without an error message.")
					else:
						st.success(f"Backup created: {output_path}")
				except (OSError, ValueError) as error:
					st.error(f"Could not create backup: {error}")

if rerun_requested:
	st.rerun()
