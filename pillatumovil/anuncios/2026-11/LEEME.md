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
- **Publicado**: anuncio 120250354553120622 (creative 944862398478057), enlace a /collections/packs, utm_campaign=video-2026-11.

## 03/11/2026 · Vídeo en pausa

- Pausado «Vídeo · problema-solución» (120250354553120622). Lo pidió el dueño: «Prefiero mover el dinero al pack».
- Datos del día: 5,37 € de gasto, 24 clics, 15 visitas y 0 carritos. Pack A, con 0,71 €, consiguió 3 carritos.
- El presupuesto del conjunto no se ha tocado. El dinero se reparte entre los anuncios que siguen activos: Pack A, Pack B, Tienda y Catálogo.

## 06/11/2026 · Anuncio de recordatorio (carritos sin compra)

- El dueño aceptó las condiciones de públicos personalizados de Meta.
- Público «Carrito sin compra · 30 días» (120250440862930622): personas que añadieron al carrito o empezaron el pago en 30 días, sin las que ya compraron.
- Conjunto «Recordatorio · carrito sin compra 30 días» (120250440870340622) dentro de «primera campaña». Busca compras y solo se muestra a ese público. El presupuesto es de campaña (6 €/día) y no cambia.
- Anuncio «Recordatorio · Su pack sigue esperándole» (120250440883070622), creatividad 1782456869537318, con la imagen de Pack A. Enlace a /collections/packs con utm `recordatorio-carrito`.
- Publicado y en revisión (IN_PROCESS).

## 09/11/2026 · Anuncios nuevos desde cero: producto real con fondo de estudio

Por qué: casi no había carritos. Meta contaba unos 12 del 05/11 al 09/11, pero parece que los cuenta dos veces. Los clics eran baratos, así que el anuncio no convencía. Lo que más frena en este producto es el miedo a que sea una imitación (ver `estudio/competencia-2026-11.md`), y las imágenes de estudio hechas con IA no daban confianza.

1. Primera versión, R1/R2 (`tools/anuncio_real.py`): fotos reales del stock, con la terraza de fondo. El dueño no la quiso («tiene que verse profesional»). Anuncios 120250485469710622 y 120250485469920622 en **pausa**.
2. Versión buena, E1/E2 (`tools/anuncio_estudio.py`): las mismas fotos reales, recortadas (`fotos/recortes/`, con rembg) y puestas sobre un fondo de estudio azul noche con luz y sombra. Sigue siendo su producto de verdad; solo cambia el fondo.
   - E1 «Cargador + cable originales de Apple»: anuncio **120250486270030622**, creatividad 1124799337104554.
   - E2 «¿Original o imitación? Caja de Apple y sello CE»: anuncio **120250486271850622**, creatividad 2202763110597465.
   - Enlace a la ficha del pack USB-C con utm `estudio-2026-11`, E1/E2. Texto con la comparación con Apple y su fecha, «¿Por qué tan barato?» y «Compre aquí 👉 /collections/packs».
   - Solo se ha subido la imagen 4:5: Meta no deja poner aquí una imagen distinta por ubicación. Las de 9:16 quedan para subirlas a mano en stories si se quiere.
3. En pausa: Pack B, Tienda y «Nuevo anuncio de Ventas» (catálogo).
4. Siguen activos: E1, E2, Pack A (como referencia, era el mejor) y el anuncio de recordatorio.
5. Presupuesto: sin cambios (6 €/día de campaña). Los 3 borradores rotos siguen sin publicar.

## 09/11/2026 (tarde) · Versión estilo Apple (A1/A2)

- El dueño no veía profesionales las E1/E2 («quiero algo a nivel de estudio, al estilo Apple»).
- Higgsfield tiene 0 créditos, así que no se pudo generar con IA.
- `tools/anuncio_apple.py`: caras limpias de las cajas (`fotos/cine/`) montadas en 3D (lateral, tapa, sombra de contacto y reflejo) sobre fondo gris claro sin costuras. Titular sobrio, precio, comparación con Apple con fecha, ventajas y la web en grande abajo.
  - A1 «Carga original.»: anuncio **120250488394170622**, creatividad 951034024528049.
  - A2 «Original. Se nota.» (trasera con sello CE): anuncio **120250488394460622**, creatividad 4056920461270010.
  - utm `apple-2026-11`, A1/A2. Publicados; Meta los está revisando.
- En pausa: E1 (120250486270030622) y E2 (120250486271850622).
- Activos: A1, A2, Pack A y el recordatorio. Presupuesto sin cambios.

## 09/11/2026 · Informe semanal (últimos 7 días, datos de Meta)

| Anuncio | Gasto | Clics | Visitas | Carritos* | Pagos iniciados | Compras |
|---|---|---|---|---|---|---|
| Pack A v4 (activo) | 16,09 € | 77 | 48 | 26 | 5 | 0 |
| Tienda v4 (pausado hoy) | 13,04 € | 65 | 49 | 4 | 3 | 1 (13,04 €/compra) |
| Vídeo (pausado 03/11) | 6,51 € | 37 | 25 | 0 | 0 | 0 |
| Catálogo (pausado hoy) | 5,99 € | 15 | 7 | 2 | 2 | 0 |
| Pack B v4 (pausado hoy) | 1,63 € | 4 | 2 | 0 | 0 | 0 |
| A1/A2 estilo Apple | 0 € | publicados hoy, en revisión | | | | |
| Recordatorio | 0 € | el público es aún muy pequeño | | | | |

*Meta parece contar cada carrito dos veces.

- Total: 43,26 €. Pedidos reales en la tienda esta semana: 2 (#1002 y #1003). Unos 21,6 € de anuncios por venta, por encima de los 7 € a partir de los que se pierde dinero.
- Pack A: CTR 3,7 %, frecuencia 1,4. No está cansado. Muchos carritos, pero pocos pagos y ninguna compra.
- Cambios: ninguno más que los de hoy. A1/A2 tienen menos de 7 días; no se tocan. Presupuesto sin cambios.

## 09/11/2026 (noche) · Recordatorio ampliado y A1/A2 en pausa

- Con el «sí» del dueño: nuevo público «Visitantes web sin compra · 30 días» (120250488459900622). Lo forman todos los que visitaron la web, sin los que compraron.
- El conjunto de recordatorio (120250440870340622) usa ahora ese público más «Carrito sin compra · 30 días». Se llama «Recordatorio · visitantes y carritos sin compra 30 días». El presupuesto no cambia.
- A1 y A2 en pausa: al dueño le parecen hechas con IA y malas («tiene que verse reales»). Sigue activo Pack A.
- No se usan fotos de Apple ni de Pinterest: tienen derechos de autor y no son nuestras. Hacen falta fotos propias hechas en estudio.

## 09/11/2026 (noche) · Anuncios P1/P2 con fotos de estudio retocadas

- Al dueño le gustaba el de Pack A («se ve bien el cargador y el cable, pero faltaban retoques profesionales»). También pidió enganchar en el primer segundo y un botón claro a la web.
- `tools/anuncio_pro.py` usa las fotos de estudio de Pack A (`fotos/estudio/`). Les da contraste, nitidez, un tono cálido y viñeta. Añade un gancho grande arriba y un panel noche con precio, comparación con Apple y su fecha, 3 ventajas y un botón dorado «pillatumovil.com →».
  - P1 «¿Su iPhone vino sin cargador?» (cargador con el cable puesto): anuncio **120250488549080622**, creatividad 1837527177399951.
  - P2 «Original de Apple. A mitad de precio.» (cajas en el pedestal): anuncio **120250488549310622**, creatividad 1118701940780845. El texto empieza con «Compre aquí 👉 …/collections/packs». El botón de Meta es «Comprar» y lleva a la ficha del pack (utm `pro-2026-11`).
- Activos: P1, P2, Pack A y el recordatorio. Presupuesto sin cambios.

## 09/11/2026 (tarde) · Anuncios de tienda T1/T2 (fondo Higgsfield + producto real)

- Fondo de tienda vacío, sin marcas ni producto, creado con Higgsfield (gpt_image_2_6, 2 imágenes, 5,5 créditos): `fotos/fondos/tienda-ia-1.png` y `fotos/fondos/tienda-ia-2.png`.
- Encima va el producto real, recortado de la foto de estudio (`fotos/recortes/pro_cajas.png`), con sombra y tono cálido. Lo monta `tools/anuncio_boutique.py`.
  - T1 «¿Su iPhone vino sin cargador?»: anuncio **120250494972430622**, creatividad 29442277175460279.
  - T2 «Original de Apple. A mitad de precio.»: anuncio **120250494972800622**, creatividad 2231144557450238. utm `boutique-2026-11`.
- P1 y P2 en pausa: T1 y T2 llevan el mismo mensaje con mejor imagen.
- Pedido #1004 (09/11, Málaga, 18,99 €, pack Lightning): llegó por Google (búsqueda gratis) y luego entró directo. No viene de Meta.
