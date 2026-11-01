# Marca de Pillatumovil, version 3 (01/11/2026).
# El dueno queria algo reconocible, que llame la atencion y que valga para
# una tienda de moviles y accesorios (no solo cargadores). Dos propuestas:
#   1 "movil-P": la P de Pillatumovil hecha con un movil (el movil es el asta
#     y la panza sale de su costado). Silueta unica, se lee a 36 px.
#   2 "abanico": tres moviles abiertos como un abanico de cartas (oro,
#     titanio y el de delante con pantalla). Dice "tienda de moviles".
# Colores de la tienda: noche #0B0F1A, oro champan, marfil.
# Letra del logotipo: Unbounded (Google Fonts, licencia OFL), convertida a
# trazos: los SVG no dependen de tener la letra instalada.
# Necesita: pip install fonttools uharfbuzz ; playwright (ya en el entorno).
# uso: python3 marca_v3.py CARPETA_SALIDA
import os, sys, json, math, subprocess, tempfile, urllib.request, re

NOCHE = '#0B0F1A'; MARFIL = '#F4F1EA'; TINTA = '#141824'; PAPEL = '#F6F2EA'
ORO_TXT = '#D9BB7C'; ORO_OSCURO = '#9A7535'

# ---------------------------------------------------------------- letra
CACHE = os.path.expanduser('~/.cache/pillatumovil-fuentes')

def fuente(peso):
    os.makedirs(CACHE, exist_ok=True)
    ruta = os.path.join(CACHE, f'Unbounded-{peso}.ttf')
    if not os.path.exists(ruta):
        req = urllib.request.Request(f'https://fonts.googleapis.com/css2?family=Unbounded:wght@{peso}',
                                     headers={'User-Agent': 'Mozilla/4.0'})
        css = urllib.request.urlopen(req).read().decode()
        url = re.search(r'url\((https[^)]+\.ttf)\)', css).group(1)
        urllib.request.urlretrieve(url, ruta)
    return ruta

def texto_trazos(peso, partes, tam, x, y, tracking=0.0):
    """partes: [(texto, color)]. Devuelve (svg, ancho, (arriba, abajo)) con la
    linea base en y. tracking en em. Usa harfbuzz para el kerning."""
    import uharfbuzz as hb
    from fontTools.ttLib import TTFont
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    from fontTools.pens.boundsPen import BoundsPen
    ruta = fuente(peso)
    tt = TTFont(ruta); gs = tt.getGlyphSet(); orden = tt.getGlyphOrder()
    face = hb.Face(hb.Blob.from_file_path(ruta)); font = hb.Font(face); upem = face.upem
    texto = ''.join(t for t, _ in partes)
    colores = []
    for t, c in partes: colores += [c] * len(t)
    buf = hb.Buffer(); buf.add_str(texto); buf.guess_segment_properties(); hb.shape(font, buf, {'kern': True, 'liga': False})
    k = tam / upem; cx = x; trozos = {}; arriba = abajo = None
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        nombre = orden[info.codepoint]; color = colores[info.cluster]
        pen = SVGPathPen(gs)
        gs[nombre].draw(TransformPen(pen, (k, 0, 0, -k, cx + pos.x_offset * k, y - pos.y_offset * k)))
        d = pen.getCommands()
        if d: trozos.setdefault(color, []).append(d)
        bp = BoundsPen(gs); gs[nombre].draw(bp)
        if bp.bounds:
            a, b = y - bp.bounds[3] * k, y - bp.bounds[1] * k
            arriba = a if arriba is None else min(arriba, a); abajo = b if abajo is None else max(abajo, b)
        cx += pos.x_advance * k + tracking * tam
    ancho = cx - x - tracking * tam
    svg = ''.join(f'<path fill="{c}" d="{" ".join(ds)}"/>' for c, ds in trozos.items())
    return svg, ancho, (arriba, abajo)

# ---------------------------------------------------------------- simbolos
DEFS = '''<defs>
<radialGradient id="fondo" cx="50%" cy="34%" r="74%"><stop offset="0" stop-color="#22305a"/><stop offset=".6" stop-color="#121a2e"/><stop offset="1" stop-color="#070a12"/></radialGradient>
<radialGradient id="fondoOro" cx="38%" cy="28%" r="85%"><stop offset="0" stop-color="#f8e7b8"/><stop offset=".5" stop-color="#e6c682"/><stop offset="1" stop-color="#c79c50"/></radialGradient>
<linearGradient id="oro" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f8e8bb"/><stop offset=".45" stop-color="#dcbb76"/><stop offset="1" stop-color="#a9843e"/></linearGradient>
<linearGradient id="marfil" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset=".55" stop-color="#f2ece1"/><stop offset="1" stop-color="#d6ccb8"/></linearGradient>
<linearGradient id="titanio" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#eef1f6"/><stop offset="1" stop-color="#97a1b5"/></linearGradient>
<linearGradient id="azul" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3b4b78"/><stop offset="1" stop-color="#1a2440"/></linearGradient>
<linearGradient id="pantalla" x1="0" y1="0" x2=".7" y2="1"><stop offset="0" stop-color="#2a3756"/><stop offset=".55" stop-color="#131b2e"/><stop offset="1" stop-color="#090d17"/></linearGradient>
<linearGradient id="cuerpoNoche" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1b2338"/><stop offset="1" stop-color="#05070d"/></linearGradient>
<filter id="sombra" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="16" stdDeviation="20" flood-color="#000" flood-opacity=".42"/></filter>
<filter id="sombraOro" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="14" stdDeviation="18" flood-color="#5a3d0c" flood-opacity=".35"/></filter>
<filter id="sombraClara" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="10" stdDeviation="14" flood-color="#141824" flood-opacity=".18"/></filter>
</defs>'''

_n = [0]
def movil(cx, cy, w, h, cuerpo='url(#marfil)', pantalla='url(#pantalla)', isla='url(#oro)', borde=None, camara=None):
    """Movil de frente (con pantalla) o de espaldas (camara), centrado en cx, cy."""
    r = w * .24; b = w * .07
    s = f'<g transform="translate({cx},{cy})">'
    if borde:
        e = borde[1]
        s += f'<rect x="{-w/2-e}" y="{-h/2-e}" width="{w+2*e}" height="{h+2*e}" rx="{r+e}" fill="{borde[0]}"/>'
    s += f'<rect x="{-w/2}" y="{-h/2}" width="{w}" height="{h}" rx="{r}" fill="{cuerpo}"/>'
    if pantalla:
        _n[0] += 1; cp = f'pt{_n[0]}'
        sx, sy, sw, sh = -w/2 + b, -h/2 + b, w - 2*b, h - 2*b
        s += f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="{r-b}" fill="{pantalla}"/>'
        s += f'<clipPath id="{cp}"><rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="{r-b}"/></clipPath>'
        s += (f'<path clip-path="url(#{cp})" d="M{sx+sw*.55} {sy} L{sx+sw} {sy} L{sx+sw} {sy+sh*.18} '
              f'L{sx} {sy+sh*.62} L{sx} {sy+sh*.38} Z" fill="#fff" opacity=".055"/>')
    if isla:
        iw = w * .32; ih = w * .09
        s += f'<rect x="{-iw/2}" y="{-h/2+b+w*.06}" width="{iw}" height="{ih}" rx="{ih/2}" fill="{isla}"/>'
    if camara:
        m = w * .36; x = -w/2 + w*.1; y = -h/2 + w*.1
        s += f'<rect x="{x}" y="{y}" width="{m}" height="{m}" rx="{m*.3}" fill="{camara}" opacity=".9"/>'
        for ox, oy in ((.3, .3), (.7, .7)):
            s += f'<circle cx="{x+m*ox}" cy="{y+m*oy}" r="{m*.17}" fill="{NOCHE}" opacity=".55"/>'
    return s + '</g>'

def movil_p(tema):
    """Devuelve (svg, caja) en un marco de 1000 x 1000, centrado en 500, 500.
    tema: 'oro' y 'claro' -> silueta noche; 'noche' -> movil marfil y panza oro."""
    if tema == 'noche':
        panza, cuerpo, borde, filtro = 'url(#oro)', 'url(#marfil)', ('#0d1322', 16), 'sombra'
    else:
        panza, cuerpo, borde = NOCHE, 'url(#cuerpoNoche)', None
        filtro = 'sombraOro' if tema == 'oro' else 'sombraClara'
    w, h, x0, y0 = 250, 620, 300, 190
    grosor, r = 112, 150
    yt = y0 + grosor/2; yb = yt + 2*r; xs = x0 + w - 30
    ancho = (xs + 40 + r + grosor/2) - x0
    dx = 500 - (x0 + ancho/2)
    g = f'<path d="M{xs} {yt} H{xs+40} A{r} {r} 0 0 1 {xs+40} {yb} H{xs}" fill="none" stroke="{panza}" stroke-width="{grosor}"/>'
    g += movil(x0 + w/2, y0 + h/2, w, h, cuerpo=cuerpo, borde=borde)
    caja = (x0 + dx, y0, x0 + dx + ancho, y0 + h)
    return f'<g transform="translate({dx},0)" filter="url(#{filtro})">{g}</g>', caja

def abanico(tema):
    piv = (500, 860); ang = 26; w, h, cy = 260, 520, 520; dy = -28
    borde = ({'oro': '#e6c682', 'noche': '#0d1322', 'claro': PAPEL}[tema], 12)
    def girado(a, **k):
        return f'<g transform="rotate({a} {piv[0]} {piv[1]})">{movil(500, cy, w, h, **k)}</g>'
    if tema == 'oro':
        izq = girado(-ang, cuerpo='url(#marfil)', pantalla=None, isla=None, borde=borde, camara='#d6ccb8')
        der = girado(ang, cuerpo='url(#azul)', pantalla=None, isla=None, borde=borde, camara='#56689a')
        cen = girado(0, cuerpo='url(#cuerpoNoche)', borde=borde); filtro = 'sombraOro'
    else:
        izq = girado(-ang, cuerpo='url(#oro)', pantalla=None, isla=None, borde=borde, camara='#c7a35d')
        der = girado(ang, cuerpo='url(#titanio)' if tema == 'noche' else 'url(#azul)', pantalla=None, isla=None, borde=borde,
                     camara='#b7bfcd' if tema == 'noche' else '#56689a')
        cen = girado(0, cuerpo='url(#marfil)' if tema == 'noche' else 'url(#cuerpoNoche)', borde=borde)
        filtro = 'sombra' if tema == 'noche' else 'sombraClara'
    # caja: esquinas de los tres rectangulos girados
    xs, ys = [], []
    for a in (-ang, 0, ang):
        t = math.radians(a)
        for px, py in ((500-w/2-12, cy-h/2-12), (500+w/2+12, cy-h/2-12), (500-w/2-12, cy+h/2+12), (500+w/2+12, cy+h/2+12)):
            vx, vy = px - piv[0], py - piv[1]
            xs.append(piv[0] + vx*math.cos(t) - vy*math.sin(t)); ys.append(piv[1] + vx*math.sin(t) + vy*math.cos(t) + dy)
    caja = (min(xs), min(ys), max(xs), max(ys))
    return f'<g transform="translate(0,{dy})" filter="url(#{filtro})">{izq}{der}{cen}</g>', caja

SIMBOLOS = {'movil-p': movil_p, 'abanico': abanico}
FONDO = {'oro': 'url(#fondoOro)', 'noche': 'url(#fondo)', 'claro': PAPEL}

# ---------------------------------------------------------------- piezas
def svg_perfil(simbolo, tema, escala=1.0):
    g, caja = SIMBOLOS[simbolo](tema)
    cx = (caja[0] + caja[2]) / 2; cy = (caja[1] + caja[3]) / 2
    # que la silueta ocupe ~64 % del circulo
    s = escala * 640 / max(caja[2] - caja[0], caja[3] - caja[1])
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1080" width="1080" height="1080">{DEFS}'
            f'<rect width="1080" height="1080" fill="{FONDO[tema]}"/>'
            f'<g transform="translate(540,540) scale({s:.4f}) translate({-cx:.1f},{-cy:.1f})">{g}</g></svg>')

def svg_horizontal(simbolo, oscuro, fondo=True):
    """Logo horizontal: simbolo + pilla(tu)movil + MOVILES Y ACCESORIOS."""
    tema = 'noche' if oscuro else 'claro'
    g, caja = SIMBOLOS[simbolo](tema)
    alto_s = 560; s = alto_s / (caja[3] - caja[1]); ancho_s = (caja[2] - caja[0]) * s
    tinta = MARFIL if oscuro else TINTA; oro = ORO_TXT if oscuro else ORO_OSCURO
    gris = '#A9AEBB' if oscuro else '#5A5F6C'
    pad = 120; x_txt = pad + ancho_s + 90; T = 236
    pal, w_pal, (a1, b1) = texto_trazos(700, [('pilla', tinta), ('tu', oro), ('movil', tinta)], T, x_txt, 0, -0.035)
    # el lema ocupa el ancho de la palabra con un espaciado de 0,3 em
    LEMA = 'MÓVILES Y ACCESORIOS'
    _, w0, _ = texto_trazos(500, [(LEMA, gris)], 100, 0, 0, 0.3)
    TL = 100 * (w_pal - 8) / w0
    lema, w_lema, (a2, b2) = texto_trazos(500, [(LEMA, gris)], TL, 0, 0, 0.3)
    # bloque de texto: de lo alto de la "l" a la base del lema; centrado con el simbolo
    gap = 64
    alto_bloque = (0 - a1) + gap + (b2 - a2)
    H = alto_s + 2 * pad; top = (H - alto_bloque) / 2
    base1 = top - a1; base2 = base1 + gap - a2
    pal, w_pal, _ = texto_trazos(700, [('pilla', tinta), ('tu', oro), ('movil', tinta)], T, x_txt, base1, -0.035)
    lema, w_lema, _ = texto_trazos(500, [(LEMA, gris)], TL, x_txt + 8, base2, 0.3)
    W = x_txt + w_pal + pad
    sim = (f'<g transform="translate({pad:.1f},{pad:.1f}) scale({s:.4f}) translate({-caja[0]:.1f},{-caja[1]:.1f})">{g}</g>')
    fondo_svg = f'<rect width="{W:.0f}" height="{H:.0f}" fill="{"url(#fondoAncho)" if oscuro else PAPEL}"/>' if fondo else ''
    defs = DEFS.replace('</defs>', '<radialGradient id="fondoAncho" cx="35%" cy="30%" r="90%"><stop offset="0" stop-color="#1e2a4a"/><stop offset=".6" stop-color="#111829"/><stop offset="1" stop-color="#070a12"/></radialGradient></defs>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" width="{W:.0f}" height="{H:.0f}">{defs}'
            f'{fondo_svg}{sim}{pal}{lema}</svg>'), round(W), round(H)

def svg_simbolo(simbolo, tema):
    """Solo el simbolo, fondo transparente, cuadrado 1000 (favicon, marca de agua)."""
    g, caja = SIMBOLOS[simbolo](tema)
    cx = (caja[0] + caja[2]) / 2; cy = (caja[1] + caja[3]) / 2
    s = 860 / max(caja[2] - caja[0], caja[3] - caja[1])
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" width="1000" height="1000">{DEFS}'
            f'<g transform="translate(500,500) scale({s:.4f}) translate({-cx:.1f},{-cy:.1f})">{g}</g></svg>')

# ---------------------------------------------------------------- muestra
def mini(svg, tam):
    return svg.replace('width="1080" height="1080"', f'width="{tam}" height="{tam}" style="border-radius:50%;display:block;flex:none"', 1)

def chats(perfil, oscuro=True):
    """Lista de chats generica (no imita ninguna app) para ver el perfil a tamano real."""
    filas = [('Mamá', 'Vale, luego te llamo', '12:41', 'linear-gradient(135deg,#8a9bb0,#56637a)', 'M'),
             ('Pillatumovil', 'Su pedido sale hoy. Llega en 24-48 h', '12:30', None, ''),
             ('Fútbol martes', 'Carlos: ¿quién lleva el balón?', '11:58', 'linear-gradient(135deg,#7fb08a,#3f6b4d)', 'F'),
             ('Lucía', 'Foto', '10:15', 'linear-gradient(135deg,#d9a38f,#9b5f50)', 'L'),
             ('Trabajo', 'Ana: subo el informe', 'ayer', 'linear-gradient(135deg,#a79bd0,#5e5390)', 'T')]
    fondo, txt, sub, lin = ('#111b21', '#e9edef', '#8696a0', '#222d34') if oscuro else ('#ffffff', '#111b21', '#667781', '#e9edef')
    h = f'<div style="background:{fondo};border-radius:22px;padding:6px 0;width:420px;font-family:Inter,system-ui,sans-serif">'
    for n, m, t, grad, ini in filas:
        av = mini(perfil, 50) if grad is None else f'<div style="width:50px;height:50px;border-radius:50%;background:{grad};color:#fff;display:flex;align-items:center;justify-content:center;font-weight:600;font-size:20px;flex:none">{ini}</div>'
        h += (f'<div style="display:flex;align-items:center;gap:14px;padding:9px 16px;border-bottom:1px solid {lin}">{av}'
              f'<div style="flex:1;min-width:0"><div style="display:flex;justify-content:space-between"><b style="color:{txt};font-size:16px;font-weight:600">{n}</b>'
              f'<span style="color:{sub};font-size:12px">{t}</span></div><div style="color:{sub};font-size:14px;margin-top:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{m}</div></div></div>')
    return h + '</div>'

def muestra(piezas):
    """Hoja con las dos propuestas lado a lado."""
    col = ''
    for clave, titulo, nota in (('movil-p', 'Propuesta 1 · El móvil-P', 'La P de Pillatumovil hecha con un móvil. Silueta propia: se reconoce aunque sea diminuta.'),
                                ('abanico', 'Propuesta 2 · El abanico', 'Tres móviles abiertos como cartas: «aquí hay móviles para elegir».')):
        p = piezas[clave]
        col += f'''<section>
<h2>{titulo}</h2><p class="nota">{nota}</p>
<div class="fila">{mini(p['perfil-oro'], 300)}{mini(p['perfil-noche'], 300)}</div>
<div class="fila peq">{''.join(mini(p['perfil-oro'], t) for t in (96, 56, 36))}<span class="sep"></span>{''.join(mini(p['perfil-noche'], t) for t in (96, 56, 36))}</div>
<div class="ancho">{p['h-oscuro'][0].replace('<svg ', '<svg style="width:100%;height:auto;display:block;border-radius:14px" ', 1)}</div>
<div class="ancho">{p['h-claro'][0].replace('<svg ', '<svg style="width:100%;height:auto;display:block;border-radius:14px;box-shadow:0 0 0 1px #e2ddd2" ', 1)}</div>
<div class="fila">{chats(p['perfil-oro'], True)}</div>
</section>'''
    return f'''<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<style>body{{margin:0;background:#e9e7e2;font-family:Inter,sans-serif;color:#141824;padding:48px;display:grid;grid-template-columns:1fr 1fr;gap:48px;width:1600px;box-sizing:border-box}}
section{{background:#fff;border-radius:28px;padding:36px;display:flex;flex-direction:column;gap:24px}}
h2{{margin:0;font-size:30px}} .nota{{margin:-14px 0 0;color:#5a5f6c;font-size:17px}}
.fila{{display:flex;gap:24px;align-items:center;justify-content:center}} .peq{{gap:16px}} .sep{{width:20px}}</style></head>
<body>{col}</body></html>'''

# ---------------------------------------------------------------- pintar
def pintar(trabajos):
    """trabajos: [(html, png, ancho, alto, transparente)]"""
    js = os.path.join(tempfile.mkdtemp(), 'pintar.js')
    open(js, 'w').write('''const { chromium } = require('playwright');
const t = JSON.parse(process.argv[2]);
(async () => { const b = await chromium.launch();
  for (const [h, png, w, ht, tr] of t) { const p = await b.newPage({ viewport: { width: w, height: ht }, deviceScaleFactor: 1 });
    await p.goto('file://' + h, { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(250);
    await p.screenshot({ path: png, omitBackground: !!tr, fullPage: true }); await p.close(); }
  await b.close(); })();''')
    r = subprocess.run(['node', js, json.dumps(trabajos)], capture_output=True, text=True)
    if r.returncode: print(r.stderr[-800:])

def envolver(svg, w, h, transparente=False):
    bg = 'transparent' if transparente else '#000'
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0;width:{w}px;height:{h}px;'
            f'overflow:hidden;background:{bg}}}svg{{display:block}}</style></head><body>{svg}</body></html>')

if __name__ == '__main__':
    salida = os.path.abspath(sys.argv[1]); os.makedirs(salida, exist_ok=True)
    tmp = tempfile.mkdtemp(); trabajos = []; piezas = {}
    def pieza(nombre, svg, w, h, transparente=False):
        open(os.path.join(salida, nombre + '.svg'), 'w').write(svg)
        ruta = os.path.join(tmp, nombre + '.html'); open(ruta, 'w').write(envolver(svg, w, h, transparente))
        trabajos.append((ruta, os.path.join(salida, nombre + '.png'), w, h, transparente))
    for clave in SIMBOLOS:
        p = piezas[clave] = {}
        for tema in ('oro', 'noche'):
            p[f'perfil-{tema}'] = svg_perfil(clave, tema)
            pieza(f'{clave}_perfil-{tema}', p[f'perfil-{tema}'], 1080, 1080)
        for oscuro, nombre in ((True, 'oscuro'), (False, 'claro')):
            p[f'h-{nombre}'] = svg_horizontal(clave, oscuro)
            pieza(f'{clave}_logo-horizontal-{nombre}', *p[f'h-{nombre}'])
            svg, w, h = svg_horizontal(clave, oscuro, fondo=False)
            pieza(f'{clave}_logo-horizontal-{nombre}-transparente', svg, w, h, True)
        pieza(f'{clave}_simbolo-transparente', svg_simbolo(clave, 'oro'), 1000, 1000, True)
    ruta = os.path.join(tmp, 'muestra.html'); open(ruta, 'w').write(muestra(piezas))
    trabajos.append((ruta, os.path.join(salida, 'muestra-marca-v3.png'), 1600, 1000, False))
    pintar(trabajos)
    print('\n'.join(sorted(os.listdir(salida))))
