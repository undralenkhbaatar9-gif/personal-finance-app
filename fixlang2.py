path = 'pages/2_Review.py'
s = open(path, encoding='utf-8').read()
old = 'apply_global_styles()\nst.title("\ud83d\udd0d \u0433\u04af\u0439\u043b\u0433\u044d\u044d \u0445\u044f\u043d\u0430\u0445, \u0430\u043d\u0433\u0438\u043b\u0430\u0445")'
# try different
if old not in s:
    old = 'apply_global_styles()\r\nst.title("\ud83d\udd0d \u0433\u04af\u0439\u043b\u0433\u044d\u044d \u0445\u044f\u043d\u0430\u0445, \u0430\u043d\u0433\u0438\u043b\u0430\u0445")'
if old not in s:
    # grep
    import re
    m = re.search(r"st\.title\([^)]+\)", s)
    if m:
        old = m.group(0)
        # reconstruct
        prefix = s.split(old)[0]
        new = prefix + 'from finance.i18n import language_switcher\nlang = language_switcher()\napply_global_styles()\nif lang == "mn":\n    st.title("\ud83d\udd0d \u0413\u04af\u0439\u043b\u0433\u044d\u044d \u0445\u044f\u043d\u0430\u0445, \u0430\u043d\u0433\u0438\u043b\u0430\u0445")\nelse:\n    st.title("\ud83d\udd0d Review & Classify Transactions")'
        open(path,'w',encoding='utf-8').write(new)
        print('replaced')
        raise SystemExit
    else:
        print('no')
        raise SystemExit
new = old.replace('apply_global_styles()\n', 'from finance.i18n import language_switcher\nlang = language_switcher()\napply_global_styles()\n')
# add lang based
# simpler
s2 = s.replace(old, 'from finance.i18n import language_switcher\nlang = language_switcher()\napply_global_styles()\nif lang == "mn":\n    st.title("\ud83d\udd0d \u0413\u04af\u0439\u043b\u0433\u044d\u044d \u0445\u044f\u043d\u0430\u0445, \u0430\u043d\u0433\u0438\u043b\u0430\u0445")\nelse:\n    st.title("\ud83d\udd0d Review and Classify Transactions")')
open(path,'w',encoding='utf-8').write(s2)
print('done')
