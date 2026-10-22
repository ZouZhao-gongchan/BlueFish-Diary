import numpy as np, soundfile as sf
y, sr = sf.read(r"E:\Agent-bluefish\working\_scratch\voice-ref\ref_bigfatfish.wav")
y = y.astype(np.float32)
# crude f0 track via autocorrelation on 40ms frames
frame, hop = int(0.04*sr), int(0.02*sr)
f0s = []
for i in range(0, len(y)-frame, hop):
    f = y[i:i+frame]
    if np.sqrt((f**2).mean()) < 0.02: continue
    f = f - f.mean()
    ac = np.correlate(f, f, 'full')[frame-1:]
    lo, hi = int(sr/500), int(sr/80)
    seg = ac[lo:hi]
    if len(seg)==0: continue
    lag = lo + int(np.argmax(seg))
    f0s.append(sr/lag)
f0s = np.array(f0s)
print("frames", len(f0s), "f0 median %.0f Hz  p10 %.0f p90 %.0f" % (np.median(f0s), np.percentile(f0s,10), np.percentile(f0s,90)))
print("=> approx note", 12*np.log2(np.median(f0s)/440)+69 if len(f0s) else None)
