import tempfile

import pandas as pd
import streamlit as st
from sqlalchemy import select

from finance.db import get_session
from finance.importer import DuplicateFileError, ValidationError, import_statement
from finance.models import Import
from finance.parsers import PARSERS
from finance.ui import apply_global_styles, render_footer

st.set_page_config(page_title="Хуулга импортлох", page_icon="📄", layout="wide")
apply_global_styles()

st.title("📄 Банкны хуулга импортлох")

bank_options = list(PARSERS.keys())
bank_code_map = {
    "khan": "Хаан банк",
}

bank_label_map = {code: bank_code_map.get(code, code) for code in bank_options}
bank = st.selectbox(
    "Банк сонгох",
    options=bank_options,
    format_func=lambda code: bank_label_map.get(code, code),
)

uploaded_file = st.file_uploader("Банкны хуулгаа сонгоно уу (XLSX)", type=["xlsx"])

if uploaded_file is not None:
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            tmp.write(uploaded_file.getbuffer())
            tmp_path = tmp.name

        parser = PARSERS[bank]
        if not parser.detect(tmp_path):
            st.warning("Энэ файл сонгосон банкны хуулгатай таарахгүй байна.")
        else:
            info, txns = parser.parse(tmp_path)
            st.subheader("Хуулгын мэдээлэл")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Данс", info.account_no)
            c2.metric("Валют", info.currency)
            c3.metric("Нийт орлого", f"{info.total_credit or 0:,.2f}")
            c4.metric("Нийт зарлага", f"{info.total_debit or 0:,.2f}")

            st.subheader("Урьдчилсан харагдац (эхний 20 мөр)")
            preview_rows = []
            for t in txns[:20]:
                preview_rows.append(
                    {
                        "Огноо": t.txn_datetime,
                        "Дүн": float(t.amount),
                        "Тайлбар": t.description,
                        "Дансны үлдэгдэл (урьд)": float(t.balance_before) if t.balance_before is not None else None,
                        "Дансны үлдэгдэл (дараа)": float(t.balance_after) if t.balance_after is not None else None,
                        "Харилцагчийн данс": t.counterparty_account,
                        "Салбар": t.branch_code,
                    }
                )
            st.dataframe(pd.DataFrame(preview_rows), use_container_width=True)

            if st.button("Импорт хийх", type="primary"):
                try:
                    result = import_statement(tmp_path, uploaded_file.name, bank)
                    st.success(
                        f"Амжилттай импортоллоо. Нийт уншсан: {result.rows_read}, Шинэ: {result.rows_new}, Давхардсан: {result.rows_duplicate}"
                    )
                    st.info("Гүйлгээг Review хуудсанд ангилах боломжтой.")
                except DuplicateFileError as e:
                    st.error(str(e))
                except ValidationError as e:
                    st.error("Хуулга баталгаажуулалтад тэнцээгүй байна:")
                    for err in e.errors:
                        st.write(f"- {err}")
                except Exception as e:
                    st.error(f"Алдаа гарлаа: {e}")
    except Exception as e:
        st.error(f"Файл боловсруулахад алдаа гарлаа: {e}")

st.markdown("---")
st.subheader("Өмнөх импортууд")
try:
    with get_session() as session:
        imports = session.scalars(select(Import).order_by(Import.imported_at.desc())).all()
        if imports:
            rows = []
            for imp in imports:
                rows.append(
                    {
                        "Файл": imp.file_name,
                        "Импортлогдсон огноо": imp.imported_at,
                        "Уншсан": imp.rows_read,
                        "Шинэ": imp.rows_new,
                        "Давхардсан": imp.rows_duplicate,
                    }
                )
            st.dataframe(pd.DataFrame(rows), use_container_width=True)
        else:
            st.info("Одоогоор импортын түүх алга байна.")
except Exception as e:
    st.error(f"Түүхийг ачаалахад алдаа гарлаа: {e}")

render_footer()