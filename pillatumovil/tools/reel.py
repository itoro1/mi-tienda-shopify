"""Fábrica de reels 9:16: monta un reel a partir de un guion (JSON) y una voz.

14/11/2026. El dueño quiere sacar reels a menudo sin grabar ni editar. Este script hace
la parte de montaje: escenas + voz + subtítulos PALABRA A PALABRA (la palabra que suena
va en dorado). No gasta créditos: usa los planos que ya hay en el repositorio, fichas
dibujadas con las fotos reales de las cajas y una tarjeta de cierre.

Uso: python3 reel.py GUION.json SALIDA.mp4
Las rutas del JSON son relativas a la carpeta del JSON. Formato:
{
  "voz": "voz.mp3",
  "guion": "Texto tal como se dice. [veinte vatios|20 W] = se dice lo primero, se escribe lo segundo.",
  "escenas": [
    {"tipo": "clip",   "hasta": 2.9, "fuente": "clip.mp4", "ini": 0, "chip": "18,99 €"},   # chip: opcional
    {"tipo": "ficha",  "hasta": 7.2, "rotulo": "¿QUÉ CABLE NECESITA?", "titulo": "iPhone 15 o posterior",
                       "grande": "USB-C", "foto": "caja.png"},
    {"tipo": "cierre", "hasta": 21.0, "plazo": "Precio de lanzamiento · hasta el 30/11 o fin de existencias"}
  ]
}
«hasta» es el segundo en que termina la escena. Los tiempos de las palabras salen de la voz
(faster-whisper) y se casan con el texto del guion, así que el subtítulo dice lo que pone
el guion aunque el reconocedor oiga otra cosa.

Reglas de la tienda que este script NO comprueba y hay que cumplir al escribir el guion:
de usted; nada de reseñas, clientes ni «antes» inventados; nada de «se agotan»; la
comparación con Apple, siempre «En Apple, 38,00 € (precio del 01/11/2026)».
"""
import difflib, json, os, re, subprocess, sys, tempfile, unicodedata
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

spec_p, salida = sys.argv[1], sys.argv[2]
BASE = os.path.dirname(os.path.abspath(spec_p))
spec = json.load(open(spec_p, encoding='utf8'))
FUENTES = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fuentes')
W, H, FPS = 1080, 1920, 24
NOCHE = (11, 15, 26); ORO = (214, 180, 112); MARFIL = (244, 241, 234); ROJO = (196, 38, 46)
tmp = tempfile.mkdtemp()


def ruta(p): return p if os.path.isabs(p) else os.path.join(BASE, p)
def ff(*a): subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *a], check=True)
def unb(t, w=700): f = ImageFont.truetype(f'{FUENTES}/Unbounded.ttf', t); f.set_variation_by_axes([w]); return f
def arc(t, w=600): f = ImageFont.truetype(f'{FUENTES}/Archivo.ttf', t); f.set_variation_by_axes([w, 100]); return f
def centro(d, y, t, f, col, **kw): d.text(((W - d.textlength(t, font=f)) / 2, y), t, font=f, fill=col, **kw)


def encaja(d, t, tam, ancho, w=700):
    f = unb(tam, w)
    while d.textlength(t, font=f) > ancho: tam -= 4; f = unb(tam, w)
    return f


# ---------- 1) palabras del guion y sus tiempos ----------
def norm(s):
    s = unicodedata.normalize('NFD', s.lower()); return re.sub(r'[^a-z0-9]', '', ''.join(c for c in s if unicodedata.category(c) != 'Mn'))


fichas = []          # (palabras dichas, texto en pantalla, corta_frase)
for m in re.finditer(r'\[([^|\]]+)\|([^\]]+)\]([.,:;!?…]*)|(\S+)', spec['guion']):
    if m.group(1): dichas, pant, cola = m.group(1).split(), m.group(2) + m.group(3), m.group(3)
    else: dichas, pant = [m.group(4)], m.group(4); cola = pant[-1] if pant[-1] in '.,:;!?…' else ''
    fichas.append((dichas, pant, bool(cola)))
dichas = [(norm(w), i) for i, f in enumerate(fichas) for w in f[0]]

from faster_whisper import WhisperModel
raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', ruta(spec['voz']), '-f', 'f32le', '-ac', '1', '-ar', '16000', '-'], capture_output=True).stdout
audio = np.frombuffer(raw, np.float32); DUR = len(audio) / 16000
segs, _ = WhisperModel('small', device='cpu', compute_type='int8').transcribe(audio, language='es', word_timestamps=True, initial_prompt=re.sub(r'\[([^|\]]+)\|[^\]]+\]', r'\1', spec['guion']))
oidas = [(norm(w.word), w.start, w.end) for s in segs for w in s.words if norm(w.word)]
t0 = [None] * len(dichas); t1 = [None] * len(dichas)
for a, b, n in difflib.SequenceMatcher(None, [d[0] for d in dichas], [o[0] for o in oidas], autojunk=False).get_matching_blocks():
    for k in range(n): t0[a + k], t1[a + k] = oidas[b + k][1], oidas[b + k][2]
# palabras que el reconocedor oyó distinto: se reparten entre las vecinas que sí casaron
conoc = [i for i, t in enumerate(t0) if t is not None]
if not conoc: raise SystemExit('No se pudo casar la voz con el guion.')
for i in range(len(dichas)):
    if t0[i] is None:
        ant = max([c for c in conoc if c < i], default=None); sig = min([c for c in conoc if c > i], default=None)
        ta = t1[ant] if ant is not None else 0.0; tb = t0[sig] if sig is not None else DUR
        hueco = (sig if sig is not None else len(dichas)) - (ant if ant is not None else -1)
        pos = i - (ant if ant is not None else -1)
        t0[i] = ta + (tb - ta) * (pos - 1) / max(1, hueco - 1); t1[i] = ta + (tb - ta) * pos / max(1, hueco - 1)
pal = []             # (texto en pantalla, inicio, fin, corta_frase)
for i, (ds, pant, corta) in enumerate(fichas):
    idx = [k for k, d in enumerate(dichas) if d[1] == i]
    pal.append((pant, t0[idx[0]], t1[idx[-1]], corta))
# grupos de hasta 3 palabras y 20 letras, sin cruzar signos de puntuación
grupos, g = [], []
for p in pal:
    g.append(p)
    if p[3] or len(g) == 3 or sum(len(x[0]) for x in g) > 16: grupos.append(g); g = []
if g: grupos.append(g)

# ---------- 2) escenas ----------
def ficha(e):
    im = Image.new('RGB', (W, H), NOCHE); d = ImageDraw.Draw(im)
    for y in range(H):      # degradado suave hacia abajo
        k = y / H; d.line([(0, y), (W, y)], fill=tuple(int(NOCHE[c] + (28 - NOCHE[c]) * k * .6) for c in range(3)))
    if e.get('rotulo'): centro(d, 190, e['rotulo'], arc(40, 800), ORO)
    centro(d, 270, e['titulo'], encaja(d, e['titulo'], 66, W - 140), MARFIL)
    centro(d, 370, e['grande'], encaja(d, e['grande'], 170, W - 160), ORO)
    if e.get('foto'):
        f = Image.open(ruta(e['foto'])).convert('RGBA'); alto = 860; f = f.resize((int(f.width * alto / f.height), alto), Image.LANCZOS)
        x, y = (W - f.width) // 2, 640
        sombra = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sombra.paste((0, 0, 0, 150), (x + 14, y + 26), f.split()[3]); sombra = sombra.filter(ImageFilter.GaussianBlur(26))
        im.paste(sombra, (0, 0), sombra); im.paste(f, (x, y), f)
    return im


def cierre(e):
    im = Image.new('RGB', (W, H), NOCHE); d = ImageDraw.Draw(im)
    centro(d, 330, 'pillatumovil', unb(84), MARFIL)
    centro(d, 470, 'Cargador 20 W + cable · originales de Apple', arc(34), MARFIL)
    centro(d, 550, '18,99 €', unb(170), ORO)
    centro(d, 775, 'En Apple, 38,00 € (precio del 01/11/2026)', arc(30, 500), MARFIL)
    centro(d, 830, 'Compramos por cantidad y ganamos menos', arc(30, 500), MARFIL)
    if e.get('plazo'):
        d.rounded_rectangle((60, 915, W - 60, 1000), radius=42, fill=ROJO)
        centro(d, 938, e['plazo'], encaja(d, e['plazo'], 32, W - 180, 800) if False else arc(30, 800), (255, 255, 255))
    centro(d, 1045, 'Envío gratis · llega a su casa en 24-48 h', arc(34, 700), MARFIL)
    d.rounded_rectangle((70, 1160, W - 70, 1330), radius=85, fill=ORO)
    centro(d, 1203, 'pillatumovil.com', unb(72), NOCHE)
    return im


def chip(txt):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    f = unb(110); tw = d.textlength(txt, font=f)
    d.rounded_rectangle(((W - tw) / 2 - 60, 1250, (W + tw) / 2 + 60, 1440), radius=40, fill=NOCHE + (232,))
    centro(d, 1272, txt, f, ORO)
    return im


ENC = ['-an', '-c:v', 'libx264', '-crf', '15', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-r', str(FPS)]
partes, t_ant, cuadros = [], 0.0, 0
for i, e in enumerate(spec['escenas']):
    n = round(e['hasta'] * FPS) - cuadros; cuadros += n; out = f'{tmp}/e{i}.mp4'
    if e['tipo'] == 'clip':
        vf = f"trim=start_frame={e.get('ini', 0)}:end_frame={e.get('ini', 0) + n},setpts=PTS-STARTPTS,scale=-2:{H}:flags=lanczos,crop={W}:{H},setsar=1"
        if e.get('chip'):
            chip(e['chip']).save(f'{tmp}/chip{i}.png')
            ff('-i', ruta(e['fuente']), '-i', f'{tmp}/chip{i}.png', '-filter_complex', f'[0:v]{vf}[v];[v][1:v]overlay=0:0', '-frames:v', str(n), *ENC, out)
        else:
            ff('-i', ruta(e['fuente']), '-vf', vf, '-frames:v', str(n), *ENC, out)
    else:
        (ficha(e) if e['tipo'] == 'ficha' else cierre(e)).resize((W * 2, H * 2), Image.LANCZOS).save(f'{tmp}/f{i}.png')
        d = n / FPS; z = 0.05 if e['tipo'] == 'ficha' else 0.02
        ff('-loop', '1', '-framerate', str(FPS), '-i', f'{tmp}/f{i}.png', '-vf',
           f"format=rgb24,scale=w='{W}*(1+{z}*t/{d})':h='{H}*(1+{z}*t/{d})':eval=frame:flags=bicubic,crop={W}:{H},setsar=1,format=yuv420p", '-frames:v', str(n), *ENC, out)
    partes.append(out)
open(f'{tmp}/l.txt', 'w').write(''.join(f"file '{p}'\n" for p in partes))
ff('-f', 'concat', '-safe', '0', '-i', f'{tmp}/l.txt', '-c', 'copy', f'{tmp}/v.mp4')
TOTAL = cuadros / FPS

# ---------- 3) subtítulos palabra a palabra ----------
BANDA_Y, BANDA_H = 1560, 190
FS = unb(74, 800)
medir = ImageDraw.Draw(Image.new('RGB', (10, 10)))


def banda(grupo, activa):
    im = Image.new('RGBA', (W, BANDA_H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    f = FS; txt = ' '.join(p[0] for p in grupo)
    while medir.textlength(txt, font=f) > W - 90: f = unb(f.size - 4, 800)
    x = (W - medir.textlength(txt, font=f)) / 2; esp = medir.textlength(' ', font=f)
    for k, p in enumerate(grupo):
        d.text((x, 40), p[0], font=f, fill=ORO if k == activa else (255, 255, 255), stroke_width=8, stroke_fill=(0, 0, 0))
        x += medir.textlength(p[0], font=f) + esp
    return np.asarray(im).tobytes()


vacia = bytes(W * BANDA_H * 4); estados = {}
p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-i', f'{tmp}/v.mp4', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{BANDA_H}', '-r', str(FPS), '-i', '-',
                      '-i', ruta(spec['voz']), '-filter_complex', f'[0:v][1:v]overlay=0:{BANDA_Y}:format=auto,format=yuv420p[v];[2:a]apad=whole_dur={TOTAL}[a]',
                      '-map', '[v]', '-map', '[a]', '-t', f'{TOTAL}', '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-r', str(FPS),
                      '-c:a', 'aac', '-b:a', '160k', '-ar', '44100', '-ac', '2', '-movflags', '+faststart', salida], stdin=subprocess.PIPE)
for n in range(cuadros):
    t = (n + 0.5) / FPS; cuadro = vacia
    for gi, g in enumerate(grupos):
        fin = g[-1][2] + 0.25
        if gi + 1 < len(grupos) and grupos[gi + 1][0][1] - g[-1][2] < 0.45: fin = grupos[gi + 1][0][1]
        if g[0][1] - 0.04 <= t < fin:
            act = max([k for k, w in enumerate(g) if w[1] - 0.04 <= t], default=0)
            if (gi, act) not in estados: estados[(gi, act)] = banda(g, act)
            cuadro = estados[(gi, act)]; break
    p.stdin.write(cuadro)
p.stdin.close(); p.wait()
print('ok', salida, f'{TOTAL:.1f} s,', len(pal), 'palabras,', len(grupos), 'grupos')
for g in grupos: print('  ', f'{g[0][1]:5.2f}', ' '.join(x[0] for x in g))
