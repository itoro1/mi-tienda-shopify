# Pillatumovil

Segunda tienda (`j2zukw-xp.myshopify.com`), separada de ITorostore.

- Moneda: EUR. Acceso por API con la app del Dev Dashboard (variables
  `SHOPIFY_PTM_*`, token por *client credentials*, caduca a las 24 h).
- Tema de trabajo: **Dawn 16.1.0, sin publicar** (`207180497244`). Canyon es
  el publicado y no se toca. Se publica con un clic desde el admin, igual que
  en ITorostore.
- Esta carpeta es el espejo de lo que hay en Dawn: si se cambia un fichero
  aquí, se sube al tema; si se cambia en el editor, se trae aquí.

## Portada

Siete secciones propias, todas con el prefijo `pt-` y con nombre
`PT · …` en el editor de temas:

| Sección | Qué hace |
|---|---|
| `pt-hero` | Titular grande, dos botones, sellos y foto del producto estrella con su precio |
| `pt-ventajas` | Franja de iconos (bloques: se añaden, quitan y reordenan) |
| `pt-buscador` | «¿Qué iPhone tienes?»: una tarjeta por conector con el producto que le va |
| `pt-productos` | Rejilla de productos elegidos a mano (o de una colección) |
| `pt-pack` | Banner del pack: En Apple / Por separado / Pack, calculados |
| `pt-faq` | Preguntas en acordeón + datos estructurados FAQPage para Google |
| `pt-cta` | Cierre con el color de marca de fondo |

Piezas comunes: `assets/pt-base.css` (botones, tipografía, colores),
`snippets/pt-precio.liquid` (precio + comparativa con Apple) y
`snippets/pt-icono.liquid` (iconos).

## Cómo se cambia (sin tocar código)

Todo se hace en *Tienda online → Temas → Dawn → Personalizar*:

- **Color de marca**: *Configuración del tema → Pillatumovil*. Un solo color
  que usan todas las secciones `PT ·` (botones, titulares en color, iconos).
- **Textos, botones y enlaces**: en cada sección.
- **Productos**: cada sección tiene su selector de productos. Foto, precio y
  PVP de Apple salen del producto: **no hay precios escritos a mano**, así que
  cambiar un precio en el admin lo cambia en toda la portada.
- **Fondo claro u oscuro**: casilla en la portada, el pack y las ventajas.

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
- **Las fotos de producto llevan fondo blanco**, por eso en fondo claro se
  pintan con `mix-blend-mode: multiply` (el blanco se funde con el gris) y
  en fondo oscuro van dentro de una tarjeta blanca.
- **Los productos se eligen en el editor**, no por handle en el código como
  en las secciones `it-` de ITorostore: así se cambian sin programar.

## Pendiente

- Los 5 productos están **en borrador**: mientras no se activen, la portada
  muestra huecos en su lugar. Ya están añadidos al canal Tienda online, así
  que basta con pasarlos a *Activo*.
- El botón de la sección de preguntas («Contactar») no sale hasta que se le
  ponga un enlace (página de contacto o WhatsApp).
- Sin sección de opiniones a propósito: la tienda es nueva y no tiene
  reseñas propias. No se copian las de ITorostore.

Capturas de la portada en `disenos/` (renderizado local con los datos
reales de los productos; la vista previa real necesita la contraseña de la
tienda).
