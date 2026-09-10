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
