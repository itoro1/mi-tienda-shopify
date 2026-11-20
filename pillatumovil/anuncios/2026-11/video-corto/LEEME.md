# Anuncio corto · precio primero (20/11/2026)

Sale del estudio de `../prompt-mejora-anuncio.md`. Es el vídeo de la chica (el que vende), recortado y reordenado: 18 s en vez de 32, y el precio en pantalla desde el primer fotograma.

- `pillatumovil_anuncio_corto_v1_9x16.mp4`: 1080x1920, 24 fps, 18,3 s, voz a −14 LUFS. Es el que se subió a Meta.
- El máster en 4K (2160x3840) se le envió al dueño por el chat. No está aquí por tamaño.
- `cortes-v1.json`: la lista de cortes con la que se monta (`tools/anuncio_cortes.py`). `SCRATCH` es la carpeta de trabajo con los tramos 4K de la chica (`k4/1, 3, 4, 6.mp4`), las cajas 3D (`c3d/dep/B.mp4`) y el giro. `PTM` es `pillatumovil/`.
- `miniatura-corto-v1.jpg`: portada del anuncio (segundo 3).

## Plano a plano (tiempos de la voz original → vídeo final, todo a ×1,10)

| Final | Imagen | Voz |
|---|---|---|
| 0,0-2,0 | Chica, plano general (H1) | «¿Su iPhone vino sin cargador?» (0,00-2,20) |
| 2,0-4,3 | Chica, primer plano (H3) | «En Apple, 38 €.» (12,30-14,80) |
| 4,3-6,6 | Chica, plano general (H4) | «Aquí, 18,99 €.» (15,08-17,62) |
| 6,6-7,8 | Foto real del cargador: grabado «Designed by Apple in California» | «Originales de Apple,» (8,86-10,20), en off |
| 7,8-9,1 | Caja real en 3D girando, sin la cara | «en su caja sin abrir.» (10,22-11,70), en off |
| 9,1-11,8 | Chica, plano general (H4) | «Compramos por cantidad y ganamos menos.» (17,70-20,66) |
| 11,8-14,9 | Foto real: traseras de las cajas, cargador y cable (sin la bolsa de Apple) | «Envío gratis en 24-48 h.» (20,94-24,35), en off |
| 14,9-16,3 | Chica, primer plano (H6) | «Toque «Comprar».» (27,94-29,40) |
| 16,3-18,3 | Tarjeta final: pillatumovil.com, 18,99 €, comparación, 2 y 3 packs, envío y devolución gratis, plazo | — |

- Cada tramo con la boca de la chica lleva su propio audio a la misma hora, así que la boca cuadra.
- Los cortes caen en silencios, medidos en la forma de onda: «Normal:» empieza en 2,40; «En» en 12,42; la respiración está entre 20,72 y 20,90; «Dese» empieza en 24,38.
- Se quitó «Dese prisa: este precio acaba el 30/11»: la fecha queda solo como condición, en la tarjeta final y en el texto.

## Rótulos

- Cartel de precio a dos columnas: «En Apple 38,00 € (precio del 01/11/2026)» | «Aquí 18,99 €». Nunca tachado. Va arriba (15-23 % de la altura) en los planos de la chica y a media altura en el último.
- «ORIGINAL de Apple · adaptador 20 W + cable» durante los primeros 6,6 s, encima de las cajas del mostrador.
- Subtítulos palabra a palabra al 54 % de la altura. En los insertos suben al 13 % para no tapar el producto.
- Todo cabe en el 4:5 del feed (corta un 15 % arriba y otro abajo) y queda fuera de la zona que tapan los botones de Reels.

## Lo que se descartó y por qué

- «¿Original o imitación?», con una voz nueva: gastaba el único crédito que queda, escondía a la chica hasta el segundo 6 y abría sembrando la duda.
- Empezar directamente con «En Apple, 38 €»: quitaba el gancho que ya vende.
- La foto `cajas-frente-usb-c.jpg` a pantalla completa: sale la bolsa con el logo de Apple y la caja de un iPhone. Daría a entender que todo eso va por 18,99 €.
- Queda de reserva por si este anuncio trae clics pero no compras.
