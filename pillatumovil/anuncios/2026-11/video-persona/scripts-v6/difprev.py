import subprocess, numpy as np, sys, json
F = sys.argv[1]; P = sys.argv[2]; LM = np.load(sys.argv[3])['lm']
W, H = 1080, 1920
def lector(f): return subprocess.Popen(['ffmpeg','-v','error','-threads','2','-i',f,'-vf','format=gray','-f','rawvideo','-'],stdout=subprocess.PIPE)
a, b = lector(F), lector(P); res = []
for n in range(766):
    x = np.frombuffer(a.stdout.read(W*H),np.uint8).reshape(H,W).astype(np.int16); y = np.frombuffer(b.stdout.read(W*H),np.uint8).reshape(H,W).astype(np.int16)
    d = np.abs(x-y); l = LM[n] if n < len(LM) else np.full((68,2),np.nan)
    if not np.isnan(l).any():
        x0,y0 = l.min(0).astype(int); x1,y1 = l.max(0).astype(int); cara = float(d[max(0,y0-20):y1+20, max(0,x0-20):x1+20].mean())
    else: cara = None
    ys = np.where(d.max(1) > 40)[0]
    res.append((n, float(d.mean()), cara, int(ys.min()) if len(ys) else -1, int(ys.max()) if len(ys) else -1))
json.dump(res, open(sys.argv[4],'w'))
def tramo(a0,a1):
    r=res[a0:a1]; m=[x[1] for x in r]; c=[x[2] for x in r if x[2] is not None]
    return f'{a0}-{a1-1}: dif media {np.mean(m):.2f} (max {np.max(m):.2f}); cara {np.mean(c) if c else float("nan"):.2f} (max {np.max(c) if c else float("nan"):.2f}); filas con cambios >40: y {min([x[3] for x in r if x[3]>=0], default=-1)}-{max([x[4] for x in r], default=-1)}'
for t in [(0,56),(56,117),(117,165),(165,298),(298,358),(358,432),(432,504),(504,584),(584,649),(649,681),(681,766)]: print(tramo(*t))
