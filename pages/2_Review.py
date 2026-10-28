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
        # 1. Categories хүснэгтээс өгөгдөл татах
        categories_raw = session.execute(
            text("SELECT id, kind, name FROM categories ORDER BY kind, name")
        ).fetchall()
        
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

        # 2. Unclassified гүйлгээнүүдийг SQL-ээр татах
        with st.spinner("Ангилаагүй гүйлгээнүүдийг ачаалж байна..."):
            tx_raw = session.execute(
                text("""
                    SELECT id, date, description, amount, type, category_source, category_id, counterparty_id, bank_name 
                    FROM transactions 
                    WHERE category_source = 'unclassified' OR category_source IS NULL OR category_id IS NULL
                """)
            ).fetchall()

        unclassified = []
        for r in tx_raw:
            unclassified.append(SimpleObj(
                id=r[0], date=r[1], description=r[2], amount=Decimal(str(r[3]) if r[3] is not None else "0"),
                type=r[4], category_source=r[5], category_id=r[6], counterparty_id=r[7], bank_name=r[8]
            ))

        counterparty_ids = {txn.counterparty_id for txn in unclassified if txn.counterparty_id}
        
        counterparties = {}
        if counterparty_ids:
            id_list = ",".join(str(i) for i in counterparty_ids)
            cp_raw = session.execute(
                text(f"SELECT id, match_key, display_name, default_category_id, is_own_account, ask_per_txn FROM counterparties WHERE id IN ({id_list})")
            ).fetchall()
            for r in cp_raw:
                counterparties[r[0]] = SimpleObj(
                    id=r[0], match_key=r[1], display_name=r[2], 
                    default_category_id=r[3], is_own_account=bool(r[4]), ask_per_txn=bool(r[5])
                )
        
        transactions_by_counterparty: dict[int, list] = {}
        for txn in unclassified:
            if txn.counterparty_id is not None:
                transactions_by_counterparty.setdefault(txn.counterparty_id, []).append(txn)

        st.sidebar.metric("Ангилаагүй гүйлгээ", len(unclassified))
        
        if not unclassified:
            st.success("Бүх гүйлгээ ангилагдсан байна.")
        elif not transactions_by_counterparty:
            st.info("Ангилаагүй гүйлгээнд харилцагч холбогдоогүй байна. Импортлогдсон гүйлгээнүүдийг шалгана уу.")
            
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

                        # Counterparties хүснэгтийг SQL-ээр шинэчлэх
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