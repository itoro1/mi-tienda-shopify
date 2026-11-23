"""Sincronía labios-voz: (1) desfase de la voz del vídeo frente a clip-intone-30nov-chica (correlación cruzada por frase);
   (2) apertura de la boca (puntos 62-66 / alto de la cara) frente a la envolvente de la voz, por plano hablado, en el
   vídeo final y en el original de Intone (clip-intone.mp4 con su audio): el desfase final menos el de Intone es lo que
   el montaje ha movido. python3 sincro.py FINAL.mp4 caras_final.npz"""
import subprocess, sys, numpy as np, scipy.signal as ss, scipy.io.wavfile as wf
FIN, CAR = sys.argv[1:3]
VP = '/home/user/mi-tienda-shopify/pillatumovil/anuncios/2026-11/video-persona'
def audio(f):
    p = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-map', '0:a', '-ac', '1', '-ar', '48000', '-f', 'f32le', '-'], capture_output=True)
    return np.frombuffer(p.stdout, np.float32).astype(np.float64)
C0, CD = 24.40, 0.875        # 23/11 (T1): el audio quita 24,40-25,275 s; lo de después va 0,875 s antes
FS = 48000; fa = audio(FIN); ch = audio(f'{VP}/clip-intone-30nov-chica.mp4'); it = audio(f'{VP}/clip-intone.mp4')
frases = [(0.31, 1.89), (2.40, 2.95), (3.30, 4.40), (12.43, 13.06), (13.45, 14.69), (15.23, 15.62), (15.86, 17.54), (18.03, 19.22),
          (19.48, 20.49), (21.02, 21.93), (22.06, 24.12), (25.58, 27.80), (28.43, 29.12)]
print('(1) voz del vídeo final frente a clip-intone-30nov-chica (ms, + = más tarde):')
for a0, a1 in frases:
    i, j = int(a0 * FS), int(a1 * FS); s = ch[i:j]; m = int(0.3 * FS); sh = int(round(CD * FS)) if a0 > C0 else 0
    r = fa[i - sh - m:j - sh + m]
    c = ss.correlate(r, s, mode='valid', method='fft'); k = int(np.argmax(c)); dk = 0.5 * (c[k - 1] - c[k + 1]) / (c[k - 1] - 2 * c[k] + c[k + 1])
    print(f'   {a0:6.2f}-{a1:6.2f} s: {(k + dk - m) / FS * 1000:+7.2f} ms' + (f'   (en el vídeo {a0 - CD:5.2f} s: corte de 0,875 s)' if sh else ''))
print('    «Toque Comprar» frente a clip-intone.mp4 (su audio original):', end=' ')
i, j = int(27.93 * FS), int(28.62 * FS); s_ = it[i:j]; m = int(1.2 * FS); r = fa[i - m:j + m]
c = ss.correlate(r, s_, mode='valid', method='fft'); k = int(np.argmax(c)); VOZ6 = (k - m) / FS * 1000; print(f'{VOZ6:+.2f} ms')
def apertura(lm):
    return np.linalg.norm(lm[:, 66] - lm[:, 62], axis=1) / (lm[:, 8, 1] - lm[:, 27, 1])
mF = apertura(np.load(CAR)['lm'])
import os
if not os.path.exists('caras_intone.npz'):
    subprocess.run([sys.executable, 'caras.py', f'{VP}/clip-intone.mp4', 'caras_intone.npz'], check=True)
mI = apertura(np.load('caras_intone.npz')['lm'])
print('(2) imagen: qué fotograma de clip-intone.mp4 se ve en cada plano hablado (serie de apertura de la boca,')
print('    puntos 62-66 / alto de cara, que no cambia con el recorte); y desfase neto voz-labios respecto a Intone:')
voz = {'6': VOZ6}
for nom, a, b in (('1 (con el recorte x1,3)', 6, 117), ('3', 298, 358), ('4 abierto (con el x1,25)', 358, 491),
                  ('4 primer plano, 1.ª frase', 504, 522), ('4 primer plano x1,22', 528, 574), ('6', 651, 683)):
    best = []
    for d in range(-15, 16):
        x = mF[a:b]; y = mI[a - d:b - d]
        best.append(np.corrcoef(np.nan_to_num(x), np.nan_to_num(y))[0, 1] if len(y) == len(x) else -9)
    k = int(np.argmax(best)); d = k - 15; v = voz.get(nom[0], 23.2)
    print(f'    plano {nom:28s}: fotograma n = Intone n{-d:+d} (r {best[k]:.3f}) -> imagen {d / 24 * 1000:+6.1f} ms, voz {v:+6.1f} ms: '
          f'la voz va {v - d / 24 * 1000:+5.1f} ms ({(v - d / 24 * 1000) / 1000 * 24:+.2f} fotogramas) respecto al original')
