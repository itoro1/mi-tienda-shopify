# Pillatumovil

Segunda tienda (`j2zukw-xp.myshopify.com`), separada de ITorostore.

- Moneda: EUR. Acceso por API con la app del Dev Dashboard (variables
  `SHOPIFY_PTM_*`, token por *client credentials*, caduca a las 24 h).
- Tema: **Dawn 16.1.0** (`207180497244`), **sin publicar** (la tienda sigue
  con Canyon). Se publicó por error a las 15:53 del 24/10 y se volvió a
  Canyon a las 16:22; todo lo posterior está solo en Dawn. Vista previa:
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

## Portada (25/10/2026, versión «estudio»)

Rehecha de cero el 25/10 por la tarde: el cliente veía la anterior «pobre» y
las cajas 3D en CSS «hechas por ordenador». Ahora la llevan **fotos y vídeos
de estudio fotorrealistas** (Higgsfield, ver más abajo) y la interfaz se
aparta, al estilo de Nomad. Secciones `ps-*` y hoja `assets/ps-base.css`.

| Orden | Sección | Qué hace |
|---|---|---|
| 1 | `ps-hero` · PS · Portada con vídeo | Vídeo de estudio a todo el ancho (las dos cajas sobre piedra oscura, acercamiento lento de cámara, en bucle de ida y vuelta). Titular, precio del pack y PVP de Apple sacados del producto, botón «Comprar el pack» (baja a `#pack`) y tres garantías. En móvil, vídeo en cuadrado arriba y texto debajo |
| 2 | `ps-pack` · PS · El pack | Foto de estudio del pack y compra directa. Selector «¿Qué iPhone tiene?» (15 o posterior / 8 a 14) que cambia foto, precio, ahorro y lo que incluye, sin JavaScript. «Añadir al carrito» añade 1 pack y lleva al carrito |
| 3 | `ps-envio` · PS · Envío gratis | Titular grande «Envío gratis. Devolución, también.», tres cifras y la foto del paquete recién llegado |
| 4 | `ps-categorias` · PS · Categorías | Cargador, Cables y Packs con foto de estudio y precio «desde» |
| 5 | `ps-editorial` · PS · Foto y texto | La mesilla de noche: carga rápida de 20 W |
| 6 | `ps-video` · PS · Vídeo | Manos abriendo la caja y sacando el cargador; solo se reproduce mientras se ve |
| 7 | `ps-editorial` | «Tal como lo prepara Apple»: el cable enrollado con sus fajas, sobre noche |
| 8 | `ps-precios` · PS · Precios | Los 5 productos en tarjetas con precio aquí y en Apple; añadir al carrito o elegir cantidad. Carrusel en móvil |
| 9 | `ps-faq` · PS · Preguntas | Acordeón + FAQPage de schema.org |
| 10 | `ps-cierre` · PS · Cierre | «¿No sabe qué cable necesita?» con WhatsApp |

Las secciones `pt-*` de las versiones anteriores siguen en el tema sin usar
en la portada (`pt-ventajas` sí está en la ficha y la colección). La portada
«noche y champán» queda guardada en el historial de git
(`templates/index.json` del commit anterior a esta versión).

### Identidad

- **Fondos sacados de las fotos**: noche `#0B0F1A` (el fondo del estudio
  oscuro: portada, vídeo, cierre) y piedra `#E8E5DF` / papel `#F3F1EC` (el
  papel gris cálido de los bodegones, para que las fotos se fundan con la
  página). Tinta `#141824`, marfil `#F4F1EA`.
- **Oro champán `#C9A86A`** solo como luz: botón principal, cifras y filetes.
  Sin degradados en los textos. Oro oscuro `#7D5F28` para iconos y la
  etiqueta de ahorro sobre fondo claro.
- **Tipografía**: una sola familia, **Archivo** (titulares en 600, apretados;
  texto en 400). Es una grotesca como la rotulación de las cajas. La Bodoni
  Moda queda solo en el **logo** (`marca/`, `tools/logo_firma.py`).
- **Movimiento**: solo los dos vídeos. Nada de animaciones al hacer scroll.
- **Barra superior** (`ps-barra`, sustituye a la de anuncios de Dawn): oro,
  tres mensajes con icono en fila; en móvil van de uno en uno con un fundido.
  El primero, en negrita: **«Lo recibe en casa en 24-48 h»** (plazo que da
  el dueño, 25/10).
- **Cabecera**: logo en el centro, menú a la izquierda (menú
  `principal-estudio`, solo de Dawn: Cargador, Cables, Packs, ¿Qué cable
  necesito? → `/#pack`), subrayado en oro al pasar y en la página activa,
  burbuja del carrito en oro. **En la portada es transparente sobre el
  vídeo** y al bajar se vuelve noche translúcida con desenfoque (en todas
  las páginas). Los estilos van en `ps-barra.liquid` y se apoyan en lo que
  ya pone Dawn: `--header-height` y la clase `.scrolled-past-header`.
- En ordenador el vídeo de portada ocupa la parte derecha (desde el 38 %)
  con el borde izquierdo fundido, y el titular va en tres líneas: así el
  texto no pisa las cajas cuando la cámara se acerca. Pie en noche.

### Fotos y vídeos con IA (Higgsfield)

En `estudio-ia/` (y en Contenido > Archivos con el mismo nombre):

| Fichero | Dónde |
|---|---|
| `ps-estudio-portada.mp4` / `.jpg` | Portada (vídeo 10 s en bucle de ida y vuelta, y foto de espera). También en el cierre |
| `ps-pack-usb-c.jpg`, `ps-pack-lightning.jpg` | El pack (mismo encuadre: al cambiar de iPhone solo cambia la caja del cable). La Lightning, también en Categorías > Packs |
| `ps-envio.jpg` | Envío gratis |
| `ps-cargador.jpg`, `ps-cable.jpg` | Categorías |
| `ps-mesilla.jpg` (en Archivos, `ps-mesilla-v2.jpg`) | Carga rápida |
| `ps-unboxing.mp4` / `.jpg` (en Archivos, `ps-unboxing-v2.*`) | Banda de vídeo (bucle con fundido de 0,75 s) |
| `ps-cable-en-su-caja.jpg` | «Tal como lo prepara Apple» |
| `ps-cable-lightning.jpg` | Ficha del cable Lightning y del pack Lightning (cable liso, no trenzado, como el real) |
| `ps-cargador-con-cable.jpg` | Ficha del pack USB-C (cargador en horizontal, cable USB-C trenzado en el puerto del centro) |

**Galerías de las fichas** (26/10): la foto real sobre blanco sigue la
primera y detrás van las de estudio, enlazadas desde Archivos sin copiarlas
(`fileUpdate` con `referencesToAdd`), cada una con su texto alternativo:

| Producto | Fotos de estudio, en orden |
|---|---|
| Cargador 20 W | `ps-cargador`, `ps-mesilla-v2`, `ps-unboxing-v2` |
| Cable USB-C | `ps-cable`, `ps-cable-en-su-caja` |
| Cable Lightning | `ps-cable-lightning` |
| Pack USB-C | `ps-pack-usb-c`, `ps-cargador-con-cable`, `ps-estudio-portada`, `ps-unboxing-v2` |
| Pack Lightning | `ps-pack-lightning`, `ps-cable-lightning`, `ps-mesilla-v2`, `ps-unboxing-v2` |

Las fotos son del producto, no del tema: también salen en la tienda
publicada. Al cargador suelto no se le puso la foto con cable, para no dar
a entender que lo incluye.

- Hechas con Nano Banana Pro (fotos, 2 créditos) y Kling 3.0 Pro (vídeo,
  8,75 créditos cada 5 s), siempre con las **fotos reales** como referencia:
  las de `fotos/` y las del cliente en `fotos/reales/`.
- Los vídeos se suben como **archivo genérico** (sin recodificar, 1080p):
  si se suben como vídeo, Shopify los deja en 720p.
- **Reglas de fidelidad** (todo lo que no las cumpla se descarta):
  - la **pestaña de colgar es de cartón blanco opaco**, nunca de plástico
    transparente: el cliente avisa de que las transparentes son de cajas
    falsas;
  - **enchufe europeo** de dos clavijas redondas (la IA tiende a dibujar el
    americano);
  - textos de la caja como en la real («USB-C» / «20W Power Adapter»,
    «USB-C» / «60W Charge Cable (1 m)», «USB-C to Lightning Cable (1 m)»);
  - nada de **datos grabados inventados**: se descartó un primer plano de
    las clavijas porque la IA se inventó voltajes y añadió una tercera clavija;
  - **el cargador como es**: laterales lisos sin nada escrito; la cara del
    USB-C (la opuesta a las clavijas) es lisa, con el puerto en el centro y
    sin letras (`fotos/reales/cargador-cara-usb-c.jpg`). Enchufado en la
    pared va en **horizontal** y el cable sale del puerto del centro, de
    frente. Se rehicieron el vídeo de las manos (salían letras en la cara
    de abajo al girarlo: ahora no gira) y la foto de la mesilla;
  - **luz física**: se descartó un vídeo en el que la caja «brillaba» con
    bordes amarillos, como si emitiera luz. Delata que es artificial.
- El vídeo anterior, hecho con las fotos de la caja montadas en 3D
  (`video/`, `tools/video/estudio.html` y `rodar.js`), queda para redes; en
  la web se sustituyó porque se notaba hecho por ordenador.

### Trampas de Dawn que ya están resueltas (no deshacer)

- **Dawn oculta los `div` vacíos** (`base.css`: `div:empty{display:none}`).
  Las caras de las cajas 3D de las secciones `pt-` son `div` vacíos que se
  pintan con CSS; se fuerzan con `.pt-c3 > .pt-c3__f{display:block}`.
- **El orden de carga de las hojas**: `pt-base.css` y `ps-base.css` se
  cargan después de los `{% stylesheet %}` de las secciones; una regla de
  sección que quiera pisar una de la hoja base necesita más especificidad
  (ej. `.pt-of .pt-of__h1`, `.ps-env .ps-env__titulo`).
- **Dawn pinta los `h3` con el color del esquema** (marfil sobre noche): en
  una tarjeta clara hay que darle color al título (`.ps-pre .ps-pre__nombre`).
- **El euro en Bodoni Moda se lee como una «C»**: en las secciones `pt-` va
  en `<span class="pt-eur">`. Con Archivo en los titulares ya no hace falta.
- **«24-48» se partía por el guion** en móvil: en los textos va con
  separadores invisibles (U+2060) a los lados del guion y espacio duro antes
  de «h» o «horas»; «14 días», con espacio duro.
- **Un vídeo en bucle no deja que la página quede «inactiva»**: en las
  pruebas con Playwright hay que esperar a `load`, no a `networkidle`.
- **`PUB_SUB_EVENTS` no cuelga de `window`**: en `constants.js` es un
  `const` global. Se comprueba con `typeof PUB_SUB_EVENTS`, y como
  `pubsub.js` va con `defer`, la suscripción se hace al cargar el DOM
  (`ps-ficha-barra`).
- **El precio de la ficha se refresca solo**: Dawn, al cambiar de variante,
  sustituye el elemento con id `price-<sección>` por el recién pintado en el
  servidor. `ps-ficha-precio` lleva ese id, así que no necesita JavaScript.
- **Los botones del selector de cantidad heredan el fondo** de `.quantity`
  y lo pintan cuadrado: el fondo va en `.quantity::before`, que es redondo.
- **`.cart__ctas` es flex**: lo que se meta dentro se pone al lado del
  botón de pago y lo aplasta. Las garantías del carrito van después.
- **Un ajuste `url` no admite cualquier valor por defecto** (por ejemplo,
  `/pages/contact` da error al subir): se deja vacío y se pone el valor en
  Liquid con `default`.
- **Los filtros no van dentro de `for`** (`for h in 'a,b' | split: ','` da
  error de sintaxis): primero `assign`, luego `for`.
- **El título y la descripción de la portada** no salen de los metacampos
  `global.title_tag` / `global.description_tag` (probado: Shopify ya no los
  lee). Se ponen en *Tienda online → Preferencias*.
- **Ancho de página**: el ajuste de Dawn solo admite múltiplos de 100.
  `ps-barra` fija `--page-width` a 1360 px y el mismo margen que `.ps-wrap`,
  en línea y antes del contenido para que no salte. Menú, portada, ficha y
  colección empiezan en la misma línea (96 px a 1440 de ancho).

## Ficha, colección y carrito (26/10/2026, versión «estudio»)

- **Ficha de producto** (`templates/product.json`, `main-product` de Dawn
  con el esquema 3 = piedra). De arriba abajo:
  - galería: la foto real primero, en grande sobre papel, y las de estudio
    debajo de dos en dos, todas cuadradas (en móvil, carrusel);
  - antetítulo «Original de Apple · Nuevo, en su caja», título;
  - **precio** (`snippets/ps-ficha-precio.liquid`): el de la variante, lo
    que sale cada pack, «En Apple» × número de packs, «Ahorra X € (n %)»
    y, en los packs de 2 y 3, lo que se ahorra frente a packs de 1;
  - packs de 1, 2 o 3 como tarjetas, cantidad y «Añadir al carrito» (sin
    los botones de pago rápido);
  - **garantías** (`ps-ficha-sellos`): 24-48 h, devolución gratis en 14
    días, original con 3 años; y la ayuda por WhatsApp;
  - descripción (subtítulos pequeños y listas con check) y los dos
    desplegables;
  - **barra fija de compra** (`ps-ficha-barra`): sale al pasar el botón de
    compra, sigue a la variante elegida y pulsa el botón de la ficha.
    Mientras se ve, el botón de WhatsApp sube.
  - Debajo: vídeo «Nuevo y precintado», «Complete su carga» (las mismas
    tarjetas de la portada, sin el producto que se está viendo) y las
    preguntas.
- **Tarjeta de producto** (`snippets/ps-tarjeta.liquid`), la misma en la
  portada, las colecciones y la ficha: foto real y, al pasar el ratón, la
  de estudio; precio, «En Apple» y ahorro; «Añadir al carrito» si el
  producto tiene una sola variante, «Elegir cantidad» si es un pack.
- **Colección** (`sections/ps-coleccion.liquid`, plantilla
  `templates/collection.json`): título, descripción, número de productos,
  tarjetas (2 columnas en móvil), garantías y el cierre de la portada.
  `cargadores-y-cables` tiene los 5 productos, en orden manual.
- **Carrito lateral** (`snippets/cart-drawer.liquid`, copia del de Dawn,
  esquema 3): todo lo que se añade desde la portada, las colecciones, la
  ficha o el propio carrito lo abre sin salir de la página
  (`assets/ps-carrito.js` para los formularios `data-ps-anadir`). Lleva:
  - el aviso «Envío gratis. Lo recibe en casa en 24-48 h»;
  - **la sugerencia de lo que falta** (`snippets/ps-carrito-extra.liquid`):
    con un cargador sin cable, los dos cables («¿Y el cable? Elija el de su
    iPhone»); con un cable sin cargador, el cargador; con un pack, nada. Se
    decide por la referencia (SKU `CHRG-`, `CBL-`, `PACK-`);
  - las garantías bajo «Pagar pedido» y los precios como «12,99 €».
  - Si se actualiza Dawn, hay que volver a copiar `cart-drawer.liquid` y
    repetir los tres `render 'ps-carrito-extra'` (lo explica su cabecera).
- **Textos de Dawn** (`locales/es.json`): «Añadir al carrito», «Su
  carrito», «Su carrito está vacío», «IVA incluido. Envío gratis.» y el
  resto del carrito tratando de usted.

## El resto de páginas (26/10/2026, segunda ronda)

Ya no queda ninguna página con el aspecto de Dawn de serie:

| Página | Plantilla | Sección |
|---|---|---|
| Pie (todas) | `sections/footer-group.json` | `ps-pie`: frase, WhatsApp, menús «Tienda» y «Ayuda», contacto, boletín (formulario de cliente con etiqueta `newsletter`), pagos activos y políticas |
| Menú móvil | `snippets/header-drawer.liquid` (copia de Dawn) | `ps-menu-extra`: enlaces grandes, los dos packs con foto y precio, garantías y WhatsApp |
| ¿Qué cable necesito? | `page.guia.json` | `ps-guia`: los dos conectores dibujados (borde inferior del iPhone), modelos, compra directa del pack o el cable y el cargador |
| Contacto | `page.contact.json` | `ps-contacto`: WhatsApp destacado, formulario (nombre, correo, teléfono, n.º de pedido, mensaje) y atajos |
| Envío, garantía y devoluciones | `page.info.json` | `ps-pagina` con cuatro cifras (24-48 h, 0 €, 14 días, 3 años) |
| Otras páginas de texto | `page.json` | `ps-pagina`: índice automático con los `<h2>` del texto y WhatsApp al lado |
| Buscar | `search.json` | `ps-buscar`: tarjetas `ps-tarjeta` y atajos si no hay resultados |
| No encontrada | `404.json` | `ps-404` + `ps-precios` |
| /collections | `list-collections.json` | `ps-categorias` con el título como `h1` («Colecciones») |
| /cart | `cart.json` | el de Dawn en claro + «Complete su carga» sin lo que ya lleva el carrito |

Cambios en datos de la tienda (no en el tema), hechos por la API:

- Página nueva **«¿Qué cable necesito?»** (`/pages/que-cable-necesito`,
  plantilla `guia`). En Canyon sale con la plantilla normal y su texto.
- La página de envío y garantía usa la plantilla `info`. Comprobado que en
  Canyon, que no la tiene, se sigue viendo con la normal.
- Menús nuevos: `pie-tienda`, `pie-ayuda` y `atajos-contacto`. El enlace
  «¿Qué cable necesito?» del menú `principal-estudio` va ahora a la guía.
  Los menús que usa Canyon (`main-menu`, `footer`) no se han tocado.

**Vídeo de portada en móvil**: `estudio-ia/ps-estudio-portada-movil.mp4`,
un corte cuadrado de 900 × 900 sobre las cajas (520 KB, frente a 2,5 MB del
de 1080p). `ps-hero` elige el vídeo por el ancho de pantalla (ajuste «Vídeo
para móvil»); sin JavaScript se queda la foto de espera.

## Resto de la tienda
- **Páginas**: Contacto (WhatsApp + formulario) y «Envío, garantía y
  devoluciones» (envío gratis, plazo 24-48 h laborables, devolución gratis).
- **Menús**: principal (Inicio, Cargadores y cables, ¿Qué cargador
  necesito?, Contacto) y pie (Información).
- **`assets/pt-dawn.css`**: lleva el estilo «estudio» a lo que sigue
  siendo de Dawn (ficha, carrito, páginas de texto). Lo carga `pt-whatsapp`.
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

- **Vídeos**: en *PS · Portada con vídeo* y *PS · Vídeo* se pega el enlace
  .mp4 del archivo subido en Contenido > Archivos.
- **Fotos**: cada sección tiene su selector de imagen.
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

## Precios (historial para la regla de los 30 días)

El precio «antes» de una rebaja tiene que ser el más bajo cobrado en los 30
días anteriores (Ómnibus). Por eso se apunta aquí cada cambio:

| Desde | Cargador 20 W | Cables (USB-C y Lightning) | Pack 1 / 2 / 3 |
|---|---|---|---|
| 24/10/2026 (alta) | 14,99 € | 14,99 € | 25,99 / 46,99 / 62,99 € |
| 26/10/2026 | 12,99 € | 10,99 € | 18,99 / 33,99 / 45,99 € |

Los del 26/10 son los que tenía ITorostore hasta el 15/10 (sacados de sus
pedidos); el pack de 3 no llegó a venderse entonces y lo fijó el dueño en
45,99 €. Sin precio comparado («antes») en ningún producto. El PVP de Apple
va aparte, siempre con su etiqueta «En Apple».

## idealo (comparador de precios)

- **Feed**: `theme/templates/collection.idealo.liquid`. Se genera solo con los
  datos de Shopify (precio, stock, fotos, EAN del campo «Código de barras»):
  `https://<dominio>/collections/cargadores-y-cables?view=idealo`. CSV según
  https://idealo.github.io/csv-importer/en/csv/ (coma, punto decimal, listas
  con «;»). Una fila por variante con stock; los packs van con su número en
  `packagingUnit`.
- Hoy está **solo en Dawn** (sin publicar): idealo no puede leerlo hasta que
  se publique Dawn, o hasta copiar la plantilla a Canyon.
- Ejemplo de la salida en `idealo/feed-ejemplo-2026-10-25.csv`.
- **Pendiente para darlo de alta**:
  - cuenta de comerciante en idealo (la abre el dueño: datos fiscales y
    forma de pago; idealo cobra por clic);
  - transportista real para la columna `deliveryCosts_<transportista>` (ahora
    `correos` de marcador, sin confirmar);
  - comprobar que los EAN de las fichas (copiados de ITorostore) coinciden
    con el código de barras de las cajas; los packs no tienen EAN y saldrán
    con menos visibilidad;
  - opcional: referencia de Apple (`hans`) en un metacampo `custom.mpn`;
  - **páginas legales** que faltan en la tienda: aviso legal (titular, NIF,
    domicilio, correo) y condiciones de venta. Solo existe la política de
    privacidad.

## Pendiente

- Publicar Dawn cuando se dé el visto bueno a la vista previa.
- Formato de moneda de la tienda: sale «€25,99»; en España se escribe
  «25,99 €». Se cambia en *Configuración → General → Moneda de la tienda →
  Cambiar formato* (`{{amount_with_comma_separator}} €`). La app no tiene
  permiso para tocarlo.
- Comprobar en *Configuración → Envío* que hay una tarifa para España: el
  descuento pone el envío a 0 €, pero necesita una tarifa a la que
  aplicarse.
- Plazo de entrega **24-48 h** (lo indica el dueño, 25/10): en la barra
  superior, la portada, las preguntas y la página «Envío, garantía y
  devoluciones», donde se precisa «24 a 48 horas laborables (de lunes a
  viernes, sin contar festivos)». Falta confirmar si vale para Baleares,
  Canarias, Ceuta y Melilla y si hay hora de corte para el envío del día.
- Sin sección de opiniones a propósito: la tienda es nueva y no tiene
  reseñas propias. No se copian las de ITorostore.
- **Título y descripción de la portada para Google** (*Tienda online →
  Preferencias*), propuesta: «Cargador y cable originales de Apple para
  iPhone | Pillatumovil» y «Cargador USB-C de 20 W y cables USB-C y
  Lightning originales de Apple, nuevos y precintados. Envío gratis, en su
  casa en 24-48 h, y 3 años de garantía.» Hoy sale solo «Pillatumovil».
- **Aviso de cookies** de Shopify: trata de tú («tu experiencia», «las
  aceptes»). Se cambia en *Configuración → Privacidad del cliente →
  Banner de cookies*.
- Higgsfield: prueba de 3 días con renovación automática a 49 €/mes si no
  se cancela. Quedan 5 créditos (26/10, 13:45).
- Secciones `pt-` antiguas que ya no usa ninguna plantilla de Dawn (hero,
  oferta, ventajas, cta…): se pueden borrar cuando se publique Dawn.

Capturas en `disenos/`: `estudio-*.jpg` es la portada actual; `cine-*.png`
y `oro-*.jpg`, las anteriores.
