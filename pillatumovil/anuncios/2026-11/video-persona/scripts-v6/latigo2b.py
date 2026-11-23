"""3.ª revisión de la v6 (23/11, R2-2b-turn): el giro de la caja del adaptador en 2b (fotogramas 32-49 de cajas/2b.mp4 =
197-214 del vídeo) tiene fallos de composición que se ven en pausa: fantasma del pulgar y «U»/«2» dobles (197-200), muescas
blancas entre los dedos y el canto (201-204), una mota oscura pegada a la cara blanca (203-209) y el canto de la palma en
escalera (210-214). En vez de retocarlos, el barrido (que antes iba de 50 a 52, del canto a la trasera) empieza antes:
de 31 (último fotograma limpio, la caja aún casi de frente) a 53 (la trasera), en 5 fotogramas, como un giro rápido.

Uso: python3 latigo2b.py cajas/2b.mp4 cajas/2b_latigo.mp4
Salida: 0-31 de 2b.mp4 tal cual, 5 de barrido, 53-117 tal cual = 102 fotogramas (2160x3840, crf 12). El montaje
(tools/montaje_dependienta_v6.sh, LATIGO2B=1) reparte la trasera en lo que queda del plano (ver allí).
El barrido es el de montar6.py (misma zona 'caja' y rampas que el de antes; fuera de la zona, corte seco a mitad)."""
import subprocess, sys
import cv2, numpy as np
cv2.setNumThreads(2)
ENT, SAL = sys.argv[1:3]
A, B, N_LAT = 31, 53, 5
CAJA, RAMPA = [0, 1250, 1230, 3500], [450, 350, 0, 180]          # de corte-2b.json
W, H = 2160, 3840
p = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-i', ENT, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
fr = []
while True:
    b = p.stdout.read(W * H * 3)
    if len(b) < W * H * 3: break
    fr.append(np.frombuffer(b, np.uint8).reshape(H, W, 3))
assert len(fr) == 118, len(fr)


def latigo(Af, Bf, al):
    A_ = Af.astype(np.float32); B_ = Bf.astype(np.float32); x0, y0, x1, y1 = CAJA
    L = int(round(W * .16 * np.sin(np.pi * al))) | 1
    k = np.ones((1, L), np.float32) / L
    zA = cv2.filter2D(A_[y0:y1, x0:x1], -1, k, borderType=cv2.BORDER_REFLECT)
    zB = cv2.filter2D(B_[y0:y1, x0:x1], -1, k, borderType=cv2.BORDER_REFLECT)
    m = np.zeros((H, W), np.float32)
    yy = np.arange(y0, y1, dtype=np.float32)[:, None]; xx = np.arange(x0, x1, dtype=np.float32)[None, :]
    r = lambda d, a: np.ones_like(d) if a <= 0 else np.clip(d / a, 0, 1)
    v = r(yy - y0, RAMPA[0]) * r(y1 - 1 - yy, RAMPA[1]) * r(xx - x0, RAMPA[2]) * r(x1 - 1 - xx, RAMPA[3])
    m[y0:y1, x0:x1] = v * v * (3 - 2 * v); m = m[..., None]
    Ab = A_.copy(); Ab[y0:y1, x0:x1] = zA; Bb = B_.copy(); Bb[y0:y1, x0:x1] = zB
    Ab = A_ * (1 - m) + Ab * m; Bb = B_ * (1 - m) + Bb * m
    w = al * al * (3 - 2 * al); w = m * w + (1 - m) * (0.0 if al <= .5 else 1.0)
    return np.clip(Ab * (1 - w) + Bb * w + .5, 0, 255).astype(np.uint8)


sal = fr[:A + 1] + [latigo(fr[A], fr[B], (j + 1) / (N_LAT + 1)) for j in range(N_LAT)] + fr[B:]
enc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', '24', '-i', '-',
                        '-an', '-c:v', 'libx264', '-crf', '12', '-preset', 'medium', '-pix_fmt', 'yuv420p', SAL], stdin=subprocess.PIPE)
for f in sal: enc.stdin.write(np.ascontiguousarray(f).tobytes())
enc.stdin.close(); enc.wait()
print('ok', SAL, len(sal), 'fotogramas')
