"""Hoja de contactos: un fotograma cada 0,5 s con su tiempo y, debajo, todos los fotogramas alrededor de cada corte.
   python3 hoja_v6.py VIDEO SALIDA.jpg"""
import subprocess, sys
from PIL import Image, ImageDraw, ImageFont
V, OUT = sys.argv[1:3]; w, h = 180, 320
F = '/home/user/mi-tienda-shopify/pillatumovil/tools/fuentes/Archivo.ttf'
def fnt(t, wg=600):
    f = ImageFont.truetype(F, t); f.set_variation_by_axes([wg, 100]); return f
N = int(subprocess.run(['ffprobe', '-v', 'error', '-count_packets', '-select_streams', 'v:0', '-show_entries', 'stream=nb_read_packets', '-of', 'csv=p=0', V], capture_output=True, text=True).stdout.strip())
p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', V, '-vf', f'scale={w}:{h}:flags=area:in_color_matrix=bt709,format=rgb24', '-f', 'rawvideo', '-'], stdout=subprocess.PIPE)
frs = []
while (b := p.stdout.read(w * h * 3)) and len(b) == w * h * 3: frs.append(Image.frombytes('RGB', (w, h), b))
cada = [round(k * 12) for k in range(0, 64) if round(k * 12) < len(frs)]
CORTES = [('1 recortado -> 1 abierto', 56), ('1 -> 2a de producto x1,76 (R2)', 117), ('2a -> inserto del adaptador (N3)', 165),
          ('inserto -> las dos cajas x1,41 (giro)', 190), ('barrido del 2b, 197-201 (3.ª revisión)', 199),
          ('2b -> 3 (en «En Apple»)', 298), ('3 -> 4 abierto', 358),
          ('4 abierto -> x1,25 (D40)', 432), ('4: cámara lenta sin voz (D20)', 491), ('-> primer plano x1,095 (Intone n+2, R1)', 504),
          ('sonrisa a media velocidad', 522), ('-> x1,22 en Intone 530 (T2/R7)', 528), ('4 -> 5 de producto, desde su 21 (T1)', 584),
          ('látigo del 5 (giro de la caja)', 609), ('5 -> 6 x1,13', 649), ('fundido al cierre', 681)]
cols = 8; cab = 26; filas1 = (len(cada) + cols - 1) // cols
filas2 = (len(CORTES) + 1) // 2
W = cols * w; H = 60 + filas1 * (h + cab) + 50 + filas2 * (h + cab + 22)
o = Image.new('RGB', (W, H), (16, 18, 24)); d = ImageDraw.Draw(o)
d.text((10, 14), f'Dependienta v6 · {len(frs)} fotogramas a 24 fps · un fotograma cada 0,5 s', font=fnt(26, 700), fill=(244, 241, 234))
y0 = 60
for i, n in enumerate(cada):
    x = (i % cols) * w; y = y0 + (i // cols) * (h + cab)
    d.text((x + 6, y + 4), f'{n / 24:5.2f} s  (f{n})', font=fnt(16), fill=(214, 180, 112)); o.paste(frs[n], (x, y + cab))
y0 += filas1 * (h + cab) + 10
d.text((10, y0 + 8), 'Alrededor de cada corte: los 2 fotogramas de antes y los 2 de después (en rojo el primero del plano nuevo)', font=fnt(22, 700), fill=(244, 241, 234))
y0 += 50
for i, (nom, c) in enumerate(CORTES):
    bx = (i % 2) * 4 * w; by = y0 + (i // 2) * (h + cab + 22)
    d.text((bx + 6, by), f'{nom} · {c / 24:.2f} s', font=fnt(17, 700), fill=(244, 241, 234))
    for k, n in enumerate(range(c - 2, c + 2)):
        if 0 <= n < len(frs):
            x = bx + k * w; y = by + 22
            d.text((x + 6, y + 4), f'f{n}', font=fnt(16), fill=(230, 60, 60) if n == c else (200, 200, 200)); o.paste(frs[n], (x, y + cab))
o.save(OUT, quality=86); print('ok', OUT, o.size)
