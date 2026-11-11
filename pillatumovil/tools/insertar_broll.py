"""Sustituye un tramo de imagen de un clip por planos de producto (fotos) con zoom lento.
El audio del clip original se conserva entero.

Uso: python3 insertar_broll.py CLIP.mp4 SALIDA.mp4 INICIO FIN FOTO1 [FOTO2 ...]

11/11/2026: en el clip Intone del vídeo con dependienta, el plano de las manos
sobre las cajas (4,875-11,79 s) traía el texto de las cajas deformado
(«LI58-C», «Comge Cable»). Se cambia por las fotos de estudio de los packs
(fotos/estudio-pro/pack-usbc.png y pack-lightning.png), que tienen el texto correcto.
Cada foto (cuadrada) va centrada sobre una copia suya ampliada y desenfocada para llenar el 9:16.
"""
import subprocess, sys, tempfile

clip, salida, ini, fin = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
fotos = sys.argv[5:]
W, H, FPS = 720, 1280, 30
tmp = tempfile.mkdtemp()
dur = (fin - ini) / len(fotos)


def run(*a):
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *a], check=True)


partes = []
# 1) antes del tramo
run('-i', clip, '-t', f'{ini}', '-an', '-vf', f'scale={W}:{H},fps={FPS},format=yuv420p', '-c:v', 'libx264', '-crf', '16', f'{tmp}/p0.mp4')
partes.append(f'{tmp}/p0.mp4')
# 2) planos de producto
for i, f in enumerate(fotos):
    n = int(round(dur * FPS))
    vf = (f"[0:v]scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},boxblur=30:2,eq=brightness=-0.04[bg];"
          f"[0:v]scale={W*2}:-1[fg];[bg][fg]overlay=0:(H-h)/2,"
          f"zoompan=z='1+0.07*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={FPS},format=yuv420p")
    run('-loop', '1', '-i', f, '-filter_complex', vf, '-frames:v', str(n), '-c:v', 'libx264', '-crf', '16', f'{tmp}/b{i}.mp4')
    partes.append(f'{tmp}/b{i}.mp4')
# 3) después del tramo
run('-ss', f'{fin}', '-i', clip, '-an', '-vf', f'scale={W}:{H},fps={FPS},format=yuv420p', '-c:v', 'libx264', '-crf', '16', f'{tmp}/p9.mp4')
partes.append(f'{tmp}/p9.mp4')
open(f'{tmp}/l.txt', 'w').write(''.join(f"file '{p}'\n" for p in partes))
run('-f', 'concat', '-safe', '0', '-i', f'{tmp}/l.txt', '-c', 'copy', f'{tmp}/v.mp4')
run('-i', f'{tmp}/v.mp4', '-i', clip, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', salida)
print('ok', salida)
