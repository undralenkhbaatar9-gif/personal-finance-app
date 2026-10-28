path = 'pages/1_Import.py'
with open(path, 'r', encoding='utf-8', errors='replace') as f:
    c = f.read()
c = c.replace('page_title="D�����D�D3D� D,D�D�D_�?�,D�D_�."', 'page_title="Банкны хуулга импортлох"')
with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
