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

## 09/11/2026 (noche) · Anuncio «Escena E»: tienda con letrero LED y los dos packs

- El dueño pidió un letrero LED «Pillatumovil» de fondo, las cajas apoyadas en la mesa con el logo de Apple a la vista, los dos packs (USB‑C y Lightning) y algún iPhone al fondo.
- Higgsfield (gpt_image_2_6):
  1. Fondo con el letrero: `fotos/fondos/tienda-led-1.png` y `tienda-led-2.png`.
  2. Escena montada con ese fondo y las caras reales de las cajas (`fotos/cine/*.png`) como referencia: `fotos/fondos/escena-packs-1.png` (la elegida) y `-2.png`. Los textos de las cajas se revisaron a mano y son correctos.
- `tools/anuncio_escena.py` añade el precio, la comparación con Apple y su fecha, y un botón «pillatumovil.com →».
- Anuncio **120250495087240622**, creatividad 1317300623855058. Enlace a /collections/packs con utm `escena-2026-11`. ACTIVO.
- T1 y T2 en pausa (al dueño no le convencían).
- Activos: Escena E, Pack A y el recordatorio. Presupuesto sin cambios.
- Créditos de Higgsfield usados hoy: unos 20 de 600.

## 10/11/2026 · Anuncio «Escena Premium»: fondo de tienda de más categoría

- El dueño: «el fondo se sigue viendo irreal; tiene que verse de más categoría, con varios modelos de iPhone, incluido el 18 Pro Max».
- Higgsfield: edición de `escena-packs-1` en la que las cajas del mostrador no cambian. Se cambió el fondo por una tienda premium con pared de madera oscura, el letrero LED «pillatumovil» y una vitrina iluminada. Las referencias de iPhone son las fotos de producto de la propia tienda: 18 Pro Max burdeos y plata, 18 Pro negro y 17. Resultado en `fotos/fondos/escena-premium-1.png` y `-2.png`; se eligió la 2. Las cajas se revisaron de cerca y siguen correctas.
- Montaje con `tools/anuncio_escena.py fotos FUENTES anuncios/2026-11 escena-premium-2.png PREMIUM`.
- Anuncio **120250504942170622**, creatividad 1661274328980699. Enlace a /collections/packs con utm `escena-2026-11/PREMIUM`.
- Escena E (120250495087240622) en pausa.
- Activos: Escena Premium, Pack A y el recordatorio. Presupuesto sin cambios.
- Ubicación de Shopify: el dueño quiere quitar el «1B». El token no tiene permiso `write_locations`, así que se le dieron los pasos para hacerlo él.

## 10/11/2026 · Urgencia real: precio de lanzamiento hasta el jueves 12/11 a las 18:00

- Lo pidió el dueño: 48 horas a 18,99 € y después el pack sube a 19,99 €. Al cliente solo se le enseña el plazo, no el precio futuro. Es urgencia verdadera porque el precio sube de verdad.
- Web: `ps_lanzamiento_texto` = «Precio de lanzamiento: solo hasta el jueves 12/11 a las 18:00» (tema 207877767516, settings_data comparado con el publicado antes de subir).
- Anuncio **Urgencia U** 120250512815050622, creatividad 2588966644941883 (`tools/anuncio_urgencia.py`). Lleva una franja roja con el plazo y «Envío gratis · llega a su casa en 24-48 h». Termina solo el 12/11 a las 18:00 (ad_schedule_end_time). Enlace a /collections/packs con utm `urgencia-2026-11`.
- Escena Premium (120250504942170622) en pausa.
- Routine **trig_0173LcPnve9rC4M41Z8hn1hh**, el 12/11 a las 18:00 (hora de Madrid):
  - sube a 19,99 € las dos variantes «1 pack» (59637591474524 y 59637591605596);
  - apaga `ps_lanzamiento`;
  - pausa Pack A y el recordatorio (muestran 18,99 €);
  - avisa al dueño.
- Los packs de 2 y 3 unidades (33,99 € y 45,99 €) no cambian.
- 10/11: contador en directo en la web (`theme/snippets/ps-cuenta-atras.liquid`, cargado desde `layout/theme.liquid`). Es una barra roja arriba: «Precio de lanzamiento · termina en 2 d 00:02:57». Cuenta cada segundo hasta el 12/11 a las 17:00 UTC y se oculta sola. Solo aparece si `ps_lanzamiento` está activo. Probado en un iPhone 13 simulado. En el anuncio no cabe un contador real: Meta no lo permite en imagen ni en vídeo.
- 10/11: fotos nuevas de los packs en la tienda. Son de estudio, hechas con Higgsfield a partir de las caras reales de las cajas: `fotos/estudio-pro/pack-usbc.png` y `pack-lightning.png`. Ahora son la foto principal (MediaImage 73072086024540 y 73072086057308); las fotos antiguas siguen detrás, no se ha borrado nada.
- 10/11: vídeo pro en marcha. Fotograma vertical `fotos/fondos/escena-premium-9x16.png` (job 9941f75a). Vídeo Kling 3.0 Pro de 10 s (job d1625821, 25 créditos).
- 10/11: anuncio **Vídeo pro** 120250513055960622 (creatividad 1556820797503598, vídeo Meta 4554601834815513), publicado en el conjunto de prospección. Montaje con `tools/video_pro.py`: 12,6 s en 9:16. Guion:
  - 0-2,6 s: «¿Su iPhone vino sin cargador?»
  - 2,6-6 s: «Originales de Apple · precintados en su caja»
  - 6-10 s: 18,99 € y «En Apple, 38,00 € (precio del 01/11/2026)», con envío gratis en 24-48 h
  - cierre: tarjeta con el plazo del jueves y el botón pillatumovil.com
  - Enlace a /collections/packs con utm `video-pro-2026-11`. Termina solo el 12/11 a las 18:00 (ad_schedule_end_time).
  - La escena está hecha con IA: el dueño debe marcar en el Administrador de anuncios la casilla de contenido hecho con IA.
  - El clip sin montar es `clip-kling.mp4` (19 MB, job d1625821 de Higgsfield).
- 11/11: **vídeo con dependienta v2** (`anuncios/2026-11/video-persona/pillatumovil_video_dependienta_v2_9x16.mp4`, 31,5 s). Todavía sin publicar; espera el visto bueno del dueño.
  - Voz ElevenLabs «Elena» (`voz-final-elena.mp3`). Dice «en su caja sin abrir» en vez de «precintada», que se entendía «presentada». Urgencia real: «este precio acaba el jueves». No dice «se agotan» porque hay unas 200 unidades.
  - Vídeo Higgsfield Intone (job 5630c05b, 720p, 203 créditos) a partir de `fotograma-dependienta-real-v7.png`. La boca va sincronizada con la voz y hay 5 planos.
  - El plano de las manos (4,9-11,8 s) traía el texto de las cajas deformado. Se cambió por las fotos de estudio de los packs (`tools/insertar_broll.py`).
  - El plano del precio (11,8-14,9 s) se recortó a primer plano para sacar las cajas deformadas.
  - Subtítulos, precio y cierre añadidos con `tools/video_persona.py ... v2`.
- 11/11: **el precio de lanzamiento se amplía hasta el 30/11 a las 23:59**, porque lo pidió el dueño («hasta final de mes para tener más margen»).
  - La Routine trig_0173LcPnve9rC4M41Z8hn1hh pasa al 30/11 a las 23:59 (Madrid).
  - Web: `ps-cuenta-atras.liquid` cambia su data-fin a 2026-11-30T22:59:00Z, y `ps_lanzamiento_texto` dice «Precio de lanzamiento: solo hasta el 30/11». Se comparó con el tema publicado antes de subirlo.
  - Urgencia U y Vídeo pro llevan «hasta el jueves 12/11» en la imagen, así que se dejan acabar solos el 12/11 a las 18:00.
  - El vídeo con dependienta pasa a la versión 30/11 (`pillatumovil_video_dependienta_30nov_9x16.mp4`). La frase final se cambió por la voz nueva (`voz-frase-30nov.mp3`) sobre un plano de los dos packs (`fotos/estudio-pro/dos-packs-9x16.png`), así no se nota que la boca no coincide. Subtítulos v3.
  - Anuncio **Vídeo dependienta · tienda real · oferta hasta 30/11**: ID 120250535868370622, creatividad 1774846063806047, vídeo Meta 1826881621787791. Está en el conjunto de prospección 120250314921150622, enlaza a /collections/packs con utm `dependienta-2026-11` / V2 y lleva el botón «Comprar». Termina solo el 30/11 a las 23:59. Publicado; Meta lo estaba revisando (IN_PROCESS) al anotarlo.
  - La Routine del 30/11 ya incluye este anuncio en su lista de pausas.
- 11/11: **vídeo con dependienta 30/11 en 4K** (`pillatumovil_video_dependienta_30nov_4k.mp4`, 2160x3840, 32 s, 31 MB). Todavía sin publicar; espera el visto bueno del dueño.
  - El tramo de 4,9 a 11,8 s (antes fotos de los packs sobre fondo gris) es ahora un plano de la chica detrás del mostrador señalando las cajas (Intone, job 83934977, 70 créditos), acelerado ×1,38 para que encaje con la voz.
  - Intone cambió la voz de ese tramo por palabras sin sentido, así que se dejó la voz original de Elena por encima. En ese tramo la boca no va exacta, aunque en plano abierto casi no se nota.
  - El primer intento (job 6bb1dd7f, 70 créditos) salió mal por un error de recorte: la voz quedó muda a partir de 2,4 s.
  - El 4K se hizo con Topaz 2160p (job 055ddbaa, unos 27 créditos) y luego se recomprimió con crf 21. Quedan 51 créditos.
- 12/11: **origen de las últimas ventas** (Shopify, `customerJourneySummary`).
  - #1006 (Ibiza, 11/11 21:11, 18,99 €): vino del vídeo con dependienta (Facebook, utm `dependienta-2026-11` / V2). Compró 5 minutos después de entrar.
  - #1007 (Marbella, 12/11 08:24, 18,99 €): origen desconocido. Shopify no guardó ninguna visita previa.
  - Últimos 7 días en Meta: vídeo dependienta 0,69 € gastados, 9 clics, 2 carritos y 1 compra; Vídeo pro 6,42 €, 38 clics, 8 carritos y 1 compra.
- 12/11: **prueba A/B hasta el 30/11** porque lo pidió el dueño («pon en circulación el vídeo que ya estaba generando click y este último para ver cuál funciona mejor»).
  - **Vídeo pro · tienda premium · oferta hasta 30/11**: anuncio 120250547516480622, creatividad 3503495793171923, vídeo Meta 1747312976333535 (`video-pro/pillatumovil_video_pro_30nov_9x16.mp4`, hecho con `tools/video_pro.py` y el plazo nuevo). utm `video-pro-2026-11` / V2. Termina solo el 30/11 a las 23:59. Activo.
  - Urgencia U y el Vídeo pro antiguo acaban solos el 12/11 a las 18:00.
- 12/11: **vídeo con dependienta v4** (`video-persona/pillatumovil_video_dependienta_v4_9x16.mp4`, 1080x1920, 32 s). El dueño no quería cajas sobre fondo vacío: «tiene que estar todo el tiempo que se vea a la chica», enseñando la caja y dándole la vuelta, y cambiando de sitio.
  - Planos nuevos con Kling 3.0 Pro (5 s, sin sonido, 8,75 créditos cada uno), siempre a partir de una imagen con el texto de las cajas correcto. Kling mantiene las letras nítidas.
    - `broll/clipA.mp4` (job 217c32f0): junto al escaparate, enseña las dos cajas. Imagen inicial `broll/frameA.png` (job e814d40b).
    - `broll/clipB.mp4` (job d93567a7): primer plano, gira la caja del cargador y enseña la parte de atrás. Va de `broll/frameB_cerca.png` a `broll/frameB_trasera_cerca.png`.
    - `broll/clipC.mp4` (job 70bef678): entrega las dos cajas sobre el mostrador. Imagen inicial `broll/frameC.png` (job 77b0d162).
  - La parte de atrás de la caja es la foto real (`fotos/cine/caja-cargador-trasera.png`) pegada sobre la caja con `tools/caja_trasera_en_mano.py`. Así las letras son las de verdad y no las inventa la IA.
  - Montaje con `tools/montaje_dependienta_v4.sh` (24 fps, 1080x1920) y subtítulos v3 con `tools/video_persona.py`. El audio no cambia.
  - En los planos nuevos la chica no habla (sonríe y enseña) y su voz sigue de fondo.
  - Anuncio **Vídeo dependienta v4 · enseña la caja · oferta hasta 30/11**: ID 120250547806320622, creatividad 1137902302322366, vídeo Meta 1462843802614567. Conjunto de prospección 120250314921150622, utm `dependienta-2026-11` / V3, botón «Comprar», termina solo el 30/11 a las 23:59. Publicado; Meta lo estaba revisando (IN_PROCESS) al anotarlo.
  - El anuncio dependienta anterior (120250535868370622, con el plano de packs sobre fondo vacío) queda en pausa.
  - La Routine del 30/11 (trig_0173LcPnve9rC4M41Z8hn1hh) ya lleva los dos anuncios nuevos en su lista.
  - Estudio de anuncios parecidos: `estudio-anuncios.md`.
  - Quedan 24,2 créditos de Higgsfield.
  - Pendiente del dueño: marcar en Meta la casilla de contenido hecho con IA en los dos anuncios de vídeo.
- 12/11 (tarde): **4K real en todo el vídeo**. El dueño vio que los planos nuevos (Kling) salían nítidos pero los planos donde habla la chica (Intone, 720x1280) seguían blandos.
  - `tools/mejorar_4k.py`: superresolución x4 de toda la imagen (SPAN «clear_reality») y restauración de la cara (GFPGAN 1.4), en local con onnxruntime. No gasta créditos. Tarda unos 5 s por fotograma. Los modelos no están en el repositorio; la cabecera del script dice de dónde bajarlos.
  - `tools/montaje_dependienta_v4.sh CARPETA_4K` monta a 2160x3840 y `tools/video_persona.py ... v3 0 2` dibuja los textos directamente en 4K.
- 12/11 (tarde): Urgencia U (120250512815050622) y el Vídeo pro antiguo (120250513055960622) seguían en «activo» a las 19:50, pasada su hora de fin (18:00). Se pusieron en pausa a mano, porque su imagen dice «hasta el jueves 12/11».
- 12/11 (tarde): **código de descuento de un solo uso para un cable suelto**, porque lo pidió el dueño. Descuenta 10,99 € (el 100 % de un cable) en los dos cables sueltos, con límite de 1 uso. El código no se escribe aquí; está en Shopify → Descuentos, «Cable suelto gratis (un solo uso)».
- 12/11: **revisión diaria**. Gasto del día 4,50 €, 36 clics y 4 carritos. Del 05/11 al 12/11: 45,29 € y 5 pedidos pagados (#1003 a #1007), 9,06 € por venta (11,32 € sin contar el #1003). En los tres últimos días: 18,30 € y 3 ventas, 6,10 € por venta. Sin pagos abandonados en los últimos 3 días. Propuesta (sin aplicar): no subir el presupuesto todavía y dejar solo los dos vídeos hasta el 16/11.
