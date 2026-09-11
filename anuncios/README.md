# Creatividades para Meta Ads

`mkad.py` genera los dos anuncios del pack de cargador en 1080x1080 y
1080x1350. Renderiza HTML con Playwright a tamaño exacto, con la tipografía
Inter y las imágenes incrustadas en base64, así que no necesita red al
generar y sale siempre idéntico.

    python3 anuncios/mkad.py      # escribe ad-*.html
    python3 shot_ads.py           # los pasa a PNG

## De dónde salen las imágenes

La única foto del pack en Shopify son las **cajas cerradas**, que es
justo lo que no convertía. Las piezas sueltas son los renders oficiales
de Apple, en PNG con transparencia:

| Pieza | Asset de Apple |
|---|---|
| Adaptador USB-C 20 W (enchufe europeo) | `MHJE3` |
| Cable USB-C a USB-C trenzado 1 m | `MXCL3Y_AV4` |

Se descargan de `store.storeimages.cdn-apple.com/1/as-images.apple.com/is/<ID>`
con `?wid=...&hei=...&fmt=png-alpha`. Hay que mandar un User-Agent de
navegador o responde 404. El parámetro `.v=` de la URL original es un
cache-buster y se puede quitar; las dimensiones sí se pueden subir.

**Ojo con el vataje.** Buena parte de los adaptadores del catálogo de Apple
son de 35, 70 o 96 W y a simple vista se parecen. `MHJE3` es el de 20 W, que
es el que se vende en el pack. No sustituir por otro.

## El descuento del 20%

No hay ningún precio comparado puesto en Shopify, así que el "antes" no
sale de un precio anterior inventado: **17,00 € frente a 21,25 €**, que es
lo que cuestan hoy el cargador (12,75 €) y el cable (8,50 €) comprados por
separado en la propia tienda. Son 4,25 € = 20% exacto. El pie de la
creatividad lo dice explícitamente, que es lo que exige la Directiva
Ómnibus para poder tachar un precio.

Para los otros formatos: 2 unidades 30,60 € frente a 42,50 € (28%) y
3 unidades 40,80 € frente a 63,75 € (36%).
