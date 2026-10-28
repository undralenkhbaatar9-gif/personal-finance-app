from decimal import Decimal
import traceback
import pandas as pd
import streamlit as st
from sqlalchemy import text

from finance.classifier import classify_transactions
from finance.db import get_session
from finance.ui import apply_global_styles, render_footer

apply_global_styles()
st.title("Гүйлгээ ангилах")
rerun_requested = False
notification_message: str | None = None
kind_labels = {"income": "Орлого", "expense": "Зарлага", "transfer": "Шилжүүлэг"}

try:
    with get_session() as session:
        # Хүснэгтүүдийн багануудыг автоматаар шалгах
        tx_cols = [row[1] for row in session.execute(text("PRAGMA table_info(transactions)")).fetchall()]
        cp_cols = [row[1] for row in session.execute(text("PRAGMA table_info(counterparties)")).fetchall()]
        cat_cols = [row[1] for row in session.execute(text("PRAGMA table_info(categories)")).fetchall()]

        # Categories татах
        cat_select_cols = ", ".join([c for c in ["id", "kind", "name"] if c in cat_cols])
        categories_raw = session.execute(text(f"SELECT {cat_select_cols} FROM categories ORDER BY kind, name")).fetchall()
        
        class SimpleObj:
            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)

        categories = [SimpleObj(id=r[0], kind=r[1], name=r[2]) for r in categories_raw]

        category_options = [
            f"{kind_labels.get(cat.kind, cat.kind)}: {cat.name}"
            for cat in categories
        ]
        category_by_label = {
            f"{kind_labels.get(cat.kind, cat.kind)}: {cat.name}": cat.id
            for cat in categories
        }

        # Transactions шүүх нөхцөл болон багануудыг динамикаар үүсгэх
        date_col = next((c for c in ["date", "transaction_date", "tx_date"] if c in tx_cols), tx_cols[1] if len(tx_cols) > 1 else tx_cols[0])
        desc_col = next((c for c in ["description", "memo", "details"] if c in tx_cols), "description" if "description" in tx_cols else tx_cols[0])
        amount_col = next((c for c in ["amount", "sum", "value"] if c in tx_cols), "amount")
        type_col = next((c for c in ["type", "tx_type"] if c in tx_cols), "type" if "type" in tx_cols else None)
        cs_col = next((c for c in ["category_source", "source"] if c in tx_cols), None)
        cid_col = next((c for c in ["category_id"] if c in tx_cols), None)
        cpid_col = next((c for c in ["counterparty_id"] if c in tx_cols), None)
        bank_col = next((c for c in ["bank_name", "bank"] if c in tx_cols), None)

        select_fields = ["id", date_col, desc_col, amount_col]
        if type_col: select_fields.append(type_col)
        if cs_col: select_fields.append(cs_col)
        if cid_col: select_fields.append(cid_col)
        if cpid_col: select_fields.append(cpid_col)
        if bank_col: select_fields.append(bank_col)

        where_clauses = []
        if cs_col:
            where_clauses.append(f"({cs_col} = 'unclassified' OR {cs_col} IS NULL)")
        if cid_col:
            where_clauses.append(f"({cid_col} IS NULL)")
        
        where_sql = " WHERE " + " OR ".join(where_clauses) if where_clauses else ""

        with st.spinner("Ангилаагүй гүйлгээнүүдийг ачаалж байна..."):
            tx_raw = session.execute(text(f"SELECT {', '.join(select_fields)} FROM transactions{where_sql}")).fetchall()

        unclassified = []
        for r in tx_raw:
            # Динамикаар утгуудыг оноох
            val_map = {field: r[i] for i, field in enumerate(select_fields)}
            unclassified.append(SimpleObj(
                id=val_map.get("id"),
                date=val_map.get(date_col),
                description=val_map.get(desc_col),
                amount=Decimal(str(val_map.get(amount_col, 0) or 0)),
                type=val_map.get(type_col) if type_col else "",
                category_source=val_map.get(cs_col) if cs_col else "",
                category_id=val_map.get(cid_col) if cid_col else None,
                counterparty_id=val_map.get(cpid_col) if cpid_col else None,
                bank_name=val_map.get(bank_col) if bank_col else ""
            ))

        counterparty_ids = {txn.counterparty_id for txn in unclassified if txn.counterparty_id}
        
        counterparties = {}
        if counterparty_ids and cpid_col:
            id_list = ",".join(str(i) for i in counterparty_ids)
            cp_select = ", ".join([c for c in ["id", "match_key", "display_name", "default_category_id", "is_own_account", "ask_per_txn"] if c in cp_cols])
            cp_raw = session.execute(text(f"SELECT {cp_select} FROM counterparties WHERE id IN ({id_list})")).fetchall()
            for r in cp_raw:
                c_map = {cp_select.split(', ')[i].strip(): r[i] for i in range(len(r))}
                counterparties[c_map.get("id")] = SimpleObj(
                    id=c_map.get("id"),
                    match_key=c_map.get("match_key", ""),
                    display_name=c_map.get("display_name", ""),
                    default_category_id=c_map.get("default_category_id"),
                    is_own_account=bool(c_map.get("is_own_account", 0)),
                    ask_per_txn=bool(c_map.get("ask_per_txn", 0))
                )
        
        transactions_by_counterparty: dict[int, list] = {}
        for txn in unclassified:
            if txn.counterparty_id is not None:
                transactions_by_counterparty.setdefault(txn.counterparty_id, []).append(txn)

        st.sidebar.metric("Ангилаагүй гүйлгээ", len(unclassified))
        
        if not unclassified:
            st.success("Бүх гүйлгээ ангилагдсан байна.")
        elif not transactions_by_counterparty:
            st.info("Ангилаагүй гүйлгээнд харилцагч холбогдоогүй байна. Хуулгаа шалгана уу.")
            
            records = []
            for txn in unclassified:
                records.append({
                    "id": txn.id,
                    "date": txn.date,
                    "description": txn.description,
                    "amount": float(txn.amount),
                    "type": txn.type,
                    "bank": txn.bank_name
                })
            if records:
                st.dataframe(pd.DataFrame(records), use_container_width=True)
        else:
            records = []
            for counterparty_id, transactions in transactions_by_counterparty.items():
                counterparty = counterparties.get(counterparty_id)
                if not counterparty:
                    continue
                descriptions = list(dict.fromkeys(txn.description or "" for txn in transactions))[:3]
                incoming = sum((txn.amount for txn in transactions if txn.amount > 0), Decimal("0.00"))
                outgoing = sum((abs(txn.amount) for txn in transactions if txn.amount < 0), Decimal("0.00"))
                
                default_cat_id = getattr(counterparty, "default_category_id", None)
                selected_category = next(
                    (
                        f"{kind_labels.get(category.kind, category.kind)}: {category.name}"
                        for category in categories
                        if category.id == default_cat_id
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

            if not frame.empty:
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
                    )
                    submitted = st.form_submit_button("Хадгалаад ангилах", type="primary")

                if submitted:
                    changed_ids: list[int] = []
                    edited_rows = edited.set_index("counterparty_id").to_dict("index")
                    for counterparty_id, values in edited_rows.items():
                        c_id = int(counterparty_id)
                        selected = values["category"] or ""
                        new_display_name = values["display_name"] or None
                        new_cat_id = category_by_label.get(selected)
                        new_own = 1 if values["own account"] else 0
                        new_ask = 1 if values["ask per txn"] else 0

                        session.execute(
                            text("UPDATE counterparties SET display_name = :d, default_category_id = :c, is_own_account = :o, ask_per_txn = :a WHERE id = :id"),
                            {"d": new_display_name, "c": new_cat_id, "o": new_own, "a": new_ask, "id": c_id}
                        )
                        
                        tx_res = session.execute(
                            text("SELECT id FROM transactions WHERE counterparty_id = :id"),
                            {"id": c_id}
                        ).fetchall()
                        changed_ids.extend([t[0] for t in tx_res])
                        
                    with st.spinner("Гүйлгээг дахин ангилж байна..."):
                        classify_transactions(session, changed_ids)
                    notification_message = "Харилцагчдын тохиргоог хадгалж, гүйлгээг дахин ангиллаа."
                    rerun_requested = True
            else:
                st.info("Ангилах харилцагчийн мэдээлэл одоогоор алга байна.")
except Exception as error:
    st.error(f"Алдаа гарлаа: {error}")
    st.code(traceback.format_exc())

if notification_message:
    st.success(notification_message)
    st.toast("Харилцагчийн тохиргоо амжилттай хадгалагдлаа.")

render_footer()
if rerun_requested:
    st.rerun()