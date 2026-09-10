import json, re, subprocess, tempfile, os, base64
from playwright.sync_api import sync_playwright

URL = "https://www.wallapop.com/user/fernandot-419803299"
UA  = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
SKIP_HDR = {"host","connection","content-length","accept-encoding",
            "proxy-connection","transfer-encoding"}
api_hits = []

def curl_fetch(method, url, headers, body):
    hf = tempfile.NamedTemporaryFile(delete=False, suffix=".hdr"); hf.close()
    bf = tempfile.NamedTemporaryFile(delete=False, suffix=".bin"); bf.close()
    cmd = ["curl","-sS","--compressed","--max-time","20",
           "-D", hf.name, "-o", bf.name, "-X", method, url]
    for k,v in headers.items():
        if k.lower() in SKIP_HDR: continue
        cmd += ["-H", f"{k}: {v}"]
    if body:
        df = tempfile.NamedTemporaryFile(delete=False, suffix=".body")
        df.write(body); df.close()
        cmd += ["--data-binary", "@"+df.name]
    r = subprocess.run(cmd, capture_output=True)
    raw = open(bf.name,"rb").read()
    hdr_txt = open(hf.name, "rb").read().decode("utf-8","replace")
    os.unlink(hf.name); os.unlink(bf.name)
    if r.returncode != 0:
        return None
    # last header block (after redirects)
    blocks = [b for b in re.split(r"\r?\n\r?\n", hdr_txt) if b.strip().startswith("HTTP/")]
    block = [b for b in blocks if "Connection Established" not in b.split("\n")[0]][-1]
    lines = [l for l in re.split(r"\r?\n", block.strip()) if l.strip()]
    status = int(lines[0].split()[1])
    out = {}
    for ln in lines[1:]:
        if ":" in ln:
            k,v = ln.split(":",1); k=k.strip().lower()
            if k in ("content-encoding","content-length","transfer-encoding",
                     "content-security-policy","content-security-policy-report-only",
                     "x-frame-options","strict-transport-security"):
                continue
            out[k]=v.strip()
    return status, out, raw

BLOCK = ("consentmanager.net","rudderlabs.com","sentry.io","accounts.google.com",
         "googletagmanager.com","google-analytics.com","doubleclick.net","braze",
         "tracking.wallapop.com","facebook.net","facebook.com")

def handler(route):
    req = route.request
    if any(b in req.url for b in BLOCK):
        return route.abort()
    if req.resource_type in ("image","font","media"):
        return route.abort()
    body = req.post_data_buffer
    res = curl_fetch(req.method, req.url, req.headers, body)
    if res is None:
        return route.abort()
    status, hdrs, raw = res
    u = req.url
    open("allreq.log","a").write(f"{status} {req.method} {u}\n")
    if "api.wallapop.com" in u:
        api_hits.append({"url":u,"status":status,"ct":hdrs.get("content-type",""),"body":raw.decode("utf-8","replace")[:60000]})

    route.fulfill(status=status, headers=hdrs, body=raw)

with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium",
                          args=["--no-sandbox","--disable-dev-shm-usage"])
    ctx = b.new_context(user_agent=UA, locale="es-ES",
                        viewport={"width":1400,"height":2200},
                        extra_http_headers={"Accept-Language":"es-ES,es;q=0.9"})
    ctx.route("**/*", handler)
    pg = ctx.new_page()
    pg.on("console", lambda m: print("CONSOLE", m.type, m.text[:200], flush=True))
    pg.on("pageerror", lambda e: print("PAGEERR", str(e)[:250], flush=True))
    pg.goto(URL, wait_until="domcontentloaded", timeout=90000)
    print("title:", pg.title())
    pg.wait_for_timeout(8000)
    try:
        pg.locator("#tab-reviews").click(timeout=15000, force=True)
        print("clicked #tab-reviews", flush=True)
    except Exception as e:
        print("tabfail", str(e)[:120], flush=True)
        try:
            pg.eval_on_selector("#tab-reviews", "el => el.click()")
            print("js-clicked #tab-reviews", flush=True)
        except Exception as e2:
            print("jsclickfail", str(e2)[:120], flush=True)
    pg.wait_for_timeout(9000)
    for i in range(30):
        pg.mouse.wheel(0, 2200); pg.wait_for_timeout(900)
        clicked = False
        for ms in ["button:has-text('Load more')", "button:has-text('Ver m\u00e1s')",
                   "button:has-text('Cargar m\u00e1s')", "button:has-text('more reviews')"]:
            try:
                b2 = pg.locator(ms).first
                if b2.count() and b2.is_visible():
                    b2.click(timeout=5000); clicked = True
                    print("loadmore", i, ms, flush=True); pg.wait_for_timeout(3500)
            except Exception:
                pass
        n = pg.locator("#tabpanel-reviews li, #tabpanel-reviews article, [class*=review-card]").count()
        if i % 5 == 0: print("  scroll", i, "cards:", n, flush=True)
    open("rendered.html","w",encoding="utf-8").write(pg.content())
    pg.screenshot(path="wp.png", full_page=True)
    b.close()

json.dump(api_hits, open("wp_api.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("api hits:", len(api_hits))
for h in api_hits: print("  ", h["status"], h["url"][:130])
