"""Anuncio «problema → solución» 9:16 (13/11/2026): subtítulos, carteles de precio y cierre.

El dueño pidió cambiar el mensaje: primero el problema (la batería dura menos; un cargador
de mala calidad puede calentar el iPhone), luego la solución (pack original a 18,99 €), el
plazo (30/11 o fin de existencias) y el cierre con pillatumovil.com en grande.
La voz (Elena) va por encima de las imágenes: nadie habla a cámara.

Uso: python3 video_problema.py MONTAJE.mp4 FUENTES_DIR SALIDA.mp4 [ESCALA]
MONTAJE.mp4 ya trae la imagen montada y la voz (tools/montaje_problema.sh).
ESCALA 2 = 4K nativo (2160x3840): los textos se dibujan al doble, no se amplían.

Legal: la comparación dice «En Apple, 38,00 € (precio del 01/11/2026)»; la única urgencia es
el plazo real; «o fin de existencias» es condición de la oferta, no aviso de que se acaben.
"""
import subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont

clip, fuentes, salida = sys.argv[1:4]
K = int(sys.argv[4]) if len(sys.argv) > 4 else 1
W, H = 1080 * K, 1920 * K
NOCHE = (11, 15, 26); ORO = (214, 180, 112); MARFIL = (244, 241, 234); ROJO = (196, 38, 46)


def unb(t, w=700):
    f = ImageFont.truetype(f'{fuentes}/Unbounded.ttf', t * K); f.set_variation_by_axes([w]); return f


def arc(t, w=600):
    f = ImageFont.truetype(f'{fuentes}/Archivo.ttf', t * K); f.set_variation_by_axes([w, 100]); return f


# Subtítulos: texto del guion; tiempos medidos con faster-whisper sobre voz-problema-elena.mp3.
# (texto, inicio, fin). El fin es el final de la frase hablada: en los silencios no queda texto colgado.
SUBS = [
    ('¿La batería de su iPhone', 0.00, 1.16), ('dura cada vez menos?', 1.16, 2.60),
    ('Un cargador de mala calidad', 3.20, 4.72), ('puede calentarlo', 4.72, 5.82), ('y castigar la batería.', 5.82, 7.55),
    ('Y los originales son caros:', 7.72, 9.60), ('en Apple, 38 €.', 9.78, 11.75),
    ('En Pillatumovil', 12.24, 13.10), ('tenemos la solución:', 13.10, 14.55), ('adaptador de 20 W y cable,', 14.74, 16.85),
    ('originales de Apple,', 17.16, 18.56), ('por 18,99 €.', 18.56, 20.15),
    ('Solo hasta el 30 de noviembre', 20.76, 22.72), ('o fin de existencias.', 22.72, 24.00),
    ('Envío gratis', 24.30, 25.44), ('en 24-48 h.', 25.44, 27.45),
    ('No se quede sin su pack', 27.54, 29.20), ('a este precio.', 29.20, 30.05), ('Compre en pillatumovil.com', 30.28, 32.40),
]
FIN_VOZ = 32.3
APPLE = (9.70, 12.10)        # cartel «En Apple, 38,00 €»
PRECIO = (18.50, 22.20)      # cartel «18,99 €»
CIERRE = 26.58               # desde aquí, tarjeta de cierre sobre la imagen desenfocada
PASTILLA = 27.50             # la pastilla del plazo entra con «No se quede sin su pack»
FINAL = 33.0
Y_SUB = 1720 * K


def lienzo():
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); return im, ImageDraw.Draw(im)


def centro(d, y, t, f, col, **kw):
    d.text(((W - d.textlength(t, font=f)) / 2, y * K), t, font=f, fill=col, **kw)


def capa_sub(txt):
    im, d = lienzo()
    t = 64; f = unb(t, 800)
    while d.textlength(txt, font=f) > W - 100 * K:
        t -= 4; f = unb(t, 800)
    d.text(((W - d.textlength(txt, font=f)) / 2, Y_SUB), txt, font=f, fill=(255, 255, 255), stroke_width=7 * K, stroke_fill=(0, 0, 0))
    return im


def cartel(grande, color, linea1, linea2=None):
    """Cartel de precio en el tercio inferior: no tapa caras ni cajas."""
    im, d = lienzo()
    alto = 300 if linea2 else 250
    y0 = 1390
    d.rounded_rectangle((150 * K, y0 * K, W - 150 * K, (y0 + alto) * K), radius=40 * K, fill=NOCHE + (232,))
    centro(d, y0 + 18, grande, unb(120), color)
    centro(d, y0 + 180, linea1, arc(30, 600), MARFIL)
    if linea2: centro(d, y0 + 232, linea2, arc(28, 500), MARFIL)
    return im


def cierre(con_pastilla):
    im = Image.new('RGBA', (W, H), NOCHE + (168,)); d = ImageDraw.Draw(im)
    centro(d, 330, 'pillatumovil', unb(84), MARFIL)
    centro(d, 470, 'Cargador 20 W + cable · originales de Apple', arc(34), MARFIL)
    centro(d, 550, '18,99 €', unb(170), ORO)
    centro(d, 775, 'En Apple, 38,00 € (precio del 01/11/2026)', arc(30, 500), MARFIL)
    centro(d, 830, 'Compramos por cantidad y ganamos menos', arc(30, 500), MARFIL)
    if con_pastilla:
        d.rounded_rectangle((70 * K, 915 * K, W - 70 * K, 1000 * K), radius=42 * K, fill=ROJO)
        centro(d, 938, 'Hasta el 30 de noviembre o fin de existencias', arc(32, 800), (255, 255, 255))
    centro(d, 1045, 'Envío gratis · llega a su casa en 24-48 h', arc(34, 700), MARFIL)
    d.rounded_rectangle((70 * K, 1160 * K, W - 70 * K, 1330 * K), radius=85 * K, fill=ORO)
    centro(d, 1203, 'pillatumovil.com', unb(72), NOCHE)
    centro(d, 1365, 'Toque «Comprar» y elija 1, 2 o 3 packs', arc(32, 600), MARFIL)
    return im


tmp = tempfile.mkdtemp()
capas = [(capa_sub(t), ini, fin) for t, ini, fin in SUBS]
capas.insert(0, (cartel('18,99 €', ORO, 'En Apple, 38,00 € (precio del 01/11/2026)', 'Compramos por cantidad y ganamos menos'), *PRECIO))
capas.insert(0, (cartel('38,00 €', MARFIL, 'En Apple (precio del 01/11/2026)'), *APPLE))
capas.insert(0, (cierre(True), PASTILLA, FINAL + 1))
capas.insert(0, (cierre(False), CIERRE, PASTILLA))
for i, (im, _, _) in enumerate(capas):
    im.save(f'{tmp}/c{i}.png')

ins = ['-i', clip] + sum([['-i', f'{tmp}/c{i}.png'] for i in range(len(capas))], [])
# bajo la tarjeta de cierre, la imagen se desenfoca
fc = f"[0:v]scale={W}:{H}:flags=lanczos,setsar=1,gblur=sigma={14 * K}:enable='gte(t,{CIERRE})',format=yuv420p[v0];"
for i, (_, a, b) in enumerate(capas):
    fc += f"[v{i}][{i+1}:v]overlay=0:0:enable='between(t,{a:.2f},{b:.2f})'[v{i+1}];"
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *ins, '-filter_complex', fc.rstrip(';'), '-map', f'[v{len(capas)}]', '-map', '0:a',
                '-t', f'{FINAL}', '-c:v', 'libx264', '-crf', '18' if K > 1 else '17', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-r', '24',
                '-c:a', 'aac', '-b:a', '160k', '-ar', '44100', '-ac', '2', '-movflags', '+faststart', salida], check=True)
print('ok', salida)
