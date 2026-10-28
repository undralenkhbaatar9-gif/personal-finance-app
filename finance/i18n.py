import streamlit as st


def get_lang() -> str:
    if "lang" not in st.session_state:
        st.session_state["lang"] = "mn"
    return st.session_state["lang"]


def language_switcher():
    lang = get_lang()
    with st.sidebar:
        choice = st.selectbox(
            "Хэл / Language",
            options=["mn", "en"],
            format_func=lambda x: "Монгол" if x == "mn" else "English",
            index=0 if lang == "mn" else 1,
            key="lang_switcher_main",
        )
        if choice != st.session_state.get("lang"):
            st.session_state["lang"] = choice
            st.rerun()
    return st.session_state["lang"]
