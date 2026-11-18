# -*- coding: utf-8 -*-
"""生成《信息论 · 编码五题详解》docx（工整公式排版版）"""
import re
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

FONT_BODY = "宋体"
FONT_HEAD = "微软雅黑"
FONT_MATH = "Cambria Math"
FONT_MONO = "Consolas"
ACCENT = "1F3864"
ACCENT_LIGHT = "D9E2F3"
EQ_FILL = "F4F7FB"
EX_FILL = "FFF6E9"
EX_LINE = "C55A11"
GREEN = "2E6B34"
GREEN_FILL = "EAF4EA"
GRAY = "595959"

WRITE = r"E:\Agent-bluefish\working\信息论编码五题详解.docx"


def set_fonts(run, ascii_name, ea_name, size=None, bold=None, italic=None, color=None):
    run.font.name = ascii_name
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)
    rfonts.set(qn("w:ascii"), ascii_name)
    rfonts.set(qn("w:hAnsi"), ascii_name)
    rfonts.set(qn("w:eastAsia"), ea_name)
    rfonts.set(qn("w:cs"), ascii_name)
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold
    if italic is not None:
        run.font.italic = italic
    if color is not None:
        run.font.color.rgb = RGBColor.from_string(color)


def shade_paragraph(p, fill):
    ppr = p._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    ppr.append(shd)


def para_border(p, side="left", color=ACCENT, sz=18, space=6):
    ppr = p._p.get_or_add_pPr()
    pbdr = ppr.find(qn("w:pBdr"))
    if pbdr is None:
        pbdr = OxmlElement("w:pBdr")
        ppr.append(pbdr)
    el = OxmlElement("w:%s" % side)
    el.set(qn("w:val"), "single")
    el.set(qn("w:sz"), str(sz))
    el.set(qn("w:space"), str(space))
    el.set(qn("w:color"), color)
    pbdr.append(el)


def box_paragraph(p, color="9DB3D5", sz=6, space=4):
    for side in ("top", "left", "bottom", "right"):
        para_border(p, side, color, sz, space)


def shade_cell(cell, fill):
    tcpr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tcpr.append(shd)


def cell_borders(cell, color="9DB3D5", sz=6):
    tcpr = cell._tc.get_or_add_tcPr()
    borders = OxmlElement("w:tcBorders")
    for edge in ("top", "left", "bottom", "right"):
        el = OxmlElement("w:%s" % edge)
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), str(sz))
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), color)
        borders.append(el)
    tcpr.append(borders)


def table_borders(table, color="A6A6A6", sz=4):
    tblpr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement("w:%s" % edge)
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), str(sz))
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), color)
        borders.append(el)
    tblpr.append(borders)


def no_borders(table):
    tblpr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement("w:%s" % edge)
        el.set(qn("w:val"), "none")
        el.set(qn("w:sz"), "0")
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), "auto")
        borders.append(el)
    tblpr.append(borders)


def table_cell_margins(table, top=26, bottom=26, left=60, right=60):
    tblpr = table._tbl.tblPr
    mar = OxmlElement("w:tblCellMar")
    for side, val in (("top", top), ("left", left), ("bottom", bottom), ("right", right)):
        el = OxmlElement("w:%s" % side)
        el.set(qn("w:w"), str(val))
        el.set(qn("w:type"), "dxa")
        mar.append(el)
    tblpr.append(mar)


def fixed_layout(table):
    tblpr = table._tbl.tblPr
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    tblpr.append(layout)


# %%...%% = 粗斜体（矢量）；**...** = 粗体（矩阵/强调）；_{} ^{} = 上下标
TOKEN = re.compile(r"(\*\*.+?\*\*|%%.+?%%|_\{[^}]*\}|\^\{[^}]*\})")


def add_rich(p, text, font=FONT_MATH, size=10, color=None, bold=False, italic=False):
    for part in TOKEN.split(text):
        if not part:
            continue
        b, i, sub, sup, t = bold, italic, False, False, part
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            b, t = True, part[2:-2]
        elif part.startswith("%%") and part.endswith("%%") and len(part) > 4:
            b, i, t = True, True, part[2:-2]
        elif part.startswith("_{") and part.endswith("}"):
            sub, t = True, part[2:-1]
        elif part.startswith("^{") and part.endswith("}"):
            sup, t = True, part[2:-1]
        r = p.add_run(t)
        set_fonts(r, font, FONT_BODY, size, b, i, color)
        if sub:
            r.font.subscript = True
        if sup:
            r.font.superscript = True


doc = Document()
st = doc.styles["Normal"]
st.font.name = FONT_MATH
st.font.size = Pt(10)
rpr = st.element.get_or_add_rPr()
rf = rpr.find(qn("w:rFonts"))
if rf is None:
    rf = OxmlElement("w:rFonts")
    rpr.insert(0, rf)
for k in ("w:ascii", "w:hAnsi"):
    rf.set(qn(k), FONT_MATH)
rf.set(qn("w:eastAsia"), FONT_BODY)
st.paragraph_format.space_before = Pt(0)
st.paragraph_format.space_after = Pt(2)
st.paragraph_format.line_spacing = 1.12

sec = doc.sections[0]
sec.page_width = Cm(21)
sec.page_height = Cm(29.7)
sec.top_margin = Cm(1.6)
sec.bottom_margin = Cm(1.5)
sec.left_margin = Cm(1.7)
sec.right_margin = Cm(1.7)


def H1(text, pb=False):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(10)
    pf.space_after = Pt(5)
    pf.keep_with_next = True
    if pb:
        pf.page_break_before = True
    shade_paragraph(p, ACCENT)
    r = p.add_run("  " + text)
    set_fonts(r, FONT_HEAD, FONT_HEAD, 11.5, True, False, "FFFFFF")


def H2(text):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(7)
    pf.space_after = Pt(3)
    pf.keep_with_next = True
    add_rich(p, "▍" + text, font=FONT_HEAD, size=10.5, color=ACCENT, bold=True)


def B(items, size=9.5):
    for it in items:
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.space_before = Pt(0)
        pf.space_after = Pt(1)
        pf.left_indent = Cm(0.6)
        pf.first_line_indent = Cm(-0.45)
        pf.line_spacing = 1.18
        add_rich(p, "• " + it, font=FONT_MATH, size=size)


def NOTE(text, size=8.5):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(3)
    pf.left_indent = Cm(0.15)
    add_rich(p, text, font=FONT_BODY, size=size, color=GRAY)


def EQ(text, size=10.5, indent=0.9):
    """单行公式：浅底 + 左竖线"""
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(2)
    pf.space_after = Pt(2)
    pf.left_indent = Cm(indent)
    pf.line_spacing = 1.2
    shade_paragraph(p, EQ_FILL)
    para_border(p, "left", ACCENT, 12, 6)
    add_rich(p, text, font=FONT_MATH, size=size)


DERIV_HINT = None


def DERIV(rows, size=10, indent=1.0, widths=(4.6, 1.0, 11.6), mono=False):
    """多步推导：无边框三列表格，等号严格对齐（rows = [(左式, 符号, 右式), ...]）"""
    t = doc.add_table(rows=0, cols=3)
    t.alignment = WD_TABLE_ALIGNMENT.LEFT
    t.autofit = False
    fixed_layout(t)
    no_borders(t)
    table_cell_margins(t, top=12, bottom=12, left=0, right=40)
    for lhs, op, rhs in rows:
        cells = t.add_row().cells
        for idx, (txt, al) in enumerate((
            (lhs, WD_ALIGN_PARAGRAPH.RIGHT),
            (op, WD_ALIGN_PARAGRAPH.CENTER),
            (rhs, WD_ALIGN_PARAGRAPH.LEFT),
        )):
            p = cells[idx].paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.18
            p.alignment = al
            if txt:
                add_rich(p, txt, font=(FONT_MONO if mono else FONT_MATH), size=size)
    for i, w in enumerate(widths):
        for row in t.rows:
            row.cells[i].width = Cm(w)
    cant_split(t)
    for ri, row in enumerate(t.rows):
        if ri < len(t.rows) - 1:
            for c in row.cells:
                for pp in c.paragraphs:
                    pp.paragraph_format.keep_with_next = True
    gap = doc.add_paragraph()
    gap.paragraph_format.space_before = Pt(0)
    gap.paragraph_format.space_after = Pt(0)
    gap.paragraph_format.line_spacing = 0.45
    r = gap.add_run("")
    set_fonts(r, FONT_BODY, FONT_BODY, 7)


def MONO(lines, size=9.5, fill="F7F7F7"):
    """等宽块（矩阵、竖式、码字表），整块加框"""
    n = len(lines)
    for k, line in enumerate(lines):
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.space_before = Pt(3 if k == 0 else 0)
        pf.space_after = Pt(3 if k == n - 1 else 0)
        pf.left_indent = Cm(0.9)
        pf.line_spacing = 1.0
        pf.keep_together = True
        if k < n - 1:
            pf.keep_with_next = True
        shade_paragraph(p, fill)
        box_paragraph(p)
        add_rich(p, line if line else " ", font=FONT_MONO, size=size)


def cant_split(table):
    for row in table.rows:
        trPr = row._tr.get_or_add_trPr()
        el = OxmlElement("w:cantSplit")
        trPr.append(el)


def T(header, rows, widths, size=8.8, align_left=False):
    t = doc.add_table(rows=1, cols=len(header))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    fixed_layout(t)
    table_borders(t)
    table_cell_margins(t, top=24, bottom=24, left=60, right=60)
    hdr = t.rows[0].cells
    for i, h in enumerate(header):
        hdr[i].text = ""
        p = hdr[i].paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_rich(p, h, font=FONT_HEAD, size=size, bold=True, color=ACCENT)
        shade_cell(hdr[i], ACCENT_LIGHT)
        hdr[i].vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    for row in rows:
        cells = t.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.08
            if not align_left:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            add_rich(p, val, font=FONT_MATH, size=size)
            cells[i].vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    for i, w in enumerate(widths):
        for row in t.rows:
            row.cells[i].width = Cm(w)
    cant_split(t)
    gap = doc.add_paragraph()
    gap.paragraph_format.space_before = Pt(0)
    gap.paragraph_format.space_after = Pt(0)
    gap.paragraph_format.line_spacing = 0.5
    r = gap.add_run("")
    set_fonts(r, FONT_BODY, FONT_BODY, 7)


def QNO(no, desc, score):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(11)
    pf.space_after = Pt(3)
    pf.keep_with_next = True
    shade_paragraph(p, GREEN_FILL)
    para_border(p, "left", GREEN, 20, 5)
    add_rich(p, "  " + no + "　" + desc, font=FONT_HEAD, size=11.5, color=GREEN, bold=True)
    r = p.add_run("　（" + score + "）")
    set_fonts(r, FONT_HEAD, FONT_HEAD, 9.5, True, False, EX_LINE)


def QT(text):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(2)
    pf.space_after = Pt(3)
    pf.left_indent = Cm(0.2)
    pf.line_spacing = 1.22
    add_rich(p, text, font=FONT_MATH, size=10)


def STEP(n, text, size=9.8):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(3)
    pf.space_after = Pt(1)
    pf.left_indent = Cm(0.75)
    pf.first_line_indent = Cm(-0.45)
    pf.line_spacing = 1.22
    pf.keep_with_next = True
    add_rich(p, "（" + str(n + 1) + "）" + text, font=FONT_MATH, size=size)


def ANS(text, size=9.8):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(4)
    pf.space_after = Pt(3)
    pf.left_indent = Cm(0.6)
    pf.line_spacing = 1.25
    shade_paragraph(p, EX_FILL)
    para_border(p, "left", EX_LINE, 16, 6)
    add_rich(p, "答案　" + text, font=FONT_MATH, size=size, color=EX_LINE, bold=True)


fp = sec.footer.paragraphs[0]
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
r1 = fp.add_run("信息论 · 编码五题详解　—　")
set_fonts(r1, FONT_BODY, FONT_BODY, 8, False, False, GRAY)
r = fp.add_run()
set_fonts(r, FONT_BODY, FONT_BODY, 8, False, False, GRAY)
fld = OxmlElement("w:fldSimple")
fld.set(qn("w:instr"), " PAGE ")
fp._p.append(fld)

# ================= 标题 =================
p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(0)
p.paragraph_format.space_after = Pt(2)
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("信息论 · 编码五题详解")
set_fonts(r, FONT_HEAD, FONT_HEAD, 21, True, False, ACCENT)

p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(0)
p.paragraph_format.space_after = Pt(6)
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
add_rich(p, "信道容量 · 变长编码 · 霍夫曼编码 · CRC 校验 · 线性分组码", font=FONT_HEAD, size=10, color=GRAY)

H2("符号与排版约定（以后都按这个来）")
T(
    ["记号", "含义", "示例"],
    [
        ["**黑斜体**", "矢量 / 向量（GB 3102 习惯）", "码字矢量 %%r%%、信息矢量 %%m%%"],
        ["**粗正体**", "矩阵", "生成矩阵 **G**、校验矩阵 **H**"],
        ["常规正体", "标量、常数、运算符", "码长 n、错误概率 p、熵 H"],
        ["下角标", "区分同一类量", "H(X)、H(X|Y)、%%r%%_{i}"],
        ["等宽框", "矩阵、竖式除法、码字表", "见第 4、5 题的框"],
    ],
    [2.8, 7.4, 7.4],
    size=8.8,
)
NOTE("多步推导一律按等号对齐（左侧写「本步要算的量」，等号一列，右侧写「怎么来的」），这样一眼能看出哪一步变形、哪一步代入数值。")

H1("第 1 题　香农公式求信道容量")
QT("在电话信道中常允许许多路复用。一般电话信号的带宽为 3.3 kHz。若信噪功率比为 20 dB（即 P_{s}/(N_{0}W) = 100），计算电话信道的信道容量。")

H2("① 先把题面翻译成符号")
T(
    ["题面说法", "符号", "数值"],
    [
        ["带宽 3.3 kHz", "B", "3.3×10³ Hz"],
        ["信噪功率比 20 dB", "S/N", "10^{20/10} = 100"],
        ["（题面已给出）P_{s}/(N_{0}W)", "S/(N_{0}B)", "100"],
    ],
    [6.6, 4.6, 6.4],
    size=9,
)
NOTE("dB 与比值的换算：x dB ⇔ 10^{x/10}。所以 20 dB = 100 倍，题目括号里那个 100 正好和它一致，说明两个说法是同一件事。")

H2("② 套香农公式")
EQ("C = B·log_{2}(1 + S/N)")
STEP(0, "代入 B = 3.3×10³ Hz、S/N = 100：")
DERIV([
    ("C", "=", "3.3×10^{3} × log_{2}(1 + 100)"),
    ("", "=", "3.3×10^{3} × log_{2}(101)"),
])
STEP(1, "算对数：101 不是 2 的整数次幂，用换底公式。")
DERIV([
    ("log_{2}101", "=", "ln101 / ln2"),
    ("", "=", "4.6151 / 0.6931"),
    ("", "≈", "6.658　(bit)"),
])
NOTE("记住几个常用值能省时间：log₂2 = 1、log₂4 = 2、log₂8 = 3、log₂10 ≈ 3.322、log₂100 ≈ 6.644。101 比 100 只多一点，所以 6.658 略大于 6.644，合理。")
STEP(2, "乘回带宽：")
DERIV([
    ("C", "=", "3.3×10^{3} × 6.658"),
    ("", "≈", "2.197×10^{4} bit/s"),
    ("", "=", "21.97 kbit/s"),
])
ANS("C ≈ 21.97 kbit/s（约 22 kbit/s），折算成带宽效率约 6.66 bit/s/Hz。")

H2("③ 顺带说清楚「为什么是极限」")
B([
    "这是**无差错传输的最高速率**：香农第二定理说，只要实际速率 R < C，就存在编码让误码率任意小；R > C 则不可能可靠传输。",
    "注意 C 是「存在性」结论，它不告诉你用哪种码 —— 那要靠 LDPC、Turbo 这类编码去逼近。",
    "如果信噪比提到 30 dB（比值 1000）：C = 3300×log₂1001 ≈ 32.9 kbit/s。功率涨 10 倍，容量只涨 1.5 倍，这就是对数增长的含义。",
])
NOTE("【踩分点】dB 换算成 100（2 分）→ 写出香农公式（2 分）→ 算出 log₂101 ≈ 6.658（3 分）→ 结果与单位（3 分）。直接拿 20 代进去是典型错法，会立刻掉一半分。")

H1("第 2 题　变长编码（L=2 扩展）与编码效率")
QT("设离散无记忆信源的概率空间为 X = {a_{1}, a_{2}}，P = (3/4, 1/4)。当 L = 2 的信源序列进行变长编码时，给出编码结果，并计算编码效率。")

H2("① 先做 L = 2 的扩展信源")
STEP(0, "无记忆 ⇒ 序列概率等于各符号概率之积，共 2² = 4 个长度为 2 的序列：")
T(
    ["序列", "a_{1}a_{1}", "a_{1}a_{2}", "a_{2}a_{1}", "a_{2}a_{2}"],
    [["概率", "9/16", "3/16", "3/16", "1/16"]],
    [2.6, 3.4, 3.4, 3.4, 3.4],
    size=9,
)
NOTE("检查归一化：9/16 + 3/16 + 3/16 + 1/16 = 16/16 = 1 ✓ 这一步养成习惯，能挡掉一半的低级错误。")

H2("② 对这 4 个序列做霍夫曼合并")
T(
    ["步", "挑出最小的两个", "合并后", "性质"],
    [
        ["①", "3/16 (a_{2}a_{1}) + 1/16 (a_{2}a_{2})", "4/16", "新节点 n_{1}"],
        ["②", "3/16 (a_{1}a_{2}) + 4/16 (n_{1})", "7/16", "新节点 n_{2}"],
        ["③", "9/16 (a_{1}a_{1}) + 7/16 (n_{2})", "1", "根"],
    ],
    [1.2, 8.6, 2.6, 4.4],
    size=8.8,
)
STEP(1, "按「概率小的走 0 支、大的走 1 支」从根往下读，得码字：")
T(
    ["序列", "a_{1}a_{1}", "a_{1}a_{2}", "a_{2}a_{1}", "a_{2}a_{2}"],
    [["概率", "9/16", "3/16", "3/16", "1/16"], ["码字", "0", "10", "110", "111"], ["码长", "1", "2", "3", "3"]],
    [2.6, 3.4, 3.4, 3.4, 3.4],
    size=9,
)

H2("③ 平均码长与效率")
STEP(2, "按 2 个符号一组算平均码长：")
DERIV([
    ("L̄_{2}", "=", "1×(9/16) + 2×(3/16) + 3×(3/16) + 3×(1/16)"),
    ("", "=", "9/16 + 6/16 + 9/16 + 3/16"),
    ("", "=", "27/16 = 1.6875　bit / 2 符号"),
])
STEP(3, "折算到每个信源符号：L̄ = 1.6875 / 2 = 0.84375 bit/符号。")
STEP(4, "求信源熵（L = 1 时的极限）：")
DERIV([
    ("H(X)", "=", "−(3/4)log_{2}(3/4) − (1/4)log_{2}(1/4)"),
    ("", "=", "0.3113 + 0.5"),
    ("", "=", "0.8113　bit/符号"),
])
STEP(5, "扩展信源的熵（无记忆时可加）：H(X²) = 2H(X) = 1.6226 bit。")
STEP(6, "编码效率 = 信息量 ÷ 实际传输的比特数：")
DERIV([
    ("η", "=", "H(X²) / L̄_{2}"),
    ("", "=", "1.6226 / 1.6875"),
    ("", "≈", "0.9615 = 96.15%"),
])
ANS("码字 a_{1}a_{1}→0、a_{1}a_{2}→10、a_{2}a_{1}→110、a_{2}a_{2}→111；平均码长 0.84375 bit/符号；效率 η ≈ 96.15%。")

H2("④ 为什么非要做扩展（对比一下就有说服力）")
T(
    ["方案", "平均码长 (bit/符号)", "效率"],
    [
        ["不扩展，直接霍夫曼（2 个符号）", "1.0000", "81.13%"],
        ["L = 2 扩展", "0.84375", "96.15%"],
        ["理论极限（熵）", "0.8113", "100%"],
    ],
    [8.2, 5.4, 4.0],
    size=8.8,
)
NOTE("扩展后码长更接近熵，因为「按块编码」把整块的冗余也利用上了；代价是必须缓冲两个符号再编一次，延迟和存储都变大 —— 这是所有「分组扩展」的共同代价。")
NOTE("【踩分点】4 个序列概率（3 分）→ 合并过程（3 分）→ 码字（2 分）→ 平均码长（1 分）→ 效率（1 分）。码字不唯一，0/1 互换照样给满分，只要平均码长对。")

H1("第 3 题　霍夫曼编码与编码效率")
QT("将下列消息按霍夫曼编码方法编码，并计算其编码效率：S = {a_{1},…,a_{7}}，P = (0.15, 0.19, 0.10, 0.17, 0.20, 0.18, 0.01)。")

H2("① 先排序（从小到大）")
T(
    ["符号", "a_{7}", "a_{3}", "a_{1}", "a_{4}", "a_{6}", "a_{2}", "a_{5}"],
    [["概率", "0.01", "0.10", "0.15", "0.17", "0.18", "0.19", "0.20"]],
    [2.4, 2.4, 2.4, 2.4, 2.4, 2.4, 2.4, 2.4],
    size=9,
)

H2("② 六次合并（每次挑当前最小的两个）")
T(
    ["步", "合并", "新节点概率", "节点名"],
    [
        ["①", "0.01 + 0.10", "0.11", "n_{1}"],
        ["②", "0.11 + 0.15", "0.26", "n_{2}"],
        ["③", "0.17 + 0.18", "0.35", "n_{3}"],
        ["④", "0.19 + 0.20", "0.39", "n_{4}"],
        ["⑤", "0.26 + 0.35", "0.61", "n_{5}"],
        ["⑥", "0.39 + 0.61", "1.00", "根"],
    ],
    [1.2, 6.4, 4.2, 3.0],
    size=8.8,
)
NOTE("自检：所有内部节点概率之和 = 0.11+0.26+0.35+0.39+0.61+1.00 = 2.72，它一定等于平均码长。这条恒等式可以直接当答案用，也可以用来验算。")

H2("③ 读码字（左支 0、右支 1，从根到叶）")
MONO([
    "根 1.00",
    "├─0─ n4 0.39",
    "│    ├─0─ a2 0.19  →  00",
    "│    └─1─ a5 0.20  →  01",
    "└─1─ n5 0.61",
    "     ├─0─ n2 0.26",
    "     │    ├─0─ n1 0.11",
    "     │    │    ├─0─ a7 0.01  →  1000",
    "     │    │    └─1─ a3 0.10  →  1001",
    "     │    └─1─ a1 0.15  →  101",
    "     └─1─ n3 0.35",
    "          ├─0─ a4 0.17  →  110",
    "          └─1─ a6 0.18  →  111",
], size=9)
T(
    ["符号", "a_{1}", "a_{2}", "a_{3}", "a_{4}", "a_{5}", "a_{6}", "a_{7}"],
    [
        ["概率", "0.15", "0.19", "0.10", "0.17", "0.20", "0.18", "0.01"],
        ["码字", "101", "00", "1001", "110", "01", "111", "1000"],
        ["码长", "3", "2", "4", "3", "2", "3", "4"],
    ],
    [1.9, 2.3, 2.3, 2.3, 2.3, 2.3, 2.3, 2.3],
    size=8.8,
)

H2("④ 平均码长")
DERIV([
    ("L̄", "=", "0.15×3 + 0.19×2 + 0.10×4 + 0.17×3 + 0.20×2 + 0.18×3 + 0.01×4"),
    ("", "=", "0.45 + 0.38 + 0.40 + 0.51 + 0.40 + 0.54 + 0.04"),
    ("", "=", "2.72　bit/符号"),
])
H2("⑤ 信源熵")
DERIV([
    ("H", "=", "−Σ p_{i}·log_{2}p_{i}"),
    ("", "=", "0.4105 + 0.4552 + 0.3322 + 0.4346 + 0.4644 + 0.4453 + 0.0664"),
    ("", "=", "2.6087　bit/符号"),
])
H2("⑥ 编码效率")
DERIV([
    ("η", "=", "H / L̄"),
    ("", "=", "2.6087 / 2.72"),
    ("", "≈", "0.9591 = 95.9%"),
])
ANS("平均码长 L̄ = 2.72 bit/符号，编码效率 η ≈ 95.9%。")
NOTE("【踩分点】排序+六次合并（4 分）→ 码字表（3 分）→ 平均码长（2 分）→ 效率（1 分）。合并时若把等概率的两个节点换了顺序，码字会变但码长不变，照给满分；效率只有 4.6% 的冗余，属于很理想的结果。")

H1("第 4 题　CRC 校验码")
QT("假设 m(x) = x^{6} + x^{4} + x^{3} + 1（即信息码字 1011001），g(x) = x^{4} + x^{3} + 1，求 CRC 校验码。")

H2("① 多项式 → 二进制串（逐项写系数，缺项补 0）")
T(
    ["幂次", "x^{6}", "x^{5}", "x^{4}", "x^{3}", "x^{2}", "x^{1}", "x^{0}"],
    [["m(x)", "1", "0", "1", "1", "0", "0", "1"], ["g(x)", "—", "—", "1", "1", "0", "0", "1"]],
    [2.2, 2.2, 2.2, 2.2, 2.2, 2.2, 2.2, 2.2],
    size=9,
)
STEP(0, "m(x) 最高次为 6 ⇒ 7 位信息码：**1011001**；g(x) 最高次为 4 ⇒ 5 位生成码 **11001**，校验位数 r = deg g = 4。")
NOTE("写串的口诀：从最高次往 0 次，一项一位，有就算 1，没有就写 0。x⁶+x⁴+x³+1 缺 x⁵、x²、x¹，所以是 1 0 1 1 0 0 1。")

H2("② 信息码左移 r 位（等于乘 x^{4}）")
STEP(1, "在末尾补 4 个 0（不是补到 4 位，而是补 r 个 0）：")
MONO(["1 0 1 1 0 0 1 0 0 0 0", "↑ 原信息码 1011001   ↑ 补的 4 个 0"], size=10)
NOTE("为什么补 r 个 0：这一步把「信息 × x⁴」变成多项式除法，商是码字、余数就是校验位。")

H2("③ 模 2 除法（只做异或，不借位）")
T(
    ["步", "被除数（除式）", "异或", "余式"],
    [
        ["①", "1 0 1 1 0 0 1 0 0 0 0", "1 1 0 0 1 0 0 0 0 0 0", "1 1 1 1 0 1 0 0 0 0"],
        ["②", "1 1 1 1 0 1 0 0 0 0", "1 1 0 0 1 0 0 0 0 0", "1 1 1 1 0 0 0 0"],
        ["③", "1 1 1 1 0 0 0 0", "1 1 0 0 1 0 0 0", "1 1 1 0 0 0"],
        ["④", "1 1 1 0 0 0", "1 1 0 0 1 0", "1 0 1 0"],
    ],
    [1.2, 6.2, 6.2, 4.6],
    size=8.6,
)
STEP(2, "余式为 1010，即 x^{3} + x，这就是校验码。")

H2("④ 组装与验证")
STEP(3, "把校验位接在信息位后面：")
MONO(["信息位 1 0 1 1 0 0 1   校验位 1 0 1 0", "发送码字 = 1 0 1 1 0 0 1 1 0 1 0"], size=10)
STEP(4, "验证：把余式补进末 4 位后再除一次，余数必须为 0。")
MONO(["1 0 1 1 0 0 1 0 0 0 0  ⊕  0 0 0 0 0 0 0 1 0 1 0", "= 1 0 1 1 0 0 1 1 0 1 0  ÷ 1 1 0 0 1  余式 = 0  ✓"], size=9.5)
ANS("CRC 校验码为 **1010**；完整发送码字为 **10110011010**（7 位信息 + 4 位校验）。")
NOTE("【踩分点】多项式→二进制（2 分）→ 左移 r 位（2 分）→ 模 2 除法过程（4 分，每步 1 分）→ 余式（1 分）→ 组装与验证（1 分）。常见的错：拿 x⁴ 当除数的最高位去对齐、或者中途把异或做成减法借位。")

H1("第 5 题　(7,3) 线性分组码")
QT("设某 (7,3) 线性分组码的生成矩阵 **G** 为 3×7 矩阵，三行依次为 0111101、1110000、1011010。(1) 写出由 **G** 化出的典型矩阵，并据典型矩阵写出全部码字及对应关系；(2) 计算系统码的校验矩阵 **H**_{S}，若接收码字 %%r%% = [1010111]，检验它是否为码字。")

H2("① 原生成矩阵")
MONO([
    "     ⎡ 0 1 1 1 1 0 1 ⎤",
    "G =  ⎢ 1 1 1 0 0 0 0 ⎥",
    "     ⎣ 1 0 1 1 0 1 0 ⎦",
], size=10)

H2("② 化为系统（典型）形式 [ I_{3} | P ]")
STEP(0, "目标：让前三列变成 3×3 单位阵。做法是行与行相加（模 2，等价于异或）。")
DERIV([
    ("第 1 行 ← 第 1 行 ⊕ 第 2 行", "=", "1 0 0 1 1 0 1"),
    ("第 2 行 ← 第 2 行 ⊕ 第 3 行", "=", "0 1 0 1 0 1 0"),
    ("第 3 行 ← (新第 1 行) ⊕ 第 3 行", "=", "0 0 1 0 1 1 1"),
], size=9.8, widths=(6.4, 0.9, 9.6))
NOTE("每一步都只做了「某两行相加」，属于可逆的行变换，所以行空间（也就是全体码字）没有改变。")
MONO([
    "       ⎡ 1 0 0 │ 1 1 0 1 ⎤",
    "G_S =  ⎢ 0 1 0 │ 1 0 1 0 ⎥  = [ I3 | P ]",
    "       ⎣ 0 0 1 │ 0 1 1 1 ⎦",
], size=10)
NOTE("于是 P 为 3×4 的矩阵，三行分别是 1101、1010、0111。")

H2("③ 全部 8 个码字（信息位 × 生成矩阵）")
MONO([
    "信息 m     码字 c          重量",
    "0 0 0  →  0 0 0 0 0 0 0     0",
    "0 0 1  →  0 0 1 0 1 1 1     4",
    "0 1 0  →  0 1 0 1 0 1 0     3",
    "0 1 1  →  0 1 1 1 1 0 1     5",
    "1 0 0  →  1 0 0 1 1 0 1     4",
    "1 0 1  →  1 0 1 1 0 1 0     4",
    "1 1 0  →  1 1 0 0 1 1 1     5",
    "1 1 1  →  1 1 1 0 0 0 0     3",
], size=9.5)
NOTE("最小码距 d_{min} = 3 ⇒ 可纠正 t = 1 位错误（t 取 (d_{min}−1)/2 的整数部分），可检测 2 位错误。前 3 位就是信息位，后 4 位是校验位（系统码的特征）。")

H2("④ 校验矩阵")
STEP(1, "系统码的校验矩阵按 **H**_{S} = [ P^{T} | I_{4} ] 拼出来：")
MONO([
    "       ⎡ 1 1 0 │ 1 0 0 0 ⎤",
    "H_S =  ⎢ 1 0 1 │ 0 1 0 0 ⎥",
    "       ⎢ 0 1 1 │ 0 0 1 0 ⎥",
    "       ⎣ 1 0 1 │ 0 0 0 1 ⎦",
], size=10)
STEP(2, "自检：把任一码字代进 **H**_{S}%%c%%^{T} 应得零矢量，比如 1001101 得 (0,0,0,0)^{T} ✓")

H2("⑤ 检验 %%r%% = [1010111]")
STEP(3, "算伴随式 %%s%% = **H**_{S}%%r%%^{T}（各列按 1 的个数加权求和，再模 2）：")
T(
    ["分量", "涉及的列", "求和", "模 2"],
    [
        ["s_{1}", "第 1、2、4 位（1+1+0）", "2", "0"],
        ["s_{2}", "第 1、3、5 位（1+1+1）", "3", "1"],
        ["s_{3}", "第 2、3、6 位（0+1+1）", "2", "0"],
        ["s_{4}", "第 1、3、7 位（1+1+1）", "3", "1"],
    ],
    [2.0, 8.4, 3.2, 3.0],
    size=9,
)
STEP(4, "%%s%% = (0,1,0,1)^{T} ≠ **0**，所以 %%r%% 不是码字。")
STEP(5, "继续：伴随式等于 **H**_{S} 的第 3 列，说明错误发生在第 3 位。")
DERIV([
    ("纠正后的码字", "=", "%%r%% ⊕ (0 0 1 0 0 0 0)"),
    ("", "=", "0 0 1 0 1 1 1"),
], size=9.8, widths=(6.0, 0.9, 10.0))
STEP(6, "核对：0010111 在第 ③ 步的码字表里（对应信息 001）✓ 结论自洽。")
ANS("系统生成矩阵 **G**_{S} = [100│1101; 010│1010; 001│0111]；8 个码字见上表，d_{min}=3；**H**_{S} = [P^{T}│I_{4}]；%%r%% = 1010111 不是码字（伴随式 (0,1,0,1)），错在第 3 位，正确码字为 0010111。")
NOTE("【踩分点】行变换得到 **G**_{S}（4 分）→ 8 个码字及对应（4 分）→ **H**_{S}（3 分）→ 伴随式（2 分）→ 结论与纠正（2 分，若只答「不是码字」给 1 分）。注意伴随式非零只能说明有错，要判位置必须比对 **H**_{S} 的列。")

H1("附　三张速查表")
H2("1. 霍夫曼编码步骤")
B([
    "把所有符号概率排成一列，每个当叶子；",
    "每次取最小的两个合成父节点（概率相加），父节点放回队列；",
    "重复到只剩一个根；从根往下左 0 右 1，路径即码字；",
    "平均码长 = 所有内部节点概率之和（同时也是验算公式）。",
])
H2("2. CRC 步骤")
B([
    "多项式 → 二进制（逐项写系数，缺项补 0）；",
    "确定 r = deg g，信息码左移 r 位（末尾补 r 个 0）；",
    "模 2 除法（只异或、不借位），余式即为校验码；",
    "校验位接在信息位后组成码字；再除一次应余 0。",
])
H2("3. 常用数值")
T(
    ["式", "值", "式", "值"],
    [
        ["log_{2}3", "1.585", "log_{2}6", "2.585"],
        ["log_{2}5", "2.322", "log_{2}10", "3.322"],
        ["log_{2}101", "6.658", "log_{2}1001", "9.967"],
        ["H(1/4)", "0.8113", "H(1/3)", "0.9183"],
    ],
    [4.0, 3.2, 4.0, 3.2],
    size=9,
)


doc.save(WRITE)
print("saved:", WRITE)
