"""Cara de delante de la caja del cable USB-C a Lightning, sacada de la foto real del dueño
(fotos/reales/cajas-frente-lightning.jpg) con el mismo método que tools/caja3d_texturas.py:
enderezar (proporción por perspectiva, Zhang), ampliar x4 (clear_reality_x4) e igualar la luz."""
import sys, os, json
import cv2, numpy as np, onnxruntime as ort
REPO = '/home/user/mi-tienda-shopify/pillatumovil'
MOD = sys.argv[1]; OUT = sys.argv[2]
src = open(REPO + '/tools/caja3d_texturas.py').read()
ns = {}
# solo las funciones (el script hace el trabajo al importarse)
exec(src.split('so = ort.SessionOptions()')[0].replace("MOD = sys.argv[1]", "MOD = ''"), ns)
proporcion, luz_plana = ns['proporcion'], ns['luz_plana']
so = ort.SessionOptions(); so.intra_op_num_threads = 4; so.log_severity_level = 3
sr = ort.InferenceSession(f'{MOD}/clear_reality_x4.onnx', so, providers=['CPUExecutionProvider'])
def amplia(im):
    x = (np.ascontiguousarray(im[:, :, ::-1]).astype(np.float32) / 255).transpose(2, 0, 1)[None]
    y = sr.run(None, {'input': x})[0][0].transpose(1, 2, 0)
    return (np.clip(y, 0, 1) * 255).round().astype(np.uint8)[:, :, ::-1]
im = cv2.imread(REPO + '/fotos/reales/cajas-frente-lightning.jpg'); h, w = im.shape[:2]
q = [(575.0, 810.5), (921.3, 806.3), (933.0, 1170.0), (578.0, 1169.0)]
medida, focal = proporcion(q, (w, h))
print('ancho/alto medido', medida, 'focal', focal)
prop = float(sys.argv[3]) if len(sys.argv) > 3 else medida
lado = max(np.hypot(q[1][0] - q[0][0], q[1][1] - q[0][1]), np.hypot(q[2][0] - q[3][0], q[2][1] - q[3][1]))
W0 = int(round(lado)); H0 = int(round(W0 / prop))
Hm = cv2.getPerspectiveTransform(np.float32(q), np.float32([[0, 0], [W0, 0], [W0, H0], [0, H0]]))
cara = cv2.warpPerspective(im, Hm, (W0, H0), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
cara = amplia(cara)
m = int(cara.shape[1] * .010); cara = cara[m:-m, m:-m]
cara = cv2.resize(cara, (1600, int(round(1600 / prop))), interpolation=cv2.INTER_AREA)
cara = luz_plana(cara)
cv2.imwrite(OUT, cara, [cv2.IMWRITE_PNG_COMPRESSION, 9])
print('salida', cara.shape, 'prop usada', prop)
