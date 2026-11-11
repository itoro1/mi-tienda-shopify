#!/usr/bin/env bash
# Montaje de imagen del vídeo con dependienta (oferta hasta el 30/11), a 24 fps nativos.
# 11/11/2026: el dueño lo veía «poco fluido». Las fuentes de Higgsfield vienen a 24 fps
# y antes se montaba a 30 (1 de cada 4 fotogramas repetido) y el tramo de las cajas iba
# acelerado ×1,38. Ahora todo va a 24 fps, cortado por número de fotograma, sin acelerar,
# y el zoom del plano de los packs es suave (escala en coma flotante sobre una imagen 4x).
#
# Uso (desde pillatumovil/anuncios/2026-11/video-persona):
#   bash ../../../tools/montaje_dependienta_30nov.sh
# Salida: clip-intone-30nov-24fps.mp4 (imagen nueva + audio de clip-intone-30nov-chica.mp4).
# Después: python3 tools/video_persona.py <ese clip> FUENTES SALIDA v3
set -euo pipefail
T=$(mktemp -d)
E="-an -c:v libx264 -crf 15 -preset slow -pix_fmt yuv420p -r 24"
f() { ffmpeg -y -loglevel error "$@"; }
# 1) 0-4,875 s: plano medio con la pregunta (Intone 5630c05b)
f -i clip-intone.mp4 -vf "trim=start_frame=0:end_frame=117,setpts=PTS-STARTPTS" $E $T/1.mp4
# 2) 4,875-11,79 s: la chica señala las cajas (Intone 83934977), a velocidad normal
f -i clip-tramo-cajas.mp4 -vf "trim=start_frame=10:end_frame=176,setpts=PTS-STARTPTS" $E $T/2.mp4
# 3) 11,79-14,92 s: plano del precio recortado a primer plano (sin cajas deformadas)
f -i clip-intone.mp4 -vf "trim=start_frame=283:end_frame=358,setpts=PTS-STARTPTS,crop=472:840:124:0,scale=720:1280:flags=lanczos,unsharp=5:5:0.6" $E $T/3.mp4
# 4) 14,92-24,35 s: plano abierto y frontal
f -i clip-intone.mp4 -vf "trim=start_frame=358:end_frame=584,setpts=PTS-STARTPTS" $E $T/4.mp4
# 5) 3,58 s: los dos packs mientras suena «este precio acaba el treinta de noviembre»
f -i ../../../fotos/estudio-pro/dos-packs-9x16.png -vf "scale=2880:5120:flags=lanczos" $T/big.png
f -loop 1 -framerate 24 -i $T/big.png -vf "format=rgb24,scale=w='2880*(1+0.06*t/3.583)':h='5120*(1+0.06*t/3.583)':eval=frame:flags=bicubic,crop=2880:5120,scale=720:1280:flags=lanczos,format=yuv420p" -frames:v 86 $E $T/5.mp4
# 6) final: «Toque Comprar»
f -i clip-intone.mp4 -vf "trim=start_frame=659,setpts=PTS-STARTPTS" $E $T/6.mp4
for i in 1 2 3 4 5 6; do echo "file '$T/$i.mp4'" >> $T/l.txt; done
f -f concat -safe 0 -i $T/l.txt -c copy $T/v.mp4
f -i $T/v.mp4 -i clip-intone-30nov-chica.mp4 -map 0:v -map 1:a -c:v copy -c:a copy -shortest clip-intone-30nov-24fps.mp4
echo ok clip-intone-30nov-24fps.mp4
