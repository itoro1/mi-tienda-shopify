"""Anuncio 10/11/2026: «Escena Premium» con urgencia REAL.
Uso: python3 anuncio_urgencia.py FOTOS_DIR FUENTES_DIR SALIDA_DIR
- Franja arriba: «PRECIO DE LANZAMIENTO · SOLO HASTA EL JUEVES 12/11, 18:00».
  Es verdad: a esa hora el pack individual sube a 19,99 € (Routine programada).
- «Envío gratis · llega a su casa en 24-48 h» junto al precio.
"""
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

NOCHE = (11, 15, 26); ORO = (214, 180, 112); MARFIL = (244, 241, 234); GRIS = (168, 174, 190); ROJO = (196, 38, 46)
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
    f = unb(38); tw = d.textlength(texto, font=f); l, t, r, b = d.textbbox((0, 0), texto, font=f)
    tx = (x0 + x1 - tw - 60) / 2; ty = y0 + (y1 - y0 - (b - t)) / 2 - t
    d.text((tx, ty), texto, font=f, fill=NOCHE)
    ax = tx + tw + 18; ay = (y0 + y1) / 2
    d.line([(ax, ay), (ax + 36, ay)], fill=NOCHE, width=6); d.polygon([(ax + 46, ay), (ax + 28, ay - 14), (ax + 28, ay + 14)], fill=NOCHE)

def reloj(d, cx, cy, r, col):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=col, width=4)
    d.line([(cx, cy), (cx, cy - r * .6)], fill=col, width=4); d.line([(cx, cy), (cx + r * .5, cy)], fill=col, width=4)

def anuncio(nombre, W, H):
    st = H > 1500
    esc = Image.open(f'{fotos}/fondos/escena-premium-2.png').convert('RGB')
    esc = esc.resize((W, int(W * esc.height / esc.width)), Image.LANCZOS)
    esc_h, y_esc = (1230, 120) if st else (1140, 60)
    esc = esc.crop((0, y_esc, W, y_esc + esc_h))
    im = Image.new('RGB', (W, H), NOCHE); im.paste(esc, (0, 0))
    fade = Image.new('L', (W, 140), 0); fd = ImageDraw.Draw(fade)
    for i in range(140): fd.line([(0, i), (W, i)], fill=int(255 * (i / 140) ** 1.6))
    im.paste(Image.new('RGB', (W, 140), NOCHE), (0, esc_h - 140), fade)
    d = ImageDraw.Draw(im)
    # franja de urgencia
    fy = (esc_h - 140) if st else 0; fh = 76
    d.rectangle((0, fy, W, fy + fh), fill=ROJO)
    txt = 'PRECIO DE LANZAMIENTO · SOLO HASTA EL JUEVES 12/11, 18:00'
    f = arc(29, 800); tw = d.textlength(txt, font=f)
    x = (W - tw - 46) / 2
    reloj(d, x + 16, fy + fh / 2, 15, (255, 255, 255))
    d.text((x + 46, fy + 21), txt, font=f, fill=(255, 255, 255))
    # panel
    y = esc_h - (34 if st else 74)
    if st:
        centro(d, y, 'Cargador 20 W + cable USB‑C o Lightning · originales de Apple', arc(30, 600), MARFIL, W); y += 48
    fp = unb(96); precio = '18,99 €'; pw = d.textlength(precio, font=fp)
    l1, l2 = 'cada pack · En Apple, 38,00 €', '(precio del 01/11/2026)'
    fn = arc(27, 500); nw = max(d.textlength(l1, font=fn), d.textlength(l2, font=arc(21)))
    x = (W - (pw + 32 + nw)) / 2
    d.text((x, y), precio, font=fp, fill=ORO)
    d.text((x + pw + 32, y + 22), l1, font=fn, fill=MARFIL)
    d.text((x + pw + 32, y + 58), l2, font=arc(21), fill=GRIS)
    by = (H - 330 - 130) if st else (H - 118)
    centro(d, by - 44, 'Envío gratis · llega a su casa en 24-48 h', arc(28, 700), MARFIL, W)
    boton(im, 70, by, W - 70, by + 92, 'pillatumovil.com')
    im.save(f'{salida}/{nombre}', quality=94)

anuncio('pillatumovil_urgencia_U_feed-4x5.jpg', 1080, 1350)
anuncio('pillatumovil_urgencia_U_stories-9x16.jpg', 1080, 1920)
