# Foto de perfil "currada" de Pillatumovil: la P dibujada como un cargador
# (asta con las dos clavijas del enchufe europeo, panza de la P y un rayo de
# carga en oro dentro). Dos versiones:
#   emblema: anillo dorado con "PILLATUMOVIL · CARGADORES ORIGINALES"
#   marca:   solo la P-cargador, grande (se lee mejor en pequeno)
# Se pinta en HTML/SVG con Playwright (letra Archivo de Google Fonts).
# uso: python3 perfil_emblema.py CARPETA_SALIDA
import os, sys, json, subprocess, tempfile

NOCHE = '#0b0f1a'; MARFIL = '#f4efe6'

DEFS = '''
<defs>
  <radialGradient id="fondo" cx="50%" cy="42%" r="62%">
    <stop offset="0" stop-color="#1d2740"/><stop offset=".55" stop-color="#111829"/><stop offset="1" stop-color="#070a12"/>
  </radialGradient>
  <linearGradient id="oro" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#f3e2b5"/><stop offset=".35" stop-color="#d9bb7c"/><stop offset=".7" stop-color="#b8954f"/><stop offset="1" stop-color="#e9d3a0"/>
  </linearGradient>
  <linearGradient id="marfil" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fbf8f2"/><stop offset="1" stop-color="#e6dfd2"/>
  </linearGradient>
  <linearGradient id="clavija" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#9a7b3e"/><stop offset=".45" stop-color="#f3e2b5"/><stop offset="1" stop-color="#a8864a"/>
  </linearGradient>
  <filter id="sombra" x="-20%" y="-20%" width="140%" height="140%">
    <feDropShadow dx="0" dy="14" stdDeviation="18" flood-color="#000" flood-opacity=".45"/>
  </filter>
</defs>'''

def p_cargador(cx, cy, s):
    """La P-cargador centrada en (cx, cy), escala s (1 = unos 580 px de alto)."""
    # Sistema propio: caja de la marca x 124..534, y 40..616 (centro 329, 328).
    return f'''
<g transform="translate({cx},{cy}) scale({s}) translate(-329,-328)" filter="url(#sombra)">
  <!-- asta -->
  <rect x="150" y="40" width="108" height="432" rx="18" fill="url(#marfil)"/>
  <!-- panza de la P -->
  <path d="M204 92 H350 A132 132 0 0 1 350 356 H204" fill="none" stroke="url(#marfil)" stroke-width="104"/>
  <!-- cuerpo del enchufe al pie del asta -->
  <rect x="124" y="452" width="160" height="60" rx="22" fill="url(#marfil)"/>
  <!-- clavijas del enchufe europeo -->
  <rect x="158" y="506" width="26" height="110" rx="13" fill="url(#clavija)"/>
  <rect x="224" y="506" width="26" height="110" rx="13" fill="url(#clavija)"/>
  <!-- rayo de carga, dentro del hueco de la P -->
  <path transform="translate(309,160) scale(.79)" d="M54 0 L0 88 H40 L16 162 L88 60 H46 L74 0 Z" fill="url(#oro)"/>
</g>'''

def svg_emblema():
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1080" width="1080" height="1080">{DEFS}
<rect width="1080" height="1080" fill="url(#fondo)"/>
<circle cx="540" cy="540" r="468" fill="none" stroke="url(#oro)" stroke-width="10"/>
<circle cx="540" cy="540" r="440" fill="none" stroke="url(#oro)" stroke-width="2.5" opacity=".7"/>
<circle cx="540" cy="540" r="318" fill="none" stroke="url(#oro)" stroke-width="2.5" opacity=".7"/>
<path id="arribaT" d="M 162 540 A 378 378 0 0 1 918 540" fill="none"/>
<path id="abajoT" d="M 140 540 A 400 400 0 0 0 940 540" fill="none"/>
<text font-family="Archivo" font-weight="800" font-size="66" letter-spacing="14" fill="{MARFIL}">
  <textPath href="#arribaT" startOffset="50%" text-anchor="middle">PILLATUMOVIL</textPath></text>
<text font-family="Archivo" font-weight="700" font-size="40" letter-spacing="9" fill="url(#oro)">
  <textPath href="#abajoT" startOffset="50%" text-anchor="middle">CARGADORES ORIGINALES</textPath></text>
<path transform="translate(116,540) scale(.42) translate(-40,-80)" d="M54 0 L0 88 H40 L16 162 L88 60 H46 L74 0 Z" fill="url(#oro)"/>
<path transform="translate(964,540) scale(.42) translate(-40,-80)" d="M54 0 L0 88 H40 L16 162 L88 60 H46 L74 0 Z" fill="url(#oro)"/>
{p_cargador(540, 548, .78)}
</svg>'''

def svg_marca():
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1080" width="1080" height="1080">{DEFS}
<rect width="1080" height="1080" fill="url(#fondo)"/>
<circle cx="540" cy="540" r="452" fill="none" stroke="url(#oro)" stroke-width="7" opacity=".9"/>
{p_cargador(548, 552, 1.0)}
</svg>'''

def pagina(svg):
    return f'''<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@700;800&display=swap" rel="stylesheet">
<style>html,body{{margin:0;width:1080px;height:1080px;overflow:hidden;background:{NOCHE}}}svg{{display:block}}</style>
</head><body>{svg}</body></html>'''

if __name__ == '__main__':
    salida = os.path.abspath(sys.argv[1]); os.makedirs(salida, exist_ok=True)
    tmp = tempfile.mkdtemp()
    trabajos = []
    for nombre, svg in [('perfil-pillatumovil-emblema', svg_emblema()), ('perfil-pillatumovil-marca', svg_marca())]:
        h = os.path.join(tmp, nombre + '.html'); open(h, 'w').write(pagina(svg))
        open(os.path.join(salida, nombre + '.svg'), 'w').write(svg)
        trabajos.append((h, os.path.join(salida, nombre + '.png')))
    js = os.path.join(tmp, 'pintar.js')
    open(js, 'w').write('''const { chromium } = require('playwright');
const t = JSON.parse(process.argv[2]);
(async () => { const b = await chromium.launch();
  for (const [h, png] of t) { const p = await b.newPage({ viewport: { width: 1080, height: 1080 }, deviceScaleFactor: 1 });
    await p.goto('file://' + h, { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
    await p.screenshot({ path: png }); await p.close(); }
  await b.close(); })();''')
    r = subprocess.run(['node', js, json.dumps(trabajos)], capture_output=True, text=True)
    print(r.stdout, r.stderr[-500:])
