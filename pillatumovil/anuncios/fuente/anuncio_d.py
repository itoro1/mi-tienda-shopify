# Anuncio D ("definitivo"): lectura en un segundo.
#   arriba (noche): CARGADOR iPHONE / ORIGINAL APPLE
#   centro (blanco): la foto real del pack, grande, con la pegatina de precio
#   abajo (noche): ENVIO GRATIS · En su casa en 24-48 h
# Poco texto, un solo foco, precio pegado al producto (ver estudio-anuncios).
# uso: python3 anuncio_d.py [feed|story|cuadrado ...]
import os, sys, json, subprocess
from PIL import Image
from anuncio import AQUI, REPO, LOGO, CHECK, W2, b64

def recorte(src, dst, caja):
    im = Image.open(src).convert('RGB').crop(caja)
    im.save(dst, quality=95)
    return dst

PACK = b64(recorte(os.path.join(REPO, 'fotos/pack-cargador-cable-usb-c_shopify.jpg'),
                   os.path.join(AQUI, 'pack-blanco.jpg'), (150, 430, 1950, 1700)), 'image/jpeg')
CAMION = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M2.5 6.5h11v10h-11z"/><path d="M13.5 9.5h4l3 3.2v3.8h-7"/><circle cx="6.5" cy="17.5" r="1.8"/><circle cx="17" cy="17.5" r="1.8"/></svg>'

def html(w, h, l):
    return f'''<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..900&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:{w}px;height:{h}px;overflow:hidden}}
body{{position:relative;background:#0b0f1a;color:#f4f1ea;font-family:Archivo,sans-serif;-webkit-font-smoothing:antialiased}}
.cab{{position:absolute;left:0;right:0;top:{l['cab_y']}px;height:{l['cab_h']}px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}}
.t1{{font-size:{l['t1']}px;font-weight:900;font-stretch:72%;line-height:.92;letter-spacing:-.01em;text-transform:uppercase}}
.t1 i{{font-style:normal;text-transform:none}}
.t2{{margin-top:{l['t2_mt']}px;font-size:{l['t2']}px;font-weight:800;font-stretch:80%;letter-spacing:.06em;text-transform:uppercase;color:#e2cc9a}}
.blanco{{position:absolute;left:0;right:0;top:{l['bl_y']}px;height:{l['bl_h']}px;background:#fff}}
.pack{{position:absolute;left:{l['pk_x']}px;top:{l['pk_y']}px;width:{l['pk_w']}px}}
.chip{{position:absolute;left:{l['chip_x']}px;top:{l['chip_y']}px;padding:10px 18px;border-radius:999px;background:#f1efe9;color:#141824;font-size:{l['chip']}px;font-weight:700}}
.pega{{position:absolute;left:{l['pg_x']}px;top:{l['pg_y']}px;width:{l['pg']}px;height:{l['pg']}px;border-radius:50%;
  background:radial-gradient(circle at 35% 30%,#f0dba6 0%,#d9bb7c 45%,#b8954f 100%);color:#0b0f1a;
  display:flex;flex-direction:column;align-items:center;justify-content:center;transform:rotate(-9deg);
  box-shadow:0 18px 40px -14px rgba(11,15,26,.55),inset 0 0 0 6px rgba(255,255,255,.35)}}
.pega b{{font-size:{l['pg_precio']}px;font-weight:900;font-stretch:80%;letter-spacing:-.03em;line-height:.9}}
.pega b small{{font-size:.55em;margin-left:2px}}
.pega span{{margin-top:6px;font-size:{l['pg_t']}px;font-weight:700;letter-spacing:.02em;text-transform:uppercase}}
.apple{{position:absolute;left:{l['ap_x']}px;top:{l['ap_y']}px;transform:rotate(-9deg);padding:10px 18px;border-radius:12px;background:#0b0f1a;color:#d9dbe1;font-size:{l['ap']}px;font-weight:600;box-shadow:0 10px 24px -12px rgba(11,15,26,.6)}}
.apple s{{color:#f4f1ea;font-weight:800;text-decoration-thickness:3px;text-decoration-color:#e35d5d}}
.pie{{position:absolute;left:0;right:0;top:{l['pie_y']}px;display:flex;flex-direction:column;align-items:center;text-align:center}}
.envio{{display:flex;align-items:center;gap:18px;font-size:{l['envio']}px;font-weight:900;font-stretch:72%;line-height:1;text-transform:uppercase;letter-spacing:.005em}}
.envio svg{{width:{l['camion']}px;height:{l['camion']}px;color:#e2cc9a;flex:none}}
.plazo{{margin-top:{l['plazo_mt']}px;font-size:{l['plazo']}px;font-weight:700;color:#e2cc9a}}
.mas{{display:flex;gap:10px 26px;margin-top:{l['mas_mt']}px;font-size:{l['mas']}px;font-weight:600;color:#d9dbe1}}
.mas span{{display:flex;align-items:center;gap:8px}}
.firma{{position:absolute;left:0;right:0;bottom:{l['firma_b']}px;display:flex;flex-direction:column;align-items:center;gap:8px}}
.firma img{{height:{l['logo_h']}px}}
.firma p{{max-width:92%;font-size:{l['letra']}px;line-height:1.3;color:rgba(217,219,225,.55);text-align:center}}
</style></head><body>
<div class="cab">
  <p class="t1">Cargador <i>iPhone</i></p>
  <p class="t2">Original Apple · 20 W + cable</p>
</div>
<div class="blanco"></div>
<img class="pack" src="{PACK}" alt="">
<p class="chip">USB-C o Lightning</p>
<div class="pega"><b>18,99<small>€</small></b><span>el pack</span></div>
<p class="apple">En Apple: <s>38&nbsp;€</s></p>
<div class="pie">
  <p class="envio">{CAMION}Envío gratis</p>
  <p class="plazo">En su casa en 24{W2}-{W2}48&nbsp;h</p>
  <p class="mas"><span>{CHECK}Nuevo y precintado</span><span>{CHECK}3 años de garantía</span></p>
</div>
<div class="firma"><img src="{LOGO}" alt=""><p>En Apple (apple.com/es, 29/10/2026): adaptador de 20 W, 19 €; cable de 1 m, 19 €. Pillatumovil no está afiliado a Apple.</p></div>
</body></html>'''

FORMATOS = {
    'feed': (1080, 1350, dict(cab_y=0, cab_h=250, t1=118, t2=34, t2_mt=14,
                               bl_y=250, bl_h=660, pk_x=40, pk_y=300, pk_w=820, chip_x=56, chip_y=850, chip=24,
                               pg_x=742, pg_y=272, pg=300, pg_precio=104, pg_t=24, ap_x=770, ap_y=600, ap=26,
                               pie_y=972, envio=116, camion=100, plazo=42, plazo_mt=12, mas=26, mas_mt=22,
                               firma_b=22, logo_h=40, letra=13)),
    # Stories/Reels: todo entre 250 px arriba y 340 px abajo
    'story': (1080, 1920, dict(cab_y=250, cab_h=260, t1=124, t2=36, t2_mt=14,
                                bl_y=520, bl_h=700, pk_x=40, pk_y=580, pk_w=840, chip_x=56, chip_y=1150, chip=26,
                                pg_x=740, pg_y=540, pg=310, pg_precio=108, pg_t=25, ap_x=772, ap_y=878, ap=27,
                                pie_y=1262, envio=108, camion=96, plazo=40, plazo_mt=10, mas=26, mas_mt=18,
                                firma_b=345, logo_h=36, letra=14)),
    'cuadrado': (1080, 1080, dict(cab_y=0, cab_h=200, t1=96, t2=28, t2_mt=10,
                                   bl_y=200, bl_h=560, pk_x=110, pk_y=236, pk_w=700, chip_x=60, chip_y=700, chip=22,
                                   pg_x=760, pg_y=214, pg=250, pg_precio=86, pg_t=20, ap_x=790, ap_y=490, ap=22,
                                   pie_y=788, envio=84, camion=74, plazo=30, plazo_mt=8, mas=20, mas_mt=12,
                                   firma_b=14, logo_h=26, letra=11)),
}

if __name__ == '__main__':
    trabajos = []
    for n in (sys.argv[1:] or list(FORMATOS)):
        w, h, l = FORMATOS[n]
        ruta = os.path.join(AQUI, f'anuncio-d-{n}.html')
        open(ruta, 'w').write(html(w, h, l))
        trabajos.append((ruta, os.path.join(AQUI, f'anuncio-d-{n}.png'), w, h))
    print(subprocess.run(['node', os.path.join(AQUI, 'pintar.js'), json.dumps(trabajos)], capture_output=True, text=True, cwd=AQUI).stdout)
