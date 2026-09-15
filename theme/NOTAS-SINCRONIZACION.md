# Sincronización de temas — 15/09/2026

La API de temas de Shopify **no deja copiar ficheros entre temas** cuando uno de
los dos está publicado (`themeFilesCopy` se rechaza en ambos sentidos), y cada
escritura admite ~7 KB de contenido. Por eso el tema gemelo se puso al día
fichero a fichero, leyendo del publicado y escribiendo en el gemelo.

**Tema gemelo:** `204363039045` — "✅ PUBLICAR v2 — precios + cables + Google"

## Ficheros llevados al gemelo

| Fichero | Qué aporta |
|---|---|
| `snippets/itoro-cart-progress.liquid` | Cross-sell del carrito por conector (nuevo) |
| `assets/itoro-cart-progress.css` | Su CSS, sacado fuera porque no cabía en una escritura |
| `assets/it-trust-badge.js` / `.css` | Sello de opiniones, versión discreta (píldora) |
| `assets/it-reviews-carousel.js` / `.css` | Carrusel compartido |
| `snippets/it-wallapop-data.liquid` | 15 valoraciones reales de Wallapop |
| `snippets/it-google-data.liquid` | 5 reseñas reales de Google |
| `sections/it-wallapop-reviews.liquid` | Carrusel Wallapop |
| `sections/it-google-reviews.liquid` | Carrusel Google |
| `snippets/it-schema-org.liquid` | Carga el sello + datos estructurados |
| `assets/it-hero-premium.css` / `-dark.css` | Estilos del hero |
| `sections/it-hero-premium.liquid` | Hero del iPhone 18 |
| `templates/index.json` | Portada con hero 18 y las dos secciones de valoraciones |
| `sections/it-categorias.liquid` | Rango de modelos calculado del catálogo |

## Comprobado en la vista previa del gemelo

- Hero: iPhone 18 Pro Max, foto burdeos, sin descuento inventado.
- Valoraciones: 20 tarjetas (15 Wallapop + 5 Google).
- Sello flotante: se carga en todas las páginas.
- Categorías: "del 13 al **18**", calculado, no escrito a mano.
- Carrito con iPhone 17 Pro Max → Pack **USB-C** + cable USB-C.
- Carrito con iPhone 13 → Pack **Lightning** + cable Lightning.
- Sin errores de Liquid.
