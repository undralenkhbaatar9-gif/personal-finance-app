path = 'pages/4_Reports.py'
with open(path, 'r', encoding='utf-8', errors='replace') as f:
    c = f.read()
# fix corrupted
c = c.replace('dY"^"', '📈')
c = c.replace('�', '')
with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
