"""Película de producto (CGI) del pack original de Apple, plano a plano, con Blender/Cycles.

21/11/2026. El dueño: «rehazme otro anuncio desde cero […] de categoría nivel top». El modelo es el anunciante más
longevo del nicho (Innobative, anuncios activos desde hace más de un año): vídeo de producto en 3D sobre fondo oscuro,
el producto sale de la oscuridad con luz de borde y se enseña de cerca, más una tarjeta final con precio y envío.
Aquí, con las cajas reales recreadas (tools/producto3d.py, tools/arte_cajas_apple.py).

Uso: python3 peli_cajas.py ARTE SALIDA PLANO [--ancho 1080 --alto 1920 --muestras 40 --desde N --hasta M --prueba]
     PLANO: uno de PLANOS (abajo). Saca PNG numerados en SALIDA/PLANO/0001.png ...
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector
import producto3d as P

ARTE, SAL, PLANO = sys.argv[1], sys.argv[2], sys.argv[3]
def arg(n, d): return type(d)(sys.argv[sys.argv.index(n) + 1]) if n in sys.argv else d
ANCHO, ALTO, MUESTRAS = arg('--ancho', 1080), arg('--alto', 1920), arg('--muestras', 40)
FPS = 24


# ------------------------------------------------------------------ utilidades de animación
def clave(obj, ruta, pares, interp='BEZIER'):
    """pares: [(fotograma, valor), ...]. Suaviza con curvas Bézier (entrada y salida lentas)."""
    for f, v in pares:
        setattr(obj, ruta, v) if not isinstance(v, (tuple, list)) else setattr(obj, ruta, v)
        obj.keyframe_insert(data_path=ruta, frame=f)
    ad = obj.animation_data
    if ad and ad.action:
        for fc in _fcurves(ad):
            for k in fc.keyframe_points: k.interpolation = interp


def _fcurves(ad):
    act = ad.action
    if hasattr(act, 'fcurves') and act.fcurves: return list(act.fcurves)
    out = []                                                      # Blender 5: acciones por capas
    for capa in getattr(act, 'layers', []):
        for tira in capa.strips:
            for cb in tira.channelbags: out += list(cb.fcurves)
    return out


def objetivo(nombre, pos):
    e = bpy.data.objects.new(nombre, None); bpy.context.scene.collection.objects.link(e); e.location = pos; return e


def camara_animada(pares_pos, pares_mira, focal=70, dof=None, foco_obj=None, pares_foco=None):
    cam = P.camara(pares_pos[0][1], pares_mira[0][1], focal=focal)
    mira = objetivo('mira', pares_mira[0][1])
    t = cam.constraints.new('TRACK_TO'); t.target = mira; t.track_axis = 'TRACK_NEGATIVE_Z'; t.up_axis = 'UP_Y'
    clave(cam, 'location', pares_pos); clave(mira, 'location', pares_mira)
    if dof:
        cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = dof
        if pares_foco:                                              # el foco va a la cara que se enseña, no al centro de la caja
            foco_obj = objetivo('foco', pares_foco[0][1]); clave(foco_obj, 'location', pares_foco)
        cam.data.dof.focus_object = foco_obj or mira
    return cam, mira


def escena_base():
    P.limpia(); sc = P.motor(ANCHO, ALTO, muestras=MUESTRAS, ruido=0.04)
    sc.cycles.max_bounces = 5; sc.cycles.diffuse_bounces = 2; sc.cycles.glossy_bounces = 2
    sc.cycles.transmission_bounces = 0; sc.cycles.transparent_max_bounces = 2; sc.cycles.caustics_reflective = False
    sc.cycles.caustics_refractive = False; sc.cycles.adaptive_min_samples = 12
    sc.render.use_persistent_data = True
    sc.view_settings.exposure = -1.0; sc.render.fps = FPS
    P.fondo((0.004, 0.005, 0.011), 1.0)
    P.suelo((0.010, 0.012, 0.022), 0.2, tam=6.0)
    return sc


def luces(clave_w=6.0, rim_w=7.0, oro_w=0.0):
    k = P.luz_area('clave', (-0.30, -0.30, 0.38), (0, 0, 0.04), clave_w, (0.45, 0.45))
    luces.relleno = P.luz_area('relleno', (0.35, -0.25, 0.10), (0, 0, 0.04), 1.6, (0.5, 0.5))
    a = P.luz_area('contra_i', (-0.28, 0.30, 0.22), (0, 0, 0.05), rim_w, (0.12, 0.4))
    b = P.luz_area('contra_d', (0.30, 0.30, 0.22), (0, 0, 0.05), rim_w, (0.12, 0.4))
    if oro_w: P.luz_area('oro', (0.0, 0.45, 0.08), (0, 0, 0.05), oro_w, (0.6, 0.05), color=(1.0, 0.82, 0.55))
    return k, a, b


def barrido(pares_x, z=0.10, y=-0.22, energia=3.0, ancho=0.03):
    """Tira de luz estrecha que cruza delante del producto: el brillo recorre la caja (revelado premium)."""
    l = P.luz_area('barrido', (pares_x[0][1], y, z), (0, 0, 0.045), energia, (ancho, 0.5))
    l.rotation_euler = (math.radians(90), 0, 0)
    clave(l, 'location', [(f, (x, y, z)) for f, x in pares_x])
    return l


def energia(luz, pares):
    for f, e in pares:
        luz.data.energy = e; luz.data.keyframe_insert('energy', frame=f)


# ------------------------------------------------------------------ planos
def p_gancho(n):
    """«¿Su iPhone vino sin cargador? Apple ya no lo pone.» La caja del adaptador sale de la oscuridad: un barrido de
    luz recorre «20W Power Adapter» de muy cerca, se encienden las luces y, al alejarse, gira a tres cuartos con la
    pestaña a contraluz."""
    escena_base(); k, a, b = luces()
    caja = P.caja('cargador', ARTE)
    clave(caja, 'rotation_euler', [(1, (0, 0, math.radians(26))), (n, (0, 0, math.radians(-14)))])
    energia(k, [(1, 0.0), (int(n * 0.30), 0.0), (int(n * 0.62), 6.0)])
    energia(luces.relleno, [(1, 0.0), (int(n * 0.30), 0.0), (int(n * 0.62), 1.6)])
    sw = barrido([(1, -0.14), (int(n * 0.45), 0.14)], z=0.07, y=-0.18, energia=0.3, ancho=0.02)
    energia(sw, [(1, 0.3), (int(n * 0.45), 0.3), (int(n * 0.6), 0.0)])          # al principio solo el contraluz y el barrido
    camara_animada([(1, (0.022, -0.105, 0.066)), (int(n * 0.35), (0.018, -0.125, 0.066)), (n, (0.0, -0.33, 0.088))],
                   [(1, (0.004, -0.014, 0.062)), (int(n * 0.35), (0.004, -0.014, 0.060)), (n, (0.0, 0.0, 0.050))],
                   focal=70, dof=5.6,
                   pares_foco=[(1, (0.004, -0.016, 0.062)), (int(n * 0.35), (0.004, -0.016, 0.060)), (n, (0.0, -0.014, 0.050))])
    return n


def p_precinto(n):
    """«Originales de Apple, en su caja sin abrir.» La trasera: el precinto con la flecha verde en primer plano y un
    brillo rasante que dibuja su canto; la cámara se desliza despacio a lo largo de la pegatina."""
    escena_base(); k, a, b = luces(clave_w=3.0, rim_w=5.0)
    caja = P.caja('cargador', ARTE); caja.rotation_euler = (0, 0, math.radians(180 + 10))
    rasante = P.luz_area('rasante', (0.20, -0.06, 0.085), (0, -0.015, 0.074), 2.4, (0.02, 0.25))
    clave(rasante, 'location', [(1, (0.22, -0.07, 0.095)), (n, (-0.22, -0.07, 0.095))])
    camara_animada([(1, (-0.030, -0.118, 0.098)), (n, (-0.016, -0.124, 0.097))],
                   [(1, (-0.012, -0.015, 0.071)), (n, (-0.010, -0.015, 0.071))], focal=85, dof=5.6,
                   pares_foco=[(1, (-0.016, -0.016, 0.073)), (n, (-0.008, -0.016, 0.073))])
    return n


def p_pack(n):
    """«En Apple, 38 euros. Aquí, 18,99.» Las dos cajas juntas (un pack), abajo del encuadre para dejar sitio al
    precio; la cámara se acerca despacio y un barrido de luz cruza justo cuando entra el 18,99."""
    escena_base(); k, a, b = luces(oro_w=2.5)
    c1 = P.caja('cargador', ARTE); c2 = P.caja('cable', ARTE)
    c1.location = (-0.036, 0.0, 0); c1.rotation_euler = (0, 0, math.radians(10))
    c2.location = (0.040, 0.012, 0); c2.rotation_euler = (0, 0, math.radians(-12))
    barrido([(int(n * 0.45), -0.30), (int(n * 0.8), 0.30)], z=0.07, y=-0.20, energia=2.0)
    camara_animada([(1, (0.0, -0.50, 0.150)), (n, (0.0, -0.43, 0.125))],
                   [(1, (0.002, 0.0, 0.075)), (n, (0.002, 0.0, 0.072))], focal=70, dof=8)
    return n


def p_cantidad(n):
    """«Compramos por cantidad y ganamos menos.» La cámara sube y se aleja: filas de packs que se pierden en la
    oscuridad (por eso el precio)."""
    escena_base(); k, a, b = luces(clave_w=7.0, rim_w=6.0)
    paso_x, paso_y = 0.165, 0.11
    for fila in range(7):
        for col in range(-2, 3):
            ox, oy = col * paso_x, fila * paso_y
            c1 = P.caja('cargador', ARTE); c1.location = (ox - 0.036, oy, 0); c1.rotation_euler = (0, 0, math.radians(6))
            c2 = P.caja('cable', ARTE); c2.location = (ox + 0.040, oy + 0.012, 0); c2.rotation_euler = (0, 0, math.radians(-6))
    camara_animada([(1, (0.0, -0.42, 0.12)), (n, (0.0, -0.62, 0.42))],
                   [(1, (0.0, 0.02, 0.06)), (n, (0.0, 0.26, 0.02))], focal=60, dof=11)
    return n


def p_producto(n):
    """«Envío gratis, en 24 o 48 horas.» Lo que va dentro: el adaptador de pie y el cable trenzado enrollado, con un
    conector a la vista, girando despacio sobre el suelo oscuro, con luz de borde."""
    escena_base(); k, a, b = luces(rim_w=8.0)
    ad = P.adaptador(); ad.location = (-0.022, 0.004, 0.0); ad.rotation_euler = (0, 0, math.radians(12))
    pts = []
    for i in range(0, 721, 12):                                   # rollo de 2 vueltas, como sale de la caja
        t = math.radians(i); r = 24 - i / 720 * 5
        pts.append((r * math.cos(t), r * math.sin(t), 1.7 + i / 720 * 3.4))
    pts += [(19 * math.cos(math.radians(730)) - 4, -24, 1.7), (2, -34, 1.7)]   # el extremo sale hacia la cámara
    cab = P.cable_usbc(pts, nombre='rollo'); cab.location = (0.030, 0.012, 0.0)
    u1 = P.conector_usbc('usbc-a'); u1.location = (0.030 + 0.002, 0.012 - 0.034, 0.0029)
    u1.rotation_euler = (math.radians(90), 0, math.radians(180))
    base = objetivo('giro', (0.004, 0.0, 0)); ad.parent = base; cab.parent = base; u1.parent = base
    clave(base, 'rotation_euler', [(1, (0, 0, math.radians(-14))), (n, (0, 0, math.radians(14)))], interp='LINEAR')
    camara_animada([(1, (0.0, -0.31, 0.135)), (n, (0.0, -0.28, 0.125))],
                   [(1, (0.004, 0.0, 0.026)), (n, (0.004, 0.0, 0.026))], focal=70, dof=8)
    return n


def p_final(n):
    """«Compre en pillatumovil.com.» Las dos cajas, de frente y abajo; arriba queda el sitio de la tarjeta final."""
    escena_base(); k, a, b = luces(oro_w=3.0)
    c1 = P.caja('cargador', ARTE); c2 = P.caja('cable', ARTE)
    c1.location = (-0.036, 0.0, 0); c1.rotation_euler = (0, 0, math.radians(8))
    c2.location = (0.040, 0.012, 0); c2.rotation_euler = (0, 0, math.radians(-10))
    camara_animada([(1, (0.0, -0.56, 0.25)), (n, (0.0, -0.54, 0.24))],
                   [(1, (0.002, 0.0, 0.105)), (n, (0.002, 0.0, 0.104))], focal=70, dof=11)
    return n


PLANOS = {'gancho': (p_gancho, 74), 'precinto': (p_precinto, 61), 'pack': (p_pack, 98),        # al ritmo de la voz
          'cantidad': (p_cantidad, 60), 'producto': (p_producto, 76), 'final': (p_final, 80)}     # (449 fotogramas, 18,7 s)

if __name__ == '__main__':
    f, n = PLANOS[PLANO]; n = arg('--fotogramas', n); f(n)
    sc = bpy.context.scene; sc.frame_start = arg('--desde', 1); sc.frame_end = arg('--hasta', n)
    os.makedirs(os.path.join(SAL, PLANO), exist_ok=True)
    sc.render.filepath = os.path.join(SAL, PLANO, '')
    sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_depth = '8'
    if '--prueba' in sys.argv:                                      # solo unos fotogramas sueltos para revisar
        for fr in [int(x) for x in arg('--fotos', '1').split(',')]:
            sc.frame_set(fr); sc.render.filepath = os.path.join(SAL, PLANO, f'prueba_{fr:04d}.png')
            bpy.ops.render.render(write_still=True)
    else:
        bpy.ops.render.render(animation=True)
