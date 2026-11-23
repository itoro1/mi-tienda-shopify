"""Geometría de las cajas IA del mostrador en el fotograma de referencia (0): silueta, bordes, pestaña, ojal."""
import sys, json, numpy as np, cv2
img = cv2.imread(sys.argv[1]); cfg = json.load(open(sys.argv[2])); out = sys.argv[3]
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV); Y = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
res = []
for i, (cx0, cy0, cx1, cy1) in enumerate(cfg['cajas']):
    # zona de búsqueda alrededor de la cara seguida
    X0, X1 = cx0 - 120, cx1 + 120; Y0, Y1 = cy0 - 260, cy1 + 160
    sub = img[Y0:Y1, X0:X1]; s = hsv[Y0:Y1, X0:X1, 1]; y = Y[Y0:Y1, X0:X1]
    m = ((y > 150) & (s < 45)).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    k = 1 + np.argmax(st[1:, 4]); comp = (lab == k).astype(np.uint8)
    comp = cv2.morphologyEx(comp, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    # rellena agujeros internos de la cara (dibujo), pero NO el ojal de la pestaña: se hace por filas
    h, w = comp.shape
    cols = np.where(comp.any(0))[0]
    # bordes izquierdo/derecho de la cara: filas del cuerpo (por debajo de la pestaña)
    rows_body = range(cy0 - Y0 + 40, cy1 - Y0 - 20)
    L = []; R = []
    for r in rows_body:
        xs = np.where(comp[r])[0]
        if len(xs): L.append(xs.min()); R.append(xs.max())
    x0 = float(np.median(L)) + X0; x1 = float(np.median(R)) + X0 + 1
    # abajo: por columnas del centro
    cc = np.arange(int(x0 - X0) + 20, int(x1 - X0) - 20)
    bots = [h - 1 - np.argmax(comp[::-1, c]) for c in cc]
    ybot = float(np.median(bots)) + Y0 + 1
    tops = np.array([np.argmax(comp[:, c]) for c in cc]) + Y0
    # cuerpo (hombros) = moda de los tops altos; pestaña = columnas con top mucho más arriba
    sh = np.median(tops[(tops > np.percentile(tops, 60))])
    tabc = cc[tops < sh - 25] + X0
    tab_top = float(np.percentile(tops[tops < sh - 25], 10)) if len(tabc) else None
    res.append({'i': i, 'x0': x0, 'x1': x1, 'ybot': ybot, 'hombro': float(sh), 'tab_x0': float(tabc.min()), 'tab_x1': float(tabc.max() + 1),
                'tab_top': tab_top, 'W': x1 - x0, 'tipo': cfg['tipos'][i], 'zona': [int(X0), int(Y0), int(X1), int(Y1)]})
    full = np.zeros(img.shape[:2], np.uint8); full[Y0:Y1, X0:X1] = comp
    np.save(out + f'_sil{i}.npy', full[Y0:Y1, X0:X1])
    print(res[-1])
json.dump(res, open(out + '.json', 'w'), indent=1)
