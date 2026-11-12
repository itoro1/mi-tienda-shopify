"""Vídeo con dependienta 9:16 (10/11/2026): clip Seedance hablado + subtítulos + precio + cierre.

Uso: python3 video_persona.py CLIP.mp4 FUENTES_DIR SALIDA.mp4 [v1|v2|v3] [RETRASO_VOZ_S] [ESCALA]
ESCALA 2 = 4K nativo (2160x3840): los textos se dibujan al doble, no se amplían.

- Subtítulos con el texto exacto del guion, sincronizados con la voz,
  abajo, sin tapar la cara ni las cajas. En Reels y TikTok casi todos ven sin sonido.
- Mientras dice el precio salen «18,99 €» y «En Apple, 38,00 € (precio del 01/11/2026)».
- Al final, tarjeta fija de 2,5 s: plazo real, envío y botón pillatumovil.com.
"""
import subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFilter, ImageFont

clip, fuentes, salida = sys.argv[1:4]
VERSION = sys.argv[4] if len(sys.argv) > 4 else 'v2'
RETRASO = float(sys.argv[5]) if len(sys.argv) > 5 else 0.0
K = int(sys.argv[6]) if len(sys.argv) > 6 else 1   # 2 = 4K nativo
W, H = 1080 * K, 1920 * K
NOCHE = (11, 15, 26); ORO = (214, 180, 112); MARFIL = (244, 241, 234); ROJO = (196, 38, 46)


def unb(t, w=700):
    f = ImageFont.truetype(f'{fuentes}/Unbounded.ttf', t * K); f.set_variation_by_axes([w]); return f


def arc(t, w=600):
    f = ImageFont.truetype(f'{fuentes}/Archivo.ttf', t * K); f.set_variation_by_axes([w, 100]); return f


# 1) subtítulos: texto exacto del guion; tiempos sacados de la voz con
#    faster-whisper (word_timestamps) y fijados aquí para el clip Seedance 11423373.
SUBS_V1 = [
    ('¿Su iPhone vino', 0.00), ('sin cargador?', 0.68), ('Normal,', 1.42), ('Apple ya no lo pone.', 1.98),
    ('Aquí tiene los dos:', 2.92), ('adaptador de 20 W', 3.76), ('y cable.', 4.68), ('Originales de Apple,', 5.24),
    ('precintados.', 5.94), ('En Apple le cuestan', 6.84), ('38 euros.', 7.56), ('Aquí, 18,99.', 8.40),
    ('Compramos por cantidad', 9.70), ('y ganamos menos.', 10.38), ('Envío gratis', 11.40),
    ('en 24-48 h', 12.02), ('en su casa.', 12.98), ('Hasta el jueves.', 13.66), ('Toque «Comprar».', 14.44),
]
# v2 (11/11): voz ElevenLabs «Elena» + vídeo Intone 5630c05b con 5 planos; tiempos medidos
#    con faster-whisper sobre el clip final (clip-intone-broll.mp4).
SUBS_V2 = [
    ('¿Su iPhone vino', 0.0), ('sin cargador?', 1.0), ('Normal:', 2.3), ('Apple ya no lo pone.', 3.2),
    ('Aquí tiene los dos:', 4.9), ('adaptador de 20 W', 6.3), ('y cable.', 7.9), ('Originales de Apple,', 8.9),
    ('en su caja sin abrir.', 10.3), ('En Apple, 38 €.', 12.4), ('Aquí, 18,99 €.', 15.2),
    ('Compramos por cantidad', 17.9), ('y ganamos menos.', 19.0), ('Envío gratis', 21.0),
    ('en 24-48 h.', 22.0), ('Dese prisa:', 24.5), ('este precio acaba el jueves.', 25.6), ('Toque «Comprar».', 27.0),
]
# v3 (11/11): oferta ampliada al 30/11. Se cambió la frase final por la voz nueva
#    (voz-frase-30nov.mp3) sobre un plano de los dos packs; todo lo de después va 0,5 s más tarde.
SUBS_V3 = SUBS_V2[:-3] + [('Dese prisa:', 24.4), ('este precio acaba el 30/11.', 25.5), ('Toque «Comprar».', 28.28)]
PLAZO = {'v1': 'hasta el jueves 12/11, 18:00', 'v2': 'hasta el jueves 12/11, 18:00', 'v3': 'hasta el 30 de noviembre'}[VERSION]
if VERSION == 'v1':
    SUBS, FIN_VOZ, PRECIO = SUBS_V1, 15.0, (6.84, 11.30)
elif VERSION == 'v2':
    SUBS, FIN_VOZ, PRECIO = SUBS_V2, 28.8, (12.4, 17.8)
else:
    SUBS, FIN_VOZ, PRECIO = SUBS_V3, 29.3, (12.4, 17.8)
SUBS = [(t, x + RETRASO) for t, x in SUBS]
FIN_VOZ += RETRASO
PRECIO = (PRECIO[0] + RETRASO, PRECIO[1] + RETRASO)

Y_SUB = 1720 * K


def capa_sub(txt):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    t = 64; f = unb(t, 800)
    while d.textlength(txt, font=f) > W - 100 * K:
        t -= 4; f = unb(t, 800)
    tw = d.textlength(txt, font=f)
    x = (W - tw) / 2
    d.text((x, Y_SUB), txt, font=f, fill=(255, 255, 255), stroke_width=7 * K, stroke_fill=(0, 0, 0))
    return im


def capa_precio():
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((170 * K, 150 * K, W - 170 * K, 420 * K), radius=40 * K, fill=NOCHE + (225,))
    f = unb(130); t = '18,99 €'
    d.text(((W - d.textlength(t, font=f)) / 2, 170 * K), t, font=f, fill=ORO)
    f2 = arc(30, 600); t2 = 'En Apple, 38,00 € (precio del 01/11/2026)'
    d.text(((W - d.textlength(t2, font=f2)) / 2, 350 * K), t2, font=f2, fill=MARFIL)
    return im


def cierre(fondo_png):
    bg = Image.open(fondo_png).convert('RGB').filter(ImageFilter.GaussianBlur(6 * K))
    bg = Image.blend(bg, Image.new('RGB', bg.size, NOCHE), .55)
    d = ImageDraw.Draw(bg)
    def c(y, t, f, col): d.text(((W - d.textlength(t, font=f)) / 2, y * K), t, font=f, fill=col)
    c(560, 'pillatumovil', unb(84), MARFIL)
    c(700, 'Cargador 20 W + cable · originales de Apple', arc(34), MARFIL)
    c(790, '18,99 €', unb(170), ORO)
    c(1010, 'En Apple, 38,00 € (precio del 01/11/2026)', arc(30, 500), MARFIL)
    d.rounded_rectangle((90 * K, 1100 * K, W - 90 * K, 1180 * K), radius=40 * K, fill=ROJO)
    c(1122, f'Precio de lanzamiento · {PLAZO}', arc(30, 800), (255, 255, 255))
    c(1220, 'Envío gratis · llega a su casa en 24-48 h', arc(34, 700), MARFIL)
    d.rounded_rectangle((110 * K, 1320 * K, W - 110 * K, 1430 * K), radius=55 * K, fill=ORO)
    c(1352, 'pillatumovil.com  →', unb(46), NOCHE)
    return bg


tmp = tempfile.mkdtemp()
capas = []
for i, (t, ini) in enumerate(SUBS):
    fin = SUBS[i + 1][1] if i + 1 < len(SUBS) else FIN_VOZ
    capas.append((capa_sub(t), ini, fin))
capas.append((capa_precio(), *PRECIO))
for i, (im, _, _) in enumerate(capas):
    im.save(f'{tmp}/c{i}.png')

subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-sseof', '-0.5', '-i', clip, '-frames:v', '1', '-vf', f'scale={W}:{H}', f'{tmp}/ult.png'], check=True)
cierre(f'{tmp}/ult.png').save(f'{tmp}/cierre.png')
ins = ['-i', clip] + sum([['-i', f'{tmp}/c{i}.png'] for i in range(len(capas))], [])
fc = f'[0:v]scale={W}:{H}:flags=lanczos,setsar=1,format=yuv420p[v0];'
for i, (_, a, b) in enumerate(capas):
    fc += f"[v{i}][{i+1}:v]overlay=0:0:enable='between(t,{a:.2f},{b:.2f})'[v{i+1}];"
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *ins, '-filter_complex', fc.rstrip(';'), '-map', f'[v{len(capas)}]', '-map', '0:a?',
                '-c:v', 'libx264', '-crf', '14' if K > 1 else '18', '-preset', 'medium', '-c:a', 'aac', '-b:a', '160k', '-ar', '44100', '-ac', '2', '-r', '24', f'{tmp}/a.mp4'], check=True)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-loop', '1', '-t', '2.5', '-i', f'{tmp}/cierre.png', '-f', 'lavfi', '-t', '2.5', '-i', 'anullsrc=r=44100:cl=stereo',
                '-vf', 'format=yuv420p,fade=in:0:8', '-c:v', 'libx264', '-crf', '14' if K > 1 else '18', '-r', '24', '-c:a', 'aac', '-shortest', f'{tmp}/b.mp4'], check=True)
open(f'{tmp}/l.txt', 'w').write(f"file '{tmp}/a.mp4'\nfile '{tmp}/b.mp4'\n")
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', f'{tmp}/l.txt', '-c:v', 'libx264', '-crf', '18' if K > 1 else '19', '-c:a', 'aac', '-movflags', '+faststart', salida], check=True)
print('ok', salida)
