#!/usr/bin/env bash
# Montaje v4 del vídeo con dependienta (12/11/2026), a 24 fps.
# El dueño no quería planos de cajas sobre fondo vacío: «tiene que estar todo el tiempo
# que se vea a la chica», enseñando la caja y dándole la vuelta para ver la parte de atrás.
# Cambios respecto a montaje_dependienta_30nov.sh:
#   - tramo 2 (4,875-11,79 s): la chica junto al escaparate enseña las dos cajas (clipA, Kling 217c32f0)
#     y luego gira la del cargador para enseñar la parte de atrás real (clipB, Kling d93567a7).
#   - tramo 5 (24,35-27,93 s): la chica entrega las cajas sobre el mostrador (clipC, Kling 70bef678).
# El audio no cambia (clip-intone-30nov-chica.mp4).
#
# Uso (desde pillatumovil/anuncios/2026-11/video-persona):
#   bash ../../../tools/montaje_dependienta_v4.sh              -> 1080x1920, clip-dependienta-v4.mp4
#   bash ../../../tools/montaje_dependienta_v4.sh CARPETA_4K   -> 2160x3840, clip-dependienta-v4-4k.mp4
# CARPETA_4K tiene los planos donde habla la chica ya mejorados con tools/mejorar_4k.py:
#   1.mp4 (fotogramas 0-117), 3.mp4 (283-358 con recorte 472:840:124:0), 4.mp4 (358-584), 6.mp4 (659-fin).
# Después: python3 tools/video_persona.py <clip> FUENTES SALIDA v3 [0 2]   (el 2 final = textos en 4K)
set -euo pipefail
K4=${1:-}
T=$(mktemp -d)
E="-an -c:v libx264 -crf 14 -preset slow -pix_fmt yuv420p -r 24"
f() { ffmpeg -y -loglevel error "$@"; }
if [ -z "$K4" ]; then
  A=1080; B=1920; SAL=clip-dependienta-v4.mp4
  UP="scale=$A:$B:flags=lanczos,unsharp=5:5:0.5,setsar=1"   # planos Intone (720x1280)
  f -i clip-intone.mp4 -vf "trim=start_frame=0:end_frame=117,setpts=PTS-STARTPTS,$UP" $E $T/1.mp4
  f -i clip-intone.mp4 -vf "trim=start_frame=283:end_frame=358,setpts=PTS-STARTPTS,crop=472:840:124:0,scale=$A:$B:flags=lanczos,unsharp=5:5:0.6,setsar=1" $E $T/3.mp4
  f -i clip-intone.mp4 -vf "trim=start_frame=358:end_frame=584,setpts=PTS-STARTPTS,$UP" $E $T/4.mp4
  f -i clip-intone.mp4 -vf "trim=start_frame=659,setpts=PTS-STARTPTS,$UP" $E $T/6.mp4
else
  A=2160; B=3840; SAL=clip-dependienta-v4-4k.mp4
  # se recodifican con los mismos ajustes que el resto para poder unirlos sin recomprimir
  for i in 1 3 4 6; do f -i "$K4/$i.mp4" -vf "setpts=PTS-STARTPTS,setsar=1" $E $T/$i.mp4; done
fi
KL="scale=-2:$B:flags=lanczos,crop=$A:$B,setsar=1"          # planos Kling (1080x1912 o 1080x1920)
# 2a) 2,25 s: junto al escaparate, enseña las dos cajas
f -i broll/clipA.mp4 -vf "trim=start_frame=0:end_frame=54,setpts=PTS-STARTPTS,$KL" $E $T/2a.mp4
# 2b) 4,67 s: primer plano, gira la caja del cargador y enseña la parte de atrás
f -i broll/clipB.mp4 -vf "trim=start_frame=0:end_frame=112,setpts=PTS-STARTPTS,$KL" $E $T/2b.mp4
# 5) 3,58 s: entrega las cajas en el mostrador («este precio acaba el treinta de noviembre»)
f -i broll/clipC.mp4 -vf "trim=start_frame=2:end_frame=88,setpts=PTS-STARTPTS,$KL" $E $T/5.mp4
for i in 1 2a 2b 3 4 5 6; do echo "file '$T/$i.mp4'" >> $T/l.txt; done
f -f concat -safe 0 -i $T/l.txt -c copy $T/v.mp4
f -i $T/v.mp4 -i clip-intone-30nov-chica.mp4 -map 0:v -map 1:a -c:v copy -c:a copy -shortest $SAL
echo ok $SAL
