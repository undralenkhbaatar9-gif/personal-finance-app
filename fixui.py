path = "finance/ui.py"
with open(path, encoding="utf-8") as f:
    s = f.read()

func = '''def render_lang_toggle(location: str = "sidebar") -> str:
    if "lang" not in st.session_state:
        st.session_state["lang"] = "mn"
    lang = st.session_state["lang"]
    if location in ("sidebar", "side", "left"):
        with st.sidebar:
            st.markdown("**Хэл / Language**")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("MN", use_container_width=True, type="primary" if lang == "mn" else "secondary", key="lang_mn_sb"):
                    st.session_state["lang"] = "mn"
                    st.rerun()
            with c2:
                if st.button("EN", use_container_width=True, type="primary" if lang == "en" else "secondary", key="lang_en_sb"):
                    st.session_state["lang"] = "en"
                    st.rerun()
        return st.session_state["lang"]
    c1, c2, c3 = st.columns([8, 1, 1])
    with c2:
        if st.button("MN", use_container_width=True, type="primary" if st.session_state["lang"] == "mn" else "secondary", key="lang_mn_top"):
            st.session_state["lang"] = "mn"
            st.rerun()
    with c3:
        if st.button("EN", use_container_width=True, type="primary" if st.session_state["lang"] == "en" else "secondary", key="lang_en_top"):
            st.session_state["lang"] = "en"
            st.rerun()
    return st.session_state["lang"]


'''

start = s.find("def render_lang_toggle")
if start >= 0:
    end = s.find("\ndef ", start + 1)
    if end == -1:
        end = len(s)
    s2 = s[:start] + func + s[end:]
else:
    idx = s.find("def style_plotly_chart")
    if idx == -1:
        idx = len(s)
    s2 = s[:idx] + func + s[idx:]

if "__all__" in s2 and "render_lang_toggle" not in s2:
    s2 = s2.replace(
        '__all__ = ["apply_global_styles", "render_footer", "style_plotly_chart"]',
        '__all__ = ["apply_global_styles", "render_footer", "style_plotly_chart", "render_lang_toggle"]',
    )

with open(path, "w", encoding="utf-8") as f:
    f.write(s2)
print("done")
