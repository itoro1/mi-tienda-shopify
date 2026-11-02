"""Vídeo anuncio de Pillatumovil (problema → solución), 02/11/2026.
Uso: python3 video_anuncio.py CARPETA_MEDIOS FUENTES SALIDA.mp4 [W H]
CARPETA_MEDIOS: ps-mesilla-v2.jpg, ps-estudio-portada.mp4, ps-unboxing-v2.mp4 (de la tienda).
Sin música (Meta reproduce sin sonido; se puede añadir música libre desde la app)."""
import sys, os, subprocess
from PIL import Image, ImageDraw, ImageFont

med, fdir, salida = sys.argv[1:4]
W, H = (int(sys.argv[4]), int(sys.argv[5])) if len(sys.argv) > 5 else (1080, 1920)
tmp = os.path.join(os.path.dirname(os.path.abspath(salida)), 'tmp_video'); os.makedirs(tmp, exist_ok=True)
NOCHE=(11,15,26); ORO=(201,168,106); ORO_T=(217,187,124); MARFIL=(244,241,234); MARFIL2=(185,188,198)
def F(n, t, p):
    f = ImageFont.truetype(os.path.join(fdir, n), t)
    f.set_variation_by_axes([p] if n.startswith('Unb') else [p, 100]); return f
U = lambda t: F('Unbounded.ttf', t, 600); A = lambda t, p=500: F('Archivo.ttf', t, p)
M = 72; vertical = H > W * 1.5
TOP = 260 if vertical else 90  # zona segura de Reels arriba

def capa(nombre, dibujar, degradado=('arriba', 0.55)):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    lado, frac = degradado
    if lado:
        g = Image.new('L', (1, H))
        for y in range(H):
            t = y / H if lado == 'abajo' else 1 - y / H
            a = max(0, (t - (1 - frac)) / frac)
            g.putpixel((0, y), int(225 * a ** 1.3))
        sombra = Image.new('RGBA', (W, H), NOCHE + (0,)); sombra.putalpha(g.resize((W, H)))
        im = Image.alpha_composite(sombra, im); d = ImageDraw.Draw(im)
    dibujar(d)
    p = os.path.join(tmp, nombre + '.png'); im.save(p); return p

def lineas(d, x, y, ls, f, c, k=1.1):
    for l in ls: d.text((x, y), l, font=f, fill=c); y += int(f.size * k)
    return y

def pill(d, x, y, t, f):
    w = d.textlength(t, font=f)
    d.rounded_rectangle([x, y, x + w + 48, y + f.size + 30], radius=(f.size + 30) // 2, outline=ORO, width=3)
    d.text((x + 24, y + 13), t, font=f, fill=ORO_T); return y + f.size + 30

def barra(d, y, h=130):
    d.rectangle([0, y, W, y + h], fill=ORO); f = U(56); t = 'pillatumovil.com'
    d.text(((W - d.textlength(t, font=f)) / 2, y + (h - 56) / 2 - 8), t, font=f, fill=NOCHE)

ts = 96 if vertical else 80
c1 = capa('c1', lambda d: lineas(d, M, TOP, ['Su iPhone', 'ya no trae', 'cargador.'], U(ts), MARFIL))
def _c2(d):
    y = lineas(d, M, TOP, ['En Apple:'], U(ts - 10), MARFIL)
    y = lineas(d, M, y, ['38,00 €'], U(ts + 40), MARFIL)
    lineas(d, M, y + 10, ['Adaptador 20 W + cable USB‑C,', 'precio de apple.com/es del 01/11/2026'], A(34), MARFIL2, 1.35)
c2 = capa('c2', _c2, (None, 0))
c3 = capa('c3', lambda d: lineas(d, M, TOP, ['El mismo.', 'Original y', 'precintado.'], U(ts), MARFIL), (None, 0))
def _c4(d):
    y = lineas(d, M, TOP, ['Aquí, el pack:'], U(ts - 30), MARFIL)
    y = lineas(d, M, y + 4, ['18,99 €'], U(ts + 70), ORO_T)
    y = pill(d, M, y + 20, 'Precio de lanzamiento · hasta fin de existencias', A(32, 600))
    lineas(d, M, y + 28, ['¿Por qué tan barato? Compramos por', 'cantidad y ganamos menos en cada pack.'], A(36), MARFIL, 1.35)
c4 = capa('c4', _c4, (None, 0))
def _c5(d):
    d.rectangle([0, 0, W, H], fill=NOCHE + (255,))
    y = H * (0.22 if vertical else 0.12)
    y = lineas(d, M, y, ['Cargador 20 W', '+ cable, de Apple.'], U(ts - 20), MARFIL)
    y = lineas(d, M, y + 20, ['18,99 €'], U(ts + 70), ORO_T)
    y = pill(d, M, y + 20, 'Precio de lanzamiento · hasta fin de existencias', A(32, 600))
    lineas(d, M, y + 30, ['Para cualquier iPhone, del 8 al 18.', 'Envío gratis en 24-48 h.', '14 días para devolverlo.'], A(40), MARFIL, 1.4)
    barra(d, int(H * (0.70 if vertical else 0.80)))
c5 = capa('c5', _c5, (None, 0))

V = lambda n: os.path.join(med, n)
BAND_Y, BAND_H = (860, 860) if vertical else (int(H*0.50), int(H*0.50))
def vid_band(cx):  # vídeo en una franja bajo el texto, sobre fondo noche
    return (f"scale=-2:{BAND_H},crop={W}:{BAND_H}:'min(max(0,iw*{cx}-{W}/2),iw-{W})':0,"
            f"pad={W}:{H}:0:{BAND_Y}:color=0x0B0F1A")
def vid_crop(cx):  # centro horizontal relativo
    return (f"scale=-2:{H},crop={W}:{H}:'min(max(0,iw*{cx}-{W}/2),iw-{W})':0" if vertical
            else f"scale={W}:-2,crop={W}:{H}:0:'(ih-{H})/2'" if False else
            f"scale=-2:{H},crop={W}:{H}:'min(max(0,iw*{cx}-{W}/2),iw-{W})':0")
seg = [
    ('s1', ['-loop', '1', '-i', V('ps-mesilla-v2.jpg')], f"scale={int(W*1.25)}:-2,zoompan=z='1+0.0009*on':x='iw/2-iw/zoom/2':y='ih*0.45-ih/zoom/2':d=1:s={W}x{H}:fps=30", c1, 3.5),
    ('s2', ['-ss', '0', '-i', V('ps-estudio-portada.mp4')], vid_band(0.62) + ",fps=30", c2, 3.0),
    ('s3', ['-ss', '0.3', '-i', V('ps-unboxing-v2.mp4')], vid_band(0.55) + ",fps=30", c3, 4.0),
    ('s4', ['-ss', '5', '-i', V('ps-estudio-portada.mp4')], vid_band(0.64) + ",fps=30", c4, 3.5),
    ('s5', ['-f', 'lavfi', '-i', f'color=c=0x0B0F1A:s={W}x{H}:r=30'], 'null', c5, 3.2),
]
partes = []
for n, entrada, filtro, ov, dur in seg:
    p = os.path.join(tmp, n + '.mp4')
    fc = f"[0:v]{filtro},setsar=1,format=yuv420p[b];[1:v]format=rgba,fade=t=in:st=0.15:d=0.45:alpha=1[o];[b][o]overlay=0:0,format=yuv420p[v]"
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *entrada, '-loop', '1', '-i', ov, '-filter_complex', fc,
                    '-map', '[v]', '-t', str(dur), '-r', '30', '-c:v', 'libx264', '-crf', '19', '-preset', 'medium', '-an', p], check=True)
    partes.append((p, dur))
# unir con fundidos cortos
args = []; [args.extend(['-i', p]) for p, _ in partes]
fc = ''; prev = '0:v'; off = 0; X = 0.35
for i in range(1, len(partes)):
    off += partes[i - 1][1] - X
    out = f'x{i}'
    fc += f"[{prev}][{i}:v]xfade=transition=fade:duration={X}:offset={off:.2f}[{out}];"; prev = out
subprocess.run(['ffmpeg', '-v', 'error', '-y', *args, '-filter_complex', fc.rstrip(';'), '-map', f'[{prev}]',
                '-c:v', 'libx264', '-crf', '20', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', salida], check=True)
print('hecho', salida)
