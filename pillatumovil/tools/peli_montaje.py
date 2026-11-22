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
    im = lienzo(); d = ImageDraw.Draw(im); f = unb(64, 700)
    w = max(ancho('¿Su iPhone vino', f), ancho('sin cargador?', f)) + 90 * K
    # 22/11 (2.ª revisión): fondo casi opaco (se veía la pestaña detrás). 3.ª revisión: aún tapaba la hoja del logo
    # en el primer fotograma (la miniatura): letra 64 y pastilla 300-492 (la hoja empieza en y 520)
    # 22/11 (5.ª revisión): en los primeros fotogramas el hueco negro de la pestaña asomaba por el lado y por debajo y se
    # fundía con la pastilla (una mancha negra con «cola»). Igual que r_marca: casi opaca y con un canto claro de 2 px.
    d.rounded_rectangle(((W - w) / 2, 300 * K, (W + w) / 2, 492 * K), radius=40 * K, fill=(11, 15, 26, 250),
                        outline=(255, 255, 255, 70), width=2 * K)
    centro(d, 312, '¿Su iPhone vino', f, BLANCO, False); centro(d, 396, 'sin cargador?', f, BLANCO, False)
    return im


def r_marca():
    # 3.ª revisión: la tienda no salía hasta el segundo 7,7: ahora va desde el 3,2, en una segunda línea
    im = lienzo(); d = ImageDraw.Draw(im); f = arc(38, 700)
    l1, l2 = 'Cargador + cable ORIGINALES de Apple', '18,99 € en pillatumovil.com'
    w = max(ancho(l1, f), ancho(l2, f)) + 76 * K
    # 4.ª revisión: al subir la cámara, la ranura negra de la pestaña se fundía con la esquina de la pastilla: casi opaca
    # y con un filo claro, para que conserve su borde sobre el negro
    d.rounded_rectangle(((W - w) / 2, 310 * K, (W + w) / 2, 440 * K), radius=36 * K, fill=(11, 15, 26, 250),
                        outline=(255, 255, 255, 70), width=2 * K)
    centro(d, 326, l1, f, MARFIL, False); centro(d, 378, l2, f, ORO, False)
    return im


def r_chip(y, t):
    im = lienzo(); d = ImageDraw.Draw(im)
    pastilla(d, y, t, arc(40, 750), fondo=(255, 255, 255, 255), col=NOCHE, check=True)
    return im


def chip_precinto():
    """«Caja sin abrir: precinto intacto» pegado al anillo de la flecha verde (22/11, 2.ª revisión: los dos chips blancos
    tapaban los textos impresos de la trasera y nada decía qué señalaba el anillo). Pastilla oscura, sin transparencia."""
    t = 'Caja sin abrir: precinto intacto'; f = arc(38, 750); alto = 84
    tw = ancho(t, f) + 70 * K + 76 * K; im = Image.new('RGBA', (int(tw) + 4, alto * K + 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, tw, alto * K), radius=alto * K / 2, fill=(11, 15, 26, 235))
    cy = alto / 2 * K; r = 24 * K; tx = 34 * K
    d.ellipse((tx, cy - r, tx + 2 * r, cy + r), fill=VERDE)
    d.line([(tx + 13 * K, cy + 1 * K), (tx + 21 * K, cy + 9 * K), (tx + 36 * K, cy - 9 * K)], fill=BLANCO, width=7 * K, joint='curve')
    d.text((tx + 66 * K, cy), t, font=f, fill=MARFIL, anchor='lm')
    return np.asarray(sombra_suave(im, 8, 140)).astype(np.float32)


def r_precio_apple():
    """Arriba de la tarjeta: lo que cuesta en Apple, con qué se compara y la fecha. Nunca tachado."""
    im = lienzo(); d = ImageDraw.Draw(im); y = 310
    # 22/11 (2.ª revisión): la aclaración «no afiliada a Apple» solo salía 3,7 s al final; ahora también aquí
    d.rounded_rectangle((90 * K, y * K, W - 90 * K, (y + 250) * K), radius=44 * K, fill=(11, 15, 26, 228))
    centro_max(d, y + 24, 'En Apple (adaptador + cable USB-C)', 34, 600, MARFIL, 840, False)
    centro(d, y + 70, '38,00 €', unb(64, 600), MARFIL, False)
    # 3.ª revisión: la fecha y la aclaración, a 34 px como el resto de la letra pequeña (antes 31 y 30)
    centro_max(d, y + 156, '(precio del 01/11/2026)', 34, 500, (225, 225, 230), 840, False)
    centro_max(d, y + 198, 'Tienda independiente, no afiliada a Apple Inc.', 34, 500, (225, 225, 230), 840, False)
    return im


def r_precio_aqui():
    im = lienzo(); d = ImageDraw.Draw(im); y = 572
    d.rounded_rectangle((90 * K, y * K, W - 90 * K, (y + 214) * K), radius=44 * K, fill=(11, 15, 26, 236))
    # 22/11 (2.ª revisión): «el mismo pack original» sonaba a pack de Apple, y sin sonido «Aquí» no decía dónde
    centro_max(d, y + 22, 'En pillatumovil.com (adaptador + cable)', 36, 700, ORO, 840, False)
    centro(d, y + 66, '18,99 €', unb(104, 800), ORO, False)
    return im


def r_porque():
    im = lienzo(); d = ImageDraw.Draw(im)
    pastilla(d, 330, '¿Por qué este precio?', arc(44, 800), fondo=(214, 180, 112, 245), col=NOCHE, alto=96)
    return im


def r_razon():
    """3.ª revisión: la respuesta al «¿Por qué este precio?» iba de subtítulo abajo, a 38 px y cruzando las letras de
    las cajas de delante. Ahora, en grande y justo debajo de la pregunta, sobre las filas desenfocadas."""
    im = lienzo(); d = ImageDraw.Draw(im); f = arc(54, 800)
    lineas = [[('Compramos', BLANCO), ('por', BLANCO), ('cantidad', ORO)], [('y', BLANCO), ('ganamos', BLANCO), ('menos.', ORO)]]
    esp = ancho(' ', f); anchos = [sum(ancho(p, f) for p, _ in l) + esp * (len(l) - 1) for l in lineas]
    w = max(anchos) + 90 * K
    d.rounded_rectangle(((W - w) / 2, 446 * K, (W + w) / 2, 606 * K), radius=40 * K, fill=(11, 15, 26, 230))
    for (l, a), y in zip(zip(lineas, anchos), (458, 528)):
        x = (W - a) / 2
        for p, c in l:
            d.text((x, y * K), p, font=f, fill=c); x += ancho(p, f) + esp
    return im


def r_final():
    im = lienzo(); d = ImageDraw.Draw(im)
    centro_max(d, 300, 'Adaptador 20 W + cable · originales de Apple', 36, 700, BLANCO)
    centro(d, 345, '18,99 €', unb(150, 800), ORO)
    centro_max(d, 540, 'En Apple (adaptador + cable USB-C): 38,00 €', 34, 600, BLANCO)
    centro_max(d, 581, '(precio del 01/11/2026)', 34, 500, BLANCO)
    # 22/11 (2.ª revisión): sin sonido faltaba el verbo; el «2 packs: 33,99 €» competía con el 18,99 € y no daba
    # tiempo a leerlo (se queda en la web); la letra pequeña, a 34 px (antes 31-33).
    centro_max(d, 624, 'Compre en', 34, 700, MARFIL)
    d.rounded_rectangle((120 * K, 668 * K, W - 120 * K, 798 * K), radius=65 * K, fill=ORO)
    centro(d, 697, 'pillatumovil.com', unb(62, 800), NOCHE, False)
    centro_max(d, 820, 'Envío gratis 24-48 h laborables · Devolución gratis', 34, 600, BLANCO)
    centro_max(d, 861, 'Precios con IVA incluido', 34, 600, BLANCO)
    centro_max(d, 902, 'Oferta válida hasta el 30/11/2026 o fin de existencias', 34, 500, BLANCO)
    centro_max(d, 943, 'Tienda independiente, no afiliada a Apple Inc.', 34, 500, BLANCO)
    return sombra_suave(im, 10, 170)


def tramo(i): return FR[i][0], FR[i][1]
CORTES = {'gancho': 0, 'precinto': 74 / FPS, 'pack': 135 / FPS, 'cantidad': 233 / FPS, 'producto': 293 / FPS, 'final': 369 / FPS}
LISTA_CORTES = sorted(CORTES.values()) + [TOTAL]
def corte_tras(t): return next(c for c in LISTA_CORTES if c > t + 1e-6)
# (de, a, función, fundido de entrada en s; 0 = ya entero en el primer fotograma)
ROT = [
    (0.0, CORTES['precinto'] - 0.04, r_gancho, 0.0),
    (CORTES['precinto'] + 0.1, CORTES['pack'] - 0.04, r_marca, 0.22),        # el chip del precinto va con el anillo
    (tramo(3)[0] - 0.05, CORTES['cantidad'] - 0.04, r_precio_apple, 0.22),
    (tramo(4)[0] + 0.15, CORTES['cantidad'] - 0.04, r_precio_aqui, 0.18),
    (CORTES['cantidad'] + 0.08, CORTES['producto'] - 0.04, r_porque, 0.22),
    (tramo(5)[0] - 0.05, CORTES['producto'] - 0.04, r_razon, 0.22),
    # 22/11 (2.ª revisión): «laborables» en el mismo rótulo (era una promesa sin condición); fuera «Devolución gratis»
    # (ya en la tarjeta final) y la compatibilidad pasa arriba: la franja de abajo cortaba el adaptador.
    (tramo(6)[0], CORTES['final'] - 0.04, lambda: r_chip(330, 'Envío gratis · 24-48 h laborables'), 0.22),
    (tramo(6)[0] + 0.9, CORTES['final'] - 0.04, lambda: r_chip(438, 'Cable USB-C o Lightning · mismo precio'), 0.22),
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


CHIP = None
def chip_anillo(n, t):
    """El chip «Caja sin abrir: precinto intacto» a la derecha del anillo, siguiéndolo. Entra entero (sin fundido que
    lo mezcle con los textos impresos): solo se desliza 18 px y aparece en 2 fotogramas."""
    global CHIP
    de = ANILLO_DE + 0.15
    if not ANILLO or t < de or t >= CORTES['pack'] - 0.04: return None
    if CHIP is None: CHIP = chip_precinto()
    k = n if n in ANILLO else min(ANILLO, key=lambda j: abs(j - n)); x, y, r = ANILLO[k]
    o = min(1.0, (t - de) / 0.08); dx = int((1 - min(1.0, (t - de) / 0.2)) * -18 * K)
    x0 = int((x + r + 22 + 26) * K) + dx; y0 = int(y * K - CHIP.shape[0] / 2)
    x0 = min(x0, W - 65 * K - CHIP.shape[1])                       # dentro del margen de Meta
    pa = CHIP.copy(); pa[..., 3] *= o
    return pa, x0, y0


def pega(Fr, an):
    if an is None: return
    pa, x0, y0 = an; h_, w_ = pa.shape[:2]; zona = Fr[y0:y0 + h_, x0:x0 + w_]
    al = pa[:zona.shape[0], :zona.shape[1], 3:] / 255; zona[:] = zona * (1 - al) + pa[:zona.shape[0], :zona.shape[1], :3] * al


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


CON_SUB = {1}              # el resto de frases ya va escrito en un rótulo (gancho, marcas ✓, precio, razón, envío, final)


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
        pega(Fr, anillo(int(t * FPS), t)); pega(Fr, chip_anillo(int(t * FPS), t))
        Image.fromarray(Fr.clip(0, 255).astype(np.uint8)).resize((540, 960)).save(f'{os.path.splitext(SALIDA)[0]}-{t:05.2f}.jpg', quality=90)
    sys.exit(0)

NT = int(round(TOTAL * FPS)); tmp = SALIDA + '.mudo.mp4'
lee = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-i', BASE, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
esc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                        '-vf', 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p', '-colorspace', 'bt709',
                        '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv',     # 22/11: BT.709 etiquetado
                        '-c:v', 'libx264', '-crf', '16', '-preset', 'medium', tmp], stdin=subprocess.PIPE)
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
    pega(Fr, anillo(n, t)); pega(Fr, chip_anillo(n, t))
    Fr = Fr.clip(0, 255).astype(np.uint8); esc.stdin.write(Fr.tobytes())
    if '--hoja' in sys.argv and n % 24 == 12: hoja.append(np.asarray(Image.fromarray(Fr).resize((270, 480))))
esc.stdin.close(); esc.wait()
lee.stdout.close(); lee.kill(); lee.wait()                         # si la base tiene más fotogramas que el audio, el lector se quedaría esperando

# ---------------------------------------------------------------- audio: voz delante, música debajo (se aparta cuando habla)
# 22/11 (2.ª revisión): la música (0,42) subía hasta el nivel de la voz en cada pausa (release 350 ms): «bombeo».
# Ahora va más baja, vuelve despacio y el volumen final se ajusta en dos pasadas (loudnorm lineal, sin compresión).
mezcla = SALIDA + '.mezcla.wav'
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', VOZ, '-i', MUSICA, '-filter_complex',
                f'[0:a]aresample=48000,aformat=channel_layouts=stereo,apad=whole_dur={TOTAL}[v];'
                f'[1:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{TOTAL},volume=0.28,'
                f'afade=t=in:d=0.4,afade=t=out:st={TOTAL - 1.0}:d=1.0[m];'
                f'[v]asplit=2[v1][v2];[m][v1]sidechaincompress=threshold=0.03:ratio=4:attack=20:release=900[md];'
                f'[v2][md]amix=inputs=2:duration=first:normalize=0[a]', '-map', '[a]', '-t', str(TOTAL), mezcla], check=True)
med = subprocess.run(['ffmpeg', '-hide_banner', '-i', mezcla, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json',
                      '-f', 'null', '-'], capture_output=True, text=True).stderr
med = json.loads(med[med.rindex('{'):med.rindex('}') + 1])
ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={med['input_i']}:measured_TP={med['input_tp']}:"
      f"measured_LRA={med['input_lra']}:measured_thresh={med['input_thresh']}:offset={med['target_offset']}:linear=true")
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', tmp, '-i', mezcla, '-af', ln + ',aresample=48000',
                '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-t', str(TOTAL),
                '-movflags', '+faststart', SALIDA], check=True)
os.remove(tmp); os.remove(mezcla)
if hoja:
    filas = [np.hstack(hoja[i:i + 10] + [np.zeros_like(hoja[0])] * (10 - len(hoja[i:i + 10]))) for i in range(0, len(hoja), 10)]
    Image.fromarray(np.vstack(filas)).save(os.path.splitext(SALIDA)[0] + '-hoja.jpg', quality=88)
print('ok', SALIDA, TOTAL)
