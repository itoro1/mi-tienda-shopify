"""Anuncio 09/11/2026 (v2): producto REAL recortado sobre fondo de estudio.

Uso: python3 anuncio_estudio.py RECORTES_DIR FUENTES_DIR SALIDA_DIR

El dueño no quería el fondo de la terraza: «tiene que verse profesional».
Se recortan sus propias fotos (fotos/recortes/*.png, sacadas de fotos/reales)
y se ponen sobre un fondo de estudio oscuro con foco de luz y sombra.
Sigue siendo su producto de verdad; solo cambia el fondo.
E1 «Original de Apple» (cajas delante + cargador + cable).
E2 «¿Es original?» (parte trasera con sello CE + cargador con sus marcas).
"""
import sys
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont

NOCHE = (11, 15, 26)
NOCHE2 = (27, 34, 54)
ORO = (201, 168, 106)
BLANCO = (255, 255, 255)
GRIS = (176, 182, 196)

rec, fuentes, salida = sys.argv[1:4]


def unb(t, w=600):
    f = ImageFont.truetype(f'{fuentes}/Unbounded.ttf', t)
    f.set_variation_by_axes([w])
    return f


def arc(t, w=500):
    f = ImageFont.truetype(f'{fuentes}/Archivo.ttf', t)
    f.set_variation_by_axes([w, 100])
    return f


def pieza(nombre, alto):
    im = Image.open(f'{rec}/{nombre}.png').convert('RGBA')
    im = ImageEnhance.Brightness(im).enhance(1.13)
    im = ImageEnhance.Contrast(im).enhance(1.05)
    w = int(im.width * alto / im.height)
    return im.resize((w, alto), Image.LANCZOS)


def fondo(W, H, cy):
    """Degradado vertical + foco de luz radial centrado en cy."""
    bg = Image.new('RGB', (W, H), NOCHE)
    d = ImageDraw.Draw(bg)
    for y in range(H):
        t = y / H
        c = tuple(int(NOCHE2[i] * (1 - t) + NOCHE[i] * t) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)
    luz = Image.new('L', (W, H), 0)
    ImageDraw.Draw(luz).ellipse((W * .08, cy - W * .42, W * .92, cy + W * .42), fill=120)
    luz = luz.filter(ImageFilter.GaussianBlur(160))
    bg.paste(Image.new('RGB', (W, H), (70, 82, 112)), (0, 0), luz)
    return bg


def poner(bg, im, x, suelo):
    """Coloca la pieza con la base en `suelo`, con sombra de contacto y reflejo."""
    W = im.width
    y = suelo - im.height
    sh = Image.new('L', bg.size, 0)
    ImageDraw.Draw(sh).ellipse((x + W * .06, suelo - 16, x + W * .94, suelo + 22), fill=200)
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    bg.paste(Image.new('RGB', bg.size, (3, 5, 10)), (0, 0), sh)
    ref = im.transpose(Image.FLIP_TOP_BOTTOM).crop((0, 0, W, int(im.height * .28)))
    grad = Image.linear_gradient('L').resize(ref.size).point(lambda v: max(0, 60 - v))
    ref.putalpha(ImageChops.darker(ref.getchannel('A'), grad))
    bg.paste(ref, (x, suelo + 4), ref)
    bg.paste(im, (x, y), im)


def check(d, x, y, s, color):
    d.line([(x, y + s * .55), (x + s * .38, y + s * .9), (x + s, y + s * .15)], fill=color, width=max(3, s // 7))


def centrar(d, y, txt, f, color, W):
    w = d.textlength(txt, font=f)
    d.text(((W - w) / 2, y), txt, font=f, fill=color)


def textos(im, W, y0, sup, titulo):
    d = ImageDraw.Draw(im)
    centrar(d, y0, sup, arc(28, 700), ORO, W)
    y = y0 + 52
    for l in titulo:
        centrar(d, y, l, unb(54, 650), BLANCO, W)
        y += 68
    return d


def bloque_precio(im, W, y, ticks):
    d = ImageDraw.Draw(im)
    fp = unb(104, 700)
    pw = d.textlength('18,99 €', font=fp)
    lado = 'Adaptador 20 W + cable'
    lw = max(d.textlength(lado, font=arc(31, 700)), d.textlength('En Apple, 38,00 €', font=arc(25, 500)))
    x = (W - (pw + 34 + lw)) / 2
    d.text((x, y), '18,99 €', font=fp, fill=BLANCO)
    px = x + pw + 34
    d.text((px, y + 18), lado, font=arc(31, 700), fill=BLANCO)
    d.text((px, y + 58), 'En Apple, 38,00 €', font=arc(25, 500), fill=GRIS)
    d.text((px, y + 88), '(precio del 01/11/2026)', font=arc(21, 500), fill=GRIS)
    y += 150
    fx = arc(28, 600)
    total = sum(40 + d.textlength(t, font=fx) for t in ticks) + 40 * (len(ticks) - 1)
    x = (W - total) / 2
    for t in ticks:
        check(d, x, y + 3, 24, ORO)
        d.text((x + 36, y), t, font=fx, fill=BLANCO)
        x += 40 + d.textlength(t, font=fx) + 40
    return y + 50


def barra(im, W, by):
    d = ImageDraw.Draw(im)
    d.rectangle((0, by, W, by + 120), fill=ORO)
    centrar(d, by + 26, 'pillatumovil.com', unb(54, 700), NOCHE, W)


def escena_e1(bg, cx, suelo, k):
    caja_a = pieza('caja_adaptador', int(470 * k))
    caja_c = pieza('caja_cable', int(400 * k))
    carg = pieza('cargador', int(250 * k))
    cable = pieza('cable', int(250 * k))
    poner(bg, caja_a, int(cx - caja_a.width - 10 * k), suelo - int(40 * k))
    poner(bg, caja_c, int(cx + 20 * k), suelo - int(40 * k))
    poner(bg, carg, int(cx - carg.width - 60 * k), suelo + int(40 * k))
    poner(bg, cable, int(cx + 30 * k), suelo + int(40 * k))


def escena_e2(bg, cx, suelo, k):
    tras = pieza('traseras', int(420 * k))
    carg = pieza('cargador', int(300 * k))
    poner(bg, tras, int(cx - tras.width / 2 + 40 * k), suelo - int(30 * k))
    poner(bg, carg, int(cx - tras.width / 2 - 70 * k), suelo + int(50 * k))


def anuncio(escena, sup, titulo, ticks, nombre, W, H):
    stories = H > 1500
    top = 250 if stories else 56
    zona_y = top + 200
    zona_h = 700 if stories else 560
    bg = fondo(W, H, zona_y + zona_h * .5)
    k = 1.1 if stories else 1.0
    escena(bg, W // 2, zona_y + zona_h + (-70 if stories else 50), k)
    textos(bg, W, top, sup, titulo)
    by = H - 330 - 120 if stories else H - 120
    bloque_precio(bg, W, by - 250, ticks)
    barra(bg, W, by)
    bg.save(f'{salida}/{nombre}', quality=93)


E1 = dict(escena=escena_e1, sup='SU IPHONE YA NO TRAE CARGADOR',
          titulo=['Cargador + cable', 'originales de Apple'],
          ticks=['Precintado', 'Envío gratis 1-2 días', '14 días de devolución'])
E2 = dict(escena=escena_e2, sup='¿ORIGINAL O IMITACIÓN?',
          titulo=['Compruébelo: caja', 'de Apple y sello CE'],
          ticks=['Precintado', 'Envío gratis 1-2 días', '14 días de devolución'])

for n, v in (('E1', E1), ('E2', E2)):
    anuncio(v['escena'], v['sup'], v['titulo'], v['ticks'], f'pillatumovil_estudio_{n}_feed-4x5.jpg', 1080, 1350)
    anuncio(v['escena'], v['sup'], v['titulo'], v['ticks'], f'pillatumovil_estudio_{n}_stories-9x16.jpg', 1080, 1920)
