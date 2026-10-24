# Logotipo de Pillatumovil: bateria cargando + nombre en Archivo 800.
import sys
from PIL import Image, ImageDraw, ImageFont
INK=(27,34,48); VERDE=(52,199,89)
def fuente(tam, peso=800, ancho=100):
    f=ImageFont.truetype('fuentes/Archivovar.ttf', tam)
    f.set_variation_by_axes([peso, ancho])   # ejes: wght, wdth
    return f
def logo(texto, alto=240, tinta=INK, salida="logo.png", ancho_fuente=94, solo_icono=False):
    S=4  # sobremuestreo para bordes suaves
    H=alto*S; f=fuente(int(H*.62), 800, ancho_fuente)
    # bateria: cuerpo, polo y carga al 60 %
    bw, bh = int(H*.78), int(H*.44); grosor=max(2,int(H*.068)); r=int(bh*.28)
    tw = 0 if solo_icono else int(ImageDraw.Draw(Image.new('L',(1,1))).textlength(texto, font=f))
    gap = int(H*.16)
    W = bw + int(H*.08) + (0 if solo_icono else gap + tw) + 4
    im=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    by=(H-bh)//2 + int(H*.03)
    d.rounded_rectangle([0,by,bw,by+bh],radius=r,outline=tinta,width=grosor)
    pad=grosor+int(H*.035)
    d.rounded_rectangle([pad,by+pad,pad+int((bw-2*pad)*.6),by+bh-pad],radius=max(1,r-pad),fill=VERDE)
    d.rounded_rectangle([bw+int(H*.015),by+int(bh*.3),bw+int(H*.08),by+int(bh*.7)],radius=int(H*.02),fill=tinta)
    if not solo_icono:
        asc,desc=f.getmetrics()
        d.text((bw+int(H*.08)+gap, H/2 + int(H*.03)), texto, font=f, fill=tinta, anchor='lm')
    im=im.resize((W//S,H//S),Image.LANCZOS); im.save(salida); return im
if __name__=='__main__':
    logo('Pillatumovil', salida='logo-pillatumovil.png')
    logo('Pillatumovil', salida='logo-pillatumovil-blanco.png', tinta=(255,255,255))
    logo('', salida='icono-pillatumovil.png', solo_icono=True, alto=512)
    # muestra sobre claro y oscuro
    a=Image.open('logo-pillatumovil.png'); b=Image.open('logo-pillatumovil-blanco.png')
    m=Image.new('RGB',(a.width+80,a.height*2+120),(255,255,255)); m.paste(a,(40,40),a)
    dk=Image.new('RGB',(a.width+80,a.height+80),(27,34,48)); dk.paste(b,(40,40),b); m.paste(dk,(0,a.height+80))
    m.save('muestra.png'); print(a.size)
