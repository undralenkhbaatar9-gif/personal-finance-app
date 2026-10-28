with open('finance/ui.py','r',encoding='utf-8',errors='replace') as f:
    s=f.read()
old = '''def render_lang_toggle(location: str = "sidebar") -> str:
    """Simple language toggle."""
    try:
        import streamlit as st
    except Exception:
        return "mn"
    if not hasattr(st, "session_state"):
        return "mn"
    if "lang" not in st.session_state:
        st.session_state["lang"] = "mn"
    lang = st.session_state["lang"]
    try:
        if location in ("sidebar", "side", "left"):
            with st.sidebar:
                st.markdown("**Хэл / Language**")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("MN", use_container_width=True, type="primary" if lang == "mn" else "secondary", key="lt_mn_sb"):
                        st.session_state["lang"] = "mn"
                        st.rerun()
                with c2:
                    if st.button("EN", use_container_width=True, type="primary" if lang == "en" else "secondary", key="lt_en_sb"):
                        st.session_state["lang"] = "en"
                        st.rerun()
            return st.session_state["lang"]
    except Exception:
        pass
    try:
        c1, c2, c3 = st.columns([8, 1, 1])
        with c2:
            if st.button("MN", use_container_width=True, type="primary" if st.session_state.get("lang") == "mn" else "secondary", key="lt_mn_top"):
                st.session_state["lang"] = "mn"
                st.rerun()
        with c3:
            if st.button("EN", use_container_width=True, type="primary" if st.session_state.get("lang") == "en" else "secondary", key="lt_en_top"):
                st.session_state["lang"] = "en"
                st.rerun()
    except Exception:
        pass
    return st.session_state.get("lang", "mn")'''
new = '''def render_lang_toggle(location: str = "top") -> str:
    try:
        import streamlit as st
    except Exception:
        return "mn"
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
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("MN", use_container_width=True, type="primary" if cur == "mn" else "secondary", key="lt_mn_sb"):
                        st.session_state["lang"] = "mn"
                        st.rerun()
                with c2:
                    if st.button("EN", use_container_width=True, type="primary" if cur == "en" else "secondary", key="lt_en_sb"):
                        st.session_state["lang"] = "en"
                        st.rerun()
            return st.session_state["lang"]
        else:
            c1, c2, c3 = st.columns([7, 1, 1])
            with c2:
                if st.button("MN", use_container_width=True, type="primary" if st.session_state.get("lang") == "mn" else "secondary", key="lt_mn_tr"):
                    st.session_state["lang"] = "mn"
                    st.rerun()
            with c3:
                if st.button("EN", use_container_width=True, type="primary" if st.session_state.get("lang") == "en" else "secondary", key="lt_en_tr"):
                    st.session_state["lang"] = "en"
                    st.rerun()
            return st.session_state["lang"]
    except Exception:
        pass
    return st.session_state.get("lang", "mn")'''
if old in s:
    with open('finance/ui.py','w',encoding='utf-8') as f:
        f.write(s.replace(old,new))
    print('ok')
else:
    print('no')
