import subprocess, sys, json, pathlib, urllib.request
import imageio_ffmpeg
out = pathlib.Path(r"E:\Agent-bluefish\working\_scratch\voice-ref"); out.mkdir(parents=True, exist_ok=True)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": "https://www.bilibili.com/"})
    return urllib.request.urlopen(req, timeout=30).read()
api = "https://api.bilibili.com/x/player/playurl?bvid=BV1PPYM6EEUR&cid=41753972459&qn=16&fnval=16&fourk=0"
d = json.loads(get(api))["data"]["dash"]["audio"]
pick = sorted(d, key=lambda x: x["id"])[0]  # lowest bitrate, smallest
print("picked audio id", pick["id"])
m4s = out / "raw.m4s"; m4s.write_bytes(get(pick["baseUrl"]))
print("m4s bytes", m4s.stat().st_size)
ff = imageio_ffmpeg.get_ffmpeg_exe()
wav = out / "ref_bigfatfish.wav"
subprocess.run([ff,"-y","-i",str(m4s),"-ac","1","-ar","44100","-c:a","pcm_s16le",str(wav)], check=True, capture_output=True)
import soundfile as sf, numpy as np
y, sr = sf.read(str(wav))
print("wav dur %.2fs sr %d peak %.3f rms %.4f" % (len(y)/sr, sr, abs(y).max(), float(np.sqrt((y.astype(float)**2).mean()))))
