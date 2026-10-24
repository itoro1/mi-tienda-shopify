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

## Portada de cine (25/10/2026)

Arriba del todo, dos secciones oscuras que sustituyen a la portada clara:

- **`pt-cine` (PT · Portada de cine)**: plató oscuro con foco y grano de
  película. La caja real del cargador en 3D (CSS 3D, sin librerías): el
  cliente la gira arrastrando, con las flechas o con «Delante / Detrás», y
  ve la trasera impresa por Apple. Al entrar, la caja aparece desde la
  oscuridad y el titular entra línea a línea: es la única animación de
  entrada de la página.
- **`pt-historia` (PT · Historia de cine)**: tres capítulos que avanzan con
  el scroll en un plano fijo. *Original* (marco verde sobre la etiqueta de
  Apple y la referencia 602-05566-A), *Seguro* (marco sobre el marcado CE y
  la garantía) y *Rápido* (batería que se carga del 0 al 50 % y reloj de 0 a
  30 min al bajar). Sin JavaScript o con «reducir movimiento», los
  capítulos se leen uno debajo de otro.
- La lógica está en `assets/pt-cine.js`. Las caras de la caja están en
  `fotos/cine/` (recortes propios; medidas en `tools/medidas/cine-cargador.json`).
- Los marcos de *Original* y *Seguro* van en % de la foto
  `caja-cargador-trasera-cuerpo.jpg`: si se cambia la foto, hay que
  recolocarlos en `sections/pt-historia.liquid`.
- No hay vídeo porque no hay grabación propia y la skill `marca-tiendas`
  prohíbe usar material oficial de Apple. Si se graba un clip con el móvil,
  la skill `videos-reels` lo deja en formato para la portada.

## Resto de la portada

Secciones propias, todas con el prefijo `pt-` y con nombre
`PT · …` en el editor de temas:

| Sección (fichero) | Nombre en el editor | Qué hace |
|---|---|---|
| `pt-hero` | PT · Portada | Titular, batería que se carga al entrar y producto estrella con su precio |
| `pt-ventajas` | PT · Garantías | Etiqueta de caja: dato y valor (producto, garantía, devolución, pago) |
| `pt-buscador` | PT · ¿Qué conector? | El cliente toca su puerto (USB-C o Lightning) y aparece su producto |
| `pt-productos` | PT · Lista de precios | Una fila por producto con columnas «En Apple» y «Aquí» |
| `pt-pack` | PT · Pack | El pack como una suma: piezas sueltas, total, precio del pack |
| `pt-faq` | PT · Preguntas | Preguntas en acordeón + datos estructurados FAQPage para Google |
| `pt-cta` | PT · Cierre | Franja final con un botón que sube al buscador |

| `pt-whatsapp` | PT · WhatsApp | Botón flotante en todas las páginas (va en el grupo del pie) |

Piezas comunes: `assets/pt-base.css` (paleta, tipografía, botones),
`snippets/pt-precio.liquid` (precio + comparativa con Apple) y
`snippets/pt-pvp.liquid` (comparativa bajo el precio de la ficha).

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
- **Logo e icono** en `marca/`, generados con `tools/logo.py` (Archivo 800,
  fuente OFL; el script la espera en `fuentes/Archivovar.ttf`).
- **Fotos de producto** en `fotos/` (2048 × 2048, fondo blanco, sin la
  bolsa de Apple). Salen de las fotos originales con `tools/cajas.py`
  (recorta la cara delantera de cada caja) y `tools/componer.py`. Las
  medidas finales de cada caja están en `tools/medidas/`; en los packs, el
  borde derecho de la primera caja se corrigió a mano (421 y 431 px)
  porque el hueco en sombra entre cajas engañaba al afinado automático.

## Identidad visual (rediseño del 24/10/2026)

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
