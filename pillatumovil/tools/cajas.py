# Recorta la cara delantera de cada caja (cuerpo + pestana de colgar) y
# la compone sobre fondo blanco, sin la bolsa del fondo.
import sys, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

APROX = {  # x0, y0, x1, y1 del cuerpo de cada caja delantera (px del original)
 'v2-cargador-20w.png':   [(237,761,609,1191)],
 'v2-cable-lightning.jpg':[(600,877,908,1237)],
 'v2-cable-usbc.jpg':     [(604,845,907,1212)],
 'v2-pack-lightning.jpg': [(121,856,433,1234),(439,874,748,1234)],
 'v2-pack-usbc.jpg':      [(148,818,440,1185),(443,822,744,1185)],
}

def afinar(g, box, r=22):
    """Mueve cada borde a la linea de mas contraste en +-r px."""
    x0,y0,x1,y1 = box
    gx = np.abs(np.diff(g, axis=1)); gy = np.abs(np.diff(g, axis=0))
    ym0, ym1 = int(y0+(y1-y0)*.3), int(y0+(y1-y0)*.9)   # tramo vertical sin pestana
    xm0, xm1 = int(x0+(x1-x0)*.05), int(x0+(x1-x0)*.95)
    def col(x): return gx[ym0:ym1, x].mean()
    def fil(y, a, b): return gy[y, a:b].mean()
    nx0 = max(range(x0-r, x0+r), key=col)
    nx1 = max(range(x1-r, x1+r), key=col) + 1
    # arriba: el centro tiene la pestana encima, se mira solo en los laterales
    lat = lambda y: (fil(y, xm0, int(x0+(x1-x0)*.18)) + fil(y, int(x0+(x1-x0)*.82), xm1))/2
    ny0 = max(range(y0-r, y0+r), key=lat) + 1
    ny1 = max(range(y1-r, y1+r), key=lambda y: fil(y, xm0, xm1)) + 1
    return nx0, ny0, nx1, ny1

def mascara(size, cajas):
    m = Image.new('L', size, 0); d = ImageDraw.Draw(m)
    for x0,y0,x1,y1 in cajas:
        w = x1-x0
        d.rectangle([x0,y0,x1-1,y1-1], fill=255)
        tx0, tx1, th = x0+.197*w, x0+.803*w, .20*w
        d.rounded_rectangle([tx0, y0-th, tx1, y0+6], radius=.045*w, fill=255)
        # ranura de la pestana: se ve el fondo a traves
        sy0, sy1 = y0-th+.055*w, y0-th+.137*w
        d.rounded_rectangle([x0+.279*w, sy0, x0+.726*w, sy1], radius=(sy1-sy0)/2, fill=0)
    return m

if __name__ == '__main__':
    src, nombre, modo = sys.argv[1], sys.argv[2], sys.argv[3]
    im = Image.open(src).convert('RGB'); g = np.asarray(im.convert('L')).astype(float)
    cajas = [afinar(g, b) for b in APROX[nombre]]
    print(nombre, cajas)
    m = mascara(im.size, cajas)
    if modo == 'revisar':
        v = im.copy(); ov = Image.new('RGB', im.size, (255,0,0))
        v = Image.composite(v, Image.blend(v, ov, .35), m)
        x0 = min(c[0] for c in cajas)-80; x1 = max(c[2] for c in cajas)+80
        y0 = min(c[1]-int(.2*(c[2]-c[0])) for c in cajas)-60; y1 = max(c[3] for c in cajas)+60
        v.crop((x0,y0,x1,y1)).save(sys.argv[4])
    json.dump(cajas, open(sys.argv[4]+'.json' if modo=='revisar' else sys.argv[4], 'w'))
