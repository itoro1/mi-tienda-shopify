"""3.ª revisión de la v6 (23/11, R2-s5-counter): en el plano 5 (Kling, cámara fija) el mostrador de delante sale vacío y de
otra madera (rojiza y mate) mientras que en los planos de Intone de antes y de después están las cajas encima y la madera
es miel. Aquí, sobre cajas/5.mp4 (2160x3840, antes de la curva de color del montaje):
  1. la madera del mostrador (desde el borde de la camiseta, y 3348) se lleva hacia el tono del mostrador de Intone
     (más clara y menos roja), con la textura de siempre;
  2. delante, en el borde del mostrador que queda fuera de cuadro, las tres cajas que no tiene en la mano (cable USB-C,
     adaptador y cable Lightning, en el orden de los planos 1 y 4): de ellas solo se ve la parte de arriba (pestaña con el
     ojal euro, tapa y el principio del frente), desenfocadas por estar más cerca que sus manos, como en los primeros planos
     de Intone. Frentes de las fotos reales del dueño (las mismas de mostrador2/cajas_reales.py).
Uso: python3 mostrador5.py cajas/5.mp4 cajas/5_mostrador.mp4 [--prueba N salida.png]"""
import subprocess, sys, os
import cv2, numpy as np
cv2.setNumThreads(2)
REPO = '/home/user/mi-tienda-shopify/pillatumovil'
AQUI = os.path.dirname(os.path.abspath(__file__))
TEX = {'cargador': REPO + '/fotos/caja3d/cargador-frente.png', 'cable': REPO + '/fotos/caja3d/cable-frente.png',
       'lightning': AQUI + '/../mostrador2/tex/lightning-frente.png'}
PROP = {'cargador': 0.923, 'cable': 1.03, 'lightning': 0.976}          # ancho/alto de la cara (como cajas_reales.py)
PEST = {'cargador': (0.57, 0.20), 'cable': (0.54, 0.22), 'lightning': (0.54, 0.20)}
ANCHO_MM = {'cargador': 79, 'cable': 67, 'lightning': 69}
W, H = 2160, 3840
BORDE = 3348                                    # primera fila de madera (borde de la camiseta), fija: la cámara no se mueve
ESC = float(os.environ.get('ESC_CAJAS', '1.10'))   # tamaño respecto a la caja de sus manos (más cerca de la cámara)
PX_MM = 580 * 2 / 79 / 2                         # px 4K por mm en la caja de sus manos (adaptador de 79 mm: ~580 px)
Y_PEST = int(os.environ.get('Y_PEST', '3420'))   # borde de arriba de la pestaña del adaptador (px 4K), bajo el borde
CAJAS = [('cable', 470), ('cargador', 1080), ('lightning', 1690)]   # tipo y centro x (px 4K); el plano 5 va de x 386 a 1736
FONDO_MM = {'cargador': 33, 'cable': 24, 'lightning': 24}
ALTO_MM = {'cargador': 85.6, 'cable': 65, 'lightning': 70.7}
TH = np.radians(18)                               # la cámara las ve desde algo más arriba: se ve la tapa
BLANCO = np.float32([230.3, 225.4, 222.9])       # blanco de la caja de sus manos en este plano (medido)


def rrect(shape, x0, y0, x1, y1, r):
    m = np.zeros(shape, np.float32); sh = 4; p = lambda v: int(round(v * (1 << sh)))
    cv2.rectangle(m, (p(x0 + r), p(y0)), (p(x1 - r), p(y1)), 1.0, -1, cv2.LINE_AA, sh)
    cv2.rectangle(m, (p(x0), p(y0 + r)), (p(x1), p(y1)), 1.0, -1, cv2.LINE_AA, sh)
    cv2.circle(m, (p(x0 + r), p(y0 + r)), p(r), 1.0, -1, cv2.LINE_AA, sh); cv2.circle(m, (p(x1 - r), p(y0 + r)), p(r), 1.0, -1, cv2.LINE_AA, sh)
    return m


def ojal(m, cx, cy, wt, ht):
    rh = 0.13 * ht; x0, x1 = cx - 0.37 * wt, cx + 0.37 * wt; rc = 1.75 * rh; sh = 4; p = lambda v: int(round(v * (1 << sh)))
    cv2.rectangle(m, (p(x0 + rh), p(cy - rh)), (p(x1 - rh), p(cy + rh)), 0, -1, cv2.LINE_AA, sh)
    cv2.circle(m, (p(x0 + rh), p(cy)), p(rh), 0, -1, cv2.LINE_AA, sh); cv2.circle(m, (p(x1 - rh), p(cy)), p(rh), 0, -1, cv2.LINE_AA, sh)
    cv2.circle(m, (p(cx), p(cy)), p(rc), 0, -1, cv2.LINE_AA, sh)
    return m


def capa_cajas():
    """RGBA (float) de las tres cajas, del tamaño del plano."""
    rgb = np.zeros((H, W, 3), np.float32); al = np.zeros((H, W), np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    for tipo, cx in CAJAS:
        Wd = ANCHO_MM[tipo] * PX_MM * ESC; x0, x1 = cx - Wd / 2, cx + Wd / 2
        k = Wd / ANCHO_MM[tipo]                           # px por mm de esta caja
        wt, ht = PEST[tipo][0] * Wd, PEST[tipo][1] * Wd * np.cos(TH)
        tapa = FONDO_MM[tipo] * k * np.sin(TH)
        # todas apoyan en la misma línea (fuera de cuadro): las del cable, más bajas, asoman menos
        Wa = ANCHO_MM['cargador'] * PX_MM * ESC; ka = Wa / ANCHO_MM['cargador']
        base = Y_PEST + PEST['cargador'][1] * Wa * np.cos(TH) + FONDO_MM['cargador'] * ka * np.sin(TH) + ALTO_MM['cargador'] * ka * np.cos(TH)
        y_fin = base; y_fr = base - ALTO_MM[tipo] * k * np.cos(TH); y_tab1 = y_fr - tapa; y_tab0 = y_tab1 - ht
        # frente (foto real), escalado al ancho
        tex = cv2.cvtColor(cv2.imread(TEX[tipo]), cv2.COLOR_BGR2RGB).astype(np.float32)
        mg = int(0.006 * tex.shape[1]); tex = tex[mg:-mg, mg:-mg]
        fw, fh = Wd, y_fin - y_fr
        Mt = np.array([[fw / tex.shape[1], 0, x0], [0, fh / tex.shape[0], y_fr]], np.float64)
        fr = cv2.warpAffine(cv2.resize(tex, (int(round(fw)), int(round(fh))), interpolation=cv2.INTER_AREA),
                            np.array([[1, 0, x0], [0, 1, y_fr]], np.float64), (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        a_fr = rrect((H, W), x0, y_fr, x1, y_fin, 1.5)
        alb = np.clip(fr / 243.0, 0, 1.06)
        # luz: arriba algo más clara (le da la luz de arriba), bordes laterales un poco más oscuros
        v = np.clip((yy - y_fr) / (y_fin - y_fr), 0, 1); u = np.clip((xx - x0) / Wd, 0, 1)
        luz_fr = (1.0 - 0.10 * v - 0.08 * np.clip(1 - np.minimum(u, 1 - u) / 0.05, 0, 1) - 0.03 * (u - 0.5))[..., None]
        c_fr = alb * BLANCO * 0.985 * luz_fr
        # tapa (cara de arriba): algo más clara y lisa, con un filo más oscuro donde se junta con el frente
        a_tp = np.zeros((H, W), np.float32)
        sh = 4; p = lambda q: int(round(q * (1 << sh)))
        cv2.rectangle(a_tp, (p(x0 + 1), p(y_tab1)), (p(x1 - 1), p(y_fr + 1)), 1.0, -1, cv2.LINE_AA, sh)
        s = np.clip((yy - y_tab1) / max(tapa, 1), 0, 1)[..., None]
        c_tp = BLANCO * (1.03 - 0.03 * s)
        # pestaña con el ojal euro (cartón como el frente, un poco más oscuro: queda detrás)
        a_pe = rrect((H, W), cx - wt / 2, y_tab0, cx + wt / 2, y_tab1 + 2, 0.42 * ht)
        a_pe = ojal(a_pe, cx, y_tab0 + 0.47 * ht, wt, ht)
        c_pe = BLANCO * 0.95
        for a_, c_ in ((a_pe, c_pe), (a_tp, c_tp), (a_fr, c_fr)):
            rgb = rgb * (1 - a_[..., None]) + c_ * a_[..., None]; al = np.maximum(al, a_)
    return rgb, al


MAD_K = np.float32([167.4, 96.7, 43.8])          # media de la madera de Kling en el plano (antes de la curva del montaje)
MAD_T = np.float32([float(v) for v in os.environ.get('MAD_T', '208,156,112').split(',')])   # objetivo (pieza): tras la
#                                                  curva del montaje queda cerca de la de Intone (L 74, a 16, b 28)


def madera(f):
    """La madera rojiza y mate de Kling, hacia el tono miel del mostrador de Intone: media nueva y la misma veta."""
    return MAD_T + (f - MAD_K) * 1.15


def prepara():
    rgb, al = capa_cajas()
    sig = float(os.environ.get('DESENF', '2.6'))    # desenfoque (px 4K): algo más que la madera de al lado (Kling ampliado)
    pre = cv2.GaussianBlur(rgb * al[..., None], (0, 0), sig); alb = cv2.GaussianBlur(al, (0, 0), sig)
    col = pre / np.maximum(alb[..., None], 1e-4)
    # sombra suave de las cajas sobre la madera de detrás (luz de delante y arriba)
    som = cv2.GaussianBlur(np.roll(al, -40, 0), (0, 0), 45) * 0.12
    mad = np.clip((np.arange(H, dtype=np.float32) - BORDE) / 10, 0, 1)[:, None]
    return col, alb, som * mad


def compone(fr, col, alb, som, rng):
    f = fr.astype(np.float32)
    mad = np.clip((np.arange(H, dtype=np.float32) - BORDE + 2) / 8, 0, 1)[:, None, None]
    f = f * (1 - mad) + np.clip(madera(f), 0, 255) * mad
    f = f * (1 - som[..., None])
    g = rng.normal(0, 2.6, (H, W, 1)).astype(np.float32)
    f = f * (1 - alb[..., None]) + (col + g) * alb[..., None]
    return np.clip(f + .5, 0, 255).astype(np.uint8)


if __name__ == '__main__':
    ENT, SAL = sys.argv[1:3]
    col, alb, som = prepara()
    prueba = int(sys.argv[sys.argv.index('--prueba') + 1]) if '--prueba' in sys.argv else None
    p = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-i', ENT, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    enc = None if prueba is not None else subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', '24', '-i', '-',
                                                         '-an', '-c:v', 'libx264', '-crf', '12', '-preset', 'medium', '-pix_fmt', 'yuv420p', SAL], stdin=subprocess.PIPE)
    n = 0
    while True:
        b = p.stdout.read(W * H * 3)
        if len(b) < W * H * 3: break
        fr = np.frombuffer(b, np.uint8).reshape(H, W, 3)
        if prueba is not None:
            if n == prueba:
                cv2.imwrite(SAL, cv2.cvtColor(compone(fr, col, alb, som, np.random.default_rng(n)), cv2.COLOR_RGB2BGR)); p.kill(); break
        else:
            enc.stdin.write(compone(fr, col, alb, som, np.random.default_rng(n)).tobytes())
        n += 1
    if enc: enc.stdin.close(); enc.wait()
    print('ok', SAL, n)
