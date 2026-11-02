# Anuncios de Meta, noviembre 2026 (02/11/2026)

Pack USB-C a 18,99 €. Foto propia de estudio (ps-estudio-portada), fondo noche, Unbounded + Archivo.
Generadas con `tools/anuncio_meta.py`.

- **A** «El cargador que su iPhone ya no trae.»: creative 1761630894923060.
- **B** «Lo mismo que en Apple. La mitad.»: creative 1727772112198515.
- Formatos: feed 4:5 (1080x1350) y stories 9:16 (1080x1920). En Meta van con la 4:5. Este acceso no deja poner una imagen por ubicación; las 9:16 se pueden subir a mano en el Administrador de anuncios.
- Enlace: ficha del pack USB-C con utm_source=meta, utm_campaign=pack-usbc-2026-11, utm_content=A/B.
- Comparación: «En Apple, 38,00 € (precio del 01/11/2026)», el mismo PVP que la web. Si cambia el precio de Apple, hay que rehacer la imagen.
- **Publicados el 02/11/2026** (con permiso del dueño) en el conjunto «Nuevo conjunto de anuncios de Ventas» (120250314921150622), junto al anuncio de catálogo que ya había. Mismo presupuesto, sin tocar.
  - A: anuncio 120250353950680622, creative 1160007503350022.
  - B: anuncio 120250353951690622, creative 1280144227746676.
  - Los primeros creativos (1761630894923060 y 1727772112198515) llevaban la imagen dos veces (enlace y hash) y Meta no los publicaba. Quedan dos borradores con ese error en el Administrador de anuncios: se pueden descartar.
- Regla del dueño: puedo crear, publicar y pausar anuncios; **el presupuesto no se cambia sin su permiso**.

## Anuncio de la tienda: «¿Qué cargador necesita su iPhone?» (02/11/2026)

- Foto propia de la mesilla (ps-mesilla-v2) con dos teselas: iPhone 8 al 14 → cable Lightning; iPhone 15 al 18 → cable USB-C; pack 18,99 € cada uno. Generada con `tools/anuncio_tienda.py`.
- Enlace: portada, directo al selector «¿Qué iPhone tiene?» (`#su-iphone`), utm_campaign=tienda-2026-11.
- **Publicado**: anuncio 120250354025830622, creative 1113019388368373 (con la cuenta de Instagram 17841437289404273).
- Borrador sin publicar 120250354022660622: le faltaba la cuenta de Instagram. Se puede descartar.

## v2 (02/11/2026): la web en grande abajo y enlace a los packs

Petición del dueño: «poner el link abajo de la web directo, en grande» y «que la lleve directamente al producto de los packs».

- Las tres imágenes llevan abajo una franja dorada con «pillatumovil.com» en grande (Unbounded, noche sobre oro).
- Tienda: el enlace va a `/collections/packs` (los dos packs). A y B van a la ficha del pack USB-C.
- Publicados: tienda 120250354076460622 (creative 1752210195854821), A 120250354076720622 (2343264039792813), B 120250354077040622 (1681377504028642). Todos con la cuenta de Instagram.
- Pausados los anteriores (sin la franja): 120250354025830622, 120250353950680622, 120250353951690622.

## v3 (02/11/2026): el enlace escrito en el texto

Petición del dueño: «que la gente simplemente tenga que clicar, no buscar el nombre en Google».

- Primera línea del texto de los tres anuncios: «Compre aquí 👉 https://pillatumovil.com/collections/packs» (en Facebook se puede tocar). La imagen y el botón «Comprar» ya llevaban directo a la tienda.
- Publicados: tienda 120250354135760622, A 120250354136280622, B 120250354137560622.
- Pausados los v2: 120250354076460622, 120250354076720622, 120250354077040622.
- **Regla para todos los anuncios**: web en grande abajo en la imagen + enlace escrito en la primera línea + botón «Comprar» a los packs.

## v4 (02/11/2026): precio de lanzamiento y por qué es barato

Petición del dueño: «hasta fin de existencias» para enganchar y explicar por qué es tan económico.

- Imagen: el sello pasa a «Precio de lanzamiento · hasta fin de existencias» (es verdad mientras `ps_lanzamiento` esté activo en la web; cuando se acaben las unidades hay que quitarlo de los anuncios también).
- Texto: «¿Por qué tan barato? Es el mismo producto que vende Apple: compramos por cantidad y ganamos menos en cada pack.»
- Publicados: tienda 120250354421120622, A 120250354422090622, B 120250354423020622. Pausados los v3.
- Las revisiones automáticas (diaria 19:47 y lunes 10:13) ya no dependen de los IDs: miran todos los anuncios activos.

## Vídeo «problema → solución» (02/11/2026)

Hecho con `tools/video_anuncio.py` (ffmpeg + Pillow), con fotos y vídeos propios de la tienda (mesilla, estudio, unboxing). Sin IA ni música. 15,8 s.
Higgsfield tenía 0 créditos (plan gratis), por eso no se usó.

1. «Su iPhone ya no trae cargador.» (mesilla) 2. «En Apple: 38,00 €» con fecha (estudio) 3. «El mismo. Original y precintado.» (unboxing) 4. «Aquí, el pack: 18,99 €» + lanzamiento + por qué es barato 5. Cierre con «pillatumovil.com».

- `pillatumovil_video_problema-solucion_4x5.mp4` (el del anuncio) y `_9x16.mp4` (stories/reels, para subir a mano).
- Vídeo en Meta: 1140870675096291, portada hash f282c0782081e7b2071f0358268d5f0e.
