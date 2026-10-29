# Genera el anuncio de Meta del pack en HTML y lo pinta con Playwright.
# uso: python3 anuncio.py  -> anuncio-feed.png (1080x1350), anuncio-story.png (1080x1920), anuncio-cuadrado.png (1080x1080)
import base64, os, subprocess, json

AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = '/home/user/mi-tienda-shopify/pillatumovil'

def b64(ruta, tipo):
    return f'data:{tipo};base64,' + base64.b64encode(open(ruta, 'rb').read()).decode()

FOTO = b64(os.path.join(AQUI, 'cajas-1536.jpg'), 'image/jpeg')
LOGO = b64(os.path.join(REPO, 'marca/logo-pillatumovil-firma.png'), 'image/png')

CAMION = '<svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M2.5 6.5h11v10h-11z"/><path d="M13.5 9.5h4l3 3.2v3.8h-7"/><circle cx="6.5" cy="17.5" r="1.8"/><circle cx="17" cy="17.5" r="1.8"/></svg>'
W2 = '⁠'  # para que "24-48" no se parta
CHECK = '<svg width="1em" height="1em" viewBox="0 0 20 20" fill="none" stroke="#c9a86a" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="m4.5 10.4 3.4 3.4 7.6-8"/></svg>'

def html(w, h, lay):
    return f'''<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:{w}px;height:{h}px;overflow:hidden}}
body{{position:relative;background:#080e18;color:#f4f1ea;font-family:Archivo,sans-serif;-webkit-font-smoothing:antialiased}}
.foto{{position:absolute;left:{lay['foto_x']}px;top:{lay['foto_y']}px;width:{lay['foto_w']}px;height:{lay['foto_w']}px;
  background:url({FOTO}) center/cover;
  -webkit-mask-image:linear-gradient(180deg,transparent 0%,#000 {lay['fade_top']}%,#000 {lay['fade_bot']}%,transparent 100%),linear-gradient(90deg,transparent 0%,#000 9%,#000 91%,transparent 100%);
  -webkit-mask-composite:source-in;mask-composite:intersect;}}
.velo{{position:absolute;inset:0;background:radial-gradient(120% 60% at 50% {lay['luz_y']}%,rgba(201,168,106,.10),transparent 60%)}}
.cinta{{position:absolute;left:0;right:0;top:{lay['cinta_y']}px;height:{lay['cinta_h']}px;display:flex;align-items:center;justify-content:center;gap:12px;background:linear-gradient(90deg,#d9c08a 0%,#e9d7ad 50%,#d9c08a 100%);color:#0b0f1a;font-size:{lay['cinta']}px;font-weight:800;letter-spacing:.07em;text-transform:uppercase;white-space:nowrap}}
.cinta i{{font-style:normal;font-weight:600;letter-spacing:0;text-transform:none}}
.logo{{position:absolute;left:50%;top:{lay['logo_y']}px;transform:translateX(-50%);height:{lay['logo_h']}px}}
.cab{{position:absolute;left:{lay['pad']}px;right:{lay['pad']}px;top:{lay['cab_y']}px;text-align:center}}
.gancho{{font-size:{lay['gancho']}px;font-weight:700;line-height:1;letter-spacing:-.04em;color:#f4f1ea}}
.gancho em{{font-style:normal;color:#e2cc9a}}
.prod{{margin-top:{lay['prod_mt']}px;font-size:{lay['prod']}px;font-weight:500;line-height:1.3;letter-spacing:-.01em;color:#b9bcc6}}
.prod b{{color:#f4f1ea;font-weight:600}}
.pie{{position:absolute;left:{lay['pad']}px;right:{lay['pad']}px;top:{lay['pie_y']}px}}
.fila{{display:flex;align-items:center;justify-content:center;gap:26px}}
.precio{{font-size:{lay['precio']}px;font-weight:800;letter-spacing:-.045em;line-height:.9;color:#f4f1ea;font-variant-numeric:tabular-nums}}
.precio small{{font-size:.55em;font-weight:700;letter-spacing:-.02em;margin-left:6px}}
.cod{{display:flex;flex-direction:column;gap:6px}}
.cod span{{font-size:{lay['cod_t']}px;font-weight:500;color:#b9bcc6}}
.cod b{{display:inline-block;padding:10px 20px;border-radius:12px;border:0;padding:0;background:none;color:#e2cc9a;font-size:{lay['cod']}px;font-weight:700;letter-spacing:-.01em}}
.apple{{margin-top:{lay['apple_mt']}px;text-align:center;font-size:{lay['apple']}px;color:#b9bcc6}}
.apple b{{color:#f4f1ea;font-weight:600}}
.sello{{display:flex;align-items:center;justify-content:center;gap:14px;margin:{lay['sello_mt']}px auto 0;width:max-content;padding:16px 30px;border-radius:999px;background:#c9a86a;color:#0b0f1a;font-size:{lay['sello']}px;font-weight:700;letter-spacing:-.005em}}
.checks{{display:flex;flex-wrap:wrap;justify-content:center;gap:8px 26px;list-style:none;margin-top:{lay['sello_mt']}px;font-size:{lay['sello']}px;font-weight:600;color:#f4f1ea}}
.checks li{{display:flex;align-items:center;gap:8px;white-space:nowrap}}
.letra{{position:absolute;left:{lay['pad']}px;right:{lay['pad']}px;bottom:{lay['letra_b']}px;text-align:center;font-size:{lay['letra']}px;line-height:1.4;color:rgba(185,188,198,.62)}}
</style></head><body>
<div class="foto"></div><div class="velo"></div>
<div class="cinta">Ganamos menos por cada pack. <i>A propósito.</i></div>
<img class="logo" src="{LOGO}" alt="">
<div class="cab">
  <p class="gancho">Menos de la mitad<br><em>que en Apple.</em></p>
  <p class="prod"><b>Cargador de 20 W + cable USB-C o Lightning</b><br>Originales de Apple, nuevos y precintados</p>
</div>
<div class="pie">
  <div class="fila">
    <p class="precio">18,99<small>€</small></p>
    <p class="cod"><span>el pack completo:</span><b>cargador + cable</b></p>
  </div>
  <p class="apple">En Apple, por separado: <b>38 €</b></p>
  <ul class="checks"><li>{CHECK}Envío gratis 24{W2}-{W2}48&nbsp;h</li><li>{CHECK}3 años de garantía</li><li>{CHECK}14 días para devolverlo</li></ul>
</div>
<p class="letra">Pack de 1: adaptador de 20 W + cable de 1 m (USB-C o Lightning). En Apple (apple.com/es, 29/10/2026): adaptador de 20 W, 19 €; cable de 1 m, 19 €. Producto nuevo y precintado. Pillatumovil no está afiliado a Apple.</p>
</body></html>'''

FORMATOS = {
    # Feed de Facebook e Instagram (4:5)
    'feed': (1080, 1350, dict(pad=60, cinta_y=0, cinta_h=72, cinta=28, logo_y=98, logo_h=38, cab_y=160, gancho=84, prod_mt=16, prod=29,
                               foto_x=120, foto_y=272, foto_w=840, fade_top=17, fade_bot=86, luz_y=50,
                               pie_y=1035, precio=128, cod_t=24, cod=32, apple_mt=14, apple=26, sello_mt=18, sello=26,
                               letra_b=16, letra=16)),
    # Stories y Reels (9:16). Arriba ~250 px y abajo ~330 px los tapa la interfaz:
    # todo va entre medias, la cinta incluida.
    'story': (1080, 1920, dict(pad=60, cinta_y=262, cinta_h=74, cinta=29, logo_y=362, logo_h=38, cab_y=424, gancho=84, prod_mt=16, prod=29,
                                foto_x=130, foto_y=526, foto_w=820, fade_top=17, fade_bot=86, luz_y=48,
                                pie_y=1270, precio=128, cod_t=24, cod=32, apple_mt=14, apple=26, sello_mt=18, sello=26,
                                letra_b=338, letra=16)),
    # Cuadrado (1:1)
    'cuadrado': (1080, 1080, dict(pad=50, cinta_y=0, cinta_h=54, cinta=22, logo_y=70, logo_h=30, cab_y=110, gancho=64, prod_mt=10, prod=22,
                                   foto_x=235, foto_y=198, foto_w=610, fade_top=17, fade_bot=86, luz_y=46,
                                   pie_y=758, precio=104, cod_t=20, cod=28, apple_mt=8, apple=22, sello_mt=12, sello=22,
                                   letra_b=12, letra=13)),
}

if __name__ == '__main__':
    import sys
    pedidos = sys.argv[1:] or list(FORMATOS)
    trabajos = []
    for n in pedidos:
        w, h, lay = FORMATOS[n]
        ruta = os.path.join(AQUI, f'anuncio-{n}.html')
        open(ruta, 'w').write(html(w, h, lay))
        trabajos.append((ruta, os.path.join(AQUI, f'anuncio-{n}.png'), w, h))
    js = os.path.join(AQUI, 'pintar.js')
    open(js, 'w').write('''const { chromium } = require('playwright');
const t = JSON.parse(process.argv[2]);
(async () => {
  const b = await chromium.launch();
  for (const [html, png, w, h] of t) {
    const p = await b.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
    await p.goto('file://' + html, { waitUntil: 'networkidle' });
    await p.evaluate(() => document.fonts.ready);
    await p.waitForTimeout(300);
    const des = await p.evaluate(() => { const r = []; for (const el of document.querySelectorAll('.cab,.pie,.letra,.logo')) { const b = el.getBoundingClientRect(); r.push([el.className, Math.round(b.top), Math.round(b.bottom)]); } return r; });
    console.log(png.split('/').pop(), JSON.stringify(des), 'fuente', await p.evaluate(() => document.fonts.check('700 40px Archivo')));
    await p.screenshot({ path: png });
    await p.close();
  }
  await b.close();
})();
''')
    print(subprocess.run(['node', js, json.dumps(trabajos)], capture_output=True, text=True, cwd=AQUI).stdout)
