# -*- coding: utf-8 -*-
"""把 CRC 竖式 ASCII 块换成对齐表格；并让推导表整表不拆页"""
import io, re

P = r"E:\Agent-bluefish\working\build_five.py"
src = io.open(P, encoding="utf-8").read()

# ---- 1) 替换 CRC 模 2 除法块 ----
start = src.index('MONO([\n    "被除数')
end = src.index('], size=8.5)', start) + len('], size=8.5)')
new_block = '''T(
    ["步", "被除数（除式）", "异或", "余式"],
    [
        ["①", "1 0 1 1 0 0 1 0 0 0 0", "1 1 0 0 1 0 0 0 0 0 0", "1 1 1 1 0 1 0 0 0 0"],
        ["②", "1 1 1 1 0 1 0 0 0 0", "1 1 0 0 1 0 0 0 0 0", "1 1 1 1 0 0 0 0"],
        ["③", "1 1 1 1 0 0 0 0", "1 1 0 0 1 0 0 0", "1 1 1 0 0 0"],
        ["④", "1 1 1 0 0 0", "1 1 0 0 1 0", "1 0 1 0"],
    ],
    [1.2, 6.2, 6.2, 4.6],
    size=8.6,
)'''
src = src[:start] + new_block + src[end:]

# ---- 2) DERIV 整表不拆页：除最后一行外都 keep_with_next ----
src = src.replace(
    '''    cant_split(t)
    gap = doc.add_paragraph()
    gap.paragraph_format.space_before = Pt(0)
    gap.paragraph_format.space_after = Pt(0)
    gap.paragraph_format.line_spacing = 0.45''',
    '''    cant_split(t)
    for ri, row in enumerate(t.rows):
        if ri < len(t.rows) - 1:
            for c in row.cells:
                for pp in c.paragraphs:
                    pp.paragraph_format.keep_with_next = True
    gap = doc.add_paragraph()
    gap.paragraph_format.space_before = Pt(0)
    gap.paragraph_format.space_after = Pt(0)
    gap.paragraph_format.line_spacing = 0.45''')

io.open(P, "w", encoding="utf-8").write(src)
print("patched ok")
