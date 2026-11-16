"""Plano de producto: las dos cajas REALES girando 360 grados sobre fondo oscuro de marca, en 4K.

Uso: python3 caja3d_giro.py SALIDA.mp4 [FOTOGRAMAS=91] [--foto N.png]
16/11/2026. El dueño pidió estudiar «los 360 grados» de las cajas y enseñarlas tal cual son. Este plano
no lleva nada generado por IA: son las caras de sus fotos (tools/caja3d_texturas.py) sobre la caja en 3D
(tools/caja3d.py), con un reflejo y una sombra suaves en el suelo.
"""
import os, subprocess, sys
import cv2, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from caja3d import Caja, giro_x, giro_y

salida = sys.argv[1]; N = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 91
SW, SH = 2160, 3840; F = 1.5 * SH
K = np.array([[F, 0, SW / 2], [0, F, SH / 2], [0, 0, 1.0]])
TEX = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'fotos', 'caja3d')
NOCHE = np.float32([11, 15, 26])
SUELO = 2330                                              # altura del suelo en la imagen
CAB = np.radians(9)                                       # la cámara mira un poco desde arriba
# (modelo, x de la base, ancho en píxeles, desfase del giro)
PIEZAS = [('cargador', 570, 960, 0.0), ('cable', 1570, 960 * 67 / 79, 0.12)]

# fondo: azul noche con un foco suave detrás de las cajas y el suelo algo más claro
yy, xx = np.mgrid[0:SH, 0:SW].astype(np.float32)
foco = np.exp(-(((xx - SW / 2) / 1300) ** 2 + ((yy - 1750) / 1100) ** 2))
fondo = NOCHE + np.float32([34, 40, 58]) * foco[..., None]
piso = np.clip((yy - SUELO) / 600, 0, 1)[..., None]
fondo = fondo * (1 - .35 * piso) + np.float32([16, 20, 32]) * .35 * piso * np.exp(-((xx - SW / 2) / 1500) ** 2)[..., None]
cajas = {m: Caja(m, TEX) for m, *_ in PIEZAS}


def suave(u):                                             # arranca y frena despacio
    return u * u * (3 - 2 * u)


def pinta(n):
    u = n / (N - 1); img = fondo.copy()
    capas = []
    for modelo, xb, ancho, desf in PIEZAS:
        caja = cajas[modelo]
        g = 2 * np.pi * suave(np.clip((u - desf * .5) / (1 - desf * .5), 0, 1)) - np.radians(18)      # empieza un poco de lado
        c = np.array([0, 0, caja.D / 2]); R = giro_x(CAB) @ giro_y(g)
        z = F / ancho + caja.D / 2
        eje = np.array([(xb - K[0, 2]) / F * z, (SUELO - K[1, 2]) / F * z, z]); t = eje - R @ c
        esq = np.array([(x, y, zz) for x in (-.5, .5) for y in (0, -caja.H - caja.Ht) for zz in (0, caja.D)])
        X = (R @ esq.T).T + t; uv = (K @ X.T).T; uv = uv[:, :2] / uv[:, 2:3]
        x0, y0 = np.floor(uv.min(0)).astype(int) - 30; x1, y1 = np.ceil(uv.max(0)).astype(int) + 30
        x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, SW), min(y1, SH)
        Kz = K.copy(); Kz[0, 2] -= x0; Kz[1, 2] -= y0
        rgb, alfa = caja.pinta(Kz, R, t, (x1 - x0, y1 - y0), amb=0.83, dif=0.21)
        capas.append((z, x0, y0, rgb, alfa, int(uv[:, 1].max())))
    for z, x0, y0, rgb, alfa, yb in sorted(capas, key=lambda c: -c[0]):
        h, w = alfa.shape[:2]
        # sombra de contacto y reflejo en el suelo
        som = np.zeros((SH, SW), np.float32); cv2.ellipse(som, (x0 + w // 2, yb + 6), (int(w * .46), 46), 0, 0, 360, 1.0, -1)
        img *= (1 - .55 * cv2.GaussianBlur(som, (0, 0), 38))[..., None]
        cae = (np.clip(1 - np.arange(h) / 460.0, 0, 1) * .20)[:, None, None]             # el reflejo se apaga hacia abajo
        ref = cv2.GaussianBlur(np.dstack([rgb[::-1], alfa[::-1]]) * cae, (0, 0), 2.5)
        ry0 = yb + (yb - (y0 + h)) + 4
        if ry0 < SH:
            hh = min(h, SH - ry0); zz = img[ry0:ry0 + hh, x0:x0 + w]
            zz[:] = zz * (1 - ref[:hh, :, 3:]) + ref[:hh, :, :3]
        zz = img[y0:y0 + h, x0:x0 + w]; zz[:] = zz * (1 - alfa) + rgb
    g = np.random.default_rng(n).normal(0, 1.2, (SH // 2, SW // 2, 1)).astype(np.float32)
    return np.clip(img + cv2.resize(g, (SW, SH))[..., None], 0, 255).round().astype(np.uint8)


if '--foto' in sys.argv:
    cv2.imwrite(salida, cv2.cvtColor(pinta(int(sys.argv[sys.argv.index('--foto') + 1])), cv2.COLOR_RGB2BGR)); sys.exit()
enc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{SW}x{SH}', '-r', '24', '-i', '-',
                        '-an', '-c:v', 'libx264', '-crf', '10', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-r', '24', salida], stdin=subprocess.PIPE)
for n in range(N): enc.stdin.write(pinta(n).tobytes())
enc.stdin.close(); enc.wait(); print('ok', salida)
