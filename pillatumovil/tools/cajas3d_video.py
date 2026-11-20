"""Pone la caja REAL en 3D (tools/caja3d.py) en las manos de la chica, fotograma a fotograma.

Uso: python3 cajas3d_video.py CLIP.mp4 PLAN.json SALIDA.mp4 [--depura CARPETA]
     (CLIP puede ser una foto y SALIDA un .png: así se hacen los planos de detalle)

16/11/2026. La primera versión (15/11) pegaba una foto plana de la caja y rellenaba lo de detrás con un
degradado: el dueño vio que «no se ve real y arriba genera algo borrado». Ahora:
  1. se sigue la caja que dibujó la IA (posición, tamaño, inclinación y, si gira, cuánto ha girado);
  2. se borra y detrás se pone CAMISETA DE VERDAD: se copia tela de otra zona de la propia camiseta
     y se funde con la de alrededor (mezcla de Poisson), así no queda mancha;
  3. se pinta la caja real en 3D en la misma postura: mismo ancho y misma base que la dibujada, con su
     alto, su grosor, sus lados y su pestaña de verdad (la dibujada por la IA era un 35 % más alta);
  4. los dedos que estaban delante siguen delante.

PLAN.json:
{"ini": 0, "fin": 121, "salida": [2160, 3840],
 "clon": [0, 550],                       # de dónde se copia la tela, en píxeles del clip (abajo, la barriga)
 "cajas": [{"semilla": [540, 1100], "modelo": "cargador", "sentido": 1,
            "tramos": [{"de": 0, "a": 30, "modo": "frente"}, {"de": 31, "a": 55, "modo": "giro"},
                       {"de": 56, "a": 120, "modo": "trasera"}]}]}
Las cajas se pintan en el orden de la lista: la que queda delante va la última.
"""
import json, os, subprocess, sys
import cv2, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from caja3d import Caja, giro_x, giro_y, giro_z, PAPEL

clip, plan_p, salida = sys.argv[1:4]
DEP = sys.argv[sys.argv.index('--depura') + 1] if '--depura' in sys.argv else None
plan = json.load(open(plan_p))
TEX = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'fotos', 'caja3d')
info = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', clip],
                      capture_output=True, text=True).stdout.strip().split(',')
W, H = int(info[0]), int(info[1])
INI, FIN = plan.get('ini', 0), plan['fin']
SW, SH = plan.get('salida', [W * 2, H * 2])
AW = int(round(W * SH / H)); OFF = (AW - SW) // 2; SX = AW / W; SY = SH / H
cajas = plan['cajas']; N = FIN - INI
FOCAL = 1.5 * SH                                        # cámara supuesta: unos 37 grados de campo vertical
K = np.array([[FOCAL, 0, SW / 2], [0, FOCAL, SH / 2], [0, 0, 1.0]])
CLON = plan.get('clon')


def fotogramas():
    p = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-i', clip, '-vf', f'trim=start_frame={INI}:end_frame={FIN},setpts=PTS-STARTPTS',
                          '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    while True:
        b = p.stdout.read(W * H * 3)
        if len(b) < W * H * 3: break
        yield np.frombuffer(b, np.uint8).reshape(H, W, 3)


def modo(c, n):
    for t in c['tramos']:
        if t['de'] <= n + INI <= t['a']: return t['modo']
    return None


def mascaras(fr):
    f = fr.astype(np.int16); r, g, b = f[..., 0], f[..., 1], f[..., 2]
    mn, mx = f.min(2), f.max(2)
    blanco = (mn > 150) & (mx - mn < 48)
    piel = (r > 90) & (r - b > 38) & (r - g > 12) & ~blanco
    return blanco, piel


def piel_gruesa(piel):
    """Piel de verdad: manchas gruesas (fuera píxeles sueltos y el canto kraft de la caja dibujada)."""
    gorda = cv2.morphologyEx(piel.astype(np.uint8), cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
    return piel & (cv2.dilate(gorda, np.ones((11, 11), np.uint8)) > 0)


def recta(t, v, hacia):
    t = np.asarray(t, float); v = np.asarray(v, float); ok = np.ones(len(t), bool)
    if hacia:
        a, b = np.polyfit(t, v, 1); res = (v - (a * t + b)) * hacia; ok = res <= np.median(res)
    for _ in range(8):
        a, b = np.polyfit(t[ok], v[ok], 1)
        res = (v - (a * t + b)) * (hacia or 1); s = max(1.2, np.median(np.abs(res[ok])) * 2.5)
        nuevo = (res < s) & (res > -(3 if hacia else 1) * s)
        if nuevo.sum() < 8 or (nuevo == ok).all(): break
        ok = nuevo
    return a, b


def cruce(v_ab, h_ab):
    a, b = v_ab; c, d = h_ab
    y = (c * b + d) / (1 - a * c); return np.array([a * y + b, y])


def componente(etq, centro, r=40):
    cx, cy = int(round(centro[0])), int(round(centro[1]))
    v = etq[max(cy - r, 0):cy + r + 1, max(cx - r, 0):cx + r + 1]; v = v[v > 0]
    return (etq == np.bincount(v).argmax()) if len(v) else None


def localizar(vis):
    """Esquinas TL TR BR BL del cuerpo de la caja dibujada (sin la pestaña)."""
    ys, xs = np.where(vis)
    if len(ys) < 500: return None
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    anch = vis[y0:y1 + 1, x0:x1 + 1].sum(1)
    cuerpo = np.where(anch > np.percentile(anch, 80) * .80)[0]
    yt, yb = cuerpo[0] + y0, cuerpo[-1] + y0; alto = yb - yt
    filas = np.arange(int(yt + alto * .10), int(yb - alto * .06))
    izq = [np.argmax(vis[y, x0:x1 + 1]) + x0 for y in filas]
    der = [x1 - np.argmax(vis[y, x0:x1 + 1][::-1]) for y in filas]
    L = recta(filas, izq, +1); R = recta(filas, der, -1)
    xl, xr = L[0] * (yt + yb) / 2 + L[1], R[0] * (yt + yb) / 2 + R[1]; an = xr - xl
    cols = np.arange(int(xl + an * .06), int(xr - an * .06))
    aba = [y1 - np.argmax(vis[y0:y1 + 1, x][::-1]) for x in cols]
    Bm = recta(cols, aba, -1)
    cols_t = np.arange(int(L[0] * yt + L[1] + an * .03), int(R[0] * yt + R[1] - an * .03))
    d = np.sort(np.array([np.argmax(vis[y0:yb, x]) + y0 for x in cols_t]) - Bm[0] * cols_t)
    Tm = (Bm[0], float(np.median(d[int(len(d) * .75):int(len(d) * .97)])))
    return np.array([cruce(L, Tm), cruce(R, Tm), cruce(R, Bm), cruce(L, Bm)])


def silueta(vis, piel):
    """Mientras gira: (centro de la base, ancho, ángulo de inclinación) de la caja dibujada."""
    cuerpo = cv2.morphologyEx(vis.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((21, 21), np.uint8))
    pts = cv2.findNonZero(cuerpo).reshape(-1, 2).astype(np.float64)
    cen = pts.mean(0); _, _, vt = np.linalg.svd(pts - cen, full_matrices=False)
    eje = vt[0] if abs(vt[0][1]) > abs(vt[0][0]) else vt[1]                 # eje largo, el más vertical
    if eje[1] < 0: eje = -eje                                               # apuntando hacia abajo
    lat = np.array([eje[1], -eje[0]])
    a = (pts - cen) @ eje; b = (pts - cen) @ lat
    medio = np.abs(a - np.median(a)) < (np.percentile(a, 90) - np.percentile(a, 10)) * .35      # zona central: sin pestaña ni dedos
    ancho = np.percentile(b[medio], 98) - np.percentile(b[medio], 2)
    base = cen + eje * np.percentile(a, 99.5) + lat * (np.percentile(b[medio], 98) + np.percentile(b[medio], 2)) / 2
    return base, ancho, np.arctan2(eje[0], eje[1])


def suaviza(a, k=7):
    out = a.copy(); ok = ~np.isnan(a.reshape(len(a), -1)[:, 0]); idx = np.where(ok)[0]
    if not len(idx): return out
    for tr in np.split(idx, np.where(np.diff(idx) > 1)[0] + 1):
        seg = a[tr]; w = np.bartlett(k + 2)[1:-1]; w /= w.sum(); h = k // 2
        pad = np.concatenate([np.repeat(seg[:1], h, 0), seg, np.repeat(seg[-1:], h, 0)])
        out[tr] = sum(w[j] * pad[j:j + len(seg)] for j in range(k))
    return out


# ---------- pasada 1: seguir la caja dibujada ----------
base = [np.full((N, 2), np.nan) for _ in cajas]         # centro del borde de abajo (px del clip)
ancho = [np.full(N, np.nan) for _ in cajas]             # ancho que se ve
incl = [np.full(N, np.nan) for _ in cajas]              # inclinación (radianes; + = caída hacia la derecha por abajo)
quads = [np.full((N, 4, 2), np.nan) for _ in cajas]
blancos = [np.full((N, 3), np.nan) for _ in cajas]      # color del cartón dibujado: da la luz de la escena
centros = [np.array(c['semilla'], float) for c in cajas]
for n, fr in enumerate(fotogramas()):
    blanco, piel = mascaras(fr)
    _, etq = cv2.connectedComponents(blanco.astype(np.uint8))
    for i, c in enumerate(cajas):
        m = modo(c, n)
        if m is None: continue
        vis = componente(etq, centros[i], 40 if m != 'giro' else 60)
        if vis is None: continue
        blancos[i][n] = np.median(fr[vis], 0)
        if m in ('frente', 'trasera'):
            q = localizar(vis)
            if q is None: continue
            quads[i][n] = q; centros[i] = q.mean(0)
            base[i][n] = (q[2] + q[3]) / 2; ancho[i][n] = np.linalg.norm(q[2] - q[3])
            incl[i][n] = np.arctan2(q[2][1] - q[3][1], q[2][0] - q[3][0])
        else:
            ys, xs = np.where(vis); centros[i] = np.array([xs.mean(), ys.mean()])
            b, a, g = silueta(vis, piel)
            base[i][n] = b; ancho[i][n] = a; incl[i][n] = -g

# giro: cuánto ha girado la caja en cada fotograma, por lo que se estrecha
giros = [np.zeros(N) for _ in cajas]; escala = [None] * len(cajas)
for i, c in enumerate(cajas):
    ms = [modo(c, n) for n in range(N)]
    plano = np.array([m in ('frente', 'trasera') for m in ms])
    ref = np.where(plano, ancho[i], np.nan)                       # ancho de la caja de frente
    if 'giro' in ms:
        g = np.array([m == 'giro' for m in ms]); idx = np.where(g)[0]; a0, a1 = idx[0], idx[-1]
        antes = np.nanmedian(ancho[i][max(a0 - 14, 0):max(a0 - 4, 1)]); despues = np.nanmedian(ancho[i][a1 + 5:a1 + 20])
        ref = np.where(np.arange(N) < a0 - 4, ref, np.nan); ref[a1 + 5:] = ancho[i][a1 + 5:]
        ref[a0 - 4:a1 + 5] = np.interp(np.arange(a0 - 4, a1 + 5), [a0 - 4, a1 + 5], [antes, despues])
        r = np.clip(ancho[i] / ref, 0, 1)
        k = a0 - 4 + int(np.nanargmin(r[a0 - 4:a1 + 5])); d = float(np.clip(r[k], .25, .7))      # de canto: el grosor de la dibujada
        th = np.arctan(d) + np.arccos(np.clip(r / np.sqrt(1 + d * d), -1, 1))
        th = np.where(r >= 1, 0, th); th = np.where(np.arange(N) > k, np.pi - th, th)
        th[:a0 - 4] = 0; th[a1 + 5:] = np.pi
        th = np.maximum.accumulate(np.nan_to_num(th, nan=0.0))
        giros[i] = suaviza(th[:, None], 5)[:, 0]
        print('caja', i, '| de canto en el fotograma', k + INI, '| grosor de la dibujada', round(d, 2))
    else:
        giros[i] = np.where(np.array([m == 'trasera' for m in ms]), np.pi, 0.0)
    escala[i] = suaviza(ref[:, None] * SX, 7)[:, 0]
    base[i] = suaviza(base[i], 5); incl[i] = suaviza(incl[i][:, None], 7)[:, 0]
    blancos[i] = suaviza(blancos[i], 15)
print('pasada 1 lista')


# ---------- pasada 2: pintar ----------
def a_salida(p):
    p = np.asarray(p, float); return np.stack([p[..., 0] * SX - OFF, p[..., 1] * SY], -1)


def postura(caja, p_base, ancho_px, guinada, balanceo, sentido):
    """R y t de la caja para que su eje vertical central caiga en p_base, con el ancho pedido."""
    c = np.array([0, 0, caja.D / 2])
    R = giro_z(balanceo) @ giro_y(sentido * guinada)
    z = FOCAL / ancho_px + caja.D / 2 * abs(np.cos(guinada))                 # la cara que se ve queda a la distancia que da su ancho
    eje = np.array([(p_base[0] - K[0, 2]) / FOCAL * z, (p_base[1] - K[1, 2]) / FOCAL * z, z])
    return R, eje - R @ c


def caja_en_zona(caja, R, t, margen=30):
    """Pinta la caja solo en el recorte que ocupa. Devuelve (x0, y0, rgb, alfa)."""
    esq = np.array([(x, y, z) for x in (-.5, .5) for y in (0, -caja.H - caja.Ht) for z in (0, caja.D)])
    X = (R @ esq.T).T + t; uv = (K @ X.T).T; uv = uv[:, :2] / uv[:, 2:3]
    x0, y0 = np.floor(uv.min(0)).astype(int) - margen; x1, y1 = np.ceil(uv.max(0)).astype(int) + margen
    x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, SW), min(y1, SH)
    Kz = K.copy(); Kz[0, 2] -= x0; Kz[1, 2] -= y0
    rgb, alfa = caja.pinta(Kz, R, t, (x1 - x0, y1 - y0))
    return x0, y0, rgb, alfa


def relleno_basto(R, hoyo, piel):
    """Tapa el hueco con el tono de lo que tiene alrededor (sin textura): pegado al borde, lo de al lado (tela,
    madera); más adentro, la tela oscura. Sirve de base: encima va la tela de verdad o la caja nueva."""
    f = R.astype(np.float32)
    fuera = ~cv2.dilate(hoyo.astype(np.uint8), np.ones((13, 13), np.uint8)).astype(bool)
    cerca = fuera & ~cv2.dilate(mascaras(R)[0].astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool) & ~cv2.dilate(piel.astype(np.uint8), np.ones((15, 15), np.uint8)).astype(bool)
    tela = cerca & (R.max(2) < 110)
    h, w_ = R.shape[:2]; ch = (max(w_ // 4, 1), max(h // 4, 1))
    out = np.zeros((ch[1], ch[0], 3), np.float32); hecho = np.zeros((ch[1], ch[0]), np.float32)
    for s, fuente in ((4, cerca), (13, tela), (34, tela)):
        w = cv2.resize(fuente.astype(np.float32), ch, interpolation=cv2.INTER_AREA); fw = cv2.resize(f * fuente[..., None], ch, interpolation=cv2.INTER_AREA)
        den = cv2.GaussianBlur(w, (0, 0), s); num = cv2.GaussianBlur(fw, (0, 0), s)
        ok = np.clip(den / 0.05, 0, 1) * (1 - hecho); out += num / np.maximum(den, 1e-4)[..., None] * ok[..., None]; hecho += ok
    out += (np.median(f[tela], 0) if tela.any() else np.float32([20, 20, 20])) * (1 - hecho)[..., None]
    return cv2.resize(out, (w_, h), interpolation=cv2.INTER_CUBIC)


modelos = {}
for c in cajas:
    if c['modelo'] not in modelos: modelos[c['modelo']] = Caja(c['modelo'], TEX)
FOTO = salida.lower().endswith('.png')
DESPL = [None]                                           # de dónde se copia la tela (se decide en el primer fotograma)
enc = None if FOTO else subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{SW}x{SH}', '-r', '24', '-i', '-',
                                          '-an', '-c:v', 'libx264', '-crf', '10', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-r', '24', salida], stdin=subprocess.PIPE)
for n, fr in enumerate(fotogramas()):
    F = np.ascontiguousarray(cv2.resize(fr, (AW, SH), interpolation=cv2.INTER_LANCZOS4)[:, OFF:OFF + SW])
    orig = F.copy()
    blanco, piel = mascaras(orig); piel = piel_gruesa(piel)
    _, etq = cv2.connectedComponents(blanco.astype(np.uint8))
    # manchas pequeñas de color piel sueltas: son el interior de cartón (kraft) de la tapa de la caja dibujada,
    # no dedos (los dedos van unidos a la mano, que es una mancha grande). Se quitan de la piel y se borran luego.
    ns, es, st, _ = cv2.connectedComponentsWithStats(piel.astype(np.uint8))
    kraft = np.isin(es, [k for k in range(1, ns) if st[k, 4] < 14000 * (SH / 3840) ** 2])
    piel &= ~kraft
    pd = cv2.dilate(piel.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    pintadas = []
    # 1) cada caja: su postura y su imagen
    for i, c in enumerate(cajas):
        m = modo(c, n)
        if m is None or np.isnan(base[i][n]).any() or np.isnan(escala[i][n]): continue
        caja = modelos[c['modelo']]
        R, t = postura(caja, a_salida(base[i][n]), escala[i][n], giros[i][n], incl[i][n], c.get('sentido', 1))
        x0, y0, rgb, alfa = caja_en_zona(caja, R, t)
        vis = componente(etq, a_salida(base[i][n]) - [0, escala[i][n] * .5], 90)
        pintadas.append((i, x0, y0, rgb, alfa, vis))
    # 2) fuera las cajas dibujadas: relleno basto en toda la silueta y tela de verdad donde va a quedar al aire
    nueva = np.zeros((SH, SW), np.float32)
    for i, x0, y0, rgb, alfa, vis in pintadas:
        z = nueva[y0:y0 + alfa.shape[0], x0:x0 + alfa.shape[1]]; np.maximum(z, alfa[..., 0], out=z)
    hoyo = np.zeros((SH, SW), bool)
    for i, x0, y0, rgb, alfa, vis in pintadas:
        if vis is None: continue
        sil = cv2.morphologyEx(vis.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((45, 45), np.uint8))
        cs, _ = cv2.findContours(sil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE); cv2.drawContours(sil, cs, -1, 1, -1)
        sil = cv2.dilate(sil, np.ones((41, 41), np.uint8)).astype(bool)
        # restos claros pegados (pestaña suelta, cantos): también fuera, salvo la piel
        claro = (orig.max(2) > 62) & ~cv2.dilate(piel.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool)
        cerca = cv2.dilate(sil.astype(np.uint8), np.ones((121, 121), np.uint8)).astype(bool)
        _, e2 = cv2.connectedComponents((claro & cerca).astype(np.uint8))
        resto = np.isin(e2, np.unique(e2[sil & claro & (e2 > 0)]))
        resto |= kraft & cerca                                            # tapa kraft de la caja dibujada
        hoyo |= cv2.dilate((sil | resto).astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool)
    borde_carton = cv2.dilate(blanco.astype(np.uint8), np.ones((13, 13), np.uint8)).astype(bool)
    hoyo &= ~(pd & ~borde_carton)                                        # la piel se respeta, salvo el filo pegado al cartón
    if hoyo.any():
        ys, xs = np.where(hoyo); a0, a1, b0, b1 = max(ys.min() - 260, 0), min(ys.max() + 260, SH), max(xs.min() - 260, 0), min(xs.max() + 260, SW)
        Rz = F[a0:a1, b0:b1]; hz = hoyo[a0:a1, b0:b1]
        basto = relleno_basto(Rz, hz, piel[a0:a1, b0:b1])
        F[a0:a1, b0:b1] = np.where(hz[..., None], np.clip(basto, 0, 255), Rz).astype(np.uint8)
        # tela de verdad en lo que queda al aire (fuera de la caja nueva), copiada de CLON y fundida con Poisson
        aire = hoyo & (cv2.erode(nueva, np.ones((25, 25), np.uint8)) < .5)
        aire = cv2.morphologyEx(aire.astype(np.uint8), cv2.MORPH_OPEN, np.ones((9, 9), np.uint8)).astype(bool)
        if aire.sum() > 400:
            # tela válida para copiar: oscura, sin piel, sin cartón y fuera de las cajas dibujadas
            tela_ok = (orig.max(2) < 105) & ~hoyo & ~cv2.dilate((piel | blanco).astype(np.uint8), np.ones((15, 15), np.uint8)).astype(bool)
            ys, xs = np.where(aire); y0, y1, x0, x1 = ys.min() - 6, ys.max() + 7, xs.min() - 6, xs.max() + 7
            if DESPL[0] is None:                                    # se elige una vez, en el primer fotograma, y ya no cambia
                cands = ([tuple(CLON)] if CLON else []) + [(dx, dy) for dy in range(300, 900, 30) for dx in (0, -80, 80, -160, 160)]
                mejor = (-1, None)
                for dx_, dy_ in cands:
                    dx, dy = int(round(dx_ * SX)), int(round(dy_ * SY))
                    if not (y0 > 0 and x0 + dx > 0 and y1 + dy < SH and x1 + dx < SW and x0 > 0): continue
                    v = tela_ok[y0 + dy:y1 + dy, x0 + dx:x1 + dx][aire[y0:y1, x0:x1]].mean()
                    if v > mejor[0] + .01: mejor = (v, (dx_, dy_))
                    if v > .985: break
                DESPL[0] = mejor[1]; print('tela copiada desde', mejor[1], '| válida', round(float(mejor[0]), 3))
            if DESPL[0] is not None:
                dx, dy = int(round(DESPL[0][0] * SX)), int(round(DESPL[0][1] * SY))
                if y0 > 0 and x0 > 0 and y1 + dy < SH and x1 + dx < SW and x0 + dx > 0:
                    vale = cv2.erode(tela_ok[y0 + dy:y1 + dy, x0 + dx:x1 + dx].astype(np.uint8), np.ones((13, 13), np.uint8)).astype(bool)
                    mk = ((aire[y0:y1, x0:x1] & vale) * 255).astype(np.uint8)
                    mk = cv2.morphologyEx(mk, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8)); mk[:3] = 0; mk[-3:] = 0; mk[:, :3] = 0; mk[:, -3:] = 0
                    if mk.any():
                        src = np.ascontiguousarray(orig[y0 + dy:y1 + dy, x0 + dx:x1 + dx])
                        bx, by, bw, bh = cv2.boundingRect(mk)
                        F[:] = cv2.seamlessClone(src, F, mk, (x0 + bx + bw // 2, y0 + by + bh // 2), cv2.NORMAL_CLONE)
    # 3) las cajas reales, con la luz de la escena, y los dedos por delante
    for i, x0, y0, rgb, alfa, vis in pintadas:
        h, w_ = alfa.shape[:2]; Rz = F[y0:y0 + h, x0:x0 + w_].astype(np.float32)
        luz = (blancos[i][n] / PAPEL * 1.04) if not np.isnan(blancos[i][n]).any() else np.float32([.84, .8, .78])
        cap = np.dstack([rgb * luz, alfa]); cap = cv2.GaussianBlur(cap, (0, 0), 0.8)
        pz = piel[y0:y0 + h, x0:x0 + w_]
        sombra_dedos = np.clip(cv2.GaussianBlur(pz.astype(np.float32), (0, 0), 12) * 1.6, 0, 1)[..., None] * .22
        g = np.random.default_rng(n * 7 + i).normal(0, 1.6, (h, w_, 1)).astype(np.float32)
        out = Rz * (1 - cap[..., 3:]) + np.clip(cap[..., :3] * (1 - sombra_dedos) + g * cap[..., 3:], 0, 255)
        pm = cv2.GaussianBlur(cv2.dilate(pz.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(np.float32), (0, 0), 1.3)[..., None]
        out = out * (1 - pm) + orig[y0:y0 + h, x0:x0 + w_].astype(np.float32) * pm          # los dedos, tal como estaban
        F[y0:y0 + h, x0:x0 + w_] = np.clip(out, 0, 255).round().astype(np.uint8)
    if FOTO:
        cv2.imwrite(salida, cv2.cvtColor(F, cv2.COLOR_RGB2BGR)); break
    enc.stdin.write(F.tobytes())
    if DEP and n % 4 == 0:
        os.makedirs(DEP, exist_ok=True); cv2.imwrite(f'{DEP}/s{n + INI:03d}.jpg', cv2.cvtColor(F, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 90])
if enc: enc.stdin.close(); enc.wait()
print('ok', salida)
