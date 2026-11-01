# Rediseño 2026 · Fase 1: auditoría y dirección (01/11/2026)

## 1. El «antes» (tema Dawn publicado, 207180497244)

Capturas en `antes/` (inspector a 1440, 768 y 390 px sobre pillatumovil.com).

| Página | Inspector | Lo que se ve |
|---|---|---|
| Portada | 10 FAIL, 9 WARN | Buena foto, pero titulares de 3 líneas, barra de oro con degradado, velos degradados, 14 filetes finos, 16 tamaños de letra, dos `h1`, márgenes distintos (72/96 px), casi nada se mueve. El selector de iPhone solo distingue «15 o posterior / 8 a 14»: el cliente tiene que saber qué conector lleva. |
| Ficha | 15 FAIL, 9 WARN | Antetítulo en mayúsculas espaciadas, título largo de 3 líneas («Pack Cargador Completo Apple — USB-C + Cable USB-C»), botones de pack pequeños, galería que repite la misma caja, «Complete su carga» como fila de 4 tarjetas iguales con sombra. |
| Packs (colección) | 7 FAIL, 9 WARN | Dos tarjetas en una página casi vacía, títulos de producto de 4 líneas en móvil, «Desde 18,99 €» sin decir qué iPhone es cada uno. |
| Todas | — | Texto de cuerpo gris (5,8:1), etiquetas en mayúsculas («CONTACTO», «OFERTAS») en el pie, el WhatsApp tapa contenido en móvil, la cabecera translúcida con desenfoque. |

Lo que funciona y se queda: las fotos de estudio, el vídeo de las cajas, el
cálculo honesto «En Apple» y el ahorro, el carrito lateral con sus avisos, la
lógica por SKU, el feed de idealo, las metaetiquetas y el JSON-LD.

## 2. Inventario: lo que solo tiene Pillatumovil

1. El nombre: «pilla**tu**movil», con «tu» en oro. El móvil-P del logo.
2. La caja blanca de Apple con su pestaña de cartón blanco opaco y su
   rotulación: «USB-C / 20W Power Adapter», «60W Charge Cable (1 m)»,
   «USB-C to Lightning Cable (1 m)».
3. El corte entre el iPhone 14 y el 15: Lightning o USB-C. Es la única
   pregunta que tiene que contestar el cliente.
4. Las cifras: 18,99 € el pack, 38 € en Apple (19 € + 19 €, 29/10/2026),
   20 W, 1 m, 24-48 h, 0 € de envío, 14 días, 3 años.
5. El porqué del precio, en palabras del dueño: «Ganamos menos por cada pack.
   A propósito.»
6. El stock real (200 por variante) y las fotos reales de las cajas.
7. El paquete de Correos recién llegado (`ps-envio.jpg`).
8. Los vídeos de estudio: las dos cajas en la piedra oscura y las manos
   abriendo la caja.
9. El WhatsApp de la tienda y el trato de usted.
10. El futuro: móviles. La marca dice «Móviles y accesorios».

## 3. El argumento de la portada

| Sección | Afirmación | Prueba |
|---|---|---|
| Primera pantalla | Es el cargador y el cable originales de Apple, a 18,99 € el pack. | La caja real, enorme; el precio en grande; «En Apple, 38 €». |
| ¿Qué iPhone tiene? (lo vivo) | Le decimos cuál es el suyo sin que tenga que saber de conectores. | Toca su iPhone y ve su pack con foto, precio y «Añadir al carrito». |
| Por qué tan barato | No es un truco: ganamos menos. | La cuenta, línea a línea, en un tique: lo que cuesta en Apple, lo que cuesta aquí. |
| Qué llega en la caja | Lo mismo que vende Apple, precintado. | Fotos reales de cerca: el cargador, el cable, las cajas. Vídeo de las manos. |
| El envío | En su casa en 24-48 h, sin pagar envío. | La foto del paquete; tres pasos que crecen: pide hoy, sale, llega. |
| Compatible con | Funciona con todos estos iPhone. | La banda de nombres de modelo corriendo. |
| Garantía y devolución | Si algo falla, se lo cambiamos; si no le convence, lo devuelve gratis. | 3 años, 14 días, sin pagar nada. |
| Preguntas | Las dudas reales, contestadas. | Seis preguntas con FAQPage. |
| Cierre | Somos de verdad y le atendemos. | WhatsApp, el logo grande sobre la última foto, las políticas. |

Lo que se quita: «Elija lo que necesita» (categorías repetidas), las dos
fotos editoriales sin argumento (mesilla y cable enrollado pasan a la prueba
de la caja), el bloque de precios de 5 tarjetas iguales.

## 4. La dirección

`draw.mjs --sector ecommerce --keep palette,type --direction hero-object`
(seed 2052516145; hoja completa en `.taste-skill/direction.json`).

- **«El objeto, grande»**: la caja, más grande de lo razonable, cortada por
  el borde. Elegida frente a «catálogo de especímenes» (pocos productos para
  un mosaico) y «escenario partido» (la caja fija en media pantalla no
  carga el selector).
- Secciones dadas y cómo se usan:
  - intro → columna estrecha: el porqué del precio;
  - showcase → retrato sobre su color: qué llega en la caja;
  - pricing → **el tique**: la cuenta de Apple contra la nuestra;
  - how-it-works → tres teselas que crecen: pedido, envío, en su casa;
  - proof → **nombres que se salen por los bordes**: los modelos de
    iPhone compatibles (no hay reseñas y no se inventan);
  - faq → titular ancho y preguntas sangradas;
  - footer → el logo a todo el ancho sobre la última foto.
- Movimiento: fundido lento entre las fotos de la caja; entradas de 16-32 px
  por sección.
- Sin redibujar nada.

### Letra y color

- **Unbounded (titulares, 600) + Archivo (texto, 400/500).** Une la web
  con el logo, que ya es Unbounded. Dos familias, el máximo. Unbounded es
  ancha: los titulares se escriben cortos (unos 26 caracteres en móvil).
- Fondo papel `#F3F1EC`, tinta `#141824`, noche `#0B0F1A` para la portada,
  el tique y el pie. Oro champán `#C9A86A` solo en el botón principal y en
  el «tu» del logo; texto oro `#D9BB7C` sobre noche; oro oscuro `#7D5F28`
  sobre claro.
- **Choque entre skills**: el inspector avisa de que papel y piedra son
  «crema». Se quedan: son los colores de la marca, sacados del papel de los
  bodegones. Y la barra superior pierde el degradado: oro plano.

## 5. La idea

> En esta tienda, **el corte entre el iPhone 14 y el 15 (Lightning o USB-C)**
> se convierte en **la caja enorme de la portada, que cambia cuando el
> cliente toca su iPhone**.

Prueba del competidor: cualquier tienda vende cargadores de Apple, pero
ninguna empieza preguntando su iPhone y enseñándole su caja.

**Lo vivo**: «¿Qué iPhone tiene?». Fichas de iPhone 8 (2017) a iPhone 17
(2025) y «iPhone Air / 17 Pro». Al tocar una, la caja grande pasa a la de su
pack, con precio y «Añadir al carrito», y se añade sin salir de la página.
Sin JavaScript, cada ficha es un enlace a la ficha de su pack.

## 6. El texto

### Portada

**Barra superior** (oro plano): «Lo recibe en casa en 24-48 h» · «Envío y
devolución gratis» · «Original de Apple, 3 años de garantía».

**Primera pantalla**
- `h1`: **Cargador y cable originales de Apple**
- Frase: «Nuevos y precintados, en su caja. Para cualquier iPhone.»
- Precio: **18,99 €** el pack · «En Apple, 38 € (29/10/2026)»
- Botón: «Elegir mi pack» (baja al selector) · enlace «Ver todo».

**¿Qué iPhone tiene?**
- `h2`: **¿Qué iPhone tiene?**
- Frase: «Tóquelo y le enseñamos su pack.»
- Fichas: iPhone 8 · 2017 | iPhone X · 2017 | iPhone XR / XS · 2018 |
  iPhone 11 · 2019 | iPhone 12 · 2020 | iPhone 13 · 2021 | iPhone 14 · 2022 |
  iPhone 15 · 2023 | iPhone 16 · 2024 | iPhone 17 · 2025
  (más «iPhone SE» 2020/2022 → Lightning).
- Resultado: «Para su iPhone 13: el pack con cable Lightning.» Foto, 18,99 €,
  «En Apple, 38 €», «Añadir al carrito», «Ver el pack».

**Por qué es tan barato**
- `h2`: **Ganamos menos. A propósito.**
- Texto: «Vendemos el mismo cargador y el mismo cable que Apple, en su caja
  precintada. No hay truco en el producto: el truco está en el margen.
  Compramos por cantidad, nos quedamos una parte pequeña de cada pack y lo
  enviamos sin cobrarle el envío. Si un día el precio cambia, lo verá aquí
  antes que en ningún sitio.»
- El tique: «Adaptador de corriente USB-C de 20 W — 19,00 €» · «Cable de
  carga — 19,00 €» · «En Apple, por separado — 38,00 €» · «Envío — 0,00 €» ·
  **«Aquí, el pack — 18,99 €»** · «Usted ahorra 19,01 € (50 %)». Pie del
  tique: «Precios de apple.com/es a 29/10/2026.»

**Qué llega en la caja**
- `h2`: **Lo que llega a su casa**
- Capítulos: «El adaptador de 20 W» (enchufe europeo, carga rápida: hasta el
  50 % en unos 30 minutos, según Apple); «El cable de 1 m» (USB-C trenzado o
  USB-C a Lightning); «Precintado, como sale de Apple» (vídeo de las manos).

**El envío**
- `h2`: **En su casa en 24-48 h**
- Pasos: «Pide hoy» (pago con tarjeta, Apple Pay, Google Pay o PayPal) ·
  «Sale con Correos» (envío gratis, sin mínimo) · «Lo abre usted» (en su
  caja, precintado).

**Compatible**
- Banda: «iPhone 8 · iPhone X · iPhone 11 · iPhone 12 · iPhone 13 · iPhone 14
  · iPhone 15 · iPhone 16 · iPhone 17».
- Frase: «El adaptador de 20 W sirve para todos. El cable depende del
  conector: Lightning hasta el iPhone 14, USB-C desde el 15.»

**Garantía**
- `h2`: **Tres años de garantía**
- «Si falla, se lo cambiamos.» · «14 días para devolverlo, gratis.» · «Le
  atendemos por WhatsApp, de persona a persona.»

**Preguntas**
- `h2`: **Lo que nos preguntan**
- ¿Es original de Apple? · ¿Por qué cuesta menos que en Apple? · ¿Qué
  cable necesita mi iPhone? · ¿Cuándo llega? · ¿Cómo lo devuelvo? · ¿Qué
  garantía tiene? (respuestas: las de `ps-faq` de hoy, revisadas).

**Pie**
- Logo grande sobre la última foto. «¿Dudas? Escríbanos por WhatsApp.»
- Tienda · Ayuda · Contacto · Pagos · Políticas.
- «Apple, iPhone y Lightning son marcas de Apple Inc. Pillatumovil no está
  afiliado a Apple.»

### Ficha
- Título corto en la página (el nombre largo se queda en Shopify para
  Google y Meta): «Pack USB-C: cargador 20 W y cable».
- Precio, «En Apple, 38 € (29/10/2026)», «Ahorra 19,01 € (50 %)».
- Packs: «1 pack · 18,99 €» · «2 packs · 17,00 € cada uno» · «3 packs ·
  15,33 € cada uno».
- «¿Es para mi iPhone?»: la lista de modelos con un sí claro.
- «En la caja»: lo que trae, con foto real.
- Envío, garantía y devolución: una línea cada uno.
- «Quizá también necesite»: el cable de repuesto del mismo conector o el
  cargador suelto.

### Colecciones, carrito y el resto
- Colecciones: «Packs», «Cables», «Cargadores y cables»; filtro «Conector:
  USB-C / Lightning» y «Tipo: Pack / Cargador / Cable / (Móvil)».
- Carrito: «Su carrito», el aviso del envío, la sugerencia honesta, «¿Tiene
  un código de descuento?» visible y «Pagar pedido».
- 404: «Esta página no existe» · «Pero su cargador sí.» + selector.

## 7. Datos que quedan por confirmar (no bloquean)

- PVP de Apple: comprobados el 29/10/2026 (19 € cada uno). Se vuelven a
  mirar antes de publicar y se cambia la fecha.
- «Precio de lanzamiento hasta fin de existencias»: se deja como ajuste
  apagado por defecto. Se enciende solo si el dueño lo confirma.
