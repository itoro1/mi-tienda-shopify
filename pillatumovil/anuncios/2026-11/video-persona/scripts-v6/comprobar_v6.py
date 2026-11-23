"""Comprueba en CADA fotograma (hasta el fundido del cierre) dónde caen los rótulos del vídeo v6:
   caja de los píxeles que cambian respecto al máster limpio (zona segura x 90-990, y 300-1240 en 1080x1920),
   y si tocan la cara (casco de los 68 puntos + frente), la boca, las cajas que ella tiene en la mano o sus manos (23/11:
   en todos los fotogramas; en los planos de Intone, la piel que queda delante de la camiseta).
   python3 comprobar_v6.py VIDEO_CON_TEXTOS MAESTRO_LIMPIO caras.npz NFIN [informe.json]"""
import os, subprocess, sys, json, numpy as np, cv2
V, M, CAR, NFIN = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
OUT = sys.argv[5] if len(sys.argv) > 5 else None
W, H = 1080, 1920; LM = np.load(CAR)['lm']

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from caras import ses
TPL = np.array([[0.37691676, 0.46864664], [0.62285697, 0.46912813], [0.50123859, 0.61331904], [0.39308822, 0.72541100], [0.61150205, 0.72490465]], np.float32)
def cara_bisenet(rgb, l):
    """Máscaras (cara = piel de la cara, cejas, ojos, nariz, boca y labios; boca = boca y labios ensanchada 12 px)
       con bisenet sobre el recorte alineado (escala 0,8: entra la barbilla entera), devueltas al fotograma."""
    p5 = np.array([l[36:42].mean(0), l[42:48].mean(0), l[30], l[48], l[54]], np.float32)
    t = (TPL - 0.5) * 0.8 + 0.5
    Mx, _ = cv2.estimateAffinePartial2D(p5, t * 512, method=cv2.LMEDS)
    cr = cv2.warpAffine(rgb, Mx, (512, 512), flags=cv2.INTER_AREA, borderMode=cv2.BORDER_REPLICATE).astype(np.float32) / 255
    x = (cr - np.array([0.485, 0.456, 0.406], np.float32)) / np.array([0.229, 0.224, 0.225], np.float32)
    o = ses('bisenet_resnet_34').run(None, {'input': x.transpose(2, 0, 1)[None].copy()})[0][0].argmax(0)
    cara = np.isin(o, [1, 2, 3, 4, 5, 10, 11, 12, 13]).astype(np.uint8); boca = np.isin(o, [11, 12, 13]).astype(np.uint8)
    Mi = cv2.invertAffineTransform(Mx)
    mc = cv2.warpAffine(cara, Mi, (W, H), flags=cv2.INTER_NEAREST); mb = cv2.warpAffine(boca, Mi, (W, H), flags=cv2.INTER_NEAREST)
    return mc, cv2.dilate(mb, np.ones((25, 25), np.uint8))
def lector(f):
    return subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-threads', '2', '-i', f, '-vf',
        f'scale={W}:{H}:flags=area:in_color_matrix=bt709:in_range=tv,format=rgb24', '-f', 'rawvideo', '-'], stdout=subprocess.PIPE)
a, b = lector(V), lector(M)
NEON = range(298, 358)                        # plano 3: neón desenfocado a propósito por encima de y 420
MANO = list(range(117, 298)) + list(range(584, 649))   # 2a, 2b y 5: cajas en sus manos (23/11: 5 = 584-648)
res = {'fotogramas': 0, 'caja_total': [9999, 9999, -1, -1], 'fuera_zona': [], 'cara': [], 'boca': [], 'cajas_mano': [], 'manos': []}
k3 = np.ones((3, 3), np.uint8)
for n in range(NFIN):
    x = a.stdout.read(W * H * 3); y = b.stdout.read(W * H * 3)
    if len(x) < W * H * 3 or len(y) < W * H * 3: break
    fa = np.frombuffer(x, np.uint8).reshape(H, W, 3).astype(np.int16); fb = np.frombuffer(y, np.uint8).reshape(H, W, 3).astype(np.int16)
    d = (np.abs(fa - fb).max(2) > 45).astype(np.uint8)
    if n in NEON: d[:420] = 0
    d = cv2.morphologyEx(d, cv2.MORPH_OPEN, k3)
    ys, xs = np.where(d)
    res['fotogramas'] += 1
    if not len(ys): continue
    bb = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]
    t = res['caja_total']; res['caja_total'] = [min(t[0], bb[0]), min(t[1], bb[1]), max(t[2], bb[2]), max(t[3], bb[3])]
    if bb[0] < 84 or bb[2] > 996 or bb[1] < 292 or bb[3] > 1246: res['fuera_zona'].append([n, bb])
    l = LM[n]
    hay_cara = not np.isnan(l).any()
    if hay_cara:
        mc, mb = cara_bisenet(fb.astype(np.uint8), l)
        c1 = int((d & mc).sum()); c2 = int((d & mb).sum())
        if c1: res['cara'].append([n, c1])
        if c2: res['boca'].append([n, c2])
    if n in MANO:   # 23/11: también sin cara (2b y 5 de producto, del cuello para abajo); y las manos
            g = fb; blanco = ((g.min(2) > 150) & ((g.max(2) - g.min(2)) < 50)).astype(np.uint8)
            if hay_cara: blanco[:int(l[8, 1]) + 20] = 0
            r_, g_, b_ = g[..., 0], g[..., 1], g[..., 2]
            piel = ((r_ > 90) & (r_ - b_ > 38) & (r_ - g_ > 12) & (g_ - b_ < .25 * r_)).astype(np.uint8)   # sin la madera (g-b alto)
            nc2, lab2, st2, _ = cv2.connectedComponentsWithStats(cv2.morphologyEx(piel, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)))
            mp = np.isin(lab2, [j for j in range(1, nc2) if st2[j, 4] > 3000]).astype(np.uint8)
            if hay_cara: mp[:int(l[8, 1]) + 40] = 0
            c4 = int((d & mp).sum())
            if c4: res['manos'].append([n, c4])
            nc, lab, st, _ = cv2.connectedComponentsWithStats(cv2.morphologyEx(blanco, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)))
            mk = np.zeros((H, W), np.uint8)
            for j in range(1, nc):
                if st[j, 4] > 4000: mk |= (lab == j).astype(np.uint8)
            c3 = int((d & mk).sum())
            if c3: res['cajas_mano'].append([n, c3])
    else:   # 23/11 (3.ª revisión, T1): manos también en los planos de Intone. La madera del fondo tiene el mismo tono que
            # la piel, así que solo cuenta la piel que queda delante de su cuerpo: en cada fila, entre el primer y el
            # último píxel de la camiseta negra (con 40 px de margen), por debajo de la barbilla + 40 px y sin el cuello.
        g = fb; r_, g_, b_ = g[..., 0], g[..., 1], g[..., 2]
        piel = ((r_ > 90) & (r_ - b_ > 38) & (r_ - g_ > 12) & (g_ - b_ < .25 * r_)).astype(np.uint8)
        piel = cv2.morphologyEx(piel, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
        cam = g.max(2) < 55
        span = np.zeros((H, W), np.uint8); filas = np.where(cam.sum(1) > 60)[0]
        for yy in filas:
            xs_ = np.where(cam[yy])[0]; span[yy, max(0, xs_[0] - 40):xs_[-1] + 41] = 1
        mp = piel & span
        if hay_cara:   # sin el cuello: la piel que sigue pegada a la barbilla (corte en barbilla + 40) no es una mano
            yc = int(l[8, 1]) + 40; mp[:yc] = 0
            nc5, lab5, st5, _ = cv2.connectedComponentsWithStats(mp)
            mp = np.isin(lab5, [j for j in range(1, nc5) if st5[j, 1] > yc + 1]).astype(np.uint8)
        c4 = int((d & mp).sum())
        if c4 > 300: res['manos'].append([n, c4])        # (menos de 300 px: el borde suave de la pastilla)
print('fotogramas comparados', res['fotogramas'], '| caja total de los rótulos (x0,y0,x1,y1):', res['caja_total'])
for k in ('fuera_zona', 'cara', 'boca', 'cajas_mano', 'manos'):
    v = res[k]; print(f'{k}: {len(v)} fotogramas', v[:12])
if OUT: json.dump(res, open(OUT, 'w'))
