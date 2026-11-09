"""Anuncio nuevo (09/11/2026): foto REAL del stock, no de estudio.

Uso: python3 anuncio_real.py FOTOS_REALES_DIR FUENTES_DIR SALIDA_DIR

Por qué así (ver anuncios/2026-11/LEEME.md, sección 09/11):
- La gente añadía al carrito pero no compraba: falta confianza. La foto real,
  con las cajas de Apple, el precinto y la etiqueta trasera, da más confianza
  que una foto de estudio.
- Precio grande y comparación con Apple, con fecha (regla Omnibus).
- La web en grande abajo, sobre oro.
Dos versiones: R1 «Foto real» (cajas por delante) y R2 «¿Es original?»
(cajas por detrás, con precinto y sello CE).
"""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageOps

NOCHE = (11, 15, 26)
ORO = (201, 168, 106)
ORO_T = (125, 95, 40)
MARFIL = (244, 241, 234)
BLANCO = (255, 255, 255)

fotos, fuentes, salida = sys.argv[1:4]


def unb(t, w=600):
    f = ImageFont.truetype(f'{fuentes}/Unbounded.ttf', t)
    f.set_variation_by_axes([w])
    return f


def arc(t, w=500):
    f = ImageFont.truetype(f'{fuentes}/Archivo.ttf', t)
    f.set_variation_by_axes([w, 100])
    return f


def recorte(img, w, h, cy):
    """Recorta a w:h manteniendo todo el ancho; cy = centro vertical (0-1)."""
    img = ImageOps.exif_transpose(img).convert('RGB')
    W, H = img.size
    ch = int(W * h / w)
    y0 = max(0, min(H - ch, int(H * cy - ch / 2)))
    return img.crop((0, y0, W, y0 + ch)).resize((w, h), Image.LANCZOS)


def pastilla(d, x, y, texto, f, fondo, color, pad=(22, 12)):
    l, t, r, b = d.textbbox((0, 0), texto, font=f)
    w, h = r - l + pad[0] * 2, b - t + pad[1] * 2
    d.rounded_rectangle((x, y, x + w, y + h), radius=h // 2, fill=fondo)
    d.text((x + pad[0] - l, y + pad[1] - t), texto, font=f, fill=color)
    return w, h


def check(d, x, y, s, color):
    d.line([(x, y + s * .55), (x + s * .38, y + s * .9), (x + s, y + s * .15)], fill=color, width=max(3, s // 7))


def anuncio(foto, cy, H, foto_h, sup, titulo, ticks, nombre, bar_y=None):
    W = 1080
    im = Image.new('RGB', (W, H), MARFIL)
    im.paste(recorte(Image.open(f'{fotos}/{foto}'), W, foto_h, cy), (0, 0))
    d = ImageDraw.Draw(im)
    top = 250 if H > 1500 else 36
    pastilla(d, 36, top, 'FOTO REAL · NUESTRO STOCK', arc(26, 700), NOCHE, BLANCO)

    y = foto_h + 34
    d.text((60, y), sup, font=arc(32, 600), fill=ORO_T)
    y += 50
    for linea in titulo:
        d.text((60, y), linea, font=unb(50), fill=NOCHE)
        y += 64
    y += 14
    # precio
    fp = unb(96, 700)
    d.text((56, y - 10), '18,99 €', font=fp, fill=NOCHE)
    px = 60 + d.textlength('18,99 €', font=fp) + 30
    d.text((px, y + 8), 'Adaptador 20 W + cable', font=arc(30, 700), fill=NOCHE)
    d.text((px, y + 46), 'En Apple, 38,00 € (precio del 01/11/2026)', font=arc(24, 500), fill=(90, 90, 90))
    y += 128
    fx = arc(29, 600)
    for t in ticks:
        check(d, 62, y + 4, 26, ORO_T)
        d.text((104, y), t, font=fx, fill=NOCHE)
        y += 44
    # barra de la web
    bh = 120
    by = bar_y if bar_y else H - bh
    d.rectangle((0, by, W, by + bh), fill=ORO)
    fw = unb(54, 700)
    tw = d.textlength('pillatumovil.com', font=fw)
    d.text(((W - tw) / 2, by + 26), 'pillatumovil.com', font=fw, fill=NOCHE)
    if bar_y:
        d.rectangle((0, by + bh, W, H), fill=NOCHE)
    im.save(f'{salida}/{nombre}', quality=92)


R1 = dict(foto='cajas-frente-usb-c.jpg', cy=0.66,
          sup='Su iPhone ya no trae cargador.',
          titulo=['Cargador + cable', 'originales de Apple'],
          ticks=['Precintado, en su caja de Apple', 'Envío gratis: le llega en 1-2 días',
                 '14 días para devolverlo'])
R2 = dict(foto='cajas-traseras-y-producto.jpg', cy=0.62,
          sup='¿Original o imitación? Compruébelo.',
          titulo=['Caja de Apple, precinto', 'y sello CE'],
          ticks=['Fotos reales, no de catálogo', 'Envío gratis: le llega en 1-2 días',
                 '14 días para devolverlo'])

for n, v in (('R1', R1), ('R2', R2)):
    anuncio(v['foto'], v['cy'], 1350, 750, v['sup'], v['titulo'], v['ticks'],
            f'pillatumovil_real_{n}_feed-4x5.jpg')
    anuncio(v['foto'], v['cy'], 1920, 960, v['sup'], v['titulo'], v['ticks'],
            f'pillatumovil_real_{n}_stories-9x16.jpg', bar_y=1920 - 330 - 120)
