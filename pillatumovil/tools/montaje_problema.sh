#!/usr/bin/env bash
# Montaje del anuncio «problema → solución» (13/11/2026), a 24 fps y 2160x3840.
# Guion y planos: anuncios/2026-11/video-problema/LEEME.md. La voz va por encima (nadie habla).
#   1) 0-2,83 s     cliente fastidiado con el móvil sin batería (clipH, Kling 2df2a782)
#   2) 2,83-5,42 s  detalle del cargador barato (recorte de frameH.png ampliado, con zoom lento)
#   3) 5,42-7,63 s  cliente, sigue
#   4) 7,63-13,21 s la tienda (plano abierto ya mejorado a 4K: CARPETA_4K/4.mp4)
#   5) 13,21-17,21 s la chica enseña las dos cajas (video-persona/broll/clipA.mp4)
#   6) 17,21-22,25 s gira la caja del cargador con las dos manos (clipT, Kling 0ca6e566)
#   7) 22,25-26,58 s entrega el pack en el mostrador (video-persona/broll/clipC.mp4)
#   8) 26,58-33 s   fondo de la tarjeta de cierre (clipC, que video_problema.py desenfoca)
#
# Uso (desde pillatumovil/anuncios/2026-11/video-problema):
#   bash ../../../tools/montaje_problema.sh CARPETA_4K MODELOS_DIR
# Salida: montaje-problema-4k.mp4. Después:
#   python3 ../../../tools/video_problema.py montaje-problema-4k.mp4 FUENTES SALIDA.mp4 2
set -euo pipefail
K4=$1; MOD=$2
T=$(mktemp -d)
A=2160; B=3840
E="-an -c:v libx264 -crf 14 -preset slow -pix_fmt yuv420p -r 24"
KL="scale=-2:$B:flags=lanczos,crop=$A:$B,setsar=1"          # planos Kling (1080 px de ancho)
P=../video-persona/broll
f() { ffmpeg -y -loglevel error "$@"; }
f -i clipH.mp4 -vf "trim=start_frame=0:end_frame=68,setpts=PTS-STARTPTS,$KL" $E $T/1.mp4
python3 ../../../tools/foto_4k.py frameH.png $T/det.png "$MOD" 760 1337 1520 2688
f -loop 1 -framerate 24 -i $T/det.png -vf "format=rgb24,scale=w='$A*(1+0.10*t/2.6)':h='$B*(1+0.10*t/2.6)':eval=frame:flags=bicubic,crop=$A:$B:'(in_w-out_w)*0.8':'(in_h-out_h)*0.55',setsar=1,format=yuv420p" -frames:v 62 $E $T/2.mp4
f -i clipH.mp4 -vf "trim=start_frame=68:end_frame=121,setpts=PTS-STARTPTS,$KL" $E $T/3.mp4
f -i "$K4/4.mp4" -vf "trim=start_frame=0:end_frame=134,setpts=PTS-STARTPTS,setsar=1" $E $T/4.mp4
f -i $P/clipA.mp4 -vf "trim=start_frame=0:end_frame=96,setpts=PTS-STARTPTS,$KL" $E $T/5.mp4
f -i clipT.mp4 -vf "trim=start_frame=0:end_frame=121,setpts=PTS-STARTPTS,$KL" $E $T/6.mp4
f -i $P/clipC.mp4 -vf "trim=start_frame=0:end_frame=104,setpts=PTS-STARTPTS,$KL" $E $T/7.mp4
# fondo del cierre: clipC sigue, vuelve hacia atrás y avanza otra vez (va desenfocado)
f -i $P/clipC.mp4 -vf "trim=start_frame=104:end_frame=121,setpts=PTS-STARTPTS,$KL" $E $T/8a.mp4
f -i $P/clipC.mp4 -vf "reverse,$KL" $E $T/8b.mp4
f -i $P/clipC.mp4 -vf "trim=start_frame=0:end_frame=24,setpts=PTS-STARTPTS,$KL" $E $T/8c.mp4
for i in 1 2 3 4 5 6 7 8a 8b 8c; do echo "file '$T/$i.mp4'" >> $T/l.txt; done
f -f concat -safe 0 -i $T/l.txt -c copy $T/v.mp4
f -i $T/v.mp4 -i voz-problema-elena.mp3 -filter_complex "[1:a]apad=whole_dur=33.5[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest montaje-problema-4k.mp4
echo ok montaje-problema-4k.mp4
