"""Montaje final de la película de producto (tools/peli_cajas.py): imagen 4K + rótulos animados + subtítulos + voz y música.

Uso: python3 peli_montaje.py BASE_4K.mp4 VOZ.wav TIEMPOS.json MUSICA.mp3 SALIDA.mp4 [--hoja]
  BASE_4K.mp4: los planos ya unidos y subidos a 2160x3840 (24 fps, sin audio).
  TIEMPOS.json: {'frases': [[ini, fin, texto], ...], 'total': s} (lo saca el montaje de la voz).
Los rótulos están pensados para Reels: todo entre el 13 % y el 66 % de la altura (fuera de los botones de Instagram)
y dentro del 4:5 del feed. Reglas: «En Apple, 38,00 € (precio del 01/11/2026)» nunca tachado; sin prisas ni escasez;
la fecha del 30/11 solo como condición de la oferta.
"""
import json, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE, VOZ, TIEMPOS, MUSICA, SALIDA = sys.argv[1:6]
AQUI = os.path.dirname(os.path.abspath(__file__)); F = os.path.join(AQUI, 'fuentes')
K = 2; W, H, FPS = 2160, 3840, 24
NOCHE = (11, 15, 26); ORO = (214, 180, 112); MARFIL = (244, 241, 234); VERDE = (52, 199, 89); BLANCO = (255, 255, 255)
T = json.load(open(TIEMPOS)); FR = T['frases']; TOTAL = T['total']


def unb(t, w=700): f = ImageFont.truetype(f'{F}/Unbounded.ttf', int(t * K)); f.set_variation_by_axes([w]); return f
def arc(t, w=600): f = ImageFont.truetype(f'{F}/Archivo.ttf', int(t * K)); f.set_variation_by_axes([w, 100]); return f
MED = ImageDraw.Draw(Image.new('RGB', (8, 8)))
def ancho(t, f): return MED.textlength(t, font=f)


def lienzo(): return Image.new('RGBA', (W, H), (0, 0, 0, 0))


def centro(d, y, t, f, col, sombra=True):
    x = (W - ancho(t, f)) / 2
    if sombra: d.text((x, y * K + 3 * K), t, font=f, fill=(0, 0, 0, 120))
    d.text((x, y * K), t, font=f, fill=col)


def sombra_suave(im, radio=18, fuerza=150):
    """Sombra difusa bajo los rótulos: se leen sobre cualquier fondo sin cajas pesadas."""
    a = im.split()[3].filter(ImageFilter.GaussianBlur(radio * K / 2))
    s = Image.new('RGBA', im.size, (0, 0, 0, 0)); s.putalpha(a.point(lambda v: min(255, int(v * fuerza / 255))))
    s.alpha_composite(im); return s


def pastilla(d, y, t, f, fondo=(11, 15, 26, 215), col=MARFIL, alto=86, check=False):
    tw = ancho(t, f) + (70 * K if check else 0); x0 = (W - tw) / 2 - 38 * K
    d.rounded_rectangle((x0, y * K, x0 + tw + 76 * K, (y + alto) * K), radius=alto * K / 2, fill=fondo)
    tx = x0 + 38 * K
    if check:
        cy = (y + alto / 2) * K; r = 26 * K
        d.ellipse((tx, cy - r, tx + 2 * r, cy + r), fill=VERDE)
        d.line([(tx + 14 * K, cy + 1 * K), (tx + 23 * K, cy + 10 * K), (tx + 39 * K, cy - 10 * K)], fill=BLANCO, width=7 * K, joint='curve')
        tx += 70 * K
    d.text((tx, (y + alto / 2) * K), t, font=f, fill=col, anchor='lm')


# ---------------------------------------------------------------- rótulos (de, a, función que pinta)
def r_marca():
    im = lienzo(); d = ImageDraw.Draw(im)
    pastilla(d, 250, 'Cargador + cable · ORIGINALES de Apple', arc(34, 700), fondo=(11, 15, 26, 190), alto=74)
    return im


def r_gancho():
    im = lienzo(); d = ImageDraw.Draw(im)
    centro(d, 360, '¿Su iPhone vino', unb(70, 700), BLANCO); centro(d, 455, 'sin cargador?', unb(70, 700), BLANCO)
    return sombra_suave(im)


def r_checks(n):
    im = lienzo(); d = ImageDraw.Draw(im)
    items = ['Original de Apple', 'Caja sin abrir: precinto intacto']
    for i, t in enumerate(items[:n]): pastilla(d, 1080 + i * 108, t, arc(40, 750), fondo=(255, 255, 255, 238), col=NOCHE, check=True)
    return im


def r_precio(fase):
    """Fase 1: «En Apple, 38,00 €». Fase 2: entra «Aquí 18,99 €» grande en oro. Nunca tachado."""
    im = lienzo(); d = ImageDraw.Draw(im); y = 270
    d.rounded_rectangle((90 * K, y * K, W - 90 * K, (y + 400) * K), radius=48 * K, fill=(11, 15, 26, 222))
    centro(d, y + 40, 'En Apple', arc(36, 500), MARFIL, False)
    centro(d, y + 88, '38,00 €', unb(64, 600), MARFIL, False)
    centro(d, y + 172, '(precio del 01/11/2026)', arc(26, 500), (190, 190, 196), False)
    if fase >= 2:
        d.line([(170 * K, (y + 222) * K), (W - 170 * K, (y + 222) * K)], fill=(255, 255, 255, 50), width=2 * K)
        centro(d, y + 236, 'Aquí', arc(36, 700), ORO, False)
        centro(d, y + 272, '18,99 €', unb(104, 800), ORO, False)
    return im


def r_porque():
    im = lienzo(); d = ImageDraw.Draw(im)
    pastilla(d, 270, '¿Por qué este precio?', arc(44, 800), fondo=(214, 180, 112, 240), col=NOCHE, alto=96)
    return im


def r_envio(n):
    im = lienzo(); d = ImageDraw.Draw(im)
    items = ['Envío gratis · llega a su casa en 24-48 h', 'Devolución gratis']
    for i, t in enumerate(items[:n]): pastilla(d, 270 + i * 108, t, arc(38, 750), fondo=(255, 255, 255, 238), col=NOCHE, check=True)
    centro(d, 520, 'Adaptador 20 W + cable USB-C (o Lightning)', arc(30, 600), MARFIL)
    return im


def r_final():
    im = lienzo(); d = ImageDraw.Draw(im)
    centro(d, 250, 'Pack ORIGINAL de Apple · adaptador 20 W + cable', arc(32, 700), MARFIL)
    centro(d, 300, '18,99 €', unb(150, 800), ORO)
    centro(d, 500, 'En Apple, 38,00 € (precio del 01/11/2026)', arc(30, 500), MARFIL)
    centro(d, 548, '2 packs: 33,99 € · Envío gratis 24-48 h · Devolución gratis', arc(28, 600), MARFIL)
    d.rounded_rectangle((120 * K, 620 * K, W - 120 * K, 770 * K), radius=75 * K, fill=ORO)
    centro(d, 657, 'pillatumovil.com', unb(66, 800), NOCHE, False)
    centro(d, 800, 'Precio de lanzamiento hasta el 30/11/2026 o fin de existencias', arc(24, 500), (200, 200, 206))
    return im


def tramo(i): return FR[i][0], FR[i][1]
CORTES = {'gancho': 0, 'precinto': 74 / FPS, 'pack': 135 / FPS, 'cantidad': 233 / FPS, 'producto': 293 / FPS, 'final': 369 / FPS}
ROT = [
    (0.0, tramo(1)[1] + 0.1, r_gancho, 0.0),
    (tramo(0)[1] - 0.2, CORTES['cantidad'], r_marca, 0.0),
    (tramo(2)[0] + 0.1, CORTES['pack'], lambda: r_checks(1), 0.0),
    (tramo(2)[0] + 1.0, CORTES['pack'], lambda: r_checks(2), 0.0),
    (tramo(3)[0] - 0.05, tramo(4)[0] + 0.15, lambda: r_precio(1), 0.0),
    (tramo(4)[0] + 0.15, CORTES['cantidad'], lambda: r_precio(2), 0.0),
    (CORTES['cantidad'], CORTES['producto'], r_porque, 0.0),
    (tramo(6)[0], tramo(6)[0] + 1.2, lambda: r_envio(1), 0.0),
    (tramo(6)[0] + 1.2, CORTES['final'], lambda: r_envio(2), 0.0),
    (CORTES['final'] + 0.15, TOTAL + 1, r_final, 0.0),
]


# ---------------------------------------------------------------- subtítulos (frase entera, palabra activa en oro)
def palabras():
    from faster_whisper import WhisperModel
    a = np.frombuffer(subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', VOZ, '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'],
                                     capture_output=True).stdout, np.float32)
    segs, _ = WhisperModel('small', device='cpu', compute_type='int8').transcribe(
        a, language='es', word_timestamps=True, initial_prompt=' '.join(f[2] for f in FR))
    return [(w.word.strip(), w.start, w.end) for s in segs for w in s.words if w.word.strip()]


PAL = palabras()
SUB_Y = 1130                                                       # 59 % de la altura
sub_cache = {}


def subtitulo(t):
    for i, (a, b, txt) in enumerate(FR):
        if a - 0.05 <= t < b + 0.25:
            if i in (0, 1) and t < tramo(1)[1] + 0.1: return None        # el gancho ya va en grande arriba
            pal = txt.split(); ws = [w for w in PAL if a - 0.15 <= w[1] < b + 0.1]
            act = sum(1 for w in ws if w[1] <= t) - 1
            act = max(0, min(len(pal) - 1, round(act * len(pal) / max(1, len(ws)))))
            clave = (i, act)
            if clave not in sub_cache:
                im = lienzo(); d = ImageDraw.Draw(im); f = arc(52, 800)
                while ancho(txt, f) > W - 160 * K: f = arc(f.size / K - 3, 800)
                x = (W - ancho(txt, f)) / 2; esp = ancho(' ', f)
                for k, p in enumerate(pal):
                    d.text((x, SUB_Y * K), p, font=f, fill=ORO if k == act else BLANCO)
                    x += ancho(p, f) + esp
                sub_cache[clave] = np.asarray(sombra_suave(im, 14, 200)).astype(np.float32)
            return sub_cache[clave]
    return None


# ---------------------------------------------------------------- composición fotograma a fotograma
capas = {}
def capa(i):
    if i not in capas: capas[i] = np.asarray(ROT[i][2]()).astype(np.float32)
    return capas[i]


def opacidad(t, a, b, fundido=0.22):
    if t < a or t >= b: return 0.0
    return min(1.0, (t - a) / fundido, (b - t) / fundido if b < TOTAL else 1.0)


NT = int(round(TOTAL * FPS)); tmp = SALIDA + '.mudo.mp4'
lee = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-i', BASE, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
esc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                        '-c:v', 'libx264', '-crf', '16', '-preset', 'medium', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
hoja = []; ultimo = None
for n in range(NT):
    b = lee.stdout.read(W * H * 3)
    if len(b) < W * H * 3: b = ultimo                               # si la base es más corta, se congela el último
    ultimo = b; t = (n + 0.5) / FPS
    Fr = np.frombuffer(b, np.uint8).reshape(H, W, 3).astype(np.float32)
    for i, (a_, b_, _, _) in enumerate(ROT):
        o = opacidad(t, a_, b_)
        if o > 0:
            c = capa(i); dy = int((1 - o) * 18 * K)                  # entra subiendo un poco
            al = c[..., 3:] / 255 * o
            if dy: c = np.roll(c, dy, axis=0); al = np.roll(al, dy, axis=0)
            Fr = Fr * (1 - al) + c[..., :3] * al
    s = subtitulo(t)
    if s is not None:
        al = s[..., 3:] / 255; Fr = Fr * (1 - al) + s[..., :3] * al
    Fr = Fr.clip(0, 255).astype(np.uint8); esc.stdin.write(Fr.tobytes())
    if '--hoja' in sys.argv and n % 24 == 12: hoja.append(np.asarray(Image.fromarray(Fr).resize((270, 480))))
esc.stdin.close(); esc.wait(); lee.wait()

# ---------------------------------------------------------------- audio: voz delante, música debajo (se aparta cuando habla)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', tmp, '-i', VOZ, '-i', MUSICA, '-filter_complex',
                f'[1:a]aresample=48000,aformat=channel_layouts=stereo,apad=whole_dur={TOTAL}[v];'
                f'[2:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{TOTAL},volume=0.42,'
                f'afade=t=in:d=0.4,afade=t=out:st={TOTAL - 1.0}:d=1.0[m];'
                f'[v]asplit=2[v1][v2];[m][v1]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350[md];'
                f'[v2][md]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]',
                '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-t', str(TOTAL),
                '-movflags', '+faststart', SALIDA], check=True)
os.remove(tmp)
if hoja:
    filas = [np.hstack(hoja[i:i + 10] + [np.zeros_like(hoja[0])] * (10 - len(hoja[i:i + 10]))) for i in range(0, len(hoja), 10)]
    Image.fromarray(np.vstack(filas)).save(os.path.splitext(SALIDA)[0] + '-hoja.jpg', quality=88)
print('ok', SALIDA, TOTAL)
