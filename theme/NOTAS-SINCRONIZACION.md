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

## Segunda pasada — 30/09/2026

| Fichero | De | A | Qué aporta |
|---|---|---|---|
| `assets/itoro-trade-in.js` | 13.478 B | 15.944 B | Tasador v4: ficha completa, fotos y multiplicadores <= 1 |
| `sections/itoro-trade-in.liquid` | 11.691 B | 16.884 B | Los 6 pasos (Modelo, Memoria, Estado, Ficha, Fotos, Enviar) |
| `snippets/it-wallapop-data.liquid` | 5.222 B | 6.369 B | 21 valoraciones reales (29/09) en vez de 18 |
| `snippets/it-schema-org.liquid` | — | 3.528 B | Sello y `aggregateRating` al día: 5,0 · 21 y 26 reseñas |
| `templates/index.json` | — | 7.123 B | Hero del 18 Pro Max a 1.800 € |

Los dos ficheros del tasador quedan con el **mismo tamaño exacto** que en el
tema publicado. `itoro-trade-in.css` (13.763 B) ya era idéntico en los dos, así
que no hizo falta tocarlo.

Comprobado en la vista previa del gemelo (`/pages/compramos-tu-movil`):
los 6 pasos del navegador, los 6 paneles, los campos de la ficha
(color, batería, IMEI, notas, desperfectos) y la rejilla de fotos.
Cero errores de Liquid. El JS servido por el CDN lleva `renderFicha`,
`renderShots`, `itrBateria`, el tramo de 2 TB y el WhatsApp 34624150603.

### Diferencias que quedan a propósito

`it-footer.liquid`, `it-popup-email.liquid`, `it-compra-banner.liquid`,
`it-slider-valor.liquid` y `itoro-trust-strip.liquid` siguen distintos porque
el gemelo va por delante. `it-email-gate.liquid` existe en los dos pero el
`index.json` del gemelo ya no lo invoca, así que no se renderiza.

### Pendiente

La copia de `snippets/it-schema-org.liquid` de este repositorio tiene 3.532 B
y la del tema 3.528 B. El contenido que importa es el mismo (mismas cifras,
mismo JSON, comprobado renderizado), pero conviene igualarlas cuando se vuelva
a tocar el fichero.
