#!/usr/bin/env bash
# Montaje v6 del vídeo con dependienta (23/11/2026), 24 fps, 2160x3840, SIN textos ni audio (máster limpio).
# Igual que la v5 (tools/montaje_dependienta_v5.sh): orden 1, 2a, 2b, 3, 4, 5, 6 y los mismos fotogramas en el
# mismo sitio hasta el plano 5 (desde la revisión del 23/11: 687 fotogramas hablados + 79 del cierre de video_persona.py = 766),
# así la voz sigue cuadrando con los labios. Cambios, según la revisión independiente (D2, D4, D20, D21, D36, D38, D40):
#   - Piezas nuevas: planos 1 y 4 con las cajas del mostrador con texto real, la calle desenfocada y la «a» del neón
#     arreglada (v6/mostrador); 2a, 2b y 5 con la cara de la chica que habla y las cajas reales en 3D (v6/cajas, ya con
#     su largo final). 3 y 6 son los de la v4 (mejorados con tools/mejorar_4k.py).
#   - D2/D38 (color): los planos de Kling (2a, 2b, 5) se igualan a los de Intone de al lado con una curva fija por
#     canal (no parpadea) que lleva tres colores medidos a los de Intone: piel (bisenet), camiseta negra y blanco de las
#     cajas. Medido en 1080 (piel Lab, mediana de bisenet): antes Kling 54,7/17,9/22,6 (2a) y 58,2/19,8/25,8 (5) frente a
#     Intone 55-59/26-28/30-33; salto en los cortes ΔE 13,1 / 11,8 / 8,4 / 6,6, ahora 1,8 / 1,6 / 2,8 / 1,5. Grano y
#     nitidez ya iguales tras el cambio de cara (medidos en mejillas y camiseta), no se tocan.
#   - D36: 0-2,29 s, el plano 1 entra recortado x1,3 (con el acercamiento de cámara que ya trae, x1,3 -> x1,5): la cara
#     se ve más grande desde el primer fotograma; corte al plano abierto en «¡Normal!» (fotograma 56).
#   - D40: en 18,0 s (fotograma 432, justo antes de «Compramos por cantidad») corte a x1,25 del mismo plano abierto hasta
#     el primer plano (x1,25 y no más para que quepan la tarjeta «¿Por qué tan barato?» encima del pelo y los rótulos
#     «Pack USB-C / Pack Lightning» encima de las cajas, dentro de y 300-1240).
#   - D20 + D4: el primer plano del plano 4 (20,71 s) empezaba con una carcajada muda y luego la boca se cerraba de golpe
#     en el empalme de Intone (fotograma 504). Ahora el plano abierto x1,25 sigue hasta el 503 (los 6 últimos fotogramas,
#     sonrisa quieta y ya sin voz, a cámara lenta con flujo óptico) y el corte al primer plano cae justo en el empalme.
#     El segundo empalme (528, boca abierta -> cerrada) se tapa con un corte a x1,18 del primer plano.
#   - D21: el plano 6 iba 1 fotograma adelantado respecto a la voz (la voz de «Toque Comprar» está 0,500 s más tarde
#     que en clip-intone.mp4 y el plano se puso 11 fotogramas, 0,458 s, más tarde). Ahora 12: el primer fotograma
#     se repite una vez (fotograma 670-671, todavía sin voz).
#   - D20 del plano 3 (EXT2B=1, por defecto): el 2b sigue 15 fotogramas más (su final quieto, 78-117, a 40/55 de
#     velocidad con flujo óptico, sin voz) y el plano 3 empieza en su fotograma 15, cuando arranca «En Apple» (12,42 s),
#     en vez de con la carcajada muda de 12,04-12,42 s. Para que ese final no parezca una foto fija (D37), desde el
#     látigo (fotograma 218) la cámara se acerca despacio, x1,00 -> x1,06. EXT2B=0 deja el corte de la v5 (2b de 118).
#     El plan de rótulos de video_persona.py tiene que llevar el mismo corte (2b hasta 12,417 s).
# Revisión independiente de la v6 (23/11/2026):
#   - R2/R9/R5/T4: en 2b y 5 la chica de Kling (aun con la cara cambiada) no parece la misma que la de Intone (cara más
#     ancha, rizos, aros gruesos). Esos planos pasan a ser de producto, del cuello para abajo (las manos y las cajas):
#     2b x1,31 -> x1,36 con el borde de arriba fijo bajo el labio (y 445 de 1920; labio inferior en 428, barbilla 529,
#     así que solo asoma la barbilla bajo la cabecera de Reels) y el plano 5 x1,6 desde y 720 (barbilla como mucho en
#     688). En 2b la cámara se acerca despacio todo el plano (con arranque y llegada suaves) y lleva un pulso de cámara en
#     mano (dos senos de 0,4 y 0,9 Hz, unos ±4 px a 1080, y ±0,2° de giro; 0,2-0,7 px por fotograma, como el
#     acercamiento de cámara de Intone en el plano 1): ni el arranque (T4) ni el final quieto (R5) parecen una
#     foto fija. 2a (plano abierto, cara pequeña) se queda como estaba.
#   - T1: tras quitar «Dese prisa:» quedaban 1,64 s sin voz sobre los 21 primeros fotogramas del plano 5, casi quietos.
#     El plano 5 empieza en su fotograma 21 (cuando ella empieza a moverse) y el audio quita los mismos 0,875 s dentro del
#     silencio (audio/hacer.sh CORTE=24.40:25.275). Todo lo de después llega 21 fotogramas antes (el plano 6 y su voz
#     juntos, la sincronía no cambia): 687 fotogramas hablados; con --cierre 3.5417 el cierre dura 0,875 s más y el vídeo
#     sigue teniendo 766 fotogramas (687 - 6 + 85).
#   - R1/T3/T2/R7: en el primer plano del 4 Intone empieza cada frase con los labios cerrados 2 fotogramas después de que
#     arranque la voz (empalmes 504 y 529) y acaba con la boca abierta en silencio. Ahora se ve el fotograma n+2 de
#     Intone: 504-521 -> Intone 506-523; la sonrisa quieta 524-526 a media velocidad (522-527); el x1,18 entra en 528 con
#     Intone 530 (el primer fotograma asentado tras el empalme, sin el tirón de 528-529); 528-573 -> 530-575; y la
#     sonrisa final 576-583 a 0,8 de velocidad (574-583). En medio de las frases los labios van 2 fotogramas por
#     delante de antes (83 ms; la voz sigue dentro de lo que no se nota, <125 ms de retraso). El audio no se toca.
# 2.ª revisión de la v6 (23/11/2026):
#   - R2 (alta): en 2a (117-164) la chica de Kling salía con la cara grande (257-277 px, aros gruesos, rizos: otra mujer).
#     2a pasa también a plano de producto: x1,76 desde y 825 (barbilla como mucho en 809, fotograma 27, cuando asiente),
#     las dos cajas enteras de lado a lado con las manos. Ninguna boca a la vista mientras la voz habla sobre los planos de
#     Kling (2a, 2b y 5).
#   - N3 + R2 (que el 2a -> 2b no sea un salto en el mismo encuadre): 2b empieza con un inserto de la caja del adaptador
#     (x2,27 -> x2,31, el frente y «USB-C 20W Power Adapter» enteros mientras dice «adaptador de 20 W», 165-189) y corta,
#     en el arranque del giro y con «y cable.» (190), a las dos cajas x1,41 con los dos nombres enteros; ahí se queda,
#     acercándose un 1 % con el pulso de cámara en mano, mientras gira la caja y enseña la trasera. El borde izquierdo
#     queda entre el canto de la caja (x 140 en 1080, donde el compuesto deja las yemas recortadas en recta) y la «U»
#     (x 159); el inserto acaba a la izquierda de la caja del cable (x 631) para no cortarle el nombre.
#   - R3: las cuatro cajas del mostrador de los planos 1 y 4 tenían la forma de la IA (altas, todas iguales, pestañas
#     enormes) y cambiaban de forma al pasar a sus manos. v6/mostrador2 (mostrador2/cajas_reales.py) las cambia por las
#     cajas con las proporciones y los frentes reales (adaptador 0,92, cable 1,03 de ancho/alto, pestaña con el hueco del
#     euro), con el mismo ancho y la misma línea de arriba de la pestaña, más atrás en el mostrador (la base más alta;
#     solo se rellena madera del mostrador). El primer plano del 4 (139-225) es idéntico al de v6/mostrador.
#     MOSTRADOR=mostrador vuelve a las cajas de antes.
# 3.ª revisión de la v6 (23/11/2026; TERCERA=0 deja el montaje de la 2.ª):
#   - R2-tabs-closeup: en el primer plano del 4 (504-527) y en el plano 6 (649-686) asomaban abajo las pestañas de la IA
#     (anchas, sin el hueco del euro) justo después del plano abierto con las cajas reales. 504-527 se acerca x1,095 desde
#     el borde de arriba (las pestañas empezaban en y 1767), el x1,18 de 528-583 pasa a x1,22 (asomaba su filo) y el plano 6
#     va a x1,13 (pestañas desde y 1835), los dos con la línea del subtítulo (y 1110) fija para que la pastilla no tape
#     más cuello que antes. Ya no se ve ninguna pestaña en los primeros planos; el corte de 528 sigue siendo un acercamiento
#     (x1,11 y la cara sube).
#   - R2-2b-turn: el giro de la caja del adaptador en 2b (197-214) tenía fallos de composición en pausa. El barrido
#     empieza antes (cajas/latigo2b.py -> cajas/2b_latigo.mp4: 0-31, 5 de barrido, la trasera): 197-201 barrido, la
#     trasera desde 202, repartida hasta 297 a 0,78 -> 0,57 de velocidad (antes 1,0 y luego 0,73), sin tirones.
#   - R2-s5-counter: el plano 5 sale de cajas/5_mostrador.mp4 (cajas/mostrador5.py): madera del mostrador con el tono de
#     Intone y, delante, las tres cajas que no tiene en la mano (solo asoman pestañas y tapas, como en Intone).
# Mientras habla, cada fotograma de los planos 1, 3 y 4 abierto es el mismo fotograma de Intone que en la v5 (los recortes solo
# cambian el encuadre, nunca el tiempo) y el 6 va uno más tarde (D21): con el audio v6 la voz llega 23 ms (0,56
# fotogramas) después que en el clip de Intone en todos los planos hablados.
#
# Uso (desde pillatumovil/anuncios/2026-11/video-persona):
#   bash ../../../tools/montaje_dependienta_v6.sh CARPETA_V6 CARPETA_4K [SALIDA]   -> clip-dependienta-v6-4k.mp4
#     CARPETA_V6: con mostrador2/1.mp4, mostrador2/4.mp4 (o mostrador/ con MOSTRADOR=mostrador), cajas/2a.mp4, cajas/2b.mp4, cajas/5.mp4
#     CARPETA_4K: con 3.mp4 y 6.mp4 (los de la v4)
#   ESCALA=0.5 da un máster de 1080x1920 para revisar deprisa; HILOS (3), CRF (12) y PRESET (fast) son los de x264.
#   (cajas/2a.mp4 ya lleva el escaparate desenfocado de día, R6: cajas/ventana.py)
# Después (textos en 4K nativo; el audio nuevo, sin «Dese prisa», encima del vídeo ya terminado):
#   python3 ../../../tools/video_persona.py clip-dependienta-v6-4k.mp4 ../../../tools/fuentes rotulos-v6-4k.mp4 v6 0 2 \
#           --montaje rotulos-v6/plan_v6.json --subs rotulos-v6/subs_v6.json --foto pack-usbc-recorte.png \
#           --cierre 3.5417 --crf 17 --hilos 3                                  (687 - 6 + 85 = 766 fotogramas)
#   SIN_PRISA=1 CORTE=24.40:25.275 PREVIEW=0 bash .../v6/audio/hacer.sh         -> audio_v6_sin_prisa_corte.wav
#   ffmpeg -i rotulos-v6-4k.mp4 -i audio_v6_sin_prisa_corte.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -ar 48000 \
#          -movflags +faststart dependienta_v6_4k.mp4
#   (1080 para Meta: scale=1080:1920:flags=lanczos, libx264 High crf 19, -c:a copy; ver LEEME_v6.txt)
set -euo pipefail
V6=$1; K4=$2; SAL=${3:-clip-dependienta-v6-4k.mp4}
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
cat > $T/montar.py <<'PY'
import os, subprocess, sys
import cv2, numpy as np
from scipy.interpolate import PchipInterpolator
cv2.setNumThreads(2)
V6, K4, SAL = sys.argv[1:4]
ESC = float(os.environ.get('ESCALA', '1')); EXT2B = os.environ.get('EXT2B', '1') == '1'
W, H = round(2160 * ESC), round(3840 * ESC); E = W / 1080          # E: de coordenadas 1080x1920 a las de salida

# ---- color de Kling -> Intone: curva por canal (PCHIP, monótona) por tres anclas medidas en 1080 (RGB 0-255):
#      camiseta negra, piel (mediana de la piel de bisenet en la cara) y blanco de las cajas (8 % más claro).
#      Intone 1/3: camiseta 19/15,5/17, cajas del mostrador 239/227/227; Intone 4/6 (primeros planos): camiseta
#      23,3/18,8/20,6; blanco con el tono de Intone y la luz de la caja del plano 5 (231,9/220,2/220,2).
#      Piel: la de Intone junto a los cortes (Lab ~58/27,5/31,5, más clara que su media de 55: en los últimos y primeros
#      fotogramas de los planos 1, 3, 4 y 6 la cara está más cerca y más iluminada), para que el corte no salte de luz.
ANCLAS = {
    'k1': {'de': [(14.0, 15.5, 12.7), (173.5, 117.5, 90.5), (237.5, 228.2, 217.2)],     # 2a y 2b (misma luz)
           'a':  [(19.0, 15.5, 17.0), (199.2, 118.0, 83.4), (239.3, 227.0, 227.0)]},   # piel Lab 57,8/28,5/32,5
    'k5': {'de': [(18.7, 19.3, 16.0), (189.0, 125.0, 93.0), (228.3, 221.3, 216.3)],     # 5
           'a':  [(23.3, 18.8, 20.6), (199.0, 118.9, 84.8), (231.9, 220.2, 220.2)]},   # piel Lab 58/28/32
}
def lut(nombre):
    a = ANCLAS[nombre]; x16 = np.arange(65536, dtype=np.float64) / 257.0; out = []
    for c in range(3):
        xs = [0.0] + [p[c] for p in a['de']] + [255.0]; ys = [0.0] + [p[c] for p in a['a']] + [255.0]
        out.append(np.clip(PchipInterpolator(xs, ys)(x16) * 257.0 + 0.5, 0, 65535).astype(np.uint16))
    return out
LUT = {k: lut(k) for k in ANCLAS}

# ---- encuadres (coordenadas 1080x1920): zoom z con el punto (sx, sy) del plano en (ox, oy) de la salida
def M(z, sx, sy, ox, oy):
    return np.array([[z, 0, (ox - z * sx) * E], [0, z, (oy - z * sy) * E]], np.float64)
P1 = M(1.30, 530, 966, 540, 960)       # plano 1, 0-55: cara en el tercio de arriba, el móvil y las cajas debajo
P4A = M(1.25, 545, 888, 540, 960)      # plano 4 abierto, 432-503: cabe la tarjeta encima del pelo y las cajas debajo
P4C = M(1.18, 548, 1110, 548, 1110)    # primer plano del 4, 528-583: zoom con la línea del subtítulo fija
TERCERA = os.environ.get('TERCERA', '1') == '1'   # 3.ª revisión (23/11): sin pestañas de la IA en los primeros planos
P4B = M(1.095, 548, 0, 548, 0) if TERCERA else None   # 504-527: acercado desde arriba (pestañas desde y 1767 -> fuera)
if TERCERA: P4C = M(1.22, 548, 1110, 548, 1110)       # 528-583: x1,22 (asomaba el filo de las pestañas), misma línea
P6 = M(1.13, 548, 1110, 548, 1110) if TERCERA else None    # plano 6: pestañas desde y 1835 -> fuera; misma línea del
#   subtítulo fija (1110), así el cuello no baja hacia la pastilla (con el acercamiento desde arriba bajaba 58 px)
def MR(z, sx, sy, ox, oy, dx=0.0, dy=0.0, gr=0.0):
    """Como M, con un giro de gr grados alrededor del centro de la salida y un desplazamiento (dx, dy) de la salida."""
    c, s_ = np.cos(np.radians(gr)), np.sin(np.radians(gr)); R = np.array([[c, -s_], [s_, c]]) * z
    t = np.array([ox + dx, oy + dy]) - R @ np.array([sx, sy])
    return np.hstack([R, (t * E)[:, None]]).astype(np.float64)
P2A = M(1.76, 579, 825 + 960 / 1.76, 540, 960)   # 2a de producto (2.ª revisión, R2): de y 825 (barbilla <= 809) abajo
def pulso(o, ax=1.0):
    """Pulso de cámara en mano (dos senos de 0,4 y 0,9 Hz; ax escala el horizontal): (dx, dy) en px de salida y giro."""
    t = (o - 165) / 24
    dx = ax * (3.4 * np.sin(2 * np.pi * 0.4 * t + 0.7) + 1.5 * np.sin(2 * np.pi * 0.9 * t + 2.1))
    dy = 3.0 * np.sin(2 * np.pi * 0.37 * t + 1.9) + 1.3 * np.sin(2 * np.pi * 0.83 * t + 0.4)
    return dx, dy, 0.2 * np.sin(2 * np.pi * 0.31 * t + 1.2)
def P2B(o):
    """2b (2.ª revisión, R2/N3): 165-189 inserto de la caja del adaptador (x2,27 -> x2,31, el frente entero mientras dice
    «adaptador de 20 W»); corte en el arranque del giro (190, «y cable.») a las dos cajas x1,41 (los dos nombres enteros),
    que se acerca un 1 % hasta el final. Borde izquierdo en x 144-146, entre el canto de la caja (140, con las yemas
    recortadas del compuesto) y la «U» de «USB-C» (159); en el inserto, el derecho antes de la caja del cable (631)."""
    dx, dy, gr = pulso(o, 0.5)
    if o < 190:
        u = (o - 165) / 24; u = u * u * (3 - 2 * u); z = 2.27 + 0.04 * u
        return MR(z, 146 + 540 / z, 1017 + (960 - 530) / z, 540, 960, dx, dy, gr)   # pestaña (y 1017) en y 530
    u = np.clip((o - 190) / 107, 0, 1); u = u * u * (3 - 2 * u)
    xl, xr = 144 + 1 * u, 910 - 7 * u; z = 1080 / (xr - xl)          # «USB-C» desde 159, «...Cable (1 m)» hasta 890
    return MR(z, (xl + xr) / 2, 547 + 960 / 1.41, 540, 960, dx, dy, gr)   # arriba en y 547 (barbilla en 529)
P5 = M(1.60, 530, 1920 - 960 / 1.60, 540, 960)   # plano 5 de producto: de y 720 (barbilla <= 688) al mostrador

# ---- de qué fotograma de qué plano sale cada fotograma de salida: (pieza, posición, curva, encuadre)
MOS = os.environ.get('MOSTRADOR', 'mostrador2')   # R3 (2.ª revisión): cajas del mostrador con la forma real (mostrador2)
PIEZAS = {'1': f'{V6}/{MOS}/1.mp4', '2a': f'{V6}/cajas/2a.mp4', '2b': f'{V6}/cajas/2b.mp4', '3': f'{K4}/3.mp4',
          '4': f'{V6}/{MOS}/4.mp4', '5': f'{V6}/cajas/5.mp4', '6': f'{K4}/6.mp4'}
if TERCERA:   # 2b con el barrido antes (cajas/latigo2b.py) y el plano 5 con las cajas en el mostrador (cajas/mostrador5.py)
    PIEZAS['2b'] = f'{V6}/cajas/2b_latigo.mp4'; PIEZAS['5'] = f'{V6}/cajas/5_mostrador.mp4'
LARGO = {'1': 117, '2a': 48, '2b': 118, '3': 75, '4': 226, '5': 86, '6': 38}
mapa = []
for n in range(117): mapa.append(('1', n, None, P1 if n < 56 else None))
for n in range(48): mapa.append(('2a', n, 'k1', P2A))
if EXT2B:   # 2b: 0-77 igual; 78-117 (final quieto) a 40/55 de velocidad -> 133 fotogramas; el 3 desde su fotograma 15
    pos2b = list(range(78)) + [78 + k * 39 / 54 for k in range(55)]
    if TERCERA:   # 2b_latigo.mp4: 0-31 igual, 32-36 barrido (197-201), trasera 37-101 en 202-297 (96 fotogramas): la
        # velocidad baja poco a poco de 0,78 a 0,57 (suma 64), en vez de 1,0 y luego 0,73 con un cambio brusco en 243
        v = np.linspace(0.78, 0.78 - 2 * (0.78 - 64 / 95), 95)
        pos2b = list(range(37)) + [float(x) for x in 37 + np.concatenate([[0.0], np.cumsum(v)])]
        pos2b[-1] = 101.0
        assert len(pos2b) == 133 and abs(pos2b[-1] - 101) < 1e-9, (len(pos2b), pos2b[-1])
    for o, p in enumerate(pos2b, 165):   # 2b de producto (R2): ver P2B
        mapa.append(('2b', p, 'k1', P2B(o)))
    for n in range(15, 75): mapa.append(('3', n, None, None))
else:
    for n in range(118): mapa.append(('2b', n, 'k1', P2B(165 + n)))
    for n in range(75): mapa.append(('3', n, None, None))
for n in range(226):
    o = 358 + n
    if o < 432: mapa.append(('4', n, None, None))
    elif o < 491: mapa.append(('4', n, None, P4A))
    elif o < 504: mapa.append(('4', 133 + (o - 491) * 5 / 12, None, P4A))   # 133..138 en 13 fotogramas (sin voz)
    # primer plano (R1/T3/T2/R7): Intone n+2 (índice del plano 4 = Intone - 358)
    elif o < 522: mapa.append(('4', o + 2 - 358, None, P4B))                # 504-521 -> Intone 506-523
    elif o < 528: mapa.append(('4', 166 + (o - 522) * 0.4, None, P4B))      # 522-527 -> sonrisa 524-526 a media velocidad
    elif o < 574: mapa.append(('4', o + 2 - 358, None, P4C))                # x1,18 desde 528 = Intone 530 (asentado)
    else: mapa.append(('4', 218 + (o - 574) * 7 / 9, None, P4C))            # 574-583 -> sonrisa final 576-583 (0,8x)
for n in range(21, 86): mapa.append(('5', n, 'k5', P5))                     # T1: desde el 21 (antes, casi quieto)
for n in range(38): mapa.append(('6', max(0, n - 1), None, P6))
assert len(mapa) == 687, len(mapa)

# ---- lectura (RGB de 16 bits, BT.709, redondeo exacto) y escritura
def lector(f):
    vf = f'scale={W}:{H}:flags=lanczos+accurate_rnd+full_chroma_int:in_color_matrix=bt709:in_range=tv,format=rgb48le'
    return subprocess.Popen(['ffmpeg', '-v', 'error', '-threads', '2', '-i', f, '-vf', vf, '-f', 'rawvideo', '-'], stdout=subprocess.PIPE)
class Pieza:
    def __init__(s, f): s.p = lector(f); s.n = -1; s.cache = {}
    def get(s, i):
        while s.n < i:
            b = s.p.stdout.read(W * H * 6); assert len(b) == W * H * 6, 'faltan fotogramas'
            s.n += 1; s.cache[s.n] = np.frombuffer(b, np.uint16).reshape(H, W, 3)
            for k in [k for k in s.cache if k < s.n - 2]: del s.cache[k]
        return s.cache[i]
def intermedio(a, b, t):
    """Fotograma entre a y b (t de 0 a 1) con flujo óptico DIS a 1/4: cada uno se lleva a su sitio y se mezclan."""
    q = 4; sm = lambda x: cv2.cvtColor((cv2.resize(x, (W // q, H // q), interpolation=cv2.INTER_AREA) >> 8).astype(np.uint8), cv2.COLOR_RGB2GRAY)
    dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
    fab = dis.calc(sm(a), sm(b), None); fba = dis.calc(sm(b), sm(a), None)
    up = lambda f: cv2.resize(f, (W, H), interpolation=cv2.INTER_LINEAR) * q
    gx, gy = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
    fab, fba = up(fab), up(fba)
    wa = cv2.remap(a.astype(np.float32), gx - t * fab[..., 0], gy - t * fab[..., 1], cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    wb = cv2.remap(b.astype(np.float32), gx - (1 - t) * fba[..., 0], gy - (1 - t) * fba[..., 1], cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    return np.clip((1 - t) * wa + t * wb + 0.5, 0, 65535).astype(np.uint16)

enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb48le', '-s', f'{W}x{H}', '-r', '24', '-i', '-',
                        '-vf', 'scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd+full_chroma_int,format=yuv420p',
                        '-c:v', 'libx264', '-crf', os.environ.get('CRF', '12'), '-preset', os.environ.get('PRESET', 'fast'), '-threads', os.environ.get('HILOS', '3'),
                        '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv',
                        '-an', SAL], stdin=subprocess.PIPE)
abiertas = {}
for o, (pz, pos, curva, enc_m) in enumerate(mapa):
    if pz not in abiertas:
        for k in list(abiertas): abiertas.pop(k).p.kill()
        abiertas[pz] = Pieza(PIEZAS[pz])
    P = abiertas[pz]; i0 = int(np.floor(pos + 1e-9)); t = pos - i0
    fr = P.get(i0) if t < 1e-6 else intermedio(P.get(i0), P.get(i0 + 1), t)
    if curva:
        L = LUT[curva]; fr = np.dstack([L[c][fr[..., c]] for c in range(3)])
    if enc_m is not None:
        fr = cv2.warpAffine(fr, enc_m, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
    enc.stdin.write(np.ascontiguousarray(fr).tobytes())
    if o % 48 == 0: print(f'  {o}/687', flush=True)
for k in list(abiertas): abiertas.pop(k).p.kill()
enc.stdin.close(); enc.wait()
print('ok', SAL, len(mapa), 'fotogramas')
PY
nice -n 5 python3 $T/montar.py "$V6" "$K4" "$SAL"
N=$(ffprobe -v error -select_streams v:0 -count_packets -show_entries stream=nb_read_packets -of csv=p=0 "$SAL")
[ "$N" = 687 ] || { echo "ERROR: $N fotogramas (tienen que ser 687)"; exit 1; }
echo "ok $SAL ($N fotogramas; con el cierre de video_persona.py --cierre 3.5417: 687 - 6 + 85 = 766)"
