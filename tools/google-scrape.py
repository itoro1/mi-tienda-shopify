"""Lee la ficha de Google Business de ITOROSTORE y vuelca nota, numero de
resenas y los textos. Mismo truco que wallapop-scrape.py: Chromium real, pero
cada peticion se resuelve por curl porque Chromium no atraviesa el proxy."""
import json, re, subprocess, tempfile, os
from playwright.sync_api import sync_playwright

CID = "1115849531936487308"
# La URL a la que redirige el enlace corto g.page: abre la ficha directamente,
# sin pasar por el mapa del mundo. 12e1 abre el panel de resenas.
URL = ("https://www.google.com/maps/place//data=!4m3!3m2"
       "!1s0xd0d73558ac38dff:0xf7c4b3cbddc378c!12e1?hl=es&gl=ES")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
SKIP_HDR = {"host", "connection", "content-length", "accept-encoding",
            "proxy-connection", "transfer-encoding"}
hits = []


def curl_fetch(method, url, headers, body):
    hf = tempfile.NamedTemporaryFile(delete=False, suffix=".hdr"); hf.close()
    bf = tempfile.NamedTemporaryFile(delete=False, suffix=".bin"); bf.close()
    cmd = ["curl", "-sS", "--compressed", "--max-time", "25",
           "-D", hf.name, "-o", bf.name, "-X", method, url]
    for k, v in headers.items():
        if k.lower() in SKIP_HDR:
            continue
        cmd += ["-H", f"{k}: {v}"]
    if body:
        df = tempfile.NamedTemporaryFile(delete=False, suffix=".body")
        df.write(body); df.close()
        cmd += ["--data-binary", "@" + df.name]
    r = subprocess.run(cmd, capture_output=True)
    raw = open(bf.name, "rb").read()
    hdr_txt = open(hf.name, "rb").read().decode("utf-8", "replace")
    os.unlink(hf.name); os.unlink(bf.name)
    if r.returncode != 0:
        return None
    blocks = [b for b in re.split(r"\r?\n\r?\n", hdr_txt) if b.strip().startswith("HTTP/")]
    block = [b for b in blocks if "Connection Established" not in b.split("\n")[0]][-1]
    lines = [l for l in re.split(r"\r?\n", block.strip()) if l.strip()]
    status = int(lines[0].split()[1])
    out = {}
    for ln in lines[1:]:
        if ":" not in ln:
            continue
        k, v = ln.split(":", 1); k = k.strip().lower()
        # Google manda cabeceras que Playwright no sabe reenviar (alt-svc
        # anuncia HTTP/3, los report-to y cross-origin-* traen JSON con
        # comas). Si fulfill revienta, la peticion se escapa a la red real.
        if k in ("content-encoding", "content-length", "transfer-encoding",
                 "content-security-policy", "content-security-policy-report-only",
                 "x-frame-options", "strict-transport-security",
                 "alt-svc", "set-cookie", "report-to", "reporting-endpoints",
                 "permissions-policy", "document-policy", "origin-trial",
                 "cross-origin-opener-policy", "cross-origin-embedder-policy",
                 "cross-origin-resource-policy", "accept-ch", "critical-ch",
                 "p3p", "link", "server-timing"):
            continue
        out[k] = v.strip()
    return status, out, raw


def handler(route):
    req = route.request
    print("REQ", req.resource_type, req.url[:95], flush=True)
    if req.resource_type in ("image", "font", "media"):
        return route.abort()
    res = curl_fetch(req.method, req.url, req.headers, req.post_data_buffer)
    if res is None:
        return route.abort()
    status, hdrs, raw = res
    if ("listugcposts" in req.url or "listentitiesreviews" in req.url
            or "/maps/preview/place" in req.url):
        hits.append({"url": req.url[:200], "status": status,
                     "body": raw.decode("utf-8", "replace")})
    try:
        route.fulfill(status=status, headers=hdrs, body=raw)
    except Exception as e:
        print("FULFILL FALLO", status, req.url[:70], "->", str(e)[:200], flush=True)
        try:
            route.fulfill(status=status,
                          headers={"content-type": hdrs.get("content-type", "text/html")},
                          body=raw)
        except Exception as e2:
            print("  segundo intento tambien", str(e2)[:120], flush=True)
            route.abort()


with sync_playwright() as p:
    # Google va por QUIC (UDP) en cuanto puede, y ese transporte se salta el
    # interceptor de Playwright. Desactivandolo, Chromium usa TCP y entonces
    # SI pasa por el handler, que resuelve cada peticion con curl. No se toca
    # nada de la validacion del certificado: curl valida como siempre.
    b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium",
                          args=["--no-sandbox", "--disable-dev-shm-usage",
                                "--disable-quic"])
    ctx = b.new_context(user_agent=UA, locale="es-ES",
                        viewport={"width": 1400, "height": 1600},
                        extra_http_headers={"Accept-Language": "es-ES,es;q=0.9"})
    ctx.add_cookies([
        {"name": "SOCS", "value": "CAESHAgBEhJnd3NfMjAyNDA2MDMtMF9SQzEaAmVzIAEaBgiA4a-zBg",
         "domain": ".google.com", "path": "/"},
        {"name": "CONSENT", "value": "YES+cb", "domain": ".google.com", "path": "/"},
    ])
    ctx.route("**/*", handler)
    pg = ctx.new_page()
    pg.route("**/*", handler)
    pg.goto(URL, wait_until="domcontentloaded", timeout=90000)
    pg.wait_for_timeout(9000)
    print("title:", pg.title(), flush=True)
    try:
        print("=== PANEL ===\n", pg.locator('div[role="main"]').first.inner_text(timeout=15000)[:1500], flush=True)
    except Exception as e:
        print("panelfail", str(e)[:150], flush=True)
    for sel in ['button[aria-label*="Reseñas"]', 'button[aria-label*="reseñas"]',
                'button:has-text("Reseñas")', 'button[jsaction*="reviewChart"]']:
        try:
            l = pg.locator(sel).first
            if l.count():
                l.click(timeout=6000)
                print("click", sel, flush=True)
                pg.wait_for_timeout(5000)
                break
        except Exception:
            pass
    for _ in range(14):
        try:
            pg.mouse.wheel(0, 2000)
        except Exception:
            pass
        pg.wait_for_timeout(1200)
    open("g_rendered.html", "w", encoding="utf-8").write(pg.content())
    try:
        print("=== RESENAS ===\n", pg.locator('div[role="main"]').first.inner_text()[:6000], flush=True)
    except Exception as e:
        print("rfail", str(e)[:120], flush=True)
    b.close()

json.dump(hits, open("g_api.json", "w", encoding="utf-8"), ensure_ascii=False)
print("rpc hits:", len(hits), flush=True)
