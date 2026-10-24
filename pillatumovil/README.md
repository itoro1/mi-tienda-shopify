# Pillatumovil

Segunda tienda (`j2zukw-xp.myshopify.com`), separada de ITorostore.

- Moneda: EUR. Acceso por API con la app del Dev Dashboard (variables
  `SHOPIFY_PTM_*`, token por *client credentials*, caduca a las 24 h).
- Tema: **Dawn 16.1.0** (`207180497244`), **sin publicar**. Se publicó a
  las 15:53 del 24/10 y se volvió a Canyon a las 16:22; la portada de cine
  se hizo después, solo en Dawn. Vista previa:
  `https://j2zukw-xp.myshopify.com/?preview_theme_id=207180497244`.
- La tienda está **abierta al público** (sin contraseña) y los 5 productos
  están **activos**, así que ya se ven y se venden con el tema publicado.
- **Stock**: 200 unidades por variante (24/10/2026), sin vender sin stock.
  Rutina diaria «Aviso de stock bajo Pillatumovil» (8:31, hora de Madrid):
  avisa por notificación y correo si alguna variante baja de 50.
- **Envío gratis** en todos los pedidos: descuento automático «Envío
  gratis» (la app no tiene permiso de envíos, así que no toca las tarifas).
  **Devolución gratis** también, según la página de garantía.
- WhatsApp de la tienda: **+34 641 04 75 39** (distinto del de ITorostore).
- Tono: **de usted** con el cliente. Las ayudas del editor van de tú.
- Esta carpeta es el espejo de lo que hay en Dawn: si se cambia un fichero
  aquí, se sube al tema; si se cambia en el editor, se trae aquí.

## Portada (25/10/2026, versión «noche y champán»)

| Orden | Sección | Qué hace |
|---|---|---|
| 1 | `pt-oferta` · PT · Oferta del pack | Lo primero: el pack cargador + cable. Dos cajas 3D con volumen sobre una peana con filo de oro; se inclinan con el ratón o el dedo. Selector «Mi iPhone es del 15 al 18 / 8 al 14» que cambia caja del cable, precio, ahorro y botón |
| 2 | `pt-envio` · PT · Envío gratis | Banner grande «Envío gratis.» y tres cifras (0 € envío, 0 € devolución, 14 días) |
| 3 | `pt-categorias` · PT · Categorías | Cargador, Cables y Packs con foto y precio «desde» (colecciones `cables` y `packs`) |
| 4 | `pt-video` · PT · Vídeo | Banda a todo el ancho con el vídeo de estudio en bucle |
| 5 | `pt-historia` · PT · Historia de cine | Original / Seguro / Rápido, ligado al scroll |
| 6 | `pt-productos` · PT · Lista de precios | Precio aquí y en Apple |
| 7 | `pt-faq`, `pt-cta` | Preguntas y cierre |

Siguen en el tema, sin usar en la portada: `pt-cine` (caja que gira 360°),
`pt-hero`, `pt-buscador`, `pt-pack` y `pt-ventajas` (esta última sí está en
la ficha de producto y en la colección).

### Identidad

- **Paleta**: noche `#0B0F1A`, medianoche `#131A2B`, oro champán `#C9A86A`,
  oro claro `#E7D3A6`, marfil `#F4EFE6`, y marfil cálido `#EDE8DF` como
  fondo de las fotos de producto. No es el negro y oro de ITorostore: el
  fondo es azul noche.
- **Tipografía**: Bodoni Moda (titulares, precios grandes, logo) y Archivo
  (texto y botones).
- **Logo**: el nombre en Bodoni Moda con los puntos de las dos «i» en oro
  (`marca/`, `tools/logo_firma.py`). Icono: una «P» con el punto en oro.
- **Barra superior** en oro con «Envío gratis…», cabecera y pie en noche.

### Trampas de Dawn que ya están resueltas (no deshacer)

- **Dawn oculta los `div` vacíos** (`base.css`: `div:empty{display:none}`).
  Las caras de las cajas 3D (laterales, tapa, trasera) son `div` vacíos que
  se pintan con CSS: por eso la caja parecía «de papel». Se fuerzan con
  `.pt-c3 > .pt-c3__f{display:block}` (y `.pt-box > .pt-box__cara`).
- **El orden de carga de las hojas**: `pt-base.css` se carga después de los
  `{% stylesheet %}` de las secciones; una regla de sección que quiera pisar
  una de `pt-base` necesita más especificidad (ej. `.pt-of .pt-of__h1`).
- **El euro en Bodoni Moda se lee como una «C»**: todos los «€» de las
  secciones van en `<span class="pt-eur">` con la fuente de texto, y el
  precio de la ficha de producto va en Archivo.
- **La pestaña de colgar de las cajas** se recorta del frontal y se pinta en
  el plano trasero (`.pt-c3__pestana`), que es de donde sale en la caja real.

### Vídeo de estudio

- `video/pillatumovil-estudio-web.mp4` (1600 × 900, 8 s en bucle) está
  subido a Contenido > Archivos; la sección `pt-video` usa su versión 720p
  del CDN de Shopify. `video/pillatumovil-estudio-reel.mp4` (1080 × 1920,
  24 s) es para Reels, TikTok y Stories.
- Se rueda con `tools/video/estudio.html` (la caja del adaptador girando
  360° sobre la peana, con foco y barrido de luz) y `tools/video/rodar.js`,
  que la fotografía fotograma a fotograma con Playwright; luego `ffmpeg`.
  `estudio.html` espera `caja-cargador-frente.png` y `-trasera.png` (en
  `fotos/cine/`) en su misma carpeta.
- No es vídeo generado con IA ni material de Apple: son las fotos propias
  de la caja montadas en 3D. Para clips con IA (Higgsfield u otro), el
  vídeo se sube a Archivos y se pega su enlace en *PT · Vídeo*.

## Resto de la tienda

- **Ficha de producto** (`templates/product.json`): título, precio, precio
  de Apple, cantidades, compra, enlace a WhatsApp, descripción y dos
  desplegables («¿Qué cable necesita su iPhone?» y «Garantía y
  devoluciones»). Debajo, la etiqueta de garantías y productos relacionados.
- **Colección** `cargadores-y-cables` con los 5 productos, orden manual.
- **Páginas**: Contacto (WhatsApp + formulario) y Garantía y devoluciones.
- **Menús**: principal (Inicio, Cargadores y cables, ¿Qué cargador
  necesito?, Contacto) y pie (Información).
- **`assets/pt-dawn.css`**: lleva el estilo de la portada a las páginas de
  Dawn (títulos, precios, fotos sobre gris de caja). Lo carga `pt-whatsapp`.
- **Logo e icono** en `marca/`, generados con `tools/logo_firma.py`
  (Bodoni Moda, fuente OFL; el script la espera en `fuentes/BodoniModa.ttf`).
- **Fotos de producto** en `fotos/` (2048 × 2048, fondo blanco, sin la
  bolsa de Apple). Salen de las fotos originales con `tools/cajas.py`
  (recorta la cara delantera de cada caja) y `tools/componer.py`. Las
  medidas finales de cada caja están en `tools/medidas/`; en los packs, el
  borde derecho de la primera caja se corrigió a mano (421 y 431 px)
  porque el hueco en sombra entre cajas engañaba al afinado automático.

## Identidad anterior (24/10/2026, sustituida el 25/10)

Hecha con la skill `frontend-design`, a partir de los objetos que se venden
y no de una plantilla:

- **Paleta**: blanco del plástico de Apple `#FFFFFF`, gris de la caja
  `#EEEFEC`, tinta pizarra `#1B2230`, verde de carga `#0E7C3A` (botones) y
  verde batería de iOS `#34C759` (solo la batería).
- **Tipografía**: Archivo, una sola familia. Titulares en 800 y apretados,
  como la rotulación de una caja.
- **Un único elemento llamativo**: la batería de la portada, que se carga
  una vez al entrar. Es la única animación que no provoca el cliente.
- **Evitado a propósito**: antetítulos en mayúsculas, una palabra del
  titular en otro color, flechas «→» en los botones, rejillas de tarjetas
  iguales y animaciones en cada sección. Son las marcas de una web hecha
  con plantilla.

## Cómo se cambia (sin tocar código)

Todo se hace en *Tienda online → Temas → Dawn → Personalizar*:

- **Color de marca**: *Configuración del tema → Pillatumovil*. Usa un tono
  oscuro: el texto de los botones es blanco.
- **Batería**: en *PT · Portada* se elige hasta qué porcentaje se carga y
  el texto de debajo, o se oculta.
- **Textos, botones y enlaces**: en cada sección.
- **Productos**: cada sección tiene su selector. Foto, precio y PVP de
  Apple salen del producto: **no hay precios escritos a mano**.
- **Garantías, opciones del buscador y preguntas** son bloques: se añaden,
  quitan y reordenan.

## Decisiones que conviene no deshacer

- **El PVP de Apple siempre va con la etiqueta «En Apple»** delante del
  tachado. Un tachado suelto junto a nuestro precio se leería como «antes
  costaba esto aquí», que es un descuento inventado (Omnibus). Es la misma
  regla que en ITorostore (`theme/assets/it-pvp.css`).
- **El ahorro se calcula, no se escribe**, y el porcentaje se redondea
  **hacia abajo**: 12,01 € sobre 38 € es un 31,6 % y se anuncia −31 %.
- **En el pack, cada fila solo sale si es más cara que el pack.** Si un día
  el precio suelto baja, la fila «Por separado» desaparece sola en vez de
  anunciar un ahorro falso.
- **Garantía de 3 años**, no 1: producto nuevo (ver el README principal).
- **Las fotos de producto llevan fondo blanco**, por eso sobre el gris se
  pintan con `mix-blend-mode: multiply`: el blanco se funde con el gris.
- **Los avisos para el editor no los ve el cliente.** Con
  `request.design_mode`, una sección sin producto enseña «Falta elegir…»
  solo dentro del editor; en la web se oculta entera. Así un producto en
  borrador o agotado no deja huecos ni textos internos a la vista.
- **Las variantes de cantidad no llevan porcentaje en el nombre.** Antes
  ponía «3 unidades - 20% dto» y el descuento real era del 19 %.
- **El buscador funciona sin JavaScript** (radios + `:has()`). En un
  navegador sin `:has()` se ven todas las respuestas a la vez, que sigue
  siendo correcto.
- **Los productos se eligen en el editor**, no por handle en el código como
  en las secciones `it-` de ITorostore: así se cambian sin programar.

## Pendiente

- Publicar Dawn cuando se dé el visto bueno a la vista previa.
- Formato de moneda de la tienda: sale «€25,99»; en España se escribe
  «25,99 €». Se cambia en *Configuración → General → Moneda de la tienda →
  Cambiar formato* (`{{amount_with_comma_separator}} €`). La app no tiene
  permiso para tocarlo.
- Comprobar en *Configuración → Envío* que hay una tarifa para España: el
  descuento pone el envío a 0 €, pero necesita una tarifa a la que
  aplicarse. Plazos de entrega: no se anuncian hasta conocerlos.
- Sin sección de opiniones a propósito: la tienda es nueva y no tiene
  reseñas propias. No se copian las de ITorostore.

Capturas en `disenos/`: `cine-*.png` son las escenas de la portada de cine.
