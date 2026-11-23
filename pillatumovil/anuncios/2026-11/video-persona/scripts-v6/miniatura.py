"""Miniatura v6 (D44): fotograma 576 del máster limpio (24,0 s, primer plano x1,18, sonrisa a cámara) a 1080x1920,
   con la tarjeta del precio en el estilo de video_persona.py v6 (gancho, 18,99 €, En Apple 38,00 € con su fecha,
   qué lleva el pack y la línea de IA), todo dentro de x 90-990 e y 300-1240.
   python3 miniatura.py MAESTRO_4K FUENTES SALIDA.jpg [fotograma]"""
import subprocess, sys, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
M, FU, OUT = sys.argv[1:4]; N = int(sys.argv[4]) if len(sys.argv) > 4 else 576
K = 2; W, H = 1080 * K, 1920 * K
NOCHE, ORO, MARFIL, BLANCO, GRIS = (11, 15, 26), (214, 180, 112), (244, 241, 234), (255, 255, 255), (226, 226, 232)
p = subprocess.run(['ffmpeg', '-v', 'error', '-i', M, '-vf', f"select=eq(n\\,{N}),scale={W}:{H}:flags=lanczos+accurate_rnd+full_chroma_int:in_color_matrix=bt709:in_range=tv,format=rgb24",
                    '-vframes', '1', '-f', 'rawvideo', '-'], capture_output=True)
fr = Image.frombytes('RGB', (W, H), p.stdout).convert('RGBA')
def unb(t, w=700):
    f = ImageFont.truetype(f'{FU}/Unbounded.ttf', round(t * K)); f.set_variation_by_axes([w]); return f
def arc(t, w=600):
    f = ImageFont.truetype(f'{FU}/Archivo.ttf', round(t * K)); f.set_variation_by_axes([w, 100]); return f
MED = ImageDraw.Draw(Image.new('RGB', (8, 8))); L = lambda t, f: MED.textlength(t, font=f)
X0, X1, Y0, HT = 90, 990, 976, 258; cw = (X1 - X0) * K
capa = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
# sombra suave + panel opaco
sm = Image.new('L', (W, H), 0); ImageDraw.Draw(sm).rounded_rectangle((X0 * K, (Y0 + 4) * K, X1 * K, (Y0 + HT + 4) * K), radius=32 * K, fill=120)
sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sh.putalpha(sm.filter(ImageFilter.GaussianBlur(16 * K)))
fr.alpha_composite(sh)
d.rounded_rectangle((X0 * K, Y0 * K, X1 * K, (Y0 + HT) * K), radius=32 * K, fill=NOCHE + (248,), outline=(255, 255, 255, 30), width=K)
def c(yb, t, f, col): d.text((X0 * K + (cw - L(t, f)) / 2, (Y0 + yb) * K), t, font=f, fill=col, anchor='ls')
c(44, '¿Su iPhone vino sin cargador?', arc(34, 700), MARFIL)
d.line([((X0 + 40) * K, (Y0 + 62) * K), ((X1 - 40) * K, (Y0 + 62) * K)], fill=(255, 255, 255, 34), width=K)
fp = unb(88, 800); pz = '18,99 €'; fa, fb, fq = arc(26, 600), unb(40, 700), arc(24, 500)
wd = max(L('En Apple', fa), L('38,00 €', fb), L('(precio del 01/11/2026)', fq)); gap = 60 * K
x = X0 * K + (cw - (L(pz, fp) + gap + wd)) / 2
d.text((x, (Y0 + 166) * K), pz, font=fp, fill=ORO, anchor='ls'); xr = x + L(pz, fp) + gap
d.line([(xr - gap / 2, (Y0 + 88) * K), (xr - gap / 2, (Y0 + 170) * K)], fill=(255, 255, 255, 46), width=3)
d.text((xr, (Y0 + 106) * K), 'En Apple', font=fa, fill=GRIS, anchor='ls')
d.text((xr, (Y0 + 148) * K), '38,00 €', font=fb, fill=BLANCO, anchor='ls')
d.text((xr, (Y0 + 176) * K), '(precio del 01/11/2026)', font=fq, fill=GRIS, anchor='ls')
d.line([((X0 + 40) * K, (Y0 + 192) * K), ((X1 - 40) * K, (Y0 + 192) * K)], fill=(255, 255, 255, 34), width=K)
c(222, '1 adaptador 20 W + 1 cable (USB-C o Lightning)', arc(27, 600), MARFIL)
c(246, 'Tienda online · escena recreada con IA', arc(19, 500), GRIS)
fr.alpha_composite(capa)
fr.convert('RGB').resize((1080, 1920), Image.LANCZOS).save(OUT, quality=93, subsampling=0)
print('ok', OUT)
