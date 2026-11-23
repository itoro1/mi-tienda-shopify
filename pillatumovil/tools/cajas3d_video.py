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

22/11/2026 (v6, solo si el plan trae la clave "v6"; sin ella el resultado es idéntico al de antes): hueco tapado
por zonas (camiseta o madera/fondo, prolongando el borde de la camiseta), uñas como dedo, mate suave de los dedos
sin escalones ni mordiscos, fuera los puntos oscuros y los borrones sueltos de la IA, y la caja algo más cálida, con
un degradado de luz y la sombra suave de los dedos. Ver el bloque «v6» más abajo y cajas/plan3d-*-v6.json.
Opciones: --solo 10,36 (solo esos fotogramas, a PNG en la carpeta de --depura); variables CAJAS_HILOS (hilos de
OpenCV), CAJA3D_TEX (carpeta de las texturas) y CAJAS_VOLCADO (carpeta donde guardar las máscaras, para depurar).
"""
import json, os, subprocess, sys
import cv2, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from caja3d import Caja, giro_x, giro_y, giro_z, PAPEL

clip, plan_p, salida = sys.argv[1:4]
DEP = sys.argv[sys.argv.index('--depura') + 1] if '--depura' in sys.argv else None
plan = json.load(open(plan_p))
TEX = os.environ.get('CAJA3D_TEX') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'fotos', 'caja3d')
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


def caja_en_zona(caja, R, t, margen=30, **luz_kw):
    """Pinta la caja solo en el recorte que ocupa. Devuelve (x0, y0, rgb, alfa). luz_kw va a Caja.pinta (amb, dif)."""
    esq = np.array([(x, y, z) for x in (-.5, .5) for y in (0, -caja.H - caja.Ht) for z in (0, caja.D)])
    X = (R @ esq.T).T + t; uv = (K @ X.T).T; uv = uv[:, :2] / uv[:, 2:3]
    x0, y0 = np.floor(uv.min(0)).astype(int) - margen; x1, y1 = np.ceil(uv.max(0)).astype(int) + margen
    x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, SW), min(y1, SH)
    Kz = K.copy(); Kz[0, 2] -= x0; Kz[1, 2] -= y0
    rgb, alfa = caja.pinta(Kz, R, t, (x1 - x0, y1 - y0), **luz_kw)
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



# ======================= v6 (22/11/2026) =======================
# Solo se usa si el plan trae la clave "v6"; sin ella todo funciona exactamente como antes. Arregla lo que vio la
# revisión de la v5 (D11):
#   - el hueco que deja la caja dibujada se tapa con lo que había detrás SEGÚN LA ZONA: camiseta donde había
#     camiseta y madera/fondo donde había fondo (el borde camiseta|fondo se prolonga en recta desde donde se ve).
#     Antes todo se tapaba con camiseta y salía una mancha negra escalonada sobre la madera;
#   - los «restos» de la caja dibujada solo son cartón (gris/blanco neutro), nunca madera;
#   - las uñas son dedo (antes, al ser claras, contaban como cartón y quedaban puntos negros);
#   - los dedos van encima con un mate suave que separa el color del dedo del fondo viejo (sin escalones ni
#     mordiscos en el canto de la caja) y se quitan los puntos oscuros sueltos;
#   - la caja nueva algo más cálida, con un degradado suave de luz y la sombra suave de los dedos.
# "v6": {"calido": [1.03, 1.0, 0.95], "sombra": [0.30, 0.12], "desenfoque": 1.0, "degradado": 0.05,
#        "margen": 15, "motas": true, "crf": 10}
# 22/11 (dueño: «le quite un pelín de oscuridad a las cajas, tanto del enchufe como del cable… le veo mucha sombra»).
# Dos claves más, opcionales (sin ellas, igual que antes). Aclaran la LUZ de la caja, no la tinta:
#   "aclarar": [gamma, techo]  la luz de la escena que recibe el frente (la del cartón que dibujó la IA, a 0-255) pasa
#                              por 255·(L/255)^gamma, sin pasar de 'techo' (gamma 1 = como antes; 0.5 = bastante más
#                              clara). El color de la luz (cálido/frío) se conserva y la tinta guarda su contraste.
#   "ambiente": [amb, dif]     luz ambiente y direccional de Caja.pinta (por defecto 0.80 y 0.25): con más ambiente
#                              los lados y la tapa quedan menos oscuros respecto al frente.
# 23/11: "puntas": [ratio, ancho] (opcional; sin ella, igual que antes). Mientras gira la caja, la yema que tocaba el
#   canto de la caja dibujada trae pegada la sombra oscura de ese canto; sobre el cartón blanco nuevo salía como una
#   losa negra en la punta de los dedos y el canto de la mano quedaba mordido. Con la clave, en el borde de la mano
#   (hasta 'ancho' px a 4K) y SOLO encima de la caja nueva, lo que es bastante más oscuro que la piel de al lado
#   (canal más alto < ratio × el de la piel de justo al lado, o muy oscuro junto a una yema clara) y toca el exterior
#   se vuelve transparente (se ve la caja nueva), igual que los picos finos (< 8 px) de ese borde. Valor probado:
#   [0.7, 20] (plan3d-B-v6 y plan3d-T-v6).
# 23/11: "restaura": true (opcional; sin ella, igual que antes). (1) El cartón blanco neutro que la máscara de la mano
#   metía entre los dedos (huecos rellenos) sale de la mano: ahí se ve la caja nueva o el relleno, no la caja dibujada.
#   (2) Donde el borde de la mano tocaba la caja dibujada (más alta) y ahora da al relleno, por encima de la caja nueva,
#   el dedo quedaba cortado en recta (pulgar plano y claro hasta el filo): se redondean las esquinas (apertura de 6 px a
#   4K, solo en ese borde) y la piel cae de luz en los últimos 7 px, como el canto de un dedo. Probado en plan3d-A-v6.
# 23/11 (2.ª revisión de la v6: N1, R4, N2). Tres claves más, opcionales (sin ellas, todo igual que antes):
#   "dedos": {"solape": 18, "max": 30, "radio": 420, "redondea": [12, 22, ["trasera"]], "contacto": 0.2}   (plano 5)
#     Los dedos que sujetan la caja por un lado quedan ENCIMA del canto de la caja nueva, como en una mano de verdad:
#     (1) si las yemas no llegan a la caja nueva (la dibujada era más ancha o estaba algo movida) o llegan justo al canto,
#         la mano se acerca a la caja con una deformación suave (todo lo que hay en el canto se mueve 'd' px y nada a
#         'radio' px de él, ni fuera de las filas de la mano) hasta que la mediana de las puntas de los dedos entra
#         'solape' px en la caja; 'd' como mucho 'max' px y suave en el tiempo (se mide antes de pintar, en todos los
#         fotogramas). Solo se mueven las filas de los dedos que llegan al canto (no la palma, que queda detrás de la
#         caja). La caja nueva no se mueve.
#     (2) mate de la mano con dos fondos: detrás del borde de la yema puede haber cartón blanco (la caja dibujada) o
#         camiseta, y su media no es ninguno de los dos (salían flecos y muescas blancas entre los dedos). Se estiman
#         por separado y en cada píxel se usa el que mejor explica su color; la yema borrosa sobre el cartón sale
#         entera, con su borde de verdad. También sale de la mano el cartón blanco metido entre los dedos.
#     (3) yemas cortadas en recta (la IA las tapaba con el canto de su caja): las esquinas del contorno de la mano que
#         queda encima de la caja nueva se redondean con una apertura elíptica de semiejes 'redondea' = [x, y] px a 4K
#         (solo trozos del tamaño de una esquina); con un tercer elemento, solo en esos tramos (p. ej. ["trasera"]: en
#         "frente" y "giro" las yemas del plano 5 ya están enteras y se estropeaban).
#     (4) sombra de contacto: la caja nueva se oscurece hasta 'contacto' (0-1) justo alrededor de las yemas.
#   "puntas" admite un tercer elemento con los tramos en que se usa (p. ej. [0.7, 20, ["giro"]]); el plano 5 ya no la
#   lleva: con las manos acercadas se comía el borde oscuro natural de las yemas y dejaba muescas blancas.
#   "espejo": {"ancho": 150, "alto": 30, "abomba": 5, "radio": 12}   (plano 2a, R4)
#     Dedo vertical cuyo lado tapaba la caja dibujada (más alta) y que ahora da al relleno (el pulgar derecho de 2a, que
#     salía con el lado izquierdo recto como una regla y un filo claro): ese lado se rehace con canto suave (5 px) y
#     abombado hacia fuera 'abomba' px en el centro, la esquina de la punta contra el corte redondeada con radio 'radio'
#     (px a 4K), el color de la propia piel (alargado desde 6 px dentro, sin el canto oscurecido de "restaura") y el
#     canto algo más oscuro, como el del otro lado; detrás, lo de alrededor (relleno o madera). 'ancho': ancho máximo
#     del dedo; 'alto': alto mínimo del corte. Además, fuera las motas oscuras pequeñas rodeadas de claro junto al dedo
#     (la punta del pulgar traía una). Se probó a reflejar el otro lado del dedo: con la punta medio tapada por la caja
#     dibujada salían «banderitas» de piel y pliegues; no se usa.
#   "motas_claras": [radio, area]   (plano 2b, N2)
#     Manchas claras sueltas de la IA (p. ej. una pincelada blanco-azulada junto a la pestaña de la caja dibujada) a
#     menos de 'radio' px del hueco, de menos de 'area' px (a 4K) y rodeadas de camiseta oscura: se tapan como el hueco.
V6 = plan.get('v6')
E6 = SH / 3840
DEDOS = (V6 or {}).get('dedos')
ESPEJO = (V6 or {}).get('espejo')
SOLO = [int(x) for x in sys.argv[sys.argv.index('--solo') + 1].split(',')] if '--solo' in sys.argv else None
if os.environ.get('CAJAS_HILOS'): cv2.setNumThreads(int(os.environ['CAJAS_HILOS']))


def k_el(r):
    r = max(int(round(r)), 1); return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))


def dil(m, r):
    """Dilatación circular de radio r (con r grande, por distancia: mucho más rápida)."""
    m = np.asarray(m).astype(bool)
    if r <= 6: return cv2.dilate(m.astype(np.uint8), k_el(r)).astype(bool)
    return cv2.distanceTransform((~m).astype(np.uint8), cv2.DIST_L2, 3) <= r


def media_pesada(img, w, s, red=1):
    """Media de img ponderada por w (convolución normalizada, gaussiana de sigma s). Devuelve (media, peso)."""
    h, w_ = w.shape
    if red > 1:
        ch = (max(w_ // red, 1), max(h // red, 1))
        wi = cv2.resize(w, ch, interpolation=cv2.INTER_AREA); ii = cv2.resize(img * w[..., None], ch, interpolation=cv2.INTER_AREA)
        den = cv2.GaussianBlur(wi, (0, 0), s / red); num = cv2.GaussianBlur(ii, (0, 0), s / red)
        m = num / np.maximum(den, 1e-6)[..., None]
        return cv2.resize(m, (w_, h), interpolation=cv2.INTER_LINEAR), cv2.resize(den, (w_, h), interpolation=cv2.INTER_LINEAR)
    den = cv2.GaussianBlur(w, (0, 0), s); num = cv2.GaussianBlur(img * w[..., None], (0, 0), s)
    return num / np.maximum(den, 1e-6)[..., None], den


def rellena_capas(img, w, sigmas, red=1):
    """Como media_pesada, pero donde cerca no hay muestras usa sigmas cada vez más grandes."""
    img = img.astype(np.float32); w = w.astype(np.float32)
    out = np.zeros_like(img); hecho = np.zeros(w.shape, np.float32)
    for s in sigmas:
        m, den = media_pesada(img, w, s, red)
        ok = np.clip(den / 0.08, 0, 1) * (1 - hecho)
        out += m * ok[..., None]; hecho += ok
    if hecho.min() < .999:
        out += (img[w > .5].mean(0) if (w > .5).any() else 0) * (1 - hecho)[..., None]
    return out


def mano6(fr):
    """Mano (y brazos, cara…): piel, también la muy clara o en sombra, y las uñas; sin motas, con los huecos pequeños
    rellenos. La madera (más amarilla: g-b alto) y el cartón (poco rojo) no son piel. Las uñas (claras y rosadas,
    del mismo color que el halo borroso de la yema sobre el cartón) solo cuentan si quedan dentro del dedo."""
    f = fr.astype(np.float32); r, g, b = f[..., 0], f[..., 1], f[..., 2]
    piel = (r > 45) & (r - g > .26 * r) & (r - b > .30 * r) & (g - b < .25 * r)   # sin la sombra rosada del dedo en el cartón
    una = (r > 175) & (r - g > 20) & (r - b > 26) & (g - b < .2 * r)
    nucleo = cv2.morphologyEx(piel.astype(np.uint8), cv2.MORPH_OPEN, k_el(2 * E6))
    n, et, st, _ = cv2.connectedComponentsWithStats(nucleo)
    nucleo = np.isin(et, [k for k in range(1, n) if st[k, 4] >= 14000 * E6 * E6]).astype(np.uint8)   # lo pequeño es kraft
    una &= cv2.morphologyEx(nucleo, cv2.MORPH_CLOSE, k_el(18 * E6)).astype(bool)
    m = cv2.morphologyEx(((nucleo > 0) | una).astype(np.uint8), cv2.MORPH_CLOSE, k_el(4 * E6))
    n, et, st, _ = cv2.connectedComponentsWithStats(1 - m, connectivity=4)
    hueco = np.isin(et, [k for k in range(1, n) if st[k, 4] < 3000 * E6 * E6])   # brillo de una uña, pliegues
    m = (m > 0) | hueco
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, k_el(5 * E6))           # fuera tiras finas (canto del cartón)
    n, et, st, _ = cv2.connectedComponentsWithStats(m)
    return np.isin(et, [k for k in range(1, n) if st[k, 4] >= 14000 * E6 * E6])


def alfa_mano6(I, m, zona, pares=False):
    """Mate suave de la mano (0-1): 1 dentro, 0 fuera y, en el borde, mezcla de color entre la piel de al lado (F)
    y el fondo viejo de al lado (B): alfa = (I-B)·(F-B)/|F-B|². Devuelve (alfa, B).
    pares (opción "dedos"): detrás de la yema puede haber cartón blanco (la caja dibujada) o camiseta oscura, y la
    media de los dos no es ninguno (salían flecos y muescas blancas). Se estiman los dos fondos por separado y en cada
    píxel se usa el que mejor explica su color como mezcla de piel y fondo; junto al cartón la franja de borde llega a
    12 px (la yema borrosa sobre el blanco es más ancha)."""
    seg_m = cv2.erode(m.astype(np.uint8), k_el(7 * E6)).astype(np.float32)
    claro = (I.min(2) > 140) & (I.max(2) - I.min(2) < 45)                                 # cartón (sin la tinta)
    if not pares:
        seg_f = 1 - cv2.dilate(m.astype(np.uint8), k_el(5 * E6)).astype(np.float32)
    else:
        seg_f = 1 - (dil(m, 5 * E6) | (dil(m, 12 * E6) & dil(claro & ~dil(m, 5 * E6), 14 * E6))).astype(np.float32)
    Fm = rellena_capas(I, seg_m, (6 * E6, 20 * E6, 60 * E6), 2)
    if not pares:
        Bm = rellena_capas(I, seg_f, (5 * E6, 16 * E6, 50 * E6), 2)
    else:
        Bw = rellena_capas(I, seg_f * claro, (5 * E6, 16 * E6, 50 * E6, 150 * E6), 2)
        Bd = rellena_capas(I, seg_f * (I.max(2) < 110), (5 * E6, 16 * E6, 50 * E6, 150 * E6), 2)
        def ajusta(B):
            d_ = Fm - B; a_ = np.clip(((I - B) * d_).sum(2) / np.maximum((d_ * d_).sum(2), 400.0), 0, 1)
            return np.sqrt(((I - (a_[..., None] * Fm + (1 - a_[..., None]) * B)) ** 2).sum(2))
        blanco_ = cv2.GaussianBlur((ajusta(Bw) < ajusta(Bd)).astype(np.float32), (0, 0), 1.0 * E6)[..., None]
        Bm = blanco_ * Bw + (1 - blanco_) * Bd
        FONDO_FUERA[0] = Bd
    d = Fm - Bm; a = ((I - Bm) * d).sum(2) / np.maximum((d * d).sum(2), 400.0)
    a = np.where(seg_m > 0, 1.0, np.where(seg_f > 0, 0.0, np.clip(a, 0, 1))).astype(np.float32)
    a = cv2.GaussianBlur(a, (0, 0), 0.9 * E6)
    return a * zona, Bm


def puntas6(mano, orig, nueva, ratio=.7, ancho=20):
    """Opción "puntas": en el borde de la mano y solo encima de la caja nueva, lo bastante más oscuro que la piel de al
    lado (canal más alto < ratio × el de la piel de justo al lado, o < 85 y < 0,55 × la yema clara más cercana) y que
    toca el exterior es la sombra del canto de la caja dibujada pegada a las yemas; también los picos finos (< 8 px)
    del borde. Devuelve esa máscara (ahí el mate de la mano va a 0 y se ve la caja nueva) o None. La máscara de la
    mano no cambia (el color del fondo viejo se sigue estimando igual)."""
    enc = nueva > .5
    ys, xs = np.where(enc & dil(mano, 4))
    if not len(ys): return None
    m_ = int(60 * E6)
    y0, y1, x0, x1 = max(ys.min() - m_, 0), min(ys.max() + m_, SH), max(xs.min() - m_, 0), min(xs.max() + m_, SW)
    Z = (slice(y0, y1), slice(x0, x1))
    m = mano[Z]; e = enc[Z]; V = orig[Z].max(2).astype(np.float32)
    nucleo = cv2.erode(m.astype(np.uint8), k_el(8 * E6)).astype(np.float32)               # piel de justo al lado: así
    den = cv2.GaussianBlur(nucleo, (0, 0), 8 * E6); Vmed = cv2.GaussianBlur(V * nucleo, (0, 0), 8 * E6) / np.maximum(den, 1e-6)   # la sombra suave del dedo no cuenta
    borde = m & ~cv2.erode(m.astype(np.uint8), k_el(ancho * E6)).astype(bool)
    Vmax = cv2.dilate(V * nucleo, k_el(25 * E6))                                        # y lo muy oscuro junto a una
    osc = borde & e & (((den > .03) & (V < ratio * Vmed)) | ((V < .55 * Vmax) & (V < 85)))  # yema clara (hueco ancho)
    n, et, _, _ = cv2.connectedComponentsWithStats(osc.astype(np.uint8))
    toca = np.unique(et[dil(~m & e, 2) & (et > 0)])
    m2 = m & ~np.isin(et, toca)
    abierta = cv2.morphologyEx(m2.astype(np.uint8), cv2.MORPH_OPEN, k_el(4 * E6)).astype(bool)
    m2 = np.where(dil(e, 2), abierta, m2)
    q = np.zeros_like(mano); q[Z] = dil(m & ~m2, 6 * E6) & ~m2 & dil(e, 2)                  # y la banda del mate de fuera
    return q if q.any() else None


def recta_robusta(y, x):
    y = np.asarray(y, float); x = np.asarray(x, float); ok = np.ones(len(y), bool)
    for _ in range(8):
        a, b = np.polyfit(y[ok], x[ok], 1)
        res = np.abs(x - (a * y + b)); s = max(3.0 * E6, np.median(res[ok]) * 2.5)
        nuevo = res < s
        if nuevo.sum() < 12 or (nuevo == ok).all(): break
        ok = nuevo
    return a, b, int(ok.sum())


def bordes_camiseta(oscuro, valido, y0, y1, x0, x1):
    """Puntos del borde de la camiseta con el fondo en el recorte: (ys, xs) del borde derecho (camiseta a la
    izquierda, fondo a la derecha) y del izquierdo. Se exigen 12 px seguidos de cada lado."""
    H_, W_ = oscuro.shape; y0, y1, x0, x1 = max(y0, 0), min(y1, H_), max(x0, 0), min(x1, W_)
    if y1 - y0 < 4 or x1 - x0 < 30: return (np.array([]), np.array([])), (np.array([]), np.array([]))
    s = (oscuro & valido)[y0:y1, x0:x1].astype(np.uint8); f = (~oscuro & valido)[y0:y1, x0:x1].astype(np.uint8)
    L = int(round(12 * E6)); k = np.ones((1, L + 1), np.uint8)
    s_izq = cv2.erode(s, k, anchor=(L, 0), borderType=cv2.BORDER_CONSTANT, borderValue=0)   # camiseta en x-L..x
    s_der = cv2.erode(s, k, anchor=(0, 0), borderType=cv2.BORDER_CONSTANT, borderValue=0)   # camiseta en x..x+L
    f_izq = cv2.erode(f, k, anchor=(L, 0), borderType=cv2.BORDER_CONSTANT, borderValue=0)
    f_der = cv2.erode(f, k, anchor=(0, 0), borderType=cv2.BORDER_CONSTANT, borderValue=0)
    d = max(int(round(2 * E6)), 1); G = int(round(26 * E6))        # entre camiseta y fondo puede haber unos px de mezcla
    f_der_g = cv2.dilate(f_der, np.ones((1, G + 1), np.uint8), anchor=(0, 0))     # hay fondo en x..x+G
    s_der_g = cv2.dilate(s_der, np.ones((1, G + 1), np.uint8), anchor=(0, 0))
    der = np.zeros_like(s); der[:, :-d] = s_izq[:, :-d] & f_der_g[:, d:] & ~s[:, d:]
    izq = np.zeros_like(s); izq[:, :-d] = f_izq[:, :-d] & s_der_g[:, d:] & ~f[:, d:]
    yd, xd = np.where(der); yi, xi = np.where(izq)
    return (yd + y0, xd + x0 + d), (yi + y0, xi + x0 + d + G / 2)


def borde_por_fila(ys, xs, lado):
    """Un punto de borde por fila: el más exterior (derecho: el de más a la derecha; izquierdo: el de más a la izquierda)."""
    if not len(ys): return np.array([]), np.array([])
    o = np.lexsort((xs if lado == 0 else -xs, ys)); ys, xs = ys[o], xs[o]
    ult = np.r_[ys[1:] != ys[:-1], True]
    return ys[ult].astype(float), xs[ult].astype(float)


def borde_en_filas(fy, fx, filas):
    """x del borde en cada fila de 'filas': entre dos tramos vistos se interpola; fuera, se prolonga desde las filas
    vistas más cercanas con poca pendiente (los hombros se van poniendo verticales) y sin alejarse más de 60 px."""
    out = np.full(len(filas), np.nan)
    if len(fy) < 20: return out
    for j, r in enumerate(filas):
        arr = fy < r; abj = fy > r
        if arr.sum() >= 8 and abj.sum() >= 8 and (r - fy[arr].max()) + (fy[abj].min() - r) < 400 * E6:
            ya, xa = fy[arr][-8:].mean(), np.median(fx[arr][-8:]); yb, xb = fy[abj][:8].mean(), np.median(fx[abj][:8])
            out[j] = xa + (xb - xa) * (r - ya) / max(yb - ya, 1); continue
        lado = arr if arr.sum() >= 20 else (abj if abj.sum() >= 20 else None)
        if lado is None: continue
        y_, x_ = fy[lado], fx[lado]
        cerca = np.argsort(np.abs(y_ - r))[:int(60 * E6)]
        if len(cerca) < 15: continue
        a, b, ok = recta_robusta(y_[cerca], x_[cerca])
        y0 = y_[cerca][np.argmin(np.abs(y_[cerca] - r))]
        out[j] = a * y0 + b + np.clip(.4 * np.clip(a, -.4, .4) * (r - y0), -60 * E6, 60 * E6)
    ok = ~np.isnan(out)
    if ok.sum() > 5:                                           # sin escalones de una fila a otra
        v = np.interp(np.arange(len(out)), np.where(ok)[0], out[ok])
        v = cv2.GaussianBlur(v.reshape(-1, 1).astype(np.float32), (1, 0), 12 * E6).ravel()
        out = np.where(ok, v, np.nan)
    return out


BORDES = {}


def clase_camiseta(oscuro, valido, hueco, fondo_ok):
    """Dentro del hueco: True donde había camiseta. El borde camiseta|fondo que se ve encima, debajo y al lado del
    hueco se continúa por dentro (se interpola o se prolonga). Fuera del hueco, lo que se ve."""
    pred = oscuro.copy()
    n, et, st, _ = cv2.connectedComponentsWithStats(hueco.astype(np.uint8))
    banda = int(round(260 * E6)); mx = int(round(90 * E6))
    ys_, xs_ = np.where(hueco); y0_, y1_ = ys_.min(), ys_.max()
    centro = np.median(np.where(oscuro[y0_:y1_ + 1:8])[1]) if oscuro[y0_:y1_ + 1:8].any() else SW / 2   # centro del torso
    for k in range(1, n):
        x, y, w, h, area = st[k]
        comp = et[y:y + h, x:x + w] == k
        filas = np.arange(y, y + h)
        bordes = []
        for lado in (0, 1):
            pts = bordes_camiseta(oscuro, valido & (oscuro | fondo_ok), y - banda, y + h + banda, x - mx, x + w + mx)[lado]
            fuera = (pts[1] > centro + 150 * E6) if lado == 0 else (pts[1] < centro - 150 * E6)    # solo el contorno de fuera
            fy, fx = borde_por_fila(pts[0][fuera], pts[1][fuera], lado)
            xb = borde_en_filas(fy, fx, filas)
            clave = (lado, int(x + w / 2) // int(300 * E6))
            prev = BORDES.get(clave)
            if prev is not None:                                   # suave en el tiempo: el borde no tiembla
                pv = np.full(len(filas), np.nan); m_ = (filas >= prev[0]) & (filas < prev[0] + len(prev[1]))
                pv[m_] = prev[1][filas[m_] - prev[0]]
                ambos = ~np.isnan(xb) & ~np.isnan(pv)
                xb = np.where(ambos, .6 * pv + .4 * xb, xb)
            BORDES[clave] = (int(filas[0]), xb.copy())
            bordes.append((lado, xb))
        xx = np.arange(x, x + w)[None, :]
        c = np.ones_like(comp); alguno = False
        for lado, xb in bordes:
            ok = ~np.isnan(xb)
            if ok.sum() < 3: continue
            alguno = True
            xb = np.where(ok, xb, np.nan)
            cond = (xx <= xb[:, None]) if lado == 0 else (xx >= xb[:, None])
            c &= np.where(ok[:, None], cond, True)
        if not alguno:                                               # sin borde a la vista: lo que hay alrededor
            ani = dil(comp, 30 * E6)
            zz = (slice(y, y + h), slice(x, x + w))
            v = valido[zz] & ani & ~comp & (oscuro[zz] | fondo_ok[zz])
            c = np.full_like(comp, (oscuro[zz][v].mean() > .5) if v.any() else True)
        z = pred[y:y + h, x:x + w]; z[comp] = c[comp]
    return pred


CLON6 = {}


def elige_desplaz(objetivo, fuente_ok, cands, n=4):
    """Los n desplazamientos (dx, dy) de cands con más fuente válida para los píxeles de objetivo."""
    ys, xs = np.where(objetivo)
    if len(ys) > 20000:
        i = np.random.default_rng(0).choice(len(ys), 20000, replace=False); ys, xs = ys[i], xs[i]
    H_, W_ = fuente_ok.shape; res = []
    for dx, dy, pena in cands:
        yy, xx = ys + dy, xs + dx; ok = (yy >= 0) & (yy < H_) & (xx >= 0) & (xx < W_)
        v = np.zeros(len(ys), bool); v[ok] = fuente_ok[yy[ok], xx[ok]]
        res.append((v.mean() - pena, (dx, dy)))
    res.sort(key=lambda r: -r[0])
    return [d for _, d in res[:n]]


def clona(I, objetivo, fuente_ok, desplaz, margen):
    """Para cada píxel del recorte (objetivo + margen): el primer desplazamiento cuya fuente vale. Devuelve
    (recorte, S = imagen copiada, asignado)."""
    H_, W_ = objetivo.shape
    ys, xs = np.where(objetivo); y0, y1 = max(ys.min() - margen, 0), min(ys.max() + margen + 1, H_)
    x0, x1 = max(xs.min() - margen, 0), min(xs.max() + margen + 1, W_)
    yy, xx = np.mgrid[y0:y1, x0:x1]
    S = np.zeros((y1 - y0, x1 - x0, 3), np.float32); hecho = np.zeros((y1 - y0, x1 - x0), bool)
    for dx, dy in desplaz:
        sy, sx = yy + dy, xx + dx; ok = (sy >= 0) & (sy < H_) & (sx >= 0) & (sx < W_) & ~hecho
        ok[ok] = fuente_ok[sy[ok], sx[ok]]
        S[ok] = I[sy[ok], sx[ok]]; hecho |= ok
    return (slice(y0, y1), slice(x0, x1)), S, hecho


def rellena6(I, hueco, tapa, valido, oscuro, camiseta, fondo_ok):
    """Tapa el hueco: donde quedará a la vista ('tapa'), textura copiada de otra zona de la misma clase (camiseta o
    fondo; el fondo se copia en vertical para seguir la veta de la madera), con el color corregido por el de
    alrededor (solo frecuencias bajas); el resto del hueco, la media suave de alrededor de su clase."""
    out = I.copy()
    m_out = int(round(50 * E6))
    for clase in (True, False):
        es = camiseta if clase else ~camiseta
        hz = hueco & es
        if not hz.any(): continue
        fuente_ok = valido & (oscuro if clase else (~oscuro & fondo_ok))
        # base: media suave de la clase (por si no hay textura que copiar)
        ys, xs = np.where(hz); y0, y1 = max(ys.min() - 300, 0), min(ys.max() + 301, I.shape[0]); x0, x1 = max(xs.min() - 300, 0), min(xs.max() + 301, I.shape[1])
        zz = (slice(y0, y1), slice(x0, x1))
        base = rellena_capas(I[zz], fuente_ok[zz], (8 * E6, 24 * E6, 70 * E6, 200 * E6, 500 * E6), 4)
        o = out[zz]; o[hz[zz]] = base[hz[zz]]
        obj = tapa & es
        n, et, st, cen = cv2.connectedComponentsWithStats(obj.astype(np.uint8))
        for k in range(1, n):
            if st[k, 4] < 150 * E6 * E6: continue
            comp = et == k; x, y, w, h = st[k, :4]
            # el mismo trozo de un fotograma a otro copia siempre del mismo sitio (si no, la textura salta)
            clave = next((c_ for c_ in CLON6 if c_[0] == clase and abs(c_[1] - cen[k][0]) + abs(c_[2] - cen[k][1]) < 350 * E6), None)
            if clave is None:
                clave = (clase, float(cen[k][0]), float(cen[k][1]))
                if clase:
                    cands = [(dx, dy, 4e-5 * (abs(dx) + abs(dy))) for dy in range(-int(2000 * E6), int(2000 * E6), int(40 * E6))
                             for dx in (0, -int(150 * E6), int(150 * E6), -int(400 * E6), int(400 * E6), -int(800 * E6), int(800 * E6))]
                else:
                    cands = [(0, dy, 3e-5 * abs(dy)) for dy in range(-int(1600 * E6), int(1600 * E6), int(20 * E6))] + \
                            [(dx, dy, 3e-5 * abs(dy) + 2e-4 * abs(dx)) for dx in (-int(60 * E6), int(60 * E6), -int(150 * E6), int(150 * E6))
                             for dy in range(-int(1600 * E6), int(1600 * E6), int(40 * E6))]
                cands = [c for c in cands if abs(c[0]) + abs(c[1]) > 8 * E6]
                CLON6[clave] = elige_desplaz(comp, fuente_ok, cands, 5)
                print('  clon', 'camiseta' if clase else 'fondo', (round(clave[1]), round(clave[2])), CLON6[clave][:3])
            Z, S, asig = clona(I, comp, fuente_ok, CLON6[clave], m_out)
            cz = comp[Z]; hzz = hz[Z]
            anillo = dil(cz, 40 * E6) & ~hueco[Z] & fuente_ok[Z] & asig
            if anillo.sum() < 30: continue
            usa = (cz & asig & hzz)
            o = out[Z]
            if clase:
                # camiseta: la luz y los pliegues grandes salen de alrededor (base suave) y de la copia solo el grano
                # de la tela; así no se cuelan manchas ni pliegues de otra zona
                fino = S - cv2.GaussianBlur(S, (0, 0), 6 * E6)
                o[usa] = (o + fino)[usa]
            else:
                corr = rellena_capas(I[Z] - S, anillo, (20 * E6, 60 * E6, 180 * E6), 2)
                o[usa] = (S + corr)[usa]
    return out


def quita_motas(F, zona):
    """Puntos oscuros sueltos (unos px) dentro de zona: se cambian por la mediana de alrededor."""
    ys, xs = np.where(zona)
    if not len(ys): return
    y0, y1, x0, x1 = max(ys.min() - 20, 0), min(ys.max() + 21, F.shape[0]), max(xs.min() - 20, 0), min(xs.max() + 21, F.shape[1])
    Z = F[y0:y1, x0:x1]; L = Z.astype(np.float32).mean(2)
    med = cv2.medianBlur(Z, 2 * int(round(9 * E6)) + 1); Lm = med.astype(np.float32).mean(2)
    oscuro = (L < Lm * .62) & (Lm - L > 35) & zona[y0:y1, x0:x1]
    n, et, st, _ = cv2.connectedComponentsWithStats(oscuro.astype(np.uint8))
    malo = np.isin(et, [k for k in range(1, n) if st[k, 4] < 260 * E6 * E6])
    malo = cv2.dilate(malo.astype(np.uint8), k_el(2 * E6)).astype(bool)
    Z[malo] = med[malo]


def suave01(t):
    t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)


def mide_lado(bm, mano, lado):
    """Opción "dedos": cuánto entran en la caja nueva (bm, bool) los dedos que la sujetan por su canto 'lado' (-1 el
    izquierdo, +1 el derecho). Por fila: hasta dónde llega la mano que viene de fuera (px; > 0 = encima de la caja);
    las puntas de los dedos son los máximos del perfil y se toma su mediana. Devuelve (alcance, filas, a, b): 'filas'
    (SH) vale 1 en las filas de los dedos que llegan al canto (no en la palma que queda detrás de la caja, que no se
    mueve), suave; el canto es x = a·y + b. None si ninguna mano llega cerca del canto."""
    filas = np.flatnonzero(bm.any(1))
    if len(filas) < 60: return None
    P = int(round(60 * E6)); L = int(round(90 * E6)); m_ = int(round(14 * E6))
    ys, es, ov = [], [], []
    for y in range(filas[0] + m_, filas[-1] - m_):
        r = np.flatnonzero(bm[y])
        if not len(r): continue
        e = r[0] if lado < 0 else r[-1]
        ys.append(y); es.append(e)
        a = e - P if lado < 0 else e + P
        if a < 0 or a >= SW or not mano[y, a]: ov.append(np.nan); continue
        seg = mano[y, a:min(e + L, SW)] if lado < 0 else mano[y, max(e - L, 0):a + 1][::-1]
        ov.append((len(seg) if seg.all() else int(np.argmin(seg))) - P)
    ys = np.array(ys); es = np.array(es, float); ov = np.array(ov)
    v = ~np.isnan(ov)
    if v.sum() < 25 * E6: return None
    i0, i1 = np.flatnonzero(v)[[0, -1]]
    from scipy.signal import find_peaks
    prof = np.where(v, ov, -P - 5.0)[i0:i1 + 1]
    pk, _ = find_peaks(np.r_[-P - 5.0, prof, -P - 5.0], distance=max(int(28 * E6), 1), prominence=3 * E6)
    alt = prof[pk - 1] if len(pk) else prof[[int(np.argmax(prof))]]
    alt = alt[alt > -P + 3]
    if not len(alt): return None
    sel = slice(max(i0 - int(120 * E6), 0), i1 + int(120 * E6))
    a, b, _ = recta_robusta(ys[sel], es[sel])
    alc = float(np.median(alt))
    dedo = np.zeros(SH, np.float32); dedo[ys[v & (ov >= alc - 30 * E6)]] = 1
    g = int(round(40 * E6)) | 1                                                 # sin huecos entre dedo y dedo
    dedo = cv2.morphologyEx(dedo.reshape(-1, 1), cv2.MORPH_CLOSE, np.ones((g, 1), np.uint8)).ravel()
    return alc, cv2.GaussianBlur(dedo.reshape(-1, 1), (1, 0), 12 * E6).ravel(), float(a), float(b)


FONDO_FUERA = [None]      # opción "dedos": fondo de fuera de la caja dibujada (lo último que calculó alfa_mano6)
MANOS = {}      # opción "dedos": (caja, lado) -> {'d', 'y0', 'y1', 'a', 'b'}: arrays por fotograma (ya suavizados)


def acerca_manos(F, n):
    """Opción "dedos": acerca cada mano a su caja (deformación horizontal suave; ver el bloque de arriba)."""
    for (i, lado), p in MANOS.items():
        d = p['d'][n]
        if not d >= .5: continue
        a, b, fil = p['a'][n], p['b'][n], p['filas'][n]
        R = DEDOS.get('radio', 420) * E6; Din = 50 * E6
        yy = np.flatnonzero(fil > .01)
        if len(yy) < 10: continue
        ya, yb = int(yy[0]), int(yy[-1]) + 1
        Y = np.arange(ya, yb, dtype=np.float32); e = a * Y + b
        if lado < 0: xa, xb = int(max(e.min() - R - 4, 0)), int(min(e.max() + 2 * Din + 4, SW))
        else: xa, xb = int(max(e.min() - 2 * Din - 4, 0)), int(min(e.max() + R + 4, SW))
        if xb - xa < 10: continue
        X = np.arange(xa, xb, dtype=np.float32)[None, :]
        q = lado * (X - e[:, None])                                              # > 0: fuera de la caja (la mano)
        wx = np.where(q >= 0, 1 - suave01(q / R), 1 - suave01((-q - Din) / Din))
        wy = fil[ya:yb, None]
        Dx = (-lado * d) * wx * wy                                               # hacia dentro de la caja
        mx = (X - Dx).astype(np.float32); my_ = np.repeat(Y[:, None], xb - xa, 1).astype(np.float32)
        F[ya:yb, xa:xb] = cv2.remap(np.ascontiguousarray(F[ya:yb, xa:xb]), mx - xa, my_ - ya, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return F


def espejo6(out, G, am, Iz, fill, nz, out0):
    """Opción "espejo": un dedo vertical cuyo lado tapaba la caja dibujada y ahora da al relleno (corte recto, alto, en
    'fill') se rehace por ese lado: canto suave y algo abombado en vez de recto, esquina de la punta redondeada, color
    de la propia piel; detrás, lo de alrededor. (Se probó a reflejar el otro lado: con la punta medio tapada salían
    banderitas y pliegues, ver el informe del 23/11.)"""
    ancho = ESPEJO.get('ancho', 150) * E6; alto = ESPEJO.get('alto', 30) * E6
    H_, W_ = am.shape; dentro = am > .5
    corte = dentro & dil(fill, 3 * E6)
    n_, e_, s_, _ = cv2.connectedComponentsWithStats(corte.astype(np.uint8))
    hechos = []
    for k in range(1, n_):
        x, y, w, h, _ = s_[k]
        if h < alto or w > .6 * h: continue
        comp = e_[y:y + h] == k
        xc = np.array([np.flatnonzero(r).mean() if r.any() else np.nan for r in comp])
        if np.isnan(xc).all(): continue
        xcm = float(np.nanmedian(xc)); ym = y + h // 2
        lado = 1 if am[ym, int(min(xcm + 10 * E6, W_ - 1))] > .5 else -1
        c0 = int(max(xcm - (30 * E6 if lado > 0 else ancho), 0)); c1 = int(min(xcm + (ancho if lado > 0 else 30 * E6), W_))
        filas, izq, der = [], [], []
        for r in range(y + h - 1, max(y - int(160 * E6), 0) - 1, -1):          # de abajo arriba, hasta la punta
            fila = dentro[r, c0:c1]
            if r >= y:
                x0_ = xc[r - y] if not np.isnan(xc[r - y]) else xcm
                j = int(round(x0_)) - c0; run = fila[j::lado] if lado > 0 else fila[j::-1]
                if not len(run) or not run[0]: continue
                L = len(run) if run.all() else int(np.argmin(run))
                if L > ancho: continue                                          # aquí el dedo ya es la mano
                filas.append(r); izq.append(x0_); der.append(x0_ + lado * (L - 1))
            else:
                cols = np.flatnonzero(fila)
                if not len(cols): break
                filas.append(r); izq.append(c0 + (cols.min() if lado > 0 else cols.max())); der.append(c0 + (cols.max() if lado > 0 else cols.min()))
        if len(filas) < alto: continue
        filas = np.array(filas); der = np.array(der, float); izq = np.array(izq, float)
        ya = filas.min()
        # forma nueva del lado cortado: sigue el corte pero abombado hacia fuera 'abomba' px en el centro (no recto como
        # una regla), con canto suave de 5 px, y arriba con el mismo perfil que la punta junto al corte; la esquina de
        # arriba (donde la punta tocaba el corte) se redondea con radio 'radio'. El otro lado y la punta no se tocan.
        ra, rb = int(max(ya - 8 * E6, 0)), int(filas.max()) + 1
        R_ = np.arange(ra, rb, dtype=np.float32)
        xcf = np.interp(R_, np.arange(y, y + h)[~np.isnan(xc)], xc[~np.isnan(xc)])
        rad = ESPEJO.get('radio', 12) * E6; ab = ESPEJO.get('abomba', 5) * E6
        xa0 = int(max(np.floor((xcf.min() - ab - 12 * E6) if lado > 0 else (xcf.min() - 3 * rad)), 0))
        xb0 = int(min(np.ceil((xcf.max() + 3 * rad) if lado > 0 else (xcf.max() + ab + 12 * E6)), W_))
        X = np.arange(xa0, xb0, dtype=np.float32)[None, :]
        Z_ = (slice(ra, rb), slice(xa0, xb0))
        n2, e2 = cv2.connectedComponents((am > .25).astype(np.uint8))           # solo el propio dedo
        ks2 = np.unique(e2[y:y + h][comp & (e2[y:y + h] > 0)])
        a_vis = (am * dil(np.isin(e2, ks2), 2 * E6))[Z_].astype(np.float32)
        t_ = np.clip((R_ - y) / max(rb - y, 1), 0, 1)
        borde = xcf - lado * ab * np.sin(np.pi * t_) ** .7
        a_lado = suave01((lado * (X - borde[:, None]) + 2.5 * E6) / (5 * E6))
        cin = np.clip(np.round(xcf + lado * 4 * E6).astype(int) - xa0, 0, xb0 - xa0 - 1)
        perfil = a_vis[np.arange(rb - ra), cin]                                   # la punta junto al corte, por filas
        fuera = lado * (X - xcf[:, None]) < 4 * E6
        a_r = np.where(fuera, a_lado * perfil[:, None], a_vis)
        esq = (R_[:, None] < ya + 2.5 * rad) & (lado * (X - xcf[:, None]) < 2.5 * rad)
        op = cv2.morphologyEx((a_r > .5).astype(np.uint8), cv2.MORPH_OPEN, k_el(rad)).astype(np.float32)
        a_r = np.where(esq, np.minimum(a_r, cv2.GaussianBlur(op, (0, 0), 1.5 * E6)), a_r)
        # color: el de la propia piel (out0: antes del canto oscurecido de "restaura"); hasta 6 px dentro del corte
        # viejo y más allá, el de la piel a 6 px del corte, alargado en horizontal (la piel es lisa: sin bandas); el canto
        # nuevo algo más oscuro en sus últimos 7 px, como el del otro lado
        xs6 = np.clip(np.round(xcf + lado * 6 * E6).astype(int), 0, W_ - 1)
        piel6 = out0[np.arange(ra, rb), xs6]
        dentro_viejo = lado * (X - xcf[:, None]) >= 6 * E6
        C_r = np.where(dentro_viejo[..., None], out0[Z_], piel6[:, None, :])
        d_in = cv2.distanceTransform((a_r > .5).astype(np.uint8), cv2.DIST_L2, 3)
        C_r = C_r * (0.88 + 0.12 * suave01(d_in / (7 * E6)))[..., None]
        # detrás: lo de alrededor que no es mano (el relleno de camiseta o la madera)
        fondo_ok = ~dil(am > .03, 3 * E6)
        bg = rellena_capas(G[Z_], fondo_ok[Z_].astype(np.float32), (3 * E6, 10 * E6, 30 * E6))
        bg = np.where(fondo_ok[Z_][..., None], G[Z_], bg)
        nuevo = a_r[..., None] * C_r + (1 - a_r[..., None]) * bg
        wt = (fuera | esq).astype(np.float32)
        wt = cv2.GaussianBlur(wt, (0, 0), 1.5 * E6) * (1 - np.clip(nz[Z_] * 2, 0, 1))   # la caja nueva no se toca
        wt *= np.clip((rb - 1 - R_[:, None]) / (14 * E6), 0, 1)                   # abajo, donde empieza la mano, se funde
        out[Z_] = out[Z_] * (1 - wt[..., None]) + nuevo * wt[..., None]
        hechos.append((int(ya), int(y), int(rb), int(lado)))
        cambio_ = np.zeros(am.shape, bool); cambio_[Z_] = wt > .01
        ESPEJO_ZONA.append(cambio_)
        # motas oscuras junto al dedo nuevo que no son la camiseta del relleno (la punta del pulgar traía una: el
        # final de la franja de camiseta que se veía entre la caja dibujada y la madera): fuera, con el fondo de al lado
        Zm = (slice(max(ra - int(20 * E6), 0), rb), slice(max(xa0 - int(10 * E6), 0), min(xb0 + int(30 * E6), W_)))
        ozz = out[Zm]; a_now = np.zeros(am.shape, np.float32); a_now[Z_] = a_r * wt + am[Z_] * (1 - wt)
        dedo_ = np.maximum(a_now, am)[Zm] > .3
        osc_ = (ozz.max(2) < 95) & ~fill[Zm] & ~dedo_
        n_o, e_o, s_o, _ = cv2.connectedComponentsWithStats(osc_.astype(np.uint8))
        cerca_ = dil(dedo_, 10 * E6); claro_ = ozz.max(2) >= 95; osc_[:] = False
        for k_ in range(1, n_o):                    # solo motas: pequeñas, junto al dedo y rodeadas de claro (madera, piel)
            if s_o[k_, 4] > 220 * E6 * E6: continue
            m_ = e_o == k_
            if not (m_ & cerca_).any(): continue
            ani_ = dil(m_, 3 * E6) & ~m_
            if claro_[ani_].mean() > .6: osc_ |= m_
        if osc_.any():
            ok_ = ~dedo_ & ~fill[Zm] & (ozz.max(2) >= 95) & ~dil(osc_, 2 * E6)
            rep_ = rellena_capas(ozz, ok_.astype(np.float32), (3 * E6, 8 * E6, 20 * E6))
            w_ = cv2.GaussianBlur(dil(osc_, 1.5 * E6).astype(np.float32), (0, 0), 1.0 * E6)[..., None]
            out[Zm] = ozz * (1 - w_) + rep_ * w_
    return hechos


ESPEJO_ZONA = []


def compone6(n, F, orig, blanco, etq, pintadas):
    """El fotograma v6: fuera las cajas dibujadas, hueco tapado por zonas, cajas reales y la mano encima."""
    if not pintadas: return
    piel_v5 = piel_gruesa(mascaras(orig)[1])
    ns, es, st, _ = cv2.connectedComponentsWithStats(piel_v5.astype(np.uint8))
    kraft = np.isin(es, [k for k in range(1, ns) if st[k, 4] < 14000 * E6 * E6])
    mano = mano6(orig)
    RESTAURA = V6.get('restaura')
    if RESTAURA or DEDOS:      # 23/11 (R4): fuera de la mano el cartón blanco que se colaba entre los dedos (huecos rellenos)
        o16_ = orig.astype(np.int16); carton_ = (o16_.min(2) > 135) & (o16_.max(2) - o16_.min(2) < 25)
        mano &= ~dil(carton_, 2 * E6)
        mano = cv2.morphologyEx(mano.astype(np.uint8), cv2.MORPH_OPEN, k_el(2 * E6)).astype(bool)
    nueva = np.zeros((SH, SW), np.float32)
    for i, x0, y0, rgb, alfa, vis in pintadas:
        z = nueva[y0:y0 + alfa.shape[0], x0:x0 + alfa.shape[1]]; np.maximum(z, alfa[..., 0], out=z)
    pt = V6.get('puntas')       # [ratio, ancho] o [ratio, ancho, modos] o [ratio, ancho, modos, [de, a]]: con modos (p. ej.
    #                             ["giro"]), solo en esos tramos; con [de, a], solo en esos fotogramas del clip
    if pt and len(pt) > 2 and not any(modo(cajas[i_], n) in pt[2] for i_, *_ in pintadas): pt = None
    if pt and len(pt) > 3 and not (pt[3][0] <= n + INI <= pt[3][1]): pt = None
    quitado = puntas6(mano, orig, nueva, pt[0], pt[1]) if pt else None
    mg = V6.get('margen', 15)
    hoyo = np.zeros((SH, SW), bool)
    o16 = orig.astype(np.int16); omax = o16.max(2); omin = o16.min(2)
    neutro = (omax > 110) & ((omax - omin < 40) | (o16[..., 2] > o16[..., 0] + 8)) \
        & ~cv2.dilate(mano.astype(np.uint8), k_el(4 * E6)).astype(bool)                 # cartón gris/blanco o restos azulados (no los brillos de la camiseta)
    for i, x0, y0, rgb, alfa, vis in pintadas:
        if vis is None: continue
        sil = cv2.morphologyEx(vis.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((45, 45), np.uint8))
        cs, _ = cv2.findContours(sil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE); cv2.drawContours(sil, cs, -1, 1, -1)
        sil = cv2.dilate(sil, k_el(mg / 2)).astype(bool)
        # restos de cartón pegados (pestaña suelta, cantos en sombra): gris o blanco neutro, nunca madera ni piel
        cerca = dil(sil, 60 * E6)
        # trozos claros neutros pegados a la silueta, pero no el suelo o una pared clara que toque la caja: solo
        # trozos pequeños (contados enteros, fuera de la silueta)
        n3, e3, s3, _ = cv2.connectedComponentsWithStats((neutro & ~sil).astype(np.uint8))
        toca = np.unique(e3[dil(sil, 2) & (e3 > 0)])
        resto = np.isin(e3, [k for k in toca if s3[k, 4] < 40000 * E6 * E6]) & cerca
        resto |= kraft & dil(sil, 20 * E6)                     # el cartón kraft de la tapa dibujada, pegado a la caja
        hoyo |= cv2.dilate((sil | resto).astype(np.uint8), k_el(4 * E6)).astype(bool)
    hoyo &= ~mano
    # manchas claras sueltas junto a la caja dibujada que no son madera ni piel (fallos de la IA, p. ej. un borrón
    # azulado junto a la pestaña): también fuera
    suelto = (omax >= 110) & (o16[..., 0] - o16[..., 2] < 45) & ~cv2.dilate(mano.astype(np.uint8), k_el(4 * E6)).astype(bool) & ~hoyo
    ns_, es_, st_, _ = cv2.connectedComponentsWithStats(suelto.astype(np.uint8))
    cerca_h = dil(hoyo, 80 * E6); lejos_h = dil(hoyo, 400 * E6)
    oscuro_ = omax < 80
    peq = np.zeros_like(hoyo)
    for k in range(1, ns_):
        if st_[k, 4] >= 6000 * E6 * E6: continue
        x_, y_, w_, h_ = st_[k, :4]
        zz = (slice(max(y_ - 12, 0), y_ + h_ + 12), slice(max(x_ - 12, 0), x_ + w_ + 12))
        m_ = es_[zz] == k
        anillo_ = dil(m_, 8 * E6) & ~m_
        rodeada = oscuro_[zz][anillo_ & ~hoyo[zz]].mean() > .7 if (anillo_ & ~hoyo[zz]).any() else True
        if cerca_h[zz][m_].any() and rodeada: peq[zz] |= m_; continue
        anillo_ = anillo_                          # más lejos: solo borrones azulados sueltos sobre la camiseta
        azul = (o16[zz][m_][:, 2] > o16[zz][m_][:, 0] + 8).mean() > .5
        if azul and lejos_h[zz][m_].any() and oscuro_[zz][anillo_].mean() > .8: peq[zz] |= m_
    hoyo |= cv2.dilate(peq.astype(np.uint8), k_el(5 * E6)).astype(bool) & ~mano
    if V6.get('motas_claras'):      # 23/11 (N2): pinceladas claras sueltas de la IA, algo más lejos de la caja
        rad, area_max = V6['motas_claras']
        n_, e_, s_, _ = cv2.connectedComponentsWithStats(((omax >= 60) & ~dil(mano, 10 * E6) & ~hoyo).astype(np.uint8))
        cerca_ = dil(hoyo, rad * E6); claras = np.zeros_like(hoyo)
        for k in range(1, n_):
            if s_[k, 4] > area_max * E6 * E6 or s_[k, 4] < 20 * E6 * E6: continue
            x_, y_, w_, h_ = s_[k, :4]; r_ = int(16 * E6)
            zz = (slice(max(y_ - r_, 0), y_ + h_ + r_), slice(max(x_ - r_, 0), x_ + w_ + r_))
            m_ = e_[zz] == k
            if not cerca_[zz][m_].any(): continue
            ani_ = dil(m_, 12 * E6) & ~dil(m_, 4 * E6)
            if ani_.any() and (omax[zz][ani_] < 70).mean() > .85: claras[zz] |= m_
        if claras.any():
            print(f'  motas claras {n + INI}:', int(claras.sum()), 'px')
            hoyo |= dil(claras, 8 * E6) & ~mano
    zona = dil(hoyo | (nueva > 0), 70 * E6)
    ys, xs = np.where(zona); a0, a1, b0, b1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    Z = (slice(a0, a1), slice(b0, b1))
    I = orig.astype(np.float32)
    oscuro = omax < 80
    valido = ~cv2.dilate((hoyo | mano | kraft | cv2.dilate(blanco.astype(np.uint8), k_el(3 * E6)).astype(bool)).astype(np.uint8), k_el(6 * E6)).astype(bool)
    f_ = orig.astype(np.int16)
    pielish = (f_[..., 0] > 40) & (f_[..., 0] - f_[..., 1] > .12 * f_[..., 0]) & (f_[..., 1] - f_[..., 2] < .25 * f_[..., 0])
    fondo_ok = ~cv2.dilate(pielish.astype(np.uint8), k_el(6 * E6)).astype(bool)
    # fondo de verdad: zonas grandes que llegan al borde izquierdo o derecho del cuadro (no un trozo gris de la caja
    # dibujada dentro del torso)
    nf, ef, sf, _ = cv2.connectedComponentsWithStats((fondo_ok & ~oscuro & valido).astype(np.uint8))
    fondo_ok &= np.isin(ef, [k for k in range(1, nf) if sf[k, 4] >= 20000 * E6 * E6 and (sf[k, 0] <= 2 or sf[k, 0] + sf[k, 2] >= SW - 2)])
    if os.environ.get('CAJAS_VOLCADO'):
        np.savez_compressed(f"{os.environ['CAJAS_VOLCADO']}/v{n + INI:03d}.npz", oscuro=oscuro, valido=valido, hoyo=hoyo, fondo_ok=fondo_ok, mano=mano, nueva=nueva)
    tapa = hoyo & dil(nueva <= .5, 8 * E6)
    # costura: una banda de 12 px alrededor del hueco también se rellena y se funde poco a poco con lo de verdad
    # (así no queda la línea del canto ni la sombra de la caja dibujada)
    dist = cv2.distanceTransform((~hoyo).astype(np.uint8), cv2.DIST_L2, 5)
    anch = 12 * E6
    banda = (dist > 0) & (dist <= anch) & ~cv2.dilate((mano | blanco).astype(np.uint8), k_el(3 * E6)).astype(bool)
    relleno = hoyo | banda
    valido &= ~dil(banda, 6 * E6)
    camiseta = clase_camiseta(oscuro, valido, relleno, fondo_ok)
    G = rellena6(I, relleno, tapa | banda, valido, oscuro, camiseta, fondo_ok)[Z]
    peso = np.where(hoyo, 1.0, np.where(banda, np.clip(1 - dist / anch, 0, 1), 0.0)).astype(np.float32)[Z]
    G = G * peso[..., None] + I[Z] * (1 - peso[..., None])
    # las cajas reales: luz de la escena, algo más cálidas, degradado suave y la sombra de los dedos
    Iz = I[Z]; mz = mano[Z]
    cambio = dil(hoyo[Z] | (nueva[Z] > 0), 24 * E6).astype(np.float32)
    am, Bold = alfa_mano6(Iz, mz, cambio, bool(DEDOS))
    if quitado is not None: am *= 1 - np.clip(cv2.GaussianBlur(quitado[Z].astype(np.float32), (0, 0), .8 * E6) * 1.6, 0, 1)
    corte = np.zeros(am.shape, np.float32)                  # opción "dedos" (3): lo que se quita de las yemas cortadas
    rd = DEDOS.get('redondea') if DEDOS else None     # [x, y] o [x, y, modos]: con modos, solo en esos tramos
    if rd and len(rd) > 2 and not any(modo(cajas[i_], n) in rd[2] for i_, *_ in pintadas): rd = None
    if rd:
        rx, ry = rd[:2]; hb = (am > .5).astype(np.uint8)
        ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * int(round(rx * E6)) + 1, 2 * int(round(ry * E6)) + 1))
        op = cv2.morphologyEx(hb, cv2.MORPH_OPEN, ker).astype(bool)
        # solo el contorno de la mano que queda encima de la caja nueva (o a 6 px de su canto): las yemas
        sobre = dil(nueva[Z] > .5, 6 * E6)
        filo = hb.astype(bool) & ~cv2.erode(hb, k_el(1.5 * E6)).astype(bool) & sobre
        quita = hb.astype(bool) & ~op & dil(filo, 22 * E6) & sobre
        n_, e_, s_, _ = cv2.connectedComponentsWithStats(quita.astype(np.uint8))
        # solo esquinas (ni el polvo del borde ni trozos grandes: donde el óvalo no cabe en un dedo fino, no se toca)
        quita = np.isin(e_, [k for k in range(1, n_) if 12 * E6 * E6 <= s_[k, 4] <= rx * ry * E6 * E6])
        corte = np.clip(cv2.GaussianBlur(quita.astype(np.float32), (0, 0), 1.6 * E6) * 1.25, 0, 1) * (am > .02)
    am_s = am * (1 - corte)                                  # la mano que hace sombra
    calido = np.float32(V6.get('calido', [1, 1, 1])); sombra = V6.get('sombra', [0, 0]); deg = V6.get('degradado', 0.0)
    for i, x0, y0, rgb, alfa, vis in pintadas:
        h, w_ = alfa.shape[:2]; yy, xx = y0 - a0, x0 - b0
        Rz = G[yy:yy + h, xx:xx + w_]
        luz = (blancos[i][n] / PAPEL * 1.04) if not np.isnan(blancos[i][n]).any() else np.float32([.84, .8, .78])
        if V6.get('aclarar'):
            gam, techo = V6['aclarar']
            Lf = float(PAPEL * np.mean(luz * calido))                                   # luz del frente, 0-255
            luz = luz * (min(255 * (Lf / 255) ** gam, max(techo, Lf)) / Lf)
        cap = np.dstack([rgb * (luz * calido), alfa])
        if deg:
            ya = np.where(alfa[..., 0].max(1) > .5)[0]
            if len(ya):
                v = np.clip((np.arange(h, dtype=np.float32) - ya[0]) / max(ya[-1] - ya[0], 1), 0, 1)
                cap[..., :3] *= (1 + deg / 2 - deg * v)[:, None, None]
        cap = cv2.GaussianBlur(cap, (0, 0), V6.get('desenfoque', 0.8) * E6)
        az = am_s[yy:yy + h, xx:xx + w_]
        s1 = cv2.GaussianBlur(np.roll(az, (int(round(6 * E6)), int(round(4 * E6))), (0, 1)), (0, 0), 6 * E6)
        s2 = cv2.GaussianBlur(az, (0, 0), 22 * E6)
        s0 = cv2.GaussianBlur(az, (0, 0), 2.5 * E6) * DEDOS.get('contacto', 0) if DEDOS else 0
        som = np.clip(s1 * sombra[0] + s2 * sombra[1] + s0, 0, .6)[..., None]
        g = np.random.default_rng(n * 7 + i).normal(0, 1.4, (h, w_, 1)).astype(np.float32)
        G[yy:yy + h, xx:xx + w_] = Rz * (1 - cap[..., 3:]) + np.clip(cap[..., :3] * (1 - som) + g * cap[..., 3:], 0, 255)
    # la mano encima: donde el borde del dedo mezclaba piel y fondo viejo, se cambia el fondo viejo por el nuevo
    hz = hoyo[Z]
    c = np.maximum(nueva[Z], cv2.GaussianBlur(hz.astype(np.float32), (0, 0), 2 * E6))[..., None]
    NB = c * G + (1 - c) * Bold
    w = np.clip((am - .04) / .2, 0, 1)[..., None]
    out = (1 - w) * G + w * (Iz + (1 - am[..., None]) * (NB - Bold))
    # costura suave del hueco con lo que no cambia
    borde = np.maximum(cv2.GaussianBlur((hz | (nueva[Z] > 0) | (am > .02)).astype(np.float32), (0, 0), 1.5 * E6), peso)[..., None]
    out = borde * out + (1 - borde) * Iz
    out_pre = out.copy() if ESPEJO else None
    if DEDOS:     # (3) las yemas cortadas en recta, redondeadas: ahí se ve la caja nueva, el relleno o la camiseta
        c_ = np.maximum(nueva[Z], cv2.GaussianBlur(hz.astype(np.float32), (0, 0), 2 * E6))[..., None]
        out = out * (1 - corte[..., None]) + (c_ * G + (1 - c_) * FONDO_FUERA[0]) * corte[..., None]
    if RESTAURA:
        # 23/11 (R4): el borde de la mano que tocaba la caja dibujada y ahora da al relleno (por encima de la caja nueva,
        # que es más baja) era un corte recto: dedo plano y claro hasta el filo. Se redondean las esquinas (apertura de
        # 6 px a 4K, solo en ese borde) y la piel cae de luz en los últimos 7 px, como el canto de un dedo de verdad.
        fill_ = (hoyo[Z] & (nueva[Z] < .05)).astype(np.uint8)
        cerca_ = dil(fill_, 10 * E6); dentro = am > .5
        ab = cv2.morphologyEx(dentro.astype(np.uint8), cv2.MORPH_OPEN, k_el(6 * E6)).astype(bool)
        corta = cv2.GaussianBlur((dentro & ~ab & cerca_).astype(np.float32), (0, 0), 1.0 * E6)[..., None]
        d_ = cv2.distanceTransform((1 - fill_).astype(np.uint8), cv2.DIST_L2, 5)
        cae = np.where(dentro & (d_ < 7 * E6), 0.74 + 0.26 * np.clip(d_ / (7 * E6), 0, 1) ** 0.8, 1.0).astype(np.float32)
        cae = cv2.GaussianBlur(cae, (0, 0), 1.0 * E6)[..., None]
        out = (out * cae) * (1 - corta) + G * corta
    if ESPEJO:
        ESPEJO_ZONA.clear()
        hechos = espejo6(out, G, am, Iz, hoyo[Z] & (nueva[Z] < .05), nueva[Z], out_pre)
        if hechos: print(f'  espejo {n + INI}: (punta, corte, abajo, lado)', hechos)
    out = np.clip(out, 0, 255).round().astype(np.uint8)
    if V6.get('motas', True):
        quita_motas(out, (am > .3) & (cambio > 0))
    F[Z] = out
    if DEP and SOLO:
        os.makedirs(DEP, exist_ok=True)
        cv2.imwrite(f'{DEP}/m{n + INI:03d}.png', np.dstack([mz * 255, (am * 255).astype(np.uint8), hz * 255, camiseta[Z] * 120 + 60]).astype(np.uint8)[..., :3])
        cv2.imwrite(f'{DEP}/k{n + INI:03d}.png', (camiseta[Z] * 200 + hz * 55).astype(np.uint8))
        if DEDOS or ESPEJO:
            cv2.imwrite(f'{DEP}/o{n + INI:03d}.png', cv2.cvtColor(orig, cv2.COLOR_RGB2BGR))
            np.savez_compressed(f'{DEP}/d{n + INI:03d}.npz', a0=a0, b0=b0, am=am, corte=corte, mz=mz, hz=hz,
                                nueva=nueva[Z],
                                quitado=quitado[Z] if quitado is not None else 0)


modelos = {}
for c in cajas:
    if c['modelo'] not in modelos: modelos[c['modelo']] = Caja(c['modelo'], TEX)
FOTO = salida.lower().endswith('.png')
LUZ_KW = dict(zip(('amb', 'dif'), V6['ambiente'])) if (V6 and V6.get('ambiente')) else {}
DESPL = [None]                                           # de dónde se copia la tela (se decide en el primer fotograma)
if DEDOS:
    # opción "dedos" (1): cuánto hay que acercar cada mano a su caja; se mide en todos los fotogramas antes de pintar
    # (con --solo, solo en los de alrededor) para que el movimiento sea suave en el tiempo
    from scipy.ndimage import gaussian_filter1d, maximum_filter1d
    med = {}; med_n = {}
    for n, fr in enumerate(fotogramas()):
        if SOLO and not any(abs(n + INI - s_) <= 8 for s_ in SOLO): continue
        F0 = np.ascontiguousarray(cv2.resize(fr, (AW, SH), interpolation=cv2.INTER_LANCZOS4)[:, OFF:OFF + SW])
        mano0 = mano6(F0); o16_ = F0.astype(np.int16)
        mano0 &= ~dil((o16_.min(2) > 135) & (o16_.max(2) - o16_.min(2) < 25), 2 * E6)
        mano0 = cv2.morphologyEx(mano0.astype(np.uint8), cv2.MORPH_OPEN, k_el(2 * E6)).astype(bool)
        for i, c in enumerate(cajas):
            if modo(c, n) is None or np.isnan(base[i][n]).any() or np.isnan(escala[i][n]): continue
            caja = modelos[c['modelo']]
            R, t = postura(caja, a_salida(base[i][n]), escala[i][n], giros[i][n], incl[i][n], c.get('sentido', 1))
            x0, y0, rgb, alfa = caja_en_zona(caja, R, t, **LUZ_KW)
            bm = np.zeros((SH, SW), bool); bm[y0:y0 + alfa.shape[0], x0:x0 + alfa.shape[1]] = alfa[..., 0] > .5
            for lado in (-1, 1):
                r = mide_lado(bm, mano0, lado)
                if r is not None: med[(i, lado, n)] = r; med_n.setdefault((i, lado), set()).add(n)
    sol, dmax = DEDOS.get('solape', 14) * E6, DEDOS.get('max', 30) * E6
    for i in range(len(cajas)):
        for lado in (-1, 1):
            ks = [n for n in range(N) if (i, lado, n) in med]
            if not ks: continue
            need = np.zeros(N); arr = np.full((N, 2), np.nan); fil = np.zeros((N, SH), np.float32)
            for n in ks:
                al, f_, a_, b_ = med[(i, lado, n)]
                need[n] = np.clip(sol - al, 0, dmax); arr[n] = (a_, b_); fil[n] = f_
            idx = np.array(ks)
            for n in range(N):                       # sin medida: las filas del fotograma medido más cercano
                if n not in med_n.get((i, lado), ()): fil[n] = fil[idx[np.argmin(np.abs(idx - n))]]
            print('dedos: caja', i, 'lado', lado, '| alcance de las puntas (px):',
                  ' '.join(f'{n + INI}:{med[(i, lado, n)][0]:.0f}' for n in ks))
            if need.max() < .5: continue
            d = gaussian_filter1d(maximum_filter1d(need, 5, mode='nearest'), 1.5, mode='nearest')
            for k in range(2): arr[:, k] = gaussian_filter1d(np.interp(np.arange(N), idx, arr[idx, k]), 1.5, mode='nearest')
            fil = gaussian_filter1d(fil, 1.5, axis=0, mode='nearest')
            MANOS[(i, lado)] = {'d': d, 'a': arr[:, 0], 'b': arr[:, 1], 'filas': fil}
            print('   acercar (px):', ' '.join(f'{n + INI}:{d[n]:.0f}' for n in range(N) if d[n] >= .5))
enc = None if (FOTO or SOLO) else subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{SW}x{SH}', '-r', '24', '-i', '-',
                                          '-an', '-c:v', 'libx264', '-crf', str((V6 or {}).get('crf', 10)), '-preset', 'medium', '-pix_fmt', 'yuv420p', '-r', '24', salida], stdin=subprocess.PIPE)
for n, fr in enumerate(fotogramas()):
    if SOLO and n + INI not in SOLO: continue
    F = np.ascontiguousarray(cv2.resize(fr, (AW, SH), interpolation=cv2.INTER_LANCZOS4)[:, OFF:OFF + SW])
    if MANOS: F = acerca_manos(F, n)                    # opción "dedos" (1)
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
        x0, y0, rgb, alfa = caja_en_zona(caja, R, t, **LUZ_KW)
        vis = componente(etq, a_salida(base[i][n]) - [0, escala[i][n] * .5], 90)
        pintadas.append((i, x0, y0, rgb, alfa, vis))
    if V6:
        compone6(n, F, orig, blanco, etq, pintadas)
    else:
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
    if SOLO:
        os.makedirs(DEP or '.', exist_ok=True)
        cv2.imwrite(f'{DEP or "."}/f{n + INI:03d}.png', cv2.cvtColor(F, cv2.COLOR_RGB2BGR)); continue
    enc.stdin.write(F.tobytes())
    if DEP and n % 4 == 0:
        os.makedirs(DEP, exist_ok=True); cv2.imwrite(f'{DEP}/s{n + INI:03d}.jpg', cv2.cvtColor(F, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 90])
if enc: enc.stdin.close(); enc.wait()
print('ok', salida)
