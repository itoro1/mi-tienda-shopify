"""Sigue la flecha verde del precinto en los fotogramas del plano «precinto» para que el montaje dibuje un anillo encima.

Uso: python3 peli_anillo.py CARPETA_PLANO PRIMER_FOTOGRAMA_GLOBAL SALIDA.json
  CARPETA_PLANO: los PNG 0001.png ... del plano (720x1280).
  PRIMER_FOTOGRAMA_GLOBAL: índice (desde 0) que tiene 0001.png en la película entera (precinto: 74).
Sale {fotograma_global: [x, y, radio]} en coordenadas de 1080x1920.
"""
import glob, json, os, sys
import numpy as np
from PIL import Image

CARP, PRIMERO, SAL = sys.argv[1], int(sys.argv[2]), sys.argv[3]
pista = {}
for i, f in enumerate(sorted(glob.glob(os.path.join(CARP, '[0-9]*.png')))):
    a = np.asarray(Image.open(f).convert('RGB')).astype(np.int16); r, g, b = a[..., 0], a[..., 1], a[..., 2]
    verde = (g > 110) & (g - r > 25) & (g - b > 60)               # el círculo verde de la flecha
    ys, xs = np.nonzero(verde)
    if len(xs) < 30: continue
    e = 1080 / a.shape[1]
    pista[PRIMERO + i] = [round(float(xs.mean()) * e, 1), round(float(ys.mean()) * e, 1), round(float(np.sqrt(len(xs) / np.pi)) * e, 1)]
json.dump(pista, open(SAL, 'w'))
print('ok', len(pista), 'fotogramas con la flecha')
