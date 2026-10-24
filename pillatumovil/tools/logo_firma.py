# Logotipo de Pillatumovil: el nombre en Bodoni Moda con los puntos de las
# dos "i" en oro champan. Los puntos se obtienen restando el texto sin
# puntos (con "ı", i sin punto) del texto normal.
from PIL import Image, ImageDraw, ImageFont, ImageChops
IV=(244,239,230); NOCHE=(11,15,26); ORO=(201,168,106)
def fuente(t): 
    f=ImageFont.truetype('fuentes/BodoniModa.ttf',t); f.set_variation_by_axes([560, 22]); return f
def firma(salida, alto=200, tinta=IV, oro=ORO, texto='Pillatumovil'):
    S=4; H=alto*S; f=fuente(int(H*.78))
    W=int(ImageDraw.Draw(Image.new('L',(1,1))).textlength(texto,font=f))+int(H*.1)
    def mascara(t):
        m=Image.new('L',(W,H),0); ImageDraw.Draw(m).text((int(H*.04),H*.56),t,font=f,fill=255,anchor='lm'); return m
    con=mascara(texto); sin=mascara(texto.replace('i','ı'))
    puntos=ImageChops.subtract(con,sin)
    im=Image.new('RGBA',(W,H),(0,0,0,0))
    im.paste(Image.new('RGBA',(W,H),tinta+(255,)),(0,0),sin)
    im.paste(Image.new('RGBA',(W,H),oro+(255,)),(0,0),puntos)
    bb=im.getbbox(); im=im.crop((bb[0]-8,bb[1]-8,bb[2]+8,bb[3]+8))
    im=im.resize((im.width//S,im.height//S),Image.LANCZOS); im.save(salida); return im
def monograma(salida, lado=512):
    S=2; L=lado*S; im=Image.new('RGBA',(L,L),NOCHE+(255,)); f=fuente(int(L*.86))
    d=ImageDraw.Draw(im); d.text((L*.5,L*.53),'P',font=f,fill=IV,anchor='mm')
    r=L*.055; cx,cy=L*.74,L*.27; d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=ORO)
    im.resize((lado,lado),Image.LANCZOS).save(salida)
if __name__=='__main__':
    a=firma('logo-pillatumovil-firma.png'); firma('logo-pillatumovil-firma-noche.png',tinta=NOCHE)
    monograma('favicon-pillatumovil-p.png')
    p=a.resize((int(a.width*36/a.height),36),Image.LANCZOS)
    fav=Image.open('favicon-pillatumovil-p.png').resize((96,96))
    m=Image.new('RGB',(a.width+80,a.height+200),NOCHE); m.paste(a,(40,30),a); m.paste(p,(40,a.height+70),p); m.paste(fav,(a.width-80,a.height+60)); m.save('muestra-firma.png'); print(a.size)
