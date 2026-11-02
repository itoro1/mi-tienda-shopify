"""Anuncios de Meta de Pillatumovil (02/11/2026).
Uso: python3 anuncio_meta.py FOTO_ESTUDIO.jpg FUENTES_DIR SALIDA_DIR
Dos ideas (A: el cargador que ya no viene; B: la cuenta) en 4:5 y 9:16.
Cifras: precio de la tienda y PVP de apple.com/es del 01/11/2026."""
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

foto, fdir, out = sys.argv[1:4]
NOCHE=(11,15,26); ORO=(201,168,106); ORO_T=(217,187,124); MARFIL=(244,241,234); MARFIL2=(185,188,198)

def fuente(nombre, tam, peso, ancho=None):
    f = ImageFont.truetype(os.path.join(fdir, nombre), tam)
    ejes = {'Weight': peso}
    if ancho: ejes['Width'] = ancho
    try:
        f.set_variation_by_axes([peso] if nombre.startswith('Unb') else [peso, ancho or 100])
    except Exception:
        pass
    return f
UNB=lambda t: fuente('Unbounded.ttf', t, 600)
ARC=lambda t, p=500: fuente('Archivo.ttf', t, p)

def base(W, H, foto_h_frac, foto_y):
    src = Image.open(foto).convert('RGB')
    # recorte alrededor de las cajas (derecha de la foto de estudio)
    cx = int(src.width*0.68); ch = src.height
    rw = int(ch*W/(H*foto_h_frac))
    x0 = max(0, min(src.width-rw, cx-rw//2))
    rec = src.crop((x0, 0, x0+rw, ch)).resize((W, int(H*foto_h_frac)), Image.LANCZOS)
    lienzo = Image.new('RGB', (W, H), NOCHE)
    lienzo.paste(rec, (0, foto_y))
    # fundido de la foto con el fondo noche arriba y abajo
    m = Image.new('L', (W, rec.height), 255); d = ImageDraw.Draw(m)
    fade = int(rec.height*0.22)
    for i in range(fade):
        a = int(255*(i/fade)**1.6)
        d.line([(0, i), (W, i)], fill=a); d.line([(0, rec.height-1-i), (W, rec.height-1-i)], fill=a)
    fondo = Image.new('RGB', rec.size, NOCHE)
    lienzo.paste(Image.composite(rec, fondo, m), (0, foto_y))
    return lienzo

def texto_lineas(d, x, y, lineas, f, color, interl):
    for l in lineas:
        d.text((x, y), l, font=f, fill=color); y += interl
    return y

def sello(d, x, y, txt, f):
    w = d.textlength(txt, font=f); h = f.size
    d.rounded_rectangle([x, y, x+w+48, y+h+30], radius=(h+30)//2, outline=ORO, width=3)
    d.text((x+24, y+13), txt, font=f, fill=ORO_T)
    return y+h+30

def logo(d, W, y, f):
    t1, t2, t3 = 'pilla', 'tu', 'movil'
    w = sum(d.textlength(t, font=f) for t in (t1, t2, t3)); x = (W-w)/2
    for t, c in ((t1, MARFIL), (t2, ORO_T), (t3, MARFIL)):
        d.text((x, y), t, font=f, fill=c); x += d.textlength(t, font=f)

def idea(nombre, W, H, safe_top, safe_bot):
    story = H > W*1.5
    M = 72
    if nombre == 'A':
        titulo = ['El cargador que', 'su iPhone ya', 'no trae.']
    else:
        titulo = ['Lo mismo', 'que en Apple.', 'La mitad.']
    ft = UNB(92 if not story else 100)
    alto_tit = len(titulo)*int(ft.size*1.08)
    foto_y = safe_top + alto_tit + (10 if not story else 60)
    foto_frac = 0.50 if not story else 0.46
    im = base(W, H, foto_frac, foto_y - int(H*foto_frac*0.18))
    d = ImageDraw.Draw(im)
    texto_lineas(d, M, safe_top, titulo, ft, MARFIL, int(ft.size*1.08))
    # bloque de precio, abajo
    fp = UNB(150 if not story else 170); fs = ARC(40, 500); fsm = ARC(31, 450); fb = ARC(34, 600)
    y = H - safe_bot - (fp.size + 36 + 40 + 30 + 76)
    d.text((M, y), 'Cargador 20 W + cable USB‑C, de Apple', font=fs, fill=MARFIL)
    y += 56
    d.text((M-6, y), '18,99 €', font=fp, fill=ORO_T)
    y += fp.size + 22
    d.text((M, y), 'En Apple, 38,00 € (precio del 01/11/2026)', font=fsm, fill=MARFIL2)
    y += 58
    sello(d, M, y, 'Envío gratis en 24-48 h', fb)
    if not story:
        logo(d, W, H-safe_bot+26, ARC(30, 700)) if safe_bot > 60 else None
    return im

os.makedirs(out, exist_ok=True)
for n in ('A', 'B'):
    idea(n, 1080, 1350, 84, 70).save(f'{out}/pillatumovil_pack-usbc_{n}_feed-4x5.jpg', quality=92)
    idea(n, 1080, 1920, 250, 330).save(f'{out}/pillatumovil_pack-usbc_{n}_stories-9x16.jpg', quality=92)
print('hecho')
