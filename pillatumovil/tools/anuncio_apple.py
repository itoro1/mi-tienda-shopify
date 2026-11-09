"""Anuncio 09/11/2026 (v3): estilo Apple, fondo claro de estudio, cajas en 3D.

Uso: python3 anuncio_apple.py FOTOS_DIR FUENTES_DIR SALIDA_DIR

El dueño quería algo «a nivel de estudio, al estilo Apple y las grandes marcas».
Usa las caras limpias de las cajas (fotos/cine/*.png), las monta en 3D con
cara lateral, cara superior, sombra de contacto y reflejo sobre un fondo gris
claro sin costuras. Mucho aire, una sola idea y tipografía sobria.
A1 «Carga original.» (las dos cajas) · A2 «Original. Y se nota.» (trasera con CE).
"""
import sys
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

TINTA = (29, 29, 31)
GRIS = (110, 110, 115)
FONDO_A = (251, 251, 253)
FONDO_B = (232, 232, 237)
ORO = (201, 168, 106)

fotos, fuentes, salida = sys.argv[1:4]


def arc(t, w=600, ancho=100):
    f = ImageFont.truetype(f'{fuentes}/Archivo.ttf', t)
    f.set_variation_by_axes([w, ancho])
    return f


def unb(t, w=700):
    f = ImageFont.truetype(f'{fuentes}/Unbounded.ttf', t)
    f.set_variation_by_axes([w])
    return f


def cara(nombre, alto):
    im = Image.open(f'{fotos}/cine/{nombre}.png').convert('RGBA')
    w = int(im.width * alto / im.height)
    return im.resize((w, alto), Image.LANCZOS)


def tope_cuerpo(im):
    """Primera fila en la que la caja ocupa casi todo el ancho (debajo de la pestaña)."""
    a = im.getchannel('A')
    for y in range(im.height):
        fila = a.crop((0, y, im.width, y + 1))
        if sum(1 for v in fila.get_flattened_data() if v > 200) > im.width * .9:
            return y
    return 0


def caja3d(frente, prof=.26, sube=.30):
    """Caja vista un poco desde la izquierda y desde arriba: frente + lateral + tapa."""
    w, h = frente.size
    d = int(w * prof)
    dy = int(d * sube)
    ty = tope_cuerpo(frente)
    lienzo = Image.new('RGBA', (w + d, h + dy), (0, 0, 0, 0))
    dr = ImageDraw.Draw(lienzo)
    # lateral derecho (degradado gris)
    lat = Image.new('RGBA', (d, h - ty), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lat)
    for x in range(d):
        t = x / d
        c = int(222 - 30 * t)
        ld.line([(x, 0), (x, h - ty)], fill=(c, c, c + 4, 255))
    mask = Image.new('L', (d, h - ty + dy), 0)
    ImageDraw.Draw(mask).polygon([(0, dy), (d, 0), (d, h - ty), (0, h - ty + dy)], fill=255)
    lat_full = Image.new('RGBA', (d, h - ty + dy), (0, 0, 0, 0))
    lat_full.paste(lat.resize((d, h - ty + dy)), (0, 0))
    lienzo.paste(lat_full, (w, ty), mask)
    # tapa
    dr.polygon([(0, ty + dy), (d, ty), (w + d, ty), (w, ty + dy)], fill=(246, 246, 248, 255))
    # frente (un pelo más oscuro abajo, como con luz cenital)
    fr = frente.copy()
    som = Image.linear_gradient('L').resize(fr.size).point(lambda v: int(v * .10))
    oscuro = Image.new('RGBA', fr.size, (0, 0, 0, 255))
    oscuro.putalpha(ImageChops.multiply(som, fr.getchannel('A')))
    fr = Image.alpha_composite(fr, oscuro)
    lienzo.alpha_composite(fr, (0, dy))
    # arista
    dr.line([(w, ty + dy), (w, h + dy - 1)], fill=(255, 255, 255, 180), width=2)
    return lienzo


def fondo(W, H, suelo):
    bg = Image.new('RGB', (W, H), FONDO_A)
    d = ImageDraw.Draw(bg)
    for y in range(H):
        t = min(1, max(0, (y - suelo * .55) / (suelo * .55)))
        c = tuple(int(FONDO_A[i] * (1 - t) + FONDO_B[i] * t) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)
    # suelo un poco más claro (luz que rebota)
    luz = Image.new('L', (W, H), 0)
    ImageDraw.Draw(luz).ellipse((W * .1, suelo - 60, W * .9, suelo + 220), fill=90)
    luz = luz.filter(ImageFilter.GaussianBlur(70))
    bg.paste(Image.new('RGB', (W, H), (255, 255, 255)), (0, 0), luz)
    return bg


def poner(bg, im, x, suelo):
    W, H = im.size
    y = suelo - H
    sh = Image.new('L', bg.size, 0)
    sd = ImageDraw.Draw(sh)
    sd.ellipse((x - W * .02, suelo - 18, x + W * 1.04, suelo + 30), fill=110)
    sh = sh.filter(ImageFilter.GaussianBlur(22))
    bg.paste(Image.new('RGB', bg.size, (120, 120, 128)), (0, 0), sh)
    cs = Image.new('L', bg.size, 0)
    ImageDraw.Draw(cs).rectangle((x + 6, suelo - 4, x + W - 6, suelo + 4), fill=150)
    cs = cs.filter(ImageFilter.GaussianBlur(5))
    bg.paste(Image.new('RGB', bg.size, (70, 70, 76)), (0, 0), cs)
    ref = im.transpose(Image.FLIP_TOP_BOTTOM).crop((0, 0, W, int(H * .22)))
    grad = Image.linear_gradient('L').resize(ref.size).point(lambda v: max(0, 38 - v))
    ref.putalpha(ImageChops.darker(ref.getchannel('A'), grad))
    bg.paste(ref, (x, suelo + 2), ref)
    bg.paste(im, (x, y), im)


def centrar(d, y, txt, f, color, W, tracking=0):
    w = d.textlength(txt, font=f) + tracking * (len(txt) - 1)
    x = (W - w) / 2
    if not tracking:
        d.text((x, y), txt, font=f, fill=color)
        return
    for ch in txt:
        d.text((x, y), ch, font=f, fill=color)
        x += d.textlength(ch, font=f) + tracking


def escena_a1(bg, cx, suelo, k):
    a = caja3d(cara('caja-cargador-frente', int(470 * k)))
    c = caja3d(cara('caja-cable-usbc-frente', int(500 * k)))
    poner(bg, c, int(cx - c.width + 40 * k), suelo - int(30 * k))
    poner(bg, a, int(cx - 70 * k), suelo)


def escena_a2(bg, cx, suelo, k):
    f = caja3d(cara('caja-cargador-frente', int(470 * k)))
    t = caja3d(cara('caja-cargador-trasera', int(470 * k)))
    poner(bg, f, int(cx - f.width + 40 * k), suelo - int(30 * k))
    poner(bg, t, int(cx - 70 * k), suelo)


def anuncio(escena, kicker, titulo, sub, nombre, W, H):
    st = H > 1500
    top = 240 if st else 70
    suelo = (1190 if st else 880)
    bg = fondo(W, H, suelo)
    escena(bg, W // 2, suelo, 1.12 if st else 1.0)
    d = ImageDraw.Draw(bg)
    centrar(d, top, kicker, arc(26, 650), ORO, W, tracking=3)
    centrar(d, top + 46, titulo, arc(84, 700, 92), TINTA, W, tracking=-2)
    centrar(d, top + 150, sub, arc(31, 450), GRIS, W)
    # precio
    y = suelo + 60
    fp = arc(80, 700)
    precio = '18,99 €'
    pw = d.textlength(precio, font=fp)
    nota = 'En Apple, 38,00 € (precio del 01/11/2026)'
    centrar(d, y, precio, fp, TINTA, W)
    centrar(d, y + 100, nota, arc(23, 450), GRIS, W)
    centrar(d, y + 140, 'Precintado  ·  Envío gratis en 1-2 días  ·  14 días de devolución',
            arc(24, 550), TINTA, W)
    # web abajo
    by = H - 330 - 120 if st else H - 120
    d.rectangle((0, by, W, by + 120), fill=TINTA)
    centrar(d, by + 30, 'pillatumovil.com', unb(52, 650), (255, 255, 255), W)
    if st:
        d.rectangle((0, by + 120, W, H), fill=TINTA)
    bg.save(f'{salida}/{nombre}', quality=94)


A1 = dict(escena=escena_a1, kicker='ORIGINAL DE APPLE', titulo='Carga original.',
          sub='Adaptador 20 W + cable USB‑C. Precintados.')
A2 = dict(escena=escena_a2, kicker='¿ORIGINAL O IMITACIÓN?', titulo='Original. Se nota.',
          sub='Caja de Apple, precinto y sello CE.')

for n, v in (('A1', A1), ('A2', A2)):
    anuncio(v['escena'], v['kicker'], v['titulo'], v['sub'], f'pillatumovil_apple_{n}_feed-4x5.jpg', 1080, 1350)
    anuncio(v['escena'], v['kicker'], v['titulo'], v['sub'], f'pillatumovil_apple_{n}_stories-9x16.jpg', 1080, 1920)
