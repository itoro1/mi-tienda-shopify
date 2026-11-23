"""Afina x0/x1 de la cara de cada caja vieja: cruce a media altura entre el blanco de la caja y el fondo, por filas."""
import sys, json, numpy as np, cv2
img = cv2.imread(sys.argv[1]).astype(np.float32); g = json.load(open(sys.argv[2]))
L = img.mean(2)
fijo = {0: 'x1', 3: 'x0'}          # lado que da al centro en las cajas de los extremos: se mantiene (va con la cara de lado)
for b in g:
    rows = range(int(b['hombro']) + 60, int(b['ybot']) - 60, 4)
    for lado in ('x0', 'x1'):
        if fijo.get(b['i']) == lado: continue
        xs = []
        s = -1 if lado == 'x0' else 1
        for r in rows:
            xin = int(b[lado]) - s * 10
            wv = np.median(L[r - 1:r + 2, xin - 3:xin + 4])
            prof = L[r - 1:r + 2].mean(0)
            xo = int(b[lado]) + s * 16; bg = np.median(L[r - 1:r + 2, min(xo, xo + s * 6):max(xo, xo + s * 6)])
            if wv - bg < 40: continue
            thr = (wv + bg) / 2
            x = xin
            while abs(x - xin) < 30 and prof[x] > thr: x += s
            # subpíxel
            xa, xb = x - s, x; fa, fb = prof[xa] - thr, prof[xb] - thr
            xs.append(xa + s * fa / (fa - fb) if fa != fb else xa)
        if xs:
            nuevo = float(np.median(xs)) + (0.5 if s > 0 else -0.5) * 0
            print(b['i'], lado, b[lado], '->', round(nuevo, 1), 'n', len(xs), 'iqr', round(np.percentile(xs, 75) - np.percentile(xs, 25), 2))
            b[lado + '_seg'] = b[lado]; b[lado] = round(nuevo, 2)
    b['W'] = b['x1'] - b['x0']
json.dump(g, open(sys.argv[2], 'w'), indent=1)
