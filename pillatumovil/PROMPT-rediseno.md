# Rediseño completo de pillatumovil.com

Eres el director de diseño y el desarrollador de la tienda **Pillatumovil**
(https://pillatumovil.com). Tu trabajo: **reestructurar la tienda entera**
para que quien entre se quede impresionado por el nivel de detalle, el
cuidado y la profesionalidad, y compre. Usa todo lo que tienes: las skills
de diseño, Playwright para mirar lo que haces y la API de Shopify. Háblame
en español, con frases cortas y sin tecnicismos. En la tienda se trata al
cliente de **usted**.

## 1. Lee esto antes de tocar nada

0. Todo lo hecho hasta hoy está en la rama **`claude/modest-shannon-2mk475`**
   (no en la rama por defecto). Antes de nada, tráetela a tu rama de
   trabajo: `git fetch origin claude/modest-shannon-2mk475 && git merge
   origin/claude/modest-shannon-2mk475`. Comprueba que existen
   `pillatumovil/README.md`, `pillatumovil/marca/v3/` y
   `pillatumovil/tools/shopify/ptm.py`.
1. `pillatumovil/README.md` entero: cómo está hecha la tienda, las trampas
   de Dawn ya resueltas, las decisiones que no hay que deshacer, los precios
   y las reglas legales.
2. `pillatumovil/tools/shopify/ptm.py`: con ella hablas con la tienda
   (`temas`, `bajar`, `subir`, `medios`, `gql`). Las credenciales están en
   las variables de entorno `SHOPIFY_PTM_*`. **Nunca me pidas tokens ni
   contraseñas en el chat.**
3. Carga estas skills, en este orden, y aplícalas de verdad:
   - `marca-tiendas`: identidad y reglas de Pillatumovil.
   - `design-taste-frontend`: la dirección de arte, la idea, el texto, el
     inspector (`inspect.mjs`) y la crítica. Es la que manda en el diseño.
   - `impeccable`: auditoría y pulido (jerarquía, color, textos, accesibilidad).
   - `apple-design`: respuesta inmediata al tocar, muelles en lo que se
     arrastra, tipografía (tracking y leading por tamaño), movimiento reducido.
   - `mobile-native`: que en el móvil parezca una app (sin zoom en los
     campos, zona segura del notch, nada de 100vh roto, toques sin retraso).
   - `emil-design-eng`: los detalles invisibles que hacen que se note cuidado.
   - `find-animation-opportunities` y `animate`: el movimiento, al final.
   - `break-ui`: prueba cada pieza con los peores datos posibles.
   - `web-design-guidelines`: la revisión final.
   - `fotos-producto`, si hacen falta fotos nuevas de producto.

   Si dos skills chocan (por ejemplo, el cristal y el desenfoque de
   `apple-design` contra la regla «sin cristal» de `design-taste-frontend`),
   manda `design-taste-frontend` en la tienda. Apunta en el README cada
   decisión de ese tipo.

## 2. Seguridad: la tienda está abierta al público

- El tema **Dawn (207180497244) está publicado**: cada cambio en él lo ven
  los clientes al instante. **No lo toques.**
- Duplícalo con la mutación `themeDuplicate` (nombre «Dawn — Rediseño
  2026») y trabaja solo en la copia. La vista previa es
  `https://pillatumovil.com/?preview_theme_id=<id de la copia>`.
- **Publicar la copia (`themePublish`) solo cuando yo diga «publícalo»** en
  el chat. Antes, mándame el enlace de vista previa y las capturas.
- Antes de publicar, compara `config/settings_data.json` y los grupos de
  cabecera y pie de la copia con los del tema publicado. Si yo he cambiado
  algo desde el editor mientras tanto, no lo pises.
- No hagas pedidos de prueba con pago real ni cambies precios, productos,
  descuentos o envíos sin preguntarme.

## 3. La tienda hoy

- **Productos** (consulta los precios por API antes de escribirlos; estos
  son los del 01/11/2026):
  - Pack cargador 20 W + cable USB-C: 18,99 € (2 packs 33,99 €; 3 packs 45,99 €).
  - Pack cargador 20 W + cable Lightning: los mismos precios.
  - Cargador USB-C 20 W suelto: 12,99 €.
  - Cable USB-C a USB-C de 1 m: 10,99 €.
  - Cable USB-C a Lightning de 1 m: 10,99 €.

  Todo es original de Apple, nuevo y precintado, con 3 años de garantía.
  El envío es gratis y llega en 24-48 h. La devolución es gratis en
  14 días. Hay un código, PACK1799, que deja el pack en 17,99 €. En el
  futuro la tienda venderá también **móviles**: la estructura tiene que
  aguantarlo sin rehacerse.
- **Marca nueva (v3)**, en `marca/v3/`. El símbolo es el móvil-P: la P de
  Pillatumovil hecha con un móvil. El logotipo es «pilla**tu**movil» en
  **Unbounded** 700, con «tu» en oro. Colores:
  - noche `#0B0F1A`;
  - oro champán `#C9A86A` (texto oro `#D9BB7C`; oro oscuro `#7D5F28` sobre claro);
  - marfil `#F4F1EA`, piedra `#E8E5DF`, papel `#F3F1EC`, tinta `#141824`.

  Ahora el texto de la web va en Archivo. Une la web con el logo: titulares
  en Unbounded y texto en Archivo, o justifica otra cosa. Dos familias como
  máximo.
- **Fotos y vídeos reales**, que son lo que hay que lucir:
  - `fotos/`: fotos de producto sobre blanco, de 2048 px;
  - `fotos/reales/`: fotos reales del stock;
  - `estudio-ia/`: fotos y vídeos de estudio (portada, unboxing, mesilla,
    envío, cable, cargador, packs);
  - Shopify, en *Contenido → Archivos*: están ya subidos.

  Higgsfield no tiene créditos: no cuentes con generar nada nuevo con IA
  salvo que yo lo recargue. Nunca presentes una imagen de otro como si
  fuera nuestro producto.

## 4. Lo que no se puede romper

- El carrito con panel lateral y sus avisos (`ps-carrito-extra`, la lógica
  por SKU `CHRG-` / `CBL-` / `PACK-`), el botón de pago y el código de
  descuento.
- El feed de idealo: `templates/collection.idealo.liquid`, en
  `/collections/cargadores-y-cables?view=idealo`. Que siga dando las mismas
  columnas.
- `snippets/meta-tags.liquid` (`og:price:amount` con punto decimal, para
  Meta), el JSON-LD de producto, el píxel y el catálogo de Facebook e
  Instagram.
- El botón de WhatsApp, los enlaces a las páginas legales y a las
  políticas, el formulario de contacto y el del boletín.
- Las URLs actuales: los anuncios de Meta apuntan a
  `/collections/packs?utm_…`. Ninguna puede dar 404.
- Las reglas legales (Omnibus y consumo en España):
  - nada de reseñas, cifras de ventas ni clientes inventados;
  - nada de precios «antes» inventados ni de urgencia o escasez falsas;
  - cualquier comparación lleva «En Apple» y la fecha;
  - en el pie va «Pillatumovil no está afiliado a Apple»;
  - «Precio de lanzamiento hasta fin de existencias» solo mientras sea
    verdad.
- No subas al repositorio el NIF ni la dirección del dueño.

## 5. Qué hay que rehacer (todo, con la misma calidad)

Sigue el método de `design-taste-frontend` en este orden:

1. Fotos del «antes».
2. Inventario de lo que es solo nuestro.
3. El argumento de la página.
4. La dirección, con `draw.mjs --keep palette,type`.
5. La idea en una frase.
6. El texto completo antes de maquetar.

Luego se construye en secciones `ps-*` de Liquid dentro de Dawn. Los
textos, las fotos y los enlaces tienen que poder cambiarse desde el editor
de Shopify (ajustes de sección), sin tocar código.

Páginas, por orden de importancia:

1. **Portada.** La primera pantalla responde en letra grande qué es, cuánto
   cuesta y qué hago ahora, con la foto o el vídeo real grande. Tiene que
   llevar **una cosa viva**: el selector «¿Qué iPhone tiene?». El cliente
   toca su modelo (iPhone 8 al 16, con su año), ve su pack (USB-C o
   Lightning) con foto, precio y «Añadir al carrito», y se añade sin salir
   de la página. Tiene que funcionar con el pulgar, con teclado y sin
   JavaScript (un enlace normal). Después, solo las secciones que demuestren
   algo:
   - por qué es tan barato: margen pequeño;
   - qué llega en la caja;
   - el precio frente a Apple, con su fecha;
   - el envío en 24-48 h;
   - la garantía y la devolución;
   - las preguntas reales.
2. **Ficha de producto** (los 5 productos):
   - galería grande;
   - precio con «En Apple» y el ahorro;
   - selector de 1, 2 o 3 packs con el precio por unidad;
   - compatibilidad clara con cada iPhone;
   - lo que hay dentro de la caja;
   - envío, garantía y devolución sin ruido;
   - la barra fija de compra en el móvil;
   - un «quizá también necesite» con sentido.
3. **Colecciones** (`packs`, `cargadores-y-cables` y las demás) y
   **/collections**: tarjetas propias con filtro por tipo de cable o
   iPhone. Que ya admitan móviles en el futuro.
4. **Carrito**: panel lateral y página. Mensajes claros, sugerencias
   honestas, el código de descuento visible y el pago sin fricción.
5. **Cabecera y menú** (escritorio y móvil):
   - el logo nuevo;
   - el buscador útil;
   - la barra superior con el envío;
   - el menú móvil a pantalla completa, bien hecho.
6. **Pie**: el logo grande como cierre, el contacto, el WhatsApp, los
   pagos, los enlaces legales y la nota de Apple.
7. **El resto**:
   - la guía «¿Qué cable necesito?»;
   - contacto;
   - las páginas de información (envíos, garantía, devoluciones, quiénes somos);
   - buscar;
   - la 404;
   - la página de contraseña;
   - las cuentas de cliente, si se ven.

Y en todo:

- **Movimiento** según `apple-design`:
  - respuesta al pulsar en menos de 100 ms;
  - entradas escalonadas de 16-32 px por sección, que se disparan una vez;
  - nada que bloquee la lectura;
  - versión con `prefers-reduced-motion`;
  - solo `transform` y `opacity`.
- **Rendimiento**:
  - en móvil, LCP por debajo de 2,5 s y CLS por debajo de 0,1;
  - imágenes con `image_url` y `srcset`;
  - los vídeos con póster y cargados solo cuando hagan falta;
  - sin librerías pesadas.
- **Accesibilidad**:
  - contraste AA;
  - foco visible;
  - texto alternativo en todas las imágenes;
  - todo se puede usar con teclado;
  - campos de 16 px o más en el móvil para que no hagan zoom.

## 6. Cómo trabajar

- Ve por fases. Al terminar cada una, **mándame capturas** de escritorio
  (1440) y móvil (390) con `SendUserFile` y un resumen de 3-5 líneas. Las
  fases son:
  1. auditoría del «antes» y dirección elegida;
  2. sistema (letra, colores, botones, cabecera y pie);
  3. portada;
  4. ficha;
  5. colecciones y carrito;
  6. el resto;
  7. movimiento y revisión final.
- No me preguntes lo que puedas decidir tú. Decide, di qué decidiste en una
  línea y sigue. Pregunta solo si falta un dato que bloquea, como un precio
  o una promesa al cliente.
- Antes de enseñarme nada:
  - pasa `inspect.mjs` a 1440, 768 y 390 sobre la vista previa;
  - pasa `break-ui` en las tarjetas, el carrito y la ficha;
  - revisa las capturas tú mismo y corrige lo que se vea mal;
  - prueba que añadir al carrito, cambiar cantidades, el código de
    descuento, el menú móvil, el buscador y el WhatsApp siguen funcionando;
  - comprueba que el feed de idealo da lo mismo que antes.
- Guarda en git cada fase (en la rama de la sesión): la copia de los
  archivos del tema en `pillatumovil/theme/` y el README actualizado (qué
  se hizo, por qué y dónde se cambia cada cosa). No crees pull requests si
  no te lo pido.
- Al final, dame:
  1. el enlace de vista previa;
  2. las capturas de cada página en móvil y escritorio;
  3. el antes y el después;
  4. la lista de lo que tengo que hacer yo a mano en el admin.

  Luego espera a que diga «publícalo».

Empieza ahora por la fase 1.
