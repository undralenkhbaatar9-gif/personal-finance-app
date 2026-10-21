from dataclasses import asdict
from pathlib import Path
from tempfile import TemporaryDirectory

import streamlit as st
from sqlalchemy import select

from finance.db import get_session
from finance.importer import DuplicateFileError, ValidationError, import_statement, validate
from finance.models import Import
from finance.parsers import PARSERS
from finance.ui import apply_global_styles, render_footer

apply_global_styles()

def _validation_message(message: str) -> str:
	translations = {
		"balance_before and balance_after are required": "өмнөх болон дараах үлдэгдэл шаардлагатай",
		"balance_before + amount does not equal balance_after": "өмнөх үлдэгдэл дээр гүйлгээний дүнг нэмэхэд дараах үлдэгдэлтэй тэнцэхгүй байна",
		"balance_before does not match the previous row": "өмнөх үлдэгдэл нь өмнөх мөрийн дараах үлдэгдэлтэй таарахгүй байна",
	}
	for english, mongolian in translations.items():
		if english in message:
			return message.replace(english, mongolian).replace("Row ", "Мөр ")
	if message.startswith("Statement total credit"):
		return "Хуулгын нийт орлогын дүн мөрүүдийн орлогын нийлбэртэй таарахгүй байна."
	if message.startswith("Statement total debit"):
		return "Хуулгын нийт зарлагын дүн мөрүүдийн зарлагын нийлбэртэй таарахгүй байна."
	return message.replace("Row ", "Мөр ")


st.title("Хуулга импортлох")
bank_code = st.selectbox(
	"Банк",
	options=list(PARSERS),
	format_func=lambda code: "Хаан банк" if code == "khan" else PARSERS[code].name,
)
uploaded_file = st.file_uploader("Банкны хуулгаа сонгоно уу", type=["xlsx", "csv"])
st.caption("Excel эсвэл CSV хуулгаа сонгох буюу файл сонгох хэсэгт чирж оруулна уу.")

if uploaded_file is not None:
	suffix = Path(uploaded_file.name).suffix.lower()
	with TemporaryDirectory() as temporary_folder:
		temporary_path = Path(temporary_folder) / f"statement{suffix}"
		try:
			with st.spinner("Хуулгыг уншиж, шалгаж байна..."):
				temporary_path.write_bytes(uploaded_file.getvalue())
				info, transactions = PARSERS[bank_code].parse(temporary_path)
				errors = validate(info, transactions)
			st.subheader("Хуулгын мэдээлэл")
			st.table(
				{
					"Дансны дугаар": info.account_no,
					"IBAN": info.iban or "",
					"Валют": info.currency,
					"Эхлэх огноо": info.period_from,
					"Дуусах огноо": info.period_to,
					"Уншсан гүйлгээ": len(transactions),
					"Нийт орлого": f"{info.total_credit:,.2f} ₮" if info.total_credit is not None else "Мэдээлэл алга",
					"Нийт зарлага": f"{info.total_debit:,.2f} ₮" if info.total_debit is not None else "Мэдээлэл алга",
				},
				alt="Хуулгын данс, хугацаа болон нийт дүн",
			)
			preview = [
				{
					"Огноо": txn.txn_datetime,
					"Дүн": f"{txn.amount:,.2f} ₮",
					"Өмнөх үлдэгдэл": f"{txn.balance_before:,.2f} ₮" if txn.balance_before is not None else "",
					"Дараах үлдэгдэл": f"{txn.balance_after:,.2f} ₮" if txn.balance_after is not None else "",
					"Гүйлгээний утга": txn.description,
					"Харилцагчийн данс": txn.counterparty_account or "",
					"Салбарын код": txn.branch_code or "",
				}
				for txn in transactions[:20]
			]
			st.subheader("Гүйлгээний урьдчилсан харагдац")
			st.dataframe(preview, hide_index=True, alt="Хуулгын эхний 20 гүйлгээ")
			if errors:
				st.error("Хуулгын шалгалт амжилтгүй боллоо")
				for message in errors:
					st.write(f"- {_validation_message(message)}")
			else:
				st.success("Үлдэгдлийн дараалал болон хуулгын нийлбэр зөв байна")
				if st.button("Импорт баталгаажуулах", type="primary", disabled=bool(errors)):
					try:
						with st.spinner("Гүйлгээг хадгалж, ангилж байна..."):
							result = import_statement(
								temporary_path,
								uploaded_file.name,
								bank_code,
							)
						st.success(
							f"{result.rows_new} шинэ гүйлгээг импортолж, "
							f"{result.rows_duplicate} давхардлыг алгаслаа."
						)
						st.toast(f"{result.rows_new} шинэ гүйлгээг амжилттай импортоллоо.")
						st.page_link("pages/2_Review.py", label="Ангилаагүй гүйлгээг ангилах", icon=":material/rule:")
					except DuplicateFileError as error:
						st.warning(f"Энэ хуулгыг өмнө нь импортолсон байна: {uploaded_file.name}")
					except ValidationError as error:
						st.error("Хуулгын шалгалт амжилтгүй боллоо.")
						for message in error.errors:
							st.write(f"- {_validation_message(message)}")
					except Exception as error:
						st.error("Импорт амжилтгүй боллоо. Өгөгдлийн сангийн холболтыг шалгаад дахин оролдоно уу.")
		except Exception as error:
			st.error("Хуулгыг уншиж чадсангүй. Файлын төрөл болон агуулгыг шалгаад дахин оролдоно уу.")

st.subheader("Өмнөх импортууд")
try:
	with st.spinner("Импортын түүхийг ачаалж байна..."):
		with get_session() as session:
			imports = session.scalars(
				select(Import).order_by(Import.imported_at.desc()).limit(100)
			).all()
		st.dataframe(
			[
				{
					"Файл": item.file_name,
					"Импортолсон огноо": item.imported_at,
					"Эхлэх огноо": item.period_from,
					"Дуусах огноо": item.period_to,
					"Уншсан": item.rows_read,
					"Шинэ": item.rows_new,
					"Давхардсан": item.rows_duplicate,
				}
				for item in imports
			],
			hide_index=True,
			alt="Сүүлд импортолсон банкны хуулгууд",
		)
except Exception as error:
	st.warning("Импортын түүхийг одоогоор харуулах боломжгүй байна.")

render_footer()
