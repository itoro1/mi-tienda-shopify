"""Estabilidad en el tiempo: cada fotograma se lleva a las coordenadas de la caja en el fotograma 0 (afín de la
caja) y se mide, por zonas, cuánto cambia de un fotograma al siguiente (media de |dif| en luma, después de quitar
el cambio medio de brillo). Zonas por caja: cara nueva, franja de mostrador nueva, pestaña nueva.
Se compara el vídeo nuevo con el de antes (mismas zonas, que allí son caja vieja / mostrador)."""
import sys, json, numpy as np, cv2
sys.path.insert(0, '.')
import cajas_reales as cr
plano, vid = sys.argv[1], sys.argv[2]
geo = json.load(open(f'geo{plano}.json')); seg = json.load(open(f'{cr.MOST}/seg{plano}.json')); n = seg['n']
A = cr.afines(seg, geo, n)
# zonas en ref (rectángulos): cara (parte central de la cara nueva), franja (base nueva+8 .. base vieja), pestaña
zonas = []
for b in geo:
    t = b['tipo']; Wd = b['x1'] - b['x0']; ht = cr.PEST[t][1] * Wd
    lid = (20.0 if plano == '1' else 18.0) * (cr.FONDO[t] / (33 / 79)) * 0.9
    yft = b['tab_top'] + ht + lid; yb = yft + Wd / cr.PROP[t]
    zonas.append({'cara': (b['x0'] + 20, yft + 20, b['x1'] - 20, yb - 20), 'franja': (b['x0'] + 10, yb + 6, b['x1'] - 10, b['ybot'] + 30),
                  'pestana': (b['tab_x0'] + 30, b['tab_top'] + 6, b['tab_x1'] - 30, b['tab_top'] + ht - 4)})
prev = None; acc = {}
for t_, (Y, U, V) in enumerate(cr.lector(vid)):
    if t_ >= n: break
    cur = {}
    for k, z in enumerate(zonas):
        for nom, (x0, y0, x1, y1) in z.items():
            Mi = A[t_, k]
            # muestreo: rejilla ref -> fotograma
            gx, gy = np.meshgrid(np.arange(x0, x1, 2.0), np.arange(y0, y1, 2.0))
            fx = (Mi[0, 0] * gx + Mi[0, 1] * gy + Mi[0, 2]).astype(np.float32); fy = (Mi[1, 0] * gx + Mi[1, 1] * gy + Mi[1, 2]).astype(np.float32)
            ok = (fx > 2) & (fx < cr.W - 3) & (fy > 2) & (fy < cr.H - 3)
            v = cv2.remap(Y, fx, fy, cv2.INTER_LINEAR).astype(np.float32)
            cur[(k, nom)] = (v, ok)
    if prev is not None:
        for key, (v, ok) in cur.items():
            pv, pok = prev[key]; m = ok & pok
            if m.sum() < 100: continue
            d = (v - pv)[m]; d = d - d.mean()
            acc.setdefault(key, []).append(np.abs(d).mean())
    prev = cur
res = {f'{k}_{nom}': [round(float(np.mean(v)), 3), round(float(np.percentile(v, 95)), 3), round(float(np.max(v)), 3)] for (k, nom), v in acc.items()}
print(json.dumps(res))
