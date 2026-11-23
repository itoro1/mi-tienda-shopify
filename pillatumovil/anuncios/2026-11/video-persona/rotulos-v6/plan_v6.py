# Uso: python3 plan_v6.py plan_v6.json   (escribe plan_v6.json y subs_v6.json; --sin-ext2b si el montaje se hizo con EXT2B=0)
"""Plan de rótulos (--montaje) y subtítulos (--subs) de video_persona.py v6 para el máster v6 con los recortes."""
import json, sys
EXT2B = '--sin-ext2b' not in sys.argv   # como el montaje: 2b hasta 12,417 s (EXT2B=1)
OUT = sys.argv[1]
f = lambda n: round(n / 24 - 0.001, 4)          # borde de plano un pelo antes del fotograma n (t = n/24)
# encuadres del montaje (coordenadas 1080x1920): salida = z*(punto - s) + o
P4A = dict(z=1.25, sx=545, sy=888, ox=540, oy=960)
def tr(P, x, y): return P['z'] * (x - P['sx']) + P['ox'], P['z'] * (y - P['sy']) + P['oy']
C3 = 298 if EXT2B else 283          # primer fotograma del plano 3
# rótulo IA: la pastilla mide 38 px; arriba en y 300 y abajo en 1202, así va entera dentro de y 300-1240.
planos = [
    {'de': 0.0,      'a': f(56),  'sub': 1110, 'ia': ['centro', 1202]},                 # 1 recortado x1,3 (móvil y cajas)
    {'de': f(56),    'a': f(117), 'sub': 1098, 'ia': ['izq', 300]},                     # 1 abierto
    {'de': f(117),   'a': f(165), 'sub': 892, 'chip': 830, 'ia': ['der', 300]},         # 2a (30 px más abajo que en v4: el chip rozaba la barbilla)
    {'de': f(165),   'a': f(C3),  'sub': 618, 'chip': 556, 'ia': ['der2', 300]},        # 2b de producto (24/11, R2): las cajas desde y 737
    {'de': f(C3),    'a': f(358), 'sub': 1156, 'ia': ['izq', 300], 'neon': [380, 420]}, # 3
    {'de': f(358),   'a': f(432), 'sub': 860, 'ia': ['centro', 956]},                   # 4 abierto
    {'de': f(432),   'a': f(504), 'sub': 900, 'ia': ['centro', 996]},                   # 4 abierto recortado x1,25
    {'de': f(504),   'a': f(528), 'sub': 1110, 'ia': ['centro', 1202]},                 # 4 primer plano
    {'de': f(528),   'a': f(584), 'sub': 1110, 'ia': ['centro', 1202]},                 # 4 primer plano x1,18
    {'de': f(584),   'a': f(649), 'sub': 306, 'ia': ['centro', 1202]},                  # 5 de producto (24/11): caja en y 411-1115
    {'de': f(649),   'a': 999,    'sub': 1110, 'ia': ['centro', 1202]},                 # 6 (21 fotogramas antes: corte T1)
]
# tarjeta: borde de abajo (cambio de altura justo en el corte 3 -> 4, fotograma 358: en v4/v5 iba 1 fotograma tarde).
# Plano 3 fijo en 464 (arriba en 338, justo debajo del rótulo IA de y 300-338); plano 4 abierto sigue el acercamiento de la cámara tapando el neón (como en v4);
# la pregunta entra a 17,55 s (fundido de 0,38 s, acaba antes del corte); en el corte x1,25 (18,0 s) la tarjeta salta
# con el encuadre a 456 y baja a 444 cuando ella sube la cabeza (arranque del pelo en ese encuadre, MODNet: 490 -> 450).
tarjeta = {'de': f(C3), 'a': f(504), 'beat2': 15.15, 'pregunta': 17.55,
           'y': [[f(C3), 464], [14.875, 464], [f(358), 563], [17.45, 529], [f(432), 521.4], [18.0, 456], [19.85, 456], [20.35, 444], [21.0, 444]]}
# packs: [t, x0, x1, y_pestaña] USB-C y Lightning (v4, medidos en el plano abierto); desde 18,0 s, en el encuadre x1,25,
# con los corchetes dentro de x 96-984 y el de abajo como mucho en y 1238
kf = [[14.95, 152, 510, 1086, 544, 904, 1084], [16.45, 134, 510, 1092, 544, 924, 1090], [17.95, 116, 508, 1098, 544, 944, 1094],
      [19.45, 96, 508, 1102, 544, 964, 1100], [20.45, 84, 508, 1106, 544, 976, 1104], [20.75, 82, 508, 1107, 544, 978, 1105]]
def interp(t):
    for a, b in zip(kf, kf[1:]):
        if a[0] <= t <= b[0]:
            u = (t - a[0]) / (b[0] - a[0]); return [a[i] + (b[i] - a[i]) * u for i in range(1, 7)]
    return kf[-1][1:]
def recorte(t):
    ux0, ux1, uy, lx0, lx1, ly = interp(min(t, 20.75))
    a0, ay = tr(P4A, ux0, uy); a1, _ = tr(P4A, ux1, uy); b0, by = tr(P4A, lx0, ly); b1, _ = tr(P4A, lx1, ly)
    cl = lambda x: max(96, min(984, x))
    return [round(t, 4), round(cl(a0), 1), round(cl(a1), 1), round(min(ay, 1238), 1), round(cl(b0), 1), round(cl(b1), 1), round(min(by, 1238), 1)]
pk = [k for k in kf if k[0] < 17.99] + [[f(432)] + interp(f(432))[:]]
pk += [recorte(18.0), recorte(19.45), recorte(20.45), recorte(21.0)]
packs = {'de': 16.95, 'a': f(504), 'kf': pk}
json.dump({'planos': planos, 'chip': [4.9, f(C3)], 'tarjeta': tarjeta, 'packs': packs}, open(OUT, 'w'), indent=1, ensure_ascii=False)
# cambios de subtítulo en los cortes (4,87 / 18,0 / 24,33 / 27,9 s), no 1-2 fotogramas antes o después.
# plano 3 (12,42-15,2 s): sin subtítulo; en ese primer plano la barbilla llega a y 1150-1200 y la pastilla la tapaba,
# y la tarjeta ya dice lo mismo («En Apple: 38,00 €»).
# subtítulos: los de v6 (SUBS_V3 con «¡Normal!», «y ganamos menos.» a 19,45 s y el precio en oro) sin «Dese prisa:»;
# «Este precio acaba» / «el 30 de noviembre.» con los tiempos de la voz (faster-whisper sobre voz-frase-30nov.mp3:
# «Este» 25,53 s, «el» 26,51 s en la línea de clip-intone-30nov-chica).
# 24/11 (revisión): «laborables» en el subtítulo del plazo (como en el cierre: «llega a su casa en 24-48 h
# laborables»); y el corte T1: el audio quita 24,40-25,275 s (0,875 s sin voz) y el montaje los 21 primeros
# fotogramas del plano 5, así que lo de después de 24,4 s va 0,875 s antes.
CORTE = 0.875
subs = [['¿Su iPhone vino', 0.0], ['sin cargador?', 1.0], ['¡Normal!', 2.3], ['Apple ya no lo pone.', 3.2],
        ['Aquí tiene los dos:', 4.87], ['adaptador de 20 W', 6.3], ['y cable.', 7.9], ['Originales de Apple,', 8.9],
        ['en su caja sin abrir.', 10.3], ['', 12.4], ['Aquí, *18,99 €*.', 15.2], ['Compramos por cantidad', 18.0],
        ['y ganamos menos.', 19.45], ['Envío gratis', 21.0], ['en 24-48 h laborables.', 22.0], ['', 24.33],
        ['Este precio acaba', 25.55 - CORTE], ['el 30 de noviembre.', 26.5 - CORTE], ['', f(649)],
        ['Toque «Comprar».', 28.28 - CORTE]]
json.dump(subs, open(OUT.replace('plan', 'subs'), 'w'), indent=0, ensure_ascii=False)
print('ok', OUT)
