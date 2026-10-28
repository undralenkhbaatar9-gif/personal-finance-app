import streamlit as st


def render_lang_toggle(location: str = "top") -> str:
    """Language toggle - single button switching MN<->EN in top right."""
    try:
        if not hasattr(st, "session_state"):
            return "mn"
        if "lang" not in st.session_state:
            st.session_state["lang"] = "mn"
        cur = st.session_state["lang"]
        try:
            if location in ("sidebar", "side", "left"):
                with st.sidebar:
                    st.markdown("<div style='display:flex;align-items:center;gap:8px;margin:6px 0;'><span style='font-size:18px;'>🏦</span><span style='font-weight:700;'>Personal Finance</span></div>", unsafe_allow_html=True)
                    st.markdown("**Хэл / Language**")
                    if st.button("MN" if cur == "en" else "EN", use_container_width=True, key="lt_toggle_sb"):
                        st.session_state["lang"] = "en" if cur == "mn" else "mn"
                        st.rerun()
                return st.session_state["lang"]
            else:
                c1, c2, c3 = st.columns([7, 1, 1])
                with c3:
                    label = "EN" if cur == "mn" else "MN"
                    if st.button(label, use_container_width=True, key="lt_toggle_tr"):
                        st.session_state["lang"] = "en" if cur == "mn" else "mn"
                        st.rerun()
                return st.session_state["lang"]
        except Exception:
            pass
        return st.session_state.get("lang", "mn")
    except Exception:
        return "mn"
