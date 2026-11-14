#!/usr/bin/env bash
# Montaje del anuncio «problema → solución», a 24 fps y 2160x3840.
# Guion y planos: anuncios/2026-11/video-problema/LEEME.md. La voz va por encima: NADIE mueve la boca.
# v2 (14/11/2026): fuera el plano abierto de la tienda, que venía de una toma en la que la chica
# hablaba otra frase y la boca no coincidía con la voz. Se probó a dejarle la boca quieta copiando
# la de otro fotograma, pero en los fotogramas con sonrisa quedaba raro. Ahora todo son planos
# donde ella no habla, más dos planos de detalle de la caja.
#   1) 0-2,83 s      cliente fastidiado con el móvil sin batería (clipH)
#   2) 2,83-5,42 s   detalle del cargador barato (recorte de frameH.png, zoom lento)
#   3) 5,42-7,63 s   cliente, sigue
#   4) 7,63-9,71 s   detalle: la caja original en sus manos (recorte de frameT.png)
#   5) 9,71-12,21 s  la chica con las dos cajas junto al escaparate (clipA) + cartel de Apple
#   6) 12,21-16,71 s entrega el pack en el mostrador, con el letrero «pillatumovil» (clipC)
#   7) 16,71-21,75 s gira la caja con las dos manos (clipT) + cartel 18,99 €
#   8) 21,75-24,29 s detalle: la parte de atrás real de la caja (recorte de frameT_trasera.png)
#   9) 24,29-33 s    fondo de la tarjeta de cierre (clipC; video_problema.py lo desenfoca)
#
# Uso (desde pillatumovil/anuncios/2026-11/video-problema):
#   bash ../../../tools/montaje_problema.sh MODELOS_DIR
# Salida: montaje-problema-4k.mp4. Después:
#   python3 ../../../tools/video_problema.py montaje-problema-4k.mp4 FUENTES SALIDA.mp4 2
set -euo pipefail
MOD=$1
T=$(mktemp -d)
A=2160; B=3840
E="-an -c:v libx264 -crf 14 -preset slow -pix_fmt yuv420p -r 24"
KL="scale=-2:$B:flags=lanczos,crop=$A:$B,setsar=1"          # planos Kling (1080 px de ancho)
P=../video-persona/broll
f() { ffmpeg -y -loglevel error "$@"; }
# detalle con zoom lento: FOTO X0 Y0 X1 Y1 FOTOGRAMAS ANCLA_X ANCLA_Y SALIDA
detalle() {
  python3 ../../../tools/foto_4k.py "$1" $T/d.png "$MOD" $2 $3 $4 $5
  local d; d=$(python3 -c "print($6/24)")
  f -loop 1 -framerate 24 -i $T/d.png -vf "format=rgb24,scale=w='$A*(1+0.09*t/$d)':h='$B*(1+0.09*t/$d)':eval=frame:flags=bicubic,crop=$A:$B:'(in_w-out_w)*$7':'(in_h-out_h)*$8',setsar=1,format=yuv420p" -frames:v $6 $E "$9"
}
f -i clipH.mp4 -vf "trim=start_frame=0:end_frame=68,setpts=PTS-STARTPTS,$KL" $E $T/1.mp4
detalle frameH.png 760 1337 1520 2688 62 0.8 0.55 $T/2.mp4
f -i clipH.mp4 -vf "trim=start_frame=68:end_frame=121,setpts=PTS-STARTPTS,$KL" $E $T/3.mp4
detalle frameT.png 392 950 1152 2301 50 0.5 0.45 $T/4.mp4
f -i $P/clipA.mp4 -vf "trim=start_frame=0:end_frame=60,setpts=PTS-STARTPTS,$KL" $E $T/5.mp4
f -i $P/clipC.mp4 -vf "trim=start_frame=0:end_frame=108,setpts=PTS-STARTPTS,$KL" $E $T/6.mp4
f -i clipT.mp4 -vf "trim=start_frame=0:end_frame=121,setpts=PTS-STARTPTS,$KL" $E $T/7.mp4
detalle frameT_trasera.png 392 950 1152 2301 61 0.5 0.45 $T/8.mp4
# fondo del cierre: clipC sigue, vuelve hacia atrás y avanza otra vez (va desenfocado)
f -i $P/clipC.mp4 -vf "trim=start_frame=108:end_frame=121,setpts=PTS-STARTPTS,$KL" $E $T/9a.mp4
f -i $P/clipC.mp4 -vf "reverse,$KL" $E $T/9b.mp4
f -i $P/clipC.mp4 -vf "trim=start_frame=0:end_frame=90,setpts=PTS-STARTPTS,$KL" $E $T/9c.mp4
for i in 1 2 3 4 5 6 7 8 9a 9b 9c; do echo "file '$T/$i.mp4'" >> $T/l.txt; done
f -f concat -safe 0 -i $T/l.txt -c copy $T/v.mp4
f -i $T/v.mp4 -i voz-problema-elena.mp3 -filter_complex "[1:a]apad=whole_dur=33.5[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest montaje-problema-4k.mp4
echo ok montaje-problema-4k.mp4
