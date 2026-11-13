# Anuncio «problema → solución» (13/11/2026)

El dueño pidió cambiar el mensaje: en vez de «¿Su iPhone vino sin cargador?», un anuncio que
resuelva un problema. Vídeo vertical 9:16 de 33 s. La voz (Elena) va por encima: nadie habla a cámara.

## Guion (voz)
1. «¿La batería de su iPhone dura cada vez menos?»
2. «Un cargador de mala calidad puede calentarlo, y castigar la batería.»
3. «Y los originales son caros: en Apple, treinta y ocho euros.»
4. «En Pillatumóvil tenemos la solución: adaptador de veinte vatios y cable, originales de Apple, por dieciocho con noventa y nueve.»
5. «Solo hasta el treinta de noviembre, o fin de existencias. Envío gratis, en veinticuatro o cuarenta y ocho horas.»
6. «No se quede sin su pack a este precio. Compre en pillatumóvil punto com.»

## Lo que se cambió de la idea del dueño, y por qué
- «Se deteriora porque no usa cargadores originales» no se puede afirmar: la batería también se gasta
  con el uso y hay cargadores buenos que no son de Apple. Se dice lo que sí es cierto: uno de mala
  calidad *puede* calentar el iPhone, y el calor castiga la batería.
- «Para que no se queden sin su pack» pasa a «sin su pack a este precio»: hay unos 600 packs, así que
  no se da a entender que se acaban. «O fin de existencias» es una condición de la oferta.
- Se trata de usted al cliente, como en toda la tienda.

## Planos
| Tiempo | Plano | Origen |
|---|---|---|
| 0-2,8 s | Cliente fastidiado, móvil sin batería | `clipH.mp4` (Kling 3.0 Pro, job 2df2a782) desde `frameH.png` (job 88b43c75) |
| 2,8-5,4 s | Detalle del cargador barato | Recorte de `frameH.png` ampliado con `tools/foto_4k.py`, zoom lento |
| 5,4-7,6 s | Cliente, sigue | `clipH.mp4` |
| 7,6-13,2 s | La tienda, cartel «38,00 € · En Apple (precio del 01/11/2026)» | Plano abierto de `video-persona/clip-intone.mp4` mejorado a 4K |
| 13,2-17,2 s | La chica enseña las dos cajas | `video-persona/broll/clipA.mp4` |
| 17,2-22,3 s | Gira la caja con las dos manos; cartel «18,99 €» | `clipT.mp4` (Kling, job 0ca6e566), de `frameT.png` (job f54c3320) a `frameT_trasera.png` |
| 22,3-26,6 s | Entrega el pack en el mostrador | `video-persona/broll/clipC.mp4` |
| 26,6-33 s | Cierre: precio, plazo, envío y **pillatumovil.com** en grande | `tools/video_problema.py` |

- `frameT_trasera.png` lleva la parte de atrás real de la caja (`tools/caja_trasera_en_mano.py`).
- El plano del giro se rehízo porque en el anterior la gente de la calle se quedaba parada y el giro
  salía mecánico. Ahora el fondo es la pared de la tienda y gira la caja con las dos manos.
- Voz: `voz-problema-elena.mp3` (ElevenLabs, Elena, job 7ed0cccb, 1,5 créditos).

## Cómo se monta
```
cd pillatumovil/anuncios/2026-11/video-problema
bash ../../../tools/montaje_problema.sh CARPETA_4K MODELOS_DIR      # montaje-problema-4k.mp4
python3 ../../../tools/video_problema.py montaje-problema-4k.mp4 FUENTES SALIDA.mp4 2
```
CARPETA_4K es la de los planos mejorados con `tools/mejorar_4k.py` (hace falta `4.mp4`).

## Ficheros finales
- `pillatumovil_video_problema_9x16.mp4`: 1080x1920, el que se sube a Meta.
- `pillatumovil_video_problema_4k.mp4`: 2160x3840 (crf 22). El máster (69 MB) se envió al dueño por el chat.

## Legal
- Personas y escenas hechas con IA: el dueño debe marcar en Meta la casilla de contenido hecho con IA.
- Comparación: «En Apple, 38,00 € (precio del 01/11/2026)». Sin reseñas ni «antes» inventados.
