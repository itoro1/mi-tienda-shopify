#!/usr/bin/env bash
# Montaje del anuncio «problema → solución», a 24 fps y 2160x3840.
# Guion y planos: anuncios/2026-11/video-problema/LEEME.md. La voz va por encima: NADIE mueve la boca.
# v2 (14/11/2026): fuera el plano abierto de la tienda, que venía de una toma en la que la chica
# hablaba otra frase y la boca no coincidía con la voz. Se probó a dejarle la boca quieta copiando
# la de otro fotograma, pero en los fotogramas con sonrisa quedaba raro. Ahora todo son planos
# donde ella no habla, más dos planos de detalle de la caja.
#   1) 0-2,83 s      cliente fastidiado con el móvil sin batería (clipH)
#   2) 2,83-5,42 s   detalle del cargador barato (frameD.png, foto de cerca, zoom lento)
#   3) 5,42-7,63 s   cliente, sigue
#   4) 7,63-10,21 s  detalle: la caja original en sus manos (recorte de frameT.png) + cartel de Apple al final
#   5) 10,21-12,21 s la chica con las dos cajas junto al escaparate (clipA) + cartel de Apple
#   6) 12,21-16,00 s las dos cajas reales girando 360 grados (plano de producto)
#   7) 16,00-21,04 s gira la caja con las dos manos (clipT) + cartel 18,99 €
#   8) 21,04-24,29 s detalle: la parte de atrás real de la caja (recorte de frameT.png)
#   9) 24,29-33 s    fondo de la tarjeta de cierre (clipC; video_problema.py lo desenfoca)
#
# v5 (16/11/2026): LA CAJA REAL EN 3D. El dueño: «cuando la chica coge nuestros cargadores se ven las cajas
# mal hechas, no se ve un producto real»; y de la v4 (foto plana pegada): «no se ve real y arriba genera algo
# borrado […] quiero que estudies los 360 grados que tiene la caja». Ahora:
#   - planos 4, 5, 7 y 8: la caja que dibujó la IA se cambia por la caja real en 3D (tools/cajas3d_video.py,
#     planes en cajas/plan3d-*.json), con la camiseta de detrás reconstruida con tela de verdad;
#   - plano 6: ya no es la entrega en el mostrador (ahí detrás hay madera y brazo y el arreglo se notaba):
#     son las dos cajas reales girando 360 grados (tools/caja3d_giro.py), sin nada de IA;
#   - de clipA solo valen los 48 primeros fotogramas (después sube una caja a la altura del cuello).
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
CR="python3 ../../../tools/cajas3d_video.py"
# detalle con zoom lento y la caja real: FOTO X0 Y0 X1 Y1 PLAN FOTOGRAMAS ANCLA_X ANCLA_Y SALIDA
detalle() {
  python3 ../../../tools/foto_4k.py "$1" $T/d.png "$MOD" $2 $3 $4 $5
  f -i $T/d.png -vf "scale=$A:$B:flags=lanczos" $T/d2.png
  $CR $T/d2.png "$6" $T/d3.png
  local d; d=$(python3 -c "print($7/24)")
  f -loop 1 -framerate 24 -i $T/d3.png -vf "format=rgb24,scale=w='$A*(1+0.09*t/$d)':h='$B*(1+0.09*t/$d)':eval=frame:flags=bicubic,crop=$A:$B:'(in_w-out_w)*$8':'(in_h-out_h)*$9',setsar=1,format=yuv420p" -frames:v $7 $E "${10}"
}
f -i clipH.mp4 -vf "trim=start_frame=0:end_frame=68,setpts=PTS-STARTPTS,$KL" $E $T/1.mp4
# v3 (14/11): el detalle del enchufe ya no es un recorte ampliado de frameH (se veía poco real):
# es una foto propia hecha de cerca (frameD.png, job 2e9bb0c1), a su tamaño, sin superresolución.
f -loop 1 -framerate 24 -i frameD.png -vf "format=rgb24,scale=w='$A*(1+0.09*t/2.583)':h='$B*(1+0.09*t/2.583)':eval=frame:flags=lanczos,crop=$A:$B:'(in_w-out_w)*0.55':'(in_h-out_h)*0.45',setsar=1,format=yuv420p" -frames:v 62 $E $T/2.mp4
f -i clipH.mp4 -vf "trim=start_frame=68:end_frame=121,setpts=PTS-STARTPTS,$KL" $E $T/3.mp4
detalle frameT.png 392 950 1152 2301 cajas/plan3d-detalle-frente.json 62 0.5 0.45 $T/4.mp4
# planos con la chica: primero se cambian las cajas (ya salen a 2160x3840) y luego se recodifican igual que el resto
$CR $P/clipA.mp4 cajas/plan3d-A.json $T/A.mp4
python3 ../../../tools/caja3d_giro.py $T/G.mp4 91
$CR clipT.mp4 cajas/plan3d-T.json $T/T.mp4
f -i $T/A.mp4 -vf "setpts=PTS-STARTPTS,setsar=1" $E $T/5.mp4
f -i $T/G.mp4 -vf "setpts=PTS-STARTPTS,setsar=1" $E $T/6.mp4
f -i $T/T.mp4 -vf "setpts=PTS-STARTPTS,setsar=1" $E $T/7.mp4
detalle frameT.png 392 950 1152 2301 cajas/plan3d-detalle-trasera.json 78 0.5 0.45 $T/8.mp4
# fondo del cierre: clipC sigue, vuelve hacia atrás y avanza otra vez (va desenfocado)
f -i $P/clipC.mp4 -vf "trim=start_frame=108:end_frame=121,setpts=PTS-STARTPTS,$KL" $E $T/9a.mp4
f -i $P/clipC.mp4 -vf "reverse,$KL" $E $T/9b.mp4
f -i $P/clipC.mp4 -vf "trim=start_frame=0:end_frame=90,setpts=PTS-STARTPTS,$KL" $E $T/9c.mp4
for i in 1 2 3 4 5 6 7 8 9a 9b 9c; do echo "file '$T/$i.mp4'" >> $T/l.txt; done
f -f concat -safe 0 -i $T/l.txt -c copy $T/v.mp4
f -i $T/v.mp4 -i voz-problema-elena.mp3 -filter_complex "[1:a]apad=whole_dur=33.5[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest montaje-problema-4k.mp4
echo ok montaje-problema-4k.mp4
