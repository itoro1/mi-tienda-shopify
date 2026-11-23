# -*- coding: utf-8 -*-
"""Recorte del pack (caja del cargador + caja del cable USB-C) para el anuncio.

v4 (TAMAÑOS REALES). Medidas de las cajas (fotos/caja3d/medidas.json):
cargador 79 x 85,6 x 33 mm, cable 67 x 65 x 24 mm. En la foto de estudio
(pillatumovil/fotos/estudio/ps-estudio-portada.jpg, «Pack A») la caja del cable
está dibujada tan alta como la del cargador y el cargador lleva una franja de
cartón vacío de más, así que:
  * Cargador: luz, silueta, lateral y pestaña de la foto de estudio; se le
    quitan dos franjas horizontales vacías (FRANJAS_CARGADOR) y su frontal se
    pinta con la cara REAL escaneada (fotos/caja3d/cargador-frente.png) con la
    luz de la foto (CARGADOR_CARA_REAL; False = frontal de la foto, recortado).
  * Cable: caja NUEVA con las proporciones reales respecto al cargador
    (67/79 de ancho, 65/85,6 de alto, 24/33 de fondo), en la misma perspectiva
    y sobre el mismo suelo: frontal = cara REAL (fotos/caja3d/cable-frente.png)
    con la luz de la foto (incluida la sombra que le deja el cargador), lateral
    y pestaña de la foto de estudio, encogidos (pestaña real ~36 x 16 mm).
  * Nada generado con IA; nada de fotos/cine/.

v5 (retoques sobre la v4, comparados con fotos/reales/cajas-frente-usb-c.jpg):
  * Pestaña del cargador x0,87 entera (0,66 -> 0,57 del frontal; ojal 0,47 ->
    0,41), mismo centro: _escalar_pestana_cargador.
  * Pestaña del cable: costados estrechados (0,59 -> 0,55; ojal 0,424 -> 0,415)
    y sin el «pie» de 1 px en la base de su borde derecho (_caja_cable).
  * Cara lateral del cargador: sin escalón de luz en las dos costuras de las
    franjas quitadas (degradado rehecho, GANANCIA_COSTURA_*).

v3 (se conserva en _recortar_v3, de ahí salen silueta, laterales y pestañas):
  * Silueta: umbral local sobre la luminancia ampliada x4, contorno suavizado y
    vuelto a rasterizar con supermuestreo -> bordes antialias limpios.
  * Base: cortada por las rectas medidas del borde inferior de cada cara.
  * Color del borde: se empuja el color del interior hacia fuera.
  * Laterales: cartón blanco con luz cálida suave (no dorado).

recortar(escala) -> (RGBA PIL, info) con info['apoyos'] = línea de apoyo de cada
caja (coordenadas del recorte ya escalado) e info['par'] = bordes del par en la
foto (PAR_X0, PAR_X1). medidas() da las proporciones del par.
"""
from PIL import Image
import numpy as np
import cv2

SRC = '/home/user/mi-tienda-shopify/pillatumovil/fotos/estudio/ps-estudio-portada.jpg'

# zona de trabajo en la foto original
RX0, RY0, RX1, RY1 = 940, 220, 1850, 862
DEBUG = False
F = 4  # sobremuestreo para la silueta

# geometría medida en la foto (px de la foto original)
#   frontal: borde inferior y = a + b*x ; lateral: recta entre dos puntos
CAJAS = {
    'adaptador': dict(
        x_izq=965.6, x_pliegue=1329.9, x_der=1401.6,
        frontal_inf=(776.65, 0.04326),
        lateral_inf=((1329.9, 834.3), (1401.6, 818.0)),
        corte_x=(950, 1404.5),
        izq=(965.58, 0.003644), der=(1401.49, -0.00032), sup=(359.59, -0.01754),
    ),
    'cable': dict(
        x_izq=1417.0, x_pliegue=1758.7, x_der=1823.6,
        frontal_inf=(719.03, 0.07239),
        lateral_inf=((1758.7, 845.5), (1823.6, 830.0)),
        corte_x=(1409.5, 1830),
        izq=(1414.0, 0.00678), der=(1823.21, 0.00054), sup=(371.74, -0.02403),
    ),
}


def _base_poli(c, sube=0.6):
    """Polilínea de la base (coordenadas de la foto). `sube` px por encima de
    la transición blanco->oscuro para no arrastrar la línea negra original."""
    a, b = c['frontal_inf']
    x0 = c['corte_x'][0]
    pts = [(x0, a + b * x0)]
    xp = c['x_pliegue']
    pts.append((xp, a + b * xp))
    (lx0, ly0), (lx1, ly1) = c['lateral_inf']
    # lateral: recta desde el pliegue (a la altura de la frontal) hasta el fondo
    yp = a + b * xp
    dy = (ly1 - ly0)
    pts.append((lx1, yp + dy))
    pts.append((c['corte_x'][1], yp + dy + (c['corte_x'][1] - lx1) * dy / (lx1 - lx0)))
    return [(x, y - sube) for x, y in pts]


def _mascara_x4():
    a = np.asarray(Image.open(SRC).convert('RGB')).astype(np.float32)
    sub = a[RY0:RY1, RX0:RX1]
    L = sub @ np.array([0.30, 0.59, 0.11], np.float32)
    L = cv2.GaussianBlur(L, (0, 0), 0.6)
    lmax = cv2.dilate(L, np.ones((9, 9), np.uint8))
    lmin = cv2.erode(L, np.ones((9, 9), np.uint8))
    h, w = L.shape
    L4 = cv2.resize(L, (w * F, h * F), interpolation=cv2.INTER_CUBIC)
    thr4 = cv2.resize((lmax + lmin) / 2, (w * F, h * F), interpolation=cv2.INTER_LINEAR)
    con4 = cv2.resize(lmax - lmin, (w * F, h * F), interpolation=cv2.INTER_LINEAR)
    thr4 = np.minimum(thr4, 72.0)
    fg = np.where(con4 > 35, L4 > thr4, L4 > 42).astype(np.uint8)
    return sub, fg


def _limpiar_caja(fg, c):
    """Máscara x4 de una caja: corte lateral, corte de base, componente mayor,
    huecos rellenos salvo la ranura de la pestaña."""
    h, w = fg.shape
    m = fg.copy()
    xa, xb = c['corte_x']
    xa4, xb4 = int(round((xa - RX0) * F)), int(round((xb - RX0) * F))
    m[:, :max(0, xa4)] = 0
    m[:, xb4:] = 0
    # base
    poli = _base_poli(c)
    abajo = np.zeros_like(m)
    pts = [((x - RX0) * F, (y - RY0) * F) for x, y in poli]
    pts = [(pts[0][0] - 40, pts[0][1])] + pts + [(pts[-1][0] + 40, pts[-1][1])]
    pts += [(pts[-1][0], h + 10), (pts[0][0], h + 10)]
    cv2.fillPoly(abajo, [np.round(np.array(pts) * 16).astype(np.int32)], 1, lineType=cv2.LINE_8, shift=4)
    m[abajo > 0] = 0
    # bordes rectos: los laterales de la caja son rectas medidas; el cuerpo
    # (por debajo del borde superior) es macizo -> sin mordiscos ni bultos
    yo = RY0 + (np.arange(h, dtype=np.float32)[:, None] + 0.5) / F
    xo = RX0 + (np.arange(w, dtype=np.float32)[None, :] + 0.5) / F
    dentro = (xo >= c['izq'][0] + c['izq'][1] * yo) & (xo <= c['der'][0] + c['der'][1] * yo)
    cuerpo = dentro & (yo >= c['sup'][0] + c['sup'][1] * xo + 5) & (abajo == 0)
    m = ((m > 0) & dentro) | cuerpo
    m = m.astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    if n > 1:
        big = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
        m = (lab == big).astype(np.uint8)
    inv = (1 - m).astype(np.uint8)
    n, lab, st, cen = cv2.connectedComponentsWithStats(inv, 4)
    borde = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
    y_tab = (333 - RY0) * F  # la ranura de la pestaña queda por encima de aquí
    for i in range(1, n):
        if i in borde:
            continue
        ybot = st[i, cv2.CC_STAT_TOP] + st[i, cv2.CC_STAT_HEIGHT]
        area = st[i, cv2.CC_STAT_AREA]
        es_ranura = ybot < y_tab and area > 2000
        if DEBUG:
            print('hueco', i, st[i], ybot, y_tab, es_ranura)
        if not es_ranura:
            m[lab == i] = 1
    return m


def _contornos_suaves(m, sigma):
    cs, jer = cv2.findContours(m, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    out = []
    for i, c in enumerate(cs):
        p = c[:, 0, :].astype(np.float32)
        if len(p) < 20:
            continue
        # suavizado circular a lo largo del contorno
        k = int(sigma * 3)
        ext = np.concatenate([p[-k:], p, p[:k]], 0)
        g = np.exp(-0.5 * (np.arange(-k, k + 1) / sigma) ** 2)
        g /= g.sum()
        xs = np.convolve(ext[:, 0], g, mode='same')[k:-k]
        ys = np.convolve(ext[:, 1], g, mode='same')[k:-k]
        # +0.5: centro del píxel x4
        es_hueco = jer[0][i][3] >= 0
        out.append((np.stack([xs + 0.5, ys + 0.5], 1), es_hueco))
    return out


def _rasterizar(contornos, escala, size, ss=4):
    """Contornos (coords x4 del recorte) -> alfa antialias al tamaño final."""
    W, H = size
    acc = np.zeros((H * ss, W * ss), np.uint8)
    k = escala / F * ss
    # primero exteriores, luego huecos
    for es_hueco in (False, True):
        for p, h in contornos:
            if h != es_hueco:
                continue
            q = np.round(p * k * 16).astype(np.int32)
            cv2.fillPoly(acc, [q], 0 if h else 255, lineType=cv2.LINE_8, shift=4)
    return cv2.resize(acc.astype(np.float32) / 255, (W, H), interpolation=cv2.INTER_AREA)


Y_LATERAL = 190.0                      # luminancia media de la cara lateral
TINTE_LATERAL = (1.02, 1.0, 0.965)    # blanco con luz cálida muy suave (R-B ≈ 11)


def _lateral_blanco(rgb, region, banda, escala):
    """Cartón blanco con luz cálida suave (no dorado). region: alfa 0..1 de la
    cara lateral; banda: el filo del pliegue (solo se le quita el amarillo)."""
    Y = rgb @ np.array([0.30, 0.59, 0.11], np.float32)
    sel = region > 0.5
    ref = np.median(Y[sel]) if sel.any() else 120
    gan = Y_LATERAL / max(ref, 1)
    # textura algo más fina (la ganancia la aumentaría)
    Ys = 0.55 * Y + 0.45 * cv2.GaussianBlur(Y, (0, 0), 1.4 * escala)
    tinte = np.array(TINTE_LATERAL, np.float32)
    Yn = Ys * gan
    # rodilla suave: los brillos no se queman (si no, el filo sale amarillo)
    tope, rod = 226.0, 196.0
    Yn = np.where(Yn > rod, rod + (tope - rod) * (1 - np.exp(-(Yn - rod) / (tope - rod))), Yn)
    nuevo = np.clip(Yn[..., None] * tinte, 0, 255)
    out = rgb * (1 - region[..., None]) + nuevo * region[..., None]
    # pliegue: mismo brillo, color casi neutro con un toque cálido
    Yo = out @ np.array([0.30, 0.59, 0.11], np.float32)
    neutro = np.clip(Yo[..., None] * tinte, 0, 255)
    return out * (1 - banda[..., None]) + neutro * banda[..., None]


def _recortar_v3(escala=1.0):
    """Recorte v3 de las DOS cajas tal como salen en la foto (la del cable aún
    con su tamaño de la foto). Devuelve también el alfa de cada caja."""
    sub, fg = _mascara_x4()
    h, w = sub.shape[:2]
    W, H = int(round(w * escala)), int(round(h * escala))
    rgb = cv2.resize(sub, (W, H), interpolation=cv2.INTER_CUBIC if escala > 1 else cv2.INTER_AREA)
    alfa = np.zeros((H, W), np.float32)
    bases = []
    alfas = {}
    lat = np.zeros((H, W), np.float32)
    ban = np.zeros((H, W), np.float32)
    for nombre, c in CAJAS.items():
        m = _limpiar_caja(fg, c)
        cont = _contornos_suaves(m, sigma=3.2)
        a = _rasterizar(cont, escala, (W, H))
        alfa = np.maximum(alfa, a)
        alfas[nombre] = a
        bases.append([((x - RX0) * escala, (y - RY0) * escala) for x, y in _base_poli(c)])
        if nombre == 'adaptador':
            xs = (np.arange(W) / escala + RX0)
            t = np.clip((xs - (c['x_pliegue'] + 0.6)) / 1.4, 0, 1)
            lat_ad = np.broadcast_to(t[None, :], (H, W)) * a
        if nombre == 'cable':
            # cara lateral: a la derecha del pliegue (borde suave de 1 px)
            xs = (np.arange(W) / escala + RX0)
            t = np.clip((xs - (c['x_pliegue'] + 0.8)) / 1.6, 0, 1)
            lat = np.maximum(lat, np.broadcast_to(t[None, :], (H, W)) * a)
            tb = np.clip((xs - (c['x_pliegue'] - 4.0)) / 1.5, 0, 1) * (1 - t)
            ban = np.maximum(ban, np.broadcast_to(tb[None, :], (H, W)) * a)

    # color limpio en el borde: media de los vecinos del interior
    r = max(2, int(round(1.6 * escala)))
    interior = cv2.erode((alfa > 0.995).astype(np.uint8), np.ones((3, 3), np.uint8), iterations=r).astype(np.float32)
    num = cv2.GaussianBlur(rgb * interior[..., None], (0, 0), 1.2 * escala + 0.8)
    den = cv2.GaussianBlur(interior, (0, 0), 1.2 * escala + 0.8)[..., None]
    empuje = num / np.maximum(den, 1e-4)
    banda = ((alfa > 0.0) & (interior < 0.5) & (den[..., 0] > 1e-3))[..., None]
    rgb = np.where(banda, empuje, rgb)

    rgb = _lateral_blanco(rgb, lat, ban, escala)
    # lateral del cargador (en sombra, entre las dos cajas): gris neutro-cálido
    # de cartón blanco en sombra, sin el tono marrón-rosado de la foto
    Y = rgb @ np.array([0.30, 0.59, 0.11], np.float32)
    # toque de rebote cálido (la luz viene del mismo lado que en el cable)
    gris = np.clip((Y * 1.08)[..., None] * np.array([1.035, 1.0, 0.955], np.float32), 0, 255)
    rgb = rgb * (1 - lat_ad[..., None]) + gris * lat_ad[..., None]

    out = np.dstack([np.clip(rgb, 0, 255), np.clip(alfa, 0, 1) * 255]).astype(np.uint8)
    # línea de apoyo de cada caja, solo entre sus bordes izquierdo y derecho
    apoyos = []
    for n, c in CAJAS.items():
        poli = _base_poli(c, sube=0.0)
        a, b = c['frontal_inf']
        y0 = a + b * c['x_izq']
        xi = c['izq'][0] + c['izq'][1] * y0
        (lx0, ly0), (lx1, ly1) = c['lateral_inf']
        xp = c['x_pliegue']; yp = a + b * xp
        pend = (ly1 - ly0) / (lx1 - lx0)
        xd = c['der'][0] + c['der'][1] * (yp + pend * (c['x_der'] - xp))
        pts = [(xi, a + b * xi), (xp, yp), (xd, yp + pend * (xd - xp))]
        apoyos.append([((x - RX0) * escala, (y - RY0) * escala) for x, y in pts])
    info = dict(bases=bases, apoyos=apoyos, escala=escala, origen=(RX0, RY0),
                cajas={n: dict(x_izq=(c['x_izq'] - RX0) * escala, x_der=(c['x_der'] - RX0) * escala,
                               x_pliegue=(c['x_pliegue'] - RX0) * escala) for n, c in CAJAS.items()})
    info['alfas'] = alfas
    return Image.fromarray(out, 'RGBA'), info


# =====================================================================
# v4: TAMAÑOS REALES
# =====================================================================
# En la foto de estudio la caja del cable está dibujada tan alta como la del
# cargador (y un 10 % más ancha de lo que le toca), y la del cargador tiene una
# franja de cartón vacío de más bajo el dibujo del cargador. Medidas reales
# (fotos/caja3d/medidas.json), ancho x alto x fondo en mm:
MM_CARGADOR = (79.0, 85.6, 33.0)
MM_CABLE = (67.0, 65.0, 24.0)

# --- cargador: se quitan dos franjas horizontales de cartón VACÍO (fracciones
#     del alto de la cara, medidas desde arriba) -> el frontal pasa de 0,75 a
#     0,82 aparente (0,90-0,92 real una vez descontado el escorzo de 23-26°).
#     Las dos franjas son cartón liso también en el frontal de la foto (por si
#     CARGADOR_CARA_REAL = False): nada impreso se toca.
FRANJAS_CARGADOR = [(0.030, 0.062), (0.929, 0.985)]
FUNDIDO_FRANJA = 1.0          # px de la foto a cada lado de la costura
# v5: en la cara LATERAL (en sombra) la franja quitada se llevaba parte del
# degradado vertical de oclusión y dejaba un escalón de 15-20 niveles. Se
# rehace el degradado: a cada lado de la costura se aplica una ganancia que
# iguala los dos lados en la costura y vuelve a 1 a GANANCIA_COSTURA_PX px de
# la foto. Fracción de la corrección que va ENCIMA de la costura (el resto,
# debajo): franja de arriba 0,5 (repartida); franja de abajo 1,0 (lo de debajo
# es el pie de la caja, que se queda tan oscuro como en la foto).
GANANCIA_COSTURA_PX = 11.0
GANANCIA_COSTURA_ARRIBA = [0.5, 1.0]

# v5: pestaña del cargador. La de la foto de estudio es un 15 % más grande que
# la real (ocupa 0,66 del ancho del frontal y el ojal 0,47; en la caja real
# 0,57 y 0,40). Se escala entera (forma intacta) con centro en el medio de su
# base, así sigue igual de desplazada a la derecha. Medidas en la foto:
PESTANA_CARGADOR_ESCALA = 0.87
PESTANA_CARGADOR_X = (1080.0, 1318.5)        # bordes izquierdo y derecho de la pestaña
PESTANA_CARGADOR_REF = ((1052.0, 1072.0), (1322.0, 1327.0))   # columnas de solo caja a cada lado

AD = CAJAS['adaptador']
AD_SUP = AD['sup']                         # y = a + b x (borde superior frontal)
AD_INF = AD['frontal_inf']                 # y = a + b x (borde inferior frontal)
AD_LAT_SUP = ((1329.9, 336.27), (1401.6, 340.5))   # borde superior del lateral
AD_LAT_INF = AD['lateral_inf']


def _recta(p, q, x):
    (x0, y0), (x1, y1) = p, q
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)


def _cara_cargador(xp):
    """(arriba, alto) de la cara del cargador en la columna xp (px de la foto)."""
    xp = np.asarray(xp, np.float64)
    pl = AD['x_pliegue']
    top_f = AD_SUP[0] + AD_SUP[1] * xp
    bot_f = AD_INF[0] + AD_INF[1] * xp
    top_l = _recta(*AD_LAT_SUP, xp)
    bot_l = _recta(*AD_LAT_INF, xp)
    top = np.where(xp <= pl, top_f, top_l)
    bot = np.where(xp <= pl, bot_f, bot_l)
    return top, bot - top


def _alto_cargador(xp):
    return _cara_cargador(xp)[1] * (1 - sum(b - a for a, b in FRANJAS_CARGADOR))


def _quitar_franja(arr, escala, fa, fb, x_hasta, arriba_frac=0.5):
    """Quita de cada columna (hasta x_hasta, px de la foto) la franja de la cara
    entre las fracciones fa y fb de su alto; lo de encima baja. Fundido de
    FUNDIDO_FRANJA px en la costura (solo cartón liso a ambos lados). En la cara
    lateral, además, ganancia a cada lado de la costura (ver GANANCIA_COSTURA_PX)."""
    H, W = arr.shape[:2]
    xp = RX0 + (np.arange(W) + 0.5) / escala
    top, alto = _cara_cargador(xp)
    a = ((top + fa * alto) - RY0) * escala - 0.5     # fila (px recorte)
    b = ((top + fb * alto) - RY0) * escala - 0.5
    d = np.where(xp <= x_hasta, b - a, 0.0).astype(np.float32)
    b = b.astype(np.float32)
    ys = np.arange(H, dtype=np.float32)[:, None]
    mx = np.broadcast_to(np.arange(W, dtype=np.float32)[None, :], (H, W))
    arriba = cv2.remap(arr, mx, (ys - d[None, :]).astype(np.float32), cv2.INTER_LINEAR,
                       borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    w = FUNDIDO_FRANJA * escala

    # --- cara lateral: el escalón de luz de la costura se reparte en un degradado
    pl, xd = AD['x_pliegue'], AD['x_der']
    lat = np.clip((xp - (pl + 0.6)) / 1.4, 0, 1) * np.clip((xd - 0.5 - xp) / 1.0, 0, 1)
    lat = np.where(xp <= x_hasta, lat, 0.0).astype(np.float32)
    if lat.max() > 0:
        n = max(2.0, 2.0 * escala)                      # filas a cada lado para medir
        lum = np.array([0.30, 0.59, 0.11], np.float32)
        cols = np.nonzero(lat > 0)[0]

        def media(img, desde, hasta):
            """Luminancia media (premultiplicada) de cada columna entre dos filas (px recorte)."""
            out = np.zeros(W, np.float32)
            for x in cols:
                r0, r1 = int(np.floor(desde[x])), int(np.ceil(hasta[x]))
                r0, r1 = max(0, r0), min(H, max(r0 + 1, r1))
                out[x] = (img[r0:r1, x, :3] @ lum).mean()
            return out
        # justo encima y justo debajo de la costura (fuera del fundido), contenido continuo
        m_arr = media(arriba, b - w - n, b + w + n)     # lo que baja (de encima de la franja)
        m_aba = media(arr, b - w - n, b + w + n)        # lo que se queda (de debajo de la franja)
        # solo columnas de lateral pleno; suavizado horizontal y extendido a los bordes
        ok = (lat > 0.99) & (xp > pl + 3) & (xp < xd - 3) & (m_arr > 1) & (m_aba > 1)
        r = np.where(ok, np.log(np.maximum(m_aba, 1) / np.maximum(m_arr, 1)), 0).astype(np.float32)
        sig = 2.0 * escala
        num = cv2.GaussianBlur(r[None, :], (0, 0), sigmaX=sig, sigmaY=0.01)[0]
        den = cv2.GaussianBlur(ok.astype(np.float32)[None, :], (0, 0), sigmaX=sig, sigmaY=0.01)[0]
        r = np.where(den > 1e-3, num / np.maximum(den, 1e-6), 0)
        idx = np.nonzero(ok)[0]
        if len(idx):
            r[:idx[0]] = r[idx[0]]
            r[idx[-1] + 1:] = r[idx[-1]]
        r = (r * lat).astype(np.float32)
        D = GANANCIA_COSTURA_PX * escala
        rampa = np.clip(1 - (np.abs(ys - b[None, :]) - w) / (D - w), 0, 1)
        rampa = rampa * rampa * (3 - 2 * rampa)
        g_arr = np.exp(arriba_frac * r[None, :] * rampa)          # lo de encima, hacia lo de debajo
        g_aba = np.exp(-(1 - arriba_frac) * r[None, :] * rampa)   # lo de debajo, hacia lo de encima
        arriba = np.concatenate([arriba[..., :3] * g_arr[..., None], arriba[..., 3:]], 2)
        arr = np.concatenate([arr[..., :3] * g_aba[..., None], arr[..., 3:]], 2)

    t = np.clip((ys - (b[None, :] - w)) / (2 * w), 0, 1)
    t = t * t * (3 - 2 * t)
    t = np.where(d[None, :] > 0, t, 1.0)
    return arriba * (1 - t[..., None]) + arr * t[..., None]


def _escalar_pestana_cargador(ad, escala, s=PESTANA_CARGADOR_ESCALA):
    """Escala la pestaña del cargador (premultiplicado HxWx4, recorte v3) por s,
    con centro en el medio de su base (sobre el borde superior de la caja). El
    borde de la caja que la pestaña tapaba se rehace con la recta medida a sus
    dos lados (mismo antialias)."""
    if abs(s - 1) < 1e-6:
        return ad
    H, W = ad.shape[:2]
    A = ad[..., 3]
    c = lambda xp: (xp - RX0) * escala            # foto -> px recorte (continuo)
    # borde superior de la caja a cada lado de la pestaña (filas por cobertura)
    y0r, y1r = int((318 - RY0) * escala), int((352 - RY0) * escala)
    pts = []
    for xa, xb in PESTANA_CARGADOR_REF:
        cols = np.arange(int(np.ceil(c(xa))), int(np.floor(c(xb))))
        e_ = y1r - A[y0r:y1r, cols].sum(0)        # fila donde empieza la caja (borde de píxel)
        pts.append(((cols + 0.5).mean(), e_.mean()))
    (xl, el), (xr, er) = pts
    borde = lambda x: el + (er - el) * (x - xl) / (xr - xl)
    xs = np.arange(W, dtype=np.float32) + 0.5
    e = borde(xs).astype(np.float32)                  # fila del borde por columna
    ys = np.arange(H, dtype=np.float32)[:, None] + 0.5

    # zona de la pestaña: sus columnas (con margen) y por encima del borde + 3 px
    x0, x1 = PESTANA_CARGADOR_REF[0][1] + 1, PESTANA_CARGADOR_REF[1][0] - 1
    zx = ((xs >= c(x0)) & (xs <= c(x1)))[None, :]
    zona = zx & (ys < e[None, :] + 3 * escala)

    # capa pestaña: por debajo de (borde - 2,5 px) se repite la fila de (borde - 2,5 px):
    # costados rectos hasta dentro de la caja, sin nada del borde de la caja
    fila = np.clip(np.floor(e - 2.5 * escala), 0, H - 1).astype(np.int32)
    yi = np.minimum(np.arange(H)[:, None], fila[None, :])
    xi = np.broadcast_to(np.arange(W)[None, :], (H, W))
    Tp = ad[yi, xi] * (zx & (ys < e[None, :] + 4 * escala))[..., None]
    Tp = Tp.astype(np.float32)
    # escala con centro en el medio de la base (coordenadas de píxel de OpenCV)
    xc = c(0.5 * sum(PESTANA_CARGADOR_X)) - 0.5
    yc = borde(xc + 0.5) - 0.5
    M = np.float32([[s, 0, xc * (1 - s)], [0, s, yc * (1 - s)]])
    Ts = cv2.warpAffine(Tp, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    # caja sola: borde con la cobertura del antialias de la recta; color del
    # cartón de justo debajo del borde (1 px de la foto)
    B = np.clip(ys + 0.5 - e[None, :], 0, 1)
    fila_b = np.clip(np.floor(e) + 1 + int(round(escala)), 0, H - 1).astype(np.int32)
    yb = np.maximum(np.arange(H)[:, None], fila_b[None, :])
    Cb = ad[yb, xi, :3] / np.maximum(ad[yb, xi, 3:], 1e-4)
    Bp = np.dstack([Cb * B[..., None], B])
    nuevo = Bp + Ts * (1 - B[..., None])              # la pestaña nace por detrás del borde
    return np.where(zona[..., None], nuevo, ad).astype(np.float32)


# --- caja del cable NUEVA (px de la foto), con las proporciones reales:
#     frontal 67/79 del ancho del cargador y 65/85,6 de su alto (ya recortado),
#     lateral 24/33 del lateral del cargador; misma perspectiva y mismo suelo
#     que la caja del cable de la foto (esquina delantera izquierda en el mismo
#     sitio). El frontal es la cara REAL (fotos/caja3d/cable-frente.png) con la
#     luz de la foto de estudio; lateral y pestaña salen de la foto de estudio.
CABLE_FRENTE = '/home/user/mi-tienda-shopify/pillatumovil/fotos/caja3d/cable-frente.png'
CA = CAJAS['cable']
ESCALA_PESTANA = 0.78        # pestaña real del cable: ~36 x 16 mm (más estrecha que la del cargador)
# v5: con 0,78 la pestaña quedaba un 9 % ancha (0,59 del ancho del frontal; en
# la caja real 0,547 con el ojal en 0,42). Se estrechan solo sus costados (de
# la punta del ojal hacia fuera); el ojal se queda casi igual (x0,98 -> 0,416).
PESTANA_CABLE_ANCHO = 0.55   # ancho de la pestaña / ancho del borde superior del frontal
PESTANA_CABLE_OJAL = 0.98    # escala horizontal del tramo del ojal
PESTANA_CABLE_X = (1513.5, 1748.5)    # bordes de la pestaña en la foto (a media altura)
PESTANA_CABLE_OJAL_X = (1546.0, 1714.5)   # puntas del ojal en la foto
TINTA_GAMMA = 1.12           # tinta de la cara real un pelín más densa (como el texto del cargador)
SUAVE_IMPRESION = 0.55       # desenfoque (px del recorte por unidad de escala) para igualar la nitidez de la foto


def _geometria_cable():
    ad_izq = lambda y: AD['izq'][0] + AD['izq'][1] * y
    top_l = AD_SUP[0] + AD_SUP[1] * ad_izq(342.6)
    ancho_ad = AD['x_pliegue'] - 0.5 * (ad_izq(top_l) + ad_izq(818.5))
    alto_ad = 0.5 * (_alto_cargador(ad_izq(818.5)) + _alto_cargador(AD['x_pliegue']))
    lat_ad = AD['x_der'] - AD['x_pliegue']
    ancho = ancho_ad * MM_CABLE[0] / MM_CARGADOR[0]
    alto = alto_ad * MM_CABLE[1] / MM_CARGADOR[1]
    lat = lat_ad * MM_CABLE[2] / MM_CARGADOR[2]
    # perspectiva de la caja del cable de la foto
    a_inf, b_inf = CA['frontal_inf']
    izq = CA['izq']
    xbl = (izq[0] + izq[1] * a_inf) / (1 - izq[1] * b_inf)
    BL = (xbl, a_inf + b_inf * xbl)
    xbr = xbl + ancho
    BR = (xbr, a_inf + b_inf * xbr)
    # crecimiento del alto de izquierda a derecha (como en la foto: 484 -> 517 px en 342 px)
    TLs = (1416.29, 337.71); TRs = (1758.7, 329.48); BRs = (1758.7, 846.34)
    crece = ((BRs[1] - TRs[1]) / (BL[1] - TLs[1]) - 1) * ancho / (BRs[0] - BL[0])
    hl = 2 * alto / (2 + crece)
    hr = hl * (1 + crece)
    ytl = BL[1] - hl
    TL = (izq[0] + izq[1] * ytl, ytl)
    TR = (xbr, BR[1] - hr)
    (lx0, ly0), (lx1, ly1) = CA['lateral_inf']
    pend_inf = (ly1 - ly0) / (lx1 - lx0)
    BB = (xbr + lat, BR[1] + pend_inf * lat)
    # el lateral se encoge hacia el fondo como en la foto (alto atrás / alto delante)
    enc = (830.0 - 327.7) / (846.34 - 326.9)
    TB = (xbr + lat, BB[1] - hr * enc)
    # pestaña: en la foto nace detrás (del panel trasero), desplazada a la derecha
    # en proporción al lateral visible
    xc_src = 0.5 * (1513.0 + 1748.5)
    yc_src = CA['sup'][0] + CA['sup'][1] * xc_src
    desplaz = (xc_src - 0.5 * (TLs[0] + TRs[0])) * lat / (CA['x_der'] - CA['x_pliegue'])
    xc = 0.5 * (TL[0] + TR[0]) + desplaz
    yc = _recta(TL, TR, xc)
    return dict(TL=TL, TR=TR, BR=BR, BL=BL, TB=TB, BB=BB, ancho=ancho, alto=alto, lat=lat,
                hl=hl, hr=hr, pestana=dict(src=(xc_src, yc_src), dst=(xc, yc), s=ESCALA_PESTANA),
                ref=dict(ancho_ad=ancho_ad, alto_ad=alto_ad, lat_ad=lat_ad))


GEO_CABLE = _geometria_cable()
PAR_X0 = AD['x_izq']                 # borde izquierdo del par (px de la foto)
PAR_X1 = GEO_CABLE['BB'][0]          # borde derecho del par (antes 1823,6)

_cache_cara = {}

CARGADOR_FRENTE = '/home/user/mi-tienda-shopify/pillatumovil/fotos/caja3d/cargador-frente.png'
# cara frontal de cada caja en la foto de estudio (esquinas TL, TR, BR, BL) y lo
# impreso en ella: 'txt' se rellena por columnas, 'ilu' por filas
CARAS = {
    'cable': dict(png=CABLE_FRENTE, n=(344, 520),
                  quad=[(1416.29, 337.71), (1758.7, 329.48), (1758.7, 846.34), (1419.57, 821.79)],
                  txt=[(1428, 362, 1650, 494)], ilu=[(1494, 514, 1568, 850), (1614, 514, 1692, 850)],
                  impreso=[(120, 90, 1060, 500), (380, 650, 690, 1560), (930, 650, 1250, 1560)],
                  dibujo=[(380, 650, 690, 1560), (930, 650, 1250, 1560)]),
    'cargador': dict(png=CARGADOR_FRENTE, n=(364, 492),
                     quad=[(966.83, 342.63), (1329.9, 336.27), (1329.9, 834.18), (968.56, 818.55)],
                     txt=[(984, 366, 1198, 484)], ilu=[(1066, 496, 1240, 798)],
                     impreso=[(90, 60, 900, 450), (470, 460, 1160, 1740)],
                     dibujo=[(470, 460, 1160, 1740)]),
}


def _cara_real(nombre='cable'):
    """Reflectancia de la cara real (1 = cartón): se divide por la luz del propio
    escaneo (cierre morfológico grande + desenfoque; cerca de los bordes, ajuste
    fino sobre el cartón para quitar el oscurecido del escaneo)."""
    key = 'R_' + nombre
    if key not in _cache_cara:
        im = np.asarray(Image.open(CARAS[nombre]['png']).convert('RGB')).astype(np.float32)
        b = 4
        im = im[b:-b, b:-b]
        L = im @ np.array([0.30, 0.59, 0.11], np.float32)
        p = cv2.resize(L, (L.shape[1] // 4, L.shape[0] // 4), interpolation=cv2.INTER_AREA)
        p = cv2.morphologyEx(p, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (61, 61)))
        p = cv2.GaussianBlur(p, (0, 0), 6)
        W0 = cv2.resize(p, (L.shape[1], L.shape[0]), interpolation=cv2.INTER_CUBIC)
        # luz del escaneo medida sobre el cartón (fuera de lo impreso); dentro de
        # lo impreso se rellena en vertical (la sombra del escaneo va de lado a lado)
        h, w = L.shape
        # fuera: los dibujos (conectores, cargador: tienen su propio sombreado)
        # y la tinta (texto, logo) con un margen; el cartón entre letras sí cuenta
        prot = np.zeros((h, w), np.float32)
        for a0, b0, a1, b1 in CARAS[nombre]['dibujo']:
            prot[max(0, b0 - b):b1 - b, max(0, a0 - b):a1 - b] = 1
        r0 = L / np.maximum(W0, 1)
        tinta = cv2.dilate((r0 < 0.9).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (41, 41)))
        papel_m = ((1 - prot) * (1 - tinta) * (r0 > 0.7)).astype(np.float32)
        sm = lambda x, sx, sy: cv2.GaussianBlur(x, (0, 0), sigmaX=sx, sigmaY=sy)
        Wl = W0.copy()
        for sx, sy, umbral in ((60, 600, 0.02), (10, 160, 0.05), (8, 8, 0.25)):
            num, den = sm(L * papel_m, sx, sy), sm(papel_m, sx, sy)
            Wl = np.where(den > umbral, num / np.maximum(den, 1e-6), Wl)
        papel = np.median(im[L > 238].reshape(-1, 3), 0)
        R = im / np.maximum(Wl[..., None] * papel / papel.mean(), 1)
        R = np.clip(R, 0, 1)
        # motas de polvo del escaneo (fuera de lo impreso) -> cartón
        RL = R @ np.array([0.30, 0.59, 0.11], np.float32)
        tinta = (RL < 0.95).astype(np.uint8)
        n, lab, st, _ = cv2.connectedComponentsWithStats(tinta, 8)
        prot = np.zeros_like(tinta)
        for a0, b0, a1, b1 in CARAS[nombre]['impreso']:
            prot[max(0, b0 - b):b1 - b, max(0, a0 - b):a1 - b] = 1
        quitar = np.zeros(n, bool)
        for i in range(1, n):
            x, y, w_, h_, ar = st[i]
            if ar < 400 and not prot[y:y + h_, x:x + w_].any():
                quitar[i] = True
        mota = cv2.dilate(quitar[lab].astype(np.uint8), np.ones((5, 5), np.uint8)).astype(np.float32)
        mota = cv2.GaussianBlur(mota, (0, 0), 1.5)[..., None]
        R = R * (1 - mota) + 1.0 * mota
        R = R ** TINTA_GAMMA
        _cache_cara[key] = R
    return _cache_cara[key]


def _luz_frontal(nombre='cable'):
    """Luz de la cara frontal en la foto de estudio, en coordenadas normalizadas:
    el cartón sin nada impreso (lo impreso se rellena con el cartón de alrededor)."""
    key = 'S_' + nombre
    if key in _cache_cara:
        return _cache_cara[key]
    cf = CARAS[nombre]
    foto = np.asarray(Image.open(SRC).convert('RGB')).astype(np.float32)
    Wn, Hn = cf['n']
    ins = 1.2
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = cf['quad']
    src = np.float32([(x0 + ins, y0 + ins), (x1, y1 + ins), (x2, y2 - 1.6), (x3 + ins, y3 - 1.6)])
    dst = np.float32([(0, 0), (Wn, 0), (Wn, Hn), (0, Hn)])
    M = cv2.getPerspectiveTransform(src, dst)
    S = cv2.warpPerspective(foto, M, (Wn, Hn), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)

    # El texto se rellena por COLUMNAS (conserva la sombra lateral de la luz);
    # dibujos que llegan al borde de abajo o en medio, por FILAS.
    def mascara(cajas):
        m = np.zeros(foto.shape[:2], np.uint8)
        for a0, b0, a1, b1 in cajas:
            m[b0:b1, a0:a1] = 1
        return cv2.warpPerspective(m, M, (Wn, Hn), flags=cv2.INTER_NEAREST) > 0

    m_txt = mascara(cf['txt'])
    m_con = mascara(cf['ilu'])
    base = cv2.GaussianBlur(S, (0, 0), 1.5)
    rel = S.copy()
    ys = np.arange(Hn, dtype=np.float32)
    for x in range(Wn):
        malo = m_txt[:, x]
        if malo.any():
            for c in range(3):
                rel[malo, x, c] = np.interp(ys[malo], ys[~malo], base[~malo, x, c])
    xs = np.arange(Wn, dtype=np.float32)
    for y in range(Hn):
        malo = m_con[y]
        if malo.any():
            for c in range(3):
                rel[y, malo, c] = np.interp(xs[malo], xs[~malo], rel[y, ~malo, c])
    malo = (m_txt | m_con).astype(np.float32)
    rel_s = cv2.GaussianBlur(rel, (0, 0), 2.5)
    pes = cv2.GaussianBlur(malo, (0, 0), 2.0)
    pes = np.maximum(pes, malo)[..., None]
    S = S * (1 - pes) + rel_s * pes
    # cartón: quita el ruido de jpeg grueso pero deja el grano
    S = 0.5 * S + 0.5 * cv2.GaussianBlur(S, (0, 0), 1.0)
    _cache_cara[key] = S
    return S


def _pintar_cara(nombre, dst_q, size, k):
    """Cara real `nombre` con la luz de la foto, sobre el cuadrilátero dst_q
    (px del lienzo de tamaño size, escala k respecto a la foto)."""
    Ws, Hs = size
    R = _cara_real(nombre)
    hR, wR = R.shape[:2]
    dst_q = np.float32(dst_q)
    fac = min(1.0, 1.5 * (dst_q[1][0] - dst_q[0][0]) / wR)
    Rr = cv2.resize(R, (max(8, int(wR * fac)), max(8, int(hR * fac))), interpolation=cv2.INTER_AREA)
    hr_, wr_ = Rr.shape[:2]
    M = cv2.getPerspectiveTransform(np.float32([(0, 0), (wr_, 0), (wr_, hr_), (0, hr_)]), dst_q)
    Rd = cv2.warpPerspective(Rr, M, (Ws, Hs), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    Rd = np.clip(Rd, 0, 1)
    if SUAVE_IMPRESION > 0:
        Rd = cv2.GaussianBlur(Rd, (0, 0), SUAVE_IMPRESION * k / 2)
    S = _luz_frontal(nombre)
    if nombre == 'cable' and SOMBRA_CABLE < 1:
        # 23/11 (dueño): «en la caja del cable veo tonalidades negras oscuras en los laterales; un poquito de sombra
        # como la caja del enchufe, vale, pero no esos colores negros». La sombra del cargador sobre el cable (borde
        # izquierdo) se queda en una fracción de su fuerza.
        Lm = S.mean(2)
        ref = np.percentile(Lm, 95)
        S = S + (np.clip(ref - Lm, 0, None) * (1 - SOMBRA_CABLE))[..., None]
    M2 = cv2.getPerspectiveTransform(np.float32([(0, 0), (S.shape[1], 0), (S.shape[1], S.shape[0]), (0, S.shape[0])]), dst_q)
    Sd = cv2.warpPerspective(S, M2, (Ws, Hs), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    return Sd * Rd


SOMBRA_CABLE = 0.35          # fuerza de la sombra del cargador sobre el frontal del cable (1 = la de la foto)
LATERAL_CABLE_LISO = True     # lateral del cable liso (sin las vetas oscuras de la foto)
LATERAL_CABLE_Y = 158.0       # tono del lateral antes del aclarado de hacer.py (queda ~190, más claro que el del cargador)


def _caja_cable(escala, fuente_rgb, fuente_alfa, size):
    """Capa RGBA (float, rgb premultiplicado aparte) de la caja del cable nueva
    al tamaño del recorte. fuente_*: recorte v3 (de ahí salen lateral y pestaña)."""
    W, H = size
    SS = 2
    g = GEO_CABLE
    k = escala * SS

    def P(p):  # foto -> px del lienzo supermuestreado
        return ((p[0] - RX0) * k, (p[1] - RY0) * k)

    Ws, Hs = W * SS, H * SS
    # fuente v3 ampliada al lienzo SS
    f_rgb = cv2.resize(fuente_rgb, (Ws, Hs), interpolation=cv2.INTER_CUBIC)
    f_a = cv2.resize(fuente_alfa, (Ws, Hs), interpolation=cv2.INTER_LINEAR)

    # ---- pestaña (detrás): semejanza desde la de la foto (escala s, centro de la
    # pestaña sobre el borde superior de la caja nueva) y, en horizontal, los
    # costados estrechados (ver PESTANA_CABLE_ANCHO). Se calcula hacia atrás:
    # para cada píxel del lienzo, de qué punto de la foto sale.
    pe = g['pestana']
    s = pe['s']
    (xs, ys), (xd, yd) = P(pe['src']), P(pe['dst'])
    yy, xx = np.mgrid[0:Hs, 0:Ws].astype(np.float32)
    ud = (xx - xd) / s                               # px del lienzo, a la escala de la foto
    ci = PESTANA_CABLE_OJAL
    ancho_dst = PESTANA_CABLE_ANCHO * (g['TR'][0] - g['TL'][0])      # px de la foto
    medio = 0.5 * ancho_dst / s * k                  # semiancho buscado (px de la foto escalada)
    us = ud / ci
    for lado, borde, punta in ((1, PESTANA_CABLE_X[1], PESTANA_CABLE_OJAL_X[1]),
                               (-1, PESTANA_CABLE_X[0], PESTANA_CABLE_OJAL_X[0])):
        E = abs(borde - pe['src'][0]) * k            # borde de la pestaña (px, desde su centro)
        e_ = (abs(punta - pe['src'][0]) + 1.5) * k   # punta del ojal + 1,5 px: hasta aquí, sin tocar
        f = (medio - ci * e_) / (E - e_)             # compresión de este costado
        sel = (lado * ud) > ci * e_
        us = np.where(sel, lado * (e_ + (lado * ud - ci * e_) / f), us)
    map_x = (xs + us).astype(np.float32)
    map_y = (ys + (yy - yd) / s).astype(np.float32)
    # la pestaña acaba sobre el borde de la caja de la foto: por debajo de
    # (borde - 3 px) se repite esa fila (costados rectos hacia dentro de la caja
    # nueva, que la tapa) -> nada del borde de la caja de la foto (el «pie»)
    xf = RX0 + map_x / k
    tope = (CA['sup'][0] + CA['sup'][1] * xf - 3 - RY0) * k
    map_y = np.minimum(map_y, tope).astype(np.float32)
    yf = RY0 + (ys + (yy - yd) / s) / k
    corte = (yf < CA['sup'][0] + CA['sup'][1] * xf + 8) & (xf > 1505) & (xf < 1753)
    pa = cv2.remap(f_a, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0) * corte
    pr = cv2.remap(f_rgb, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)

    # ---- silueta de la caja (frontal + lateral)
    def poli(pts, ss=8):
        m = np.zeros((Hs, Ws), np.uint8)
        q = np.array([P(p) for p in pts], np.float64)
        cv2.fillPoly(m, [np.round(q * 16).astype(np.int32)], 255, lineType=cv2.LINE_AA, shift=4)
        return m.astype(np.float32) / 255

    sil_f = poli([g['TL'], g['TR'], g['BR'], g['BL']])
    sil_l = poli([g['TR'], g['TB'], g['BB'], g['BR']])

    # ---- frontal: cara real x luz de la foto
    dst_q = [P(g['TL']), P(g['TR']), P(g['BR']), P(g['BL'])]
    frontal = _pintar_cara('cable', dst_q, (Ws, Hs), k)

    # ---- lateral: el de la foto (ya en blanco cálido), comprimido a su sitio
    src_l = np.float32([P((1759.6, 328.0)), P((1822.4, 328.6)), P((1822.4, 830.6)), P((1759.6, 845.6))])
    dst_l = np.float32([P(g['TR']), P(g['TB']), P(g['BB']), P(g['BR'])])
    M3 = cv2.getPerspectiveTransform(src_l, dst_l)
    lado = cv2.warpPerspective(f_rgb, M3, (Ws, Hs), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    Yl = lado @ np.array([0.30, 0.59, 0.11], np.float32)
    if LATERAL_CABLE_LISO:
        # 23/11 (dueño): el lateral salía con vetas oscuras (parecía metal). Ahora es cartón blanco liso en sombra
        # suave, como el lateral del cargador: tono uniforme con un leve degradado vertical y solo el grano fino.
        d = np.array(P(g['BR']), np.float32) - np.array(P(g['TR']), np.float32)
        tv = np.clip(((yy - P(g['TR'])[1]) / max(d[1], 1)), 0, 1)
        grano = Yl - cv2.GaussianBlur(Yl, (0, 0), 1.2 * k)
        Yl = LATERAL_CABLE_Y * (1.04 - 0.10 * tv) + 0.35 * grano
    lado = np.clip(Yl[..., None] * np.array(TINTE_LATERAL, np.float32), 0, 255)

    # ---- composición (pestaña detrás, caja delante)
    a_caja = np.maximum(sil_f, sil_l)
    t_l = sil_l / np.maximum(sil_f + sil_l, 1e-4)
    caja = frontal * (1 - t_l[..., None]) + lado * t_l[..., None]
    alfa = a_caja + pa * (1 - a_caja)
    rgb = (caja * a_caja[..., None] + pr * (pa * (1 - a_caja))[..., None]) / np.maximum(alfa, 1e-4)[..., None]
    rgb = cv2.resize(rgb * alfa[..., None], (W, H), interpolation=cv2.INTER_AREA)
    alfa = cv2.resize(alfa, (W, H), interpolation=cv2.INTER_AREA)
    rgb = rgb / np.maximum(alfa, 1e-4)[..., None]
    return np.clip(rgb, 0, 255), np.clip(alfa, 0, 1)


# Cargador: también su frontal con la cara REAL (cargador-frente.png). En la
# foto de estudio el texto y el dibujo del cargador no son los de la caja real
# (texto un 17 % más grande, cargador más pequeño y más arriba); con la cara real
# los dos textos «USB-C» salen del mismo tamaño, como en la caja de verdad.
# False = frontal de la foto de estudio (solo recortado).
CARGADOR_CARA_REAL = True


def _geometria_cargador():
    f = sum(b - a for a, b in FRANJAS_CARGADOR)
    i0, i1 = AD['izq']
    top = lambda x: (AD_SUP[0] + AD_SUP[1] * x) * (1 - f) + (AD_INF[0] + AD_INF[1] * x) * f
    bot = lambda x: AD_INF[0] + AD_INF[1] * x
    xtl = (i0 + i1 * top(0)) / (1 - i1 * (top(1) - top(0)))
    xbl = (i0 + i1 * AD_INF[0]) / (1 - i1 * AD_INF[1])
    xp = AD['x_pliegue']
    return dict(TL=(xtl, top(xtl)), TR=(xp, top(xp)), BR=(xp, bot(xp)), BL=(xbl, bot(xbl)))


GEO_CARGADOR = _geometria_cargador()


def recortar(escala=1.0):
    """Par con tamaños reales: cargador de la foto (sin la franja vacía de más)
    + caja del cable nueva. Mismo formato de salida que la v3."""
    im3, info3 = _recortar_v3(escala)
    arr = np.asarray(im3).astype(np.float32)
    rgb3, a_ad, a_ca = arr[..., :3], info3['alfas']['adaptador'], info3['alfas']['cable']
    H, W = a_ad.shape
    # cargador solo (premultiplicado para que el remuestreo no ensucie el borde)
    ad = np.dstack([rgb3 * a_ad[..., None], a_ad])
    ad = _escalar_pestana_cargador(ad, escala)          # v5: pestaña a su tamaño real
    for (fa, fb), arriba_frac in zip(FRANJAS_CARGADOR, GANANCIA_COSTURA_ARRIBA):
        # de arriba abajo: la de abajo no se mueve con la de arriba
        ad = _quitar_franja(ad, escala, fa, fb, AD['x_der'] + 3, arriba_frac)
    if CARGADOR_CARA_REAL:
        SS = 2
        k = escala * SS
        g = GEO_CARGADOR
        q = [((x - RX0) * k, (y - RY0) * k) for x, y in (g['TL'], g['TR'], g['BR'], g['BL'])]
        fr = _pintar_cara('cargador', q, (W * SS, H * SS), k)
        m = np.zeros((H * SS, W * SS), np.uint8)
        cv2.fillPoly(m, [np.round(np.array(q) * 16).astype(np.int32)], 255, lineType=cv2.LINE_AA, shift=4)
        m = m.astype(np.float32) / 255
        fr = cv2.resize(fr * m[..., None], (W, H), interpolation=cv2.INTER_AREA)
        m = cv2.resize(m, (W, H), interpolation=cv2.INTER_AREA)
        fr = fr / np.maximum(m, 1e-4)[..., None]
        a = ad[..., 3:4]
        rgb_ad = ad[..., :3] / np.maximum(a, 1e-4)
        rgb_ad = rgb_ad * (1 - m[..., None]) + fr * m[..., None]
        ad = np.dstack([rgb_ad * a, a[..., 0]])
    # caja del cable nueva
    c_rgb, c_a = _caja_cable(escala, rgb3, a_ca, (W, H))
    pre = ad[..., :3] + c_rgb * c_a[..., None] * (1 - ad[..., 3:4])
    alfa = ad[..., 3] + c_a * (1 - ad[..., 3])
    rgb = pre / np.maximum(alfa, 1e-4)[..., None]
    out = np.dstack([np.clip(rgb, 0, 255), np.clip(alfa, 0, 1) * 255]).astype(np.uint8)

    g = GEO_CABLE
    apoyos = [info3['apoyos'][0],
              [((x - RX0) * escala, (y - RY0) * escala) for x, y in (g['BL'], g['BR'], g['BB'])]]
    info = dict(apoyos=apoyos, escala=escala, origen=(RX0, RY0), par=(PAR_X0, PAR_X1), geo=g)
    return Image.fromarray(out, 'RGBA'), info


def medidas(info=None):
    """Proporciones aparentes (px de la foto) de las dos caras frontales."""
    g = GEO_CABLE
    ad_izq = lambda y: AD['izq'][0] + AD['izq'][1] * y
    xl = 0.5 * (ad_izq(342.6) + ad_izq(818.5))
    ancho_ad = AD['x_pliegue'] - xl
    alto_ad_v3 = 0.5 * (_cara_cargador(ad_izq(818.5))[1] + _cara_cargador(AD['x_pliegue'])[1])
    alto_ad = 0.5 * (_alto_cargador(ad_izq(818.5)) + _alto_cargador(AD['x_pliegue']))
    ancho_ca = g['BR'][0] - 0.5 * (g['TL'][0] + g['BL'][0])
    alto_ca = 0.5 * (g['hl'] + g['hr'])
    return dict(cargador_frontal_ancho_alto_v3=ancho_ad / alto_ad_v3, cargador_frontal_ancho_alto=ancho_ad / alto_ad,
                cable_frontal_ancho_alto=ancho_ca / alto_ca, cable_ancho_rel=ancho_ca / ancho_ad,
                cable_alto_rel=alto_ca / alto_ad, cable_lateral_rel=g['lat'] / (AD['x_der'] - AD['x_pliegue']),
                px=dict(ancho_ad=ancho_ad, alto_ad=alto_ad, alto_ad_v3=alto_ad_v3, ancho_ca=ancho_ca, alto_ca=alto_ca,
                        lat_ad=AD['x_der'] - AD['x_pliegue'], lat_ca=g['lat']))


if __name__ == '__main__':
    import sys
    esc = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
    dst = sys.argv[2] if len(sys.argv) > 2 else 'recorte.png'
    im, info = recortar(esc)
    im.save(dst)
    print(im.size, info['apoyos'])
    for k_, v_ in medidas().items():
        print(k_, v_)
