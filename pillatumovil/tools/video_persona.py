"""Vídeo con dependienta 9:16 (10/11/2026): clip Seedance hablado + subtítulos + precio + cierre.

Uso: python3 video_persona.py CLIP.mp4 FUENTES_DIR SALIDA.mp4

- Subtítulos palabra a palabra sincronizados con la voz (faster-whisper),
  abajo, sin tapar la cara ni las cajas. En Reels y TikTok casi todos ven sin sonido.
- Mientras dice el precio salen «18,99 €» y «En Apple, 38,00 € (precio del 01/11/2026)».
- Al final, tarjeta fija de 2,5 s: plazo real, envío y botón pillatumovil.com.
"""
import subprocess, sys, tempfile
from faster_whisper import WhisperModel
from PIL import Image, ImageDraw, ImageFilter, ImageFont

clip, fuentes, salida = sys.argv[1:4]
W, H = 1080, 1920
NOCHE = (11, 15, 26); ORO = (214, 180, 112); MARFIL = (244, 241, 234); ROJO = (196, 38, 46)


def unb(t, w=700):
    f = ImageFont.truetype(f'{fuentes}/Unbounded.ttf', t); f.set_variation_by_axes([w]); return f


def arc(t, w=600):
    f = ImageFont.truetype(f'{fuentes}/Archivo.ttf', t); f.set_variation_by_axes([w, 100]); return f


# 1) palabras con tiempos
m = WhisperModel('small', device='cpu', compute_type='int8')
segs, _ = m.transcribe(clip, language='es', word_timestamps=True)
palabras = [(w.word.strip(), w.start, w.end) for s in segs for w in s.words]
print(' '.join(p for p, _, _ in palabras))

# 2) grupos de 2-4 palabras (cortes en pausas y signos)
grupos, cur = [], []
for p, a, b in palabras:
    cur.append((p, a, b))
    if len(cur) >= 4 or p[-1:] in '.,?!:' or (len(cur) >= 2 and len(' '.join(x[0] for x in cur)) > 18):
        grupos.append(cur); cur = []
if cur:
    grupos.append(cur)

FS = unb(64, 800)
Y_SUB = 1600


def capa_sub(txt):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    txt = txt.upper()
    tw = d.textlength(txt, font=FS)
    x = (W - tw) / 2
    d.text((x, Y_SUB), txt, font=FS, fill=(255, 255, 255), stroke_width=7, stroke_fill=(0, 0, 0))
    return im


def capa_precio():
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((170, 150, W - 170, 420), radius=40, fill=NOCHE + (225,))
    f = unb(130); t = '18,99 €'
    d.text(((W - d.textlength(t, font=f)) / 2, 170), t, font=f, fill=ORO)
    f2 = arc(30, 600); t2 = 'En Apple, 38,00 € (precio del 01/11/2026)'
    d.text(((W - d.textlength(t2, font=f2)) / 2, 350), t2, font=f2, fill=MARFIL)
    return im


def cierre(fondo_png):
    bg = Image.open(fondo_png).convert('RGB').filter(ImageFilter.GaussianBlur(6))
    bg = Image.blend(bg, Image.new('RGB', bg.size, NOCHE), .55)
    d = ImageDraw.Draw(bg)
    def c(y, t, f, col): d.text(((W - d.textlength(t, font=f)) / 2, y), t, font=f, fill=col)
    c(560, 'pillatumovil', unb(84), MARFIL)
    c(700, 'Cargador 20 W + cable · originales de Apple', arc(34), MARFIL)
    c(790, '18,99 €', unb(170), ORO)
    c(1010, 'En Apple, 38,00 € (precio del 01/11/2026)', arc(30, 500), MARFIL)
    d.rounded_rectangle((90, 1100, W - 90, 1180), radius=40, fill=ROJO)
    c(1122, 'Precio de lanzamiento · hasta el jueves 12/11, 18:00', arc(30, 800), (255, 255, 255))
    c(1220, 'Envío gratis · llega a su casa en 24-48 h', arc(34, 700), MARFIL)
    d.rounded_rectangle((110, 1320, W - 110, 1430), radius=55, fill=ORO)
    c(1352, 'pillatumovil.com  →', unb(46), NOCHE)
    return bg


tmp = tempfile.mkdtemp()
capas = []
for i, g in enumerate(grupos):
    a = g[0][1]
    b = grupos[i + 1][0][1] if i + 1 < len(grupos) else g[-1][2] + .3
    capas.append((capa_sub(' '.join(x[0] for x in g)), a, b))
# precio: desde «treinta y ocho»/«38» hasta el final de «menos»
ini = next((a for p, a, _ in palabras if p.lower().strip('.,') in ('treinta', '38')), 7.0)
fin = next((b for p, _, b in palabras if p.lower().strip('.,') == 'menos'), ini + 4)
capas.append((capa_precio(), ini, fin))
for i, (im, _, _) in enumerate(capas):
    im.save(f'{tmp}/c{i}.png')

subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-sseof', '-0.1', '-i', clip, '-frames:v', '1', '-vf', f'scale={W}:{H}', f'{tmp}/ult.png'], check=True)
cierre(f'{tmp}/ult.png').save(f'{tmp}/cierre.png')
ins = ['-i', clip] + sum([['-i', f'{tmp}/c{i}.png'] for i in range(len(capas))], [])
fc = f'[0:v]scale={W}:{H}:flags=lanczos,setsar=1,format=yuv420p[v0];'
for i, (_, a, b) in enumerate(capas):
    fc += f"[v{i}][{i+1}:v]overlay=0:0:enable='between(t,{a:.2f},{b:.2f})'[v{i+1}];"
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *ins, '-filter_complex', fc.rstrip(';'), '-map', f'[v{len(capas)}]', '-map', '0:a?',
                '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-c:a', 'aac', '-b:a', '160k', '-ar', '44100', '-ac', '2', '-r', '30', f'{tmp}/a.mp4'], check=True)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-loop', '1', '-t', '2.5', '-i', f'{tmp}/cierre.png', '-f', 'lavfi', '-t', '2.5', '-i', 'anullsrc=r=44100:cl=stereo',
                '-vf', 'format=yuv420p,fade=in:0:8', '-c:v', 'libx264', '-crf', '18', '-r', '30', '-c:a', 'aac', '-shortest', f'{tmp}/b.mp4'], check=True)
open(f'{tmp}/l.txt', 'w').write(f"file '{tmp}/a.mp4'\nfile '{tmp}/b.mp4'\n")
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', f'{tmp}/l.txt', '-c:v', 'libx264', '-crf', '19', '-c:a', 'aac', '-movflags', '+faststart', salida], check=True)
print('ok', salida)
