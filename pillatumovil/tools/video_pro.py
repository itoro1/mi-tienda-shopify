"""Vídeo pro 9:16 (10/11/2026): clip Kling + textos exactos + cierre con precio y web.
Uso: python3 video_pro.py CLIP.mp4 FUENTES_DIR SALIDA.mp4
Guion (lo que funciona en Reels/TikTok: gancho en 1 s, una idea por plano, cierre con CTA):
 0-2,5 s  «¿Su iPhone vino sin cargador?»          (gancho: el problema)
 2,5-6 s  «Originales de Apple · Precintados»        (confianza)
 6-10 s   «18,99 €  ·  En Apple, 38,00 €» + envío    (precio ancla)
 10-12,5 s cierre fijo: plazo real + botón pillatumovil.com
"""
import os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFilter, ImageFont

clip, fuentes, salida = sys.argv[1:4]
W, H = 1080, 1920
NOCHE = (11, 15, 26); ORO = (214, 180, 112); MARFIL = (244, 241, 234); ROJO = (196, 38, 46)
def unb(t, w=700):
    f = ImageFont.truetype(f'{fuentes}/Unbounded.ttf', t); f.set_variation_by_axes([w]); return f
def arc(t, w=600):
    f = ImageFont.truetype(f'{fuentes}/Archivo.ttf', t); f.set_variation_by_axes([w, 100]); return f

def capa(lineas, y, sombra=True):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if sombra:
        s = Image.new('L', (W, H), 0); ImageDraw.Draw(s).rectangle((0, y - 60, W, y + 70 * len(lineas) + 90), fill=150)
        im.paste((0, 0, 0, 255), (0, 0), s.filter(ImageFilter.GaussianBlur(50)).point(lambda v: v * 0.8))
        d = ImageDraw.Draw(im)
    for txt, f, col in lineas:
        tw = d.textlength(txt, font=f); d.text(((W - tw) / 2, y), txt, font=f, fill=col); y += f.size + 26
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
capas = [
    (capa([('¿Su iPhone vino', unb(78), MARFIL), ('sin cargador?', unb(78), MARFIL)], 660), 0.0, 2.6),
    (capa([('Originales de Apple', unb(64), MARFIL), ('Precintados · en su caja', arc(44), ORO)], 680), 2.6, 6.0),
    (capa([('18,99 €', unb(140), ORO), ('En Apple, 38,00 € (precio del 01/11/2026)', arc(32, 500), MARFIL), ('Envío gratis · 24-48 h', arc(40, 700), MARFIL)], 600), 6.0, 10.0),
]
for i, (im, a, b) in enumerate(capas): im.save(f'{tmp}/c{i}.png')
# último fotograma del clip -> fondo del cierre
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-sseof', '-0.1', '-i', clip, '-frames:v', '1', '-vf', f'scale={W}:{H}', f'{tmp}/ult.png'], check=True)
cierre(f'{tmp}/ult.png').save(f'{tmp}/cierre.png')
ins = ['-i', clip] + sum([['-i', f'{tmp}/c{i}.png'] for i in range(len(capas))], [])
fc = f'[0:v]scale={W}:{H},setsar=1,format=yuv420p[v0];'
for i, (_, a, b) in enumerate(capas):
    fc += f"[v{i}][{i+1}:v]overlay=0:0:enable='between(t,{a},{b})'[v{i+1}];"
fc = fc.rstrip(';')
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *ins, '-filter_complex', fc, '-map', f'[v{len(capas)}]', '-map', '0:a?',
                '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-c:a', 'aac', '-b:a', '160k', '-r', '30', f'{tmp}/a.mp4'], check=True)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-loop', '1', '-t', '2.5', '-i', f'{tmp}/cierre.png', '-f', 'lavfi', '-t', '2.5', '-i', 'anullsrc=r=44100:cl=stereo',
                '-vf', 'format=yuv420p,fade=in:0:8', '-c:v', 'libx264', '-crf', '18', '-r', '30', '-c:a', 'aac', '-shortest', f'{tmp}/b.mp4'], check=True)
open(f'{tmp}/l.txt', 'w').write(f"file '{tmp}/a.mp4'\nfile '{tmp}/b.mp4'\n")
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', f'{tmp}/l.txt', '-c:v', 'libx264', '-crf', '19', '-c:a', 'aac', '-movflags', '+faststart', salida], check=True)
print('ok', salida)
