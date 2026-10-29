# Foto de perfil de Pillatumovil (WhatsApp, Instagram, Facebook y logo
# cuadrado de Shopify): el monograma "P" del favicon (Bodoni Moda, marfil,
# con el punto de oro), recolocado para que quepa entero en un circulo.
# Uso: python3 perfil.py RUTA/BodoniModa.ttf CARPETA_SALIDA
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

IV = (244, 239, 230); NOCHE = (11, 15, 26); ORO = (201, 168, 106)

def fuente(ruta, t):
    f = ImageFont.truetype(ruta, t); f.set_variation_by_axes([560, 22]); return f

def perfil(ruta_fuente, salida, lado=1080, alto_p=.42, anillo=False):
    S = 3; L = lado * S
    # Fondo: noche con una luz suave en el centro (como el estudio de las fotos)
    im = Image.new('RGB', (L, L), NOCHE)
    luz = Image.new('L', (L, L), 0)
    ImageDraw.Draw(luz).ellipse([L * .12, L * .08, L * .88, L * .84], fill=255)
    luz = luz.filter(ImageFilter.GaussianBlur(L * .16))
    im = Image.composite(Image.new('RGB', (L, L), (26, 34, 54)), im, luz)
    d = ImageDraw.Draw(im)
    # La P: misma proporcion punto/letra que el favicon (punto r = 5,5 % del
    # cuerpo 0,86; centro en 0,74/0,27 con la P centrada en 0,5/0,53).
    cuerpo = L * alto_p / .62           # la P mide ~62 % del cuerpo de la fuente
    f = fuente(ruta_fuente, int(cuerpo))
    caja = d.textbbox((0, 0), 'P', font=f, anchor='mm')
    escala = cuerpo / (L * .86)          # respecto al favicon
    r = L * .055 * escala
    dx, dy = (0.74 - 0.5) * L * escala, (0.27 - 0.53) * L * escala
    # centrar el conjunto P + punto
    x0 = min(caja[0], dx - r); x1 = max(caja[2], dx + r)
    y0 = min(caja[1], dy - r); y1 = max(caja[3], dy + r)
    cx = L / 2 - (x0 + x1) / 2; cy = L / 2 - (y0 + y1) / 2
    d.text((cx, cy), 'P', font=f, fill=IV, anchor='mm')
    d.ellipse([cx + dx - r, cy + dy - r, cx + dx + r, cy + dy + r], fill=ORO)
    if anillo:
        a = L * .455; g = L * .006
        d.ellipse([L / 2 - a, L / 2 - a, L / 2 + a, L / 2 + a], outline=ORO, width=int(g))
    im = im.resize((lado, lado), Image.LANCZOS)
    im.save(salida, quality=95)
    return im

if __name__ == '__main__':
    fuente_ttf, carpeta = sys.argv[1], sys.argv[2]
    os.makedirs(carpeta, exist_ok=True)
    a = perfil(fuente_ttf, os.path.join(carpeta, 'perfil-pillatumovil.png'))
    b = perfil(fuente_ttf, os.path.join(carpeta, 'perfil-pillatumovil-anillo.png'), anillo=True)
    # Muestra: como se ve en circulo, grande y pequeno (lista de chats)
    m = Image.new('RGB', (1500, 640), (240, 242, 245))
    for i, im in enumerate([a, b]):
        circ = Image.new('L', im.size, 0); ImageDraw.Draw(circ).ellipse([0, 0, im.width, im.height], fill=255)
        for j, t in enumerate([420, 96, 48]):
            c = im.resize((t, t), Image.LANCZOS); mk = circ.resize((t, t), Image.LANCZOS)
            x = 60 + i * 740 + [0, 470, 600][j]; y = 110 if j == 0 else 270
            m.paste(c, (x, y), mk)
    m.save(os.path.join(carpeta, 'muestra-perfil.png'))
