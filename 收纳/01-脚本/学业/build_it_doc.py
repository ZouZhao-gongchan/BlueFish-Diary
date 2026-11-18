# -*- coding: utf-8 -*-
"""生成《信息论期中·十题详解与知识点》docx"""
import re
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

FONT_BODY = "宋体"
FONT_HEAD = "微软雅黑"
FONT_MATH = "Cambria Math"
ACCENT = "1F3864"
ACCENT_LIGHT = "D9E2F3"
BOX_FILL = "F2F5FA"
EX_FILL = "FFF4E6"
EX_LINE = "C55A11"
GREEN_FILL = "E8F3E8"
GREEN = "2E6B34"
GRAY = "595959"

WRITE = r"E:\Agent-bluefish\working\收纳\05-作业成品\信息论期中十题详解.docx"


def set_fonts(run, ascii_name, ea_name, size=None, bold=None, color=None):
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


def shade_cell(cell, fill):
    tcpr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tcpr.append(shd)


def cell_borders(cell, color="7F7F7F", sz=8):
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


def table_cell_margins(table, top=28, bottom=28, left=70, right=70):
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


TOKEN = re.compile(r"(\*\*.+?\*\*|_\{[^}]*\}|\^\{[^}]*\})")


def add_rich(p, text, font=FONT_MATH, size=10, color=None, bold=False):
    for part in TOKEN.split(text):
        if not part:
            continue
        b, sub, sup, t = bold, False, False, part
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            b, t = True, part[2:-2]
        elif part.startswith("_{") and part.endswith("}"):
            sub, t = True, part[2:-1]
        elif part.startswith("^{") and part.endswith("}"):
            sup, t = True, part[2:-1]
        r = p.add_run(t)
        set_fonts(r, font, FONT_BODY, size, b, color)
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
st.paragraph_format.line_spacing = 1.1

sec = doc.sections[0]
sec.page_width = Cm(21)
sec.page_height = Cm(29.7)
sec.top_margin = Cm(1.6)
sec.bottom_margin = Cm(1.5)
sec.left_margin = Cm(1.7)
sec.right_margin = Cm(1.7)


def P(text="", size=10, align=None, before=0, after=2, indent=0, color=None, font=FONT_MATH):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    if indent:
        pf.left_indent = Cm(indent)
    if align == "center":
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if text:
        add_rich(p, text, font=font, size=size, color=color)
    return p


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
    set_fonts(r, FONT_HEAD, FONT_HEAD, 11.5, True, "FFFFFF")


def H2(text):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(6)
    pf.space_after = Pt(2)
    pf.keep_with_next = True
    add_rich(p, "▍" + text, font=FONT_HEAD, size=10.5, color=ACCENT, bold=True)


def F(text, size=10):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(1)
    pf.space_after = Pt(2)
    pf.left_indent = Cm(0.45)
    pf.line_spacing = 1.15
    shade_paragraph(p, BOX_FILL)
    para_border(p, "left", ACCENT, 14, 4)
    add_rich(p, text, font=FONT_MATH, size=size)


def B(items, size=9.5):
    for it in items:
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.space_before = Pt(0)
        pf.space_after = Pt(1)
        pf.left_indent = Cm(0.55)
        pf.first_line_indent = Cm(-0.45)
        pf.line_spacing = 1.12
        add_rich(p, "• " + it, font=FONT_MATH, size=size)


def NOTE(text, size=8.5):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(3)
    pf.left_indent = Cm(0.1)
    add_rich(p, text, font=FONT_BODY, size=size, color=GRAY)


def QNO(no, desc, score):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(10)
    pf.space_after = Pt(2)
    pf.keep_with_next = True
    shade_paragraph(p, GREEN_FILL)
    para_border(p, "left", GREEN, 18, 4)
    add_rich(p, "  " + no + "　" + desc, font=FONT_HEAD, size=11, color=GREEN, bold=True)
    r = p.add_run("（" + score + "）")
    set_fonts(r, FONT_HEAD, FONT_HEAD, 9.5, True, EX_LINE)


def QT(text):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(1)
    pf.space_after = Pt(2)
    pf.left_indent = Cm(0.2)
    pf.line_spacing = 1.15
    add_rich(p, text, font=FONT_MATH, size=9.8)


def TAG(text):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(2)
    pf.left_indent = Cm(0.2)
    add_rich(p, "【考点】" + text, font=FONT_BODY, size=9, color=ACCENT, bold=True)


def ST(step, text, size=9.5):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(1)
    pf.left_indent = Cm(0.85)
    pf.first_line_indent = Cm(-0.4)
    pf.line_spacing = 1.15
    add_rich(p, "①②③④⑤⑥⑦⑧⑨⑩"[step] + " " + text, font=FONT_MATH, size=size)


def ANS(text):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(2)
    pf.space_after = Pt(2)
    pf.left_indent = Cm(0.85)
    pf.line_spacing = 1.15
    shade_paragraph(p, EX_FILL)
    add_rich(p, "⇒ " + text, font=FONT_MATH, size=9.5, color=EX_LINE, bold=True)


def T(header, rows, widths, size=8.8, align_left=False):
    t = doc.add_table(rows=1, cols=len(header))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    fixed_layout(t)
    table_borders(t)
    table_cell_margins(t)
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
    gap = doc.add_paragraph()
    gap.paragraph_format.space_before = Pt(0)
    gap.paragraph_format.space_after = Pt(0)
    gap.paragraph_format.line_spacing = 0.5
    r = gap.add_run("")
    set_fonts(r, FONT_BODY, FONT_BODY, 7)


def DIAGRAM():
    """用表格画通信系统框图"""
    labels_top = ["信源", "→", "信源编码", "→", "信道编码", "→", "调制器"]
    labels_bot = ["信宿", "←", "信源译码", "←", "信道译码", "←", "解调器"]
    widths = [2.6, 0.9, 2.9, 0.9, 2.9, 0.9, 2.6]
    t = doc.add_table(rows=3, cols=7)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    fixed_layout(t)
    table_borders(t, color="7F7F7F", sz=6)
    table_cell_margins(t, top=50, bottom=50)
    for i, w in enumerate(widths):
        for row in t.rows:
            row.cells[i].width = Cm(w)
    for i, txt in enumerate(labels_top):
        c = t.rows[0].cells[i]
        c.text = ""
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        if txt == "→":
            add_rich(p, "→", size=13, color=EX_LINE, bold=True)
        else:
            add_rich(p, txt, font=FONT_HEAD, size=9.5)
            shade_cell(c, ACCENT_LIGHT)
    mid = t.rows[1].cells[0]
    for i in range(1, 7):
        mid = mid.merge(t.rows[1].cells[i])
    mid.text = ""
    p = mid.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    add_rich(p, "信　道（传输媒质：自由空间 / 电缆 / 光纤，含衰减、加性噪声与干扰）", font=FONT_HEAD, size=9.5, color=GREEN, bold=True)
    shade_cell(mid, GREEN_FILL)
    for i, txt in enumerate(labels_bot):
        c = t.rows[2].cells[i]
        c.text = ""
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        if txt == "←":
            add_rich(p, "←", size=13, color=EX_LINE, bold=True)
        else:
            add_rich(p, txt, font=FONT_HEAD, size=9.5)
            shade_cell(c, ACCENT_LIGHT)
    NOTE("说明：第一行是发送端（自左向右），中间是信道（噪声源并入信道），第三行是接收端（自右向左）。实际系统还会加加密/解密、同步与射频前端。")


fp = sec.footer.paragraphs[0]
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
r1 = fp.add_run("信息论 · 期中十题详解与知识点   —   ")
set_fonts(r1, FONT_BODY, FONT_BODY, 8, False, GRAY)
r = fp.add_run()
set_fonts(r, FONT_BODY, FONT_BODY, 8, False, GRAY)
fld = OxmlElement("w:fldSimple")
fld.set(qn("w:instr"), " PAGE ")
fp._p.append(fld)

# ==================== 封面 ====================
p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(0)
p.paragraph_format.space_after = Pt(1)
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("信息论 · 期中十题详解与知识点")
set_fonts(r, FONT_HEAD, FONT_HEAD, 20, True, ACCENT)

p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(0)
p.paragraph_format.space_after = Pt(4)
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
add_rich(p, "十道大题（每题 10 分）｜逐题详解 + 考点标注 + 答案速览 + 知识点速查", font=FONT_HEAD, size=9.5, color=GRAY)

NOTE("用法：先看第一节的「答案速览」自测，再按题号读详解；每题的【考点】是这一题真正在考的东西，考场上认得出题型比算得快更重要。最后一节是公式与常用数值，考前十分钟够翻一遍。")

# ==================== 一、答案速览 ====================
H1("一、答案速览（先自测，再看详解）")
T(
    ["题", "考点", "核心结论"],
    [
        ["1", "通信系统模型", "信源→信源编码→信道编码→调制→信道→解调→信道译码→信源译码→信宿；各部分分别管有效性、可靠性、搬移与噪声"],
        ["2", "熵族关系", "H(X,Y)=H(X)+H(Y|X)=H(Y)+H(X|Y)；I(X;Y)=H(X)−H(X|Y)=H(Y)−H(Y|X)=H(X)+H(Y)−H(X,Y)"],
        ["3", "香农公式", "C = B·log₂(1+S/N)；B 与 S/N 可互换，B→∞ 时 C→1.44·S/N₀"],
        ["4", "两类编码", "信源编码求有效性（压缩），信道编码求可靠性（纠错）；由分离定理可分两级设计"],
        ["5", "联合/条件熵", "H(XY)≈2.301 bit，H(Y)=log₂3≈1.585 bit，H(X|Y)≈0.716 bit"],
        ["6", "熵的链式关系", "H(X)=H(Y)=1；H(Z)≈0.5436；H(XZ)≈1.4056；I(X;Y)≈0.1887；I(X;Z)≈0.1379 等（详见该题表）"],
        ["7", "二次扩展信源", "9 个序列，H(X)=1.5 bit，H(X²)=3 bit"],
        ["8", "二元对称信道", "I(X;Y)≈0.0615 bit；C=1−H(1/3)≈0.0817 bit，等概输入达到"],
        ["9", "一般离散信道", "H(Y)≈1.406，H(Y|X)=1.25；C≈0.161 bit，达到时 p(x₁)=0.6"],
        ["10", "对称信道容量", "C = log₂4 − H(1/3,1/6,1/3,1/6) = 2 − 1.9183 ≈ 0.0817 bit"],
    ],
    [1.0, 3.4, 13.0],
    size=8.6,
    align_left=True,
)

# ==================== 二、逐题详解 ====================
H2("题目索引（打印后按页翻）")
B([
    "第 1 题 通信系统的基本模型 · P.2　｜　第 2 题 熵族关系 · P.2",
    "第 3 题 香农公式 · P.3　｜　第 4 题 两类编码的目标与关系 · P.4",
    "第 5 题 联合熵/条件熵计算 · P.4　｜　第 6 题 熵的链式计算 · P.5",
    "第 7 题 二次扩展信源 · P.6　｜　第 8 题 二元对称信道 · P.6",
    "第 9 题 一般离散信道的容量 · P.7　｜　第 10 题 对称信道容量 · P.8",
    "知识点速查：熵族公式 / 常用容量表 / 对数值 / 易错点 · P.9",
])
H1("二、逐题详解", pb=True)

# ---------- 1 ----------
QNO("第 1 题", "无线通信系统的基本模型", "10 分")
QT("画出无线通信系统的基本模型图，简述各部分的核心功能。")
TAG("香农通信系统模型；各部件的作用与「有效性 / 可靠性」的对应关系")
H2("① 模型框图")
DIAGRAM()
H2("② 各部分核心功能")
B([
    "**信源**：产生消息（语音、图像、数据、视频），输出随机序列。它的统计特性（概率分布、相关性）决定熵率 H，是压缩的极限。",
    "**信源编码**：去除信源的冗余与相关性，用尽量少的比特表示消息 → 提高**有效性**（传输效率）。无失真时的极限是 H；有失真时按率失真函数 R(D) 取舍。",
    "**信道编码**：按规则加入**可控冗余**（校验位），使接收端能检错/纠错 → 提高**可靠性**。码率必须小于信道容量 C 才能把误码率压到任意小。",
    "**调制器**：把数字基带信号搬移到射频载波（ASK/FSK/PSK/QAM），便于天线辐射、频分复用、匹配信道带宽。",
    "**信道**：传输媒质（自由空间、同轴电缆、光纤、水声等）。它带来衰减、**加性噪声**（多为高斯白噪声）、多径衰落与人为干扰，是随机性的来源。",
    "**解调器**：从载波上把基带信号取下来并做判决（硬判决/软判决），判决本身可能出错，是误码产生的直接环节。",
    "**信道译码**：利用冗余做检错/纠错（Viterbi、LDPC、Turbo 等），输出对信息比特的估计。",
    "**信源译码**：解压缩，恢复出消息交给信宿。",
])
NOTE("拓展（可作加分点）：实际系统还在信源编码后加**加密**、在收发两端加**同步**（载波同步、位同步、帧同步）、加射频前端与天线；噪声源在模型中并入信道。")
ANS("框图 + 一句话：这个模型把通信问题抽象成「在有噪声的信道上可靠地传输信源的信息」，八个部件分别对应有效性、可靠性、频谱搬移和噪声抑制四件事。")

# ---------- 2 ----------
NOTE("【踩分点】框图 5 分（信源、信源编码、信道编码、调制、信道、解调、信道译码、信源译码、信宿，缺一项扣 0.5 分）；功能 5 分（每个部件约 0.6 分，能落到「有效性 / 可靠性 / 噪声」这层就不扣）。", size=8.5)
NOTE("【关键词】信源编码=有效性、信道编码=可靠性、调制=频谱搬移、信道=叠加噪声、整体=香农模型。", size=8.5)

QNO("第 2 题", "信源熵、联合熵、条件熵、平均互信息的关系", "10 分")
QT("简述信源熵、联合熵、条件熵、平均互信息四者之间的数学关系，并说明其物理含义。")
TAG("熵族的恒等式与不等式；维恩图理解「不确定性 → 信息量」的转化")
H2("① 四个量的定义")
F("信源熵：H(X) = −Σ_{i} p(x_{i})·log₂p(x_{i})")
F("联合熵：H(X,Y) = −Σ_{i}Σ_{j} p(x_{i},y_{j})·log₂p(x_{i},y_{j})")
F("条件熵：H(Y|X) = −Σ_{i}Σ_{j} p(x_{i},y_{j})·log₂p(y_{j}|x_{i})")
F("平均互信息：I(X;Y) = Σ_{i}Σ_{j} p(x_{i},y_{j})·log₂[p(x_{i},y_{j})/(p(x_{i})p(y_{j}))]")
H2("② 核心数学关系（必须能默写）")
F("H(X,Y) = H(X) + H(Y|X) = H(Y) + H(X|Y)　（链式法则）")
F("H(X|Y) = H(X,Y) − H(Y)，　H(Y|X) = H(X,Y) − H(X)")
F("I(X;Y) = H(X) − H(X|Y) = H(Y) − H(Y|X) = H(X) + H(Y) − H(X,Y)")
F("I(X;Y) = H(X,Y) − H(X|Y) − H(Y|X)　（维恩图中两圆的「重叠」部分）")
F("推广：H(X₁X₂…X_{n}) = Σ_{k=1}^{n} H(X_{k}|X₁…X_{k−1})")
H2("③ 重要不等式")
B([
    "H(X|Y) ≤ H(X)：**知道得越多，剩下的不确定性越小**（条件作用不会增加熵）。",
    "H(X,Y) ≤ H(X) + H(Y)：等号当且仅当 X、Y **相互独立**。",
    "I(X;Y) ≥ 0：等号当且仅当独立；且 I(X;Y) = I(Y;X)，所以叫「互」信息。",
    "I(X;Y) ≤ min{H(X), H(Y)}：你从 Y 里最多只能得到 X 的全部信息。",
])
H2("④ 物理含义（答题必须写这一层）")
B([
    "**H(X)**：不观测时 X 的平均不确定性，也就是平均信息量（「猜中 X 平均要问几个是/否问题」）。",
    "**H(X,Y)**：把 X、Y 当成一个联合事件时的总平均不确定性。",
    "**H(Y|X)**：已知发送端 X 后，接收端 Y 还剩的不确定性 —— 这是**噪声**造成的，称疑义度。",
    "**H(X|Y)**：收到 Y 后对 X 还剩的不确定性 —— 后验不确定性，反映**信道的危害程度**。",
    "**I(X;Y)**：通过 Y 平均获得多少关于 X 的信息 = 不确定性的减少量 H(X) − H(X|Y)；它衡量信道「传递信息」的能力，是信道容量的基础。",
])
ANS("四条恒等式 + 三条不等式 + 一句话：熵是不确定性，互信息是「不确定性被消掉的那部分」，链式法则把联合不确定性拆成「先知道一部分 + 剩下的条件不确定性」。")

# ---------- 3 ----------
NOTE("【踩分点】四个定义各 0.75 分；四条关系式 4 分（链式、条件熵=联合−边缘、互信息两式、链式推广）；不等式 1 分；物理含义 2 分（「后验不确定性」「信息量=不确定性的减少」各 1 分）。", size=8.5)
NOTE("【关键词】链式法则、后验不确定性、疑义度、不确定性的减少量、维恩图两圆交集。", size=8.5)

QNO("第 3 题", "香农公式的意义与参数关系", "10 分")
QT("简述香农公式的基本意义，并分析其中参数的相互影响关系。")
TAG("信道容量定理；带宽—功率—噪声三者的定量制约")
H2("① 公式")
F("C = B·log₂(1 + S/N)　（bit/s）　其中 B 为带宽(Hz)，S 为信号平均功率，N 为噪声平均功率")
F("若噪声为白噪声（单边功率谱密度 N₀），则 N = N₀B，于是 C = B·log₂(1 + S/(N₀B))")
H2("② 基本意义")
B([
    "它给出**信道无差错传输的最高信息速率**——即容量；是「存在性」结论，不告诉你具体怎么编。",
    "**只要 R < C，就存在一种编码使误码率任意小**；R > C 时不可能可靠传输（香农第二定理）。",
    "它把「带宽、信号功率、噪声功率」与「可达速率」定量绑在一起，是通信系统设计的性能天花板。",
])
H2("③ 参数之间的相互影响")
B([
    "**B 增大 → C 增大**，但并不成正比：因为 N = N₀B 也随之增大，S/N 被压低，log 项涨得越来越慢。",
    "**S/N 增大 → C 增大**，但只是**对数**增长：高信噪比区每提高 3 dB（功率翻倍），每赫兹容量约增加 1 bit/s/Hz。所以单纯加大功率的收益递减。",
    "**带宽与功率可以互换**：功率受限（卫星、深空）时用大带宽换速率；带宽受限（电缆、频谱管制）时用功率换速率（提高调制阶数）。",
    "**极限**：令 B → ∞，C → S/(N₀·ln2) ≈ 1.44·S/N₀。这说明**只用带宽不可能突破功率决定的极限**，是香农公式最有名的一条推论。",
    "**S/N → 0 时 C → 0**：信噪比为零时信道完全不传信息，与带宽多大无关。",
    "工程折中：换带宽要付「噪声变大」的代价，换功率要付「能耗与设备」的代价，实际系统在两者之间取最经济的点（如调制阶数与编码码率的联合选择）。",
])
ANS("C = B·log₂(1+S/N)：给定 B 与 S/N 的无差错速率上限；B 与 S/N 可互换，B→∞ 时 C→1.44·S/N₀，单靠带宽无法突破功率极限。")

# ---------- 4 ----------
NOTE("【踩分点】公式 3 分（B 与 S/N 的含义各 0.5）；意义 3 分（最高速率 1、存在性/可任意小 1、性能上限 1）；参数关系 4 分（B 与 S/N 各 1.5，B→∞ 极限 1）。", size=8.5)
NOTE("【关键词】无差错最高信息速率、存在性定理、对数增长、带宽与功率互换、1.44S/N₀ 极限。", size=8.5)

QNO("第 4 题", "信源编码与信道编码的目标与关系", "10 分")
QT("信道编码和信源编码的设计目标分别是什么？它们之间有怎样的关系？")
TAG("有效性 vs 可靠性；香农分离定理；率失真与信道容量")
H2("① 设计目标")
F("信源编码：**提高有效性**——去掉信源的冗余与相关性，用最少的比特/符号表示消息。无失真时平均码长逼近 H(X)；有失真时在给定失真度 D 下使码率逼近率失真函数 R(D)。依据是**信源的统计特性**。")
F("信道编码：**提高可靠性**——按规则加入受控冗余（校验位），使接收端能检错、纠错，把误码率压到允许范围。依据是**信道的特性**（差错统计规律与容量 C）。")
H2("② 两者的关系")
B([
    "**目标方向相反**：信源编码「去冗余」，信道编码「加冗余」；一个追求效率，一个追求可靠。",
    "**依据不同**：前者看信源的概率分布（H），后者看信道的转移特性（C）。",
    "**由香农定理统一**：信源编码定理给出 R > H 可无失真（或 R > R(D) 可限失真）；信道编码定理给出 R < C 可任意可靠。两条合起来说明——**先压缩到 R < C，再纠错，两级分开设计不损失渐近最优性**，这就是分离定理。",
    "**分离是有代价的**：它只保证「码长 → ∞、允许任意大延迟」时最优；实际系统受限长码、低延迟、低成本，会出现联合信源信道编码（JSCC），例如图像/视频的不等差错保护。",
    "**工程上的相互牵制**：压缩越狠，码流对差错越敏感（差错传播、雪崩效应），需要的信道保护越强；信道码率越高，留下的有效载荷越少。所以两者要按 R_s·R_c 的乘积在 C 的约束下统筹。",
])
ANS("信源编码求有效性（压缩，极限 H 或 R(D)），信道编码求可靠性（纠错，条件 R<C）；二者目标相反但由分离定理统一：先压缩再纠错可渐近达到最优。")

# ---------- 5 ----------
NOTE("【踩分点】两个目标 4 分（有效性、可靠性各 2）；依据 2 分（信源统计特性 vs 信道特性）；关系 4 分（方向相反 1、分离定理 2、代价 1）。", size=8.5)
NOTE("【关键词】去冗余 / 加冗余、有效性 / 可靠性、信源统计特性 / 信道特性、分离定理、R<C。", size=8.5)

QNO("第 5 题", "联合熵、边缘熵与条件熵", "10 分")
QT("两个实验 X 和 Y，X={x₁,x₂,x₃}，Y={y₁,y₂,y₃}，联合概率 r(x_{i},y_{j}) 为矩阵 [[7/24,1/24,0],[1/24,1/4,1/24],[0,1/24,7/24]]。求：(1) 告诉你 X 和 Y 的实验结果，你得到的平均信息量；(2) 告诉你 Y 的结果，得到的平均信息量；(3) 已知 Y 的结果时告诉你 X 的结果，得到的平均信息量。")
TAG("三问分别对应 H(XY)、H(Y)、H(X|Y)；关键是先求边缘分布")
H2("① 先求边缘分布（这是全题的钥匙）")
ST(0, "对行求和得 X 的边缘分布：第 1 行 7/24+1/24+0 = 8/24 = 1/3，第 2 行 1/24+6/24+1/24 = 8/24 = 1/3，第 3 行 0+1/24+7/24 = 8/24 = 1/3。")
ST(1, "对列求和得 Y 的边缘分布：各列同样是 8/24 = 1/3。所以 X、Y 都**等概**，且每个联合概率都是「边缘相乘 ± 一项」的形式，矩阵是对称的。")
F("P(X) = (1/3, 1/3, 1/3)，P(Y) = (1/3, 1/3, 1/3)")
H2("② (2) 告诉你 Y 的结果 → 平均信息量是 H(Y)")
F("H(Y) = −3×(1/3)·log₂(1/3) = log₂3 ≈ **1.585 bit**")
NOTE("三要素等概时，一个结果平均给出 log₂3 的信息，这正是「猜三次等可能结果需要问 1.585 个是/否问题」的意思。")
H2("③ (1) 告诉你 X 和 Y 的结果 → 平均信息量是 H(XY)")
ST(0, "矩阵里有三种非零概率：7/24（出现 2 次：(1,1)、(3,3)）、1/24（出现 4 次：(1,2)、(2,1)、(2,3)、(3,2)）、1/4（出现 1 次：(2,2)）。")
F("H(XY) = −2×(7/24)log₂(7/24) − 4×(1/24)log₂(1/24) − (1/4)log₂(1/4)")
ST(1, "逐个算：log₂(7/24) = log₂7 − log₂24 = 2.807 − 4.585 = −1.778；log₂(1/24) = −4.585；log₂(1/4) = −2。")
F("H(XY) = 2×0.2917×1.778 + 4×0.0417×4.585 + 0.25×2 = 1.037 + 0.764 + 0.500 ≈ **2.301 bit**")
H2("④ (3) 已知 Y 时告诉你 X → 平均信息量是 H(X|Y)")
F("用恒等式最快：H(X|Y) = H(XY) − H(Y) = 2.301 − 1.585 = **0.716 bit**")
ST(0, "验算（按条件熵定义）：y₁ 下 X 的条件分布为 (7/8, 1/8, 0)，其熵 0.544；y₂ 下为 (1/8, 3/4, 1/8)，其熵 1.061；y₃ 下为 (0, 1/8, 7/8)，熵 0.544。")
F("H(X|Y) = (1/3)(0.544 + 1.061 + 0.544) ≈ **0.716 bit** ✓ 与上式一致")
ANS("(1) H(XY) ≈ 2.301 bit；(2) H(Y) = log₂3 ≈ 1.585 bit；(3) H(X|Y) ≈ 0.716 bit")
NOTE("理解角度：H(XY) 是「两个结果一起告诉你」的不确定性；H(X|Y) 只剩 0.716 bit，说明 Y 已经把 X 的不确定性消掉了 1.585−0.716 ≈ 0.869 bit，这部分正是 I(X;Y)。")

# ---------- 6 ----------
NOTE("【踩分点】边缘分布 1 分；H(Y) 2 分；H(XY) 4 分（三类概率项各 1、结果 1）；H(X|Y) 3 分（恒等式 2、条件熵验算 1）。", size=8.5)
NOTE("【关键词】行列求和得边缘、H(XY) 按「相同概率归并」省时间、H(X|Y)=H(XY)−H(Y)。", size=8.5)

QNO("第 6 题", "熵、条件熵与互信息的全套计算", "10 分")
QT("二元随机变量 X、Y 的联合概率 P(0,0)=1/8，P(0,1)=3/8，P(1,0)=3/8，P(1,1)=1/8；定义 Z=XY。试计算：(1) H(X)、H(Y)、H(Z)、H(XZ)、H(YZ)、H(XYZ)；(2) 九个条件熵；(3) 六个互信息。")
TAG("同一张联合表的各种「切片」；记住 Z 是 X、Y 的函数 → H(Z|XY)=0")
H2("① 先把联合表与派生的表都列出来")
T(
    ["(X,Y)", "(0,0)", "(0,1)", "(1,0)", "(1,1)"],
    [["概率", "1/8", "3/8", "3/8", "1/8"], ["Z=XY", "0", "0", "0", "1"]],
    [2.6, 3.5, 3.5, 3.5, 3.5],
)
F("边缘：P(X=0)=P(X=1)=1/2，P(Y=0)=P(Y=1)=1/2，P(Z=1)=P(X=1,Y=1)=1/8，P(Z=0)=7/8")
F("(X,Z) 的联合：(0,0)=1/2（X=0 时 Z 恒为 0），(1,0)=3/8，(1,1)=1/8；(Y,Z) 完全同样")
H2("② (1) 六个熵")
ST(0, "H(X) = H(1/2,1/2) = **1 bit**；同理 H(Y) = **1 bit**。")
ST(1, "H(Z) = H(7/8, 1/8) = (7/8)log₂(8/7) + (1/8)log₂8 = 0.1686 + 0.375 = **0.5436 bit**。")
ST(2, "H(XZ) = −(1/2)log₂(1/2) − (3/8)log₂(3/8) − (1/8)log₂(1/8) = 0.5 + 0.5306 + 0.375 = **1.4056 bit**；由对称性 H(YZ) 相同。")
ST(3, "H(XYZ)：Z 是 (X,Y) 的函数，知道 (X,Y) 就完全知道 Z，所以 H(XYZ) = H(XY) = −2×(1/8)log₂(1/8) − 2×(3/8)log₂(3/8) = 0.75 + 1.0613 = **1.8113 bit**。")
H2("③ (2) 九个条件熵")
T(
    ["量", "算法", "值"],
    [
        ["H(X|Y)", "H(XY) − H(Y) = 1.8113 − 1", "0.8113"],
        ["H(Y|X)", "H(XY) − H(X)", "0.8113"],
        ["H(X|Z)", "H(XZ) − H(Z) = 1.4056 − 0.5436", "0.8621"],
        ["H(Z|X)", "H(XZ) − H(X) = 1.4056 − 1", "0.4056"],
        ["H(Y|Z)", "H(YZ) − H(Z)", "0.8621"],
        ["H(Z|Y)", "H(YZ) − H(Y)", "0.4056"],
        ["H(X|YZ)", "H(XYZ) − H(YZ) = 1.8113 − 1.4056", "0.4056"],
        ["H(Y|XZ)", "H(XYZ) − H(XZ)", "0.4056"],
        ["H(Z|XY)", "Z 由 X、Y 唯一确定，无残余不确定性", "0"],
    ],
    [3.2, 11.2, 2.6],
)
NOTE("H(Z|XY)=0 是「函数关系不增加不确定性」的直接体现；而 H(X|YZ) = 0.4056 < H(X|Y) = 0.8113，说明 Z 里还带着 X 的信息（Y=1 时 Z 就等于 X）。")
H2("④ (3) 六个互信息")
T(
    ["量", "算法", "值"],
    [
        ["I(X;Y)", "H(X) − H(X|Y) = 1 − 0.8113", "0.1887"],
        ["I(X;Z)", "H(X) − H(X|Z) = 1 − 0.8621", "0.1379"],
        ["I(Y;Z)", "H(Y) − H(Y|Z)", "0.1379"],
        ["I(X;YZ)", "H(X) − H(X|YZ) = 1 − 0.4056", "0.5944"],
        ["I(Y;Z|X)", "H(Z|X) − H(Z|XY) = 0.4056 − 0", "0.4056"],
        ["I(X;Z|Y)", "H(Z|Y) − H(Z|XY) = 0.4056 − 0", "0.4056"],
    ],
    [3.2, 11.2, 2.6],
)
ANS("H(X)=H(Y)=1；H(Z)≈0.5436；H(XZ)=H(YZ)≈1.4056；H(XYZ)≈1.8113；条件熵见上表；I(X;Y)≈0.1887，I(X;Z)=I(Y;Z)≈0.1379，I(X;YZ)≈0.5944，两个条件互信息均为 0.4056")
NOTE("自检：I(X;YZ) = I(X;Y) + I(X;Z|Y) = 0.1887 + 0.4056 = 0.5943 ✓。这条链式规则是这类题的「防错神器」，算完一定用它验一遍。")

# ---------- 7 ----------
NOTE("【踩分点】六个熵 4 分（每个约 0.67）；九个条件熵 3 分（每三个 1 分）；六个互信息 3 分（每个 0.5）。", size=8.5)
NOTE("【关键词】Z 是 X、Y 的函数 ⇒ H(Z|XY)=0；用 H(XYZ)=H(XY) 省一步；I(X;YZ)=I(X;Y)+I(X;Z|Y) 自检。", size=8.5)

F("【定义式示范】I(X;Y) = ΣΣ p(x,y)·log₂[p(x,y)/(p(x)p(y))]。这里 p(x)p(y) = (1/2)(1/2) = 1/4，四项分别为：")
F("(1/8)log₂[(1/8)/(1/4)] + (3/8)log₂[(3/8)/(1/4)] + (3/8)log₂[(3/8)/(1/4)] + (1/8)log₂[(1/8)/(1/4)]")
F("= 2×(1/8)×(−1) + 2×(3/8)×0.585 = −0.25 + 0.4388 = **0.1888 ≈ 0.1887** ✓ 与用熵差算的完全一致")
NOTE("其余互信息同理可算。这条路径的好处是能直接看出「互信息 = 联合分布偏离独立分布的程度」——独立时 p(x,y)=p(x)p(y)，每项为 0。", size=8.5)

QNO("第 7 题", "离散无记忆信源的二次扩展", "10 分")
QT("求离散无记忆信源 X 的二次扩展信源及其熵。X 的取值为 (a₁, a₂, a₃)，概率为 (1/2, 1/4, 1/4)。")
TAG("扩展信源 = 符号的 L 元组；无记忆时联合概率 = 各概率之积，熵按可加性 = L·H(X)")
H2("① 二次扩展信源的 9 个符号与概率")
F("无记忆 ⇒ p(a_{i}a_{j}) = p(a_{i})·p(a_{j})，共 3² = 9 个长度为 2 的符号")
T(
    ["二次扩展符号", "a₁a₁", "a₁a₂", "a₁a₃", "a₂a₁", "a₂a₂", "a₂a₃", "a₃a₁", "a₃a₂", "a₃a₃"],
    [["概率", "1/4", "1/8", "1/8", "1/8", "1/16", "1/16", "1/8", "1/16", "1/16"]],
    [2.4, 1.5, 1.5, 1.5, 1.5, 1.6, 1.6, 1.5, 1.6, 1.6],
    size=8.2,
)
NOTE("检查归一化：1/4 + 4×(1/8) + 4×(1/16) = 0.25 + 0.5 + 0.25 = 1 ✓")
H2("② 求熵")
ST(0, "先求原信源熵：H(X) = −(1/2)log₂(1/2) − 2×(1/4)log₂(1/4) = 0.5 + 1.0 = **1.5 bit/符号**。")
ST(1, "直接按 9 个概率算：")
F("H(X²) = −(1/4)log₂(1/4) − 4×(1/8)log₂(1/8) − 4×(1/16)log₂(1/16) = 0.5 + 1.5 + 1.0 = **3 bit/2符号**")
ST(2, "用可加性验算：无记忆时 H(X₁X₂) = H(X₁) + H(X₂) = 2H(X) = **3 bit** ✓")
ANS("二次扩展信源为上述 9 个符号（概率如表中）；H(X²) = 3 bit/2 符号，等价于 1.5 bit/符号")
NOTE("要点：扩展后「每符号的平均码长」会下降（更接近熵），代价是编码要缓冲 L 个符号、延迟变大 —— 这正是第 2 题霍夫曼编码要用扩展的原因。")

# ---------- 8 ----------
NOTE("【踩分点】9 个概率 4 分（错一个扣 0.5，未归一化扣 1）；H(X) 2 分；H(X²) 3 分（直接算 2 + 可加性验算 1）；单位 1 分。", size=8.5)
NOTE("【关键词】无记忆 ⇒ 联合概率相乘；扩展信源熵 = L 倍单符号熵；归一化先检查。", size=8.5)

QNO("第 8 题", "二元对称信道的互信息与容量", "10 分")
QT("二元对称信道（BSC）的转移矩阵 P = [[2/3, 1/3], [1/3, 2/3]]。(1) 若 P(0)=3/4、P(1)=1/4，求 H(X)、H(X|Y)、H(Y|X)、I(X;Y)；(2) 求信道容量及达到容量时的输入分布。")
TAG("BSC 的标准结论：H(Y|X) = H(p) 与输入无关；C = 1 − H(p)，等概输入达到")
H2("① (1) 先算四个量")
ST(0, "H(X) = −(3/4)log₂(3/4) − (1/4)log₂(1/4) = 0.3113 + 0.5 = **0.8113 bit**。")
ST(1, "H(Y|X)：BSC 的两行都是 (2/3, 1/3)，所以不论 X 取什么，Y 的条件熵都等于 H(1/3)。")
F("H(Y|X) = H(1/3) = (1/3)log₂3 + (2/3)log₂(3/2) = 0.5283 + 0.3900 = **0.9183 bit**")
ST(2, "求 Y 的分布（用全概率公式）：P(Y=0) = (3/4)(2/3) + (1/4)(1/3) = 7/12；P(Y=1) = (3/4)(1/3) + (1/4)(2/3) = 5/12。")
F("H(Y) = −(7/12)log₂(7/12) − (5/12)log₂(5/12) = 0.4536 + 0.5262 = **0.9798 bit**")
ST(3, "H(X|Y) 用联合熵过渡：H(XY) = H(X) + H(Y|X) = 0.8113 + 0.9183 = 1.7296，再减 H(Y)。")
F("H(X|Y) = H(XY) − H(Y) = 1.7296 − 0.9798 = **0.7497 bit**")
ST(4, "互信息两条路都得同一个值：")
F("I(X;Y) = H(X) − H(X|Y) = 0.8113 − 0.7497 = **0.0615 bit**；　或 I(X;Y) = H(Y) − H(Y|X) = 0.9798 − 0.9183 = 0.0615 ✓")
H2("② (2) 信道容量")
B([
    "BSC 的结论可以直接背：**C = 1 − H(p)**，p 为错误转移概率，且在**等概输入**时达到。",
    "这里 p = 1/3，所以 C = 1 − H(1/3) = 1 − 0.9183 = **0.0817 bit/符号**。",
    "达到容量的输入分布：P(X=0) = P(X=1) = **1/2**。直观理解：等概时输出也等概，H(Y) 取到最大 1，而 H(Y|X) 恒为 0.9183，两者之差最大。",
])
ANS("(1) H(X)≈0.8113，H(Y|X)≈0.9183，H(Y)≈0.9798，H(X|Y)≈0.7497，I(X;Y)≈0.0615 bit；(2) C = 1 − H(1/3) ≈ 0.0817 bit，等概输入达到")
NOTE("注意区分两个「H(1/3)」：H(Y|X) 等于它，C 等于 1 减它。p 越小容量越大；p=1/2 时 C=0（输出与输入无关）。")

# ---------- 9 ----------
NOTE("【踩分点】H(X) 1.5 分；H(Y|X) 1.5 分；H(Y) 2 分；H(X|Y) 2 分；I(X;Y) 2 分；容量 1 分（公式 0.5 + 等概输入 0.5）。", size=8.5)
NOTE("【关键词】H(Y|X)=H(p) 与输入无关、全概率公式求输出分布、I 的两条等价算法、C=1−H(p)。", size=8.5)

QNO("第 9 题", "一般离散信道的容量", "10 分")
QT("信源发送端有 2 个符号 x_{i}（i=1,2），p(x_{i})=a，每秒发出一个符号；接收端有 3 个符号 y_{j}（j=1,2,3），转移概率矩阵 P = [[1/2,1/2,0],[1/2,1/4,1/4]]。(1) 计算接收端的平均不确定度；(2) 计算由噪声产生的不确定度 H(Y|X)；(3) 计算信道容量。")
TAG("先由转移矩阵与输入分布求输出分布；容量必须对输入分布求极大（不能默认等概）")
NOTE("由 2 个符号且 p(x_{i}) = a 可知 2a = 1，故 a = 1/2，(1)(2) 按等概输入计算；(3) 的容量要对任意输入分布求极大。")
H2("① (1) 接收端平均不确定度 H(Y)")
ST(0, "先求输出分布：P(Y) = P(X)·P，即把两行按 a、1−a 加权相加。取 a = 1/2：")
F("P(Y) = (1/2)(1/2, 1/2, 0) + (1/2)(1/2, 1/4, 1/4) = (**1/2, 3/8, 1/8**)")
ST(1, "再求熵：")
F("H(Y) = −(1/2)log₂(1/2) − (3/8)log₂(3/8) − (1/8)log₂(1/8) = 0.5 + 0.5306 + 0.375 = **1.4056 bit**")
H2("② (2) 噪声产生的不确定度 H(Y|X)")
ST(0, "条件熵 = 各行熵按输入概率加权：H(Y|X) = Σ_{i} p(x_{i})·H(行 i)。")
F("H(第 1 行) = H(1/2, 1/2, 0) = 1 bit；　H(第 2 行) = H(1/2, 1/4, 1/4) = 0.5 + 1.0 = 1.5 bit")
F("H(Y|X) = (1/2)×1 + (1/2)×1.5 = **1.25 bit**")
NOTE("交互信息此刻为 I = 1.4056 − 1.25 = 0.1556 bit —— 但这**不是**容量，因为等概输入未必最优。")
H2("③ (3) 信道容量：对输入分布求极大")
ST(0, "设 P(X=0) = a、P(X=1) = 1−a，则 P(Y) = (1/2, (1+a)/4, (1−a)/4)。注意 P(Y=1) 恒为 1/2。")
ST(1, "写出依赖 a 的表达式：H(Y|X) = a·1 + (1−a)·1.5 = 1.5 − 0.5a。")
F("I(a) = H(Y) − H(Y|X) = H(1/2, (1+a)/4, (1−a)/4) − (1.5 − 0.5a)")
ST(2, "对 a 求导并令其为零（只对后两个概率求导）：")
F("dI/da = (1/4)·log₂[(1−a)/(1+a)] + 0.5 = 0　⇒　log₂[(1−a)/(1+a)] = −2　⇒　(1−a)/(1+a) = 1/4")
ST(3, "解得 4(1−a) = 1+a，即 **a = 0.6**（于是 P(X) = (0.6, 0.4)）。")
ST(4, "代回求容量：P(Y) = (0.5, 0.4, 0.1)，H(Y) = 0.5 + 0.5288 + 0.3322 = 1.3610；H(Y|X) = 1.5 − 0.3 = 1.2。")
F("C = 1.3610 − 1.2 = **0.161 bit/符号**（每秒 1 符号，故为 0.161 bit/s）")
F("注（凹性校验）：d²I/da² = (1/4)·(1/ln2)·[−1/(1−a) − 1/(1+a)]，对任意 0<a<1 恒为负，故 I(a) 是严格凹函数，驻点必是唯一的极大点。")
ST(5, "验算端点：a = 0.5 时 I ≈ 0.1556，a = 0 或 1 时 I = 0，都小于 0.161 ✓ 说明 0.6 确实是极大点。")
ANS("(1) H(Y) ≈ 1.4056 bit；(2) H(Y|X) = 1.25 bit；(3) C ≈ 0.161 bit/符号，此时 p(x₁)=0.6、p(x₂)=0.4")
NOTE("这道题的坑就在第 (3) 问：前面的 H(Y|X) 与输入无关，但 H(Y) 与输入有关，所以容量要在两条曲线之间找最大间隙，不能直接把等概时的 I 当容量。这也是「对称信道可直接用公式、非对称信道必须求极值」的分界线。")

# ---------- 10 ----------
NOTE("【踩分点】输出分布 2 分 + H(Y) 1 分 = 3；H(Y|X) 2 分；容量 5 分（设 a 1、写 I(a) 1、求导 2、驻点与结果 1）。", size=8.5)
NOTE("【关键词】转移矩阵×输入分布=输出分布、容量必须求极大、等概输入未必最优、驻点要用凹性确认。", size=8.5)

QNO("第 10 题", "对称离散信道的容量", "10 分")
QT("某对称离散信道的信道矩阵为 P = [[1/3,1/6,1/3,1/6],[1/6,1/3,1/6,1/3]]，求其信道容量。")
TAG("对称信道的容量公式 C = log₂m − H(行分布)，等概输入达到")
H2("① 先判断信道的对称性")
B([
    "行：两行都是集合 {1/3, 1/3, 1/6, 1/6} 的**排列**（第 2 行是第 1 行交换列得到的）；",
    "列：各列元素之和都是 1/3+1/6 = 1/2，**完全相同**。",
    "满足这两条 ⇒ 这是**对称离散信道**（强对称），容量公式可直接用。",
])
H2("② 套公式")
F("对称信道：C = log₂m − H(p₁, p₂, …, p_{m})，其中 m 为输出符号数，p 为任一行的概率分布；达到容量的输入是**等概**的。")
ST(0, "这里 m = 4（4 个输出），行分布为 (1/3, 1/6, 1/3, 1/6)。")
F("C = log₂4 − H(1/3, 1/6, 1/3, 1/6) = 2 − [2×(1/3)log₂3 + 2×(1/6)log₂6]")
ST(1, "逐项：2×(1/3)×1.585 = 1.0566；2×(1/6)×2.585 = 0.8617；两项之和 1.9183。")
F("C = 2 − 1.9183 = **0.0817 bit/符号**")
ST(2, "验算（等概输入时直接算）：P(Y) 各列和相等 ⇒ 等概、H(Y) = log₂4 = 2 bit；H(Y|X) = H(行) = 1.9183；I = 2 − 1.9183 = 0.0817 ✓ 与公式一致。")
H2("③ 一个漂亮的巧合（可以当理解加深）")
F("H(1/3,1/6,1/3,1/6) = 1 + H(1/3)，所以 C = 1 − H(1/3) ≈ 0.0817 —— 与第 8 题 BSC(p=1/3) 的容量完全相同。这不是巧合：两个信道在「抵消一半」的意义上等价，都可看成「以概率 1/3 出错」。")
ANS("C = log₂4 − H(1/3,1/6,1/3,1/6) = 2 − 1.9183 ≈ 0.0817 bit/符号，等概输入时达到")
NOTE("判断口诀：行是同一集合的排列、列和相等 → 对称信道 → 不用求极大，直接 log₂m − H(行)。若只有行对称、列和不等，则叫「准对称信道」，要分组用公式；两条都不满足，就只能解方程求极值（如第 9 题）。")

# ==================== 三、知识点速查 ====================
NOTE("【踩分点】判对称 2 分（行是排列 + 列和相等各 1）；公式 3 分；代入 3 分；结果 2 分。", size=8.5)
NOTE("【关键词】行是同一集合的排列、各列和相等 ⇒ 对称信道、C=log₂m−H(行分布)、等概输入达到。", size=8.5)

H1("三、知识点速查（考前十分钟看这页）", pb=True)
H2("1. 熵族公式")
F("H(X) = −Σp(x)log₂p(x)；　H(X|Y) = −ΣΣp(x,y)log₂p(y|x)")
F("H(X,Y) = H(X) + H(Y|X) = H(Y) + H(X|Y)；　H(X,Y) ≤ H(X) + H(Y)（独立取等号）")
F("I(X;Y) = H(X) − H(X|Y) = H(Y) − H(Y|X) = H(X) + H(Y) − H(X,Y) ≥ 0")
F("I(X;Y) = I(Y;X)；　H(Z|XY) = 0（Z 是 X、Y 的函数时）；　I(X;YZ) = I(X;Y) + I(X;Z|Y)")
F("扩展信源（无记忆）：H(X^{L}) = L·H(X)；平均每符号码长 L̄/L")
H2("2. 常用信道的容量")
T(
    ["信道", "容量公式", "达到容量的输入"],
    [
        ["无噪（行置换）", "C = log₂m", "等概"],
        ["二元对称 BSC(p)", "C = 1 − H(p)", "P(X)=1/2"],
        ["二元删除 BEC(ε)", "C = 1 − ε", "等概"],
        ["对称离散信道", "C = log₂m − H(行分布)", "等概"],
        ["一般离散信道", "C = max I(X;Y)（解方程/求导）", "按最大化条件求"],
    ],
    [4.2, 8.2, 4.6],
    size=8.6,
)
H2("3. 常用对数值（节省时间）")
T(
    ["式", "值", "式", "值"],
    [
        ["log₂3", "1.585", "log₂6", "2.585"],
        ["log₂5", "2.322", "log₂7", "2.807"],
        ["log₂10", "3.322", "log₂ 12", "3.585"],
        ["H(1/2)", "1", "H(1/4)", "0.8113"],
        ["H(1/3)", "0.9183", "H(1/8)", "0.5436"],
        ["H(1/8,7/8)", "0.5436", "H(3/4)", "0.8113"],
    ],
    [3.6, 3.0, 3.6, 3.0],
    size=8.6,
)
H2("4. 三个定理记一句话")
B([
    "**信源编码定理**：无失真时，平均码长可以任意接近但不会小于 H(X)；R > H 才可能无失真。",
    "**信道编码定理**：R < C 时存在编码使误码率任意小；R > C 时不可能可靠传输（逆定理）。",
    "**率失真定理**：允许失真 D 时，R > R(D) 即可用码率 R 恢复信源，R(D) 是理论上限。",
])
H2("5. 十道题里最容易丢分的五个点")
B([
    "求熵前**先查归一化**（Q7 的 9 个概率加起来必须等于 1），否则后面全错。",
    "条件熵先算**联合熵减边缘熵**，比直接代定义式快且不容易错；再用定义式抽一列验算。",
    "Q9 这种非对称信道，**容量 ≠ 等概时的互信息**，必须求极值；对称信道才可以直接套 log₂m − H(行)。",
    "BSC 里 H(Y|X) = H(p) **与输入分布无关**，这是能一步写出来的送分点。",
    "所有「互信息」都要满足 0 ≤ I ≤ min{H(X),H(Y)}，算出负数或超界立刻回头检查。",
])

p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(8)
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
add_rich(p, "所有数值均已复算（保留 4 位小数）；H 的单位为 bit，容量的单位为 bit/符号", font=FONT_BODY, size=8, color=GRAY)

doc.save(WRITE)
print("saved:", WRITE)
