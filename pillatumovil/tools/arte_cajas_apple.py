"""Artes de las cajas Apple (adaptador 20 W y cable USB-C 60 W) recreados en vectorial, nítidos a cualquier tamaño.

21/11/2026. El dueño: «las cajas del cargador [tienen que verse] totalmente reales, no mal hechas con un diseño cutre».
Las texturas de antes salían de sus fotos (`fotos/caja3d/`): reales pero blandas de cerca. Aquí cada texto, el logo y
los iconos se dibujan de nuevo, en su sitio y a su tamaño, medidos sobre esas caras rectificadas (milímetros de la caja).
La foto del producto de la cara de delante sale de nuestro propio render 3D (`tools/producto3d.py`).

Uso: python3 arte_cajas_apple.py SALIDA_DIR [--producto-cargador PNG] [--producto-cable PNG] [--pxmm 40]
Salida: {cargador,cable}-{frente,trasera,lado,tapa,base}.png + pestana.png (PNG RGB, papel blanco).
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SAL = sys.argv[1]; os.makedirs(SAL, exist_ok=True)
def arg(n, d=None): return sys.argv[sys.argv.index(n) + 1] if n in sys.argv else d
PXMM = float(arg('--pxmm', 40)); SS = 2                      # se dibuja al doble y se reduce: bordes suaves
AQUI = os.path.dirname(os.path.abspath(__file__))
INTER = '/usr/share/fonts/opentype/inter/Inter-{}.otf'
JP = arg('--fuente-jp', os.path.join(AQUI, 'fuentes', 'NotoSansJP-500.ttf'))
LOGO = arg('--logo', os.path.join(AQUI, 'fuentes', 'apple.svg'))
PAPEL = (247, 247, 245); NEGRO = (29, 29, 31); GRIS = (66, 66, 69); GRIS_C = (96, 96, 100); VERDE = (140, 200, 30)
MM = {'cargador': (67.5, 80.0, 29.5), 'cable': (67.0, 65.5, 23.0)}   # ancho, alto, fondo (fichas de tienda y fotos frontales)


def px(v): return int(round(v * PXMM * SS))


class Lienzo:
    def __init__(s, w_mm, h_mm):
        s.im = Image.new('RGB', (px(w_mm), px(h_mm)), PAPEL); s.d = ImageDraw.Draw(s.im)

    def texto(s, x, y_base, t, tam, peso='Regular', col=NEGRO, jp=False):
        """x, y_base en mm; y_base es la línea base. tam = altura del cuerpo en mm (cap height ≈ 0,73·tam en Inter)."""
        partes = [(t, False)] if not jp else _trozos_jp(t)
        cx = px(x)
        for trozo, es_jp in partes:
            f = ImageFont.truetype(JP if es_jp else INTER.format(peso), px(tam))
            s.d.text((cx, px(y_base)), trozo, font=f, fill=col, anchor='ls')
            cx += s.d.textlength(trozo, font=f)
        return cx / (PXMM * SS)

    def logo(s, x, y, alto):
        from svgpathtools import svg2paths
        rutas, _ = svg2paths(LOGO)
        pts = []
        for r in rutas:
            for sub in r.continuous_subpaths():
                n = max(60, int(sub.length() * 40))
                pts.append([sub.point(i / n) for i in range(n + 1)])
        todos = np.concatenate([np.array(p) for p in pts])
        x0, y0 = todos.real.min(), todos.imag.min(); h = todos.imag.max() - y0
        e = px(alto) / h
        capa = Image.new('L', s.im.size, 0); dc = ImageDraw.Draw(capa)
        for p in pts:                                             # par-impar: el bocado y la hoja salen solos
            poly = [(px(x) + (q.real - x0) * e, px(y) + (q.imag - y0) * e) for q in p]
            m = Image.new('L', s.im.size, 0); ImageDraw.Draw(m).polygon(poly, fill=255)
            capa = Image.fromarray(np.bitwise_xor(np.asarray(capa), np.asarray(m)))
        s.im.paste(Image.new('RGB', s.im.size, NEGRO), (0, 0), capa)

    def linea(s, x0, y0, x1, y1, grosor, col=GRIS_C):
        s.d.line([(px(x0), px(y0)), (px(x1), px(y1))], fill=col, width=max(1, px(grosor)))

    def usb_c(s, x, y, w, h, grosor, col=(70, 70, 74)):
        s.d.rounded_rectangle((px(x), px(y), px(x + w), px(y + h)), radius=px(h / 2), outline=col, width=px(grosor))

    def reciclar(s, cx, cy, r, grosor, col=NEGRO):
        """Las tres flechas del símbolo de reciclaje (triángulo de flechas)."""
        import math
        for k in range(3):
            a0 = math.radians(90 + k * 120)
            v = [(cx + r * math.cos(a0 + math.radians(j * 120)), cy - r * math.sin(a0 + math.radians(j * 120))) for j in (0, 1)]
            (ax, ay), (bx, by) = v
            ux, uy = bx - ax, by - ay
            p0 = (ax + ux * 0.18, ay + uy * 0.18); p1 = (ax + ux * 0.70, ay + uy * 0.70)
            s.d.line([(px(p0[0]), px(p0[1])), (px(p1[0]), px(p1[1]))], fill=col, width=px(grosor))
            l = math.hypot(ux, uy); ux, uy = ux / l, uy / l; nx, ny = -uy, ux; t = r * 0.28
            punta = (p1[0] + ux * t, p1[1] + uy * t)
            s.d.polygon([(px(punta[0]), px(punta[1])), (px(p1[0] + nx * t * 0.6), px(p1[1] + ny * t * 0.6)),
                         (px(p1[0] - nx * t * 0.6), px(p1[1] - ny * t * 0.6))], fill=col)

    def glifo(s, ch, x, y, alto, col=NEGRO):
        """Iconos de reciclaje con los glifos de DejaVu (♺ el triángulo de flechas, ♲ el de Möbius)."""
        f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', px(alto) * 2)
        b = s.d.textbbox((0, 0), ch, font=f); e = px(alto) / (b[3] - b[1])
        f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', max(1, int(px(alto) * 2 * e)))
        b = s.d.textbbox((0, 0), ch, font=f)
        s.d.text((px(x) - b[0], px(y) - b[1]), ch, font=f, fill=col)

    def ce(s, x, y, alto, grosor, col=(40, 40, 44)):
        r = alto / 2
        for k, cx in enumerate((x + r, x + alto * 1.18 + r)):
            s.d.arc((px(cx - r), px(y), px(cx + r), px(y + alto)), 50, 310, fill=col, width=px(grosor))
            if k == 1: s.d.line([(px(cx - r * 0.55), px(y + r)), (px(cx + r * 0.62), px(y + r))], fill=col, width=px(grosor))

    def flecha_verde(s, cx, cy, r):
        s.d.ellipse((px(cx - r), px(cy - r), px(cx + r), px(cy + r)), fill=VERDE)
        g = r * 0.16; s.d.line([(px(cx - r * 0.45), px(cy)), (px(cx + r * 0.42), px(cy))], fill=(255, 255, 255), width=px(g))
        s.d.line([(px(cx + r * 0.02), px(cy - r * 0.42)), (px(cx + r * 0.46), px(cy)), (px(cx + r * 0.02), px(cy + r * 0.42))],
                 fill=(255, 255, 255), width=px(g), joint='curve')

    def tira(s, w_mm, alto):
        """Tira de apertura arriba de la trasera: silueta de lengüeta con el extremo derecho redondeado."""
        s.d.rounded_rectangle((px(-alto), px(-alto), px(w_mm * 0.92), px(alto)), radius=px(alto * 0.9),
                              outline=(178, 178, 182), width=px(0.12), fill=(250, 250, 249))

    def producto(s, ruta, x, y, w):
        if not ruta or not os.path.exists(ruta): return
        p = Image.open(ruta).convert('RGBA'); p = p.crop(p.getbbox()); e = px(w) / p.width
        p = p.resize((px(w), int(p.height * e)), Image.LANCZOS)
        s.im.paste(p, (px(x), px(y)), p)

    def guarda(s, nombre):
        im = s.im.resize((s.im.width // SS, s.im.height // SS), Image.LANCZOS)
        im.save(os.path.join(SAL, nombre)); print('ok', nombre, im.size)


def _trozos_jp(t):
    out, cur, jp = [], '', None
    for ch in t:
        es = ord(ch) > 0x2E80
        if jp is None or es == jp: cur += ch
        else: out.append((cur, jp)); cur = ch
        jp = es
    if cur: out.append((cur, jp))
    return out


# ---------------- caja del adaptador 20 W (67,5 x 80 mm de frente; posiciones medidas en fotos frontales) ----------------
W, H, F = MM['cargador']
c = Lienzo(W, H)
c.logo(4.7, 2.4, 5.4)
c.texto(5.1, 13.6, 'USB-C', 3.55, 'SemiBold')
c.texto(5.1, 17.4, '20W Power Adapter', 3.55, 'Regular', GRIS)
c.producto(arg('--producto-cargador'), 19.3, 21.6, 26.5)
c.guarda('cargador-frente.png')

c = Lienzo(W, H)                                   # arriba queda el sitio del precinto (pegatina 3D aparte)
for i, t in enumerate(['20W USB-C Power Adapter', 'Adaptateur secteur USB-C de 20 W', 'Alimentatore USB-C da 20 W',
                       'Adaptador de corriente USB-C de 20 W', '20W USB-C電源アダプタ']):
    c.texto(5.1, 15.6 + i * 3.3, t, 2.2, 'SemiBold', NEGRO, jp=True)
c.usb_c(53.6, 13.9, 8.4, 2.7, 0.7); c.texto(54.8, 20.2, 'USB-C', 1.85, 'Regular', GRIS_C)
c.linea(5.1, 32.0, 62.4, 32.0, 0.15)
c.glifo('♺', 5.1, 34.6, 5.4)
c.texto(5.1, 43.4, 'Please recycle this box.', 2.2, 'SemiBold')
for i, t in enumerate(['Please recycle this box. / Veuillez recycler cette boîte. /', 'Ricicla questa confezione. / Recicla esta caja. /',
                       'この箱はリサイクルしてください。']):
    c.texto(5.1, 46.1 + i * 2.1, t, 1.5, 'Regular', GRIS, jp=True)
c.texto(5.2, 68.8, 'Apple', 2.0, 'Medium', GRIS)
for i, t in enumerate(['Apple Inc., One Apple Park Way, Cupertino,', 'CA 95014 USA. apple.com © 2025 Apple Inc.',
                       'All rights reserved.  602-06556-A']):
    c.texto(5.2, 71.5 + i * 2.1, t, 1.5, 'Regular', GRIS_C)
c.ce(45.2, 70.4, 3.9, 0.5); c.glifo('♲', 55.0, 70.0, 4.6, (60, 60, 64))
c.guarda('cargador-trasera.png')

# ---------------- caja del cable USB-C 60 W (67 x 65 mm de frente) ----------------
W, H, F = MM['cable']
c = Lienzo(W, H)
c.logo(5.9, 4.5, 5.4)
c.texto(6.0, 15.4, 'USB-C', 3.2, 'SemiBold')
c.texto(6.0, 19.6, '60W Charge Cable (1 m)', 3.25, 'Regular', GRIS)
c.producto(arg('--producto-cable'), 17.6, 28.9, 32.7)
c.guarda('cable-frente.png')

c = Lienzo(W, H)
for i, t in enumerate(['60W USB-C Charge Cable (1 m)', 'Câble de charge USB-C 60 W (1 m)', '60W USB-C Ladekabel (1 m)',
                       'Cavo di ricarica USB-C de 60 W (1 m)', 'Cable de carga  USB-C de 60 W (1 m)',
                       'Cabo para Recarga USB-C de 60 W (1 m)', '60W  USB-C充電ケーブル (1 m)']):
    c.texto(7.3, 14.6 + i * 3.05, t, 2.15, 'Medium', NEGRO, jp=True)
c.usb_c(52.6, 13.9, 10.0, 4.0, 0.95); c.texto(54.3, 22.4, 'USB-C', 1.8, 'Regular', GRIS_C)
c.linea(7.3, 35.6, 64.5, 35.6, 0.16)
c.texto(7.4, 40.8, 'Please recycle this box.', 2.15, 'SemiBold')
for i, t in enumerate(['Please recycle this box. / Veuillez recycler cette boîte. / Bitte', 'recycle diese Box. / Ricicla questa confezione. / Recicla esta',
                       'caja. / Recicla esta caixa. / この箱はリサイクルしてください。']):
    c.texto(7.4, 43.6 + i * 2.05, t, 1.5, 'Medium', GRIS, jp=True)
c.texto(7.6, 55.6, 'Apple', 2.0, 'Medium', GRIS)
for i, t in enumerate(['Apple Inc., One Apple Park Way, Cupertino,', 'CA 95014 USA. apple.com © 2025 Apple Inc.',
                       'All rights reserved.  602-06727-B']):
    c.texto(7.6, 58.4 + i * 2.05, t, 1.5, 'Regular', GRIS_C)
c.ce(47.8, 57.4, 3.9, 0.5); c.glifo('♲', 56.6, 57.0, 4.6, (60, 60, 64))
c.guarda('cable-trasera.png')

# ---------------- precinto (pegatina 3D aparte, producto3d.precinto): píldora con el círculo verde en el extremo izquierdo ----
PRECINTO = {'cargador': (59.4, 9.2), 'cable': (55.6, 9.5)}       # largo y alto (mm), medidos en fotos de compradores
for n, (largo, alto) in PRECINTO.items():
    c = Lienzo(largo, alto)
    c.d.rectangle((0, 0, c.im.width, c.im.height), fill=(250, 250, 249))
    c.flecha_verde(alto / 2, alto / 2, 2.9)                       # círculo de unos 5,8 mm, centrado en el extremo redondo
    c.guarda(f'{n}-precinto.png')

# ---------------- lados, tapa y base: cartón blanco liso, como en las fotos ----------------
for n in ('cargador', 'cable'):
    W, H, F = MM[n]
    for cara, (a, b) in {'lado': (F, H), 'tapa': (W, F), 'base': (W, F)}.items():
        Lienzo(a, b).guarda(f'{n}-{cara}.png')
