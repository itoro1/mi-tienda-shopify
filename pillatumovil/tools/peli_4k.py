"""Une los planos renderizados (PNG) y los sube a 4K real (2160x3840) con superresolución x4 («clear_reality»).

Uso: python3 peli_4k.py CARPETA_PLANOS MODELOS_DIR SALIDA.mp4 plano1 plano2 ...
En la prueba del 21/11 las letras de las cajas salían más nítidas que con lanczos y sin deformarse.
"""
import glob, os, subprocess, sys
import cv2, numpy as np, onnxruntime as ort

CARP, MOD, SAL = sys.argv[1:4]; PLANOS = sys.argv[4:]
W, H, FPS = 2160, 3840, 24
so = ort.SessionOptions(); so.intra_op_num_threads = os.cpu_count() or 4; so.log_severity_level = 3
SR = ort.InferenceSession(os.path.join(MOD, 'clear_reality_x4.onnx'), so, providers=['CPUExecutionProvider'])
NOMBRE = SR.get_inputs()[0].name


def sube(rgb):
    """SR x4 por bandas horizontales con solape (menos memoria) y luego reducción a 2160x3840."""
    h, w = rgb.shape[:2]; x = rgb.astype(np.float32) / 255; banda, solape = 320, 16; out = np.zeros((h * 4, w * 4, 3), np.float32)
    for y0 in range(0, h, banda):
        a, b = max(0, y0 - solape), min(h, y0 + banda + solape)
        y = SR.run(None, {NOMBRE: x[a:b].transpose(2, 0, 1)[None]})[0][0].transpose(1, 2, 0)
        out[y0 * 4:min(h, y0 + banda) * 4] = y[(y0 - a) * 4:(y0 - a) * 4 + (min(h, y0 + banda) - y0) * 4]
    out = (out.clip(0, 1) * 255).astype(np.uint8)
    return cv2.resize(out, (W, H), interpolation=cv2.INTER_AREA)


fotos = [f for p in PLANOS for f in sorted(glob.glob(os.path.join(CARP, p, '[0-9]*.png')))]
esc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                        '-i', '-', '-c:v', 'libx264', '-crf', '14', '-preset', 'medium', '-pix_fmt', 'yuv420p', SAL], stdin=subprocess.PIPE)
for i, f in enumerate(fotos):
    rgb = cv2.imread(f)[:, :, ::-1]
    esc.stdin.write(np.ascontiguousarray(sube(rgb)).tobytes())
    if i % 24 == 0: print(f'{i}/{len(fotos)}', flush=True)
esc.stdin.close(); esc.wait()
print('ok', SAL, len(fotos), 'fotogramas')
