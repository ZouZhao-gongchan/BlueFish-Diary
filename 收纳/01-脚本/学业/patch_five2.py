import io, re
P = r"E:\Agent-bluefish\working\build_five.py"
s = io.open(P, encoding="utf-8").read()
before = s.count("排版约定")
s2 = re.sub(r"\n *p = doc\.add_paragraph\(\)\n *p\.paragraph_format\.space_before = Pt\(8\)\n *p\.alignment = WD_ALIGN_PARAGRAPH\.CENTER\n *add_rich\(p, \"排版约定[^\n]*\n", "\n", s)
if s2 == s:
    # 兜底：只删 add_rich 那行
    s2 = re.sub(r"\n *add_rich\(p, \"排版约定[^\n]*", "", s)
io.open(P, "w", encoding="utf-8").write(s2)
print("occurrences before:", before, " after:", s2.count("排版约定"))
