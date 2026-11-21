"""Montaje final de la película de producto (tools/peli_cajas.py): imagen 4K + rótulos animados + subtítulos + voz y música.

Uso: python3 peli_montaje.py BASE_4K.mp4 VOZ.wav TIEMPOS.json MUSICA.mp3 SALIDA.mp4 [--hoja] [--anillo PRECINTO.json] [--fotos t1,t2]
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
# 22/11, tras la revisión independiente (realismo, ley y eficacia): todo lo de arriba empieza en y >= 300 (Reels tapa el
# 14 % de arriba y el feed 4:5 recorta hasta y 285); textos sobre fondo oscuro (encima de cajas blancas no se leían);
# cada pastilla es su propia capa (antes, al fundirse, la primera salía doble); letra pequeña >= 30 px y en blanco.
def centro_max(d, y, t, tam, peso=500, col=MARFIL, maximo=950, sombra=True):
    f = arc(tam, peso)
    while ancho(t, f) > maximo * K: tam -= 1; f = arc(tam, peso)
    centro(d, y, t, f, col, sombra)


def r_gancho():
    im = lienzo(); d = ImageDraw.Draw(im); f = unb(70, 700)
    w = max(ancho('¿Su iPhone vino', f), ancho('sin cargador?', f)) + 90 * K
    d.rounded_rectangle(((W - w) / 2, 330 * K, (W + w) / 2, 575 * K), radius=40 * K, fill=(11, 15, 26, 200))
    centro(d, 360, '¿Su iPhone vino', f, BLANCO, False); centro(d, 455, 'sin cargador?', f, BLANCO, False)
    return im


def r_marca():
    im = lienzo(); d = ImageDraw.Draw(im)
    pastilla(d, 320, 'Cargador + cable ORIGINALES de Apple · 18,99 €', arc(38, 700), fondo=(11, 15, 26, 225), alto=84)
    return im


def r_chip(y, t):
    im = lienzo(); d = ImageDraw.Draw(im)
    pastilla(d, y, t, arc(40, 750), fondo=(255, 255, 255, 255), col=NOCHE, check=True)
    return im


def r_precio_apple():
    """Arriba de la tarjeta: lo que cuesta en Apple, con qué se compara y la fecha. Nunca tachado."""
    im = lienzo(); d = ImageDraw.Draw(im); y = 330
    d.rounded_rectangle((90 * K, y * K, W - 90 * K, (y + 236) * K), radius=44 * K, fill=(11, 15, 26, 228))
    centro_max(d, y + 30, 'En Apple (adaptador + cable USB-C)', 34, 600, MARFIL, 840, False)
    centro(d, y + 80, '38,00 €', unb(64, 600), MARFIL, False)
    centro_max(d, y + 172, '(precio del 01/11/2026)', 31, 500, (225, 225, 230), 840, False)
    return im


def r_precio_aqui():
    im = lienzo(); d = ImageDraw.Draw(im); y = 580
    d.rounded_rectangle((90 * K, y * K, W - 90 * K, (y + 214) * K), radius=44 * K, fill=(11, 15, 26, 236))
    centro_max(d, y + 22, 'Aquí, el mismo pack original', 36, 700, ORO, 840, False)
    centro(d, y + 66, '18,99 €', unb(104, 800), ORO, False)
    return im


def r_porque():
    im = lienzo(); d = ImageDraw.Draw(im)
    pastilla(d, 330, '¿Por qué este precio?', arc(44, 800), fondo=(214, 180, 112, 245), col=NOCHE, alto=96)
    return im


def r_compatible():
    im = lienzo(); d = ImageDraw.Draw(im)
    pastilla(d, 1150, 'Para su iPhone: cable USB-C o Lightning, mismo precio', arc(34, 650), fondo=(11, 15, 26, 225), alto=78)
    return im


def r_final():
    im = lienzo(); d = ImageDraw.Draw(im)
    centro_max(d, 300, 'Adaptador 20 W + cable · originales de Apple', 36, 700, BLANCO)
    centro(d, 345, '18,99 €', unb(150, 800), ORO)
    centro_max(d, 545, 'En Apple (adaptador + cable USB-C): 38,00 €', 34, 600, BLANCO)
    centro_max(d, 588, '(precio del 01/11/2026)', 31, 500, BLANCO)
    d.rounded_rectangle((120 * K, 640 * K, W - 120 * K, 780 * K), radius=70 * K, fill=ORO)
    centro(d, 674, 'pillatumovil.com', unb(64, 800), NOCHE, False)
    centro_max(d, 806, '2 packs: 33,99 € · Envío gratis 24-48 h laborables', 33, 600, BLANCO)
    centro_max(d, 849, 'Devolución gratis · Precios con IVA incluido', 33, 600, BLANCO)
    centro_max(d, 892, 'Oferta válida hasta el 30/11/2026 o fin de existencias', 32, 500, BLANCO)
    centro_max(d, 934, 'Pillatumovil es una tienda independiente, no afiliada a Apple Inc.', 31, 500, BLANCO)
    return sombra_suave(im, 10, 170)


def tramo(i): return FR[i][0], FR[i][1]
CORTES = {'gancho': 0, 'precinto': 74 / FPS, 'pack': 135 / FPS, 'cantidad': 233 / FPS, 'producto': 293 / FPS, 'final': 369 / FPS}
LISTA_CORTES = sorted(CORTES.values()) + [TOTAL]
def corte_tras(t): return next(c for c in LISTA_CORTES if c > t + 1e-6)
# (de, a, función, fundido de entrada en s; 0 = ya entero en el primer fotograma)
ROT = [
    (0.0, CORTES['precinto'] - 0.04, r_gancho, 0.0),
    (CORTES['precinto'] + 0.1, CORTES['pack'] - 0.04, r_marca, 0.22),
    (tramo(2)[0] + 0.15, CORTES['pack'] - 0.04, lambda: r_chip(960, 'Original de Apple'), 0.22),
    (tramo(2)[0] + 1.0, CORTES['pack'] - 0.04, lambda: r_chip(1068, 'Caja sin abrir: precinto intacto'), 0.22),
    (tramo(3)[0] - 0.05, CORTES['cantidad'] - 0.04, r_precio_apple, 0.22),
    (tramo(4)[0] + 0.15, CORTES['cantidad'] - 0.04, r_precio_aqui, 0.18),
    (CORTES['cantidad'] + 0.08, CORTES['producto'] - 0.04, r_porque, 0.22),
    (tramo(6)[0], CORTES['final'] - 0.04, lambda: r_chip(330, 'Envío gratis · llega a su casa en 24-48 h'), 0.22),
    (tramo(6)[0] + 1.2, CORTES['final'] - 0.04, lambda: r_chip(438, 'Devolución gratis'), 0.22),
    (tramo(6)[0] + 0.5, CORTES['final'] - 0.04, r_compatible, 0.22),
    (CORTES['final'] + 0.15, TOTAL + 1, r_final, 0.3),
]

# anillo que señala el precinto (la flecha verde) en el plano de la trasera; posiciones medidas en los fotogramas
ANILLO = {}
if '--anillo' in sys.argv:
    ANILLO = {int(k): v for k, v in json.load(open(sys.argv[sys.argv.index('--anillo') + 1])).items()}
ANILLO_DE = tramo(2)[0] + 0.35


def anillo(n, t):
    """Devuelve (parche RGBA float, x0, y0) o None. n: fotograma global; el JSON trae {n: [x, y, r]} en 1080x1920."""
    if n not in ANILLO or t < ANILLO_DE or t >= CORTES['pack'] - 0.04: return None
    o = min(1.0, (t - ANILLO_DE) / 0.25); x, y, r = ANILLO[n]; R = (r + 22) * K; m = int(R + 30 * K)
    im = Image.new('RGBA', (2 * m, 2 * m), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    esc = 0.85 + 0.15 * o                                          # entra creciendo un poco
    d.ellipse((m - R * esc, m - R * esc, m + R * esc, m + R * esc), outline=(255, 255, 255, int(255 * o)), width=int(6 * K))
    im = sombra_suave(im, 8, 150)
    return np.asarray(im).astype(np.float32), int(x * K) - m, int(y * K) - m


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


CON_SUB = {1, 5}           # el resto de frases ya va escrito en un rótulo (gancho, marcas ✓, precio, envío, tarjeta final)


def subtitulo(t):
    for i, (a, b, txt) in enumerate(FR):
        if a - 0.05 <= t < min(b + 0.25, corte_tras(a) - 0.04):         # no pasa al plano siguiente
            if i not in CON_SUB: return None
            pal = txt.split(); ws = [w for w in PAL if a - 0.15 <= w[1] < b + 0.1]
            act = sum(1 for w in ws if w[1] <= t) - 1
            act = max(0, min(len(pal) - 1, round(act * len(pal) / max(1, len(ws)))))
            clave = (i, act)
            if clave not in sub_cache:
                im = lienzo(); d = ImageDraw.Draw(im); f = arc(50, 800)
                while ancho(txt, f) > W - 220 * K: f = arc(f.size / K - 3, 800)
                x = (W - ancho(txt, f)) / 2; esp = ancho(' ', f)
                # pastilla oscura detrás: sobre las cajas blancas el blanco y el oro no se leían
                d.rounded_rectangle((x - 34 * K, (SUB_Y - 16) * K, x + ancho(txt, f) + 34 * K, (SUB_Y + 78) * K),
                                    radius=30 * K, fill=(11, 15, 26, 205))
                for k, p in enumerate(pal):
                    d.text((x, SUB_Y * K), p, font=f, fill=ORO if k == act else BLANCO)
                    x += ancho(p, f) + esp
                sub_cache[clave] = np.asarray(im).astype(np.float32)
            return sub_cache[clave]
    return None


# ---------------------------------------------------------------- composición fotograma a fotograma
capas = {}
def capa(i):
    if i not in capas: capas[i] = np.asarray(ROT[i][2]()).astype(np.float32)
    return capas[i]


def opacidad(t, a, b, entrada=0.22, salida=0.12):
    if t < a or t >= b: return 0.0
    return min(1.0, (t - a) / entrada if entrada > 0 else 1.0, (b - t) / salida if b < TOTAL else 1.0)


if '--fotos' in sys.argv:                                          # revisión rápida: solo unos instantes, sin vídeo ni audio
    for ts in sys.argv[sys.argv.index('--fotos') + 1].split(','):
        t = float(ts)
        b = subprocess.run(['ffmpeg', '-loglevel', 'error', '-ss', str(t), '-i', BASE, '-frames:v', '1', '-f', 'rawvideo',
                            '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
        Fr = np.frombuffer(b, np.uint8).reshape(H, W, 3).astype(np.float32)
        for i, (a_, b_, _, ent) in enumerate(ROT):
            o = opacidad(t, a_, b_, ent)
            if o > 0:
                c = capa(i); al = c[..., 3:] / 255 * o; Fr = Fr * (1 - al) + c[..., :3] * al
        s_ = subtitulo(t)
        if s_ is not None: al = s_[..., 3:] / 255; Fr = Fr * (1 - al) + s_[..., :3] * al
        an = anillo(int(t * FPS), t)
        if an is not None:
            pa, x0, y0 = an; h_, w_ = pa.shape[:2]; zona = Fr[y0:y0 + h_, x0:x0 + w_]
            al = pa[:zona.shape[0], :zona.shape[1], 3:] / 255; zona[:] = zona * (1 - al) + pa[:zona.shape[0], :zona.shape[1], :3] * al
        Image.fromarray(Fr.clip(0, 255).astype(np.uint8)).resize((540, 960)).save(f'{os.path.splitext(SALIDA)[0]}-{t:05.2f}.jpg', quality=90)
    sys.exit(0)

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
    for i, (a_, b_, _, ent) in enumerate(ROT):
        o = opacidad(t, a_, b_, ent)
        if o > 0:
            c = capa(i); dy = int((1 - o) * 18 * K) if t - a_ < 0.5 else 0   # entra subiendo un poco (al salir, quieto)
            al = c[..., 3:] / 255 * o
            if dy: c = np.roll(c, dy, axis=0); al = np.roll(al, dy, axis=0)
            Fr = Fr * (1 - al) + c[..., :3] * al
    s = subtitulo(t)
    if s is not None:
        al = s[..., 3:] / 255; Fr = Fr * (1 - al) + s[..., :3] * al
    an = anillo(n, t)
    if an is not None:
        pa, x0, y0 = an; h_, w_ = pa.shape[:2]; zona = Fr[y0:y0 + h_, x0:x0 + w_]
        al = pa[:zona.shape[0], :zona.shape[1], 3:] / 255; zona[:] = zona * (1 - al) + pa[:zona.shape[0], :zona.shape[1], :3] * al
    Fr = Fr.clip(0, 255).astype(np.uint8); esc.stdin.write(Fr.tobytes())
    if '--hoja' in sys.argv and n % 24 == 12: hoja.append(np.asarray(Image.fromarray(Fr).resize((270, 480))))
esc.stdin.close(); esc.wait()
lee.stdout.close(); lee.kill(); lee.wait()                         # si la base tiene más fotogramas que el audio, el lector se quedaría esperando

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
