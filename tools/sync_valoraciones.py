#!/usr/bin/env python3
"""Relee las valoraciones de Wallapop y Google y las deja publicadas.

Pensado para correr en GitHub Actions, donde hay internet directo. En las
sesiones remotas de Claude hace falta el truco de resolver cada peticion por
curl (ver google-scrape.py y wallapop-scrape.py); aqui no, y por eso este
script es mucho mas simple.

    python3 tools/sync_valoraciones.py --dry-run   # solo escribe en disco
    python3 tools/sync_valoraciones.py             # escribe y sube al tema

Variables de entorno:

    SHOPIFY_STORE     udyaa4-gf.myshopify.com
    SHOPIFY_TOKEN     token de app privada con permiso write_themes
    WALLAPOP_PROFILE  fernandot-419803299
    GOOGLE_PLACE_ID   ChIJ_43DilVzDQ0RjDfcvTxLfA8
    GOOGLE_FEATURE_ID 0xd0d73558ac38dff:0xf7c4b3cbddc378c
    GOOGLE_API_KEY    opcional. Sin ella se actualizan nota y total pero no
                      los textos de las resenas de Google.
"""
import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNIPPETS = os.path.join(RAIZ, "theme", "snippets")

STORE = os.environ.get("SHOPIFY_STORE", "udyaa4-gf.myshopify.com")
TOKEN = os.environ.get("SHOPIFY_TOKEN", "")
WP_PROFILE = os.environ.get("WALLAPOP_PROFILE", "fernandot-419803299")
GG_PLACE = os.environ.get("GOOGLE_PLACE_ID", "ChIJ_43DilVzDQ0RjDfcvTxLfA8")
GG_FEATURE = os.environ.get("GOOGLE_FEATURE_ID",
                            "0xd0d73558ac38dff:0xf7c4b3cbddc378c")
GG_KEY = os.environ.get("GOOGLE_API_KEY", "")

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
API = "2026-07"


def log(*a):
    print(*a, flush=True)


def coma(x):
    """4.9 -> '4,9', como se escribe en espanol."""
    return ("%.1f" % float(x)).replace(".", ",")


def pipe(valores):
    """Une para un split: '|' de Liquid. Lo vacio va como espacio, porque
    Liquid se come las cadenas vacias al final del split."""
    fuera = []
    for v in valores:
        v = (v or "").replace("|", "/").replace("\n", " ").replace("\r", " ")
        fuera.append(v.strip() or " ")
    return "|".join(fuera)


# --------------------------------------------------------------------------
# Wallapop
# --------------------------------------------------------------------------

def leer_wallapop():
    """Abre el perfil en Chromium y se queda con las dos respuestas de la API
    que carga la pestana de valoraciones."""
    from playwright.sync_api import sync_playwright

    url = f"https://www.wallapop.com/user/{WP_PROFILE}"
    capturado = {}

    def mirar(resp):
        u = resp.url
        try:
            if "reviews/user-profile" in u and resp.status == 200:
                capturado.setdefault("reviews", resp.json())
            elif "reviews/summary" in u and resp.status == 200:
                capturado.setdefault("summary", resp.json())
        except Exception:
            pass

    with sync_playwright() as p:
        b = p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
        ctx = b.new_context(user_agent=UA, locale="es-ES",
                            viewport={"width": 1400, "height": 2200},
                            extra_http_headers={"Accept-Language": "es-ES,es;q=0.9"})
        # El banner de consentimiento tapa la pestana de valoraciones.
        for dominio in ("consentmanager.net", "rudderlabs.com", "sentry.io",
                        "googletagmanager.com", "google-analytics.com",
                        "doubleclick.net", "tracking.wallapop.com"):
            ctx.route(f"**://*{dominio}/**", lambda r: r.abort())
        pg = ctx.new_page()
        pg.on("response", mirar)
        pg.goto(url, wait_until="domcontentloaded", timeout=90000)
        pg.wait_for_timeout(6000)
        try:
            pg.locator("#tab-reviews").click(timeout=15000, force=True)
        except Exception as e:
            log("  no se pudo pulsar la pestana:", str(e)[:100])
        for _ in range(12):
            if "reviews" in capturado and "summary" in capturado:
                break
            pg.mouse.wheel(0, 2000)
            pg.wait_for_timeout(1500)
        b.close()

    if "reviews" not in capturado:
        raise RuntimeError("Wallapop no devolvio la lista de valoraciones")
    resumen = capturado.get("summary") or {}
    return {
        "reviews": capturado["reviews"],
        "total": resumen.get("total_reviews") or len(capturado["reviews"]),
        "media": resumen.get("average") or 5.0,
    }


def genera_wallapop(d, ratings_perfil):
    rv = d["reviews"]
    textos, nombres, estrellas, fotos, prods, fechas = [], [], [], [], [], []
    for r in rv:
        com = ((r.get("comment") or {}).get("original") or "").strip()
        venta = r.get("sale") or {}
        av = r.get("user", {}).get("picture_url") or ""
        pr = venta.get("picture_url") or ""
        # Los placeholder genericos de Wallapop no aportan nada.
        if "placeholder" in av or "cloudfront" in av:
            av = ""
        if "wallapop-sales-public" in pr or "placeholder" in pr:
            pr = ""
        textos.append(com)
        nombres.append(re.sub(r"\s+", " ", r.get("user", {}).get("name", "")).strip())
        estrellas.append(str(r.get("rating_over_five") or 5))
        fotos.append(av.replace("pictureSize=W800", "pictureSize=W320"))
        prods.append(pr.replace("pictureSize=W800", "pictureSize=W320"))
        fechas.append(r.get("published") or "")

    return f"""{{%- comment -%}}
  Valoraciones reales del perfil de Wallapop de ITorostore
  ({WP_PROFILE}). Generado por tools/sync_valoraciones.py.
  NO EDITAR A MANO: lo sobrescribe la siguiente ejecucion.
  {coma(d['media'])} de media sobre {d['total']} valoraciones escritas
  y {ratings_perfil} valoraciones en total.
  Quien puntua sin escribir comentario entra igual, con el texto en
  blanco; la seccion lo dice en vez de ensenar comillas vacias.
{{%- endcomment -%}}
{{%- assign wp_text = '{pipe(textos)}' | split: '|' -%}}
{{%- assign wp_name = '{pipe(nombres)}' | split: '|' -%}}
{{%- assign wp_stars = '{pipe(estrellas)}' | split: '|' -%}}
{{%- assign wp_photo = '{pipe(fotos)}' | split: '|' -%}}
{{%- assign wp_prod = '{pipe(prods)}' | split: '|' -%}}
{{%- assign wp_when = '{pipe(fechas)}' | split: '|' -%}}
{{%- assign wp_total = {len(rv)} -%}}
{{%- assign wp_avg = '{coma(d['media'])}' -%}}
{{%- assign wp_reviews = '{d['total']}' -%}}
{{%- assign wp_ratings = '{ratings_perfil}' -%}}
{{%- assign wp_profile = 'https://es.wallapop.com/app/user/{WP_PROFILE}' -%}}
"""


# --------------------------------------------------------------------------
# Google
# --------------------------------------------------------------------------

def _get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read().decode("utf-8", "replace")


def leer_google():
    """Con clave: Places API, que da nota, total y hasta 5 resenas con texto.
    Sin clave: el endpoint interno maps/preview/place, que da nota y total."""
    if GG_KEY:
        url = f"https://places.googleapis.com/v1/places/{GG_PLACE}?languageCode=es"
        cuerpo = _get(url, {
            "User-Agent": UA,
            "X-Goog-Api-Key": GG_KEY,
            "X-Goog-FieldMask": "rating,userRatingCount,reviews",
        })
        d = json.loads(cuerpo)
        resenas = []
        for r in d.get("reviews", []):
            resenas.append({
                "nombre": (r.get("authorAttribution") or {}).get("displayName", ""),
                "texto": ((r.get("originalText") or r.get("text") or {})
                          .get("text", "")),
                "estrellas": r.get("rating") or 5,
                "cuando": r.get("relativePublishTimeDescription") or "",
            })
        return {"media": d.get("rating"), "total": d.get("userRatingCount"),
                "resenas": resenas, "fuente": "places-api"}

    fid = urllib.parse.quote(GG_FEATURE, safe="")
    cuerpo = _get("https://www.google.com/maps/preview/place"
                  f"?authuser=0&hl=es&gl=es&pb=!1m1!1s{fid}")
    if "/sorry/" in cuerpo:
        raise RuntimeError("Google ha respondido con su CAPTCHA (/sorry). "
                           "Esta IP esta marcada como trafico automatico.")
    # Doble comprobacion a proposito: el payload trae la cifra dos veces, como
    # "8 resenas" y como el par ,4.9,8]. Si no coinciden, o si el par aparece
    # mas de una vez, preferimos fallar: esto publica en la tienda en vivo y un
    # numero equivocado es peor que no actualizar.
    texto = re.search(r'"(\d+) rese\\u00f1as"|"(\d+) reseñas"', cuerpo)
    if not texto:
        raise RuntimeError("no encuentro el numero de resenas en la respuesta")
    total = int(texto.group(1) or texto.group(2))

    pares = re.findall(r",(\d\.\d)," + str(total) + r"\]", cuerpo)
    if len(pares) != 1:
        raise RuntimeError(
            f"esperaba una sola nota junto al total {total} y encuentro "
            f"{len(pares)}: {pares}. Google ha cambiado el formato.")
    media = float(pares[0])
    if not (1.0 <= media <= 5.0):
        raise RuntimeError(f"nota fuera de rango: {media}")
    return {"media": media, "total": total,
            "resenas": [], "fuente": "maps/preview/place"}


def genera_google(g, anterior):
    """Si Google no ha dado textos, se conservan los que ya habia y solo se
    refrescan la nota y el total: es lo que hace la version sin clave."""
    if g["resenas"]:
        textos = [r["texto"] for r in g["resenas"]]
        nombres = [r["nombre"] for r in g["resenas"]]
        estrellas = [str(int(r["estrellas"])) for r in g["resenas"]]
        fechas = [r["cuando"] for r in g["resenas"]]
        # Sin foto a proposito: rehospedar las caras de los clientes en la
        # tienda nos haria responsables de esos datos sin base legal, y
        # enlazar a googleusercontent se rompe. La seccion pone la inicial.
        av = [""] * len(textos)
        pic = [""] * len(textos)
        meta = [""] * len(textos)
        total_tarjetas = len(textos)
    else:
        def saca(clave):
            m = re.search(r"assign " + clave + r" = '(.*?)' \| split", anterior, re.S)
            return m.group(1) if m else " "
        textos = saca("gg_text").split("|")
        nombres = saca("gg_name").split("|")
        estrellas = saca("gg_stars").split("|")
        fechas = saca("gg_when").split("|")
        av = saca("gg_av").split("|")
        pic = saca("gg_pic").split("|")
        meta = saca("gg_meta").split("|")
        total_tarjetas = len(textos)

    aviso = ""
    if total_tarjetas < (g["total"] or 0):
        aviso = (f"\n  Se ensenan {total_tarjetas} tarjetas de {g['total']} resenas: "
                 "Google\n  no sirve el texto de todas por esta via.")

    return f"""{{%- comment -%}}
  Resenas de la ficha de Google Business de ITorostore
  (place_id {GG_PLACE}).
  Generado por tools/sync_valoraciones.py leyendo {g['fuente']}.
  NO EDITAR A MANO: lo sobrescribe la siguiente ejecucion.
  {coma(g['media'])} de media sobre {g['total']} resenas.{aviso}
{{%- endcomment -%}}
{{%- assign gg_text = '{pipe(textos)}' | split: '|' -%}}
{{%- assign gg_name = '{pipe(nombres)}' | split: '|' -%}}
{{%- assign gg_stars = '{pipe(estrellas)}' | split: '|' -%}}
{{%- assign gg_when = '{pipe(fechas)}' | split: '|' -%}}
{{%- assign gg_meta = '{pipe(meta)}' | split: '|' -%}}
{{%- assign gg_av = '{pipe(av)}' | split: '|' -%}}
{{%- assign gg_pic = '{pipe(pic)}' | split: '|' -%}}
{{%- assign gg_total = {total_tarjetas} -%}}
{{%- assign gg_avg = '{coma(g['media'])}' -%}}
{{%- assign gg_count = '{g['total']}' -%}}
{{%- assign gg_url = 'https://g.page/r/CYw33L08S3wPEBM/review' -%}}
{{%- assign gg_maps = 'https://search.google.com/local/reviews?placeid={GG_PLACE}' -%}}
"""


# --------------------------------------------------------------------------
# El sello flotante y los datos estructurados
# --------------------------------------------------------------------------

def actualiza_sello(texto, g, w, wp_escritas):
    """Toca solo las cifras del bloque JSON y del aggregateRating."""
    texto = re.sub(r'(\{"label":"Google","avg":")[^"]*(","count":")[^"]*(")',
                   lambda m: (m.group(1) + coma(g["media"]) + m.group(2)
                              + f"{g['total']} rese\\u00f1as" + m.group(3)),
                   texto)
    texto = re.sub(r'(\{"label":"Wallapop","avg":")[^"]*(","count":")[^"]*(")',
                   lambda m: (m.group(1) + coma(w["media"]) + m.group(2)
                              + f"{wp_escritas} valoraciones" + m.group(3)),
                   texto)

    total = int(g["total"]) + int(wp_escritas)
    media = ((float(g["media"]) * int(g["total"])
              + float(w["media"]) * int(wp_escritas)) / total)
    texto = re.sub(r'("ratingValue": ")[^"]*(")',
                   lambda m: m.group(1) + ("%.1f" % media) + m.group(2), texto)
    texto = re.sub(r'("reviewCount": ")[^"]*(")',
                   lambda m: m.group(1) + str(total) + m.group(2), texto)
    return texto


# --------------------------------------------------------------------------
# Subida al tema publicado
# --------------------------------------------------------------------------

def shopify(query, variables):
    datos = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(
        f"https://{STORE}/admin/api/{API}/graphql.json", data=datos,
        headers={"Content-Type": "application/json",
                 "X-Shopify-Access-Token": TOKEN})
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.loads(r.read())
    if d.get("errors"):
        raise RuntimeError(f"Shopify: {d['errors']}")
    return d["data"]


def tema_publicado():
    d = shopify("{ themes(first: 50, roles: [MAIN]) { nodes { id name } } }", {})
    nodos = d["themes"]["nodes"]
    if not nodos:
        raise RuntimeError("no encuentro el tema publicado")
    return nodos[0]["id"], nodos[0]["name"]


def sube(tema, ficheros):
    d = shopify("""
      mutation Up($themeId: ID!, $files: [OnlineStoreThemeFilesUpsertFileInput!]!) {
        themeFilesUpsert(themeId: $themeId, files: $files) {
          upsertedThemeFiles { filename size }
          userErrors { filename code message }
        }
      }""", {"themeId": tema, "files": [
        {"filename": n, "body": {"type": "TEXT", "value": v}}
        for n, v in ficheros.items()]})
    res = d["themeFilesUpsert"]
    if res["userErrors"]:
        raise RuntimeError(f"themeFilesUpsert: {res['userErrors']}")
    return res["upsertedThemeFiles"]


# --------------------------------------------------------------------------

def valida(nombre, texto):
    """Antes de subir nada: que los arrays midan lo mismo. Un desajuste aqui
    deja tarjetas con el nombre de otro, y eso no se puede publicar."""
    largos = {}
    for m in re.finditer(r"assign ((?:wp|gg)_\w+) = '(.*?)' \| split", texto, re.S):
        largos[m.group(1)] = len(m.group(2).split("|"))
    if not largos:
        raise RuntimeError(f"{nombre}: no he generado ningun array")
    if len(set(largos.values())) != 1:
        raise RuntimeError(f"{nombre}: arrays de distinto largo -> {largos}")
    log(f"  {nombre}: {list(largos.values())[0]} tarjetas, arrays cuadrados")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="escribe en disco pero no sube nada a Shopify")
    args = ap.parse_args()

    log("Leyendo Wallapop...")
    w = leer_wallapop()
    # El total de valoraciones del perfil (incluidas las que solo son
    # estrellas) no viene en el resumen; se conserva el que ya hubiera.
    previo_wp = open(os.path.join(SNIPPETS, "it-wallapop-data.liquid"),
                     encoding="utf-8").read()
    m = re.search(r"wp_ratings = '(\d+)'", previo_wp)
    ratings = m.group(1) if m else str(w["total"])
    log(f"  {len(w['reviews'])} valoraciones, media {w['media']}, "
        f"{w['total']} escritas, {ratings} en total")

    log("Leyendo Google...")
    g = leer_google()
    log(f"  media {g['media']}, {g['total']} resenas, "
        f"{len(g['resenas'])} con texto ({g['fuente']})")

    if not w["reviews"] or not g["total"]:
        raise RuntimeError("datos vacios: no publico nada")

    previo_gg = open(os.path.join(SNIPPETS, "it-google-data.liquid"),
                     encoding="utf-8").read()
    ruta_sello = os.path.join(SNIPPETS, "it-schema-org.liquid")
    sello = open(ruta_sello, encoding="utf-8").read()

    nuevos = {
        "snippets/it-wallapop-data.liquid": genera_wallapop(w, ratings),
        "snippets/it-google-data.liquid": genera_google(g, previo_gg),
        "snippets/it-schema-org.liquid": actualiza_sello(sello, g, w, w["total"]),
    }

    log("Validando...")
    for n, v in nuevos.items():
        if n.endswith("-data.liquid"):
            valida(n, v)

    for n, v in nuevos.items():
        destino = os.path.join(RAIZ, "theme", n)
        with open(destino, "w", encoding="utf-8") as f:
            f.write(v)
        log(f"  escrito {n} ({len(v.encode())} B)")

    if args.dry_run:
        log("--dry-run: no subo nada a Shopify")
        return 0
    if not TOKEN:
        log("Sin SHOPIFY_TOKEN: no subo nada")
        return 1

    tema, nombre = tema_publicado()
    log(f"Subiendo al tema publicado: {nombre}")
    for f in sube(tema, nuevos):
        log(f"  {f['filename']} -> {f['size']} B")
    log("Listo")
    return 0


if __name__ == "__main__":
    sys.exit(main())
