# Textos para Meta Ads: pack cargador + cable (29/10/2026)

Mismo texto para las versiones A y B; cambia solo la primera línea. Se monta
un conjunto de anuncios con las dos y Meta reparte el dinero hacia la que más
vende (ver `../estudio-anuncios-2026-10.md`).

## Texto principal

**A** (imagen «Menos de la mitad que en Apple»):

> Cargador de 20 W + cable originales de Apple por 18,99 €. En Apple, por separado, cuestan 38 €.
>
> ¿Por qué tan barato? Porque ganamos menos por cada pack. A propósito.
>
> ✅ Nuevos y precintados, en su caja original
> 📱 USB-C (iPhone 15 o posterior) o Lightning (iPhone 8 al 14)
> 🛡️ 3 años de garantía
> 🚚 Envío gratis: en su casa en 24-48 h
> ↩️ 14 días para devolverlo, gratis

**B** (imagen «Mismo cargador. Misma caja. Mitad de precio.»): la primera
línea cambia por

> Mismo cargador. Misma caja. Mitad de precio. El pack de cargador de 20 W + cable originales de Apple, por 18,99 € (en Apple, por separado, 38 €).

y el resto igual.

**C** (foto real del stock, estilo nativo): la primera línea cambia por

> Así llegan: cargador de 20 W + cable originales de Apple, nuevos y precintados. 18,99 € el pack (en Apple, por separado, 38 €).

y el resto igual. La foto es real (`fotos/reales/cajas-frente-usb-c.jpg`),
recortada para que no salga la caja de iPhone que había al lado.

## Resto de campos

| Campo | Texto |
|---|---|
| Titular | Cargador + cable originales: 18,99 € |
| Descripción | Envío gratis · En casa en 24-48 h |
| Botón | Comprar |
| URL A | https://pillatumovil.com/collections/packs?utm_source=meta&utm_medium=paid_social&utm_campaign=pack_1899&utm_content=A |
| URL B | https://pillatumovil.com/collections/packs?utm_source=meta&utm_medium=paid_social&utm_campaign=pack_1899&utm_content=B |
| URL C | https://pillatumovil.com/collections/packs?utm_source=meta&utm_medium=paid_social&utm_campaign=pack_1899&utm_content=C |

## Imágenes

| Ubicación | A | B |
|---|---|---|
| Feed de Facebook e Instagram | `pillatumovil-A-mitad-que-en-apple_feed-4x5.jpg` | `pillatumovil-B-mismo-cargador_feed-4x5.jpg` |
| Stories y Reels | `pillatumovil-A-mitad-que-en-apple_stories-9x16.jpg` | `pillatumovil-B-mismo-cargador_stories-9x16.jpg` |
| Columna derecha, Marketplace, búsqueda | `pillatumovil-A-mitad-que-en-apple_cuadrado-1x1.jpg` | `pillatumovil-B-mismo-cargador_cuadrado-1x1.jpg` |

Versión C: `pillatumovil-C-foto-real_feed-4x5.jpg`, `pillatumovil-C-foto-real_stories-9x16.jpg` y `pillatumovil-C-foto-real_cuadrado-1x1.jpg`.

En Meta se sube cada versión con «Personalizar por ubicación» para que use la
4:5 en el feed, la 9:16 en Stories y Reels y la 1:1 en el resto.

## Comprobado antes de publicar

- Precios de Apple en apple.com/es el 29/10/2026: adaptador de 20 W
  (MD3J4ZM/A) 19 €, cable USB-C de 60 W 1 m (MW493ZM/A) 19 €, cable USB-C a
  Lightning 1 m (MUQ93ZM/A) 19 €. Si Apple los cambia, hay que rehacer la
  comparación.
- «Menos de la mitad» / «Mitad de precio»: 18,99 € es el 49,97 % de 38 €.
- Sin «Black Friday», sin urgencia ni reseñas: no hay rebaja ni reseñas reales.
- El porqué del precio lo dio el dueño: margen pequeño.
- Las imágenes se rehacen con `../fuente/anuncio.py` (A) y `../fuente/anuncio_b.py` (B).
