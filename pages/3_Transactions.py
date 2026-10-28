from datetime import date, timedelta
from io import BytesIO
import traceback

import pandas as pd
import streamlit as st
from sqlalchemy import or_, select, text

from finance.db import get_session
from finance.ui import apply_global_styles, render_footer

apply_global_styles()
st.title("Бүх гүйлгээ")
rerun_requested = False
notification_message: str | None = None
today = date.today()
kind_labels = {"income": "Орлого", "expense": "Зарлага", "transfer": "Шилжүүлэг"}
source_labels = {
    "manual": "Гараар ангилсан",
    "transfer": "Шилжүүлэг",
    "counterparty": "Харилцагчийн тохиргоо",
    "rule": "Дүрмээр ангилсан",
    "unclassified": "Ангилаагүй",
}

with st.sidebar:
    date_range = st.date_input(
        "Огнооны хүрээ",
        value=(today - timedelta(days=180), today),
        key="transaction-date-range",
    )
    search_text = st.text_input("Гүйлгээний утга эсвэл харилцагчаар хайх", type="search")
    unclassified_only = st.checkbox("Зөвхөн ангилаагүй")

if isinstance(date_range, tuple) and len(date_range) == 2:
    date_from, date_to = date_range
else:
    date_from = date_to = date_range

saved = 0
try:
    with get_session() as session:
        # Хүснэгтийн багануудын нэрийг шалгах
        tx_cols = [row[1] for row in session.execute(text("PRAGMA table_info(transactions)")).fetchall()]
        acc_cols = [row[1] for row in session.execute(text("PRAGMA table_info(accounts)")).fetchall()]
        cat_cols = [row[1] for row in session.execute(text("PRAGMA table_info(categories)")).fetchall()]
        cp_cols = [row[1] for row in session.execute(text("PRAGMA table_info(counterparties)")).fetchall()]

        # Данснууд болон ангилллуудыг SQL-ээр авах
        acc_raw = session.execute(text("SELECT id, account_no, nickname FROM accounts ORDER BY account_no")).fetchall()
        accounts_map = {r[0]: {"account_no": r[1], "nickname": r[2]} for r in acc_raw}
        
        account_options = {"Бүх данс": None}
        for r in acc_raw:
            acc_id, acc_no, nickname = r[0], r[1], r[2]
            account_options[f"{nickname or acc_no}"] = acc_id

        cat_raw = session.execute(text("SELECT id, kind, name FROM categories ORDER BY kind, name")).fetchall()
        categories_map = {r[0]: {"kind": r[1], "name": r[2]} for r in cat_raw}
        
        category_options = {"Бүх ангилал": None, "Ангилаагүй": -1}
        for r in cat_raw:
            c_id, kind, name = r[0], r[1], r[2]
            label = f"{kind_labels.get(kind, kind)}: {name}"
            category_options[label] = c_id

        selected_account = st.sidebar.selectbox("Данс", list(account_options))
        selected_category = st.sidebar.selectbox("Ангилал", list(category_options))

        # Динамикаар query байгуулах
        date_col = next((c for c in ["txn_datetime", "date", "transaction_date"] if c in tx_cols), tx_cols[1])
        
        query_sql = f"""
            SELECT t.id, t.{date_col}, t.amount, t.description, t.category_id, t.category_source, t.note, 
                   t.account_id, t.counterparty_id,
                   c.match_key, c.display_name
            FROM transactions t
            LEFT JOIN counterparties c ON t.counterparty_id = c.id
            WHERE t.{date_col} >= :date_from AND t.{date_col} < :date_to_plus
        """
        params = {
            "date_from": str(date_from),
            "date_to_plus": str(date_to + timedelta(days=1))
        }

        if account_options[selected_account] is not None:
            query_sql += " AND t.account_id = :acc_id"
            params["acc_id"] = account_options[selected_account]

        selected_cat_val = category_options[selected_category]
        if unclassified_only or selected_cat_val == -1:
            query_sql += " AND t.category_id IS NULL"
        elif selected_cat_val is not None:
            query_sql += " AND t.category_id = :cat_id"
            params["cat_id"] = selected_cat_val

        if search_text:
            query_sql += " AND (t.description LIKE :search OR c.display_name LIKE :search OR c.match_key LIKE :search)"
            params["search"] = f"%{search_text}%"

        query_sql += f" ORDER BY t.{date_col} DESC LIMIT 2000"

        with st.spinner("Гүйлгээнүүдийг ачаалж байна..."):
            rows = session.execute(text(query_sql), params).fetchall()

        category_labels = {
            c_id: f"{kind_labels.get(info['kind'], info['kind'])}: {info['name']}"
            for c_id, info in categories_map.items()
        }

        editor_rows = []
        for r in rows:
            txn_id, txn_date, amount, description, cat_id, cat_source, note, acc_id, cp_id, match_key, display_name = r
            acc_info = accounts_map.get(acc_id, {})
            acc_name = acc_info.get("nickname") or acc_info.get("account_no", "Данс")
            cp_name = display_name if display_name else (match_key if match_key else "")
            
            editor_rows.append({
                "txn_id": txn_id,
                "date": txn_date,
                "account": acc_name,
                "amount": float(amount) if amount is not None else 0.0,
                "description": description or "",
                "counterparty": cp_name,
                "match_key": match_key or "",
                "category": category_labels.get(cat_id, "Ангилаагүй"),
                "source": source_labels.get(cat_source, cat_source),
                "note": note or "",
                "make rule": False,
            })

        original = {row["txn_id"]: row for row in editor_rows}
        frame = pd.DataFrame(
            editor_rows,
            columns=[
                "txn_id", "date", "account", "amount", "description", "counterparty",
                "match_key", "category", "source", "note", "make rule",
            ],
        )
        category_labels_list = ["Ангилаагүй"] + list(category_labels.values())

        with st.form("transaction-editor"):
            edited = st.data_editor(
                frame,
                key="transactions-editor",
                hide_index=True,
                num_rows="fixed",
                disabled=["txn_id", "date", "account", "amount", "description", "counterparty", "match_key", "source"],
                column_config={
                    "txn_id": None,
                    "date": st.column_config.DatetimeColumn("Огноо"),
                    "account": st.column_config.TextColumn("Данс"),
                    "amount": st.column_config.NumberColumn("Дүн", format="%.2f ₮"),
                    "description": st.column_config.TextColumn("Гүйлгээний утга"),
                    "counterparty": st.column_config.TextColumn("Харилцагч"),
                    "category": st.column_config.SelectboxColumn("Ангилал", options=category_labels_list),
                    "source": st.column_config.TextColumn("Эх сурвалж"),
                    "note": st.column_config.TextColumn("Тэмдэглэл"),
                    "make rule": st.column_config.CheckboxColumn("Дүрэм үүсгэх"),
                    "match_key": None,
                },
                alt="Ангилал, тэмдэглэл засах болон дүрэм үүсгэх боломжтой гүйлгээнүүд",
            )
            submitted = st.form_submit_button("Өөрчлөлт хадгалах", type="primary")

        export_frame = frame[
            ["date", "account", "amount", "description", "counterparty", "category", "source", "note"]
        ].rename(
            columns={
                "date": "Огноо",
                "account": "Данс",
                "amount": "Дүн (₮)",
                "description": "Гүйлгээний утга",
                "counterparty": "Харилцагч",
                "category": "Ангилал",
                "source": "Ангилсан арга",
                "note": "Тэмдэглэл",
            }
        )
        csv_data = export_frame.to_csv(index=False).encode("utf-8-sig")
        xlsx_buffer = BytesIO()
        with pd.ExcelWriter(xlsx_buffer, engine="openpyxl") as writer:
            export_frame.to_excel(writer, index=False, sheet_name="Гүйлгээнүүд")
        
        with st.container():
            st.download_button(
                "Текстэн файл татах",
                csv_data,
                "гүйлгээ.csv",
                mime="text/csv",
            )
            st.download_button(
                "Хүснэгтэн файл татах",
                xlsx_buffer.getvalue(),
                "гүйлгээ.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        if submitted:
            with st.spinner("Өөрчлөлтийг хадгалж байна..."):
                rules_added = 0
                for row in edited.to_dict("records"):
                    txn_id = int(row["txn_id"])
                    previous = original[txn_id]
                    
                    category_label = row["category"]
                    category_id = None
                    if category_label != "Ангилаагүй":
                        category_id = next(
                            (key for key, label in category_labels.items() if label == category_label),
                            None,
                        )
                    
                    # Transaction шинэчлэх SQL
                    update_fields = []
                    params_update = {"txn_id": txn_id}
                    
                    # Одоогийн өгөгдлийг шалгах
                    curr_res = session.execute(text("SELECT category_id, category_source, note FROM transactions WHERE id = :txn_id"), {"txn_id": txn_id}).fetchone()
                    if not curr_res:
                        continue
                    curr_cat_id, curr_source, curr_note = curr_res[0], curr_res[1], curr_res[2]

                    if category_id != curr_cat_id:
                        update_fields.append("category_id = :cat_id")
                        update_fields.append("category_source = 'manual'")
                        params_update["cat_id"] = category_id
                        saved += 1

                    new_note = row["note"] or None
                    if new_note != curr_note:
                        update_fields.append("note = :note")
                        params_update["note"] = new_note
                        saved += 1

                    if update_fields:
                        session.execute(text(f"UPDATE transactions SET {', '.join(update_fields)} WHERE id = :txn_id"), params_update)

                    match_key = row["match_key"]
                    if row["make rule"] and match_key and category_id is not None:
                        # Rules хүснэгт байгаа эсэхийг шалгаад дүрэм нэмэх
                        rule_check = session.execute(
                            text("SELECT id FROM rules WHERE field = 'match_key' AND match_type = 'equals' AND pattern = :pat AND category_id = :cid AND active = 1"),
                            {"pat": match_key, "cid": category_id}
                        ).fetchone()
                        
                        if not rule_check:
                            session.execute(
                                text("INSERT INTO rules (priority, field, match_type, pattern, category_id, active) VALUES (50, 'match_key', 'equals', :pat, :cid, 1)"),
                                {"pat": match_key, "cid": category_id}
                            )
                            rules_added += 1

                notification_message = f"{saved} гүйлгээний өөрчлөлтийг хадгалж, {rules_added} дүрэм үүсгэлээ."
                rerun_requested = True
except Exception as error:
    notification_message = None
    st.error(f"Гүйлгээг ачаалж эсвэл хадгалж чадсангүй. Алдаа: {error}")
    st.code(traceback.format_exc())

if notification_message:
    st.success(notification_message)
    st.toast(f"{saved} гүйлгээний өөрчлөлтийг хадгаллаа.")

render_footer()
if rerun_requested:
    st.rerun()