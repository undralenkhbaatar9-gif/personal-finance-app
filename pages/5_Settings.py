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

st.title("Тохиргоо")
rerun_requested = False
kind_labels = {"income": "Орлого", "expense": "Зарлага", "transfer": "Шилжүүлэг"}
kind_values = {label: value for value, label in kind_labels.items()}
field_labels = {
	"description": "Гүйлгээний утга",
	"counterparty_account": "Харилцагчийн данс",
	"branch_code": "Салбарын код",
	"match_key": "Таних түлхүүр",
}
field_values = {label: value for value, label in field_labels.items()}
match_labels = {
	"equals": "Тэнцүү",
	"contains": "Агуулсан",
	"regex": "Тогтмол илэрхийлэл",
}
match_values = {label: value for value, label in match_labels.items()}


def _localize_category(value: object) -> str:
	if not isinstance(value, str) or not value:
		return ""
	kind, separator, name = value.partition(": ")
	if not separator:
		return value
	return f"{kind_labels.get(kind, kind)}: {name}"


accounts_tab, categories_tab, rules_tab, backup_tab = st.tabs(
	["Данс", "Ангилал", "Дүрэм", "Нөөцлөлт"],
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
						"account": st.column_config.TextColumn("Дансны дугаар"),
						"nickname": st.column_config.TextColumn("Нэр"),
						"own account": st.column_config.CheckboxColumn("Өөрийн данс"),
					},
					alt="Дансны нэр болон өөрийн дансны тохиргоо",
				)
				if st.button("Дансны тохиргоо хадгалах", key="save-account-settings"):
					for row in edited.to_dict("records"):
						account = session.get(Account, int(row["id"]))
						if account is not None:
							account.nickname = row["nickname"] or None
							account.is_own = bool(row["own account"])
					classify_transactions(session, None)
					st.success("Дансны тохиргоог хадгаллаа.")
					rerun_requested = True
		except Exception as error:
			st.error(f"Дансны мэдээллийг ачаалж чадсангүй: {error}")

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
							"kind": kind_labels.get(category.kind, category.kind),
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
						"kind": st.column_config.TextColumn("Төрөл"),
						"name": st.column_config.TextColumn("Нэр", required=True),
						"in reports": st.column_config.CheckboxColumn("Тайланд оруулах"),
					},
					alt="Ангиллын нэр болон тайланд оруулах тохиргоо",
				)
				if st.button("Ангиллын өөрчлөлтийг хадгалах", key="save-category-changes"):
					for row in edited.to_dict("records"):
						category = session.get(Category, int(row["id"]))
						if category is not None:
							category.kind = kind_values[row["kind"]]
							category.name = row["name"].strip()
							category.in_reports = bool(row["in reports"])
					st.success("Ангиллын өөрчлөлтийг хадгаллаа.")
					rerun_requested = True

				with st.form("add-category", border=False):
					kind_label = st.selectbox("Төрөл", list(kind_values))
					name = st.text_input("Ангиллын нэр")
					in_reports = st.checkbox("Тайланд оруулах", value=kind_values[kind_label] != "transfer")
					add_category = st.form_submit_button("Ангилал нэмэх", icon=":material/add:")
				if add_category:
					if not name.strip():
						st.error("Ангиллын нэр оруулна уу.")
					elif session.scalar(
						select(Category.id).where(
							Category.kind == kind_values[kind_label], Category.name == name.strip()
						)
					) is not None:
						st.error("Энэ төрөлд ийм нэртэй ангилал бүртгэлтэй байна.")
					else:
						session.add(
							Category(kind=kind_values[kind_label], name=name.strip(), in_reports=in_reports)
						)
						st.success("Ангилал нэмлээ.")
						rerun_requested = True

				removable = [
					f"{kind_labels.get(category.kind, category.kind)}: {category.name}"
					for category in categories
				]
				selected_delete = st.selectbox(
					"Устгах ангилал", options=[""] + removable, key="category-delete-select"
				)
				if selected_delete and st.button("Ангилал устгах", key="delete-category"):
					category_id = next(
						category.id
						for category in categories
						if f"{kind_labels.get(category.kind, category.kind)}: {category.name}" == selected_delete
					)
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
						st.error("Ашиглагдаж буй ангиллыг устгах боломжгүй.")
					else:
						category = session.get(Category, category_id)
						if category is not None:
							session.delete(category)
						st.success("Ангиллыг устгалаа.")
						rerun_requested = True
		except Exception as error:
			st.error(f"Ангиллыг ачаалж чадсангүй: {error}")

if rules_tab.open:
	with rules_tab:
		try:
			with get_session() as session:
				categories = session.scalars(
					select(Category).order_by(Category.kind, Category.name)
				).all()
				category_labels = {
					category.id: f"{kind_labels.get(category.kind, category.kind)}: {category.name}"
					for category in categories
				}
				category_ids = {label: category_id for category_id, label in category_labels.items()}
				rules = session.scalars(select(Rule).order_by(Rule.priority, Rule.id)).all()
				rule_rows = [
					{
						"id": rule.id,
						"priority": rule.priority,
						"field": field_labels.get(rule.field, rule.field),
						"match_type": match_labels.get(rule.match_type, rule.match_type),
						"pattern": rule.pattern,
						"amount_sign": (
							"Аль ч дүн"
							if rule.amount_sign is None
							else "Орлого (+)" if rule.amount_sign == 1 else "Зарлага (-)"
						),
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
						"priority": st.column_config.NumberColumn("Эрэмбэ", min_value=0, step=1),
						"field": st.column_config.SelectboxColumn(
							"Талбар", options=list(field_values)
						),
						"match_type": st.column_config.SelectboxColumn(
							"Нөхцөл", options=list(match_values)
						),
						"pattern": st.column_config.TextColumn("Хайлтын утга", required=True),
						"amount_sign": st.column_config.SelectboxColumn(
							"Дүнгийн төрөл", options=["Аль ч дүн", "Орлого (+)", "Зарлага (-)"]
						),
						"category": st.column_config.SelectboxColumn(
							"Ангилал", options=list(category_ids), required=True
						),
						"active": st.column_config.CheckboxColumn("Идэвхтэй"),
					},
					alt="Гүйлгээ ангилах дүрмийн жагсаалт",
				)
				if st.button("Дүрэм хадгалах", key="save-rules"):
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
						rule.field = field_values[row["field"]]
						rule.match_type = match_values[row["match_type"]]
						rule.pattern = row["pattern"]
						rule.amount_sign = {
							"Аль ч дүн": None,
							"Орлого (+)": 1,
							"Зарлага (-)": -1,
						}[row["amount_sign"]]
						rule.category_id = category_id
						rule.active = bool(row["active"])
						if rule_id is None:
							session.add(rule)
					st.success("Дүрмүүдийг хадгаллаа.")
					st.rerun()

				with st.form("add-rule"):
					priority = st.number_input("Эрэмбэ", min_value=0, value=100, step=1)
					field_label = st.selectbox("Талбар", list(field_values))
					match_label = st.selectbox("Нөхцөл", list(match_values))
					pattern = st.text_input("Хайлтын утга")
					amount_sign_label = st.selectbox("Дүнгийн төрөл", ["Аль ч дүн", "Орлого (+)", "Зарлага (-)"])
					category_label = st.selectbox("Ангилал", list(category_ids))
					active = st.checkbox("Идэвхтэй", value=True)
					add_rule = st.form_submit_button("Дүрэм нэмэх", icon=":material/add:")
				if add_rule:
					if not pattern:
						st.error("Хайлтын утга оруулна уу.")
					else:
						sign = {
							"Аль ч дүн": None,
							"Орлого (+)": 1,
							"Зарлага (-)": -1,
						}[amount_sign_label]
						session.add(
							Rule(
								priority=int(priority),
								field=field_values[field_label],
								match_type=match_values[match_label],
								pattern=pattern,
								amount_sign=sign,
								category_id=category_ids[category_label],
								active=active,
							)
						)
						st.success("Дүрэм нэмлээ.")
						rerun_requested = True

				if rules:
					preview_labels = {
						f"{rule.id}: {field_labels.get(rule.field, rule.field)} "
						f"{match_labels.get(rule.match_type, rule.match_type)} {rule.pattern}": rule
						for rule in rules
					}
					chosen = st.selectbox("Дүрмийг урьдчилан шалгах", list(preview_labels))
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
					preview = preview.rename(
						columns={
							"date": "Огноо",
							"amount": "Дүн",
							"description": "Гүйлгээний утга",
							"counterparty_account": "Харилцагчийн данс",
							"current category": "Одоогийн ангилал",
						}
					)
					if "Одоогийн ангилал" in preview.columns:
						preview["Одоогийн ангилал"] = preview["Одоогийн ангилал"].map(
							_localize_category
						)
					st.caption(f"{len(preview)} өмнөх гүйлгээнд таарна")
					st.dataframe(preview, hide_index=True, alt="Сонгосон дүрэмд таарах гүйлгээнүүд")
				if st.button("Бүх гүйлгээг дахин ангилах", key="reclassify-all"):
					classify_transactions(session, None)
					st.success("Гүйлгээг дахин ангиллаа. Гараар ангилсан гүйлгээнд өөрчлөлт ороогүй.")
					rerun_requested = True
		except Exception as error:
			st.error(f"Дүрмийг ачаалж чадсангүй: {error}")

if backup_tab.open:
	with backup_tab:
		folder = st.text_input("Нөөц файл хадгалах хавтас", value=str(Path.home() / "finance-backups"))
		if st.button("Нөөцлөлт үүсгэх", type="primary", icon=":material/backup:"):
			pg_dump = shutil.which("pg_dump")
			if pg_dump is None:
				st.error("pg_dump PATH-д олдсонгүй. PostgreSQL-ийн клиент хэрэгслийг суулгана уу.")
			elif not DATABASE_URL:
				st.error("Нөөцлөлт үүсгэхийн өмнө DATABASE_URL тохируулна уу.")
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
						st.error(result.stderr.strip() or "pg_dump алдааны мэдээлэлгүйгээр амжилтгүй боллоо.")
					else:
						st.success(f"Нөөц файл үүслээ: {output_path}")
				except (OSError, ValueError) as error:
					st.error(f"Нөөц файл үүсгэж чадсангүй: {error}")

if rerun_requested:
	st.rerun()
