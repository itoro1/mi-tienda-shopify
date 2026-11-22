"""Fotos del producto que van impresas en la cara de delante de las cajas, hechas con nuestro propio 3D.
Uso: python3 producto3d_arte.py SALIDA_DIR   ->  producto-cargador.png y producto-cable.png (fondo transparente)."""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, producto3d as P

SAL = sys.argv[-1]; os.makedirs(SAL, exist_ok=True)


def estudio():
    sc = P.motor(1400, 2000, muestras=128); sc.render.film_transparent = True; sc.view_settings.exposure = -0.5
    P.fondo((1, 1, 1), 0.35)
    P.luz_area('clave', (-0.25, -0.35, 0.35), (0, 0, 0.03), 6, (0.5, 0.5))
    P.luz_area('relleno', (0.3, -0.25, 0.12), (0, 0, 0.03), 2.5, (0.5, 0.5))
    P.luz_area('arriba', (0.0, 0.05, 0.45), (0, 0, 0.03), 3, (0.4, 0.4))
    return sc


# adaptador: clavijas arriba, a tres cuartos (girado; v5: 58°) y visto desde arriba, como en la caja real; clavijas en
# cromo de estudio (22/11: con metal normal salían manchas que parecían camuflaje y el ángulo era casi de frente)
# 22/11 (revisión): las clavijas salían pálidas con reflejos en rectángulo (las luces de área): casi sin reflejo directo.
# 22/11 v4: la rampa oscura las dejó color grafito; en la caja real y en la foto MHJE3 son de cromo claro: cantos
# blancos, una sola banda oscura y un brillo blanco en la punta redondeada (cupula).
# Además el plástico salía quemado a blanco plano (vista 'Standard'): menos exposición y el cromo con más brillo.
# 22/11 v5 (4.ª revisión): las puntas parecían tubos de cristal de punta plana (anillo negro cerrado bajo la cúpula) y el
# plástico salía gris (0,87 del blanco de la caja; en la caja real 0,94-0,99). Ahora: punta plateada media con una franja
# blanca y una banda oscura, cúpula con un brillo suave sin anillo negro, más exposición y la pose de la caja real
# (girado 58°: la clavija derecha más cerca, en diagonal, y un poco más desde arriba).
P.limpia(); sc = estudio(); sc.view_settings.exposure = -1.0
P.CROMO.update(brillo=1.7, espejo=0.03, rugosidad=0.15,
               paradas=[(0.0, 0.45), (0.14, 0.35), (0.27, 0.95), (0.36, 1.0), (0.44, 0.16), (0.60, 0.14), (0.72, 0.55),
                        (0.86, 0.35), (1.0, 0.6)],
               cupula=[(0.62, 0.7, 0.0), (0.80, 0.9, 0.55), (0.92, 1.0, 0.9), (1.0, 0.85, 0.9)])
a = P.adaptador(); a.rotation_euler = (0, 0, math.radians(-58))
P.camara((-0.08, -0.29, 0.235), (0, 0, 0.037), focal=105)
sc.render.filepath = os.path.join(SAL, 'producto-cargador.png'); bpy.ops.render.render(write_still=True)
P.CROMO.update(brillo=None, espejo=0.12, rugosidad=0.08, paradas=None, cupula=0.0)

# cable: los dos conectores USB-C de pie, uno al lado del otro, y el cable trenzado bajando; las fundas de metal en
# cromo de estudio (plateado claro, como en la caja real)
P.limpia(); sc = estudio(); P.CROMO['brillo'] = 1.25; P.CROMO['contraste'] = 0.45
for x in (-11.5, 11.5):
    c = P.conector_usbc(f'usbc{x}'); c.location = (x * P.MM, 0, 0)
    P.cable_usbc([(x, 0, 1), (x, 0, -20), (x, 0, -45), (x, 0, -70)], nombre=f'cable{x}')
P.camara((0.0, -0.22, 0.02), (0, 0, -0.004), focal=105)
sc.render.filepath = os.path.join(SAL, 'producto-cable.png'); bpy.ops.render.render(write_still=True)
P.CROMO['brillo'] = None
