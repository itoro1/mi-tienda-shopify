"""Monta un anuncio corto 9:16 en 4K a partir de una lista de cortes (JSON), sin gastar créditos.

Uso: python3 anuncio_cortes.py CORTES.json SALIDA.mp4 [--muestra]
Las rutas del JSON son relativas a la carpeta del JSON. Con --muestra solo saca la hoja de fotogramas.

20/11/2026. Lo pidió el dueño: estudiar la competencia y hacer un anuncio que venda más. El estudio
(anuncios/2026-11/prompt-mejora-anuncio.md y LEEME) dice que el vídeo de la chica es el que vende, pero
que dura 32 s, la media de visionado es de 6 s y el precio sale en el segundo 12. Este script recorta y
reordena ese vídeo SIN romper la boca: cada tramo hablado («H…») lleva su propio audio, a la misma hora.

Formato del JSON:
{
  "pista": "voz-chica.mp4",                       # audio de la chica (la línea de tiempo de los tramos H)
  "voz_nueva": "voz-elena.mp3",                   # opcional
  "fuentes": {
    "H1": {"video": "k4/1.mp4", "pista_desde": 0.0},          # tramo hablado: su segundo 0 = segundo pista_desde de la pista
    "B3D": {"video": "B3D.mp4"},                               # plano sin boca
    "foto:cajas": {"foto": "cajas.jpg", "recorte": [x0, y0, x1, y1], "zoom": 0.08}   # foto con zoom lento
  },
  "bloques": [                                     # cada bloque: un trozo de audio y los planos que lo cubren
    {"audio": ["pista", 0.0, 4.875], "planos": [{"fuente": "H1"}]},
    {"audio": ["pista", 4.9, 8.9], "planos": [{"fuente": "A3D", "desde": 0, "dur": 2.0}, {"fuente": "B3D", "desde": 0}]},
    {"audio": ["silencio", 1.0], "planos": [{"fuente": "GIRO360", "desde": 0}]}
  ],
  "acelera": 1.08,                                # todo junto (imagen y voz): la boca sigue cuadrando
  "cierre": {"dur": 1.8, "plazo": "Precio de lanzamiento hasta el 30/11 o fin de existencias"},
  "guion": "texto tal como se oye, en orden",      # para los subtítulos palabra a palabra
  "textos": [ {"tipo": "banda", "de": 0, "a": 6.5, "l1": "…", "l2": "…"},
              {"tipo": "check", "de": 8, "a": 11, "items": ["Caja sin abrir", "Original de Apple"]},
              {"tipo": "precio", "de": 11, "a": 14.5, "grande": "18,99 €", "l1": "…", "l2": "…"},
              {"tipo": "pastilla", "de": 14.5, "a": 17, "texto": "…"} ]          # tiempos del vídeo FINAL
}
El último plano de cada bloque se estira hasta llenar el bloque; en los tramos H, el punto de entrada
sale de la hora del audio, así que la boca cuadra siempre.
"""
import difflib, json, os, re, subprocess, sys, tempfile, unicodedata
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont

spec_p, salida = sys.argv[1], sys.argv[2]
BASE = os.path.dirname(os.path.abspath(spec_p))
spec = json.load(open(spec_p, encoding='utf8'))
FUENTES = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fuentes')
K = 2; W, H, FPS = 1080 * K, 1920 * K, 24
NOCHE = (11, 15, 26); ORO = (214, 180, 112); MARFIL = (244, 241, 234); ROJO = (196, 38, 46); VERDE = (52, 199, 89)
tmp = tempfile.mkdtemp()
ENC = ['-an', '-c:v', 'libx264', '-crf', '14', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-r', str(FPS)]


def ruta(p): return p if os.path.isabs(p) else os.path.join(BASE, p)
def ff(*a): subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *a], check=True)
def unb(t, w=700): f = ImageFont.truetype(f'{FUENTES}/Unbounded.ttf', int(t * K)); f.set_variation_by_axes([w]); return f
def arc(t, w=600): f = ImageFont.truetype(f'{FUENTES}/Archivo.ttf', int(t * K)); f.set_variation_by_axes([w, 100]); return f
def duracion(p): return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p], capture_output=True, text=True).stdout)


def centro(d, y, t, f, col, **kw): d.text(((W - d.textlength(t, font=f)) / 2, y * K), t, font=f, fill=col, **kw)


def encaja(d, t, tam, ancho, fuente=unb, w=700):
    f = fuente(tam, w)
    while d.textlength(t, font=f) > ancho * K: tam -= 2; f = fuente(tam, w)
    return f


# ---------- 1) imagen: plano a plano, en fotogramas exactos ----------
def plano(fu, desde, n, out):
    """Saca n fotogramas de la fuente fu desde el segundo «desde», a 2160x3840."""
    if 'foto' in fu:
        im = cv2.imread(ruta(fu['foto']))
        if fu.get('recorte'):
            x0, y0, x1, y1 = fu['recorte']; im = im[y0:y1, x0:x1]
        h, w = im.shape[:2]                                     # recorte 9:16 centrado si hace falta
        if w / h > 9 / 16: nw = int(h * 9 / 16); im = im[:, (w - nw) // 2:(w - nw) // 2 + nw]
        else: nh = int(w * 16 / 9); im = im[(h - nh) // 2:(h - nh) // 2 + nh]
        z = fu.get('zoom', 0.08)
        im = cv2.resize(im, (int(W * (1 + z)), int(H * (1 + z))), interpolation=cv2.INTER_CUBIC if im.shape[1] < W else cv2.INTER_AREA)
        if fu.get('nitidez', 0.6):                              # las fotos del móvil, ampliadas, ganan con un poco de enfoque
            g = cv2.GaussianBlur(im, (0, 0), 2.2); im = cv2.addWeighted(im, 1 + fu.get('nitidez', 0.6), g, -fu.get('nitidez', 0.6), 0)
        cv2.imwrite(f'{out}.png', im)
        d = n / FPS; ax, ay = fu.get('ancla', [0.5, 0.5])
        ff('-loop', '1', '-framerate', str(FPS), '-i', f'{out}.png', '-vf',
           f"format=rgb24,scale=w='{W}*(1+{z}*t/{d})':h='{H}*(1+{z}*t/{d})':eval=frame:flags=bicubic,crop={W}:{H}:'(in_w-out_w)*{ax}':'(in_h-out_h)*{ay}',setsar=1,format=yuv420p",
           '-frames:v', str(n), *ENC, out)
        return
    v = ruta(fu['video']); ini = int(round(desde * FPS))
    disp = int(round(duracion(v) * FPS)) - ini
    vf = f"trim=start_frame={ini},setpts=PTS-STARTPTS,scale={W}:{H}:flags=lanczos,setsar=1"
    if disp < n:                                                 # si falta, se congela el último fotograma
        vf += f",tpad=stop_mode=clone:stop={n - disp + 2}"
    ff('-i', v, '-vf', vf, '-frames:v', str(n), *ENC, out)


fuentes = spec['fuentes']; partes = []; audio_tramos = []; cuadros = 0; t_audio = 0.0
for bi, b in enumerate(spec['bloques']):
    a = b['audio']
    dur = a[2] - a[1] if a[0] in ('pista', 'nueva') else a[1]
    fin_b = int(round((t_audio + dur) * FPS)); nb = fin_b - cuadros
    usados = 0
    for pi, p in enumerate(b['planos']):
        fu = fuentes[p['fuente']]
        n = nb - usados if pi == len(b['planos']) - 1 else int(round(p['dur'] * FPS))
        if 'pista_desde' in fu:                                   # tramo hablado: entra a la hora de su audio
            if a[0] != 'pista': raise SystemExit(f'{p["fuente"]}: un tramo hablado necesita su propio audio')
            desde = a[1] + usados / FPS - fu['pista_desde']
        else:
            desde = p.get('desde', 0.0)
        out = f'{tmp}/b{bi}_{pi}.mp4'; plano(fu, desde, n, out); partes.append(out); usados += n
    cuadros = fin_b; t_audio += dur; audio_tramos.append(a)
open(f'{tmp}/l.txt', 'w').write(''.join(f"file '{p}'\n" for p in partes))
ff('-f', 'concat', '-safe', '0', '-i', f'{tmp}/l.txt', '-c', 'copy', f'{tmp}/v.mp4')

# ---------- 2) audio: los mismos tramos, con fundidos de 15 ms para que no chasquee ----------
filtros, entradas = [], ['-i', ruta(spec['pista'])]
if spec.get('voz_nueva'): entradas += ['-i', ruta(spec['voz_nueva'])]
for i, a in enumerate(audio_tramos):
    if a[0] == 'silencio':
        filtros.append(f'anullsrc=r=44100:cl=stereo,atrim=0:{a[1]}[s{i}]')
    else:
        src = 0 if a[0] == 'pista' else 1; d = a[2] - a[1]
        filtros.append(f'[{src}:a]atrim={a[1]}:{a[2]},asetpts=PTS-STARTPTS,aresample=44100,aformat=channel_layouts=stereo,'
                       f'afade=t=in:d=0.015,afade=t=out:st={max(d - 0.015, 0)}:d=0.015[s{i}]')
filtros.append(''.join(f'[s{i}]' for i in range(len(audio_tramos))) + f'concat=n={len(audio_tramos)}:v=0:a=1[a]')
ff(*entradas, '-filter_complex', ';'.join(filtros), '-map', '[a]', '-c:a', 'pcm_s16le', f'{tmp}/a.wav')

# ---------- 3) acelerar todo junto y añadir la tarjeta de cierre ----------
AC = spec.get('acelera', 1.0)
ff('-i', f'{tmp}/v.mp4', '-i', f'{tmp}/a.wav', '-filter_complex', f'[0:v]setpts=PTS/{AC},fps={FPS}[v];[1:a]atempo={AC}[a]',
   '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-crf', '14', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-c:a', 'pcm_s16le', f'{tmp}/r.mkv')
CUERPO = duracion(f'{tmp}/r.mkv')


def tarjeta_cierre(c):
    im = Image.new('RGB', (W, H), NOCHE); d = ImageDraw.Draw(im)
    centro(d, 330, 'pillatumovil', unb(84), MARFIL)
    centro(d, 470, 'Cargador 20 W + cable · originales de Apple', arc(34), MARFIL)
    centro(d, 550, '18,99 €', unb(170), ORO)
    centro(d, 775, 'En Apple, 38,00 € (precio del 01/11/2026)', arc(30, 500), MARFIL)
    centro(d, 830, 'Compramos por cantidad y ganamos menos', arc(30, 500), MARFIL)
    if c.get('plazo'):
        f = encaja(d, c['plazo'], 30, 900, arc, 800); tw = d.textlength(c['plazo'], font=f)
        d.rounded_rectangle(((W - tw) / 2 - 40 * K, 915 * K, (W + tw) / 2 + 40 * K, 1000 * K), radius=42 * K, fill=ROJO)
        centro(d, 938, c['plazo'], f, (255, 255, 255))
    centro(d, 1045, 'Envío gratis · llega a su casa en 24-48 h', arc(34, 700), MARFIL)
    d.rounded_rectangle((70 * K, 1160 * K, W - 70 * K, 1330 * K), radius=85 * K, fill=ORO)
    centro(d, 1203, 'pillatumovil.com', unb(72), NOCHE)
    if c.get('pie'): centro(d, 1365, c['pie'], arc(30, 600), MARFIL)
    return im


c = spec.get('cierre', {'dur': 1.8}); nc = int(round(c['dur'] * FPS))
tarjeta_cierre(c).save(f'{tmp}/cierre.png')
ff('-loop', '1', '-framerate', str(FPS), '-i', f'{tmp}/cierre.png', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo', '-frames:v', str(nc),
   '-vf', 'format=yuv420p', '-c:v', 'libx264', '-crf', '14', '-preset', 'medium', '-r', str(FPS), '-c:a', 'pcm_s16le', '-shortest', f'{tmp}/c.mkv')
ff('-i', f'{tmp}/r.mkv', '-i', f'{tmp}/c.mkv', '-filter_complex', '[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]', '-map', '[v]', '-map', '[a]',
   '-c:v', 'libx264', '-crf', '14', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-r', str(FPS), '-c:a', 'pcm_s16le', f'{tmp}/m.mkv')
TOTAL = duracion(f'{tmp}/m.mkv'); NT = int(round(TOTAL * FPS))
ff('-i', f'{tmp}/m.mkv', '-vn', '-ac', '1', '-ar', '16000', '-f', 'f32le', f'{tmp}/a16.raw')

# ---------- 4) subtítulos palabra a palabra (tiempos de la voz final, texto del guion) ----------
def norm(s):
    s = unicodedata.normalize('NFD', s.lower()); return re.sub(r'[^a-z0-9]', '', ''.join(ch for ch in s if unicodedata.category(ch) != 'Mn'))


fichas = []
for m in re.finditer(r'\[([^|\]]+)\|([^\]]+)\]([.,:;!?…»]*)|(\S+)', spec['guion']):
    if m.group(1): dichas, pant, cola = m.group(1).split(), m.group(2) + m.group(3), m.group(3)
    else: dichas, pant = [m.group(4)], m.group(4); cola = pant[-1] if pant[-1] in '.,:;!?…»' else ''
    fichas.append((dichas, pant, bool(cola)))
dichas = [(norm(w), i) for i, f in enumerate(fichas) for w in f[0]]
from faster_whisper import WhisperModel
audio = np.fromfile(f'{tmp}/a16.raw', np.float32)
segs, _ = WhisperModel('small', device='cpu', compute_type='int8').transcribe(audio, language='es', word_timestamps=True,
                                                                              initial_prompt=re.sub(r'\[([^|\]]+)\|[^\]]+\]', r'\1', spec['guion']))
oidas = [(norm(w.word), w.start, w.end) for s in segs for w in s.words if norm(w.word)]
t0 = [None] * len(dichas); t1 = [None] * len(dichas)
for a_, b_, n_ in difflib.SequenceMatcher(None, [d[0] for d in dichas], [o[0] for o in oidas], autojunk=False).get_matching_blocks():
    for k in range(n_): t0[a_ + k], t1[a_ + k] = oidas[b_ + k][1], oidas[b_ + k][2]
conoc = [i for i, t in enumerate(t0) if t is not None]
if not conoc: raise SystemExit('No se pudo casar la voz con el guion.')
for i in range(len(dichas)):
    if t0[i] is None:
        ant = max([q for q in conoc if q < i], default=None); sig = min([q for q in conoc if q > i], default=None)
        ta = t1[ant] if ant is not None else 0.0; tb = t0[sig] if sig is not None else CUERPO
        hueco = (sig if sig is not None else len(dichas)) - (ant if ant is not None else -1); pos = i - (ant if ant is not None else -1)
        t0[i] = ta + (tb - ta) * (pos - 1) / max(1, hueco - 1); t1[i] = ta + (tb - ta) * pos / max(1, hueco - 1)
pal = []
for i, (ds, pant, corta) in enumerate(fichas):
    idx = [k for k, d in enumerate(dichas) if d[1] == i]; pal.append((pant, t0[idx[0]], t1[idx[-1]], corta))
grupos, g = [], []
for p in pal:
    g.append(p)
    if p[3] or len(g) == 3 or sum(len(x[0]) for x in g) > 16: grupos.append(g); g = []
if g: grupos.append(g)

# ---------- 5) rótulos ----------
SUB_Y = spec.get('subtitulos_y', 1560)


def capa_banda(t):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im); y = t.get('y', 250)
    f1 = encaja(d, t['l1'], t.get('t1', 54), 960, unb, 800); w1 = d.textlength(t['l1'], font=f1)
    alto = 120 + (70 if t.get('l2') else 0)
    d.rounded_rectangle(((W - w1) / 2 - 44 * K, y * K, (W + w1) / 2 + 44 * K, (y + alto) * K), radius=36 * K, fill=NOCHE + (226,))
    centro(d, y + 24, t['l1'], f1, ORO if t.get('oro', True) else MARFIL)
    if t.get('l2'): centro(d, y + 112, t['l2'], encaja(d, t['l2'], 30, 900, arc, 600), MARFIL)
    return im


def capa_check(t, k):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im); y = t.get('y', 330); f = arc(46, 800)
    ancho = max(d.textlength(x, font=f) for x in t['items']) + 150 * K; x0 = (W - ancho) / 2
    for i, txt in enumerate(t['items'][:k]):
        yy = (y + i * 110) * K
        d.rounded_rectangle((x0, yy, x0 + ancho, yy + 90 * K), radius=45 * K, fill=(255, 255, 255, 236))
        d.ellipse((x0 + 18 * K, yy + 15 * K, x0 + 78 * K, yy + 75 * K), fill=VERDE)
        d.line([(x0 + 33 * K, yy + 46 * K), (x0 + 45 * K, yy + 58 * K), (x0 + 64 * K, yy + 33 * K)], fill=(255, 255, 255), width=8 * K, joint='curve')
        d.text((x0 + 100 * K, yy + 18 * K), txt, font=f, fill=NOCHE)
    return im


def capa_precio(t):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im); y0 = t.get('y', 1250)
    alto = 250 + (52 if t.get('l2') else 0)
    d.rounded_rectangle((150 * K, y0 * K, W - 150 * K, (y0 + alto) * K), radius=40 * K, fill=NOCHE + (232,))
    centro(d, y0 + 18, t['grande'], unb(120), ORO)
    if t.get('l1'): centro(d, y0 + 180, t['l1'], encaja(d, t['l1'], 30, 740, arc, 600), MARFIL)
    if t.get('l2'): centro(d, y0 + 232, t['l2'], encaja(d, t['l2'], 28, 740, arc, 500), MARFIL)
    return im


def capa_pastilla(t):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im); y = t.get('y', 300)
    f = encaja(d, t['texto'], t.get('tam', 44), 940, arc, 800); tw = d.textlength(t['texto'], font=f)
    d.rounded_rectangle(((W - tw) / 2 - 40 * K, y * K, (W + tw) / 2 + 40 * K, (y + 92) * K), radius=46 * K,
                        fill=tuple(t.get('fondo', NOCHE)) + (230,))
    centro(d, y + 20, t['texto'], f, tuple(t.get('color', MARFIL)))
    return im


capas = []                                                       # (de, a, imagen RGBA en numpy premultiplicada)
for t in spec.get('textos', []):
    if t['tipo'] == 'check':
        paso = t.get('paso', 0.45)
        for k in range(1, len(t['items']) + 1):
            capas.append((t['de'] + (k - 1) * paso, t['de'] + k * paso if k < len(t['items']) else t['a'], capa_check(t, k)))
    else:
        capas.append((t['de'], t['a'], {'banda': capa_banda, 'precio': capa_precio, 'pastilla': capa_pastilla}[t['tipo']](t)))
capas = [(a, b, np.asarray(im).astype(np.float32)) for a, b, im in capas]
FS = unb(74, 800); med = ImageDraw.Draw(Image.new('RGB', (10, 10)))


def banda_sub(grupo, activa):
    im = Image.new('RGBA', (W, 190 * K), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    f = FS; txt = ' '.join(p[0] for p in grupo)
    while med.textlength(txt, font=f) > W - 90 * K: f = unb(f.size / K - 4, 800)
    x = (W - med.textlength(txt, font=f)) / 2; esp = med.textlength(' ', font=f)
    for k, p in enumerate(grupo):
        d.text((x, 40 * K), p[0], font=f, fill=ORO if k == activa else (255, 255, 255), stroke_width=8 * K, stroke_fill=(0, 0, 0))
        x += med.textlength(p[0], font=f) + esp
    return np.asarray(im).astype(np.float32)


subs = {}
def sub_en(t):
    for gi, g in enumerate(grupos):
        fin = g[-1][2] + 0.25
        if gi + 1 < len(grupos) and grupos[gi + 1][0][1] - g[-1][2] < 0.45: fin = grupos[gi + 1][0][1]
        if g[0][1] - 0.04 <= t < fin:
            act = max([k for k, w in enumerate(g) if w[1] - 0.04 <= t], default=0)
            if (gi, act) not in subs: subs[(gi, act)] = banda_sub(g, act)
            return subs[(gi, act)]
    return None


muestras = [int(x * FPS) for x in spec.get('muestras', [])]
lee = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-i', f'{tmp}/m.mkv', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
esc = None if '--muestra' in sys.argv else subprocess.Popen(
    ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', f'{tmp}/m.mkv',
     '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-r', str(FPS),
     '-c:a', 'aac', '-b:a', '192k', '-ar', '44100', '-ac', '2', '-movflags', '+faststart', salida], stdin=subprocess.PIPE)
hoja = []
for n in range(NT):
    b = lee.stdout.read(W * H * 3)
    if len(b) < W * H * 3: break
    t = (n + 0.5) / FPS
    if t >= CUERPO and esc is not None: esc.stdin.write(b); continue     # la tarjeta de cierre va limpia
    F = np.frombuffer(b, np.uint8).reshape(H, W, 3).astype(np.float32)
    for a_, b_, cap in capas:
        if a_ <= t < b_:
            al = cap[..., 3:] / 255; F = F * (1 - al) + cap[..., :3] * al
    s = sub_en(t) if t < CUERPO else None
    if s is not None:
        y = SUB_Y * K; zona = F[y:y + s.shape[0]]; al = s[..., 3:] / 255; F[y:y + s.shape[0]] = zona * (1 - al) + s[..., :3] * al
    F = F.round().clip(0, 255).astype(np.uint8)
    if n in muestras: hoja.append(cv2.resize(F, (360, 640), interpolation=cv2.INTER_AREA))
    if esc is not None: esc.stdin.write(F.tobytes())
if esc is not None: esc.stdin.close(); esc.wait()
if hoja:
    filas = [np.hstack(hoja[i:i + 6] + [np.zeros_like(hoja[0])] * (6 - len(hoja[i:i + 6]))) for i in range(0, len(hoja), 6)]
    cv2.imwrite(os.path.splitext(salida)[0] + '-hoja.jpg', cv2.cvtColor(np.vstack(filas), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 85])
print('ok', salida, f'{TOTAL:.2f} s (cuerpo {CUERPO:.2f} s + cierre),', len(pal), 'palabras')
for g in grupos: print('  ', f'{g[0][1]:5.2f}', ' '.join(x[0] for x in g))
