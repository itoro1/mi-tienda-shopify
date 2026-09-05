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
