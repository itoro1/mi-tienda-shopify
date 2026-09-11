import base64, pathlib, sys

def b64(p, mime):
    return f"data:{mime};base64," + base64.b64encode(pathlib.Path(p).read_bytes()).decode()

FONTS = "".join(
    f"@font-face{{font-family:Inter;font-weight:{w};font-style:normal;src:url({b64(f'fonts/Inter-{w}.ttf','font/ttf')}) format('truetype');}}"
    for w in (400, 500, 700, 800, 900)
)
ADAPT = b64("acc/adaptador.png", "image/png")
CABLE = b64("acc/cable.png", "image/png")

def html(w, h, vertical):
    # proporciones que cambian entre cuadrado y vertical
    hero   = 430 if not vertical else 560
    padtop = 54  if not vertical else 76
    return f"""<!doctype html><html lang=es><meta charset=utf-8><style>
{FONTS}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{w}px;height:{h}px}}
body{{font-family:Inter,system-ui,sans-serif;background:#fff;color:#0d0d0d;
  display:flex;flex-direction:column;overflow:hidden;-webkit-font-smoothing:antialiased}}
.wrap{{flex:1;display:flex;flex-direction:column;padding:{padtop}px 64px 0}}
.top{{display:flex;align-items:flex-start;justify-content:space-between}}
.brand{{font-weight:800;font-size:27px;letter-spacing:.14em}}
.brand i{{font-style:normal;color:#c9a227}}
.badge{{background:#0d0d0d;color:#fff;font-weight:900;font-size:38px;letter-spacing:-.02em;
  padding:14px 24px;border-radius:100px;line-height:1}}
.hero{{height:{hero}px;display:flex;align-items:center;justify-content:center;gap:58px;margin-top:14px}}
.hero img{{display:block;height:100%;width:auto;object-fit:contain}}
.hero .ad{{height:{int(hero*0.80)}px}}
.hero .cb{{height:{hero}px}}
h1{{font-size:{62 if not vertical else 70}px;font-weight:800;letter-spacing:-.035em;line-height:1.04;margin-top:{14 if not vertical else 30}px}}
.sub{{font-size:{28 if not vertical else 31}px;font-weight:500;color:#6b6b6b;margin-top:12px;letter-spacing:-.01em}}
.prices{{display:flex;align-items:baseline;gap:20px;margin-top:{20 if not vertical else 34}px}}
.now{{font-size:{116 if not vertical else 132}px;font-weight:900;letter-spacing:-.055em;line-height:.9}}
.was{{font-size:{40 if not vertical else 45}px;font-weight:500;color:#9a9a9a;text-decoration:line-through}}
.save{{font-size:{23 if not vertical else 26}px;font-weight:700;color:#c9a227}}
.note{{font-size:{18 if not vertical else 20}px;color:#9a9a9a;font-weight:400;margin-top:8px}}
.trust{{display:flex;gap:34px;margin-top:{22 if not vertical else 38}px;flex-wrap:wrap}}
.trust span{{font-size:{24 if not vertical else 27}px;font-weight:700;display:flex;align-items:center;gap:9px}}
.trust svg{{flex:none}}
.cta{{background:#0d0d0d;color:#fff;padding:{30 if not vertical else 36}px 64px;display:flex;
  align-items:center;justify-content:space-between;margin-top:auto}}
.cta b{{font-size:{34 if not vertical else 38}px;font-weight:800;letter-spacing:-.02em}}
.cta em{{font-style:normal;font-size:{22 if not vertical else 25}px;font-weight:500;color:#b9b9b9}}
</style>
<div class=wrap>
  <div class=top>
    <div class=brand>ITORO<i>STORE</i></div>
    <div class=badge>&minus;20%</div>
  </div>
  <div class=hero>
    <img class=ad src="{ADAPT}" alt="">
    <img class=cb src="{CABLE}" alt="">
  </div>
  <h1>Pack cargador<br>completo Apple</h1>
  <div class=sub>Adaptador 20 W + cable USB&#8209;C de 1 m</div>
  <div class=prices>
    <span class=now>17&euro;</span>
    <span class=was>21,25&euro;</span>
    <span class=save>AHORRAS 4,25&euro;</span>
  </div>
  <div class=note>Precio de los dos art&iacute;culos comprados por separado en itorostore.com</div>
  <div class=trust>
    <span><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#c9a227" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>100% original Apple</span>
    <span><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#c9a227" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>Env&iacute;o gratis 24&ndash;48 h</span>
  </div>
</div>
<div class=cta><b>C&oacute;mpralo en itorostore.com</b><em>Env&iacute;o desde Espa&ntilde;a</em></div>
</html>"""

for name, w, h, vert in [("ad-1080x1080", 1080, 1080, False), ("ad-1080x1350", 1080, 1350, True)]:
    pathlib.Path(f"{name}.html").write_text(html(w, h, vert), encoding="utf-8")
    print("escrito", name)
