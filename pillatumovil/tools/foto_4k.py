"""Amplía x4 un recorte de una foto con superresolución (SPAN «clear_reality»), en local.

Uso: python3 foto_4k.py FOTO SALIDA.png MODELOS_DIR [X0 Y0 X1 Y1]
Sirve para sacar un plano de detalle nítido de una imagen (13/11/2026: el cargador barato
del plano del cliente, en el anuncio «problema → solución»). Modelos: ver tools/mejorar_4k.py.
"""
import sys
import cv2, numpy as np, onnxruntime as ort

foto, salida, modelos = sys.argv[1:4]
im = cv2.imread(foto)[:, :, ::-1]
if len(sys.argv) > 4:
    x0, y0, x1, y1 = map(int, sys.argv[4:8]); im = im[y0:y1, x0:x1]
so = ort.SessionOptions(); so.intra_op_num_threads = 4; so.log_severity_level = 3
sr = ort.InferenceSession(f'{modelos}/clear_reality_x4.onnx', so, providers=['CPUExecutionProvider'])
x = (np.ascontiguousarray(im).astype(np.float32) / 255).transpose(2, 0, 1)[None]
y = sr.run(None, {'input': x})[0][0].transpose(1, 2, 0)
cv2.imwrite(salida, (np.clip(y, 0, 1) * 255).round().astype(np.uint8)[:, :, ::-1])
print('ok', salida, y.shape[1], 'x', y.shape[0])
