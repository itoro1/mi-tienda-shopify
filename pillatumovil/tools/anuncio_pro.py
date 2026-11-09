"""Anuncio 09/11/2026 (v4): a partir de las fotos de estudio del anuncio que gustaba (Pack A).

Uso: python3 anuncio_pro.py FOTOS_DIR FUENTES_DIR SALIDA_DIR

El dueño: «como el anterior anuncio, se ve bien lo que es el cargador y cable,
pero faltaban retoques profesionales». Y: enganchar en el primer segundo y un
botón claro que lleve a la web.
- Foto grande arriba, retocada (contraste, nitidez, viñeta, tono cálido).
- Gancho arriba en una línea grande.
- Panel noche abajo: precio, comparación con Apple con fecha, 3 ventajas y un
  BOTÓN dorado «Comprar en pillatumovil.com →» (la web en grande y clicable
  a través del botón «Comprar» de Meta).
P1: cargador con el cable puesto (se ve el producto). P2: las dos cajas en el pedestal.
"""
import sys
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

NOCHE = (11, 15, 26)
ORO = (214, 180, 112)
ORO_OSC = (150, 118, 60)
MARFIL = (244, 241, 234)
GRIS = (168, 174, 190)

fotos, fuentes, salida = sys.argv[1:4]


def unb(t, w=650):
    f = ImageFont.truetype(f'{fuentes}/Unbounded.ttf', t)
    f.set_variation_by_axes([w])
    return f


def arc(t, w=500):
    f = ImageFont.truetype(f'{fuentes}/Archivo.ttf', t)
    f.set_variation_by_axes([w, 100])
    return f


def retoque(im):
    im = ImageEnhance.Contrast(im).enhance(1.08)
    im = ImageEnhance.Color(im).enhance(1.04)
    im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
    # tono cálido suave
    r, g, b = im.split()
    r = r.point(lambda v: min(255, int(v * 1.02)))
    b = b.point(lambda v: int(v * 0.97))
    im = Image.merge('RGB', (r, g, b))
    # viñeta
    W, H = im.size
    m = Image.new('L', (W, H), 0)
    ImageDraw.Draw(m).ellipse((-W * .25, -H * .2, W * 1.25, H * 1.2), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(W * .12))
    osc = ImageEnhance.Brightness(im).enhance(.72)
    return Image.composite(im, osc, m)


def cubrir(im, w, h, cx=.5, cy=.5):
    return ImageOps.fit(im, (w, h), Image.LANCZOS, centering=(cx, cy))


def check(d, x, y, s, color):
    d.line([(x, y + s * .55), (x + s * .38, y + s * .9), (x + s, y + s * .15)], fill=color, width=max(3, s // 7))


def boton(im, x0, y0, x1, y1, texto):
    sombra = Image.new('L', im.size, 0)
    ImageDraw.Draw(sombra).rounded_rectangle((x0, y0 + 10, x1, y1 + 10), radius=(y1 - y0) // 2, fill=140)
    sombra = sombra.filter(ImageFilter.GaussianBlur(14))
    im.paste(Image.new('RGB', im.size, (0, 0, 0)), (0, 0), sombra)
    d = ImageDraw.Draw(im)
    # degradado dorado
    h = y1 - y0
    capa = Image.new('RGB', (x1 - x0, h))
    cd = ImageDraw.Draw(capa)
    for y in range(h):
        t = y / h
        cd.line([(0, y), (x1 - x0, y)], fill=tuple(int(ORO[i] * (1 - t * .25) + 255 * 0 * t) for i in range(3)))
    m = Image.new('L', capa.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, x1 - x0 - 1, h - 1), radius=h // 2, fill=255)
    im.paste(capa, (x0, y0), m)
    d.rounded_rectangle((x0 + 3, y0 + 3, x1 - 3, y0 + h // 2), radius=h // 2, outline=None, fill=None)
    f = unb(42, 700)
    tw = d.textlength(texto, font=f)
    flecha = 46
    tx = (x0 + x1 - tw - flecha - 14) / 2
    l, t, r, b = d.textbbox((0, 0), texto, font=f)
    ty = y0 + (h - (b - t)) / 2 - t
    d.text((tx, ty), texto, font=f, fill=NOCHE)
    ax = tx + tw + 18
    ay = y0 + h / 2
    d.line([(ax, ay), (ax + flecha - 6, ay)], fill=NOCHE, width=6)
    d.polygon([(ax + flecha, ay), (ax + flecha - 18, ay - 14), (ax + flecha - 18, ay + 14)], fill=NOCHE)


def anuncio(foto, cx, cy, gancho, color_gancho, sombra_gancho, nombre, W, H, off=0):
    st = H > 1500
    foto_h = 1180 if st else 830
    im = Image.new('RGB', (W, H), NOCHE)
    off = (off + 120) if (st and off) else off
    ph = retoque(cubrir(Image.open(f'{fotos}/{foto}').convert('RGB'), W, foto_h - off, cx, cy))
    # fundido inferior de la foto al panel
    fade = Image.new('L', ph.size, 255)
    fd = ImageDraw.Draw(fade)
    for i in range(160):
        a = int(255 * (i / 160) ** 1.4)
        fd.line([(0, ph.height - 1 - i), (W, ph.height - 1 - i)], fill=a)
        if off:
            fd.line([(0, i), (W, i)], fill=a)
    im.paste(Image.composite(ph, Image.new('RGB', ph.size, NOCHE), fade), (0, off))
    d = ImageDraw.Draw(im)
    # gancho arriba
    top = 250 if st else 60
    if sombra_gancho:
        g = Image.new('L', (W, H), 0)
        ImageDraw.Draw(g).rectangle((0, 0, W, top + 230), fill=150)
        g = g.filter(ImageFilter.GaussianBlur(60))
        im.paste(Image.new('RGB', (W, H), NOCHE), (0, 0), g)
        d = ImageDraw.Draw(im)
    y = top
    for linea in gancho:
        f = unb(66, 700)
        tw = d.textlength(linea, font=f)
        d.text(((W - tw) / 2, y), linea, font=f, fill=color_gancho)
        y += 84
    # panel
    y = foto_h - 40
    sub = 'Adaptador 20 W + cable USB‑C · originales de Apple'
    f = arc(30, 600)
    d.text(((W - d.textlength(sub, font=f)) / 2, y), sub, font=f, fill=MARFIL)
    y += 54
    fp = unb(112, 700)
    precio = '18,99 €'
    pw = d.textlength(precio, font=fp)
    nota1, nota2 = 'En Apple, 38,00 €', '(precio del 01/11/2026)'
    fn = arc(28, 500)
    nw = max(d.textlength(nota1, font=fn), d.textlength(nota2, font=arc(22, 500)))
    x = (W - (pw + 36 + nw)) / 2
    d.text((x, y), precio, font=fp, fill=ORO)
    d.text((x + pw + 36, y + 30), nota1, font=fn, fill=MARFIL)
    d.text((x + pw + 36, y + 70), nota2, font=arc(22, 500), fill=GRIS)
    y += 150
    ticks = ['Precintado', 'Envío gratis 1-2 días', '14 días de devolución']
    fx = arc(28, 600)
    total = sum(36 + d.textlength(t, font=fx) for t in ticks) + 40 * (len(ticks) - 1)
    x = (W - total) / 2
    for t in ticks:
        check(d, x, y + 4, 24, ORO)
        d.text((x + 36, y), t, font=fx, fill=MARFIL)
        x += 36 + d.textlength(t, font=fx) + 40
    by = (H - 330 - 140) if st else (H - 140)
    boton(im, 60, by, W - 60, by + 104, 'pillatumovil.com')
    d = ImageDraw.Draw(im)
    lt = 'Toque «Comprar» y llega a la web'
    f = arc(22, 500)
    d.text(((W - d.textlength(lt, font=f)) / 2, by - 40), lt, font=f, fill=GRIS)
    im.save(f'{salida}/{nombre}', quality=94)


P1 = dict(foto='ps-cargador-con-cable.jpg', cx=.5, cy=.08, off=0, gancho=['¿Su iPhone vino', 'sin cargador?'],
          color=(20, 22, 30), sombra=False)
P2 = dict(foto='ps-estudio-portada.jpg', cx=.7, cy=.5, off=230, gancho=['Original de Apple.', 'A mitad de precio.'],
          color=MARFIL, sombra=True)

for n, v in (('P1', P1), ('P2', P2)):
    for W, H, fmt in ((1080, 1350, 'feed-4x5'), (1080, 1920, 'stories-9x16')):
        anuncio(v['foto'], v['cx'], v['cy'], v['gancho'], v['color'], v['sombra'],
                f'pillatumovil_pro_{n}_{fmt}.jpg', W, H, v['off'])
