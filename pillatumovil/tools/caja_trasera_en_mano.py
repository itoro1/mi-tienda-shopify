"""Pone la cara TRASERA real de la caja del cargador sobre la caja que sostiene la chica.

Uso: python3 caja_trasera_en_mano.py FOTO.png TRASERA_REAL.png SALIDA.png X0 Y0 X1 Y1

12/11/2026. El dueño quiere que, al dar la vuelta a la caja, la parte de atrás se vea
«igual» que la real, con todas sus letras. La IA no escribe bien textos pequeños, así que
la trasera no se genera: se pega la foto real (fotos/cine/caja-cargador-trasera.png) sobre
la caja de la foto, con perspectiva, la misma luz y respetando los dedos.
X0 Y0 X1 Y1 es un recuadro amplio alrededor de la caja en FOTO.
La imagen resultante se usa como fotograma final del clip (el inicial es la foto original).
"""
import sys
import numpy as np
from PIL import Image, ImageFilter

foto_p, tras_p, sal_p = sys.argv[1:4]
X0, Y0, X1, Y1 = map(int, sys.argv[4:8])
foto = Image.open(foto_p).convert('RGB')
reg = np.asarray(foto.crop((X0, Y0, X1, Y1))).astype(np.int16)
h, w = reg.shape[:2]

# 1) máscara de «cartón blanco» y componente que contiene el centro
blanco = (reg.min(2) > 185) & ((reg.max(2) - reg.min(2)) < 40)
vis = np.zeros_like(blanco); pila = [(h // 2, w // 2)]
# si el centro cae en un dibujo, busca un punto blanco cerca
if not blanco[h // 2, w // 2]:
    ys, xs = np.where(blanco[h // 2 - 40:h // 2 + 40, w // 2 - 40:w // 2 + 40]); pila = [(h // 2 - 40 + ys[0], w // 2 - 40 + xs[0])]
while pila:
    y, x = pila.pop()
    if y < 0 or x < 0 or y >= h or x >= w or vis[y, x] or not blanco[y, x]:
        continue
    vis[y, x] = True
    pila += [(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)]
# rellena huecos (dibujos y letras) por filas dentro del contorno
filas = np.where(vis.any(1))[0]
anchos = np.array([vis[y].sum() and (np.where(vis[y])[0][-1] - np.where(vis[y])[0][0]) for y in range(h)])
amax = np.percentile(anchos[filas], 90)
cuerpo = [y for y in filas if anchos[y] > amax * .93]          # filas del cuerpo (sin la pestaña)
y_top, y_bot = cuerpo[0], cuerpo[-1]


def borde(lado, ys):
    xs = [np.where(vis[y])[0][0 if lado == 'i' else -1] for y in ys]
    return np.polyfit(ys, xs, 1)                                  # x = a*y + b


tramo = [y for y in cuerpo if y_top + (y_bot - y_top) * .12 < y < y_top + (y_bot - y_top) * .88]
ai, bi = borde('i', tramo); ad, bd = borde('d', tramo)
# borde inferior: última fila blanca por columna
cols = range(int(ai * y_bot + bi) + 25, int(ad * y_bot + bd) - 25)
yb = [np.where(vis[:, x])[0][-1] for x in cols]
ab, bb = np.polyfit(list(cols), yb, 1)                             # y = a*x + b
y_cara = y_top + int((y_bot - y_top) * .035)                       # deja la solapa superior
TL = (ai * y_cara + bi, y_cara); TR = (ad * y_cara + bd, y_cara)
xl = (ai * bb + bi) / (1 - ai * ab); BL = (xl, ab * xl + bb)
xr = (ad * bb + bd) / (1 - ad * ab); BR = (xr, ab * xr + bb)
quad = [TL, TR, BR, BL]
print('esquinas', [(round(x + X0), round(y + Y0)) for x, y in quad])

# 2) cara trasera real, recompuesta a la proporción de la caja de la foto (sin deformar letras)
tras = Image.open(tras_p).convert('RGBA')
T = np.asarray(tras)
fil = np.where((T[..., 3] > 200).mean(1) > .9)[0]                  # filas a todo el ancho = cuerpo
cuerpo_t = tras.crop((0, fil[0], tras.width, fil[-1] + 1)).convert('RGB')
anc = ((TR[0] - TL[0]) + (BR[0] - BL[0])) / 2; alt = ((BL[1] - TL[1]) + (BR[1] - TR[1])) / 2
Wt = cuerpo_t.width; Ht = int(round(Wt * alt / anc))
papel = tuple(int(v) for v in np.median(np.asarray(cuerpo_t)[20:60, 300:460].reshape(-1, 3), 0))
plano = Image.new('RGB', (Wt, max(Ht, cuerpo_t.height)), papel)
corte = int(cuerpo_t.height * .50)                                 # entre la línea y el reciclaje
arr = np.asarray(cuerpo_t.convert('L'))
# busca una fila totalmente blanca cerca del corte
for d in range(0, 80):
    for c in (corte + d, corte - d):
        if arr[c, 40:-40].min() > 215:
            corte = c; break
    else:
        continue
    break
plano.paste(cuerpo_t.crop((0, 0, Wt, corte)), (0, 0))
resto = cuerpo_t.crop((0, corte, Wt, cuerpo_t.height))
hueco = plano.height - cuerpo_t.height
if hueco > 0:                                                      # rellena estirando una franja blanca real (sin costura)
    franja = cuerpo_t.crop((0, corte - 2, Wt, corte + 2)).resize((Wt, hueco + 4), Image.BILINEAR)
    plano.paste(franja, (0, corte - 2))
plano.paste(resto, (0, plano.height - resto.height))

# 3) perspectiva: plano -> quad
def coef(dst, src):
    A = []; B = []
    for (x, y), (u, v) in zip(dst, src):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]; B += [u, v]
    return np.linalg.solve(np.array(A, float), np.array(B, float))


src = [(0, 0), (plano.width, 0), (plano.width, plano.height), (0, plano.height)]
c = coef(quad, src)
warp = plano.transform((w, h), Image.PERSPECTIVE, c, Image.BICUBIC)
mq = Image.new('L', plano.size, 255).transform((w, h), Image.PERSPECTIVE, c, Image.BICUBIC)

# 4) luz: iguala el blanco del papel al de la caja de la foto (mapa suave)
reg8 = reg.astype(np.uint8)
lum = np.asarray(Image.fromarray(reg8).filter(ImageFilter.MaxFilter(31)).filter(ImageFilter.GaussianBlur(40))).astype(float)
gan = lum / np.array(papel, float)
W8 = np.clip(np.asarray(warp).astype(float) * gan, 0, 255)

# 5) máscara final: dentro del quad, sin piel (dedos por delante)
r, g, b = reg[..., 0], reg[..., 1], reg[..., 2]
piel = (r > 120) & (r - b > 28) & (r - g > 8) & (g > 60)
piel = np.asarray(Image.fromarray((piel * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.GaussianBlur(2))) / 255.
# los dedos solo pueden estar en el borde de la caja: en el interior no se respeta la «piel»
interior = np.asarray(mq.filter(ImageFilter.MinFilter(91))) / 255.
piel = piel * (1 - interior)
M = (np.asarray(mq) / 255.) * (1 - piel)
M = np.asarray(Image.fromarray((M * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))) / 255.
out = reg.astype(float) * (1 - M[..., None]) + W8 * M[..., None]
res = foto.copy(); res.paste(Image.fromarray(out.astype(np.uint8)), (X0, Y0)); res.save(sal_p)
print('ok', sal_p)
