# Anuncio E: los DOS packs, para que cada cual vea el suyo de un vistazo.
#   arriba (noche): CARGADOR iPHONE / ORIGINAL APPLE
#   cinta (oro): PRECIO DE LANZAMIENTO · HASTA FIN DE EXISTENCIAS
#   centro (blanco): pack USB-C y pack Lightning con su etiqueta de iPhone,
#                    pegatina 18,99 € cada pack y "En Apple: 38 €"
#   abajo (noche): ENVIO GRATIS · En su casa en 24-48 h
# "Hasta fin de existencias" es verdad mientras el dueno suba el precio al
# acabarse el stock actual (lo dijo el 01/11/2026).
# uso: python3 anuncio_e.py [feed|story|cuadrado ...]
import os, sys, json, subprocess
from PIL import Image
from anuncio import AQUI, REPO, LOGO, CHECK, W2, b64

def recorte(src, dst, caja):
    Image.open(src).convert('RGB').crop(caja).save(dst, quality=95)
    return dst

CAJA = (210, 505, 1865, 1720)   # las dos cajas de cada pack, con aire
USBC = b64(recorte(os.path.join(REPO, 'fotos/pack-cargador-cable-usb-c_shopify.jpg'), os.path.join(AQUI, 'pack-usbc-blanco.jpg'), CAJA), 'image/jpeg')
LTN = b64(recorte(os.path.join(REPO, 'fotos/pack-cargador-cable-lightning_shopify.jpg'), os.path.join(AQUI, 'pack-ltn-blanco.jpg'), CAJA), 'image/jpeg')
CAMION = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M2.5 6.5h11v10h-11z"/><path d="M13.5 9.5h4l3 3.2v3.8h-7"/><circle cx="6.5" cy="17.5" r="1.8"/><circle cx="17" cy="17.5" r="1.8"/></svg>'

def html(w, h, l):
    return f'''<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..900&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:{w}px;height:{h}px;overflow:hidden}}
body{{position:relative;background:#0b0f1a;color:#f4f1ea;font-family:Archivo,sans-serif;-webkit-font-smoothing:antialiased}}
.cab{{position:absolute;left:0;right:0;top:{l['cab_y']}px;height:{l['cab_h']}px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}}
.t1{{font-size:{l['t1']}px;font-weight:900;font-stretch:72%;line-height:.92;text-transform:uppercase}}
.t1 i{{font-style:normal;text-transform:none}}
.t2{{margin-top:{l['t2_mt']}px;font-size:{l['t2']}px;font-weight:800;font-stretch:80%;letter-spacing:.06em;text-transform:uppercase;color:#e2cc9a}}
.cinta{{position:absolute;left:0;right:0;top:{l['ci_y']}px;height:{l['ci_h']}px;display:flex;align-items:center;justify-content:center;gap:14px;
  background:linear-gradient(90deg,#d9c08a 0%,#ecd9ae 50%,#d9c08a 100%);color:#0b0f1a;font-size:{l['ci']}px;font-weight:900;font-stretch:80%;letter-spacing:.05em;text-transform:uppercase;white-space:nowrap}}
.cinta i{{font-style:normal;font-weight:700;letter-spacing:.02em}}
.blanco{{position:absolute;left:0;right:0;top:{l['bl_y']}px;height:{l['bl_h']}px;background:#fff}}
.elija{{position:absolute;left:{l['el_x']}px;top:{l['el_y']}px;color:#141824;font-size:{l['el']}px;font-weight:900;font-stretch:78%;line-height:1;text-transform:uppercase}}
.elija small{{display:block;margin-top:8px;font-size:.5em;font-weight:700;font-stretch:90%;letter-spacing:.02em;text-transform:none;color:#585d6b}}
.packs{{position:absolute;left:{l['pk_x']}px;right:{l['pk_x']}px;top:{l['pk_y']}px;display:grid;grid-template-columns:1fr 1fr;gap:{l['pk_gap']}px}}
.pack{{display:flex;flex-direction:column;align-items:center}}
.pack img{{width:100%;height:auto}}
.eti{{margin-top:{l['eti_mt']}px;width:100%;padding:{l['eti_py']}px 10px;border-radius:14px;background:#0b0f1a;color:#f4f1ea;text-align:center}}
.eti b{{display:block;font-size:{l['eti_t']}px;font-weight:900;font-stretch:78%;letter-spacing:.02em;text-transform:uppercase;color:#e2cc9a}}
.eti span{{display:block;margin-top:2px;font-size:{l['eti_s']}px;font-weight:600}}
.pega{{position:absolute;left:{l['pg_x']}px;top:{l['pg_y']}px;width:{l['pg']}px;height:{l['pg']}px;border-radius:50%;
  background:radial-gradient(circle at 35% 30%,#f0dba6 0%,#d9bb7c 45%,#b8954f 100%);color:#0b0f1a;
  display:flex;flex-direction:column;align-items:center;justify-content:center;transform:rotate(-9deg);z-index:3;
  box-shadow:0 18px 40px -14px rgba(11,15,26,.55),inset 0 0 0 6px rgba(255,255,255,.35)}}
.pega b{{font-size:{l['pg_precio']}px;font-weight:900;font-stretch:80%;letter-spacing:-.03em;line-height:.9}}
.pega b small{{font-size:.55em;margin-left:2px}}
.pega span{{margin-top:6px;font-size:{l['pg_t']}px;font-weight:800;letter-spacing:.02em;text-transform:uppercase}}
.apple{{position:absolute;left:{l['ap_x']}px;top:{l['ap_y']}px;transform:rotate(-9deg);padding:9px 16px;border-radius:12px;background:#0b0f1a;color:#d9dbe1;font-size:{l['ap']}px;font-weight:600;z-index:3}}
.apple s{{color:#f4f1ea;font-weight:800;text-decoration-thickness:3px;text-decoration-color:#e35d5d}}
.pie{{position:absolute;left:0;right:0;top:{l['pie_y']}px;display:flex;flex-direction:column;align-items:center;text-align:center}}
.envio{{display:flex;align-items:center;gap:18px;font-size:{l['envio']}px;font-weight:900;font-stretch:72%;line-height:1;text-transform:uppercase}}
.envio svg{{width:{l['camion']}px;height:{l['camion']}px;color:#e2cc9a;flex:none}}
.plazo{{margin-top:{l['plazo_mt']}px;font-size:{l['plazo']}px;font-weight:700;color:#e2cc9a}}
.mas{{display:flex;gap:10px 26px;margin-top:{l['mas_mt']}px;font-size:{l['mas']}px;font-weight:600;color:#d9dbe1}}
.mas span{{display:flex;align-items:center;gap:8px}}
.firma{{position:absolute;left:0;right:0;bottom:{l['firma_b']}px;display:flex;flex-direction:column;align-items:center;gap:6px}}
.firma img{{height:{l['logo_h']}px}}
.firma p{{max-width:94%;font-size:{l['letra']}px;line-height:1.3;color:rgba(217,219,225,.55);text-align:center}}
</style></head><body>
<div class="cab">
  <p class="t1">Cargador <i>iPhone</i></p>
  <p class="t2">Original Apple · 20 W + cable</p>
</div>
<div class="cinta">Precio de lanzamiento <i>·</i> Hasta fin de existencias</div>
<div class="blanco"></div>
<p class="elija">Elija su cable<small>El cargador de 20 W es el mismo</small></p>
<div class="pega"><b>18,99<small>€</small></b><span>cada pack</span></div>
<p class="apple">En Apple: <s>38&nbsp;€</s></p>
<div class="packs">
  <div class="pack"><img src="{USBC}" alt=""><p class="eti"><b>USB-C</b><span>iPhone 15 o posterior</span></p></div>
  <div class="pack"><img src="{LTN}" alt=""><p class="eti"><b>Lightning</b><span>iPhone 8 al 14</span></p></div>
</div>
<div class="pie">
  <p class="envio">{CAMION}Envío gratis</p>
  <p class="plazo">En su casa en 24{W2}-{W2}48&nbsp;h</p>
  <p class="mas"><span>{CHECK}Nuevo y precintado</span><span>{CHECK}3 años de garantía</span></p>
</div>
<div class="firma"><img src="{LOGO}" alt=""><p>Precio de lanzamiento hasta agotar las unidades actuales. En Apple (apple.com/es, 29/10/2026): adaptador de 20 W, 19 €; cable de 1 m, 19 €. Pillatumovil no está afiliado a Apple.</p></div>
</body></html>'''

FORMATOS = {
    'feed': (1080, 1350, dict(cab_y=0, cab_h=214, t1=110, t2=32, t2_mt=12,
                               ci_y=214, ci_h=62, ci=28,
                               bl_y=276, bl_h=716, el_x=44, el_y=312, el=56,
                               pk_x=36, pk_y=508, pk_gap=24, eti_mt=10, eti_py=10, eti_t=30, eti_s=22,
                               pg_x=784, pg_y=290, pg=236, pg_precio=82, pg_t=19, ap_x=548, ap_y=402, ap=24,
                               pie_y=1018, envio=104, camion=90, plazo=38, plazo_mt=10, mas=24, mas_mt=14,
                               firma_b=14, logo_h=34, letra=12)),
    # Stories/Reels: todo entre 250 px arriba y 340 px abajo
    'story': (1080, 1920, dict(cab_y=250, cab_h=220, t1=116, t2=34, t2_mt=12,
                                ci_y=470, ci_h=64, ci=29,
                                bl_y=534, bl_h=716, el_x=44, el_y=572, el=58,
                                pk_x=36, pk_y=770, pk_gap=24, eti_mt=10, eti_py=10, eti_t=31, eti_s=23,
                                pg_x=784, pg_y=548, pg=240, pg_precio=84, pg_t=19, ap_x=548, ap_y=664, ap=25,
                                pie_y=1272, envio=96, camion=82, plazo=34, plazo_mt=8, mas=22, mas_mt=10,
                                firma_b=345, logo_h=32, letra=12)),
    'cuadrado': (1080, 1080, dict(cab_y=0, cab_h=170, t1=88, t2=26, t2_mt=8,
                                   ci_y=170, ci_h=50, ci=23,
                                   bl_y=220, bl_h=590, el_x=40, el_y=248, el=44,
                                   pk_x=80, pk_y=384, pk_gap=24, eti_mt=8, eti_py=7, eti_t=24, eti_s=18,
                                   pg_x=820, pg_y=232, pg=196, pg_precio=68, pg_t=16, ap_x=600, ap_y=318, ap=20,
                                   pie_y=830, envio=74, camion=64, plazo=26, plazo_mt=6, mas=18, mas_mt=8,
                                   firma_b=12, logo_h=24, letra=10)),
}

if __name__ == '__main__':
    trabajos = []
    for n in (sys.argv[1:] or list(FORMATOS)):
        w, h, l = FORMATOS[n]
        ruta = os.path.join(AQUI, f'anuncio-e-{n}.html')
        open(ruta, 'w').write(html(w, h, l))
        trabajos.append((ruta, os.path.join(AQUI, f'anuncio-e-{n}.png'), w, h))
    print(subprocess.run(['node', os.path.join(AQUI, 'pintar.js'), json.dumps(trabajos)], capture_output=True, text=True, cwd=AQUI).stdout)
