"""Anuncio 09/11/2026 (v5): fondo de tienda (Higgsfield, vacío) + producto REAL encima.

Uso: python3 anuncio_boutique.py FOTOS_DIR FUENTES_DIR SALIDA_DIR
- Fondo: fotos/fondos/tienda-ia-2.png, generado vacío (sin marcas ni producto).
- Producto: fotos/recortes/pro_cajas.png (foto de estudio real, recortada).
- Sombra de contacto + sombra proyectada hacia la derecha (luz de la ventana).
- Gancho arriba, panel noche con precio, comparación con fecha, ventajas y botón.
"""
import sys
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

NOCHE = (11, 15, 26); ORO = (214, 180, 112); MARFIL = (244, 241, 234); GRIS = (168, 174, 190)
fotos, fuentes, salida = sys.argv[1:4]

def unb(t, w=700):
    f = ImageFont.truetype(f'{fuentes}/Unbounded.ttf', t); f.set_variation_by_axes([w]); return f
def arc(t, w=500):
    f = ImageFont.truetype(f'{fuentes}/Archivo.ttf', t); f.set_variation_by_axes([w, 100]); return f

def escena(W, H, base_frac):
    bg = Image.open(f'{fotos}/fondos/tienda-ia-2.png').convert('RGB')
    bg = ImageOps.fit(bg, (W, int(W * bg.height / bg.width)), Image.LANCZOS)
    y0 = int(bg.height * .14); bg = bg.crop((0, y0, W, y0 + H))
    if bg.height < H:
        bg = ImageOps.fit(Image.open(f'{fotos}/fondos/tienda-ia-2.png').convert('RGB'), (W, H), Image.LANCZOS, centering=(.5, .85))
    # desenfoque extra del fondo (por encima del tablero) para que mande el producto
    mesa = int(bg.height * base_frac) - 60
    m = Image.new('L', bg.size, 0); ImageDraw.Draw(m).rectangle((0, 0, W, mesa), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(40))
    bg = Image.composite(bg.filter(ImageFilter.GaussianBlur(5)), bg, m)
    bg = ImageEnhance.Brightness(bg).enhance(.96)
    return bg

def poner(bg, prod, x, base):
    W, H = prod.size; y = base - H
    a = prod.getchannel('A')
    # sombra proyectada (luz desde la izquierda): silueta inclinada hacia la derecha
    sh = a.resize((W, int(H * .22)))
    lien = Image.new('L', bg.size, 0)
    sk = sh.transform(sh.size, Image.AFFINE, (1, -1.2, 0, 0, 1, 0), Image.BICUBIC)
    lien.paste(sk, (x + int(W * .08), base - int(H * .22) + 10), sk)
    lien = ImageOps.flip(lien.crop((0, 0, bg.width, bg.height)))
    lien = Image.new('L', bg.size, 0)
    ImageDraw.Draw(lien).polygon([(x + W * .1, base), (x + W * .98, base), (x + W * 1.25, base + 70), (x + W * .3, base + 70)], fill=110)
    lien = lien.filter(ImageFilter.GaussianBlur(26))
    bg.paste(Image.new('RGB', bg.size, (70, 48, 25)), (0, 0), lien)
    c = Image.new('L', bg.size, 0)
    ImageDraw.Draw(c).ellipse((x + 10, base - 14, x + W - 10, base + 16), fill=190)
    c = c.filter(ImageFilter.GaussianBlur(10))
    bg.paste(Image.new('RGB', bg.size, (45, 30, 15)), (0, 0), c)
    # tono cálido del producto para que case con la luz de la tienda
    r, g, b, al = prod.split()
    r = r.point(lambda v: min(255, int(v * 1.03))); b = b.point(lambda v: int(v * .95))
    p = Image.merge('RGBA', (r, g, b, al))
    bg.paste(p, (x, y), p)

def check(d, x, y, s, col):
    d.line([(x, y + s * .55), (x + s * .38, y + s * .9), (x + s, y + s * .15)], fill=col, width=max(3, s // 7))

def boton(im, x0, y0, x1, y1, texto):
    s = Image.new('L', im.size, 0); ImageDraw.Draw(s).rounded_rectangle((x0, y0 + 10, x1, y1 + 10), radius=(y1 - y0) // 2, fill=150)
    im.paste(Image.new('RGB', im.size, (0, 0, 0)), (0, 0), s.filter(ImageFilter.GaussianBlur(14)))
    d = ImageDraw.Draw(im); d.rounded_rectangle((x0, y0, x1, y1), radius=(y1 - y0) // 2, fill=ORO)
    f = unb(42); tw = d.textlength(texto, font=f); l, t, r, b = d.textbbox((0, 0), texto, font=f)
    tx = (x0 + x1 - tw - 60) / 2; ty = y0 + (y1 - y0 - (b - t)) / 2 - t
    d.text((tx, ty), texto, font=f, fill=NOCHE)
    ax = tx + tw + 18; ay = (y0 + y1) / 2
    d.line([(ax, ay), (ax + 36, ay)], fill=NOCHE, width=6); d.polygon([(ax + 46, ay), (ax + 28, ay - 14), (ax + 28, ay + 14)], fill=NOCHE)

def anuncio(gancho, nombre, W, H):
    st = H > 1500
    esc_h = 1100 if st else 1010
    bg = escena(W, esc_h, .9)
    prod = Image.open(f'{fotos}/recortes/pro_cajas.png').convert('RGBA')
    ph = 470 if st else 430
    prod = prod.resize((int(prod.width * ph / prod.height), ph), Image.LANCZOS)
    poner(bg, prod, (W - prod.width) // 2, esc_h - 125)
    im = Image.new('RGB', (W, H), NOCHE); im.paste(bg, (0, 0))
    # fundido escena -> panel
    fade = Image.new('L', (W, 120), 0); fd = ImageDraw.Draw(fade)
    for i in range(120): fd.line([(0, i), (W, i)], fill=int(255 * (i / 120) ** 1.5))
    im.paste(Image.new('RGB', (W, 120), NOCHE), (0, esc_h - 120), fade)
    # velo claro arriba para leer el gancho
    top = 250 if st else 54
    v = Image.new('L', (W, H), 0); ImageDraw.Draw(v).rectangle((0, 0, W, top + 200), fill=170)
    im.paste(Image.new('RGB', (W, H), (250, 246, 238)), (0, 0), v.filter(ImageFilter.GaussianBlur(50)))
    d = ImageDraw.Draw(im); y = top
    for l in gancho:
        f = unb(64); d.text(((W - d.textlength(l, font=f)) / 2, y), l, font=f, fill=NOCHE); y += 82
    y = esc_h - 30
    sub = 'Adaptador 20 W + cable USB‑C · originales de Apple'; f = arc(30, 600)
    d.text(((W - d.textlength(sub, font=f)) / 2, y), sub, font=f, fill=MARFIL); y += 50
    fp = unb(100); precio = '18,99 €'; pw = d.textlength(precio, font=fp)
    fn = arc(28, 500); nw = max(d.textlength('En Apple, 38,00 €', font=fn), d.textlength('(precio del 01/11/2026)', font=arc(22)))
    x = (W - (pw + 34 + nw)) / 2
    d.text((x, y), precio, font=fp, fill=ORO)
    d.text((x + pw + 34, y + 24), 'En Apple, 38,00 €', font=fn, fill=MARFIL)
    d.text((x + pw + 34, y + 62), '(precio del 01/11/2026)', font=arc(22), fill=GRIS)
    y += 132
    ticks = ['Precintado', 'Envío gratis 1-2 días', '14 días de devolución']; fx = arc(27, 600)
    tot = sum(34 + d.textlength(t, font=fx) for t in ticks) + 36 * 2; x = (W - tot) / 2
    for t in ticks:
        check(d, x, y + 4, 22, ORO); d.text((x + 34, y), t, font=fx, fill=MARFIL); x += 34 + d.textlength(t, font=fx) + 36
    by = (H - 330 - 130) if st else (H - 122)
    boton(im, 70, by, W - 70, by + 96, 'pillatumovil.com')
    im.save(f'{salida}/{nombre}', quality=94)

for n, g in (('T1', ['¿Su iPhone vino', 'sin cargador?']), ('T2', ['Original de Apple.', 'A mitad de precio.'])):
    anuncio(g, f'pillatumovil_boutique_{n}_feed-4x5.jpg', 1080, 1350)
    anuncio(g, f'pillatumovil_boutique_{n}_stories-9x16.jpg', 1080, 1920)
