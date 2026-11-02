"""Anuncio de Meta de la tienda (02/11/2026): «¿Qué cargador necesita su iPhone?»
Uso: python3 anuncio_tienda.py FOTO_MESILLA.jpg FUENTES_DIR SALIDA_DIR
Precios de la tienda: pack 18,99 € (USB-C y Lightning)."""
import sys, os
from PIL import Image, ImageDraw, ImageFont

foto, fdir, out = sys.argv[1:4]
NOCHE=(11,15,26); ORO=(201,168,106); ORO_T=(217,187,124); MARFIL=(244,241,234); MARFIL2=(185,188,198); TINTA=(20,24,36); TINTA2=(71,76,89); ORO_OSC=(125,95,40)

def F(nombre, tam, peso):
    f = ImageFont.truetype(os.path.join(fdir, nombre), tam)
    f.set_variation_by_axes([peso] if nombre.startswith('Unb') else [peso, 100])
    return f

def foto_fundida(W, h):
    src = Image.open(foto).convert('RGB')
    # recorte centrado en la mesilla (mitad inferior de la foto)
    r = W / h; ch = int(src.width / r)
    y0 = max(0, min(src.height - ch, int(src.height * 0.40) - ch // 2))
    im = src.crop((0, y0, src.width, y0 + ch)).resize((W, h), Image.LANCZOS)
    m = Image.new('L', (W, h), 255); d = ImageDraw.Draw(m); fade = int(h * 0.35)
    for i in range(fade):
        d.line([(0, h - 1 - i), (W, h - 1 - i)], fill=int(255 * (i / fade) ** 1.4))
    return Image.composite(im, Image.new('RGB', (W, h), NOCHE), m)

def tesela(d, x, y, w, h, modelos, cable):
    d.rounded_rectangle([x, y, x + w, y + h], radius=28, fill=MARFIL)
    p = 34
    d.text((x + p, y + p), modelos, font=F('Unbounded.ttf', 44, 600), fill=TINTA)
    d.text((x + p, y + p + 66), cable, font=F('Archivo.ttf', 34, 500), fill=TINTA2)
    d.text((x + p, y + h - p - 74), 'Pack', font=F('Archivo.ttf', 28, 600), fill=ORO_OSC)
    d.text((x + p, y + h - p - 42), '18,99 €', font=F('Unbounded.ttf', 40, 600), fill=TINTA)

def anuncio(W, H, top, bot):
    story = H > W * 1.5
    lienzo = Image.new('RGB', (W, H), NOCHE)
    fh = int(H * (0.56 if not story else 0.46))
    lienzo.paste(foto_fundida(W, fh), (0, 0 if not story else top - 60))
    d = ImageDraw.Draw(lienzo); M = 64
    ft = F('Unbounded.ttf', 74 if not story else 72, 600)
    y = (fh - 130) if not story else (top - 60 + fh - 110)
    for l in ('¿Qué cargador', 'necesita su iPhone?'):
        d.text((M, y), l, font=ft, fill=MARFIL); y += int(ft.size * 1.1)
    y += 30
    tw = (W - 2 * M - 24) // 2; th = 280
    tesela(d, M, y, tw, th, 'iPhone 8 al 14', 'Cable Lightning')
    tesela(d, M + tw + 24, y, tw, th, 'iPhone 15 al 18', 'Cable USB‑C')
    y += th + 34
    d.text((M, y), 'Adaptador de 20 W + cable, originales de Apple.', font=F('Archivo.ttf', 34, 500), fill=MARFIL)
    y += 54
    d.text((M, y), 'Envío gratis en 24-48 h · 14 días para devolverlo', font=F('Archivo.ttf', 30, 500), fill=ORO_T)
    if not story:
        f = F('Archivo.ttf', 28, 700); t = 'pillatumovil.com'
        d.text((W - M - d.textlength(t, font=f), H - bot - 4), t, font=f, fill=MARFIL2)
    return lienzo

os.makedirs(out, exist_ok=True)
anuncio(1080, 1350, 0, 56).save(f'{out}/pillatumovil_tienda_que-cargador_feed-4x5.jpg', quality=92)
anuncio(1080, 1920, 250, 330).save(f'{out}/pillatumovil_tienda_que-cargador_stories-9x16.jpg', quality=92)
print('hecho')
