# Anuncio B: foto de la mesilla a sangre, gancho "Mismo cargador. Misma caja.
# Mitad de precio." (estilo Back Market) y el mismo precio.
# uso: python3 anuncio_b.py [feed|story|cuadrado ...]
import os, sys, json, subprocess
from anuncio import AQUI, REPO, LOGO, CAMION, CHECK, W2, b64

FOTO = b64(os.path.join(REPO, 'estudio-ia/ps-mesilla.jpg'), 'image/jpeg')

def html(w, h, l):
    return f'''<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:{w}px;height:{h}px;overflow:hidden}}
body{{position:relative;background:#0b0f1a;color:#f4f1ea;font-family:Archivo,sans-serif;-webkit-font-smoothing:antialiased}}
.foto{{position:absolute;inset:0;background:url({FOTO}) {l['foto_pos']}/cover}}
.velo{{position:absolute;inset:0;background:
  linear-gradient(180deg,rgba(11,15,26,.92) 0%,rgba(11,15,26,.78) {l['v1']}%,rgba(11,15,26,0) {l['v2']}%),
  linear-gradient(0deg,rgba(11,15,26,.97) 0%,rgba(11,15,26,.9) {l['v3']}%,rgba(11,15,26,0) {l['v4']}%)}}
.cinta{{position:absolute;left:0;right:0;top:{l['cinta_y']}px;height:{l['cinta_h']}px;display:flex;align-items:center;justify-content:center;gap:12px;background:linear-gradient(90deg,#d9c08a 0%,#e9d7ad 50%,#d9c08a 100%);color:#0b0f1a;font-size:{l['cinta']}px;font-weight:800;letter-spacing:.07em;text-transform:uppercase;white-space:nowrap}}
.cinta i{{font-style:normal;font-weight:600;letter-spacing:0;text-transform:none}}
.logo{{position:absolute;left:{l['pad']}px;top:{l['logo_y']}px;height:{l['logo_h']}px}}
.cab{{position:absolute;left:{l['pad']}px;right:{l['pad']}px;top:{l['cab_y']}px}}
.gancho{{font-size:{l['gancho']}px;font-weight:700;line-height:1;letter-spacing:-.04em}}
.gancho em{{font-style:normal;color:#e2cc9a}}
.prod{{margin-top:{l['prod_mt']}px;font-size:{l['prod']}px;font-weight:500;line-height:1.3;color:#d6d3cc}}
.prod b{{color:#f4f1ea;font-weight:600}}
.pie{{position:absolute;left:{l['pad']}px;right:{l['pad']}px;top:{l['pie_y']}px}}
.fila{{display:flex;align-items:center;gap:24px}}
.precio{{font-size:{l['precio']}px;font-weight:800;letter-spacing:-.045em;line-height:.9;font-variant-numeric:tabular-nums}}
.precio small{{font-size:.55em;font-weight:700;letter-spacing:-.02em;margin-left:6px}}
.cod{{display:flex;flex-direction:column;gap:6px}}
.cod span{{font-size:{l['cod_t']}px;font-weight:500;color:#c9ccd4}}
.cod b{{display:inline-block;padding:10px 20px;border-radius:12px;border:0;padding:0;background:none;color:#e2cc9a;font-size:{l['cod']}px;font-weight:700;letter-spacing:-.01em}}
.apple{{margin-top:{l['apple_mt']}px;font-size:{l['apple']}px;color:#c9ccd4}}
.apple b{{color:#f4f1ea;font-weight:600}}
.sello{{display:inline-flex;align-items:center;gap:14px;margin-top:{l['sello_mt']}px;padding:16px 30px;border-radius:999px;background:#c9a86a;color:#0b0f1a;font-size:{l['sello']}px;font-weight:700}}
.checks{{display:flex;flex-wrap:wrap;justify-content:flex-start;gap:8px 26px;list-style:none;margin-top:{l['sello_mt']}px;font-size:{l['sello']}px;font-weight:600;color:#f4f1ea}}
.checks li{{display:flex;align-items:center;gap:8px;white-space:nowrap}}
.letra{{position:absolute;left:{l['pad']}px;right:{l['pad']}px;bottom:{l['letra_b']}px;font-size:{l['letra']}px;line-height:1.4;color:rgba(201,204,212,.62)}}
</style></head><body>
<div class="foto"></div><div class="velo"></div>
<div class="cinta">Ganamos menos por cada pack. <i>A propósito.</i></div>
<img class="logo" src="{LOGO}" alt="">
<div class="cab">
  <p class="gancho">Mismo cargador.<br>Misma caja.<br><em>Mitad de precio.</em></p>
  <p class="prod"><b>Cargador de 20 W + cable USB-C o Lightning.</b><br>Originales de Apple, nuevos y precintados.</p>
</div>
<div class="pie">
  <div class="fila">
    <p class="precio">18,99<small>€</small></p>
    <p class="cod"><span>el pack completo:</span><b>cargador + cable</b></p>
  </div>
  <p class="apple">En Apple, por separado: <b>38 €</b></p>
  <ul class="checks"><li>{CHECK}Envío gratis 24{W2}-{W2}48&nbsp;h</li><li>{CHECK}3 años de garantía</li><li>{CHECK}14 días para devolverlo</li></ul>
</div>
<p class="letra">Pack de 1: adaptador de 20 W + cable de 1 m (USB-C o Lightning). En Apple (apple.com/es, 29/10/2026): adaptador de 20 W, 19 €; cable de 1 m, 19 €. Imagen de ambiente. Pillatumovil no está afiliado a Apple.</p>
</body></html>'''

FORMATOS = {
    'feed': (1080, 1350, dict(pad=64, foto_pos='center 40%', v1=32, v2=56, v3=22, v4=50, cinta_y=0, cinta_h=72, cinta=28,
                               logo_y=102, logo_h=36, cab_y=166, gancho=78, prod_mt=20, prod=29,
                               pie_y=1012, precio=128, cod_t=24, cod=32, apple_mt=14, apple=26, sello_mt=18, sello=26,
                               letra_b=18, letra=16)),
    'story': (1080, 1920, dict(pad=64, foto_pos='center 45%', v1=34, v2=52, v3=34, v4=58, cinta_y=262, cinta_h=74, cinta=29,
                                logo_y=362, logo_h=36, cab_y=424, gancho=84, prod_mt=22, prod=30,
                                pie_y=1262, precio=128, cod_t=24, cod=32, apple_mt=14, apple=26, sello_mt=18, sello=26,
                                letra_b=338, letra=16)),
    'cuadrado': (1080, 1080, dict(pad=54, foto_pos='center 42%', v1=34, v2=58, v3=26, v4=56, cinta_y=0, cinta_h=54, cinta=22,
                                   logo_y=74, logo_h=30, cab_y=122, gancho=58, prod_mt=14, prod=23,
                                   pie_y=772, precio=104, cod_t=20, cod=28, apple_mt=8, apple=22, sello_mt=12, sello=22,
                                   letra_b=12, letra=13)),
}

if __name__ == '__main__':
    trabajos = []
    for n in (sys.argv[1:] or list(FORMATOS)):
        w, h, l = FORMATOS[n]
        ruta = os.path.join(AQUI, f'anuncio-b-{n}.html')
        open(ruta, 'w').write(html(w, h, l))
        trabajos.append((ruta, os.path.join(AQUI, f'anuncio-b-{n}.png'), w, h))
    print(subprocess.run(['node', os.path.join(AQUI, 'pintar.js'), json.dumps(trabajos)], capture_output=True, text=True, cwd=AQUI).stdout)
