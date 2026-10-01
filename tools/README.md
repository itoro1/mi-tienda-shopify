# Herramientas

## wallapop-scrape.py — leer las valoraciones reales de Wallapop

Wallapop no publica las valoraciones en el HTML: las carga por JavaScript
desde `api.wallapop.com/bff/sales/reviews/user-profile`, y esa API exige
cabeceras firmadas que solo genera su propia web. Por eso el script abre el
perfil en un Chromium real, pulsa la pestaña de valoraciones e intercepta la
respuesta.

Dos detalles del entorno remoto que hacen falta:

- Chromium no atraviesa el proxy de salida de la sesion (da
  `ERR_CONNECTION_RESET`), pero `curl` si. El script intercepta cada peticion
  del navegador con `context.route()` y la resuelve por `curl`.
- El banner de cookies tapa la pestaña, asi que se bloquean los dominios de
  consentimiento y analitica y se pulsa `#tab-reviews` con `force=True`.

Uso:

    python3 tools/wallapop-scrape.py     # deja wp_api.json y rendered.html

El perfil es `https://www.wallapop.com/user/fernandot-419803299` (ojo: el slug
es `fernandot-...`, no `itoro-...`) y el id interno de usuario que usa la API
es `nz0m0prp0vjo`.

La instantanea del 10/09/2026 esta en `wallapop-reviews-2026-09-10.json`:
18 valoraciones escritas, 98 valoraciones totales, media 4,9.

Para volcarlas al tema hay que regenerar `theme/snippets/it-wallapop-data.liquid`
y subirlo con `themeFilesUpsert` a un tema NO publicado.

## google-scrape.py — leer la ficha de Google Business

Mismo truco que el de Wallapop (Chromium real, cada peticion resuelta por
`curl`), pero con un detalle que costo encontrar: **Google manda cabeceras que
Playwright no sabe reenviar** (`alt-svc`, `report-to`, `cross-origin-*`,
`set-cookie` repetido). Si `route.fulfill()` lanza una excepcion, Playwright
deja pasar la peticion a la red de verdad y Chromium choca con el certificado
del proxy: `ERR_CERT_AUTHORITY_INVALID`. Parecia un problema de TLS y era un
problema de cabeceras. Filtrandolas, la ficha carga.

### Hasta donde llega

Funciona: la nota media y el numero de resenas, por el endpoint
`maps/preview/place`, que tambien se puede pedir con `curl` a secas:

    https://www.google.com/maps/preview/place?authuser=0&hl=es&gl=es&pb=!1m1!1s<feature_id>

El 30/09/2026 devolvio **4,9 sobre 8 resenas**.

No funciona: los textos de cada resena. Los sirve `maps/rpc/listugcposts`,
que da 403 sin el token de sesion del navegador, y cuando el navegador los
pide de verdad **Google redirige a `/sorry/index`**, su CAPTCHA antibot,
porque la IP de salida de estas sesiones esta marcada. Ahi se acaba el camino,
y saltarse un CAPTCHA no es una opcion.

### Identificadores de la ficha

| | |
|---|---|
| CID | `1115849531936487308` |
| feature id | `0xd0d73558ac38dff:0xf7c4b3cbddc378c` |
| place_id | `ChIJ_43DilVzDQ0RjDfcvTxLfA8` |

El feature id sale de seguir las redirecciones del enlace corto de resenas
(`https://g.page/r/CYw33L08S3wPEBM/review`), que acaba en una URL que lo lleva.

### Para las resenas completas

La via buena es la **API de Google Business Profile**, porque la ficha es del
dueno: devuelve todas las resenas con autor, texto y foto, y es gratis. Pide
OAuth y que Google apruebe el acceso por formulario, lo que tarda dias.
