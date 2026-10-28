import re

path = "pages/2_Review.py"
with open(path, encoding="utf-8", errors="replace") as f:
    s = f.read()

if "language_switcher" not in s:
    s = s.replace(
        "from finance.ui import apply_global_styles, render_footer",
        "from finance.ui import apply_global_styles, render_footer\nfrom finance.i18n import language_switcher",
    )

if "lang = language_switcher()" not in s:
    s = s.replace("apply_global_styles()", "lang = language_switcher()\napply_global_styles()")

# replace first st.title
s = re.sub(r'st\.title\([^)]+\)', 'st.title("Гүйлгээ хянах, ангилах" if lang == "mn" else "Review and Classify Transactions")', s)

with open(path, "w", encoding="utf-8") as f:
    f.write(s)

print("done")
