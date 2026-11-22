"""Producto Apple en 3D fotorrealista con Blender (Cycles): cajas, adaptador de 20 W y cable USB-C trenzado.

21/11/2026. El dueño quiere un anuncio «de categoría nivel top» con las cajas «totalmente reales». Este módulo
construye los objetos con sus medidas de verdad y materiales físicos; las escenas (luz, cámara, planos) se montan
en otro script que lo importa. Unidades de Blender: metros (1 mm = 0.001).

Uso:  import producto3d as P
      P.limpia(); caja = P.caja('cargador', ARTE)         # ARTE: carpeta de tools/arte_cajas_apple.py
      cargador = P.adaptador(); cable = P.cable_usbc(puntos)
"""
import math, os
import bpy, bmesh
from mathutils import Vector, Matrix

MM = 0.001
MEDIDAS = {'cargador': (67.5, 80.0, 29.5), 'cable': (67.0, 65.5, 23.0)}          # ancho, alto, fondo (mm): fichas de tienda + fotos frontales (21/11)
PESTANA = {'ancho': 38.0, 'sobre': 14.7, 'bajo': 2.6, 'r': 3.0, 'ranura': (28.8, 4.8, 7.3), 'circulo': 6.8, 'grosor': 0.3}   # mm
# 22/11: 'bajo' era 6 mm y la base de la pestaña pasaba por debajo de media pegatina: salía un escalón en L que parecía
# plástico moldeado. En la caja real la pestaña acaba justo bajo el borde de arriba del precinto, que queda plano.


def limpia():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for b in (bpy.data.meshes, bpy.data.materials, bpy.data.images, bpy.data.curves, bpy.data.lights, bpy.data.cameras):
        for x in list(b): b.remove(x)


# ------------------------------------------------------------------ materiales
def _nodos(nombre):
    m = bpy.data.materials.new(nombre); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes['Principled BSDF']
    return m, nt, p


def mat_carton(nombre, imagen=None, grano=0.15):
    """Cartón estucado blanco de Apple: mate satinado, con el dibujo impreso y un grano de papel apenas visible."""
    m, nt, p = _nodos(nombre)
    p.inputs['Roughness'].default_value = 0.52
    p.inputs['Specular IOR Level'].default_value = 0.42
    p.inputs['Sheen Weight'].default_value = 0.08
    p.inputs['Subsurface Weight'].default_value = 0.03
    p.inputs['Subsurface Radius'].default_value = (0.6, 0.6, 0.55)
    p.inputs['Subsurface Scale'].default_value = 0.0006
    if imagen:
        t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(imagen, check_existing=True)
        t.interpolation = 'Cubic'; t.extension = 'EXTEND'
        t.image.colorspace_settings.name = 'sRGB'
        nt.links.new(t.outputs['Color'], p.inputs['Base Color'])
    else:
        p.inputs['Base Color'].default_value = (0.925, 0.925, 0.918, 1)
    # grano: ruido muy fino en el relieve
    n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = 9000; n.inputs['Detail'].default_value = 6
    bump = nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = grano; bump.inputs['Distance'].default_value = 0.00002
    nt.links.new(n.outputs['Fac'], bump.inputs['Height']); nt.links.new(bump.outputs['Normal'], p.inputs['Normal'])
    return m


def mat_plastico_blanco(nombre='plastico'):
    """Policarbonato blanco brillante de los cargadores Apple."""
    m, nt, p = _nodos(nombre)
    p.inputs['Base Color'].default_value = (0.86, 0.86, 0.855, 1)
    p.inputs['Roughness'].default_value = 0.22
    p.inputs['Subsurface Weight'].default_value = 0.12
    p.inputs['Subsurface Radius'].default_value = (1.0, 0.95, 0.9)
    p.inputs['Subsurface Scale'].default_value = 0.0015
    p.inputs['Coat Weight'].default_value = 0.35; p.inputs['Coat Roughness'].default_value = 0.08
    return m


def mat_metal(nombre='metal', rugosidad=0.18, color=(0.78, 0.78, 0.8)):
    m, nt, p = _nodos(nombre)
    p.inputs['Base Color'].default_value = (*color, 1); p.inputs['Metallic'].default_value = 1.0
    p.inputs['Roughness'].default_value = rugosidad
    return m


# Cromo «de foto de estudio» para las clavijas: el metal real en un estudio blanco refleja manchas sin forma
# (parecían camuflaje). En la foto de la caja de Apple se ve el cromo clásico: borde brillante, franja oscura y otra
# luz. Aquí el dibujo sale de hacia dónde mira la superficie respecto a la cámara, más un poco de brillo de verdad.
CROMO = {'brillo': None, 'contraste': 1.0, 'paradas': None, 'espejo': 0.12, 'rugosidad': 0.08, 'cupula': 0.0, 'vaina': None}                         # brillo None: metal normal; un número: cromo de estudio


def mat_cromo(nombre='cromo', brillo=1.4, contraste=None):
    contraste = CROMO['contraste'] if contraste is None else contraste   # <1: franjas más suaves (fundas USB-C, plateado claro)
    m, nt, p = _nodos(nombre)
    p.inputs['Base Color'].default_value = (0.8, 0.8, 0.82, 1); p.inputs['Metallic'].default_value = 1.0
    p.inputs['Roughness'].default_value = CROMO['rugosidad']
    g = nt.nodes.new('ShaderNodeNewGeometry')
    vt = nt.nodes.new('ShaderNodeVectorTransform'); vt.vector_type = 'NORMAL'; vt.convert_from = 'WORLD'; vt.convert_to = 'CAMERA'
    sx = nt.nodes.new('ShaderNodeSeparateXYZ')
    mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = -1.0; mr.inputs['From Max'].default_value = 1.0
    rampa = nt.nodes.new('ShaderNodeValToRGB'); cr = rampa.color_ramp
    paradas = CROMO['paradas'] or [(0.0, 0.40), (0.10, 1.0), (0.22, 0.85), (0.32, 0.22), (0.42, 0.05), (0.55, 0.14), (0.70, 0.95), (0.86, 0.55), (1.0, 0.30)]
    cr.elements[0].position, cr.elements[0].color = paradas[0][0], (paradas[0][1],) * 3 + (1,)
    cr.elements[1].position, cr.elements[1].color = paradas[-1][0], (paradas[-1][1],) * 3 + (1,)
    paradas = [(p_, 1 - contraste * (1 - v)) for p_, v in paradas]
    cr.elements[0].color = (paradas[0][1],) * 3 + (1,); cr.elements[1].color = (paradas[-1][1],) * 3 + (1,)
    for pos, v in paradas[1:-1]:
        e = cr.elements.new(pos); e.color = (v, v, v, 1)
    em = nt.nodes.new('ShaderNodeEmission'); em.inputs['Strength'].default_value = brillo
    mx = nt.nodes.new('ShaderNodeMixShader'); mx.inputs['Fac'].default_value = CROMO['espejo']
    sal = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
    nt.links.new(g.outputs['Normal'], vt.inputs['Vector']); nt.links.new(vt.outputs['Vector'], sx.inputs['Vector'])
    nt.links.new(sx.outputs['X'], mr.inputs['Value']); nt.links.new(mr.outputs['Result'], rampa.inputs['Fac'])
    if CROMO['cupula']:
        # 22/11 v4: la punta redondeada de la clavija real refleja un anillo oscuro y arriba blanco. Segunda rampa con la
        # normal vertical de la cámara (Y): los lados (Y < 0,1) no cambian; hacia arriba, oscuro y luego blanco.
        my = nt.nodes.new('ShaderNodeMapRange'); my.inputs['From Min'].default_value = -1.0; my.inputs['From Max'].default_value = 1.0
        r2 = nt.nodes.new('ShaderNodeValToRGB'); c2 = r2.color_ramp
        paradas_y = CROMO['cupula'] if isinstance(CROMO['cupula'], list) else \
            [(0.55, 0.04, 0.0), (0.62, 0.04, 1.0), (0.78, 0.04, 1.0), (0.84, 1.0, 1.0), (1.0, 1.0, 1.0)]
        c2.elements[0].position, c2.elements[0].color = paradas_y[0][0], (paradas_y[0][1],) * 3 + (paradas_y[0][2],)
        c2.elements[1].position, c2.elements[1].color = paradas_y[-1][0], (paradas_y[-1][1],) * 3 + (paradas_y[-1][2],)
        for pos, v, al in paradas_y[1:-1]:
            e = c2.elements.new(pos); e.color = (v, v, v, al)
        mc = nt.nodes.new('ShaderNodeMix'); mc.data_type = 'RGBA'
        nt.links.new(sx.outputs['Y'], my.inputs['Value']); nt.links.new(my.outputs['Result'], r2.inputs['Fac'])
        nt.links.new(r2.outputs['Alpha'], mc.inputs['Factor']); nt.links.new(r2.outputs['Color'], mc.inputs['B'])
        nt.links.new(rampa.outputs['Color'], mc.inputs['A']); nt.links.new(mc.outputs['Result'], em.inputs['Color'])
    else:
        nt.links.new(rampa.outputs['Color'], em.inputs['Color'])
    nt.links.new(em.outputs['Emission'], mx.inputs[1]); nt.links.new(p.outputs['BSDF'], mx.inputs[2])
    nt.links.new(mx.outputs['Shader'], sal.inputs['Surface'])
    return m


def mat_negro(nombre='hueco'):
    m, nt, p = _nodos(nombre)
    p.inputs['Base Color'].default_value = (0.01, 0.01, 0.012, 1); p.inputs['Roughness'].default_value = 0.6
    return m


def mat_trenzado(nombre='trenzado', paso_mm=0.9, hebras=8):
    """Funda trenzada blanca del cable: espiguilla de dos familias de hebras en hélice. Necesita la UV del tubo
    (x = mm a lo largo del cable, y = vuelta de 0 a 1), que pone tubo()."""
    m, nt, p = _nodos(nombre)
    p.inputs['Base Color'].default_value = (0.80, 0.80, 0.79, 1); p.inputs['Roughness'].default_value = 0.55
    p.inputs['Sheen Weight'].default_value = 0.5; p.inputs['Sheen Roughness'].default_value = 0.35
    uv = nt.nodes.new('ShaderNodeUVMap'); sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(uv.outputs['UV'], sep.inputs['Vector'])
    hilos = []
    for signo in (1, -1):
        a = nt.nodes.new('ShaderNodeMath'); a.operation = 'MULTIPLY'; a.inputs[1].default_value = 1.0 / paso_mm
        nt.links.new(sep.outputs['X'], a.inputs[0])
        b = nt.nodes.new('ShaderNodeMath'); b.operation = 'MULTIPLY_ADD'; b.inputs[1].default_value = signo * hebras
        nt.links.new(sep.outputs['Y'], b.inputs[0]); nt.links.new(a.outputs[0], b.inputs[2])
        f = nt.nodes.new('ShaderNodeMath'); f.operation = 'PINGPONG'; f.inputs[1].default_value = 0.5
        nt.links.new(b.outputs[0], f.inputs[0]); hilos.append(f)
    mx = nt.nodes.new('ShaderNodeMath'); mx.operation = 'MAXIMUM'
    nt.links.new(hilos[0].outputs[0], mx.inputs[0]); nt.links.new(hilos[1].outputs[0], mx.inputs[1])
    bump = nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.85; bump.inputs['Distance'].default_value = 0.00025
    nt.links.new(mx.outputs[0], bump.inputs['Height']); nt.links.new(bump.outputs['Normal'], p.inputs['Normal'])
    # las hebras se ven un poco más oscuras en los surcos
    ramp = nt.nodes.new('ShaderNodeMapRange'); ramp.inputs['To Min'].default_value = 0.72; ramp.inputs['To Max'].default_value = 0.84
    nt.links.new(mx.outputs[0], ramp.inputs['Value'])
    rgb = nt.nodes.new('ShaderNodeCombineColor'); [nt.links.new(ramp.outputs[0], rgb.inputs[k]) for k in range(3)]
    nt.links.new(rgb.outputs[0], p.inputs['Base Color'])
    return m


# ------------------------------------------------------------------ caja
def _objeto(nombre, me):
    o = bpy.data.objects.new(nombre, me); bpy.context.scene.collection.objects.link(o); return o


def caja(nombre, arte, pestana=True, bisel_mm=0.25):
    """Caja con sus 6 caras impresas, cantos levemente redondeados y la pestaña de colgar con el ojal euro.
    Origen: centro de la base. Delante mira a -Y (hacia la cámara por defecto); arriba es +Z."""
    W, H, D = (v * MM for v in MEDIDAS[nombre])
    me = bpy.data.meshes.new(nombre); bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * W, v.co.y * D, (v.co.z + 0.5) * H))
    uv = bm.loops.layers.uv.new('UVMap')
    caras = {'frente': Vector((0, -1, 0)), 'trasera': Vector((0, 1, 0)), 'lado_d': Vector((1, 0, 0)),
             'lado_i': Vector((-1, 0, 0)), 'tapa': Vector((0, 0, 1)), 'base': Vector((0, 0, -1))}
    orden = list(caras)
    for f in bm.faces:
        n = f.normal.normalized(); k = max(orden, key=lambda c: n.dot(caras[c])); f.material_index = orden.index(k)
        for l in f.loops:                                     # cada cara ocupa toda su imagen, vista desde fuera
            x, y, z = l.vert.co.x / W + 0.5, l.vert.co.y / D + 0.5, l.vert.co.z / H
            u, v = {'frente': (x, z), 'trasera': (1 - x, z), 'lado_d': (y, z), 'lado_i': (1 - y, z),
                    'tapa': (x, y), 'base': (x, 1 - y)}[k]
            l[uv].uv = (u, v)
    bm.to_mesh(me); bm.free()
    o = _objeto(nombre, me)
    arch = {'frente': 'frente', 'trasera': 'trasera', 'lado_d': 'lado', 'lado_i': 'lado', 'tapa': 'tapa', 'base': 'base'}
    for c in orden:
        o.data.materials.append(mat_carton(f'{nombre}-{c}', os.path.join(arte, f'{nombre}-{arch[c]}.png')))
    b = o.modifiers.new('bisel', 'BEVEL'); b.width = bisel_mm * MM; b.segments = 4; b.limit_method = 'ANGLE'
    b.harden_normals = True
    o.data.shade_smooth()
    if pestana:
        t = _pestana(nombre, W, H, D); t.parent = o
    if os.path.exists(os.path.join(arte, f'{nombre}-precinto.png')):
        pr = precinto(nombre, arte, W, H, D); pr.parent = o
    return o


def _pestana(nombre, W, H, D):
    """Pestaña de colgar: cartulina blanca de 0,3 mm pegada a la trasera; asoma 14,7 mm por encima de la tapa y su
    base queda tapada por el precinto. Esquinas de arriba redondeadas y ojal «euro» (ranura con un círculo en medio)."""
    from shapely.geometry import Point, box as sbox
    from shapely.ops import unary_union
    T = PESTANA; w = T['ancho'] * MM; arriba = T['sobre'] * MM; abajo = T['bajo'] * MM; r = T['r'] * MM
    exterior = unary_union([sbox(-w / 2, -abajo, w / 2, arriba - r), sbox(-w / 2 + r, -abajo, w / 2 - r, arriba),
                            Point(-w / 2 + r, arriba - r).buffer(r, 32), Point(w / 2 - r, arriba - r).buffer(r, 32)])
    lr, hr, dy = (v * MM for v in T['ranura']); cy = arriba - dy; rh = hr / 2
    ojal = unary_union([sbox(-lr / 2 + rh, cy - rh, lr / 2 - rh, cy + rh), Point(-lr / 2 + rh, cy).buffer(rh, 24),
                        Point(lr / 2 - rh, cy).buffer(rh, 24), Point(0, cy).buffer(T['circulo'] * MM / 2, 48)])
    forma = exterior.difference(ojal)
    cu = bpy.data.curves.new(f'{nombre}-pestana', 'CURVE'); cu.dimensions = '2D'; cu.fill_mode = 'BOTH'
    cu.extrude = T['grosor'] * MM / 2
    for anillo in [forma.exterior] + list(forma.interiors):
        pts = list(anillo.coords)[:-1]
        sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1); sp.use_cyclic_u = True
        for p, (x, y) in zip(sp.points, pts): p.co = (x, y, 0, 1)
    o = _objeto(f'{nombre}-pestana', cu)
    o.rotation_euler = (math.pi / 2, 0, 0); o.location = (0, D / 2 + T['grosor'] * MM / 2 + 0.02 * MM, H)
    o.data.materials.append(mat_carton(f'{nombre}-pestana-carton'))
    return o


PRECINTO = {'cargador': (4.7, 59.4, 1.6, 9.2), 'cable': (3.4, 55.6, 2.3, 9.5)}   # desde el borde izq. (visto de atrás), largo, desde arriba, alto (mm)


def precinto(nombre, arte, W, H, D, grosor_mm=0.12, levanta_mm=0.22):
    """Pegatina de precinto como en la caja real (fotos de compradores, 21/11): píldora blanca con los dos extremos
    redondos, arriba de la trasera, con el círculo verde dentro del extremo izquierdo. Tapa la base de la pestaña,
    así que se abomba encima de ella. Tiene grosor, canto y sombra; el extremo de la flecha, apenas levantado."""
    from shapely.geometry import Point, box as sbox
    from shapely.ops import unary_union
    x0, largo, z0, alto = PRECINTO[nombre]; R = alto / 2
    forma = unary_union([sbox(R, 0, largo - R, alto), Point(R, R).buffer(R, 64), Point(largo - R, R).buffer(R, 64)])
    bm = bmesh.new(); vs = [bm.verts.new((x, y, 0)) for x, y in list(forma.exterior.coords)[:-1]]; bm.faces.new(vs)
    tw = PESTANA['ancho']; tb = PESTANA['bajo']; tg = PESTANA['grosor']
    borde_i = W / MM / 2 - x0 - tw / 2                      # u donde empieza la pestaña por debajo (visto de atrás)
    cortes_u = [0.3 * k for k in range(1, 20)] + [borde_i + d for d in (-0.6, -0.3, 0, 0.3, 0.6)] + \
               [borde_i + tw + d for d in (-0.6, -0.3, 0, 0.3, 0.6)] + [1.5 * k for k in range(4, int(largo / 1.5))]
    cortes_v = [0.25 * k for k in range(1, int(alto / 0.25))]
    for v in cortes_v:
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, v, 0), plane_no=(0, 1, 0))
    for u in sorted(set(round(c, 3) for c in cortes_u if 0 < c < largo)):
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(u, 0, 0), plane_no=(1, 0, 0))
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    uv = bm.loops.layers.uv.new('UVMap')
    for f in bm.faces:
        for l in f.loops: l[uv].uv = (l.vert.co.x / largo, 1 - l.vert.co.y / alto)
    def suave(a, b, x):
        t = min(1, max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t)
    for v in bm.verts:
        u, s = v.co.x, v.co.y                                 # s: mm hacia abajo desde el borde de arriba de la pegatina
        z_mm = H / MM - z0 - s
        encima = suave(borde_i - 0.4, borde_i + 0.4, u) * (1 - suave(borde_i + tw - 0.4, borde_i + tw + 0.4, u)) * \
                 (1 - suave(tb - 0.4, tb + 0.4, z0 + s))           # 1 donde la pegatina pasa por encima de la pestaña
        lev = levanta_mm * max(0.0, 1 - u / 3.5) ** 2
        y = D / MM / 2 + 0.03 + encima * (tg + 0.02) + lev
        v.co = Vector((W / MM / 2 - x0 - u, y, z_mm)) * MM
    bm.normal_update()
    if sum(f.normal.y for f in bm.faces) < 0: bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(f'{nombre}-precinto'); bm.normal_update(); bm.to_mesh(me); bm.free()
    o = _objeto(f'{nombre}-precinto', me)
    so = o.modifiers.new('grosor', 'SOLIDIFY'); so.thickness = grosor_mm * MM; so.offset = 1.0; so.use_even_offset = False
    so.use_quality_normals = True                                  # sin picos en triángulos finos
    bv = o.modifiers.new('canto', 'BEVEL'); bv.width = 0.035 * MM; bv.segments = 2; bv.limit_method = 'ANGLE'
    o.data.shade_smooth()
    m = mat_carton(f'{nombre}-precinto', os.path.join(arte, f'{nombre}-precinto.png'), grano=0.08)
    p = m.node_tree.nodes['Principled BSDF']; p.inputs['Roughness'].default_value = 0.34; p.inputs['Coat Weight'].default_value = 0.15
    o.data.materials.append(m)
    return o


# ------------------------------------------------------------------ adaptador 20 W (Europa)
ADAPTADOR = {'ancho': 45.5, 'grueso': 24.6, 'largo': 38.0,       # A2347: techtest 37x45x24 mm; foto oficial MHJE3: 38,2 mm (con 44 parecía un cargador genérico)       # cuerpo: sección de estadio ancho x grueso; largo = eje de las clavijas
             'meseta': (35.3, 13.7, 19.0),                        # bloque de las clavijas 35,3 x 13,7 (Europlug); en Apple con los extremos redondeados                         # bloque de las clavijas: ancho, grueso, alto
             'clavija': (4.0, 19.0, 19.0)}                        # diámetro, separación entre centros, largo


def _estadio(bm, ancho, grueso, z, radio_esquina=None, n=12):
    """Anillo de vértices a la altura z: rectángulo ancho x grueso con las 4 esquinas redondeadas de radio r
    (si r = grueso/2 sale un estadio: los extremos son medios círculos)."""
    r = min(grueso / 2, ancho / 2) if radio_esquina is None else radio_esquina
    cx, cy = ancho / 2 - r, grueso / 2 - r
    pts = []
    for (sx, sy, a0) in ((1, -1, -90), (1, 1, 0), (-1, 1, 90), (-1, -1, 180)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            p = (sx * cx + r * math.cos(a), sy * cy + r * math.sin(a), z)
            if not pts or (abs(p[0] - pts[-1][0]) > 1e-9 or abs(p[1] - pts[-1][1]) > 1e-9): pts.append(p)
    if abs(pts[0][0] - pts[-1][0]) < 1e-9 and abs(pts[0][1] - pts[-1][1]) < 1e-9: pts.pop()
    return [bm.verts.new(p) for p in pts]


def _hexagono(bm, ancho, grueso, z, r=0.0016):
    """Contorno del cuello Europlug: hexágono alargado (extremos a 45°) con las esquinas redondeadas."""
    from shapely.geometry import Polygon
    c = grueso / 2; w = ancho / 2
    hx = Polygon([(-w, 0), (-w + c, -c), (w - c, -c), (w, 0), (w - c, c), (-w + c, c)]).buffer(-r).buffer(r, 16)
    pts = list(hx.exterior.coords)[:-1]
    if Polygon(pts).exterior.is_ccw is False: pts = pts[::-1]
    return [bm.verts.new((x, y, z)) for x, y in pts]


def adaptador():
    """Cargador Apple 20 W USB-C, versión europea. Origen: centro de la cara del puerto; las clavijas miran a +Z."""
    A = ADAPTADOR; s = MM
    me = bpy.data.meshes.new('adaptador'); bm = bmesh.new()
    capas = [(A['ancho'], A['grueso'], 0.0), (A['ancho'], A['grueso'], A['largo'])]
    anillos = [_estadio(bm, a * s, g * s, z * s) for a, g, z in capas]
    bm.faces.new(list(reversed(anillos[0]))); bm.faces.new(anillos[-1])
    for a, b in zip(anillos, anillos[1:]):
        n = len(a)
        for i in range(n): bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
    bm.to_mesh(me); bm.free()
    cuerpo = _objeto('adaptador', me)
    bv = cuerpo.modifiers.new('bisel', 'BEVEL'); bv.width = 2.2 * s; bv.segments = 6; bv.limit_method = 'ANGLE'
    cuerpo.data.shade_smooth()
    blanco = mat_plastico_blanco(); cuerpo.data.materials.append(blanco)
    # meseta de las clavijas (hexágono alargado con esquinas suaves)
    mw, mg, mh = A['meseta']
    me2 = bpy.data.meshes.new('meseta'); bm = bmesh.new()
    # 22/11 v4: la revisión vio las caras a 45° del hexágono hasta con 2,6 mm de bisel; en la foto oficial (MHJE3) el
    # bloque tiene los extremos redondeados: estadio de 35,3 x 13,7 mm (radio 6,85 mm) y un bisel pequeño arriba
    a0 = _estadio(bm, mw * s, mg * s, A['largo'] * s, n=16)
    a1 = _estadio(bm, mw * s, mg * s, (A['largo'] + mh) * s, n=16)
    bm.faces.new(list(reversed(a0))); bm.faces.new(a1)
    for i in range(len(a0)): bm.faces.new((a0[i], a0[(i + 1) % len(a0)], a1[(i + 1) % len(a0)], a1[i]))
    bm.to_mesh(me2); bm.free()
    meseta = _objeto('meseta', me2); meseta.parent = cuerpo
    bv = meseta.modifiers.new('bisel', 'BEVEL'); bv.width = 1.0 * s; bv.segments = 6; bv.limit_method = 'ANGLE'
    meseta.data.shade_smooth(); meseta.data.materials.append(blanco)
    # clavijas: vaina blanca aislante y punta de metal redondeada
    d, sep, largo = A['clavija']; z0 = (A['largo'] + mh) * s
    metal = mat_metal('clavija', 0.12) if CROMO['brillo'] is None else mat_cromo('clavija', CROMO['brillo'])
    # 22/11 v6: en la caja real la vaina es blanca mate y opaca, con sombra de un lado; con el plástico brillante salía
    # blanca plana y parecía un tubo de cristal. CROMO['vaina'] = (gris, rugosidad) la hace mate (solo el dibujo de la caja).
    vaina = blanco
    if CROMO['vaina']:
        vaina, _, pv = _nodos('vaina'); g_, r_ = CROMO['vaina']
        pv.inputs['Base Color'].default_value = (g_, g_, g_ * 0.995, 1); pv.inputs['Roughness'].default_value = r_
    for x in (-sep / 2, sep / 2):
        bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=d / 2 * s, depth=10 * s, location=(x * s, 0, z0 + 5 * s))
        v = bpy.context.object; v.data.materials.append(vaina); v.parent = cuerpo; v.data.shade_smooth()
        bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=d / 2 * s * 0.98, depth=(largo - 10 - d / 2) * s,
                                            location=(x * s, 0, z0 + (10 + (largo - 10 - d / 2) / 2) * s))
        c = bpy.context.object; c.data.materials.append(metal); c.parent = cuerpo; c.data.shade_smooth()
        bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=d / 2 * s * 0.98, location=(x * s, 0, z0 + (largo - d / 2) * s))
        p = bpy.context.object; p.data.materials.append(metal); p.parent = cuerpo; p.data.shade_smooth()
    # puerto USB-C en la cara de abajo: hueco negro con la lengüeta
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.2 * s)); h = bpy.context.object
    h.scale = (8.6 * s, 2.7 * s, 0.6 * s); h.data.materials.append(mat_negro()); h.parent = cuerpo
    bv = h.modifiers.new('bisel', 'BEVEL'); bv.width = 1.2 * s; bv.segments = 6; bv.affect = 'VERTICES' if False else 'EDGES'
    return cuerpo


# ------------------------------------------------------------------ cable USB-C trenzado
USBC = {'funda': (10.2, 5.8, 14.8), 'clavija': (8.25, 2.4, 6.8), 'cable_r': 1.65}   # mm (A2795: cable de 3,3 mm; funda medida en la foto de Apple)


def conector_usbc(nombre='usbc'):
    """Conector USB-C de Apple: funda blanca y clavija metálica. Origen: base de la funda (donde entra el cable);
    la clavija mira a +Z."""
    s = MM; fw, ft, fl = USBC['funda']; cw, ct, cl = USBC['clavija']
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, fl / 2 * s)); f = bpy.context.object; f.name = nombre
    f.scale = (fw * s, ft * s, fl * s); bpy.ops.object.transform_apply(scale=True)
    b = f.modifiers.new('bisel', 'BEVEL'); b.width = 2.3 * s; b.segments = 8; b.limit_method = 'ANGLE'
    f.data.shade_smooth(); f.data.materials.append(mat_plastico_blanco('funda-usbc'))
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, (fl + cl / 2 - 0.2) * s)); m = bpy.context.object
    m.scale = (cw * s, ct * s, cl * s); bpy.ops.object.transform_apply(scale=True)
    b = m.modifiers.new('bisel', 'BEVEL'); b.width = 1.15 * s; b.segments = 8; b.limit_method = 'ANGLE'
    m.data.shade_smooth(); m.data.materials.append(mat_metal('clavija-usbc', 0.16) if CROMO['brillo'] is None else mat_cromo('clavija-usbc', CROMO['brillo'])); m.parent = f
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, (fl + cl - 0.25) * s)); h = bpy.context.object
    h.scale = ((cw - 1.0) * s, (ct - 1.0) * s, 0.3 * s); h.data.materials.append(mat_negro('boca-usbc')); h.parent = f
    return f


def _spline(pts, n=24):
    """Catmull-Rom centrípeta por los puntos (mm). Devuelve la lista de puntos muestreados."""
    P_ = [Vector(p) for p in pts]; P_ = [P_[0] * 2 - P_[1]] + P_ + [P_[-1] * 2 - P_[-2]]
    out = []
    for i in range(1, len(P_) - 2):
        p0, p1, p2, p3 = P_[i - 1:i + 3]
        for k in range(n):
            t = k / n
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(P_[-2]); return out


def tubo(pts_mm, radio_mm, nombre='cable', lados=40, material=None):
    """Tubo que sigue la curva por los puntos (mm), con marcos de transporte paralelo y UV en milímetros
    (x a lo largo, y = vuelta). Así el trenzado sale a escala real en cualquier forma del cable."""
    c = _spline(pts_mm); bm = bmesh.new(); uv = bm.loops.layers.uv.new('UVMap')
    t0 = (c[1] - c[0]).normalized(); n0 = t0.orthogonal().normalized(); anillos = []; largo = [0.0]
    for i, p in enumerate(c):
        t = (c[min(i + 1, len(c) - 1)] - c[max(i - 1, 0)]).normalized()
        if i: n0 = (n0 - t * n0.dot(t)).normalized(); largo.append(largo[-1] + (c[i] - c[i - 1]).length)
        b0 = t.cross(n0)
        anillos.append([bm.verts.new((p + (n0 * math.cos(2 * math.pi * k / lados) + b0 * math.sin(2 * math.pi * k / lados)) * radio_mm) * MM)
                        for k in range(lados)])
    for i in range(len(anillos) - 1):
        for k in range(lados):
            f = bm.faces.new((anillos[i][k], anillos[i][(k + 1) % lados], anillos[i + 1][(k + 1) % lados], anillos[i + 1][k]))
            for l, (a, b) in zip(f.loops, ((i, k), (i, k + 1), (i + 1, k + 1), (i + 1, k))):
                l[uv].uv = (largo[a], b / lados)
    for an in (anillos[0], anillos[-1]): bm.faces.new(an)
    me = bpy.data.meshes.new(nombre); bm.normal_update(); bm.to_mesh(me); bm.free()
    o = _objeto(nombre, me); o.data.shade_smooth(); o.data.materials.append(material or mat_trenzado())
    return o


def cable_usbc(puntos_mm, radio_mm=None, nombre='cable'):
    return tubo(puntos_mm, radio_mm or USBC['cable_r'], nombre)


# ------------------------------------------------------------------ render
def motor(ancho=1080, alto=1920, muestras=128, ruido=0.02):
    sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
    sc.cycles.samples = muestras; sc.cycles.adaptive_threshold = ruido; sc.cycles.use_denoising = True
    try: sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    except Exception: pass
    sc.render.resolution_x, sc.render.resolution_y = ancho, alto; sc.render.resolution_percentage = 100
    sc.render.film_transparent = False
    sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'None'; sc.view_settings.exposure = 0.0
    sc.cycles.max_bounces = 8; sc.cycles.glossy_bounces = 4; sc.cycles.transmission_bounces = 4
    return sc


def camara(pos, mira, focal=85, nombre='camara', dof=None, foco=None):
    c = bpy.data.objects.new(nombre, bpy.data.cameras.new(nombre)); bpy.context.scene.collection.objects.link(c)
    c.data.lens = focal; c.data.sensor_width = 36; c.data.clip_start = 0.001
    c.location = pos; d = Vector(mira) - Vector(pos); c.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    if dof:
        c.data.dof.use_dof = True; c.data.dof.aperture_fstop = dof
        c.data.dof.focus_distance = (Vector(foco) - Vector(pos)).length if foco else d.length
    bpy.context.scene.camera = c
    return c


def luz_area(nombre, pos, mira, energia, tam=(0.3, 0.3), color=(1, 1, 1)):
    l = bpy.data.lights.new(nombre, 'AREA'); l.energy = energia; l.shape = 'RECTANGLE'; l.size, l.size_y = tam
    l.color = color
    o = bpy.data.objects.new(nombre, l); bpy.context.scene.collection.objects.link(o)
    o.location = pos; d = Vector(mira) - Vector(pos); o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    o.visible_camera = False                                       # la luz ilumina y se refleja, pero no se ve de frente
    return o


def fondo(color=(0.006, 0.008, 0.016), fuerza=1.0):
    w = bpy.data.worlds.new('mundo'); w.use_nodes = True; bpy.context.scene.world = w
    bg = w.node_tree.nodes['Background']; bg.inputs['Color'].default_value = (*color, 1); bg.inputs['Strength'].default_value = fuerza
    return w


def suelo(color=(0.01, 0.012, 0.022), rugosidad=0.18, tam=4.0):
    bpy.ops.mesh.primitive_plane_add(size=tam, location=(0, 0, 0)); s = bpy.context.object; s.name = 'suelo'
    m, nt, p = _nodos('suelo'); p.inputs['Base Color'].default_value = (*color, 1); p.inputs['Roughness'].default_value = rugosidad
    p.inputs['Specular IOR Level'].default_value = 0.6
    s.data.materials.append(m)
    return s
