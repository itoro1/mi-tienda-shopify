"""Sube a 4K real (2160x3840) un plano de vídeo de baja resolución, en local y sin créditos.

12/11/2026: el dueño veía los planos donde habla la chica (Intone, 720x1280) más blandos
que los planos nuevos de Kling. Un escalado normal (lanczos) no inventa detalle, así que:
  1. toda la imagen pasa por un modelo de superresolución x4 (SPAN «clear_reality»),
  2. la cara se restaura aparte (GFPGAN 1.4 o GPEN-BFR-1024) y se pega con máscara suave,
  3. el resultado se guarda a 2160x3840 y 24 fps.

Los modelos ONNX no están en el repositorio (pesan 300 MB). Se bajan de
https://github.com/facefusion/facefusion-assets/releases/download/models-3.0.0/
  clear_reality_x4.onnx  yoloface_8n.onnx  gfpgan_1.4.onnx  gpen_bfr_1024.onnx
Hace falta: pip install onnxruntime opencv-python-headless numpy

Uso:
  python3 mejorar_4k.py ENTRADA.mp4 SALIDA.mp4 MODELOS_DIR [--ini N] [--fin N]
        [--recorte w:h:x:y] [--cara gfpgan|gpen] [--mezcla 0.8] [--prueba FOTOGRAMA.png]
--ini/--fin: fotogramas de la entrada (fin no incluido). --recorte: recorte previo, como en ffmpeg.
--prueba: procesa solo el fotograma --ini y lo guarda como PNG (para comparar antes de lanzar todo).
"""
import argparse, subprocess, sys, time
import cv2, numpy as np, onnxruntime as ort

ap = argparse.ArgumentParser()
ap.add_argument('entrada'); ap.add_argument('salida'); ap.add_argument('modelos')
ap.add_argument('--ini', type=int, default=0); ap.add_argument('--fin', type=int, default=10**9)
ap.add_argument('--recorte'); ap.add_argument('--cara', default='gfpgan'); ap.add_argument('--mezcla', type=float, default=0.8)
ap.add_argument('--prueba'); ap.add_argument('--sin-cara', action='store_true')
a = ap.parse_args()
W, H = 2160, 3840

so = ort.SessionOptions(); so.intra_op_num_threads = 4; so.log_severity_level = 3
def ses(n): return ort.InferenceSession(f'{a.modelos}/{n}.onnx', so, providers=['CPUExecutionProvider'])
SR = ses('clear_reality_x4'); DET = ses('yoloface_8n')
TAM = 1024 if a.cara == 'gpen' else 512
CARA = None if a.sin_cara else ses('gpen_bfr_1024' if a.cara == 'gpen' else 'gfpgan_1.4')
# plantilla FFHQ de 5 puntos (ojos, nariz, comisuras) para 512 px
PLANT = np.array([[192.98138, 239.94708], [318.90277, 240.1936], [256.63416, 314.01935],
                  [201.26117, 371.41043], [313.08905, 371.15118]], np.float32) * (TAM / 512)


def superres(rgb):
    x = (rgb.astype(np.float32) / 255).transpose(2, 0, 1)[None]
    y = SR.run(None, {'input': x})[0][0].transpose(1, 2, 0)
    y = (np.clip(y, 0, 1) * 255).round().astype(np.uint8)
    inter = cv2.INTER_AREA if y.shape[1] >= W else cv2.INTER_LANCZOS4
    return cv2.resize(y, (W, H), interpolation=inter)


def detectar(rgb):
    """Devuelve los 5 puntos de la cara más grande, en coordenadas de la imagen de entrada."""
    h, w = rgb.shape[:2]; e = 640 / max(h, w)
    lienzo = np.zeros((640, 640, 3), np.uint8)
    peq = cv2.resize(rgb, (round(w * e), round(h * e))); lienzo[:peq.shape[0], :peq.shape[1]] = peq
    x = ((lienzo.astype(np.float32) - 127.5) / 128).transpose(2, 0, 1)[None]
    o = DET.run(None, {'input': x})[0][0].T          # (8400, 20): cx cy w h score + 5x(x y conf)
    o = o[o[:, 4] > 0.5]
    if not len(o): return None
    m = o[np.argmax(o[:, 2] * o[:, 3] * o[:, 4])]
    return m[5:].reshape(5, 3)[:, :2] / e


def restaurar(img4k, pts):
    """Restaura la cara de img4k (puntos ya en coordenadas 4K) y la pega con máscara suave."""
    M, _ = cv2.estimateAffinePartial2D(pts.astype(np.float32), PLANT, method=cv2.LMEDS)
    cara = cv2.warpAffine(img4k, M, (TAM, TAM), flags=cv2.INTER_AREA if abs(M[0, 0]) < 1 else cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
    x = ((cara.astype(np.float32) / 255 - 0.5) / 0.5).transpose(2, 0, 1)[None]
    y = CARA.run(None, {'input': x})[0][0].transpose(1, 2, 0)
    y = (np.clip(y * 0.5 + 0.5, 0, 1) * 255).round().astype(np.uint8)
    # máscara: óvalo centrado en la cara, bordes muy suaves (no toca pelo ni fondo)
    mk = np.zeros((TAM, TAM), np.float32)
    cv2.ellipse(mk, (TAM // 2, int(TAM * 0.56)), (int(TAM * 0.30), int(TAM * 0.37)), 0, 0, 360, 1, -1)
    mk = cv2.GaussianBlur(mk, (0, 0), TAM * 0.045) * a.mezcla
    Mi = cv2.invertAffineTransform(M)
    vuelta = cv2.warpAffine(y, Mi, (W, H), flags=cv2.INTER_AREA if abs(Mi[0, 0]) < 1 else cv2.INTER_LANCZOS4)
    mk4 = cv2.warpAffine(mk, Mi, (W, H))[..., None]
    return (img4k * (1 - mk4) + vuelta * mk4).round().astype(np.uint8)


vf = f"select='between(n,{a.ini},{a.fin - 1})',setpts=N/24/TB"
if a.recorte: vf += f',crop={a.recorte}'
info = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', a.entrada],
                      capture_output=True, text=True).stdout.strip().split(',')
w0, h0 = (int(a.recorte.split(':')[0]), int(a.recorte.split(':')[1])) if a.recorte else (int(info[0]), int(info[1]))
lee = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-i', a.entrada, '-vf', vf, '-vsync', '0', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                       stdout=subprocess.PIPE)
esc = None
if not a.prueba:
    esc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', '24', '-i', '-',
                            '-an', '-c:v', 'libx264', '-crf', '13', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-r', '24', a.salida], stdin=subprocess.PIPE)
suav, n, t0, fallos = None, 0, time.time(), 0
while True:
    b = lee.stdout.read(w0 * h0 * 3)
    if len(b) < w0 * h0 * 3: break
    rgb = np.frombuffer(b, np.uint8).reshape(h0, w0, 3)
    out = superres(rgb)
    if CARA is not None:
        p = detectar(rgb)
        if p is not None:
            p = p * (W / w0); fallos = 0
            # suavizado temporal de los puntos: evita que la cara restaurada «tiemble»
            suav = p if suav is None or np.abs(p - suav).max() > 40 else 0.6 * suav + 0.4 * p
        else:
            fallos += 1          # sin cara: se reutilizan los últimos puntos, como mucho 3 fotogramas
            if fallos > 3: suav = None
        if suav is not None:
            out = restaurar(out, suav)
    if a.prueba:
        cv2.imwrite(a.prueba, out[:, :, ::-1]); print('ok', a.prueba, round(time.time() - t0, 1), 's'); sys.exit()
    esc.stdin.write(out.tobytes()); n += 1
    if n % 24 == 0: print(n, 'fotogramas', round((time.time() - t0) / n, 1), 's/fot', flush=True)
esc.stdin.close(); esc.wait()
print('ok', a.salida, n, 'fotogramas')
