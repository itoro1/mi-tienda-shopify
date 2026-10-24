# Compone las cajas recortadas sobre fondo blanco 2048x2048 (ficha de Shopify).
import sys, json
from PIL import Image, ImageFilter, ImageDraw
sys.path.insert(0, sys.argv[0].rsplit('/',1)[0])
from cajas import mascara
src, cajas_json, salida = sys.argv[1:4]
L = 2048
im = Image.open(src).convert('RGB'); cajas = json.load(open(cajas_json))
m = mascara(im.size, cajas).filter(ImageFilter.GaussianBlur(.8))
x0 = min(c[0] for c in cajas); x1 = max(c[2] for c in cajas)
y0 = min(c[1]-int(.2*(c[2]-c[0])) for c in cajas); y1 = max(c[3] for c in cajas)
recorte = im.crop((x0,y0,x1,y1)); mrec = m.crop((x0,y0,x1,y1))
# Mismo encuadre en todas: el grupo ocupa como mucho 76 % de ancho y 70 % de alto.
k = min(L*.76/recorte.width, L*.70/recorte.height)
W, H = int(recorte.width*k), int(recorte.height*k)
recorte = recorte.resize((W,H), Image.LANCZOS); mrec = mrec.resize((W,H), Image.LANCZOS)
px, py = (L-W)//2, int(L*.53 - H/2)
lienzo = Image.new('RGB', (L,L), (255,255,255))
# Sombra: una difusa grande y otra de contacto pegada a la base.
sombra = Image.new('L', (L,L), 0)
sombra.paste(mrec.point(lambda v: int(v*.20)), (px+14, py+30))
sombra = sombra.filter(ImageFilter.GaussianBlur(42))
contacto = Image.new('L', (L,L), 0); d = ImageDraw.Draw(contacto)
d.ellipse([px+W*.04, py+H-14, px+W*.96, py+H+26], fill=70)
contacto = contacto.filter(ImageFilter.GaussianBlur(14))
for s in (sombra, contacto):
    lienzo = Image.composite(Image.new('RGB',(L,L),(30,34,42)), lienzo, s)
lienzo.paste(recorte, (px,py), mrec)
lienzo.save(salida, 'JPEG', quality=90, optimize=True, progressive=True)
print(salida, (W,H))
