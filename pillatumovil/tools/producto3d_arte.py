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


# adaptador: clavijas arriba, visto de frente-izquierda y un poco desde arriba (como en la caja real)
P.limpia(); sc = estudio()
a = P.adaptador(); a.rotation_euler = (0, 0, math.radians(-18))
P.camara((-0.06, -0.34, 0.11), (0, 0, 0.04), focal=105)
sc.render.filepath = os.path.join(SAL, 'producto-cargador.png'); bpy.ops.render.render(write_still=True)

# cable: los dos conectores USB-C de pie, uno al lado del otro, y el cable trenzado bajando
P.limpia(); sc = estudio()
for x in (-11.5, 11.5):
    c = P.conector_usbc(f'usbc{x}'); c.location = (x * P.MM, 0, 0)
    P.cable_usbc([(x, 0, 1), (x, 0, -20), (x, 0, -45), (x, 0, -70)], nombre=f'cable{x}')
P.camara((0.0, -0.22, 0.02), (0, 0, -0.004), focal=105)
sc.render.filepath = os.path.join(SAL, 'producto-cable.png'); bpy.ops.render.render(write_still=True)
