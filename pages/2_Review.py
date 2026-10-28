from decimal import Decimal
import traceback

import pandas as pd
import streamlit as st
from sqlalchemy import text

from finance.classifier import classify_transactions
from finance.db import get_session
from finance.i18n import get_lang
from finance.ui import apply_global_styles, render_footer, render_lang_toggle

lang = render_lang_toggle(location="sidebar") or get_lang()
apply_global_styles()

if lang == "mn":
    st.title("Гүйлгээ хянах, ангилах")
else:
    st.title("Review & Classify Transactions")

rerun_requested = False
notification_message = None
if lang == "mn":
    kind_labels = {"income": "Орлого", "expense": "Зарлага", "transfer": "Шилжүүлэг"}
else:
    kind_labels = {"income": "Income", "expense": "Expense", "transfer": "Transfer"}
