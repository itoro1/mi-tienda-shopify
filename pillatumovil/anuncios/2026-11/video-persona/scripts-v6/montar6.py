"""Corta y reajusta un plano ya compuesto (las cajas 3D ya puestas), para la v6 del vídeo de la dependienta.

Uso: python3 montar6.py ENTRADA.mp4 PLAN.json SALIDA.mp4 [--hoja HOJA.jpg]

PLAN.json:
{"salen": 118,                                      # fotogramas de salida (tiene que cuadrar)
 "tramos": [{"de": 0, "a": 43, "salen": 50},        # fotogramas de entrada de..a (incluidos), estirados a 'salen'
            {"latigo": 2, "caja": [x0, y0, x1, y1]},# 2 fotogramas de barrido entre el último del tramo de antes y el
                                                    # primero del siguiente: desenfoque horizontal donde gira la caja
            {"de": 62, "a": 120, "salen": 66}],
 "lento_max": 0.12}                                 # ningún tramo puede ir más de un 12 % más lento (ni más rápido)
Un barrido puede llevar "fuera": "corte": fuera de su 'caja', corte seco a mitad del barrido en vez de fundido,
y "rampa": [arriba, abajo, izq, der]: en vez del borde difuminado de 40 px, rampas suaves de esos px hacia dentro de
la 'caja' (sin raya recta en la camiseta).

Los fotogramas intermedios se calculan con flujo óptico (OpenCV DIS) entre los dos de entrada más cercanos: en los
planos quietos (sujeta la caja y sonríe) no se nota. Salida: H.264 crf 12, yuv420p, 24 fps, sin audio.
"""
import json, subprocess, sys
import cv2, numpy as np

cv2.setNumThreads(2)
ent, plan_p, sal = sys.argv[1:4]
HOJA = sys.argv[sys.argv.index('--hoja') + 1] if '--hoja' in sys.argv else None
plan = json.load(open(plan_p))
W, H = [int(v) for v in subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height',
                                        '-of', 'csv=p=0', ent], capture_output=True, text=True).stdout.strip().split(',')[:2]]

# ---- qué fotograma (o mezcla) sale en cada posición ----
salida = []                     # ('t', tiempo_en_fotogramas) | ('latigo', a, b, alfa, caja)
tramos = plan['tramos']; lento = plan.get('lento_max', 0.12)
for k, tr in enumerate(tramos):
    if 'latigo' in tr:
        a, b = tramos[k - 1]['a'], tramos[k + 1]['de']
        for j in range(tr['latigo']):
            salida.append(('latigo', a, b, (j + 1) / (tr['latigo'] + 1), tr['caja'], tr.get('fuera', 'fundido'), tr.get('rampa')))
        continue
    n_in, n_out = tr['a'] - tr['de'] + 1, tr['salen']
    vel = n_in / n_out
    print(f"tramo {tr['de']}-{tr['a']}: {n_in} -> {n_out} fotogramas, velocidad x{vel:.3f}")
    assert abs(1 - vel) <= lento + 1e-9, f'cambio de velocidad de {abs(1 - vel) * 100:.1f} % (> {lento * 100:.0f} %)'
    for j in range(n_out):
        salida.append(('t', tr['de'] + (j * (n_in - 1) / (n_out - 1) if n_out > 1 else 0)))
assert len(salida) == plan['salen'], f"salen {len(salida)} fotogramas y tienen que ser {plan['salen']}"


# ---- lectura secuencial con una pequeña caché ----
class Lector:
    def __init__(self, ruta):
        self.p = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-i', ruta, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
        self.n = -1; self.cache = {}; self.fijos = {}

    def __call__(self, i):
        if i in self.fijos: return self.fijos[i]
        while self.n < i:
            b = self.p.stdout.read(W * H * 3)
            if len(b) < W * H * 3: raise IndexError(f'el vídeo no tiene el fotograma {i}')
            self.n += 1; self.cache[self.n] = np.frombuffer(b, np.uint8).reshape(H, W, 3)
            for k in [k for k in self.cache if k < self.n - 3]: del self.cache[k]
        return self.cache[i]


lee = Lector(ent)
DIS = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
FLUJOS = {}
RED = 4                                                        # el flujo se calcula a 1/4 y se amplía


def flujo(i, j):
    if (i, j) not in FLUJOS:
        a = cv2.cvtColor(cv2.resize(lee(i), (W // RED, H // RED), interpolation=cv2.INTER_AREA), cv2.COLOR_RGB2GRAY)
        b = cv2.cvtColor(cv2.resize(lee(j), (W // RED, H // RED), interpolation=cv2.INTER_AREA), cv2.COLOR_RGB2GRAY)
        f = DIS.calc(a, b, None)
        FLUJOS.clear(); FLUJOS[(i, j)] = cv2.resize(f, (W, H), interpolation=cv2.INTER_LINEAR) * RED
    return FLUJOS[(i, j)]


GX, GY = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))


def intermedio(i, j, al):
    """Fotograma entre i y j (al = 0 -> i, 1 -> j) con flujo en los dos sentidos."""
    f01 = flujo(i, j); f10 = flujo(j, i)
    a = cv2.remap(lee(i), GX - al * f01[..., 0], GY - al * f01[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    b = cv2.remap(lee(j), GX - (1 - al) * f10[..., 0], GY - (1 - al) * f10[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    return np.clip(a.astype(np.float32) * (1 - al) + b.astype(np.float32) * al + .5, 0, 255).astype(np.uint8)


def fotograma_t(t):
    i = int(np.floor(t + 1e-6)); al = t - i
    if al < 1e-3: return lee(i)
    if al > 1 - 1e-3: return lee(i + 1)
    return intermedio(i, i + 1, al)


def latigo(a, b, al, caja, fuera='fundido', rampa=None):
    """Barrido: fundido de a a b y, en la zona de la caja, desenfoque horizontal (más fuerte a mitad del barrido).
    fuera='corte': fuera de la zona de la caja no hay fundido sino corte seco a mitad del barrido (así la cara no sale
    con dos pares de ojos, uno mirando a cámara y otro a la caja; el cambio de mirada en un fotograma parece natural)."""
    if a not in lee.fijos: lee.fijos[a] = lee(a)             # los dos extremos del barrido se guardan aparte
    if b not in lee.fijos: lee.fijos[b] = lee(b)
    A = lee(a).astype(np.float32); B = lee(b).astype(np.float32)
    x0, y0, x1, y1 = caja
    L = int(round(W * .16 * np.sin(np.pi * al))) | 1           # largo del desenfoque: hasta el 16 % del ancho
    k = np.ones((1, L), np.float32) / L
    zA = cv2.filter2D(A[y0:y1, x0:x1], -1, k, borderType=cv2.BORDER_REFLECT)
    zB = cv2.filter2D(B[y0:y1, x0:x1], -1, k, borderType=cv2.BORDER_REFLECT)
    if rampa:                                                    # [arriba, abajo, izq, der]: rampas suaves hacia dentro
        m = np.zeros((H, W), np.float32)
        yy = np.arange(y0, y1, dtype=np.float32)[:, None]; xx = np.arange(x0, x1, dtype=np.float32)[None, :]
        def r(d, ancho): return np.ones_like(d) if ancho <= 0 else np.clip(d / ancho, 0, 1)
        v = r(yy - y0, rampa[0]) * r(y1 - 1 - yy, rampa[1]) * r(xx - x0, rampa[2]) * r(x1 - 1 - xx, rampa[3])
        m[y0:y1, x0:x1] = v * v * (3 - 2 * v); m = m[..., None]
    else:
        m = np.zeros((H, W), np.float32); m[y0:y1, x0:x1] = 1
        m = cv2.GaussianBlur(m, (0, 0), 40)[..., None]
    Ab = A.copy(); Ab[y0:y1, x0:x1] = zA; Bb = B.copy(); Bb[y0:y1, x0:x1] = zB
    Ab = A * (1 - m) + Ab * m; Bb = B * (1 - m) + Bb * m
    w = al * al * (3 - 2 * al)                                   # el cambio va más rápido en el centro
    if fuera == 'corte':
        w = m * w + (1 - m) * (0.0 if al <= .5 else 1.0)
    return np.clip(Ab * (1 - w) + Bb * w + .5, 0, 255).astype(np.uint8)


enc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', '24', '-i', '-',
                        '-an', '-c:v', 'libx264', '-crf', '12', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-r', '24', sal], stdin=subprocess.PIPE)
miniaturas = []
for n, s in enumerate(salida):
    F = fotograma_t(s[1]) if s[0] == 't' else latigo(*s[1:])
    enc.stdin.write(np.ascontiguousarray(F).tobytes())
    if HOJA: miniaturas.append((cv2.resize(F, (W // 8, H // 8), interpolation=cv2.INTER_AREA), n, s))
enc.stdin.close(); enc.wait()
lee.p.stdout.close(); lee.p.kill(); lee.p.wait()                 # el resto de la entrada no hace falta
if HOJA:
    filas = []
    for k in range(0, len(miniaturas), 12):
        fila = []
        for im, n, s in miniaturas[k:k + 12]:
            im = cv2.cvtColor(im, cv2.COLOR_RGB2BGR).copy()
            txt = f'{n} <{s[1]:.1f}' if s[0] == 't' else f'{n} latigo'
            cv2.putText(im, txt, (4, 22), cv2.FONT_HERSHEY_SIMPLEX, .6, (0, 255, 255), 2)
            fila.append(im)
        while len(fila) < 12: fila.append(np.zeros_like(fila[0]))
        filas.append(np.hstack(fila))
    cv2.imwrite(HOJA, np.vstack(filas), [cv2.IMWRITE_JPEG_QUALITY, 85])
print('ok', sal, len(salida), 'fotogramas')
