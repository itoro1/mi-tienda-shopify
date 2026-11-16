"""La caja REAL en 3D: se puede pintar desde cualquier ángulo (los 360 grados).

16/11/2026. El dueño: «quiero que estudies los 360 grados que tiene la caja del cargador y la caja del
cable de las imágenes que te pasé […] y me pones el diseño tal cual, real, en 4K».

Cada caja es un prisma con sus medidas de verdad (fotos/caja3d/medidas.json) y:
  - delante y detrás: las caras sacadas de las fotos del dueño (tools/caja3d_texturas.py);
  - lados, tapa y base: cartón blanco liso, como en las fotos;
  - la pestaña de colgar: sale del canto de arriba de la cara de atrás, con las esquinas redondas y el
    ojal «euro» (ranura con un círculo en el centro), medida sobre la foto fotos/reales/cajas-frente-usb-c.jpg.

Ejes de la caja: x a la derecha, y hacia ABAJO, z hacia el fondo (alejándose de quien mira la cara de
delante). El origen está en el centro del borde de abajo de la cara de delante. Unidad: el ancho de la caja.
Uso desde otro script:
    caja = Caja('cargador', 'fotos/caja3d')
    rgb, alfa = caja.pinta(K, R, t, (ancho, alto))     # K cámara 3x3; Xcam = R·Xcaja + t
Prueba suelta:  python3 caja3d.py cargador SALIDA.png [giro_grados] [inclinación_grados]
"""
import json, os, sys
import cv2, numpy as np

PAPEL = 243.0


def _pestana(ancho_px, alto_px):
    """Pestaña de colgar: cartón blanco con el ojal euro. RGBA."""
    w, h = ancho_px, alto_px
    a = np.zeros((h, w), np.uint8); r = int(h * .30)
    cv2.rectangle(a, (0, r), (w - 1, h - 1), 255, -1); cv2.rectangle(a, (r, 0), (w - 1 - r, h - 1), 255, -1)
    cv2.circle(a, (r, r), r, 255, -1, cv2.LINE_AA); cv2.circle(a, (w - 1 - r, r), r, 255, -1, cv2.LINE_AA)
    # ojal: ranura de 0,75 del ancho de la pestaña y un círculo en el centro
    cy = int(h * .46); rh = int(h * .13); x0, x1 = int(w * .13), int(w * .87)
    cv2.rectangle(a, (x0 + rh, cy - rh), (x1 - rh, cy + rh), 0, -1)
    cv2.circle(a, (x0 + rh, cy), rh, 0, -1, cv2.LINE_AA); cv2.circle(a, (x1 - rh, cy), rh, 0, -1, cv2.LINE_AA)
    cv2.circle(a, (w // 2, cy), int(rh * 1.75), 0, -1, cv2.LINE_AA)
    rgb = np.full((h, w, 3), PAPEL - 3, np.float32)
    # canto del cartón: una línea apenas más oscura en el borde del recorte
    borde = cv2.GaussianBlur(a, (0, 0), 2.5).astype(np.float32) / 255
    rgb *= (0.90 + 0.10 * np.clip(borde * 1.6 - .3, 0, 1))[..., None]
    return np.dstack([rgb, a.astype(np.float32)])


def _liso(w, h, semilla):
    """Cartón blanco liso con un grano mínimo."""
    g = np.random.default_rng(semilla).normal(0, 1.0, (h // 4 + 1, w // 4 + 1)).astype(np.float32)
    g = cv2.resize(cv2.GaussianBlur(g, (0, 0), 1.5), (w, h))
    return np.clip(np.full((h, w, 3), PAPEL - 2, np.float32) + g[..., None] * 1.2, 0, 255)


def _canto(tex, px=5, fuerza=.07):
    """Oscurece un poco el filo de la cara: en una caja de verdad las aristas se marcan."""
    h, w = tex.shape[:2]; m = np.ones((h, w), np.float32)
    for i in range(px):
        k = 1 - fuerza * (1 - i / px)
        m[i, :] = np.minimum(m[i, :], k); m[h - 1 - i, :] = np.minimum(m[h - 1 - i, :], k)
        m[:, i] = np.minimum(m[:, i], k); m[:, w - 1 - i] = np.minimum(m[:, w - 1 - i], k)
    return tex * m[..., None]


class Caja:
    def __init__(self, nombre, carpeta, pestana=True):
        mm = json.load(open(os.path.join(carpeta, 'medidas.json')))['mm'][nombre]
        self.nombre = nombre; self.mm = mm
        self.W = 1.0; self.H = mm[1] / mm[0]; self.D = mm[2] / mm[0]
        lee = lambda n: cv2.cvtColor(cv2.imread(os.path.join(carpeta, f'{nombre}-{n}.png')), cv2.COLOR_BGR2RGB).astype(np.float32)
        px = 1600                                                  # píxeles por ancho de caja en las texturas
        self.tex = {'frente': _canto(lee('frente')), 'trasera': _canto(lee('trasera')),
                    'lado_d': _canto(_liso(int(px * self.D), int(px * self.H), 1)), 'lado_i': _canto(_liso(int(px * self.D), int(px * self.H), 2)),
                    'tapa': _canto(_liso(px, int(px * self.D), 3)), 'base': _canto(_liso(px, int(px * self.D), 4))}
        # pestaña, medida sobre fotos/reales/cajas-frente-usb-c.jpg: ocupa el 57 % del ancho en la caja del
        # cargador y el 54 % en la del cable, y sube un 20 % y un 22 % del ancho
        self.Wt, self.Ht = {'cargador': (0.57, 0.20), 'cable': (0.54, 0.22)}[nombre]
        self.pest = _pestana(int(px * self.Wt), int(px * self.Ht)) if pestana else None
        W, H, D = self.W, self.H, self.D; w2 = W / 2
        # caras: esquinas TL TR BR BL vistas desde fuera, y la normal hacia fuera
        self.caras = [
            ('frente',  [(-w2, -H, 0), (w2, -H, 0), (w2, 0, 0), (-w2, 0, 0)], (0, 0, -1)),
            ('trasera', [(w2, -H, D), (-w2, -H, D), (-w2, 0, D), (w2, 0, D)], (0, 0, 1)),
            ('lado_d',  [(w2, -H, 0), (w2, -H, D), (w2, 0, D), (w2, 0, 0)], (1, 0, 0)),
            ('lado_i',  [(-w2, -H, D), (-w2, -H, 0), (-w2, 0, 0), (-w2, 0, D)], (-1, 0, 0)),
            ('tapa',    [(-w2, -H, D), (w2, -H, D), (w2, -H, 0), (-w2, -H, 0)], (0, -1, 0)),
            ('base',    [(-w2, 0, 0), (w2, 0, 0), (w2, 0, D), (-w2, 0, D)], (0, 1, 0)),
        ]
        t2 = self.Wt / 2
        self.q_pest = [(-t2, -H - self.Ht, D), (t2, -H - self.Ht, D), (t2, -H, D), (-t2, -H, D)]

    def pinta(self, K, R, t, wh, luz=(-0.30, -0.55, -0.78), amb=0.80, dif=0.25, ss=2):
        """Devuelve (rgb premultiplicado, alfa) en float32, tamaño wh=(ancho, alto)."""
        w, h = wh[0] * ss, wh[1] * ss
        Ks = K.copy().astype(np.float64); Ks[:2] *= ss
        R = np.asarray(R, np.float64); t = np.asarray(t, np.float64).reshape(3)
        L = np.array(luz, np.float64); L /= np.linalg.norm(L)
        lienzo = np.zeros((h, w, 4), np.float32)

        def proy(q):
            X = (R @ np.array(q, np.float64).T).T + t
            uv = (Ks @ X.T).T
            return uv[:, :2] / uv[:, 2:3], X

        piezas = []
        for nombre, q, n in self.caras:
            uv, X = proy(q); nc = R @ np.array(n, np.float64)
            if np.dot(nc, X.mean(0)) >= 0: continue                          # de espaldas a la cámara
            piezas.append((X.mean(0)[2], self.tex[nombre], None, uv, amb + dif * max(0.0, float(np.dot(nc, L)))))
        if self.pest is not None:
            uv, X = proy(self.q_pest); nc = R @ np.array((0, 0, 1.0))
            if np.dot(nc, X.mean(0)) >= 0: nc = -nc
            piezas.append((X.mean(0)[2] + 1e-3, self.pest[..., :3], self.pest[..., 3], uv, amb + dif * max(0.0, float(np.dot(nc, L)))))
        for _, tex, alfa, uv, brillo in sorted(piezas, key=lambda p: -p[0]):   # de lejos a cerca
            th, tw = tex.shape[:2]
            lado = max(np.linalg.norm(uv[1] - uv[0]), np.linalg.norm(uv[2] - uv[3]), np.linalg.norm(uv[3] - uv[0]) * tw / th)
            e = min(1.0, max(lado * 1.15 / tw, 0.02))                          # textura al tamaño que va a ocupar
            if e < 1:
                tex = cv2.resize(tex, (max(int(tw * e), 2), max(int(th * e), 2)), interpolation=cv2.INTER_AREA)
                if alfa is not None: alfa = cv2.resize(alfa, (tex.shape[1], tex.shape[0]), interpolation=cv2.INTER_AREA)
            th, tw = tex.shape[:2]
            a = (np.full((th, tw), 255, np.float32) if alfa is None else alfa) / 255
            src = np.dstack([tex * a[..., None], a])
            Hm = cv2.getPerspectiveTransform(np.float32([[0, 0], [tw, 0], [tw, th], [0, th]]), np.float32(uv))
            x0, y0 = np.floor(uv.min(0)).astype(int) - 2; x1, y1 = np.ceil(uv.max(0)).astype(int) + 3
            x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, w), min(y1, h)
            if x1 <= x0 or y1 <= y0: continue
            T = np.array([[1, 0, -x0], [0, 1, -y0], [0, 0, 1.0]])
            cara = cv2.warpPerspective(src, T @ Hm, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
            cara[..., :3] *= brillo
            z = lienzo[y0:y1, x0:x1]
            lienzo[y0:y1, x0:x1] = cara + z * (1 - cara[..., 3:])
        if ss > 1: lienzo = cv2.resize(lienzo, wh, interpolation=cv2.INTER_AREA)
        return lienzo[..., :3], lienzo[..., 3:]


def giro_y(g):
    c, s = np.cos(g), np.sin(g); return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def giro_x(g):
    c, s = np.cos(g), np.sin(g); return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def giro_z(g):
    c, s = np.cos(g), np.sin(g); return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def pose_giro(caja, guinada, cabeceo=0.0, balanceo=0.0):
    """Rotación y desplazamiento para girar la caja sobre su eje vertical central (guiñada), en ejes de caja.
    Devuelve (R, c): Xgirado = R·(X − c) + c, con c en el centro de la base."""
    c = np.array([0, 0, caja.D / 2]); R = giro_z(balanceo) @ giro_x(cabeceo) @ giro_y(guinada)
    return R, c


if __name__ == '__main__':
    nombre, sal = sys.argv[1:3]
    g = np.radians(float(sys.argv[3])) if len(sys.argv) > 3 else 0.6
    inc = np.radians(float(sys.argv[4])) if len(sys.argv) > 4 else -0.15
    aqui = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'fotos', 'caja3d')
    caja = Caja(nombre, aqui); W, H = 1400, 1600
    K = np.array([[2600, 0, W / 2], [0, 2600, H / 2], [0, 0, 1.0]])
    R, c = pose_giro(caja, g, inc)
    t = R @ (-c) + c + np.array([0, caja.H / 2 + .05, 3.2])
    rgb, a = caja.pinta(K, R, t, (W, H))
    fondo = np.full((H, W, 3), (60, 64, 74), np.float32)
    cv2.imwrite(sal, cv2.cvtColor(np.clip(rgb + fondo * (1 - a), 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR))
    print('ok', sal)
