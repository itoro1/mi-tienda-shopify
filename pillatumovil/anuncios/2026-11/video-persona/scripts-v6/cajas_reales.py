"""Cajas del mostrador con la forma REAL (planos 1 y 4, 4K) - experimento R3.

Idea: las cajas de la IA son demasiado altas (ancho/alto ~0,72) y con pestañas enormes. Las de verdad son
casi cuadradas (cargador 79 x 85,6 mm, cable 67 x 65 mm). Para no tener que inventar lo que hay detrás de
ellas (camiseta, brazos, su mano señalando), cada caja nueva conserva el ANCHO y la LÍNEA DE ARRIBA de la
pestaña de la caja de la IA, y lo que cambia es dónde apoya: está algo más atrás en el mostrador, así que
su base queda más arriba. Lo único que hay que rellenar es madera del mostrador (estática, se mueve solo con la
cámara) y unas tiras finas al lado de la pestaña (la real es más estrecha).

Por fotograma y por caja:
  1. Tiras sobrantes de la silueta vieja (bordes, esquinas de la pestaña, ojal): se rellenan con el reflejo
     del fondo que hay justo al otro lado del borde (espejo a través del borde, en coordenadas de la caja).
  2. Franja del mostrador entre la base nueva y la vieja: textura de mostrador abierto (a la derecha de la
     última caja, mismas filas = misma perspectiva), con la luz baja ajustada a los bordes (membrana) y la
     sombra de contacto medida en las cajas de la IA. Fija sobre el mostrador: se mueve con la cámara.
  3. La caja: cara de delante de la foto real del dueño (fotos/caja3d, como en sus manos), tapa y pestaña con
     el ojal euro; luz = la del cartón de la caja de la IA en ese sitio (ajuste suave por fotograma).
Coordenadas: las de la caja en el fotograma de referencia (0); el paso a cada fotograma es la afín del
seguimiento de ../mostrador (seg*.json), suavizada (homografía común + desvío de cada caja filtrado).

Uso:
  python3 cajas_reales.py PLANO(1|4) ENTRADA.mp4 SALIDA.mp4 [--base mostrador|k4] [--prueba 0,40,116]
    --base k4: ENTRADA es k4/N.mp4 y se aplica antes lo de ../mostrador/componer.py (texto, ventana, neón),
               así la cara pasa por una sola codificación, como en mostrador/N.mp4.
"""
import sys, os, json, numpy as np, cv2
AQUI = os.path.dirname(os.path.abspath(__file__))
MOST = os.path.join(AQUI, '..', 'mostrador')
sys.path.insert(0, MOST)
from comun import lector, escritor, W, H   # noqa: E402

REPO = '/home/user/mi-tienda-shopify/pillatumovil'
TEX = {'cargador': REPO + '/fotos/caja3d/cargador-frente.png', 'cable': REPO + '/fotos/caja3d/cable-frente.png',
       'lightning': AQUI + '/tex/lightning-frente.png'}
PROP = {'cargador': 0.923, 'cable': 1.03, 'lightning': 0.976}          # ancho/alto de la cara (medido)
PEST = {'cargador': (0.57, 0.20), 'cable': (0.54, 0.22), 'lightning': (0.54, 0.20)}   # pestaña: ancho, alto / ancho caja
FONDO = {'cargador': 33 / 79, 'cable': 24 / 67, 'lightning': 24 / 69}  # fondo / ancho
SS = 2                      # supermuestreo del dibujo de la caja
# cara de lado que se ve en las cajas de los extremos (medida en las de la IA, px 4K): (lado, ancho)
LADO = {'1': {0: ('R', 8.0), 3: ('L', 16.0)}, '4': {0: ('R', 5.0), 3: ('L', 15.0)}}
DIL = 7                     # px de margen alrededor de la silueta vieja (bordes con halo de la IA)


def yuv2rgb(Y, U, V):
    y = Y.astype(np.float32) - 16; u = U.astype(np.float32) - 128; v = V.astype(np.float32) - 128
    return np.dstack([1.164384 * y + 1.792741 * v, 1.164384 * y - 0.213249 * u - 0.532909 * v, 1.164384 * y + 2.112402 * u])


def rgb2yuv(rgb):
    R, G, B = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    return (16 + 0.182586 * R + 0.614231 * G + 0.062007 * B, 128 - 0.100644 * R - 0.338572 * G + 0.439216 * B,
            128 + 0.439216 * R - 0.398942 * G - 0.040274 * B)


def rrect(mask_shape, x0, y0, x1, y1, r, val=1.0, sc=1.0, off=(0, 0)):
    """Rectángulo de esquinas redondeadas ARRIBA (la pestaña), en coordenadas ref*sc - off."""
    m = np.zeros(mask_shape, np.float32)
    X0, Y0, X1, Y1, R = [(v - o) * sc for v, o in zip((x0, y0, x1, y1), (off[0], off[1], off[0], off[1]))] + [r * sc]
    sh = 4
    p = lambda v: int(round(v * (1 << sh)))
    cv2.rectangle(m, (p(X0 + R), p(Y0)), (p(X1 - R), p(Y1)), val, -1, cv2.LINE_AA, sh)
    cv2.rectangle(m, (p(X0), p(Y0 + R)), (p(X1), p(Y1)), val, -1, cv2.LINE_AA, sh)
    cv2.circle(m, (p(X0 + R), p(Y0 + R)), p(R), val, -1, cv2.LINE_AA, sh)
    cv2.circle(m, (p(X1 - R), p(Y0 + R)), p(R), val, -1, cv2.LINE_AA, sh)
    return m


def ojal(mask, cx, cy, wt, ht, sc, off):
    """Ojal euro (como tools/caja3d.py): ranura de 0,74 del ancho de la pestaña y círculo en el centro."""
    rh = 0.13 * ht; x0, x1 = cx - 0.37 * wt, cx + 0.37 * wt; rc = 1.75 * rh
    sh = 4; p = lambda v: int(round(v * (1 << sh)))
    T = lambda x, y: (p((x - off[0]) * sc), p((y - off[1]) * sc))
    cv2.rectangle(mask, T(x0 + rh, cy - rh), T(x1 - rh, cy + rh), 0, -1, cv2.LINE_AA, sh)
    cv2.circle(mask, T(x0 + rh, cy), p(rh * sc), 0, -1, cv2.LINE_AA, sh)
    cv2.circle(mask, T(x1 - rh, cy), p(rh * sc), 0, -1, cv2.LINE_AA, sh)
    cv2.circle(mask, T(cx, cy), p(rc * sc), 0, -1, cv2.LINE_AA, sh)
    return mask


def poli(shape, pts, sc, off):
    m = np.zeros(shape, np.float32); sh = 4
    q = np.array([[int(round((x - off[0]) * sc * (1 << sh))), int(round((y - off[1]) * sc * (1 << sh)))] for x, y in pts], np.int32)
    cv2.fillPoly(m, [q], 1.0, cv2.LINE_AA, sh)
    return m


def canto(tex, px, fuerza):
    h, w = tex.shape[:2]; m = np.ones((h, w), np.float32)
    for i in range(px):
        k = 1 - fuerza * (1 - i / px)
        m[i, :] = np.minimum(m[i, :], k); m[h - 1 - i, :] = np.minimum(m[h - 1 - i, :], k)
        m[:, i] = np.minimum(m[:, i], k); m[:, w - 1 - i] = np.minimum(m[:, w - 1 - i], k)
    return tex * m[..., None]


def ajuste_poly(P, msk, xs, ys, grado=2, xq=None, yq=None):
    """Ajuste polinómico robusto por canal de P (N,3) en (xs, ys); evalúa en (xq, yq)."""
    cx, cy, s = xs.mean(), ys.mean(), max(xs.std(), ys.std(), 1)
    base = lambda x, y: np.stack([((x - cx) / s) ** i * ((y - cy) / s) ** j for i in range(grado + 1) for j in range(grado + 1 - i)], -1)
    A = base(xs[msk], ys[msk]); out = []
    Bq = base(xq, yq)
    for c in range(3):
        b = P[msk, c]; co, *_ = np.linalg.lstsq(A, b, rcond=None)
        r = b - A @ co; ok = np.abs(r) < 2.5 * (r.std() + 1e-3)
        co, *_ = np.linalg.lstsq(A[ok], b[ok], rcond=None)
        out.append(Bq @ co)
    return np.stack(out, -1).astype(np.float32)


# ---------------------------------------------------------------- seguimiento suavizado
def afines(seg, geo, n):
    """Afines ref->t por caja: homografía común de las 4 cajas + desvío propio de cada caja suavizado (sigma 3)."""
    refc = [np.array([[b['x0'], b['ybot']], [b['x1'], b['ybot']], [b['x1'], b['tab_top']], [b['x0'], b['tab_top']]], np.float64) for b in geo]
    P = np.zeros((n, len(geo), 4, 2)); G = []
    for t in range(n):
        for k, b in enumerate(geo):
            M = np.array(seg['M'][f'caja{b["i"]}'][t])
            P[t, k] = refc[k] @ M[:, :2].T + M[:, 2]
        Hm, _ = cv2.findHomography(np.concatenate(refc).astype(np.float32), P[t].reshape(-1, 2).astype(np.float32), 0)
        G.append(Hm)
    Q = np.zeros_like(P)
    for t in range(n):
        for k in range(len(geo)):
            Q[t, k] = cv2.perspectiveTransform(refc[k][None].astype(np.float64), G[t])[0]
    r = P - Q
    k1 = np.exp(-0.5 * (np.arange(-9, 10) / 3.0) ** 2); k1 /= k1.sum()
    rs = np.empty_like(r)
    for k in range(len(geo)):
        for c in range(4):
            for d in range(2):
                x = np.pad(r[:, k, c, d], 9, mode='reflect'); rs[:, k, c, d] = np.convolve(x, k1, 'same')[9:-9]
    C = Q + rs
    A = np.zeros((n, len(geo), 2, 3))
    for t in range(n):
        for k in range(len(geo)):
            src = np.hstack([refc[k], np.ones((4, 1))]); sol, *_ = np.linalg.lstsq(src, C[t, k], rcond=None)
            A[t, k] = sol.T
    return A


# ---------------------------------------------------------------- preparación en el fotograma de referencia
class Plano:
    def __init__(self, plano, ref_rgb):
        self.plano = plano
        self.geo = json.load(open(f'{AQUI}/geo{plano}.json'))
        self.seg = json.load(open(f'{MOST}/seg{plano}.json'))
        self.n = self.seg['n']
        self.A = afines(self.seg, self.geo, self.n)
        self.ref = ref_rgb
        lid_ai = 20.0 if plano == '1' else 18.0
        self.cajas = []
        for b in self.geo:
            self.cajas.append(self.prepara_caja(b, lid_ai))
        self.prepara_franja()

    # -- silueta vieja (paramétrica) y nueva caja
    def prepara_caja(self, b, lid_ai):
        t = b['tipo']; Wd = b['x1'] - b['x0']; x0, x1 = b['x0'], b['x1']
        c = {'b': b, 'tipo': t, 'W': Wd}
        # pestaña vieja: ancho medido justo encima del hombro; esquinas redondas ~0,4 del alto
        th_old = b['hombro'] - b['tab_top']
        c['old'] = dict(tab_x0=b['tab_x0'], tab_x1=b['tab_x1'], tab_top=b['tab_top'], r=0.42 * th_old)
        # nueva
        wt, ht = PEST[t][0] * Wd, PEST[t][1] * Wd
        lid = lid_ai * (FONDO[t] / (33 / 79)) * 0.9
        cx_old = (b['tab_x0'] + b['tab_x1']) / 2; cxb = (x0 + x1) / 2
        cx = cxb + np.clip(cx_old - cxb, -0.03 * Wd, 0.03 * Wd)
        ttop = b['tab_top']
        ybt = ttop + ht; yft = ybt + lid; yb = yft + Wd / PROP[t]
        c.update(wt=wt, ht=ht, lid=lid, cx=cx, ttop=ttop, ybt=ybt, yft=yft, yb=yb)
        lado, sw_old = LADO[self.plano].get(b['i'], ('R', 0.0))
        c['lado'] = lado; c['sw_old'] = sw_old; c['sw'] = sw_old * FONDO[t] / (33 / 79)
        # lienzo de la caja nueva (ref * SS)
        m = 10 + int(np.ceil(max(sw_old, c['sw'])))
        c['off'] = (x0 - m, ttop - m)
        cw, ch = int(np.ceil((Wd + 2 * m) * SS)), int(np.ceil((yb - ttop + 2 * m) * SS))
        c['lienzo'] = (cw, ch)
        self.dibuja_caja(c)
        return c

    def mascara_vieja(self, c, shape, off, sc=1.0):
        b = c['b']; o = c['old']
        m = np.zeros(shape, np.float32)
        X = lambda v: (v - off[0]) * sc; Y = lambda v: (v - off[1]) * sc
        ex0 = b['x0'] - (c['sw_old'] if c['lado'] == 'L' else 0); ex1 = b['x1'] + (c['sw_old'] if c['lado'] == 'R' else 0)
        cv2.rectangle(m, (int(X(ex0)), int(Y(b['hombro']))), (int(np.ceil(X(ex1))), int(np.ceil(Y(b['ybot'])))), 1, -1)
        m = np.maximum(m, rrect(shape, o['tab_x0'], o['tab_top'], o['tab_x1'], b['hombro'] + 2, o['r'], sc=sc, off=off))
        # ojal viejo: hueco medido en la silueta segmentada
        s = np.load(f'{AQUI}/geo{self.plano}_sil{b["i"]}.npy'); X0, Y0, _, _ = b['zona']
        tx0, tx1 = int(o['tab_x0']) - X0, int(o['tab_x1']) - X0; ty0, ty1 = int(o['tab_top']) - Y0, int(b['hombro']) - Y0
        sub = 1 - s[ty0:ty1, tx0:tx1]
        n, lab, st, _ = cv2.connectedComponentsWithStats(sub.astype(np.uint8), 4)
        best = None
        for k in range(1, n):
            x, y, w, h, a = st[k]
            if x > 0 and y > 0 and x + w < sub.shape[1] and y + h < sub.shape[0] and a > 200 and (best is None or a > st[best][4]):
                best = k
        if best is not None:
            x, y, w, h, a = st[best]
            # ojal viejo como rectángulo redondeado de la caja englobante (la segmentación tiene huecos)
            sl = np.zeros(shape, np.float32)
            gx0, gy0 = tx0 + X0 + x, ty0 + Y0 + y
            rr = h / 2
            sh = 4; p = lambda v: int(round(v * (1 << sh)))
            cv2.rectangle(sl, (p(X(gx0 + rr)), p(Y(gy0))), (p(X(gx0 + w - rr)), p(Y(gy0 + h))), 1, -1, cv2.LINE_AA, sh)
            cv2.circle(sl, (p(X(gx0 + rr)), p(Y(gy0 + rr))), p(rr * sc), 1, -1, cv2.LINE_AA, sh)
            cv2.circle(sl, (p(X(gx0 + w - rr)), p(Y(gy0 + rr))), p(rr * sc), 1, -1, cv2.LINE_AA, sh)
            sl = cv2.erode(sl, np.ones((3, 3), np.uint8))       # el ojal visto un poco más pequeño: margen
            m = m * (1 - sl)
            c['ojal_viejo'] = (gx0, gy0, w, h)
        return m

    def dibuja_caja(self, c):
        b = c['b']; t = c['tipo']; cw, ch = c['lienzo']; off = c['off']; ref = self.ref
        x0, x1 = b['x0'], b['x1']
        yy, xx = np.mgrid[0:ch, 0:cw].astype(np.float32)
        u = xx / SS + off[0]; v = yy / SS + off[1]                      # coords ref de cada píxel del lienzo
        # --- luz de la caja vieja: cartón de la cara (papel claro), tapa y pestaña
        X0, Y0, X1, Y1 = int(x0) + 8, int(b['hombro']) + 26, int(x1) - 8, int(b['ybot']) - 8
        P = ref[Y0:Y1, X0:X1].reshape(-1, 3)
        gy, gx = np.mgrid[Y0:Y1, X0:X1]; gy = gy.ravel().astype(np.float64); gx = gx.ravel().astype(np.float64)
        lum = P.mean(1); loc = cv2.dilate(ref[Y0:Y1, X0:X1].mean(2), np.ones((41, 41), np.uint8)).ravel()
        sat = P.max(1) - P.min(1)
        papel = (lum > loc - 7) & (lum > np.percentile(lum, 30))
        luz = ajuste_poly(P, papel, gx, gy, 2, u.ravel().astype(np.float64), v.ravel().astype(np.float64)).reshape(ch, cw, 3)
        c['papel_ref'] = P[papel].mean(0)
        # --- cara de delante
        tex = cv2.cvtColor(cv2.imread(TEX[t]), cv2.COLOR_BGR2RGB).astype(np.float32)
        mg = int(0.006 * tex.shape[1]); tex = tex[mg:-mg, mg:-mg]
        tex = canto(tex, 14, 0.07)
        fw, fh = (x1 - x0) * SS, (c['yb'] - c['yft']) * SS
        # a la medida exacta (subpíxel) con una afín desde la textura
        Mt = np.array([[fw / tex.shape[1], 0, (x0 - off[0]) * SS], [0, fh / tex.shape[0], (c['yft'] - off[1]) * SS]], np.float64)
        pre = cv2.resize(tex, (int(round(fw)), int(round(fh))), interpolation=cv2.INTER_AREA)
        Mp = np.array([[fw / pre.shape[1], 0, Mt[0, 2]], [0, fh / pre.shape[0], Mt[1, 2]]])
        frente = cv2.warpAffine(pre, Mp, (cw, ch), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        a_fr = np.zeros((ch, cw), np.float32)
        sh = 4; p = lambda q: int(round(q * (1 << sh)))
        cv2.rectangle(a_fr, (p((x0 - off[0]) * SS), p((c['yft'] - off[1]) * SS)), (p((x1 - off[0]) * SS), p((c['yb'] - off[1]) * SS)), 1, -1, cv2.LINE_AA, sh)
        alb = np.clip(frente / 243.0, 0, 1.06)
        rgb_fr = alb * luz
        # --- tapa: perfil vertical de la tapa vieja (columnas de los hombros)
        hb = int(round(b['hombro'])); cols = np.r_[int(x0) + 10:int(b['tab_x0']) - 8, int(b['tab_x1']) + 8:int(x1) - 10]
        prof = ref[hb + 1:hb + 22, cols].mean(1)                           # (21,3) de atrás a delante
        sw = c['sw']; dx_b = sw if c['lado'] == 'R' else -sw
        a_lid = poli((ch, cw), [(x0, c['yft'] + 0.5), (x1, c['yft'] + 0.5), (x1 + dx_b, c['ybt']), (x0 + dx_b, c['ybt'])], SS, off)
        s_lid = np.clip((v - c['ybt']) / max(c['lid'], 1), 0, 1)
        idx = s_lid * (len(prof) - 1); i0 = np.floor(idx).astype(int); fr_ = idx - i0; i1 = np.minimum(i0 + 1, len(prof) - 1)
        rgb_lid = prof[i0] * (1 - fr_[..., None]) + prof[i1] * fr_[..., None]
        # variación horizontal como la de la cara en su borde de arriba
        top_row = luz[min(ch - 1, int((c['yft'] - off[1]) * SS) + 2)]
        rgb_lid = rgb_lid * (top_row / top_row.mean(0))[None]
        # --- pestaña: color del cartón de la pestaña vieja (fuera del ojal), ajuste lineal
        o = c['old']
        mo = self.mascara_vieja(c, ref.shape[:2], (0, 0))
        ty0, ty1 = int(o['tab_top']) + 4, int(b['hombro']) - 4; tx0, tx1 = int(o['tab_x0']) + 4, int(o['tab_x1']) - 4
        Pt = ref[ty0:ty1, tx0:tx1].reshape(-1, 3); mt = cv2.erode(mo, np.ones((7, 7), np.uint8))[ty0:ty1, tx0:tx1].ravel() > 0.5
        lt = Pt.mean(1); st_ = Pt.max(1) - Pt.min(1); mt &= (lt > 150) & (st_ < 45)
        mt &= lt > np.percentile(lt[mt], 25) if mt.any() else mt
        gy2, gx2 = np.mgrid[ty0:ty1, tx0:tx1]
        luz_t = ajuste_poly(Pt, mt, gx2.ravel().astype(np.float64), gy2.ravel().astype(np.float64), 1, u.ravel().astype(np.float64), v.ravel().astype(np.float64)).reshape(ch, cw, 3)
        a_tab = rrect((ch, cw), c['cx'] - c['wt'] / 2, c['ttop'], c['cx'] + c['wt'] / 2, c['ybt'] + 2, 0.30 * c['ht'], sc=SS, off=off)
        a_tab = ojal(a_tab, c['cx'], c['ttop'] + 0.46 * c['ht'], c['wt'], c['ht'], SS, off)
        borde = cv2.GaussianBlur(a_tab, (0, 0), 1.2 * SS)
        rgb_tab = luz_t * (0.92 + 0.08 * np.clip(borde * 1.6 - .3, 0, 1))[..., None]
        # --- cara de lado (cajas de los extremos): perfil de color de la de la IA, de la arista de delante a la de atrás
        a_sd = np.zeros((ch, cw), np.float32); rgb_sd = np.zeros((ch, cw, 3), np.float32)
        if sw > 0.5:
            so = c['sw_old']; H_ = b['ybot'] - b['hombro']; r0, r1 = int(b['hombro'] + 0.12 * H_), int(b['hombro'] + 0.45 * H_)
            if c['lado'] == 'R':
                xe = x1; cols_s = np.arange(int(round(x1)) + 1, int(round(x1 + so)))
                a_sd = poli((ch, cw), [(x1 - 0.5, c['yft']), (x1 + sw, c['ybt']), (x1 + sw, c['yb'] - c['lid']), (x1 - 0.5, c['yb'])], SS, off)
            else:
                xe = x0; cols_s = np.arange(int(round(x0)) - 1, int(round(x0 - so)), -1)
                a_sd = poli((ch, cw), [(x0 + 0.5, c['yft']), (x0 - sw, c['ybt']), (x0 - sw, c['yb'] - c['lid']), (x0 + 0.5, c['yb'])], SS, off)
            ps = ref[r0:r1][:, cols_s].mean(0)                                  # (n,3) de delante a atrás
            ss_ = np.clip(np.abs(u - xe) / max(sw, 1), 0, 1) * (len(ps) - 1)
            j0 = np.floor(ss_).astype(int); jf = ss_ - j0; j1 = np.minimum(j0 + 1, len(ps) - 1)
            rgb_sd = ps[j0] * (1 - jf[..., None]) + ps[j1] * jf[..., None]
            ce = int(np.clip((xe - off[0]) * SS, 0, cw - 1))
            ref_l = luz[int((r0 - off[1]) * SS):int((r1 - off[1]) * SS), ce].mean(0)
            rgb_sd = rgb_sd * (luz[:, ce] / ref_l)[:, None, :]
        # --- composición (de atrás a delante: pestaña, tapa, lado, cara)
        rgb = rgb_tab * a_tab[..., None]; a = a_tab.copy()
        rgb = rgb_lid * a_lid[..., None] + rgb * (1 - a_lid[..., None]); a = a_lid + a * (1 - a_lid)
        rgb = rgb_sd * a_sd[..., None] + rgb * (1 - a_sd[..., None]); a = a_sd + a * (1 - a_sd)
        rgb = rgb_fr * a_fr[..., None] + rgb * (1 - a_fr[..., None]); a = a_fr + a * (1 - a_fr)
        # arista de arriba de la cara: línea de luz fina como la de la caja vieja
        c['rgb'] = rgb.astype(np.float32); c['a'] = a.astype(np.float32)
        # silueta vieja (ref, tamaño completo, recortada luego) y lo que queda por rellenar
        c['vieja'] = mo

    # -- franja del mostrador y relleno de las tiras sobrantes
    def prepara_franja(self):
        ref = self.ref; geo = self.geo; cs = self.cajas
        hgt, wid = ref.shape[:2]
        # línea de arriba de la franja (base nueva) y de abajo (base vieja + margen) por columna
        xs = np.arange(wid, dtype=np.float32)
        cx = [(c['b']['x0'] + c['b']['x1']) / 2 for c in cs]
        top = np.interp(xs, [c['b']['x0'] for c in cs] + [c['b']['x1'] for c in cs],
                        [c['yb'] for c in cs] + [c['yb'] for c in cs])
        orden = np.argsort([c['b']['x0'] for c in cs])
        kx, ky = [], []
        for k in orden:
            kx += [cs[k]['b']['x0'], cs[k]['b']['x1']]; ky += [cs[k]['yb'], cs[k]['yb']]
        top = np.interp(xs, kx, ky)
        kb = []
        for k in orden:
            kb += [cs[k]['b']['ybot'], cs[k]['b']['ybot']]
        bot = np.interp(xs, kx, kb) + 40
        xl = cs[orden[0]]['b']['x0'] - 1; xr = cs[orden[-1]]['b']['x1'] + 14
        self.franja_x = (xl, xr)
        Y0 = int(np.floor(top[int(xl):int(xr)].min())) - 30; Y1 = int(np.ceil(bot[int(xl):int(xr)].max())) + 40
        X0, X1 = int(np.floor(xl)) - 4, int(np.ceil(xr)) + 4
        self.fr_off = (X0, Y0)
        h, w = Y1 - Y0, X1 - X0
        yy, xx = np.mgrid[Y0:Y1, X0:X1].astype(np.float32)
        T = top[X0:X1][None]; B = bot[X0:X1][None]
        dentro = (yy >= T - 0.5) & (yy <= B) & (xx >= xl) & (xx <= xr)
        # alfa: suave abajo (contra el mostrador original), a los lados y, en los huecos entre cajas, arriba
        en_caja = np.zeros(w, bool)
        for c in cs:
            e0 = c['b']['x0'] - (c['sw'] if c['lado'] == 'L' else 0)
            e1 = c['b']['x1'] + (c['sw'] if c['lado'] == 'R' else 0)
            en_caja[max(0, int(np.floor(e0)) - X0):max(0, int(np.ceil(e1)) - X0)] = True
        d_bot = B - yy; d_l = xx - xl; d_r = xr - xx; d_t = yy - T
        sm = lambda z: np.clip(z, 0, 1) ** 2 * (3 - 2 * np.clip(z, 0, 1))
        al = sm(d_bot / 18) * sm((d_l + 2) / 3) * sm(d_r / 10)
        rampa_t = np.where(en_caja[None], sm((d_t + 2) / 3), sm(d_t / 26))
        al = al * rampa_t * (yy >= T - 2) * (yy <= B)
        # textura: el mostrador de delante de las cajas, en espejo vertical respecto a la línea de abajo de la
        # franja (continuo en horizontal y en el borde de abajo; la luz baja se pone luego)
        Bc = np.repeat(B, h, 0)
        sy = (2 * Bc - yy).astype(np.float32); sx = xx.astype(np.float32)
        tex = cv2.remap(ref, sx, sy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        # luz baja: membrana con los bordes (mostrador original de abajo, lados y huecos entre cajas)
        q = 4
        orig = ref[Y0:Y1, X0:X1]
        lo = lambda im: cv2.resize(im, (w // q, h // q), interpolation=cv2.INTER_AREA)
        sig = 18.0
        ltex = cv2.GaussianBlur(tex, (0, 0), sig)
        borde_ok = (~dentro) & (yy > T + 6) & (xx > xl) & (xx < xr + 40)        # alrededor, por debajo de la base nueva
        # en los huecos entre cajas, a la altura de la franja: NO (ahí había sombra entre cajas que ya no está)
        hueco = (~en_caja[None]) & (yy < B - 4) & (xx > xl) & (xx < xr)
        borde_ok &= ~hueco
        izq = (xx >= xl - 10) & (xx < xl - 2) & (yy > T + 6) & (yy < B + 40) & (orig.mean(2) > 70)
        borde_ok |= izq
        D = lo(cv2.GaussianBlur(orig, (0, 0), 3))
        known = lo(borde_ok.astype(np.float32)) > 0.99
        sol = D.copy(); sol[~known] = D[known].mean(0)
        for it in range(2500):
            avg = (np.roll(sol, 1, 0) + np.roll(sol, -1, 0) + np.roll(sol, 1, 1) + np.roll(sol, -1, 1)) / 4
            sol = np.where(known[..., None], D, avg)
        lowt = cv2.resize(sol, (w, h), interpolation=cv2.INTER_CUBIC)
        lowt = cv2.GaussianBlur(lowt, (0, 0), 6)
        fill = tex - ltex + lowt
        # sombra de contacto y oclusión bajo cada caja nueva (perfil medido bajo las cajas de la IA)
        perfil = self.perfil_contacto()
        for c in cs:
            x0, x1, yb = c['b']['x0'], c['b']['x1'], c['yb']
            d = yy - yb
            k = np.interp(d, np.arange(len(perfil), dtype=np.float32), perfil, left=1.0, right=1.0)
            e0 = x0 - (c['sw'] if c['lado'] == 'L' else 0); e1 = x1 + (c['sw'] if c['lado'] == 'R' else 0)
            lado = sm(np.minimum(xx - e0 + 2, e1 + 2 - xx) / 6)
            fill = fill * (1 - (1 - k) * lado)[..., None]
        self.fr_rgb = fill.astype(np.float32); self.fr_a = al.astype(np.float32)
        self.fr_ring = (borde_ok & (yy > B) & (yy < B + 30)).astype(np.float32)

    def perfil_contacto(self):
        """Cociente (fila bajo la base) / (mostrador de delante) medido en las cajas de la IA, 0..24 px."""
        ref = self.ref; ps = []
        for c in self.cajas:
            b = c['b']; x0, x1 = int(b['x0']) + 30, int(b['x1']) - 30; yb = int(round(b['ybot']))
            col = ref[yb - 4:yb + 40, x0:x1].mean(2).mean(1)
            base = np.median(col[-12:])
            # el borde de la caja (blanco) se descarta: se empieza en la primera fila por debajo del blanco
            i0 = int(np.argmax(col < base * 1.05)) if (col < base * 1.05).any() else 0
            ps.append(np.clip(col[i0:i0 + 25] / base, 0.15, 1.0))
        L = min(len(p) for p in ps)
        pr = np.median(np.stack([p[:L] for p in ps]), 0)
        return np.concatenate([pr, [1.0]]).astype(np.float32)

    # -- tiras sobrantes: espejo a través del borde de la silueta vieja
    def prepara_sobras(self, c):
        b = c['b']; off = (int(b['x0']) - 40, int(c['ttop']) - 30)
        X1, Y1 = int(b['x1']) + 40, int(b['ybot']) + 30
        h, w = Y1 - off[1], X1 - off[0]
        mv = self.mascara_vieja(c, (h, w), off)
        mvd = cv2.dilate((mv > 0.02).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * DIL + 1, 2 * DIL + 1)))
        # caja nueva en estas coords (a resolución 1)
        an = cv2.resize(c['a'], None, fx=1 / SS, fy=1 / SS, interpolation=cv2.INTER_AREA)
        cover = np.zeros((h, w), np.float32)
        dx, dy = int(round(c['off'][0] - off[0])), int(round(c['off'][1] - off[1]))
        hh, ww = min(an.shape[0], h - dy), min(an.shape[1], w - dx)
        cover[dy:dy + hh, dx:dx + ww] = an[:hh, :ww]
        sob = (mvd > 0) & (cover < 0.98)
        # fuera de la franja del mostrador (eso lo pone la franja)
        yy, xx = np.mgrid[off[1]:Y1, off[0]:X1]
        nx0 = b['x0'] - (c['sw'] if c['lado'] == 'L' else 0) - 0.5; nx1 = b['x1'] + (c['sw'] if c['lado'] == 'R' else 0) + 0.5
        sob &= (yy < c['yb'] - 1) | (((xx < nx0) | (xx > nx1)) & (yy < b['ybot'] + 12))
        # espejo: para cada píxel sobrante, el píxel de fuera más cercano q; fuente = 2q - p
        fuera = (mvd == 0).astype(np.uint8)
        dist, lab = cv2.distanceTransformWithLabels(1 - fuera, cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
        ys_f, xs_f = np.where(fuera > 0)
        idx = np.zeros(lab.max() + 1, np.int64)
        lab_f = lab[fuera > 0]; idx[lab_f] = np.arange(len(lab_f))
        qy = ys_f[idx[lab]]; qx = xs_f[idx[lab]]
        py, px = np.mgrid[0:h, 0:w]
        sy = 2 * qy - py; sx = 2 * qx - px
        # a los lados de la pestaña (lo que era pestaña vieja y la nueva ya no tapa): espejo VERTICAL respecto al
        # borde de arriba de la silueta vieja en esa columna (brazos, costados y camiseta siguen en vertical)
        ntx0, ntx1 = c['cx'] - c['wt'] / 2 - off[0], c['cx'] + c['wt'] / 2 - off[0]
        lado = sob & (py < c['ybt'] - off[1] + 2) & ((px < ntx0 + 3) | (px > ntx1 - 3))
        dentro_v = mvd > 0
        ytop = np.where(dentro_v.any(0), np.argmax(dentro_v, 0), 0)          # primera fila de la silueta (dilatada)
        ye = (ytop - 1)[None].repeat(h, 0)
        sy = np.where(lado, 2 * ye - py, sy); sx = np.where(lado, px, sx)
        c['sob'] = dict(off=off, mask=sob.astype(np.float32), sx=(sx + off[0]).astype(np.float32), sy=(sy + off[1]).astype(np.float32),
                        shape=(h, w))


def warp_ref(img, M, off, sc, roi, interp=cv2.INTER_LINEAR, border=0):
    """img en coords (ref - off) * sc -> ROI del fotograma (x0,y0,x1,y1) con la afín M (ref->fotograma)."""
    x0, y0, x1, y1 = roi
    S = np.array([[1 / sc, 0, off[0]], [0, 1 / sc, off[1]], [0, 0, 1]])
    A = np.vstack([M, [0, 0, 1]]) @ S
    A[0, 2] -= x0; A[1, 2] -= y0
    return cv2.warpAffine(img, A[:2], (x1 - x0, y1 - y0), flags=interp, borderMode=cv2.BORDER_CONSTANT, borderValue=border)


def componer(P, t, Y, U, V, rng, gan_caja, gan_fr):
    """Cambia Y,U,V del fotograma t en su sitio."""
    A = P.A[t]
    # ROI: todo lo de las cajas y la franja en este fotograma
    pts = []
    for k, c in enumerate(P.cajas):
        b = c['b']
        for (x, y) in [(b['x0'] - 50, c['ttop'] - 40), (b['x1'] + 50, c['ttop'] - 40), (b['x0'] - 50, b['ybot'] + 60), (b['x1'] + 50, b['ybot'] + 60)]:
            pts.append(A[k] @ [x, y, 1])
    pts = np.array(pts)
    x0 = max(0, int(pts[:, 0].min()) & ~1); x1 = min(W, (int(pts[:, 0].max()) + 2) & ~1)
    y0 = max(0, int(pts[:, 1].min()) & ~1); y1 = min(H, (int(pts[:, 1].max()) + 2) & ~1)
    if x1 - x0 < 16 or y1 - y0 < 16:
        return
    roi = (x0, y0, x1, y1)
    Yr = Y[y0:y1, x0:x1]; Ur = U[y0 // 2:y1 // 2, x0 // 2:x1 // 2]; Vr = V[y0 // 2:y1 // 2, x0 // 2:x1 // 2]
    Uu = cv2.resize(Ur, (x1 - x0, y1 - y0), interpolation=cv2.INTER_LINEAR); Vu = cv2.resize(Vr, (x1 - x0, y1 - y0), interpolation=cv2.INTER_LINEAR)
    orig = yuv2rgb(Yr, Uu, Vu)
    out = orig.copy(); cambio = np.zeros(orig.shape[:2], np.float32)
    # 1) tiras sobrantes (espejo), leyendo del original
    for k, c in enumerate(P.cajas):
        s = c['sob']
        m = warp_ref(s['mask'], A[k], s['off'], 1.0, roi, cv2.INTER_LINEAR)
        if m.max() < 0.01:
            continue
        sx = warp_ref(s['sx'], A[k], s['off'], 1.0, roi, cv2.INTER_LINEAR)
        sy = warp_ref(s['sy'], A[k], s['off'], 1.0, roi, cv2.INTER_LINEAR)
        fx = A[k][0, 0] * sx + A[k][0, 1] * sy + A[k][0, 2] - x0
        fy = A[k][1, 0] * sx + A[k][1, 1] * sy + A[k][1, 2] - y0
        src = cv2.remap(orig, fx.astype(np.float32), fy.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        m = np.clip(m, 0, 1)
        out = out * (1 - m[..., None]) + src * m[..., None]; cambio = np.maximum(cambio, m)
    # 2) franja del mostrador: cada caja la lleva con su afín; mezcla por cercanía en x
    acc = np.zeros_like(out); acca = np.zeros(out.shape[:2], np.float32); wsum = np.zeros(out.shape[:2], np.float32)
    cxs = []
    for k, c in enumerate(P.cajas):
        b = c['b']; cxs.append(A[k] @ [(b['x0'] + b['x1']) / 2, b['ybot'], 1])
    xsf = np.arange(x0, x1, dtype=np.float32)
    for k, c in enumerate(P.cajas):
        d = np.abs(xsf - cxs[k][0]); wk = np.exp(-0.5 * (d / 260.0) ** 2) + 1e-6
        r_ = warp_ref(P.fr_rgb, A[k], P.fr_off, 1.0, roi, cv2.INTER_LINEAR)
        a_ = warp_ref(P.fr_a, A[k], P.fr_off, 1.0, roi, cv2.INTER_LINEAR)
        acc += r_ * wk[None, :, None]; acca += a_ * wk[None]; wsum += wk[None]
    fr = acc / wsum[..., None] * gan_fr[None, None]; fa = np.clip(acca / wsum, 0, 1)
    n = rng.standard_normal(fa.shape).astype(np.float32); n = cv2.GaussianBlur(n, (0, 0), 0.7); n *= 0.6 / (n.std() + 1e-6)
    fr = fr + n[..., None]
    out = out * (1 - fa[..., None]) + fr * fa[..., None]; cambio = np.maximum(cambio, fa)
    # 3) cajas nuevas (rgb premultiplicado), luego un pelo de desenfoque + el realce suave del vídeo
    ws = np.zeros(out.shape[:2], np.float32); atot = np.zeros(out.shape[:2], np.float32)
    for k, c in enumerate(P.cajas):
        a = warp_ref(c['a'], A[k], c['off'], SS, roi, cv2.INTER_LINEAR)
        if a.max() < 0.01:
            continue
        rgb = warp_ref(c['rgb'], A[k], c['off'], SS, roi, cv2.INTER_LINEAR) * gan_caja[k][None, None]
        out = out * (1 - a[..., None]) + rgb
        atot = np.maximum(atot, a)
    if atot.max() > 0.01:
        wz = np.clip(cv2.GaussianBlur(atot, (0, 0), 1.5) * 1.6, 0, 1)
        bl = cv2.GaussianBlur(out, (0, 0), 0.55)
        sh = bl + 0.30 * (bl - cv2.GaussianBlur(bl, (0, 0), 1.4))
        out = out * (1 - wz[..., None]) + sh * wz[..., None]
        g = rng.standard_normal(atot.shape).astype(np.float32); g = cv2.GaussianBlur(g, (0, 0), 0.6); g *= 0.7 / (g.std() + 1e-6)
        out = out + (g * atot)[..., None]
        cambio = np.maximum(cambio, wz)
    # escribir solo lo cambiado
    yo, uo, vo = rgb2yuv(np.clip(out, -20, 275))
    m = cambio > 1e-3
    Yn = Yr.astype(np.float32); Yn[m] = yo[m]
    Y[y0:y1, x0:x1] = np.clip(np.rint(Yn), 0, 255).astype(np.uint8)
    mh = cv2.resize(cambio, (Ur.shape[1], Ur.shape[0]), interpolation=cv2.INTER_AREA) > 1e-3
    uh = cv2.resize(uo, (Ur.shape[1], Ur.shape[0]), interpolation=cv2.INTER_AREA)
    vh = cv2.resize(vo, (Ur.shape[1], Ur.shape[0]), interpolation=cv2.INTER_AREA)
    Un = Ur.astype(np.float32); Vn = Vr.astype(np.float32); Un[mh] = uh[mh]; Vn[mh] = vh[mh]
    U[y0 // 2:y1 // 2, x0 // 2:x1 // 2] = np.clip(np.rint(Un), 0, 255).astype(np.uint8)
    V[y0 // 2:y1 // 2, x0 // 2:x1 // 2] = np.clip(np.rint(Vn), 0, 255).astype(np.uint8)


def ganancias(P, frames_iter):
    """Luz por fotograma: cartón de cada caja vieja y mostrador de delante, respecto al fotograma 0 (suavizado)."""
    raise NotImplementedError


def a_bgr(Y, U, V):
    buf = np.concatenate([Y.ravel(), U.ravel(), V.ravel()]).reshape(H * 3 // 2, W)
    return cv2.cvtColor(buf, cv2.COLOR_YUV2BGR_I420)


def main():
    plano, ent, sal = sys.argv[1:4]
    base = sys.argv[sys.argv.index('--base') + 1] if '--base' in sys.argv else 'mostrador'
    prueba = [int(x) for x in sys.argv[sys.argv.index('--prueba') + 1].split(',')] if '--prueba' in sys.argv else None
    # fotograma de referencia (0) en RGB float, del vídeo de ../mostrador (ya con el texto real)
    g0 = next(lector(f'{MOST}/{plano}.mp4'))
    Uu = cv2.resize(g0[1], (W, H), interpolation=cv2.INTER_LINEAR); Vu = cv2.resize(g0[2], (W, H), interpolation=cv2.INTER_LINEAR)
    ref = yuv2rgb(g0[0], Uu, Vu)
    P = Plano(plano, ref)
    for c in P.cajas:
        P.prepara_sobras(c)
    print('preparado', [(c['tipo'], round(c['W']), round(c['yb'] - c['b']['ybot'])) for c in P.cajas], flush=True)
    comp = None
    if base == 'k4':
        import importlib.util
        spec = importlib.util.spec_from_file_location('componer_m', f'{MOST}/componer.py'); comp = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(comp)
        cfg = json.load(open(f'{MOST}/cfg{plano}.json'))
        cajas_txt = [comp.Caja(t_, c_, l_, x_) for t_, c_, l_, x_ in zip(cfg['tipos'], cfg['caras'], cfg['logos'], cfg['textos'])]
    gan = json.load(open(f'{AQUI}/gan{plano}.json')) if os.path.exists(f'{AQUI}/gan{plano}.json') else None
    enc = None if prueba else escritor(sal)
    cnt = 0
    for t, (Y, U, V) in enumerate(lector(ent)):
        if prueba is not None and t > max(prueba):
            break
        if prueba is not None and t not in prueba:
            continue
        if comp is not None and t < P.n:
            r0 = np.random.default_rng(1000 + t)
            for i, cc in enumerate(cajas_txt):
                cc.aplicar(Y, U, V, np.array(P.seg['M'][f'caja{i}'][t]), r0)
            if cfg.get('elipse_a') and 'neon' in P.seg['M']:
                comp.neon_a(Y, U, V, np.array(P.seg['M']['neon'][t]), cfg['elipse_a'])
            if cfg.get('poli_ventana'):
                comp.ventana(Y, U, V, np.array(P.seg['M']['ventana'][t]), cfg['poli_ventana'])
        if prueba is not None:
            antes = a_bgr(Y, U, V)
        if t < P.n:
            gc = [np.array(gan['caja'][k][t]) if gan else np.ones(3) for k in range(len(P.cajas))]
            gf = np.array(gan['franja'][t]) if gan else np.ones(3)
            componer(P, t, Y, U, V, np.random.default_rng(5000 + t), gc, gf)
        if prueba is not None:
            cv2.imwrite(f'{sal}_{t:03d}_antes.png', antes)
            cv2.imwrite(f'{sal}_{t:03d}_despues.png', a_bgr(Y, U, V))
        else:
            enc.stdin.write(Y.tobytes()); enc.stdin.write(U.tobytes()); enc.stdin.write(V.tobytes())
        cnt += 1
        if cnt % 24 == 0:
            print('fotograma', t, flush=True)
    if enc:
        enc.stdin.close(); enc.wait()
    print('ok', cnt, 'fotogramas')


if __name__ == '__main__':
    main()
