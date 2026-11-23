"""Vídeo con dependienta 9:16 (10/11/2026): clip Seedance hablado + subtítulos + precio + cierre.

Uso: python3 video_persona.py CLIP.mp4 FUENTES_DIR SALIDA.mp4 [v1|v2|v3] [RETRASO_VOZ_S] [ESCALA]
ESCALA 2 = 4K nativo (2160x3840): los textos se dibujan al doble, no se amplían.

- Subtítulos con el texto exacto del guion, sincronizados con la voz,
  abajo, sin tapar la cara ni las cajas. En Reels y TikTok casi todos ven sin sonido.
- Mientras dice el precio salen «18,99 €» y «En Apple, 38,00 € (precio del 01/11/2026)».
- Al final, tarjeta fija de 2,5 s: plazo real, envío y botón pillatumovil.com.

v6 (23/11/2026, tras la revisión independiente D7, D13, D16, D22, D25-D28, D30-D35, D39, D42, D46):
  python3 video_persona.py CLIP FUENTES SALIDA.mp4 v6 [RETRASO] [ESCALA] [opciones]
  --precio 18,99          precio del pack (tarjeta, chip, subtítulo y cierre)
  --plazo '30 de noviembre'   texto del rótulo rojo «Precio de lanzamiento hasta el …» ('' = sin rótulo)
  --acaba 30/11           fecha del subtítulo «este precio acaba el …» ('' = quita «Dese prisa» y esa frase)
  --montaje v4|v5|PLAN.json   cortes del clip y dónde va cada texto en cada plano (por defecto v4)
  --subs SUBS.json        [[texto, inicio_s], ...] si el audio cambia (sustituye a los subtítulos v6)
  --audio FICHERO         audio que se pone (por defecto el del CLIP); se alarga con silencio bajo el cierre
  --foto PNG              foto real del producto para el cierre (con transparencia; si no la tiene, se recorta)
  --cierre 2.75           segundos de tarjeta final (incluye el fundido de 6 fotogramas)
  --empuje 0.035          acercamiento lento de la tarjeta final (0 = fija); limitado a la zona segura de los textos
  --fotos t1,t2,...       solo fotogramas sueltos (JPG en la carpeta SALIDA), para revisar sin renderizar
  --crf 16 --preset medium --hilos 2   ajustes de x264 de la salida (por defecto los de siempre: crf 16 en 4K, 18 en 1080)
  Todo el texto queda entre y 300 y 1240 y entre x 90 y 990 (coordenadas 1080x1920): Reels tapa arriba ~250 px,
  abajo ~670 px y la columna de iconos de la derecha; el feed 4:5 solo deja y 285-1635.
  Salida en BT.709 etiquetado (el vídeo de entrada se lee como BT.709, así la imagen no cambia de color).
"""
import subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# 1) subtítulos: texto exacto del guion; tiempos sacados de la voz con
#    faster-whisper (word_timestamps) y fijados aquí para el clip Seedance 11423373.
SUBS_V1 = [
    ('¿Su iPhone vino', 0.00), ('sin cargador?', 0.68), ('Normal,', 1.42), ('Apple ya no lo pone.', 1.98),
    ('Aquí tiene los dos:', 2.92), ('adaptador de 20 W', 3.76), ('y cable.', 4.68), ('Originales de Apple,', 5.24),
    ('precintados.', 5.94), ('En Apple le cuestan', 6.84), ('38 euros.', 7.56), ('Aquí, 18,99.', 8.40),
    ('Compramos por cantidad', 9.70), ('y ganamos menos.', 10.38), ('Envío gratis', 11.40),
    ('en 24-48 h', 12.02), ('en su casa.', 12.98), ('Hasta el jueves.', 13.66), ('Toque «Comprar».', 14.44),
]
# v2 (11/11): voz ElevenLabs «Elena» + vídeo Intone 5630c05b con 5 planos; tiempos medidos
#    con faster-whisper sobre el clip final (clip-intone-broll.mp4).
SUBS_V2 = [
    ('¿Su iPhone vino', 0.0), ('sin cargador?', 1.0), ('Normal:', 2.3), ('Apple ya no lo pone.', 3.2),
    ('Aquí tiene los dos:', 4.9), ('adaptador de 20 W', 6.3), ('y cable.', 7.9), ('Originales de Apple,', 8.9),
    ('en su caja sin abrir.', 10.3), ('En Apple, 38 €.', 12.4), ('Aquí, 18,99 €.', 15.2),
    ('Compramos por cantidad', 17.9), ('y ganamos menos.', 19.0), ('Envío gratis', 21.0),
    ('en 24-48 h.', 22.0), ('Dese prisa:', 24.5), ('este precio acaba el jueves.', 25.6), ('Toque «Comprar».', 27.0),
]
# v3 (11/11): oferta ampliada al 30/11. Se cambió la frase final por la voz nueva
#    (voz-frase-30nov.mp3) sobre un plano de los dos packs; todo lo de después va 0,5 s más tarde.
SUBS_V3 = SUBS_V2[:-3] + [('Dese prisa:', 24.4), ('este precio acaba el 30/11.', 25.5), ('Toque «Comprar».', 28.28)]


# ---------------------------------------------------------------------------------------------------------------
# v6: dónde va cada texto en cada plano. Coordenadas en 1080x1920 (se multiplican por K). Medido sobre los
# fotogramas del máster limpio (sin textos) de los montajes v4 y v5 el 23/11:
#   sub    = borde de arriba de la pastilla del subtítulo (alto 84): sin tapar cara ni cajas
#   ia     = rótulo «Tienda online · escena recreada con IA»: ['izq'|'der', y] una línea arriba,
#            ['der2', y] dos líneas arriba a la derecha (plano 2b: la cara llena la parte de arriba),
#            ['centro', y] una línea centrada (primeros planos: bajo el subtítulo, sobre la camiseta)
#   chip   = borde de arriba del chip dorado del precio (plano 2a/2b; arriba está la cara o el pelo)
#   neon   = [y_desenfocado, y_fin]: desenfoca y oscurece el letrero de neón por encima (la «a» mal hecha, D7)
# tarjeta.y: [t, y del borde de abajo] de la tarjeta del precio; en el plano 4 abierto sigue el acercamiento de la
#   cámara para tapar el neón sin pisar el pelo (borde de abajo = arranque del pelo - 6 px).
# packs.kf: [t, x0, x1, y_pestaña] del par USB-C y del par Lightning en el mostrador (plano 4 abierto).
# chip_fundido (opcional): [t, ...] cortes en los que el chip se va en los 4 fotogramas de antes y vuelve en los 4 de
#   después (el último antes del corte y el primero, sin chip), para que no salte de sitio (23/11, T3).
PLAN_V6 = {
    'v4': {
        'planos': [
            {'de': 0.0, 'a': 4.875, 'sub': 1098, 'ia': ['izq', 296]},                  # 1 abierto, mostrador
            {'de': 4.875, 'a': 7.125, 'sub': 862, 'chip': 800, 'ia': ['der', 296]},    # 2a escaparate (clipA)
            {'de': 7.125, 'a': 11.79, 'sub': 674, 'chip': 612, 'ia': ['der2', 296]},   # 2b primer plano (clipB)
            {'de': 11.79, 'a': 14.92, 'sub': 1156, 'ia': ['izq', 296], 'neon': [380, 420]},  # 3 primer plano
            {'de': 14.92, 'a': 20.75, 'sub': 860, 'ia': ['izq', 296]},                 # 4 abierto, mostrador
            {'de': 20.75, 'a': 24.33, 'sub': 1110, 'ia': ['centro', 1206]},            # 4 primer plano
            {'de': 24.33, 'a': 27.92, 'sub': 790, 'ia': ['centro', 886]},              # 5 entrega (clipC)
            {'de': 27.92, 'a': 999, 'sub': 1110, 'ia': ['centro', 1206]},              # 6 primer plano
        ],
        'chip': [4.9, 11.79],
        'tarjeta': {'de': 11.79, 'a': 20.75, 'beat2': 15.15, 'pregunta': 17.85,
                    'y': [[11.79, 462], [14.917, 462], [14.92, 563], [17.45, 529], [20.45, 484], [20.75, 479]]},
        'packs': {'de': 16.95, 'a': 20.75,
                  'kf': [[14.95, 152, 510, 1086, 544, 904, 1084], [16.45, 134, 510, 1092, 544, 924, 1090],
                         [17.95, 116, 508, 1098, 544, 944, 1094], [19.45, 96, 508, 1102, 544, 964, 1100],
                         [20.45, 84, 508, 1106, 544, 976, 1104], [20.75, 82, 508, 1107, 544, 978, 1105]]},
    },
}
# v5: el 2a acaba 6 fotogramas antes (6,875 s) y el plano 5 es clipT (caja en las dos manos, cara 135-667,
#     pestañas de la caja desde y 989).
PLAN_V6['v5'] = dict(PLAN_V6['v4'], planos=[dict(p) for p in PLAN_V6['v4']['planos']])
PLAN_V6['v5']['planos'][1]['a'] = PLAN_V6['v5']['planos'][2]['de'] = 6.875
PLAN_V6['v5']['planos'][6].update(sub=800, ia=['centro', 896])


def v6(argv):
    """Rótulos v6: se dibujan fotograma a fotograma (numpy) sobre el clip y se codifica una sola vez en BT.709."""
    import json, os
    import numpy as np, cv2
    cv2.setNumThreads(2)
    pos, opt, i = [], {}, 1
    while i < len(argv):
        if argv[i].startswith('--'): opt[argv[i][2:]] = argv[i + 1]; i += 2
        else: pos.append(argv[i]); i += 1
    clip, fuentes, salida = pos[:3]
    R = float(pos[4]) if len(pos) > 4 else 0.0
    K = int(pos[5]) if len(pos) > 5 else 1
    W, H, FPS = 1080 * K, 1920 * K, 24
    PRECIO, PLAZO, ACABA = opt.get('precio', '18,99'), opt.get('plazo', '30 de noviembre'), opt.get('acaba', '30/11')
    m = opt.get('montaje', 'v4')
    PLAN = PLAN_V6[m] if m in PLAN_V6 else json.load(open(m))
    NOCHE, ORO, MARFIL, ROJO, BLANCO = (11, 15, 26), (214, 180, 112), (244, 241, 234), (196, 38, 46), (255, 255, 255)
    GRIS = (226, 226, 232)
    FUNDIDO = 6

    # ---- subtítulos: los de v3 con «¡Normal!» y «y ganamos menos.» a 19,45 s; *texto* = en oro
    if 'subs' in opt:
        SUBS = [tuple(s) for s in json.load(open(opt['subs']))]
    else:
        SUBS = [('¡Normal!' if t == 'Normal:' else t, 19.45 if t == 'y ganamos menos.' else x) for t, x in SUBS_V3]
        SUBS = [(t.replace('18,99 €', f'*{PRECIO} €*').replace('30/11', ACABA), x) for t, x in SUBS]
        if not ACABA:   # sin plazo: fuera la urgencia; «en 24-48 h.» acaba donde acababa (hueco hasta «Toque…»)
            SUBS = [('' if t.startswith('Dese prisa') else t, x) for t, x in SUBS if not t.startswith('este precio acaba')]
    FIN_VOZ = 29.3 + R
    SUBS = [(t, x + R) for t, x in SUBS]

    # ---- fuentes y dibujo
    def unb(t, w=700):
        f = ImageFont.truetype(f'{fuentes}/Unbounded.ttf', round(t * K)); f.set_variation_by_axes([w]); return f

    def arc(t, w=600, ancho=100):
        f = ImageFont.truetype(f'{fuentes}/Archivo.ttf', round(t * K)); f.set_variation_by_axes([w, ancho]); return f
    MED = ImageDraw.Draw(Image.new('RGB', (8, 8)))
    def largo(t, f): return MED.textlength(t, font=f)
    def alto_mayus(f): b = f.getbbox('H', anchor='ls'); return -b[1]

    def trozos(txt):
        """'Aquí, *18,99 €*.' -> [('Aquí, ', blanco), ('18,99 €', oro), ('.', blanco)]"""
        out = []
        for j, p in enumerate(txt.split('*')):
            if p: out.append((p, ORO if j % 2 else BLANCO))
        return out

    def a_capa(im):
        """PIL RGBA -> (rgb premultiplicado float32, alfa float32 0-1)."""
        a = np.asarray(im, dtype=np.float32) / 255.0
        return a[..., :3] * a[..., 3:] * 255.0, a[..., 3:]

    def sombra(im, radio=10, fuerza=150, dy=3):
        al = im.split()[3].filter(ImageFilter.GaussianBlur(radio * K / 2))
        s = Image.new('RGBA', im.size, (0, 0, 0, 0)); s.putalpha(al.point(lambda v: min(255, int(v * fuerza / 255))))
        out = Image.new('RGBA', im.size, (0, 0, 0, 0)); out.alpha_composite(s, (0, round(dy * K))); out.alpha_composite(im)
        return out

    def pastilla_txt(segs, f, alto, pad, fondo, borde=None):
        """Pastilla redondeada con texto centrado en la altura de las mayúsculas. Devuelve PIL RGBA ajustada."""
        tw = sum(largo(s, f) for s, _ in segs); w = round(tw + 2 * pad * K); h = round(alto * K)
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, w - 1, h - 1), radius=h / 2, fill=fondo, outline=borde, width=max(1, K) if borde else 0)
        x = pad * K; yb = h / 2 + alto_mayus(f) / 2
        for s, c in segs:
            d.text((x, yb), s, font=f, fill=c, anchor='ls'); x += largo(s, f)
        return im

    # ---- capas fijas
    cache = {}

    def capa_sub(txt):
        if ('sub', txt) not in cache:
            segs = trozos(txt); t = 52
            while sum(largo(s, arc(t, 800)) for s, _ in segs) > (880 - 68) * K: t -= 2
            im = pastilla_txt(segs, arc(t, 800), 84, 34, NOCHE + (200,), (255, 255, 255, 22))
            cache[('sub', txt)] = a_capa(im)
        return cache[('sub', txt)]

    IA = 'Tienda online · escena recreada con IA'
    def capa_ia(modo):
        if ('ia', modo) not in cache:
            f = arc(24, 600)
            lineas = ['Tienda online', 'Escena recreada con IA'] if modo == 'der2' else [IA]
            tw = max(largo(l, f) for l in lineas); pad, lh = 14 * K, 30 * K
            w, h = round(tw + 2 * pad), round(len(lineas) * lh + 8 * K)
            im = Image.new('RGBA', (w + 8 * K, h + 8 * K), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
            d.rounded_rectangle((4 * K, 4 * K, 4 * K + w, 4 * K + h), radius=min(h / 2, 16 * K), fill=NOCHE + (92,))
            for j, l in enumerate(lineas):
                x = 4 * K + (w - pad - largo(l, f) if modo == 'der2' else pad)
                yb = 4 * K + 4 * K + j * lh + lh / 2 + alto_mayus(f) / 2
                d.text((x + K, yb + K), l, font=f, fill=(0, 0, 0, 150), anchor='ls')
                d.text((x, yb), l, font=f, fill=(255, 255, 255, 212), anchor='ls')
            cache[('ia', modo)] = a_capa(im)
        return cache[('ia', modo)]

    def capa_chip():
        if 'chip' not in cache:
            segs = [('Cargador 20 W + cable Apple · ', NOCHE), (f'{PRECIO} €', NOCHE)]
            f = arc(29, 700); f2 = arc(29, 850)
            tw = largo(segs[0][0], f) + largo(segs[1][0], f2); h = round(52 * K); w = round(tw + 52 * K)
            im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
            d.rounded_rectangle((0, 0, w - 1, h - 1), radius=h / 2, fill=ORO + (250,))
            yb = h / 2 + alto_mayus(f) / 2
            d.text((26 * K, yb), segs[0][0], font=f, fill=NOCHE, anchor='ls')
            d.text((26 * K + largo(segs[0][0], f), yb), segs[1][0], font=f2, fill=NOCHE, anchor='ls')
            cache['chip'] = a_capa(im)
        return cache['chip']

    def capa_pack(txt):
        if ('pack', txt) not in cache:
            cache[('pack', txt)] = a_capa(pastilla_txt([(txt, MARFIL)], arc(26, 700), 42, 18, NOCHE + (225,), ORO + (200,)))
        return cache[('pack', txt)]

    # ---- tarjeta del precio: 3 estados (alto en px de 1080) que se funden; el panel se dibuja con el alto del momento
    TX0, TX1 = 90, 990
    def contenido(estado):
        hs = {'apple': 126, 'precio': 184, 'pregunta': 140}
        h = hs[estado]; im = Image.new('RGBA', ((TX1 - TX0) * K, h * K), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        cw = (TX1 - TX0) * K
        if estado == 'apple':
            f1, f2, f3 = arc(40, 650), unb(52, 700), arc(28, 500)
            a, b = 'En Apple: ', '38,00 €'
            x = (cw - largo(a, f1) - largo(b, f2)) / 2
            d.text((x, 70 * K), a, font=f1, fill=MARFIL, anchor='ls'); d.text((x + largo(a, f1), 70 * K), b, font=f2, fill=BLANCO, anchor='ls')
            q = '(precio del 01/11/2026)'
            d.text(((cw - largo(q, f3)) / 2, 108 * K), q, font=f3, fill=GRIS, anchor='ls')
        elif estado == 'precio':
            fp = unb(92, 800); p = f'{PRECIO} €'
            fa, fb, fq = arc(26, 600), unb(40, 700), arc(24, 500)
            wd = max(largo('En Apple', fa), largo('38,00 €', fb), largo('(precio del 01/11/2026)', fq))
            gap = 64 * K; total = largo(p, fp) + gap + wd; x = (cw - total) / 2
            d.text((x, 110 * K), p, font=fp, fill=ORO, anchor='ls')
            xr = x + largo(p, fp) + gap
            d.line([(xr - gap / 2, 34 * K), (xr - gap / 2, 116 * K)], fill=(255, 255, 255, 46), width=max(1, round(1.5 * K)))
            d.text((xr, 52 * K), 'En Apple', font=fa, fill=GRIS, anchor='ls')
            d.text((xr, 94 * K), '38,00 €', font=fb, fill=BLANCO, anchor='ls')
            d.text((xr, 122 * K), '(precio del 01/11/2026)', font=fq, fill=GRIS, anchor='ls')
            d.line([(40 * K, 138 * K), (cw - 40 * K, 138 * K)], fill=(255, 255, 255, 34), width=max(1, K))
            l = '1 adaptador 20 W + 1 cable (USB-C o Lightning)'; fl = arc(28, 600)
            d.text(((cw - largo(l, fl)) / 2, 170 * K), l, font=fl, fill=MARFIL, anchor='ls')
        else:
            f = unb(46, 700); q = '¿Por qué tan barato?'
            d.text(((cw - largo(q, f)) / 2, (h * K + alto_mayus(f)) / 2), q, font=f, fill=ORO, anchor='ls')
        return a_capa(im), h

    SOMBRA_M = 26
    def panel(h):
        """Panel opaco de la tarjeta (con sombra suave) de alto h (px de 1080, puede ser decimal)."""
        hk = round(h * K)
        if ('panel', hk) not in cache:
            M = SOMBRA_M * K; w = (TX1 - TX0) * K
            im = Image.new('RGBA', (w + 2 * M, hk + 2 * M), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
            d.rounded_rectangle((M, M, M + w - 1, M + hk - 1), radius=32 * K, fill=NOCHE + (248,),
                                outline=(255, 255, 255, 30), width=max(1, K))
            cache[('panel', hk)] = a_capa(sombra(im, 16, 120, 4))
        return cache[('panel', hk)]

    def foto_producto():
        ruta = opt.get('foto', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'fotos', 'estudio-pro', 'pack-usbc.png'))
        im = Image.open(ruta)
        if im.mode == 'RGBA' and im.getextrema()[3][0] < 250: return im
        # recorte: rembg (isnet) + agujeros de las dos pestañas, que se ven grises a través del cartón
        import onnxruntime as ort
        from rembg import new_session, remove
        so = ort.SessionOptions(); so.intra_op_num_threads = 2; so.inter_op_num_threads = 1
        rgb = im.convert('RGB'); mk = np.asarray(remove(rgb, session=new_session('isnet-general-use', sess_opts=so), only_mask=True, post_process_mask=True)).copy()
        g = np.asarray(rgb, dtype=np.int16).mean(2); n_, lab, st, _ = cv2.connectedComponentsWithStats(((g < 228) & (mk > 128)).astype(np.uint8))
        for j in range(1, n_):
            x, y, w, h, a = st[j]
            if a > 5000 and w > 3 * h and y < mk.shape[0] * 0.35:           # ranura alargada de la pestaña
                hole = cv2.GaussianBlur(cv2.morphologyEx((lab == j).astype(np.uint8) * 255, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)), (0, 0), 1.0)
                mk = np.clip(mk.astype(np.int16) - hole, 0, 255).astype(np.uint8)
        ys, xs = np.where(mk > 8)
        return Image.fromarray(np.dstack([np.asarray(rgb), mk])[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 'RGBA')

    def cierre(ult):
        """Tarjeta final (PIL RGB W x H): fondo = último fotograma desenfocado y oscurecido; todo entre y 300 y 1240."""
        bg = Image.fromarray(ult).filter(ImageFilter.GaussianBlur(18 * K))
        bg = Image.blend(bg, Image.new('RGB', bg.size, NOCHE), .74).convert('RGBA')
        capa = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
        def c(yb, t, f, col): d.text(((W - largo(t, f)) / 2, yb * K), t, font=f, fill=col, anchor='ls')
        def cm(yb, t, tam, peso, col, maximo=900):
            while largo(t, arc(tam, peso)) > maximo * K: tam -= 1
            c(yb, t, arc(tam, peso), col)
        c(350, 'pillatumovil', unb(50, 600), MARFIL)
        cm(394, 'Adaptador 20 W + cable · originales de Apple', 28, 600, GRIS)
        # foto real de los dos packs (adaptador + cable): luz suave detrás y sombra de apoyo
        fo = foto_producto(); hf = 300 * K; wf = round(fo.width * hf / fo.height); fo = fo.resize((wf, hf), Image.LANCZOS)
        xf, yf = (W - wf) // 2, 422 * K
        luz = Image.new('L', (W, H), 0); ImageDraw.Draw(luz).ellipse((xf - 60 * K, yf - 30 * K, xf + wf + 60 * K, yf + hf + 40 * K), fill=46)
        luz = luz.filter(ImageFilter.GaussianBlur(60 * K)); lz = Image.new('RGBA', (W, H), ORO + (0,)); lz.putalpha(luz)
        so = Image.new('L', (W, H), 0); ImageDraw.Draw(so).ellipse((xf + 30 * K, yf + hf - 14 * K, xf + wf - 30 * K, yf + hf + 16 * K), fill=150)
        so = so.filter(ImageFilter.GaussianBlur(12 * K)); sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sh.putalpha(so)
        bg.alpha_composite(lz); bg.alpha_composite(sh); bg.alpha_composite(fo, (xf, yf))
        c(840, f'{PRECIO} €', unb(108, 800), ORO)
        cm(888, 'En Apple, 38,00 € (precio del 01/11/2026)', 30, 500, MARFIL)
        y = 916
        if PLAZO:
            t = f'Precio de lanzamiento hasta el {PLAZO}'; f = arc(27, 700); w = largo(t, f) + 48 * K
            d.rounded_rectangle(((W - w) / 2, y * K, (W + w) / 2, (y + 46) * K), radius=23 * K, fill=ROJO + (255,))
            c(y + 23 + alto_mayus(f) / 2 / K, t, f, BLANCO); y += 46
        cm(y + 52, 'Envío gratis · llega a su casa en 24-48 h laborables', 29, 600, MARFIL)
        cm(y + 92, 'Cable USB-C o Lightning, mismo precio', 29, 600, MARFIL)
        c(y + 162, 'Toque «Comprar» ↓', unb(40, 700), ORO)
        cm(y + 212, 'Precios con IVA incluido', 23, 500, GRIS)
        cm(y + 242, 'Tienda online independiente, no afiliada a Apple Inc.', 23, 500, GRIS)
        bg.alpha_composite(sombra(capa, 8, 140, 2))
        return np.asarray(bg.convert('RGB')).copy(), capa.getbbox()   # y la caja de los textos (px de salida)

    # ---- tiempos y posiciones
    def lerp_kf(kf, t, cols):
        if t <= kf[0][0]: return [kf[0][c] for c in cols]
        for a, b in zip(kf, kf[1:]):
            if a[0] <= t <= b[0]:
                u = (t - a[0]) / max(1e-6, b[0] - a[0]); return [a[c] + (b[c] - a[c]) * u for c in cols]
        return [kf[-1][c] for c in cols]
    def suave(u): u = min(1.0, max(0.0, u)); return u * u * (3 - 2 * u)
    def plano(t): return next((p for p in PLAN['planos'] if p['de'] <= t < p['a']), PLAN['planos'][-1])

    def pegar(fr, capa, x, y, op=1.0):
        rgb, a = capa; h, w = a.shape[:2]; x, y = int(round(x)), int(round(y))
        x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w, W), min(y + h, H)
        if x0 >= x1 or y0 >= y1 or op <= 0: return
        sub = fr[y0:y1, x0:x1].astype(np.float32); ca = a[y0 - y:y1 - y, x0 - x:x1 - x] * op
        fr[y0:y1, x0:x1] = np.clip(sub * (1 - ca) + rgb[y0 - y:y1 - y, x0 - x:x1 - x] * op + 0.5, 0, 255).astype(np.uint8)

    TJ, CH, PK = PLAN['tarjeta'], PLAN.get('chip'), PLAN.get('packs')
    ESTADOS = {e: contenido(e) for e in ('apple', 'precio', 'pregunta')}

    def componer(fr, t, n, n_fin):
        p = plano(t)
        if p.get('neon'):                                  # neón desenfocado y apagado (bajo la tarjeta en el plano 3)
            y_ok, y_fin = p['neon'][0] * K, p['neon'][1] * K
            zona = fr[:y_fin].astype(np.float32)
            bl = cv2.GaussianBlur(zona, (0, 0), 22 * K) * 0.66
            mk = np.clip((y_fin - np.arange(y_fin, dtype=np.float32)) / max(1, y_fin - y_ok), 0, 1)[:, None, None]
            fr[:y_fin] = np.clip(zona * (1 - mk) + bl * mk + .5, 0, 255).astype(np.uint8)
        if n < n_fin:                                      # rótulo IA: del primer fotograma a la tarjeta final
            modo, yi = p['ia']; capa = capa_ia(modo); w = capa[1].shape[1]; o = 4 * K
            x = {'izq': 90 * K - o, 'der': 990 * K - w + o, 'der2': 990 * K - w + o, 'centro': (W - w) / 2}[modo]
            pegar(fr, capa, x, yi * K - o)
        for j, (txt, ini) in enumerate(SUBS):              # subtítulos (corte seco, como en v3; fuera en el fundido)
            fin = SUBS[j + 1][1] if j + 1 < len(SUBS) else FIN_VOZ
            if txt and ini <= t < fin and n < n_fin:
                capa = capa_sub(txt); pegar(fr, capa, (W - capa[1].shape[1]) / 2, p['sub'] * K)
        if CH and p.get('chip') is not None and CH[0] + R <= t < CH[1]:
            capa = capa_chip(); op = suave((t - CH[0] - R) / 0.25)
            for tc in PLAN.get('chip_fundido', []):        # 23/11 (T3): en esos cortes el chip se va y vuelve (4 fotogramas
                d = (t - tc - R) * FPS                      # a cada lado; el último antes del corte y el primero, sin chip)
                if -5 < d < 5: op *= suave((abs(d + 0.5) - 0.5) / 4)
            pegar(fr, capa, (W - capa[1].shape[1]) / 2, (p['chip'] + 8 * (1 - op)) * K, op)
        if TJ['de'] <= t < TJ['a']:                        # tarjeta del precio en dos tiempos + la pregunta
            b2, pq = TJ['beat2'] + R, TJ['pregunta'] + R; D = 0.38
            if t < b2: A, B, r = 'apple', 'apple', 0.0
            elif t < pq: A, B, r = 'apple', 'precio', (t - b2) / D
            else: A, B, r = 'precio', 'pregunta', (t - pq) / D
            # el panel cambia de alto mientras lo de antes se va y, después, entra lo nuevo (nunca los dos a la vez)
            hA, hB = ESTADOS[A][1], ESTADOS[B][1]; h = hA + (hB - hA) * suave(r)
            opA, opB = 1 - suave(r / 0.42), suave((r - 0.42) / 0.58)
            yb = lerp_kf(TJ['y'], t, [1])[0]; top = yb - h
            pegar(fr, panel(h), (TX0 - SOMBRA_M) * K, (top - SOMBRA_M) * K)
            if opA > 0: pegar(fr, ESTADOS[A][0], TX0 * K, (top + (h - hA) / 2) * K, opA)
            if opB > 0: pegar(fr, ESTADOS[B][0], TX0 * K, (top + (h - hB) / 2 + 8 * (1 - opB)) * K, opB)
        if PK and PK['de'] + R <= t < PK['a']:             # «Pack USB-C» / «Pack Lightning» sobre cada pareja
            op = suave((t - PK['de'] - R) / 0.3)
            ux0, ux1, uy, lx0, lx1, ly = lerp_kf(PK['kf'], t, [1, 2, 3, 4, 5, 6])
            for x0, x1, yy, txt in ((ux0, ux1, uy, 'Pack USB‑C'), (lx0, lx1, ly, 'Pack Lightning')):
                yl = yy - 12; im = Image.new('RGBA', (round((x1 - x0) * K), round(14 * K)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
                lw = max(2, round(3 * K)); ww = im.width - 1
                d.line([(lw, im.height - 1), (lw, lw), (ww - lw, lw), (ww - lw, im.height - 1)], fill=ORO + (235,), width=lw, joint='curve')
                pegar(fr, a_capa(im), x0 * K, yl * K - lw, op)
                capa = capa_pack(txt); pw, ph = capa[1].shape[1], capa[1].shape[0]
                pegar(fr, capa, (x0 + x1) / 2 * K - pw / 2, yl * K - ph - 4 * K, op)
        return fr

    # ---- lectura y escritura (BT.709 en las dos puntas y redondeo exacto: la imagen del clip no cambia de color;
    #      sin accurate_rnd, swscale la oscurecía 1-2 niveles en la ida y vuelta RGB)
    def lector(extra_in, extra_vf=''):
        vf = f'scale={W}:{H}:flags=lanczos+accurate_rnd+full_chroma_int:in_color_matrix=bt709:in_range=tv{extra_vf},format=rgb24'
        return subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-threads', '2', *extra_in, '-i', clip, '-vf', vf,
                                 '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    def leer(pr):
        b = pr.stdout.read(W * H * 3)
        return np.frombuffer(b, np.uint8).reshape(H, W, 3).copy() if len(b) == W * H * 3 else None

    pr = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-count_packets', '-show_entries',
                         'stream=nb_read_packets', '-of', 'csv=p=0', clip], capture_output=True, text=True)
    N = int(pr.stdout.strip().split(',')[0])
    ult = None; pr = lector(['-sseof', '-0.5'])
    while (f := leer(pr)) is not None: ult = f
    CARD, CAJA_TXT = cierre(ult)
    n_fin = N - FUNDIDO                                     # primer fotograma del fundido a la tarjeta
    total = N - FUNDIDO + round(float(opt.get('cierre', 2.75)) * FPS)

    # 23/11 (2.ª revisión, N5): la tarjeta final ya no es una foto fija: toda ella (fondo, foto y textos) se acerca despacio
    # (--empuje, 3,5 % por defecto) desde el primer fotograma del fundido hasta el último, con arranque y llegada suaves
    # (mitad smoothstep, mitad lineal: nunca se para del todo). El centro del acercamiento es el punto más cercano al centro
    # de la foto del producto con el que ningún texto sale de x 90-990, y 300-1240 (si no lo hay, se acerca menos).
    tx0, ty0, tx1, ty1 = [v / K for v in CAJA_TXT]
    def centro(s, a0, a1, lo, hi, pref):
        # punto c que deja [c + s(a0 - c), c + s(a1 - c)] dentro de [lo, hi], lo más cerca posible de pref (None si no hay)
        c_lo, c_hi = (s * a1 - hi) / (s - 1), (s * a0 - lo) / (s - 1)
        return None if c_lo > c_hi else min(c_hi, max(c_lo, pref))
    SMAX = 1 + float(opt.get('empuje', 0.035))
    while SMAX > 1.0005:
        ccx = centro(SMAX, tx0, tx1, 90, 990, W / 2 / K); ccy = centro(SMAX, ty0, ty1, 300, 1240, 572)   # foto: y 422-722
        if ccx is not None and ccy is not None: break
        SMAX -= 0.0005
    else: SMAX, ccx, ccy = 1.0, W / 2 / K, 572
    print(f'cierre: textos en x {tx0:.0f}-{tx1:.0f}, y {ty0:.0f}-{ty1:.0f}; acercamiento x1,000 -> x{SMAX:.4f} '
          f'hacia ({ccx:.0f}, {ccy:.0f}); al final, textos en x {ccx + SMAX * (tx0 - ccx):.0f}-{ccx + SMAX * (tx1 - ccx):.0f}, '
          f'y {ccy + SMAX * (ty0 - ccy):.0f}-{ccy + SMAX * (ty1 - ccy):.0f}')
    def tarjeta(n):
        u = min(1.0, max(0.0, (n - n_fin) / max(1, total - 1 - n_fin)))
        s = 1 + (SMAX - 1) * (0.5 * suave(u) + 0.5 * u)
        if s <= 1.00001: return CARD
        Mx = np.array([[s, 0, (1 - s) * ccx * K], [0, s, (1 - s) * ccy * K]], np.float64)
        return cv2.warpAffine(CARD, Mx, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)

    def mezclar(fr, n):
        if n < n_fin: return fr
        if n >= N: return tarjeta(n)
        a = (n - n_fin + 1) / FUNDIDO
        return (fr.astype(np.float32) * (1 - a) + tarjeta(n).astype(np.float32) * a + .5).astype(np.uint8)

    if 'fotos' in opt:                                      # solo fotogramas sueltos
        os.makedirs(salida, exist_ok=True)
        for ts in opt['fotos'].split(','):
            n = round(float(ts) * FPS); t = n / FPS
            if n < N:
                pr = lector(['-ss', f'{t:.4f}'], ''); fr = leer(pr); pr.kill()
                fr = mezclar(componer(fr, t, n, n_fin), n)
            else: fr = tarjeta(n)
            Image.fromarray(fr).save(f'{salida}/t{float(ts):05.2f}.jpg', quality=92)
        print('ok', salida); return

    audio = opt.get('audio', clip)
    enc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                            '-r', str(FPS), '-i', '-', '-i', audio, '-map', '0:v', '-map', '1:a?',
                            '-vf', 'scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd+full_chroma_int,format=yuv420p',
                            '-c:v', 'libx264', '-preset', opt.get('preset', 'medium'), '-crf', opt.get('crf', '16' if K > 1 else '18'), '-threads', opt.get('hilos', '2'),
                            '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv',
                            '-af', 'apad', '-t', f'{total / FPS:.4f}', '-c:a', 'aac', '-b:a', '160k', '-ar', '44100', '-ac', '2',
                            '-movflags', '+faststart', salida], stdin=subprocess.PIPE)
    pr = lector([])
    for n in range(total):
        fr = leer(pr) if n < N else None
        out = mezclar(componer(fr, n / FPS, n, n_fin), n) if fr is not None else tarjeta(n)
        enc.stdin.write(out.tobytes())
    enc.stdin.close(); enc.wait(); pr.kill()
    print('ok', salida, f'{total} fotogramas')


if len(sys.argv) > 4 and sys.argv[4] == 'v6':
    v6(sys.argv); sys.exit(0)

clip, fuentes, salida = sys.argv[1:4]
VERSION = sys.argv[4] if len(sys.argv) > 4 else 'v2'
RETRASO = float(sys.argv[5]) if len(sys.argv) > 5 else 0.0
K = int(sys.argv[6]) if len(sys.argv) > 6 else 1   # 2 = 4K nativo
W, H = 1080 * K, 1920 * K
NOCHE = (11, 15, 26); ORO = (214, 180, 112); MARFIL = (244, 241, 234); ROJO = (196, 38, 46)


def unb(t, w=700):
    f = ImageFont.truetype(f'{fuentes}/Unbounded.ttf', t * K); f.set_variation_by_axes([w]); return f


def arc(t, w=600):
    f = ImageFont.truetype(f'{fuentes}/Archivo.ttf', t * K); f.set_variation_by_axes([w, 100]); return f


PLAZO = {'v1': 'hasta el jueves 12/11, 18:00', 'v2': 'hasta el jueves 12/11, 18:00', 'v3': 'hasta el 30 de noviembre'}[VERSION]
if VERSION == 'v1':
    SUBS, FIN_VOZ, PRECIO = SUBS_V1, 15.0, (6.84, 11.30)
elif VERSION == 'v2':
    SUBS, FIN_VOZ, PRECIO = SUBS_V2, 28.8, (12.4, 17.8)
else:
    SUBS, FIN_VOZ, PRECIO = SUBS_V3, 29.3, (12.4, 17.8)
SUBS = [(t, x + RETRASO) for t, x in SUBS]
FIN_VOZ += RETRASO
PRECIO = (PRECIO[0] + RETRASO, PRECIO[1] + RETRASO)

Y_SUB = 1720 * K


def capa_sub(txt):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    t = 64; f = unb(t, 800)
    while d.textlength(txt, font=f) > W - 100 * K:
        t -= 4; f = unb(t, 800)
    tw = d.textlength(txt, font=f)
    x = (W - tw) / 2
    d.text((x, Y_SUB), txt, font=f, fill=(255, 255, 255), stroke_width=7 * K, stroke_fill=(0, 0, 0))
    return im


def capa_precio():
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((170 * K, 150 * K, W - 170 * K, 420 * K), radius=40 * K, fill=NOCHE + (225,))
    f = unb(130); t = '18,99 €'
    d.text(((W - d.textlength(t, font=f)) / 2, 170 * K), t, font=f, fill=ORO)
    f2 = arc(30, 600); t2 = 'En Apple, 38,00 € (precio del 01/11/2026)'
    d.text(((W - d.textlength(t2, font=f2)) / 2, 350 * K), t2, font=f2, fill=MARFIL)
    return im


def cierre(fondo_png):
    bg = Image.open(fondo_png).convert('RGB').filter(ImageFilter.GaussianBlur(6 * K))
    bg = Image.blend(bg, Image.new('RGB', bg.size, NOCHE), .55)
    d = ImageDraw.Draw(bg)
    def c(y, t, f, col): d.text(((W - d.textlength(t, font=f)) / 2, y * K), t, font=f, fill=col)
    c(560, 'pillatumovil', unb(84), MARFIL)
    c(700, 'Cargador 20 W + cable · originales de Apple', arc(34), MARFIL)
    c(790, '18,99 €', unb(170), ORO)
    c(1010, 'En Apple, 38,00 € (precio del 01/11/2026)', arc(30, 500), MARFIL)
    d.rounded_rectangle((90 * K, 1100 * K, W - 90 * K, 1180 * K), radius=40 * K, fill=ROJO)
    c(1122, f'Precio de lanzamiento · {PLAZO}', arc(30, 800), (255, 255, 255))
    c(1220, 'Envío gratis · llega a su casa en 24-48 h', arc(34, 700), MARFIL)
    d.rounded_rectangle((110 * K, 1320 * K, W - 110 * K, 1430 * K), radius=55 * K, fill=ORO)
    c(1352, 'pillatumovil.com  →', unb(46), NOCHE)
    return bg


tmp = tempfile.mkdtemp()
capas = []
for i, (t, ini) in enumerate(SUBS):
    fin = SUBS[i + 1][1] if i + 1 < len(SUBS) else FIN_VOZ
    capas.append((capa_sub(t), ini, fin))
capas.append((capa_precio(), *PRECIO))
for i, (im, _, _) in enumerate(capas):
    im.save(f'{tmp}/c{i}.png')

subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-sseof', '-0.5', '-i', clip, '-frames:v', '1', '-vf', f'scale={W}:{H}', f'{tmp}/ult.png'], check=True)
cierre(f'{tmp}/ult.png').save(f'{tmp}/cierre.png')
ins = ['-i', clip] + sum([['-i', f'{tmp}/c{i}.png'] for i in range(len(capas))], [])
fc = f'[0:v]scale={W}:{H}:flags=lanczos,setsar=1,format=yuv420p[v0];'
for i, (_, a, b) in enumerate(capas):
    fc += f"[v{i}][{i+1}:v]overlay=0:0:enable='between(t,{a:.2f},{b:.2f})'[v{i+1}];"
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *ins, '-filter_complex', fc.rstrip(';'), '-map', f'[v{len(capas)}]', '-map', '0:a?',
                '-c:v', 'libx264', '-crf', '14' if K > 1 else '18', '-preset', 'medium', '-c:a', 'aac', '-b:a', '160k', '-ar', '44100', '-ac', '2', '-r', '24', f'{tmp}/a.mp4'], check=True)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-loop', '1', '-t', '2.5', '-i', f'{tmp}/cierre.png', '-f', 'lavfi', '-t', '2.5', '-i', 'anullsrc=r=44100:cl=stereo',
                '-vf', 'format=yuv420p,fade=in:0:8', '-c:v', 'libx264', '-crf', '14' if K > 1 else '18', '-r', '24', '-c:a', 'aac', '-shortest', f'{tmp}/b.mp4'], check=True)
open(f'{tmp}/l.txt', 'w').write(f"file '{tmp}/a.mp4'\nfile '{tmp}/b.mp4'\n")
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', f'{tmp}/l.txt', '-c:v', 'libx264', '-crf', '18' if K > 1 else '19', '-c:a', 'aac', '-movflags', '+faststart', salida], check=True)
print('ok', salida)
