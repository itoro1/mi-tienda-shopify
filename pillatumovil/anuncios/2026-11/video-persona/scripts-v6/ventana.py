"""R6 (23/11/2026): el escaparate del plano 2a se ve como en los planos 1, 3 y 4 (calle de día y desenfocada).

En 2a (clipA, Kling) la calle de detrás del cristal era nítida y al anochecer (farolas encendidas, follaje en
«mosaico» de IA); en los planos de Intone es una calle de día desenfocada (pieza «mostrador»). Aquí:
  - cristal = dos polígonos medidos en el fotograma 0 (en 1080x1920) que siguen el movimiento de la cámara
    (correlación de fase sobre la pared de fundas, a la izquierda, que no se mueve);
  - sin la chica: silueta MODNet de cada fotograma (el pelo que pasa por delante del cristal no se toca);
  - desenfoque gaussiano (sigma 10 px a 1080 = 20 a 4K) solo con píxeles del cristal (convolución normalizada:
    no entra el marco ni la chica);
  - color: una transformación Lab fija para todo el plano (media y desviación del cristal ya desenfocado) que lo
    lleva a lo medido en el cristal del plano 4 (fotograma 0) DESPUÉS de la curva de color k1 que el montaje pone
    a 2a: se calcula en el espacio de después de la curva y se deshace la curva. Sin parpadeo.
23/11 (2.ª revisión, N4): (1) el borde derecho de la hoja izquierda ya no es fijo (x 356 + movimiento de la pared):
el montante va con otro movimiento (paralaje) y entre los dos quedaba una tira de calle nítida al anochecer, con motas
de IA, de hasta 10-12 px al final del plano. Ahora en cada fotograma se mide el canto izquierdo del montante (donde el
azul del cristal cae al gris, filas sin la chica), recta robusta suavizada en el tiempo, y el cristal llega hasta él.
(2) Las farolas y luces cálidas de la calle no entran en el desenfoque (quedaba una bola de luz, «bokeh», en
(165, 310)): fuera del cristal que se promedia los píxeles muy claros no azules y los cálidos (su halo amarillo llega a ~50 px),
más 15 px.
Uso: python3 ventana.py ENTRADA_2a.mp4 SALIDA.mp4 [--prueba 0,23,47 DIR]
"""
import os, subprocess, sys
for v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'): os.environ.setdefault(v, '2')
import cv2, numpy as np, onnxruntime as ort
from scipy.interpolate import PchipInterpolator
cv2.setNumThreads(2)
ENT, SAL = sys.argv[1:3]
PRUEBA = (sys.argv[sys.argv.index('--prueba') + 1].split(','), sys.argv[sys.argv.index('--prueba') + 2]) if '--prueba' in sys.argv else None
MOD = '/tmp/claude-0/-home-user-mi-tienda-shopify/684840b5-c1b1-582f-bcd6-bf822ef2e72f/scratchpad/modelos/modnet.onnx'
W, H = 2160, 3840
# cristal en el fotograma 0, coordenadas 1080x1920: hoja izquierda (de la pared de fundas al montante) y la de arriba
# a la derecha del montante (lo de debajo lo tapa su cabeza)
POLI = [np.array([(103, -20), (200, -20), (356, 112), (356, 1010), (103, 1010)], np.float32),
        np.array([(399, 192), (578, 296), (578, 470), (399, 470)], np.float32)]
SIGMA = 10.0
# objetivo: cristal del plano 4 (mostrador/4.mp4, fotograma 0, x 10-170, y 330-900 a 1080): Lab de OpenCV (8 bits)
OBJ_M = np.array([81.5, 127.4, 114.3]); OBJ_S = np.array([33.5, 4.9, 12.0])
# curva k1 del montaje (montaje_dependienta_v6.sh, ANCLAS['k1'])
DE = [(14.0, 15.5, 12.7), (173.5, 117.5, 90.5), (237.5, 228.2, 217.2)]
A = [(19.0, 15.5, 17.0), (199.2, 118.0, 83.4), (239.3, 227.0, 227.0)]
x8 = np.arange(256, dtype=np.float64); K1, K1i = [], []
for c in range(3):
    f = PchipInterpolator([0.0] + [p[c] for p in DE] + [255.0], [0.0] + [p[c] for p in A] + [255.0])(np.linspace(0, 255, 4096))
    K1.append((np.linspace(0, 255, 4096), f))
def k1(img):          # img float RGB 0-255
    return np.dstack([np.interp(img[..., c], *K1[c]) for c in range(3)])
def k1_inv(img):
    return np.dstack([np.interp(img[..., c], K1[c][1], K1[c][0]) for c in range(3)])

so = ort.SessionOptions(); so.intra_op_num_threads = 2; so.inter_op_num_threads = 1; so.log_severity_level = 3
SES = ort.InferenceSession(MOD, so, providers=['CPUExecutionProvider'])
def modnet(rgb):
    h, w = rgb.shape[:2]; s = 512 / min(h, w); hh, ww = int(round(h * s / 32) * 32), int(round(w * s / 32) * 32)
    x = cv2.resize(rgb, (ww, hh), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    x = ((x - 0.5) / 0.5).transpose(2, 0, 1)[None].copy()
    return cv2.resize(SES.run(None, {'input': x})[0][0, 0], (w, h), interpolation=cv2.INTER_LINEAR).clip(0, 1)

def leer():
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', ENT, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    while True:
        b = p.stdout.read(W * H * 3)
        if len(b) < W * H * 3: break
        yield np.frombuffer(b, np.uint8).reshape(H, W, 3)
fr = list(leer()); N = len(fr)
peq = [cv2.resize(f, (1080, 1920), interpolation=cv2.INTER_AREA) for f in fr]

# movimiento de la cámara: pared de fundas (x 0-100, y 80-1000) frente al fotograma 0
def pared(im):
    g = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)[80:1000, 0:100].astype(np.float32)
    return g - cv2.GaussianBlur(g, (0, 0), 8)
ref = pared(peq[0]); win = cv2.createHanningWindow(ref.shape[::-1], cv2.CV_32F); mov = []
for im in peq:
    (dx, dy), r = cv2.phaseCorrelate(ref, pared(im), win); mov.append((dx, dy))
mov = np.array(mov); mov = np.stack([np.convolve(np.pad(mov[:, k], 2, mode='edge'), np.ones(5) / 5, 'valid') for k in (0, 1)], 1)
print('cámara (px a 1080): x', mov[:, 0].round(1)[::8].tolist(), 'y', mov[:, 1].round(1)[::8].tolist())

PER = [modnet(im) for im in peq]                      # silueta de la chica (se usa dos veces)

# (1) canto izquierdo del montante en cada fotograma: x = a·y + b (1080), por filas sin la chica
def canto_montante(im, per, x0):
    b_ = cv2.GaussianBlur(im[..., 2].astype(np.float32), (0, 0), 1.0)
    ys, xs = [], []
    for y in range(125, 1000, 3):
        if per[y, int(x0) - 30:int(x0) + 30].max() > .2: continue
        c0, c1 = int(x0) - 22, int(x0) + 22
        d = b_[y, c0 + 2:c1 + 2] - b_[y, c0 - 2:c1 - 2]                    # caída del azul hacia la derecha
        j = int(np.argmin(d))
        if d[j] < -40: ys.append(y); xs.append(c0 + j)
    if len(ys) < 15: return None
    ys = np.array(ys, float); xs = np.array(xs, float); ok = np.ones(len(ys), bool)
    for _ in range(6):
        a, b = np.polyfit(ys[ok], xs[ok], 1); r = np.abs(xs - (a * ys + b)); ok = r < max(1.5, 2.5 * np.median(r[ok]))
    return a, b, len(ys)
CANTO = []
for n, im in enumerate(peq):
    r = canto_montante(im, PER[n], 356 + mov[n, 0] + 6)
    CANTO.append(r[:2] if r else (np.nan, np.nan))
CANTO = np.array(CANTO)
for k in (0, 1):
    v = ~np.isnan(CANTO[:, k]); CANTO[:, k] = np.interp(np.arange(N), np.where(v)[0], CANTO[v, k])
    CANTO[:, k] = np.convolve(np.pad(CANTO[:, k], 3, mode='edge'), np.ones(7) / 7, 'valid')
print('canto del montante (x a y=250, por fotograma):', (CANTO[:, 0] * 250 + CANTO[:, 1]).round(1)[::6].tolist())

def mascara(n):
    m = np.zeros((1920, 1080), np.uint8)
    for k, P in enumerate(POLI):
        P = P + mov[n]
        if k == 0:                       # el borde derecho de la hoja izquierda, en el canto medido (+0,5 px)
            P = P.copy(); a, b = CANTO[n]
            for j, (x, y) in enumerate(P):
                if abs(x - (356 + mov[n, 0])) < 1e-3: P[j, 0] = a * y + b + .5
        cv2.fillPoly(m, [np.round(P).astype(np.int32)], 1)
    return m.astype(np.float32)

# pasada 1: desenfoque de cada fotograma y estadística del cristal (para la transformación fija)
borr, alfas, muestras = [], [], []
for n, im in enumerate(peq):
    per = PER[n]; vid = mascara(n)
    w = vid * (1 - cv2.dilate(per, np.ones((7, 7), np.uint8)))
    # (2) farolas y luces cálidas fuera del promedio (si no, queda su bola de luz desenfocada)
    f_ = im.astype(np.float32); L_ = f_.mean(2)
    luz = ((L_ > 190) & (f_[..., 2] - f_[..., 0] < 30)) | ((f_[..., 0] - f_[..., 2] > 20) & (L_ > 90))   # y su halo cálido
    luz = cv2.dilate((luz & (vid > .5)).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))) > 0
    w = ((w > .5) & ~luz).astype(np.float32)
    num = cv2.GaussianBlur(im.astype(np.float32) * w[..., None], (0, 0), SIGMA); den = cv2.GaussianBlur(w, (0, 0), SIGMA)
    b = num / np.maximum(den, 1e-4)[..., None]
    # donde no hay cristal cerca (den ~ 0): media más ancha
    num2 = cv2.GaussianBlur(im.astype(np.float32) * w[..., None], (0, 0), SIGMA * 3); den2 = cv2.GaussianBlur(w, (0, 0), SIGMA * 3)
    t = np.clip(den / 0.25, 0, 1)[..., None]; b = b * t + num2 / np.maximum(den2, 1e-4)[..., None] * (1 - t)
    a = cv2.GaussianBlur(vid, (0, 0), 1.5) * (1 - per)
    borr.append(b); alfas.append(a)
    sel = (w > .5) & (den > .3)
    muestras.append(k1(b)[sel][::7])
mu = np.concatenate(muestras).clip(0, 255).astype(np.uint8)
lab = cv2.cvtColor(mu[None], cv2.COLOR_RGB2LAB)[0].astype(np.float64)
SM, SS = lab.mean(0), lab.std(0)
print('cristal 2a desenfocado (Lab, tras k1): media', SM.round(1), 'desv.', SS.round(1), '-> objetivo', OBJ_M, OBJ_S)

def grado(b):
    lab = cv2.cvtColor(np.clip(k1(b), 0, 255).astype(np.float32) / 255, cv2.COLOR_RGB2LAB)   # L 0-100, a/b +-127
    sc = np.array([100 / 255, 1, 1]); off = np.array([0, 128, 128])
    l8 = lab / sc + off
    l8 = (l8 - SM) * (OBJ_S / SS) + OBJ_M
    lab2 = ((l8 - np.array([0, 128, 128])) * sc).astype(np.float32)
    rgb = cv2.cvtColor(lab2, cv2.COLOR_LAB2RGB) * 255
    return k1_inv(np.clip(rgb, 0, 255))

enc = None if PRUEBA else subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', '24', '-i', '-',
                                            '-c:v', 'libx264', '-crf', '12', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-an', SAL], stdin=subprocess.PIPE)
for n in range(N):
    if PRUEBA and str(n) not in PRUEBA[0]: continue
    g = grado(borr[n])
    G = cv2.resize(g.astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
    a = cv2.resize(alfas[n], (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
    # el pelo con mucho detalle: la silueta de MODNet a 4K desde la de 1080 (suave), suficiente sobre una calle borrosa
    out = np.clip(fr[n].astype(np.float32) * (1 - a) + G * a + 0.5, 0, 255).astype(np.uint8)
    if PRUEBA:
        os.makedirs(PRUEBA[1], exist_ok=True)
        cv2.imwrite(f'{PRUEBA[1]}/v{n:03d}.jpg', cv2.cvtColor(np.hstack([fr[n], out])[:2400, :], cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 88])
    else:
        enc.stdin.write(out.tobytes())
if enc: enc.stdin.close(); enc.wait()
print('ok', SAL, N, 'fotogramas')
