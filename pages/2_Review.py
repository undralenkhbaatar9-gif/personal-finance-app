from decimal import Decimal
import pandas as pd
import streamlit as st
from sqlalchemy import select, or_

from finance.classifier import classify_transactions
from finance.db import get_session
from finance.models import Category, Counterparty, Transaction
from finance.ui import apply_global_styles, render_footer

apply_global_styles()
st.title("Гүйлгээ ангилах")
rerun_requested = False
notification_message: str | None = None
kind_labels = {"income": "Орлого", "expense": "Зарлага", "transfer": "Шилжүүлэг"}

try:
    with get_session() as session:
        categories = session.scalars(
            select(Category).order_by(Category.kind, Category.name)
        ).all()
        
        with st.spinner("Ангилаагүй гүйлгээнүүдийг ачаалж байна..."):
            unclassified = session.scalars(
                select(Transaction).where(
                    or_(
                        Transaction.category_source == "unclassified",
                        Transaction.category_source.is_(None),
                        Transaction.category_id.is_(None)
                    )
                )
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
        
        counterparties = {}
        if counterparty_ids:
            cp_results = session.scalars(
                select(Counterparty).where(Counterparty.id.in_(counterparty_ids))
            ).all()
            counterparties = {item.id: item for item in cp_results}
        
        transactions_by_counterparty: dict[int, list[Transaction]] = {}
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
                        counterparty = counterparties.get(int(counterparty_id))
                        if not counterparty:
                            continue
                        selected = values["category"] or ""
                        counterparty.display_name = values["display_name"] or None
                        counterparty.default_category_id = category_by_label.get(selected)
                        counterparty.is_own_account = bool(values["own account"])
                        counterparty.ask_per_txn = bool(values["ask per txn"])
                        
                        tx_results = session.scalars(
                            select(Transaction.id).where(
                                Transaction.counterparty_id == counterparty.id
                            )
                        ).all()
                        changed_ids.extend(tx_results)
                        
                    with st.spinner("Гүйлгээг дахин ангилж байна..."):
                        classify_transactions(session, changed_ids)
                    notification_message = "Харилцагчдын тохиргоог хадгалж, гүйлгээг дахин ангиллаа."
                    rerun_requested = True
            else:
                st.info("Ангилах харилцагчийн мэдээлэл одоогоор алга байна.")
except Exception as error:
    st.error(f"Алдаа гарлаа: {error}")

if notification_message:
    st.success(notification_message)
    st.toast("Харилцагчийн тохиргоо амжилттай хадгалагдлаа.")

render_footer()
if rerun_requested:
    st.rerun()