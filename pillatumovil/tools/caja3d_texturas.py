"""Saca de las FOTOS REALES del dueño las caras de las cajas, enderezadas y limpias, para la caja en 3D.

Uso: python3 caja3d_texturas.py MODELOS_DIR        (desde pillatumovil/)
Salida: fotos/caja3d/{cargador,cable}-{frente,trasera}.png y fotos/caja3d/medidas.json

16/11/2026. El dueño no quiere «diseños genéricos»: quiere la caja tal cual es, por todas sus caras.
Las caras que se usaban antes (fotos/cine/) eran recreaciones: la pestaña de colgar no era la real,
la caja salía más alta de lo que es y el texto de detrás no coincidía (ponía 2026 y otro código).
Aquí cada cara sale de una foto suya (fotos/reales/):
  - se marca el cuadrilátero de la cara en la foto (esquinas medidas a mano, abajo);
  - se calcula su proporción real ancho/alto a partir de la perspectiva (método de Zhang para un
    rectángulo visto con una cámara de píxel cuadrado y centro óptico en el centro de la foto);
  - se endereza, se iguala la luz (el papel queda blanco y uniforme, la impresión se conserva)
    y se amplía con superresolución para que aguante el 4K.
"""
import json, os, sys
import cv2, numpy as np, onnxruntime as ort

MOD = sys.argv[1]
R = 'fotos/reales/'
# cara: (foto, esquinas TL TR BR BL en píxeles de la foto, ancho de salida)
# Proporción real ancho/alto de cada caja. Sale de la perspectiva de las fotos (ver «medida» al ejecutar):
# la del cargador da 0,923 por delante y 0,922 por detrás; la del cable, entre 1,00 y 1,06.
PROP = {'cargador': 0.923, 'cable': 1.03}
# Medidas en milímetros. El ancho y el fondo salen de las fichas de tienda (79 x 33 mm el cargador,
# 67 x 24 mm el cable); el alto, del ancho y la proporción medida en las fotos.
MM = {'cargador': (79.0, 79.0 / 0.923, 33.0), 'cable': (67.0, 67.0 / 1.03, 24.0)}
CARAS = {
    'cargador-frente':  (R + 'cajas-frente-usb-c.jpg', [(298, 475), (1042, 457), (1040, 1243), (421, 1250)], 1600),
    'cable-frente':     (R + 'cajas-frente-usb-c.jpg', [(1126, 702), (1784, 700), (1724, 1305), (1126, 1306)], 1600),
    'cargador-trasera': (R + 'cajas-traseras-1.jpg',   [(614, 618), (963, 617), (1016, 1012), (626, 1021)], 1600),
    'cable-trasera':    (R + 'cajas-traseras-1.jpg',   [(213, 691), (560, 681), (601, 1010), (238, 1060)], 1600),
}


def proporcion(q, wh):
    """Ancho/alto real de un rectángulo a partir de sus 4 esquinas en la foto (TL TR BR BL)."""
    u0, v0 = wh[0] / 2, wh[1] / 2
    m1, m2, m4, m3 = [np.array([x - u0, y - v0, 1.0]) for x, y in q]          # m1=TL m2=TR m3=BL m4=BR
    k2 = np.dot(np.cross(m1, m4), m3) / np.dot(np.cross(m2, m4), m3)
    k3 = np.dot(np.cross(m1, m4), m2) / np.dot(np.cross(m3, m4), m2)
    n2 = k2 * m2 - m1; n3 = k3 * m3 - m1
    if abs(n2[2] * n3[2]) < 1e-9:
        return float(np.hypot(n2[0], n2[1]) / np.hypot(n3[0], n3[1])), None
    f2 = -(n2[0] * n3[0] + n2[1] * n3[1]) / (n2[2] * n3[2])
    if f2 <= 0:                                                                # perspectiva muy suave: sin focal fiable
        return float(np.hypot(n2[0], n2[1]) / np.hypot(n3[0], n3[1])), None
    r2 = (n2[0] ** 2 / f2 + n2[1] ** 2 / f2 + n2[2] ** 2) / (n3[0] ** 2 / f2 + n3[1] ** 2 / f2 + n3[2] ** 2)
    return float(np.sqrt(r2)), float(np.sqrt(f2))


def luz_plana(im):
    """Iguala la luz: el papel queda blanco neutro y uniforme; lo impreso se conserva tal cual.
    La luz de la foto se modela como una superficie suave (polinomio de grado 3 por canal) ajustada
    solo con los píxeles de papel, que son los más claros de cada zona."""
    f = im.astype(np.float32); h, w = f.shape[:2]
    p = cv2.resize(f, (240, int(240 * h / w)), interpolation=cv2.INTER_AREA); ph, pw = p.shape[:2]
    gris = p.mean(2); tope = cv2.dilate(gris, np.ones((35, 35), np.uint8))
    papel = gris > tope * 0.93
    yy, xx = np.mgrid[0:ph, 0:pw].astype(np.float64); xn = xx / pw * 2 - 1; yn = yy / ph * 2 - 1
    base = lambda x, y: np.stack([x ** i * y ** j for i in range(4) for j in range(4 - i)], -1)
    A = base(xn[papel], yn[papel])
    YY, XX = np.mgrid[0:h, 0:w].astype(np.float32); B = base(XX / w * 2 - 1, YY / h * 2 - 1)
    out = np.empty_like(f)
    for c in range(3):
        coef, *_ = np.linalg.lstsq(A, p[..., c][papel].astype(np.float64), rcond=None)
        out[..., c] = f[..., c] / np.maximum(B @ coef.astype(np.float32), 1) * 243.0
    out = 243.0 - np.maximum(243.0 - out - 6.0, 0) * (243.0 / 237.0)           # fuera las sombras muy leves del papel
    return np.clip(out, 0, 255).astype(np.uint8)


so = ort.SessionOptions(); so.intra_op_num_threads = 4; so.log_severity_level = 3
sr = ort.InferenceSession(f'{MOD}/clear_reality_x4.onnx', so, providers=['CPUExecutionProvider'])


def amplia(im):
    x = (np.ascontiguousarray(im[:, :, ::-1]).astype(np.float32) / 255).transpose(2, 0, 1)[None]
    y = sr.run(None, {'input': x})[0][0].transpose(1, 2, 0)
    return (np.clip(y, 0, 1) * 255).round().astype(np.uint8)[:, :, ::-1]


os.makedirs('fotos/caja3d', exist_ok=True)
medidas = {}
for nombre, (foto, q, ancho) in CARAS.items():
    im = cv2.imread(foto); h, w = im.shape[:2]
    medida, focal = proporcion(q, (w, h))
    prop = PROP[nombre.split('-')[0]]
    medidas[nombre] = {'ancho_alto_medido': round(medida, 4), 'focal_px': focal and round(focal)}
    # se endereza al tamaño que tiene en la foto (sin inventar píxeles) y luego se amplía
    lado = max(np.hypot(q[1][0] - q[0][0], q[1][1] - q[0][1]), np.hypot(q[2][0] - q[3][0], q[2][1] - q[3][1]))
    W0 = int(round(lado)); H0 = int(round(W0 / prop))
    Hm = cv2.getPerspectiveTransform(np.float32(q), np.float32([[0, 0], [W0, 0], [W0, H0], [0, H0]]))
    cara = cv2.warpPerspective(im, Hm, (W0, H0), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    cara = amplia(cara)                                                       # x4
    m = int(cara.shape[1] * (.016 if "trasera" in nombre else .006))                                            # fuera el filo de la arista
    cara = cara[m:-m, m:-m]
    cara = cv2.resize(cara, (ancho, int(round(ancho / prop))), interpolation=cv2.INTER_AREA)
    cara = luz_plana(cara)
    cv2.imwrite(f'fotos/caja3d/{nombre}.png', cara, [cv2.IMWRITE_PNG_COMPRESSION, 9])
    print(nombre, '| en la foto', W0, 'x', H0, '| ancho/alto medido', round(medida, 3), '-> usado', prop, '| salida', cara.shape[1], 'x', cara.shape[0])
json.dump({'mm': {k: [round(v, 1) for v in t] for k, t in MM.items()}, 'caras': medidas}, open('fotos/caja3d/medidas.json', 'w'), indent=1)
