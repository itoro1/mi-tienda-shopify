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

## Resto de la tienda
## Resto de la tienda

- **Ficha de producto** (`templates/product.json`): título, precio, precio
  de Apple, cantidades, compra, enlace a WhatsApp, descripción y dos
  desplegables («¿Qué cable necesita su iPhone?» y «Garantía y
  devoluciones»). Debajo, la etiqueta de garantías y productos relacionados.
- **Colección** `cargadores-y-cables` con los 5 productos, orden manual.
- **Páginas**: Contacto (WhatsApp + formulario) y «Envío, garantía y
  devoluciones» (envío gratis, plazo 24-48 h laborables, devolución gratis).
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
- Opcional: añadir las fotos de estudio de `estudio-ia/` como fotos
  secundarias de cada producto (la principal sigue siendo la foto real
  sobre blanco). Cambia las fichas también en la tienda publicada.
- Higgsfield: prueba de 3 días con renovación automática a 49 €/mes si no
  se cancela. Quedan 9 créditos (25/10, 12:50).

Capturas en `disenos/`: `estudio-*.jpg` es la portada actual; `cine-*.png`
y `oro-*.jpg`, las anteriores.
