# mi-tienda-shopify

Repositorio de trabajo para la tienda **ITorostore** (`itorostore.com`).

- Plan: Basic · Moneda: EUR · Zona horaria: CEST (España)
- Tema base: Dawn, muy personalizado (secciones propias con prefijo `it-`)

## Flujo de trabajo

Los cambios en la web **nunca se aplican directamente sobre el tema publicado**.
El conector de Shopify bloquea por seguridad la escritura sobre el tema MAIN.

El ciclo es:

1. **Tema de edición** — una copia sin publicar del tema en vivo.
2. **Cambios** — se editan los ficheros del tema de edición.
3. **Vista previa** — se revisa el resultado antes de nada.
4. **Publicar** — lo hace el dueño de la tienda con un clic desde el admin.

Ese es el motivo de que la biblioteca de temas tenga nombres como
`PRO (edición) — fixes selectores`, `PRO — antiguo (no publicar)` o
`✅ PUBLICAR v2 — precios + cables + Google`: cada uno es una parada del ciclo.

## Qué se puede automatizar y qué no

Operaciones de escritura disponibles vía Admin API:

| Área | Escritura |
|---|---|
| Productos, variantes, precios | Sí |
| Colecciones | Sí |
| Inventario | Sí |
| Pedidos (etiquetas, notas, fulfillment) | Sí |
| Clientes | Sí |
| Descuentos | Sí |
| Páginas, blogs, metafields, metaobjects, SEO | Sí |
| Ficheros de un tema **sin publicar** | Sí |
| Ficheros del tema **publicado (MAIN)** | **No — bloqueado** |
| Publicar un tema | **No — bloqueado** |
| Borrar un tema | **No — bloqueado** |
| Reembolsos, tarjetas regalo, gestión de personal | **No — bloqueado** |

Los bloqueos son del conector, no de los permisos de la tienda. No se
desactivan concediendo más scopes.

## Sincronización con GitHub (opcional)

Shopify tiene integración nativa con GitHub, que sincroniza en **ambos
sentidos**: los commits en la rama actualizan el tema, y las ediciones hechas
desde el admin de Shopify se commitean de vuelta a la rama.

Para activarla: *Tienda online → Temas → Añadir tema → Conectar desde GitHub*,
y se elige organización, repositorio y rama.

Requisito: la rama debe contener ya un tema con la estructura de carpetas
estándar de Shopify (`assets/`, `config/`, `layout/`, `locales/`, `sections/`,
`snippets/`, `templates/`). Una rama vacía no aparece como conectable.

Aviso de la documentación de Shopify: una vez conectada una rama, **no se puede
reconectar tras desconectarla** — al reconectar se crea un tema nuevo.

## Carrusel de valoraciones de Wallapop

Las valoraciones de la portada son reales, leidas del perfil de Wallapop
(`fernandot-419803299`) el 10/09/2026: **18 valoraciones escritas, 98
valoraciones totales, media 4,9**. Antes la web mostraba 10 y decia "4,8".

Reparto de archivos (`theme/`):

| Archivo | Para que |
|---|---|
| `snippets/it-wallapop-data.liquid` | Los datos: textos, nombres, estrellas, fotos y fechas |
| `sections/it-wallapop-reviews.liquid` | El marcado del carrusel |
| `assets/it-reviews-carousel.css` | Estilos |
| `assets/it-reviews-carousel.js` | Flechas, puntos y teclado |

Dos decisiones que conviene no deshacer sin querer:

- **Los datos van en un snippet, no en `templates/index.json`.** Cada escritura
  de archivo tiene que caber en una sola llamada de la API, y con las 15
  valoraciones dentro la plantilla se pasaba de largo. Ademas asi la portada
  queda legible.
- **La seccion usa `{% include %}` y no `{% render %}`.** `render` aisla el
  ambito: las variables `wp_*` del snippet no llegarian a la seccion y el
  carrusel saldria vacio (paso, y asi se detecto).

Las fotos de perfil y de producto apuntan a `cdn.wallapop.com` en vez de estar
subidas a Shopify. Se comprobo que sirve las imagenes sin bloquear por
`Referer`. Si algun dia Wallapop rota esas rutas, las fotos desapareceran pero
las tarjetas se siguen viendo: el marcado tiene un hueco con la inicial del
comprador cuando no hay foto.

## Política de devoluciones (`tienda/politica-devoluciones.html`)

Vive en Shopify como página, no en el tema. La copia del repositorio es un
espejo de lo publicado.

Dos cosas que **no** se pueden cambiar aunque se pidan:

- **No se puede rechazar la devolución de un iPhone o un cargador porque el
  cliente haya roto el precinto.** Las excepciones al desistimiento estan
  tasadas en el articulo 103 del TRLGDCU y la de bienes precintados cubre
  higiene y salud (103.e) y software precintado (103.i), no electronica. La
  redaccion anterior ("los iPhones con precinto roto solo se aceptan si
  presentan defecto de fabrica") era nula, y ademas se contradecia con el
  parrafo de arriba, que prometia devolucion en todos los productos.
- Lo que si ampara la ley es **descontar la depreciacion** (articulo 108.2)
  cuando el producto se manipula mas alla de lo necesario para comprobarlo.
  Eso es lo que hace la version actual: cubre el mismo riesgo comercial y es
  defendible ante una reclamacion.

**La garantia de cargadores y cables es de 3 años, no de 1.** Son bienes
nuevos, asi que les aplica el plazo del articulo 120.1. El año solo vale para
segunda mano, y por pacto expreso. Anunciar 1 año en producto nuevo rebaja el
minimo legal.
