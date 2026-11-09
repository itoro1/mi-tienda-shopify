"""Anuncio 09/11/2026 (v6): escena completa de tienda con letrero LED «pillatumovil».

Uso: python3 anuncio_escena.py FOTOS_DIR FUENTES_DIR SALIDA_DIR
- Escena: fotos/fondos/escena-packs-1.png. Higgsfield (gpt_image_2_6) a partir del fondo
  LED (fotos/fondos/tienda-led-1.png) y las caras reales de las cajas (fotos/cine/*.png).
  Muestra los 2 packs (cargador + cable USB‑C y cargador + cable Lightning) apoyados en
  el mostrador, con iPhones en la estantería del fondo.
- Abajo, panel noche con precio, comparación con su fecha y un botón grande a la web.
"""
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

NOCHE = (11, 15, 26); ORO = (214, 180, 112); MARFIL = (244, 241, 234); GRIS = (168, 174, 190)
fotos, fuentes, salida = sys.argv[1:4]

def unb(t, w=700):
    f = ImageFont.truetype(f'{fuentes}/Unbounded.ttf', t); f.set_variation_by_axes([w]); return f
def arc(t, w=500):
    f = ImageFont.truetype(f'{fuentes}/Archivo.ttf', t); f.set_variation_by_axes([w, 100]); return f
def centro(d, y, s, f, col, W):
    d.text(((W - d.textlength(s, font=f)) / 2, y), s, font=f, fill=col)

def boton(im, x0, y0, x1, y1, texto):
    s = Image.new('L', im.size, 0); ImageDraw.Draw(s).rounded_rectangle((x0, y0 + 10, x1, y1 + 10), radius=(y1 - y0) // 2, fill=150)
    im.paste(Image.new('RGB', im.size, (0, 0, 0)), (0, 0), s.filter(ImageFilter.GaussianBlur(14)))
    d = ImageDraw.Draw(im); d.rounded_rectangle((x0, y0, x1, y1), radius=(y1 - y0) // 2, fill=ORO)
    f = unb(40); tw = d.textlength(texto, font=f); l, t, r, b = d.textbbox((0, 0), texto, font=f)
    tx = (x0 + x1 - tw - 60) / 2; ty = y0 + (y1 - y0 - (b - t)) / 2 - t
    d.text((tx, ty), texto, font=f, fill=NOCHE)
    ax = tx + tw + 18; ay = (y0 + y1) / 2
    d.line([(ax, ay), (ax + 36, ay)], fill=NOCHE, width=6); d.polygon([(ax + 46, ay), (ax + 28, ay - 14), (ax + 28, ay + 14)], fill=NOCHE)

def anuncio(sup, nombre, W, H):
    st = H > 1500
    esc = Image.open(f'{fotos}/fondos/escena-packs-1.png').convert('RGB')
    esc = esc.resize((W, int(W * esc.height / esc.width)), Image.LANCZOS)   # 1080 x 1350
    if st:
        esc_h = 1230; y_esc = 120
    else:
        esc_h = 1140; y_esc = 60          # se ven las cajas enteras; el panel va sobre el mostrador
    esc = esc.crop((0, y_esc, W, y_esc + esc_h))
    im = Image.new('RGB', (W, H), NOCHE); im.paste(esc, (0, 0))
    fade = Image.new('L', (W, 140), 0); fd = ImageDraw.Draw(fade)
    for i in range(140): fd.line([(0, i), (W, i)], fill=int(255 * (i / 140) ** 1.6))
    im.paste(Image.new('RGB', (W, 140), NOCHE), (0, esc_h - 140), fade)
    d = ImageDraw.Draw(im)
    if st:
        y = esc_h - 34
        centro(d, y, sup, arc(30, 600), MARFIL, W); y += 48
    else:
        y = esc_h - 74
    fp = unb(96); precio = '18,99 €'; pw = d.textlength(precio, font=fp)
    fn = arc(27, 500); nw = max(d.textlength('cada pack · En Apple, 38,00 €', font=fn), d.textlength('(precio del 01/11/2026)', font=arc(21)))
    x = (W - (pw + 32 + nw)) / 2
    d.text((x, y), precio, font=fp, fill=ORO)
    d.text((x + pw + 32, y + 22), 'cada pack · En Apple, 38,00 €', font=fn, fill=MARFIL)
    d.text((x + pw + 32, y + 58), '(precio del 01/11/2026)', font=arc(21), fill=GRIS)
    by = (H - 330 - 130) if st else (H - 118)
    if st:
        centro(d, y + 140, 'Precintados · Envío gratis 1-2 días · 14 días de devolución', arc(27, 600), MARFIL, W)
    boton(im, 70, by, W - 70, by + 92, 'pillatumovil.com')
    im.save(f'{salida}/{nombre}', quality=94)

SUP = 'Cargador 20 W + cable USB‑C o Lightning · originales de Apple'
anuncio(SUP, 'pillatumovil_escena_E_feed-4x5.jpg', 1080, 1350)
anuncio(SUP, 'pillatumovil_escena_E_stories-9x16.jpg', 1080, 1920)
