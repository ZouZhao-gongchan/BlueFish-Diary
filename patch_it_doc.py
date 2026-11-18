# -*- coding: utf-8 -*-
"""给 build_it_doc.py 打补丁：每题加踩分点/关键词；Q6 加定义式示范；Q9 加凹性校验"""
import io, re, sys

P = r"E:\Agent-bluefish\working\build_it_doc.py"
src = io.open(P, encoding="utf-8").read()

def ins_before(anchor, block, count=1):
    global src
    if anchor not in src:
        print("!! anchor missing:", anchor[:30])
        return
    src = src.replace(anchor, block + anchor, count)

def build_block(score_text, key_text):
    return ('NOTE("【踩分点】' + score_text + '", size=8.5)\n'
            'NOTE("【关键词】' + key_text + '", size=8.5)\n\n')

# ---- 各题的踩分点 / 关键词 ----
ins_before('QNO("第 2 题"', build_block(
    "框图 5 分（信源、信源编码、信道编码、调制、信道、解调、信道译码、信源译码、信宿，缺一项扣 0.5 分）；功能 5 分（每个部件约 0.6 分，能落到「有效性 / 可靠性 / 噪声」这层就不扣）。",
    "信源编码=有效性、信道编码=可靠性、调制=频谱搬移、信道=叠加噪声、整体=香农模型。"))

ins_before('QNO("第 3 题"', build_block(
    "四个定义各 0.75 分；四条关系式 4 分（链式、条件熵=联合−边缘、互信息两式、链式推广）；不等式 1 分；物理含义 2 分（「后验不确定性」「信息量=不确定性的减少」各 1 分）。",
    "链式法则、后验不确定性、疑义度、不确定性的减少量、维恩图两圆交集。"))

ins_before('QNO("第 4 题"', build_block(
    "公式 3 分（B 与 S/N 的含义各 0.5）；意义 3 分（最高速率 1、存在性/可任意小 1、性能上限 1）；参数关系 4 分（B 与 S/N 各 1.5，B→∞ 极限 1）。",
    "无差错最高信息速率、存在性定理、对数增长、带宽与功率互换、1.44S/N₀ 极限。"))

ins_before('QNO("第 5 题"', build_block(
    "两个目标 4 分（有效性、可靠性各 2）；依据 2 分（信源统计特性 vs 信道特性）；关系 4 分（方向相反 1、分离定理 2、代价 1）。",
    "去冗余 / 加冗余、有效性 / 可靠性、信源统计特性 / 信道特性、分离定理、R<C。"))

ins_before('QNO("第 6 题"', build_block(
    "边缘分布 1 分；H(Y) 2 分；H(XY) 4 分（三类概率项各 1、结果 1）；H(X|Y) 3 分（恒等式 2、条件熵验算 1）。",
    "行列求和得边缘、H(XY) 按「相同概率归并」省时间、H(X|Y)=H(XY)−H(Y)。"))

ins_before('QNO("第 7 题"', build_block(
    "六个熵 4 分（每个约 0.67）；九个条件熵 3 分（每三个 1 分）；六个互信息 3 分（每个 0.5）。",
    "Z 是 X、Y 的函数 ⇒ H(Z|XY)=0；用 H(XYZ)=H(XY) 省一步；I(X;YZ)=I(X;Y)+I(X;Z|Y) 自检。"))

ins_before('QNO("第 8 题"', build_block(
    "9 个概率 4 分（错一个扣 0.5，未归一化扣 1）；H(X) 2 分；H(X²) 3 分（直接算 2 + 可加性验算 1）；单位 1 分。",
    "无记忆 ⇒ 联合概率相乘；扩展信源熵 = L 倍单符号熵；归一化先检查。"))

ins_before('QNO("第 9 题"', build_block(
    "H(X) 1.5 分；H(Y|X) 1.5 分；H(Y) 2 分；H(X|Y) 2 分；I(X;Y) 2 分；容量 1 分（公式 0.5 + 等概输入 0.5）。",
    "H(Y|X)=H(p) 与输入无关、全概率公式求输出分布、I 的两条等价算法、C=1−H(p)。"))

ins_before('QNO("第 10 题"', build_block(
    "输出分布 2 分 + H(Y) 1 分 = 3；H(Y|X) 2 分；容量 5 分（设 a 1、写 I(a) 1、求导 2、驻点与结果 1）。",
    "转移矩阵×输入分布=输出分布、容量必须求极大、等概输入未必最优、驻点要用凹性确认。"))

ins_before('H1("三、知识点速查（考前十分钟看这页）", pb=True)', build_block(
    "判对称 2 分（行是排列 + 列和相等各 1）；公式 3 分；代入 3 分；结果 2 分。",
    "行是同一集合的排列、各列和相等 ⇒ 对称信道、C=log₂m−H(行分布)、等概输入达到。"))

# ---- Q6 定义式示范：插在「自检」那段之后、第 7 题之前 ----
q6_demo = (
    'F("【定义式示范】I(X;Y) = ΣΣ p(x,y)·log₂[p(x,y)/(p(x)p(y))]。这里 p(x)p(y) = (1/2)(1/2) = 1/4，四项分别为：")'
    '\n'
    'F("(1/8)log₂[(1/8)/(1/4)] + (3/8)log₂[(3/8)/(1/4)] + (3/8)log₂[(3/8)/(1/4)] + (1/8)log₂[(1/8)/(1/4)]")'
    '\n'
    'F("= 2×(1/8)×(−1) + 2×(3/8)×0.585 = −0.25 + 0.4388 = **0.1888 ≈ 0.1887** ✓ 与用熵差算的完全一致")'
    '\n'
    'NOTE("其余互信息同理可算。这条路径的好处是能直接看出「互信息 = 联合分布偏离独立分布的程度」——独立时 p(x,y)=p(x)p(y)，每项为 0。", size=8.5)'
    '\n\n'
)
ins_before('QNO("第 7 题"', q6_demo)

# ---- Q9 凹性校验：插在「验算端点」那一步之前 ----
q9_concave = (
    'F("注（凹性校验）：d²I/da² = (1/4)·(1/ln2)·[−1/(1−a) − 1/(1+a)]，对任意 0<a<1 恒为负，故 I(a) 是严格凹函数，驻点必是唯一的极大点。")'
    '\n'
)
ins_before('ST(5, "验算端点', q9_concave)

io.open(P, "w", encoding="utf-8").write(src)
print("patched, new size:", len(src))
print("踩分点 count:", src.count("【踩分点】"), " 关键词 count:", src.count("【关键词】"))
