# -*- coding: utf-8 -*-
"""Anuncio «Un pack, tres precios» de Pillatumovil (imagen estática Meta).

Un solo pack grande (caja del cargador de 20 W + caja del cable USB-C, foto
real «Pack A»: fotos/estudio/ps-estudio-portada.jpg, recortada en recorte.py).
v4: las dos cajas con sus proporciones y su cara reales (ver recorte.py).
y debajo, en grande, el precio de CADA pack según cuántos se compran, igual
que el selector «¿Cuántos packs?» de la ficha de producto.

Uso:  python3 hacer.py            -> los 6 anuncios + vistas de 540 px
Sale: anuncio_4x5.png (1080x1350, feed),
      anuncio_9x16.png (1080x1920, SOLO Stories: contenido en y 270-1650),
      anuncio_9x16_reels.png (1080x1920, SOLO Reels: contenido en y 270-1248),
      y las mismas con _dic (precio de diciembre),
      vista_*.png (540 px) y _t/ (comprobaciones a 360 px y lienzos 2x).
      v3_*.png = la versión anterior (caja del cable tan alta como la del cargador), para comparar.
      v4_*.png = la v4 antes de los retoques v5 (pestañas y costuras del lateral, ver recorte.py).
Se dibuja a 2x y se reduce con LANCZOS.
"""
import os
import sys
from decimal import Decimal, ROUND_HALF_UP

import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

# =====================================================================
# PRECIOS Y TEXTOS QUE CAMBIAN (todo lo demás se calcula)
# =====================================================================
TOTAL_2 = '33.99'            # 2 packs, total
TOTAL_3 = '45.99'            # 3 packs, total
APPLE_PACK = '38.00'         # Apple: cargador 19,00 + cable 19,00
APPLE_FECHA = '01/11/2026'
VARIANTES = {
    # sufijo: precio de 1 pack y línea de lanzamiento (None = sin línea)
    '': dict(precio_1='18.99', lanzamiento=('Precio de lanzamiento', 'hasta el 30/11')),
    '_dic': dict(precio_1='19.99', lanzamiento=None),
}
# =====================================================================

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from recorte import recortar, PAR_X0, PAR_X1, medidas  # noqa: E402

TRAB = os.path.join(AQUI, '_t')
os.makedirs(TRAB, exist_ok=True)

FUENTES = '/home/user/mi-tienda-shopify/pillatumovil/tools/fuentes'
UNB = f'{FUENTES}/Unbounded.ttf'
ARC = f'{FUENTES}/Archivo.ttf'

NOCHE = (11, 15, 26)
MARFIL = (244, 241, 234)
ORO = (214, 180, 112)
ORO_G = [(0.0, (248, 232, 187)), (0.5, (220, 187, 118)), (1.0, (169, 132, 62))]
ORO_CLARO = (240, 214, 150)
ROJO = (196, 38, 46)
TESELA = (21, 26, 39)
TESELA_BORDE = (58, 64, 82)

K = 2  # lienzo a 2x
ELEMENTOS = []   # cajas de todo lo dibujado (para comprobar márgenes)


# ---------------------------------------------------------------- dinero
def D(s):
    return Decimal(s)


def eur(v):
    v = Decimal(v).quantize(Decimal('0.01'), ROUND_HALF_UP)
    e, c = f'{v:.2f}'.split('.')
    return f'{e},{c} €'


def precios(precio_1):
    p1, t2, t3 = D(precio_1), D(TOTAL_2), D(TOTAL_3)
    c2 = (t2 / 2).quantize(Decimal('0.01'), ROUND_HALF_UP)
    c3 = (t3 / 3).quantize(Decimal('0.01'), ROUND_HALF_UP)
    a2, a3 = 2 * p1 - t2, 3 * p1 - t3
    return dict(p1=eur(p1), t2=eur(t2), t3=eur(t3), c2=eur(c2), c3=eur(c3), a2=eur(a2), a3=eur(a3))


# ---------------------------------------------------------------- letras
_cache = {}


def fuente(path, size, peso, ancho=None):
    key = (path, round(size * K), peso, ancho)
    if key not in _cache:
        f = ImageFont.truetype(path, round(size * K))
        f.set_variation_by_axes([peso] if ancho is None else [peso, ancho])
        _cache[key] = f
    return _cache[key]


def U(size, peso=800):
    return fuente(UNB, size, peso)


def A(size, peso=500, ancho=100):
    return fuente(ARC, size, peso, ancho)


def largo(txt, f):
    """ancho en px 1x"""
    return f.getlength(txt) / K


def gradiente_oro(w, h, stops=ORO_G):
    t = np.linspace(0, 1, max(h, 2))[:, None]
    out = np.zeros((max(h, 2), max(w, 1), 3), np.float32)
    for i in range(len(stops) - 1):
        t0, c0 = stops[i]
        t1, c1 = stops[i + 1]
        k = np.clip((t - t0) / (t1 - t0), 0, 1)
        sel = (t >= t0) & (t <= t1)
        col = np.array(c0, np.float32) * (1 - k) + np.array(c1, np.float32) * k
        out = np.where(sel[..., None], np.broadcast_to(col[:, None, :], out.shape), out)
    return out[:h, :w]


def pegar_color(lienzo, mascara, color=None, oro=False, alpha=1.0):
    bb = mascara.getbbox()
    if bb is None:
        return None
    if alpha < 1:
        mascara = mascara.point(lambda v: int(v * alpha))
    if oro:
        x0, y0, x1, y1 = bb
        g = gradiente_oro(x1 - x0, y1 - y0)
        relleno = Image.new('RGB', lienzo.size, ORO)
        relleno.paste(Image.fromarray(g.astype(np.uint8)), (x0, y0))
    else:
        relleno = Image.new('RGB', lienzo.size, color)
    lienzo.paste(relleno, (0, 0), mascara)
    return bb


def texto(lienzo, xy, txt, f, color=MARFIL, anchor='ls', oro=False, alpha=1.0):
    """xy en px 1x. Devuelve la caja de tinta en px 1x."""
    capa = Image.new('L', lienzo.size, 0)
    ImageDraw.Draw(capa).text((xy[0] * K, xy[1] * K), txt, font=f, fill=255, anchor=anchor)
    bb = pegar_color(lienzo, capa, color, oro, alpha)
    if bb is not None:
        ELEMENTOS.append((txt, tuple(v / K for v in bb)))
    return None if bb is None else tuple(v / K for v in bb)


def texto_partes(lienzo, x, y, partes, anchor_h='l'):
    """partes: [(txt, fuente, color|'oro', alpha)] en la misma línea base."""
    total = sum(largo(t, f) for t, f, _, _ in partes)
    if anchor_h == 'm':
        x -= total / 2
    elif anchor_h == 'r':
        x -= total
    for t, f, c, a in partes:
        texto(lienzo, (x, y), t, f, None if c == 'oro' else c, oro=(c == 'oro'), alpha=a)
        x += largo(t, f)
    return total


def redondeado(lienzo, box, r, fill=None, outline=None, width=0, oro=False, alpha=1.0):
    ELEMENTOS.append(('caja', tuple(box)))
    box = [v * K for v in box]
    capa = Image.new('L', lienzo.size, 0)
    ImageDraw.Draw(capa).rounded_rectangle(box, r * K, fill=255)
    if oro or fill is not None:
        pegar_color(lienzo, capa, fill, oro, alpha)
    if outline is not None and width:
        borde = Image.new('L', lienzo.size, 0)
        ImageDraw.Draw(borde).rounded_rectangle(box, r * K, outline=255, width=round(width * K))
        pegar_color(lienzo, borde, outline)


def punto(lienzo, cx, cy, r, color):
    s = 4
    capa = Image.new('L', lienzo.size, 0)
    big = Image.new('L', (round(2 * r * K * s) + 4, round(2 * r * K * s) + 4), 0)
    ImageDraw.Draw(big).ellipse((2, 2, 2 + 2 * r * K * s, 2 + 2 * r * K * s), fill=255)
    sm = big.resize((big.width // s, big.height // s), Image.LANCZOS)
    capa.paste(sm, (round(cx * K - sm.width / 2), round(cy * K - sm.height / 2)))
    pegar_color(lienzo, capa, color)


# ---------------------------------------------------------------- logo
def logo(lienzo, x, y_base, size):
    """Logo de la web: el móvil que hace de asta de la P dorada + «pilla·tu·movil»
    (tu en oro), en Unbounded 700. x, y_base, size en px 1x."""
    f = U(size, 700)
    alto = size * 1.20                 # alto del móvil
    w = alto * 0.40                    # ancho del móvil
    y1 = y_base + size * 0.10
    y0 = y1 - alto
    x0 = x
    s = 6
    ancho_total = w * 2.05
    Wc, Hc = int(ancho_total * K * s) + 8, int(alto * K * s) + 8
    # panza de la P (oro) detrás del móvil
    m = Image.new('L', (Wc, Hc), 0)
    d = ImageDraw.Draw(m)
    g = w * 0.42 * K * s                 # grosor del trazo
    r = alto * 0.245 * K * s             # radio de la panza (eje)
    cx = w * 0.98 * K * s
    yt = g / 2 + 4
    yb = yt + 2 * r
    cy = (yt + yb) / 2
    d.ellipse((cx - r - g / 2, cy - r - g / 2, cx + r + g / 2, cy + r + g / 2), fill=255)
    d.ellipse((cx - r + g / 2, cy - r + g / 2, cx + r - g / 2, cy + r - g / 2), fill=0)
    d.rectangle((0, 0, cx, Hc), fill=0)
    d.rectangle((w * 0.5 * K * s, yt - g / 2, cx, yt + g / 2), fill=255)
    d.rectangle((w * 0.5 * K * s, yb - g / 2, cx, yb + g / 2), fill=255)
    m = m.resize((Wc // s, Hc // s), Image.LANCZOS)
    capa = Image.new('L', lienzo.size, 0)
    capa.paste(m, (round(x0 * K), round(y0 * K)))
    pegar_color(lienzo, capa, oro=True)
    # móvil
    for (dx, col, ww) in ((0, (176, 182, 196), 0), (1, (16, 21, 36), w * 0.085)):
        m = Image.new('L', (Wc, Hc), 0)
        e = ww * K * s
        ImageDraw.Draw(m).rounded_rectangle((4 + e, 4 + e, w * K * s - e, alto * K * s - e),
                                            radius=w * 0.30 * K * s - e, fill=255)
        m = m.resize((Wc // s, Hc // s), Image.LANCZOS)
        capa = Image.new('L', lienzo.size, 0)
        capa.paste(m, (round(x0 * K), round(y0 * K)))
        pegar_color(lienzo, capa, col)
    # isla
    redondeado(lienzo, (x0 + w * 0.34, y0 + alto * 0.075, x0 + w * 0.66, y0 + alto * 0.075 + w * 0.10), w * 0.05,
               fill=(60, 66, 82))
    cx1 = x0 + ancho_total + size * 0.28
    for t, c in (('pilla', MARFIL), ('tu', None), ('movil', MARFIL)):
        texto(lienzo, (cx1, y_base), t, f, c, oro=(c is None))
        cx1 += largo(t, f)
    return cx1


# ---------------------------------------------------------------- fondo
def fondo(W, H, cx, suelo, ancho_prod):
    """Estudio oscuro (noche): pared con un halo cálido detrás del pack y un
    suelo satinado algo más claro bajo las cajas, que cae a noche hacia abajo.
    Todo en px del lienzo (2x)."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    base = np.array(NOCHE, np.float32)
    img = np.broadcast_to(base, (H, W, 3)).copy()
    # pared: halo (luz de estudio sobre el fondo, más cálida a la derecha)
    d = np.sqrt(((xx - cx) / (ancho_prod * 0.95)) ** 2 + ((yy - (suelo - ancho_prod * 0.36)) / (ancho_prod * 0.62)) ** 2)
    img += np.exp(-d ** 2 * 1.4)[..., None] * np.array([30, 30, 36], np.float32)
    d = np.sqrt(((xx - (cx + ancho_prod * 0.42)) / (ancho_prod * 0.55)) ** 2 + ((yy - (suelo - ancho_prod * 0.30)) / (ancho_prod * 0.45)) ** 2)
    img += np.exp(-d ** 2 * 1.6)[..., None] * np.array([26, 18, 8], np.float32)
    # suelo
    t = np.clip((yy - (suelo - 0.10 * ancho_prod)) / (0.12 * ancho_prod), 0, 1)
    t = t * t * (3 - 2 * t)
    d2 = np.sqrt(((xx - cx) / (ancho_prod * 0.78)) ** 2 + ((yy - (suelo + 0.01 * ancho_prod)) / (ancho_prod * 0.16)) ** 2)
    charco = np.exp(-d2 ** 2 * 1.3)
    suelo_col = np.array([20, 23, 32], np.float32) + charco[..., None] * np.array([34, 31, 28], np.float32)
    img = img * (1 - t[..., None]) + suelo_col * t[..., None]
    caida = np.clip((yy - (suelo + 0.05 * ancho_prod)) / (0.30 * ancho_prod), 0, 1)
    caida = caida * caida * (3 - 2 * caida)
    img = img * (1 - caida[..., None]) + base * caida[..., None]
    # viñeta muy suave
    v = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H * 0.45) / (H * 0.75)) ** 2)
    k = 0.35 * np.clip(v - 0.6, 0, 1)
    img = img * (1 - k[..., None]) + base * k[..., None]
    rng = np.random.default_rng(7)
    img += rng.normal(0, 1.2, (H, W, 1)).astype(np.float32)
    return np.clip(img, 0, 255)


# ---------------------------------------------------------------- producto
_rec = {}


def recorte_escalado(esc):
    key = round(esc, 4)
    if key not in _rec:
        _rec[key] = recortar(esc)
    return _rec[key]


def poner_producto(img, ancho_par, cx, y_base):
    """Pega el pack (dos cajas) con el par de ancho `ancho_par` (px lienzo)
    centrado en cx y la línea de apoyo del cargador (esquina del pliegue) en y_base.
    Devuelve (img, caja del producto en px lienzo)."""
    X0, X1 = PAR_X0, PAR_X1              # bordes del par en la foto (v4: cable con su tamaño real)
    esc = ancho_par / (X1 - X0)
    rec, info = recorte_escalado(esc)
    arr = np.asarray(rec).astype(np.float32)
    rgb, a = arr[..., :3], arr[..., 3] / 255
    h, w = a.shape
    ox = cx - ((X0 + X1) / 2 - info['origen'][0]) * esc
    # apoyo: el punto más bajo de las bases (esquina del pliegue del cable)
    y_ref = max(p[1] for b in info['apoyos'] for p in b)
    oy = y_base - y_ref
    H, W = img.shape[:2]
    xi, yi = int(np.floor(ox)), int(np.floor(oy))
    fx, fy = ox - xi, oy - yi
    # desplazamiento subpíxel del recorte
    M = np.float32([[1, 0, fx], [0, 1, fy]])
    rgb = cv2.warpAffine(rgb, M, (w + 1, h + 1), flags=cv2.INTER_LINEAR)
    a = cv2.warpAffine(a, M, (w + 1, h + 1), flags=cv2.INTER_LINEAR)
    h, w = a.shape
    apoyos = [[(x + fx, y + fy) for x, y in b] for b in info['apoyos']]

    def base_y(xs):
        """y de la línea de apoyo por columna (coords del recorte)."""
        out = np.full(len(xs), np.nan, np.float32)
        for b in apoyos:
            bx = np.array([p[0] for p in b]); by = np.array([p[1] for p in b])
            sel = (xs >= bx[0] - 2) & (xs <= bx[-1] + 2)
            out[sel] = np.interp(xs[sel], bx, by)
        return out

    xs = np.arange(w, dtype=np.float32)
    by = base_y(xs)
    tiene = ~np.isnan(by)
    by_f = np.where(tiene, by, 0)

    # --- reflejo: cada columna se refleja respecto a su línea de apoyo
    largo_ref = 0.16 * ancho_par
    hh = int(largo_ref) + 4
    ys = np.arange(hh, dtype=np.float32)[:, None]
    map_x = np.broadcast_to(xs[None, :], (hh, w)).astype(np.float32)
    map_y = (by_f[None, :] - 0.5 - ys).astype(np.float32)          # fila de origen
    ref_rgb = cv2.remap(rgb, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    ref_a = cv2.remap(a, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    fade = np.clip(1 - ys / largo_ref, 0, 1) ** 1.8
    ref_a = ref_a * fade * tiene[None, :] * 0.13
    ref_rgb = cv2.GaussianBlur(ref_rgb, (0, 0), 1.6)
    ref_a = cv2.GaussianBlur(ref_a, (0, 0), 1.6)
    # cada columna del reflejo empieza en su línea de apoyo
    lien_ref = np.zeros((H, W, 3), np.float32)
    lien_ra = np.zeros((H, W), np.float32)
    for x in range(w):
        if not tiene[x]:
            continue
        X = xi + x
        if X < 0 or X >= W:
            continue
        y0 = yi + by_f[x]
        Y0 = int(np.floor(y0)); fr = y0 - Y0
        col_a = ref_a[:, x]; col_c = ref_rgb[:, x]
        # interpolación vertical subpíxel
        n = min(hh, H - Y0 - 1)
        if n <= 0:
            continue
        lien_ra[Y0:Y0 + n, X] += col_a[:n] * (1 - fr)
        lien_ra[Y0 + 1:Y0 + 1 + n, X] += col_a[:n] * fr
        lien_ref[Y0:Y0 + n, X] += col_c[:n] * (col_a[:n] * (1 - fr))[:, None]
        lien_ref[Y0 + 1:Y0 + 1 + n, X] += col_c[:n] * (col_a[:n] * fr)[:, None]
    img = img * (1 - lien_ra[..., None]) + lien_ref

    # --- sombras en el suelo
    sombra_c = np.zeros((H, W), np.float32)   # línea de contacto
    sombra_s = np.zeros((H, W), np.float32)   # sombra suave pegada a la base
    sombra_a = np.zeros((H, W), np.float32)   # sombra ambiente ancha
    SS = 8
    for b in apoyos:
        pts = np.array([(xi + x, yi + y) for x, y in b], np.float32)
        cv2.polylines(sombra_c, [np.round(pts * SS).astype(np.int32)], False, 1.0,
                      thickness=max(1, int(round(1.9 * K))), lineType=cv2.LINE_AA, shift=3)
        banda = np.concatenate([pts + np.float32([0, -1.0]), pts[::-1] + np.float32([0, 0.010 * ancho_par])], 0)
        cv2.fillPoly(sombra_s, [np.round(banda * SS).astype(np.int32)], 1.0, lineType=cv2.LINE_AA, shift=3)
        banda2 = np.concatenate([pts + np.float32([-0.02 * ancho_par, -0.01 * ancho_par]),
                                 pts[::-1] + np.float32([0.01 * ancho_par, 0.03 * ancho_par])], 0)
        cv2.fillPoly(sombra_a, [np.round(banda2 * SS).astype(np.int32)], 1.0, lineType=cv2.LINE_AA, shift=3)
    sombra_c = cv2.GaussianBlur(sombra_c, (0, 0), 0.7)
    sombra_s = cv2.GaussianBlur(sombra_s, (0, 0), 0.006 * ancho_par)
    sombra_a = cv2.GaussianBlur(sombra_a, (0, 0), 0.035 * ancho_par)
    osc = np.clip(sombra_c * 0.85 + sombra_s * 0.55 + sombra_a * 0.45, 0, 0.92)
    img = img * (1 - osc[..., None])

    # --- cajas
    x0, y0 = max(0, xi), max(0, yi)
    x1, y1 = min(W, xi + w), min(H, yi + h)
    sub_rgb = rgb[y0 - yi:y1 - yi, x0 - xi:x1 - xi]
    sub_a = a[y0 - yi:y1 - yi, x0 - xi:x1 - xi]
    img[y0:y1, x0:x1] = img[y0:y1, x0:x1] * (1 - sub_a[..., None]) + sub_rgb * sub_a[..., None]
    ys_a, xs_a = np.nonzero(a > 0.5)
    caja = (xi + xs_a.min(), yi + ys_a.min(), xi + xs_a.max(), yi + ys_a.max())
    return img, caja


# ---------------------------------------------------------------- piezas de texto
def precio_grande(lienzo, cx, y, valor, size, color):
    """«18,99 €» con el número grande y el € algo más pequeño, centrado en cx."""
    num = valor.replace(' €', '')
    fn = U(size, 800)
    fe = U(size * 0.62, 700)
    gap = size * 0.10
    total = largo(num, fn) + gap + largo('€', fe)
    x = cx - total / 2
    texto(lienzo, (x, y), num, fn, color)
    texto(lienzo, (x + largo(num, fn) + gap, y), '€', fe, color)
    return total


def pastilla(lienzo, cx, cy, txt, f, fondo_col, texto_col, alto, pad):
    w = largo(txt, f) + 2 * pad
    redondeado(lienzo, (cx - w / 2, cy - alto / 2, cx + w / 2, cy + alto / 2), alto / 2, fill=fondo_col)
    texto(lienzo, (cx, cy), txt, f, texto_col, anchor='mm')
    return w


def escalera(lienzo, x0, y0, ancho, alto, P, lanz, tam):
    """Las tres teselas «1 pack / 2 packs / 3 packs» como el selector de la web.
    tam: dict de tamaños (px 1x)."""
    gap = tam['gap']
    tw = (ancho - 2 * gap) / 3
    filas = [
        ('1 pack', P['p1'], None, None, None),
        ('2 packs', P['c2'], 'cada uno', 'Total ' + P['t2'], 'Ahorre ' + P['a2']),
        ('3 packs', P['c3'], 'cada uno', 'Total ' + P['t3'], 'Ahorre ' + P['a3']),
    ]
    # halo de luz cálida detrás de la tesela de 3 packs
    hx0 = x0 + 2 * (tw + gap)
    m = Image.new('L', lienzo.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([v * K for v in (hx0 + 8, y0 + 10, hx0 + tw - 8, y0 + alto - 4)], tam['radio'] * K, fill=255)
    m = np.asarray(m).astype(np.float32) / 255
    m = cv2.GaussianBlur(m, (0, 0), 26 * K) * 0.30
    arr = np.asarray(lienzo).astype(np.float32)
    arr = arr * (1 - m[..., None]) + np.array((214, 170, 90), np.float32) * m[..., None]
    lienzo.paste(Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)))
    for i, (etq, pp, cada, tot, ahorro) in enumerate(filas):
        bx0 = x0 + i * (tw + gap)
        bx1 = bx0 + tw
        cx = (bx0 + bx1) / 2
        sel = i == 2
        if sel:
            redondeado(lienzo, (bx0, y0, bx1, y0 + alto), tam['radio'], oro=True)
            c1, c2, c3 = NOCHE, (34, 28, 16), NOCHE
        else:
            redondeado(lienzo, (bx0, y0, bx1, y0 + alto), tam['radio'], fill=TESELA, outline=TESELA_BORDE, width=1.5)
            c1, c2, c3 = MARFIL, (226, 223, 216), MARFIL
        dy = 0
        if not cada and not lanz:
            # solo «1 pack» y el precio (diciembre): bloque centrado en la casilla
            arriba = tam['etq_y'] - tam['etq'] * 0.74
            dy = (alto - (tam['precio_y'] - arriba)) / 2 - arriba
        yy = y0 + tam['etq_y'] + dy
        texto(lienzo, (cx, yy), etq, A(tam['etq'], 700), c1, anchor='ms')
        precio_grande(lienzo, cx, y0 + tam['precio_y'] + dy, pp, tam['precio'], c1)
        if cada:
            texto(lienzo, (cx, y0 + tam['cada_y']), cada, A(tam['cada'], 600), c2, anchor='ms')
            # total: el precio final que se paga (el mismo que muestra en grande el selector de la ficha)
            et, _, cifra = tot.partition(' ')
            texto_partes(lienzo, cx, y0 + tam['total_y'], [(et + ' ', A(tam['total'], 500), c3, 1.0),
                                                           (cifra, A(tam['total'], 750), c3, 1.0)], anchor_h='m')
            fp = A(tam['pastilla'], 800)
            if sel:
                pastilla(lienzo, cx, y0 + tam['pastilla_y'], ahorro, fp, NOCHE, ORO_CLARO, tam['pastilla_alto'], tam['pastilla_pad'])
            else:
                # dorada maciza con texto noche
                w = largo(ahorro, fp) + 2 * tam['pastilla_pad']
                cy = y0 + tam['pastilla_y']
                redondeado(lienzo, (cx - w / 2, cy - tam['pastilla_alto'] / 2, cx + w / 2, cy + tam['pastilla_alto'] / 2),
                           tam['pastilla_alto'] / 2, oro=True)
                texto(lienzo, (cx, cy), ahorro, fp, NOCHE, anchor='mm')
        elif lanz:
            fl = A(tam['lanz'], 600)
            l1, l2 = lanz
            w1 = largo(l1, fl)
            r = tam['lanz'] * 0.24
            xl = cx - (w1 + r * 2 + tam['lanz'] * 0.40) / 2
            yl = y0 + tam['lanz_y']
            punto(lienzo, xl + r, yl - tam['lanz'] * 0.34, r, ROJO)
            texto(lienzo, (xl + 2 * r + tam['lanz'] * 0.40, yl), l1, fl, MARFIL, alpha=0.92)
            texto(lienzo, (cx, yl + tam['lanz'] * 1.32), l2, fl, MARFIL, anchor='ms', alpha=0.92)


def boton(lienzo, cx, y0, alto, txt, f, ancho=None):
    w = ancho or (largo(txt, f) + 2 * alto * 0.9)
    redondeado(lienzo, (cx - w / 2, y0, cx + w / 2, y0 + alto), alto / 2, oro=True)
    texto(lienzo, (cx, y0 + alto / 2 + alto * 0.02), txt, f, NOCHE, anchor='mm')


# ---------------------------------------------------------------- anuncio
TXT = dict(
    gancho='Cuantos más packs, menos paga por cada uno',
    pack='Cada pack: ',
    producto='cargador de 20 W + cable de 1 m · Originales de Apple, nuevos y precintados',
    # Apple no vende «packs»: cargador 19,00 € + cable 19,00 €
    apple=f'En Apple, cargador + cable: {eur(APPLE_PACK)} (precio del {APPLE_FECHA})',
    selector='¿Cuántos packs?',
    cable='Cable USB-C o Lightning, mismo precio',
    confianza='Envío gratis en 24\u201348 h laborables · Devolución gratis',
    boton='Elija sus packs en pillatumovil.com  →',
    legal='Precios con IVA incluido. Tienda independiente, no afiliada a Apple Inc.',
    legal_ahorro='Ahorro frente a comprar los packs de uno en uno a {p1}. Precios con IVA incluido.',
    legal_marca='Tienda independiente, no afiliada a Apple Inc.',
)
LEGAL_ALFA = 0.76      # letra pequeña: legible a 360 px (antes 0,50)


def titular(lienzo, M, y_gancho, y_titular, ancho, P, tam_g, tam_t):
    texto(lienzo, (M, y_gancho), TXT['gancho'], A(tam_g, 600), MARFIL, alpha=0.92)
    # el titular ocupa como mucho el ancho útil (márgenes intactos)
    linea = '3 packs: ' + P['c3'] + ' cada uno'
    tam_t = min(tam_t, ancho / (U(100, 800).getlength(linea) / K / 100) - 0.2)
    partes = [('3 packs: ', U(tam_t, 800), MARFIL, 1.0),
              (P['c3'], U(tam_t, 800), 'oro', 1.0),
              (' cada uno', U(tam_t, 800), MARFIL, 1.0)]
    texto_partes(lienzo, M, y_titular, partes)


# Maquetas (px 1x). zona = zona segura que se comprueba al final.
#  4x5   : feed (1080x1350), margen 72 por los cuatro lados.
#  9x16  : SOLO Stories (1080x1920): libre el 14 % de arriba y de abajo (y 270-1650).
#  reels : Reels (1080x1920): libre el 14 % de arriba y el 35 % de abajo (y 270-1248)
#          y el 6 % de cada lado; sin botón propio (Meta pone «Comprar» debajo).
MAQUETAS = {
    '4x5': dict(
        W=1080, H=1350, M=76, zona=(72, 72, 1008, 1278), nombre='4x5',
        L=dict(logo_y=104, logo=27, gancho_y=160, gancho=33, titular_y=224, titular=56,
               par=703, base_y=740,
               prod1_y=786, prod1=23, apple_y=815, apple=21,
               sel_y=862, sel=25, cable=21,
               tes_y=880, tes_alto=238,
               conf_y=1152, conf=22,
               boton_y=1168, boton_alto=52, boton=24,
               legal_y=1247, legal=21, legal_dy=26, legal_lineas=2),
        tam=dict(gap=16, radio=18, etq=25, etq_y=42, precio=56, precio_y=106, cada=23.5, cada_y=137,
                 total=27, total_y=171, pastilla=25, pastilla_y=207, pastilla_alto=42, pastilla_pad=17,
                 lanz=20, lanz_y=154)),
    '9x16': dict(
        W=1080, H=1920, M=76, zona=(72, 270, 1008, 1650), nombre='9x16',
        L=dict(logo_y=312, logo=29, gancho_y=380, gancho=35, titular_y=452, titular=58,
               par=788, base_y=1030,
               prod1_y=1080, prod1=24, apple_y=1112, apple=22,
               sel_y=1168, sel=27, cable=23,
               tes_y=1188, tes_alto=258,
               conf_y=1484, conf=23,
               boton_y=1502, boton_alto=62, boton=27,
               legal_y=1596, legal=23, legal_dy=29, legal_lineas=2),
        tam=dict(gap=16, radio=20, etq=27, etq_y=46, precio=60, precio_y=114, cada=25, cada_y=147,
                 total=28, total_y=183, pastilla=27, pastilla_y=222, pastilla_alto=46, pastilla_pad=18,
                 lanz=21.5, lanz_y=164)),
    'reels': dict(
        W=1080, H=1920, M=76, zona=(65, 270, 1015, 1248), nombre='9x16_reels',
        L=dict(logo_y=306, logo=27, gancho_y=356, gancho=31, titular_y=414, titular=54,
               par=557, base_y=828,
               prod1_y=869, prod1=21, apple_y=896, apple=20,
               sel_y=939, sel=24, cable=20,
               tes_y=955, tes_alto=226,
               conf_y=1210, conf=21,
               boton_y=None,
               legal_y=1237, legal=20.5, legal_dy=0, legal_lineas=1),
        tam=dict(gap=16, radio=18, etq=24, etq_y=38, precio=54, precio_y=98, cada=22.5, cada_y=131,
                 total=26, total_y=163, pastilla=24, pastilla_y=197, pastilla_alto=38, pastilla_pad=16,
                 lanz=19.5, lanz_y=148)),
}


def componer(formato, var):
    cfg = VARIANTES[var]
    P = precios(cfg['precio_1'])
    lanz = cfg['lanzamiento']
    mq = MAQUETAS[formato]
    W1, H1, M, L, tam = mq['W'], mq['H'], mq['M'], mq['L'], mq['tam']
    W, H = W1 * K, H1 * K
    cx = W1 / 2
    ELEMENTOS.clear()
    img = fondo(W, H, cx * K, L['base_y'] * K, L['par'] * K)
    img, caja = poner_producto(img, L['par'] * K, cx * K, L['base_y'] * K)
    lienzo = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))

    logo(lienzo, M, L['logo_y'], L['logo'])
    titular(lienzo, M, L['gancho_y'], L['titular_y'], W1 - 2 * M, P, L['gancho'], L['titular'])

    # «Cada pack:» deja claro que la foto es UN pack
    t1 = L['prod1']
    ancho_1 = (A(100, 600).getlength(TXT['pack'] + TXT['producto']) / K) / 100
    t1 = min(t1, (W1 - 2 * M) / ancho_1)
    texto_partes(lienzo, cx, L['prod1_y'], [(TXT['pack'], A(t1, 700), ORO_CLARO, 1.0),
                                            (TXT['producto'], A(t1, 600), MARFIL, 0.96)], anchor_h='m')
    texto(lienzo, (cx, L['apple_y']), TXT['apple'], A(L['apple'], 500), MARFIL, anchor='ms', alpha=0.68)

    texto(lienzo, (M, L['sel_y']), TXT['selector'], A(L['sel'], 700), MARFIL)
    texto(lienzo, (W1 - M, L['sel_y']), TXT['cable'], A(L['cable'], 600), MARFIL, anchor='rs', alpha=0.96)
    escalera(lienzo, M, L['tes_y'], W1 - 2 * M, L['tes_alto'], P, lanz, tam)

    texto(lienzo, (cx, L['conf_y']), TXT['confianza'], A(L['conf'], 500), MARFIL, anchor='ms', alpha=0.90)
    if L['boton_y'] is not None:
        boton(lienzo, cx, L['boton_y'], L['boton_alto'], TXT['boton'], A(L['boton'], 700))
    fl = A(L['legal'], 500)
    if L['legal_lineas'] == 2:
        lineas = [TXT['legal_ahorro'].format(p1=P['p1']), TXT['legal_marca']]
    else:
        lineas = [TXT['legal']]
    for n, ln in enumerate(lineas):
        texto(lienzo, (cx, L['legal_y'] + n * L['legal_dy']), ln, fl, MARFIL, anchor='ms', alpha=LEGAL_ALFA)

    ELEMENTOS.append(('producto', tuple(v / K for v in caja)))
    zona = mq['zona']
    malos = [(t, b) for t, b in ELEMENTOS if b[0] < zona[0] or b[1] < zona[1] or b[2] > zona[2] or b[3] > zona[3]]
    xs0 = min(b[0] for _, b in ELEMENTOS); ys0 = min(b[1] for _, b in ELEMENTOS)
    xs1 = max(b[2] for _, b in ELEMENTOS); ys1 = max(b[3] for _, b in ELEMENTOS)
    print(f'  contenido: x {xs0:.0f}-{xs1:.0f}, y {ys0:.0f}-{ys1:.0f}', 'FUERA DE MÁRGENES:' if malos else 'márgenes OK', malos or '')
    sufijo = mq['nombre'] + var
    nombre = f'anuncio_{sufijo}'
    final = lienzo.resize((W1, H1), Image.LANCZOS)
    final.save(os.path.join(AQUI, nombre + '.png'), optimize=True)
    final.resize((540, H1 // 2), Image.LANCZOS).save(os.path.join(AQUI, f'vista_{sufijo}.png'))
    final.resize((360, H1 // 3), Image.LANCZOS).save(os.path.join(TRAB, f'movil360_{sufijo}.png'))
    lienzo.save(os.path.join(TRAB, f'lienzo2x_{sufijo}.png'))
    print(nombre, 'producto (1x):', tuple(round(v / K) for v in caja), P)


if __name__ == '__main__':
    trabajos = sys.argv[1:] or ['4x5', '9x16', 'reels', '4x5_dic', '9x16_dic', 'reels_dic']
    for t in trabajos:
        f, _, v = t.partition('_')
        componer(f, '_' + v if v else '')
