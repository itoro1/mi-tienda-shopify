"""Luz por fotograma (respecto al fotograma 0): cartón de la cara de cada caja vieja (zona fija de la cara,
llevada con su afín) y mostrador de delante de las cajas. Suavizado (sigma 2 fotogramas). -> gan{plano}.json"""
import sys, json, numpy as np, cv2
sys.path.insert(0, '.')
import cajas_reales as cr
plano = sys.argv[1]
geo = json.load(open(f'geo{plano}.json')); seg = json.load(open(f'{cr.MOST}/seg{plano}.json')); n = seg['n']
A = cr.afines(seg, geo, n)
med_c = [[] for _ in geo]; med_f = []
for t, (Y, U, V) in enumerate(cr.lector(f'{cr.MOST}/{plano}.mp4')):
    if t >= n: break
    for k, b in enumerate(geo):
        # cuadradito de cartón liso abajo a la izquierda y a la derecha de la cara (sin dibujo)
        vals = []
        for (px, py) in [(b['x0'] + 25, b['ybot'] - 45), (b['x1'] - 25, b['ybot'] - 45), (b['x0'] + 25, b['hombro'] + 140)]:
            q = A[t, k] @ [px, py, 1]; x, y = int(q[0]), int(q[1])
            if 12 <= x < cr.W - 12 and 12 <= y < cr.H - 12:
                yy = Y[y - 8:y + 8, x - 8:x + 8].astype(np.float32); uu = U[y // 2 - 4:y // 2 + 4, x // 2 - 4:x // 2 + 4].astype(np.float32); vv = V[y // 2 - 4:y // 2 + 4, x // 2 - 4:x // 2 + 4].astype(np.float32)
                vals.append(cr.yuv2rgb(yy[::2, ::2], uu, vv).reshape(-1, 3).mean(0))
        med_c[k].append(np.mean(vals, 0) if vals else [np.nan] * 3)
    vals = []
    for k, b in enumerate(geo):
        q = A[t, k] @ [(b['x0'] + b['x1']) / 2, b['ybot'] + 70, 1]; x, y = int(q[0]), int(q[1])
        if 30 <= x < cr.W - 30 and 30 <= y < cr.H - 30:
            yy = Y[y - 20:y + 20, x - 30:x + 30].astype(np.float32); uu = U[y // 2 - 10:y // 2 + 10, x // 2 - 15:x // 2 + 15].astype(np.float32); vv = V[y // 2 - 10:y // 2 + 10, x // 2 - 15:x // 2 + 15].astype(np.float32)
            vals.append(cr.yuv2rgb(yy[::2, ::2], uu, vv).reshape(-1, 3).mean(0))
    med_f.append(np.mean(vals, 0) if vals else [np.nan] * 3)
def suaviza(a):
    a = np.array(a, np.float64)
    for c in range(3):
        x = a[:, c]; ok = ~np.isnan(x)
        x[~ok] = np.interp(np.where(~ok)[0], np.where(ok)[0], x[ok]) if ok.any() else 1
        k1 = np.exp(-0.5 * (np.arange(-6, 7) / 2.0) ** 2); k1 /= k1.sum()
        a[:, c] = np.convolve(np.pad(x, 6, mode='edge'), k1, 'same')[6:-6]
    return a / a[0]
gc = [suaviza(m) for m in med_c]; gf = suaviza(med_f)
for k in range(len(geo)):
    print('caja', k, 'gan min/max', np.round(gc[k].min(0), 3), np.round(gc[k].max(0), 3))
print('franja gan min/max', np.round(gf.min(0), 3), np.round(gf.max(0), 3))
json.dump({'caja': [g.tolist() for g in gc], 'franja': gf.tolist()}, open(f'gan{plano}.json', 'w'))
