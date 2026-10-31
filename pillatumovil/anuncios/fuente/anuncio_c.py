# Anuncio C (estilo nativo / "lo-fi"): la foto REAL del stock del dueno
# (fotos/reales/cajas-frente-usb-c.jpg) a sangre, con etiquetas de texto como
# las de Instagram. Mismo precio, misma comparacion y el mismo eslogan.
# uso: python3 anuncio_c.py [feed|story|cuadrado ...]
import os, sys, json, subprocess
from anuncio import AQUI, REPO, LOGO, CHECK, W2, b64

FOTO = b64(os.path.join(REPO, 'fotos/reales/cajas-frente-usb-c.jpg'), 'image/jpeg')

def html(w, h, l):
    return f'''<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:{w}px;height:{h}px;overflow:hidden}}
body{{position:relative;background:#0b0f1a;font-family:Archivo,sans-serif;-webkit-font-smoothing:antialiased}}
.foto{{position:absolute;inset:0;background:url({FOTO}) {l['pos']}/{l['zoom']}}}
.velo{{position:absolute;inset:0;background:linear-gradient(0deg,rgba(11,15,26,.88) 0%,rgba(11,15,26,.55) {l['v1']}%,rgba(11,15,26,0) {l['v2']}%)}}
.arriba{{position:absolute;left:{l['pad']}px;right:{l['pad']}px;top:{l['arriba_y']}px;display:flex;flex-direction:column;align-items:flex-start;gap:{l['gap']}px}}
.et{{display:inline-block;padding:{l['et_py']}px {l['et_px']}px;border-radius:{l['et_r']}px;background:#fff;color:#0b0f1a;font-size:{l['et']}px;font-weight:700;line-height:1.15;letter-spacing:-.015em;box-shadow:0 6px 24px -10px rgba(0,0,0,.45)}}
.et--oro{{background:#c9a86a;color:#0b0f1a}}
.et--noche{{background:#0b0f1a;color:#f4f1ea}}
.et small{{font-size:.7em;font-weight:600}}
.abajo{{position:absolute;left:{l['pad']}px;right:{l['pad']}px;bottom:{l['abajo_b']}px;color:#f4f1ea}}
.precio{{display:flex;align-items:flex-end;gap:20px}}
.precio b{{font-size:{l['precio']}px;font-weight:800;letter-spacing:-.045em;line-height:.85}}
.precio b small{{font-size:.5em;margin-left:4px}}
.precio span{{padding-bottom:8px;font-size:{l['apple']}px;line-height:1.3;color:#d9dbe1}}
.precio span strong{{color:#f4f1ea}}
.checks{{display:flex;flex-wrap:wrap;gap:6px 22px;list-style:none;margin-top:{l['checks_mt']}px;font-size:{l['checks']}px;font-weight:600}}
.checks li{{display:flex;align-items:center;gap:8px;white-space:nowrap}}
.marca{{display:flex;align-items:center;justify-content:space-between;margin-top:{l['marca_mt']}px}}
.marca img{{height:{l['logo_h']}px}}
.marca p{{font-size:{l['web']}px;font-weight:600;color:#e2cc9a}}
.letra{{margin-top:10px;font-size:{l['letra']}px;line-height:1.35;color:rgba(217,219,225,.62)}}
</style></head><body>
<div class="foto"></div><div class="velo"></div>
<div class="arriba">
  <p class="et et--noche">Ganamos menos por cada pack. <span style="color:#e2cc9a">A propósito.</span></p>
  <p class="et">Cargador de 20 W + cable,<br>originales de Apple</p>
  <p class="et et--oro">Nuevos y precintados</p>
</div>
<div class="abajo">
  <div class="precio"><b>18,99<small>€</small></b><span>el pack completo<br>En Apple, por separado: <strong>38 €</strong></span></div>
  <ul class="checks"><li>{CHECK}Envío gratis 24{W2}-{W2}48&nbsp;h</li><li>{CHECK}3 años de garantía</li><li>{CHECK}14 días para devolverlo</li></ul>
  <div class="marca"><img src="{LOGO}" alt=""><p>pillatumovil.com</p></div>
  <p class="letra">Foto real de nuestro stock. Pack de 1: adaptador de 20 W + cable de 1 m (USB-C o Lightning). En Apple (apple.com/es, 29/10/2026): adaptador, 19 €; cable, 19 €. Pillatumovil no está afiliado a Apple.</p>
</div>
</body></html>'''

FORMATOS = {
    'feed': (1080, 1350, dict(pad=56, pos='100% 50%', zoom='auto 126%', v1=34, v2=60,
                               arriba_y=56, gap=14, et=34, et_px=22, et_py=14, et_r=14,
                               abajo_b=34, precio=150, apple=27, checks_mt=20, checks=25, marca_mt=24, logo_h=34, web=24, letra=15)),
    # Stories / Reels: todo entre 250 px arriba y 330 px abajo
    'story': (1080, 1920, dict(pad=60, pos='88% 50%', zoom='cover', v1=36, v2=62,
                                arriba_y=270, gap=16, et=38, et_px=24, et_py=15, et_r=15,
                                abajo_b=340, precio=160, apple=29, checks_mt=22, checks=27, marca_mt=24, logo_h=36, web=26, letra=16)),
    'cuadrado': (1080, 1080, dict(pad=46, pos='100% 52%', zoom='auto 146%', v1=36, v2=64,
                                   arriba_y=40, gap=10, et=27, et_px=18, et_py=11, et_r=12,
                                   abajo_b=24, precio=112, apple=22, checks_mt=14, checks=20, marca_mt=16, logo_h=28, web=20, letra=12)),
}

if __name__ == '__main__':
    trabajos = []
    for n in (sys.argv[1:] or list(FORMATOS)):
        w, h, l = FORMATOS[n]
        ruta = os.path.join(AQUI, f'anuncio-c-{n}.html')
        open(ruta, 'w').write(html(w, h, l))
        trabajos.append((ruta, os.path.join(AQUI, f'anuncio-c-{n}.png'), w, h))
    print(subprocess.run(['node', os.path.join(AQUI, 'pintar.js'), json.dumps(trabajos)], capture_output=True, text=True, cwd=AQUI).stdout)
