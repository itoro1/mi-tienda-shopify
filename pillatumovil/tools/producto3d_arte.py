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


# adaptador: clavijas arriba, a tres cuartos (girado 32°) y visto desde arriba, como en la caja real; clavijas en
# cromo de estudio (22/11: con metal normal salían manchas que parecían camuflaje y el ángulo era casi de frente)
# 22/11 (revisión): las clavijas salían pálidas con reflejos en rectángulo (las luces de área). En la caja real son de
# cromo oscuro con un brillo limpio en la punta y el canto claro: rampa más oscura, casi sin reflejo directo y más mate.
P.limpia(); sc = estudio(); P.CROMO.update(brillo=1.0, espejo=0.03, rugosidad=0.3,
                                          paradas=[(0.0, 0.30), (0.10, 0.95), (0.20, 0.45), (0.32, 0.10), (0.45, 0.05),
                                                   (0.58, 0.12), (0.70, 0.55), (0.82, 0.18), (1.0, 0.35)])
a = P.adaptador(); a.rotation_euler = (0, 0, math.radians(-32))
P.camara((-0.08, -0.30, 0.21), (0, 0, 0.037), focal=105)
sc.render.filepath = os.path.join(SAL, 'producto-cargador.png'); bpy.ops.render.render(write_still=True)
P.CROMO.update(brillo=None, espejo=0.12, rugosidad=0.08, paradas=None)

# cable: los dos conectores USB-C de pie, uno al lado del otro, y el cable trenzado bajando; las fundas de metal en
# cromo de estudio (plateado claro, como en la caja real)
P.limpia(); sc = estudio(); P.CROMO['brillo'] = 1.25; P.CROMO['contraste'] = 0.45
for x in (-11.5, 11.5):
    c = P.conector_usbc(f'usbc{x}'); c.location = (x * P.MM, 0, 0)
    P.cable_usbc([(x, 0, 1), (x, 0, -20), (x, 0, -45), (x, 0, -70)], nombre=f'cable{x}')
P.camara((0.0, -0.22, 0.02), (0, 0, -0.004), focal=105)
sc.render.filepath = os.path.join(SAL, 'producto-cable.png'); bpy.ops.render.render(write_still=True)
P.CROMO['brillo'] = None
