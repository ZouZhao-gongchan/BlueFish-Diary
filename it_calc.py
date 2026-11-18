import math
def H(ps):
    return sum(-p*math.log2(p) for p in ps if p>0)
def h(p): return H([p,1-p])

print("== Q5 ==")
P=[[7/24,1/24,0],[1/24,1/4,1/24],[0,1/24,7/24]]
px=[sum(r) for r in P]; py=[sum(P[i][j] for i in range(3)) for j in range(3)]
print("px",px,"py",py)
HXY=H([p for r in P for p in r]); print("H(XY)=%.4f"%HXY)
print("H(X)=%.4f H(Y)=%.4f"%(H(px),H(py)))
print("H(X|Y)=%.4f"%(HXY-H(py)))
# direct conditional
hcond=0
for j in range(3):
    q=[P[i][j]/py[j] for i in range(3)]
    print("  y%d cond"%j,[round(x,4) for x in q],"H=%.4f"%H(q))
    hcond+=py[j]*H(q)
print("check H(X|Y)=%.4f"%hcond)

print("== Q6 ==")
J={ (0,0):1/8,(0,1):3/8,(1,0):3/8,(1,1):1/8 }
HX=H([1/2,1/2]); HY=H([1/2,1/2])
Hz=H([7/8,1/8])
HXY=H(list(J.values()))
# (X,Z)
from collections import defaultdict
xz=defaultdict(float); yz=defaultdict(float); xyz=defaultdict(float)
for (x,y),p in J.items():
    z=x*y; xz[(x,z)]+=p; yz[(y,z)]+=p; xyz[(x,y,z)]+=p
HXZ=H(list(xz.values())); HYZ=H(list(yz.values())); HXYZ=H(list(xyz.values()))
print("H(X)=%.4f H(Y)=%.4f H(Z)=%.4f"%(HX,HY,Hz))
print("H(XZ)=%.4f H(YZ)=%.4f H(XYZ)=%.4f H(XY)=%.4f"%(HXZ,HYZ,HXYZ,HXY))
print("pairs XZ:",{k:round(v,4) for k,v in xz.items()})
print("H(X|Y)=%.4f H(Y|X)=%.4f"%(HXY-HY,HXY-HX))
print("H(X|Z)=%.4f H(Z|X)=%.4f"%(HXZ-Hz,HXZ-HX))
print("H(Y|Z)=%.4f H(Z|Y)=%.4f"%(HYZ-Hz,HYZ-HY))
print("H(X|YZ)=%.4f H(Y|XZ)=%.4f H(Z|XY)=%.4f"%(HXYZ-HYZ,HXYZ-HXZ,HXYZ-HXY))
print("I(X;Y)=%.4f I(X;Z)=%.4f I(Y;Z)=%.4f I(X;YZ)=%.4f I(Y;Z|X)=%.4f I(X;Z|Y)=%.4f"%(
 HX-(HXY-HY), HX-(HXZ-Hz), HY-(HYZ-Hz), HX-(HXYZ-HYZ), Hz-HXY, Hz-HXY))

print("== Q7 ==")
p=[1/2,1/4,1/4]
HX7=H(p); print("H(X)=%.4f  H(X^2)=%.4f"%(HX7,2*HX7))

print("== Q8 ==")
P8=[[2/3,1/3],[1/3,2/3]]
px8=[3/4,1/4]
py8=[sum(px8[i]*P8[i][j] for i in range(2)) for j in range(2)]
print("py",py8)
HX8=H(px8); HY8=H(py8); HYgX=H(P8[0]); HXY8=HX8+HYgX
print("H(X)=%.4f H(Y)=%.4f H(Y|X)=%.4f H(X|Y)=%.4f I=%.4f"%(HX8,HY8,HYgX,HXY8-HY8,HX8-(HXY8-HY8)))
print("C(BSC)=1-H(1/3)=%.4f"%h(1/3))

print("== Q9 ==")
P9=[[1/2,1/2,0],[1/2,1/4,1/4]]
for a in [0.5]:
    py=[a*P9[0][j]+(1-a)*P9[1][j] for j in range(3)]
    HY=H(py); HYgX=a*H(P9[0])+(1-a)*H(P9[1])
    print("a=%.1f py=%s H(Y)=%.4f H(Y|X)=%.4f I=%.4f"%(a,[round(x,4) for x in py],HY,HYgX,HY-HYgX))
best=(0,None)
for k in range(1,1000):
    a=k/1000
    py=[a*P9[0][j]+(1-a)*P9[1][j] for j in range(3)]
    I=H(py)-(a*H(P9[0])+(1-a)*H(P9[1]))
    if I>best[0]: best=(I,a)
print("max I=%.5f at a=%.3f"%best)
a=0.6; py=[a*P9[0][j]+(1-a)*P9[1][j] for j in range(3)]
print("a=0.6 py=%s H(Y)=%.4f H(Y|X)=%.4f C=%.4f"%([round(x,3) for x in py],H(py),a*1+(1-a)*1.5,H(py)-(a*1+(1-a)*1.5)))

print("== Q10 ==")
row=[1/3,1/6,1/3,1/6]
print("C=log2(4)-H(row)=%.4f"%(2-H(row)))
