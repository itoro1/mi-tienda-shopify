#!/usr/bin/env bash
# Montaje v5 del vídeo con dependienta (20/11/2026), a 24 fps y 2160x3840.
# Igual que la v4 (tools/montaje_dependienta_v4.sh) y con la misma voz, pero las cajas que dibujó la IA se
# cambian por la caja REAL en 3D (tools/cajas3d_video.py, caras sacadas de las fotos del dueño). El dueño:
# «cuando la chica coge nuestros cargadores se ven las cajas mal hechas, no se ve un producto real».
#   2a) clipA, 48 fotogramas (antes 54: después sube una caja al cuello y ya no hay camiseta detrás)
#   2b) clipB, 118 fotogramas (antes 112: gana los 6 que pierde el 2a; la duración total no cambia)
#   5)  clipT (la chica gira la caja con las dos manos), 86 fotogramas, en lugar de clipC (la entrega en el
#       mostrador: dos cajas pegadas en una mano, con madera y brazo detrás, donde el arreglo se notaba).
# Uso (desde pillatumovil/anuncios/2026-11/video-persona):
#   bash ../../../tools/montaje_dependienta_v5.sh CARPETA_4K     -> clip-dependienta-v5-4k.mp4
# CARPETA_4K: los planos hablados ya mejorados con tools/mejorar_4k.py (1.mp4, 3.mp4, 4.mp4, 6.mp4; ver la v4).
# Después: python3 ../../../tools/video_persona.py clip-dependienta-v5-4k.mp4 FUENTES SALIDA.mp4 v3 0 2
set -euo pipefail
K4=$1
T=$(mktemp -d)
E="-an -c:v libx264 -crf 14 -preset slow -pix_fmt yuv420p -r 24"
CR="python3 ../../../tools/cajas3d_video.py"
f() { ffmpeg -y -loglevel error "$@"; }
$CR broll/clipA.mp4 cajas/plan3d-A.json $T/A.mp4
$CR broll/clipB.mp4 cajas/plan3d-B.json $T/B.mp4
$CR ../video-problema/clipT.mp4 cajas/plan3d-T86.json $T/C.mp4
for i in 1 3 4 6; do f -i "$K4/$i.mp4" -vf "setpts=PTS-STARTPTS,setsar=1" $E $T/$i.mp4; done
f -i $T/A.mp4 -vf "setpts=PTS-STARTPTS,setsar=1" $E $T/2a.mp4
f -i $T/B.mp4 -vf "setpts=PTS-STARTPTS,setsar=1" $E $T/2b.mp4
f -i $T/C.mp4 -vf "setpts=PTS-STARTPTS,setsar=1" $E $T/5.mp4
for i in 1 2a 2b 3 4 5 6; do echo "file '$T/$i.mp4'" >> $T/l.txt; done
f -f concat -safe 0 -i $T/l.txt -c copy $T/v.mp4
f -i $T/v.mp4 -i clip-intone-30nov-chica.mp4 -map 0:v -map 1:a -c:v copy -c:a copy -shortest clip-dependienta-v5-4k.mp4
echo ok clip-dependienta-v5-4k.mp4
