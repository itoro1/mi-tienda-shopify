# Herramienta para trabajar con la tienda Pillatumovil por la API de Shopify
# (Admin GraphQL 2025-10). Lee las credenciales de las variables de entorno
# SHOPIFY_PTM_DOMAIN, SHOPIFY_PTM_CLIENT_ID y SHOPIFY_PTM_CLIENT_SECRET
# (secretos del entorno, nunca en el repositorio ni en el chat). El token se
# pide por client credentials, dura 24 h y se guarda en ~/.cache.
#
# uso:
#   python3 ptm.py gql '{ shop { name } }'                 consulta GraphQL
#   python3 ptm.py temas                                   lista los temas y su papel
#   python3 ptm.py bajar TEMA_ID ruta/archivo ...          baja archivos del tema a theme/
#   python3 ptm.py subir TEMA_ID ruta/archivo ...          sube archivos de theme/ al tema
#   python3 ptm.py medios fichero.png fichero.mp4 ...      sube a Contenido > Archivos
# TEMA_ID es el numero (207180497244) o el gid completo.
# Rutas de tema relativas a la carpeta theme/ (p. ej. sections/ps-hero.liquid).
import json, os, sys, time, subprocess, mimetypes

API = '2025-10'
AQUI = os.path.dirname(os.path.abspath(__file__))
TEMA_DIR = os.path.normpath(os.path.join(AQUI, '..', '..', 'theme'))
CACHE = os.path.expanduser('~/.cache/ptm-token.json')

def _curl(args, datos=None):
    r = subprocess.run(['curl', '-sS'] + args, input=datos, capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr)
    return r.stdout

def token():
    try:
        t = json.load(open(CACHE))
        if t['caduca'] > time.time() + 300: return t['access_token']
    except Exception:
        pass
    dom = os.environ['SHOPIFY_PTM_DOMAIN']
    out = json.loads(_curl(['-X', 'POST', f'https://{dom}/admin/oauth/access_token',
                            '--data-urlencode', 'grant_type=client_credentials',
                            '--data-urlencode', 'client_id=' + os.environ['SHOPIFY_PTM_CLIENT_ID'],
                            '--data-urlencode', 'client_secret=' + os.environ['SHOPIFY_PTM_CLIENT_SECRET']]))
    out['caduca'] = time.time() + int(out.get('expires_in', 86399))
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    json.dump(out, open(CACHE, 'w')); os.chmod(CACHE, 0o600)
    return out['access_token']

def gql(query, variables=None):
    dom = os.environ['SHOPIFY_PTM_DOMAIN']
    out = json.loads(_curl(['-X', 'POST', f'https://{dom}/admin/api/{API}/graphql.json',
                            '-H', 'X-Shopify-Access-Token: ' + token(), '-H', 'Content-Type: application/json',
                            '--data-binary', '@-'], json.dumps({'query': query, 'variables': variables or {}})))
    if out.get('errors'): raise SystemExit(json.dumps(out['errors'], ensure_ascii=False))
    return out['data']

def gid(t):
    return t if str(t).startswith('gid://') else f'gid://shopify/OnlineStoreTheme/{t}'

def temas():
    for n in gql('{ themes(first:20){ nodes{ id name role } } }')['themes']['nodes']:
        print(n['role'].ljust(12), n['id'].split('/')[-1], n['name'])

def bajar(tema, rutas):
    d = gql('query($t:ID!,$f:[String!]){ theme(id:$t){ files(filenames:$f, first:250){ nodes{ filename body{ ... on OnlineStoreThemeFileBodyText{ content } } } } } }',
            {'t': gid(tema), 'f': rutas})
    for n in d['theme']['files']['nodes']:
        destino = os.path.join(TEMA_DIR, n['filename']); os.makedirs(os.path.dirname(destino), exist_ok=True)
        open(destino, 'w').write(n['body']['content']); print('bajado', n['filename'])

def subir(tema, rutas):
    """Sube de uno en uno para ver el error de cada archivo (Liquid mal formado, etc.)."""
    q = '''mutation($t:ID!,$f:[OnlineStoreThemeFilesUpsertFileInput!]!){ themeFilesUpsert(themeId:$t, files:$f){
             upsertedThemeFiles{ filename } userErrors{ filename message } } }'''
    for r in rutas:
        d = gql(q, {'t': gid(tema), 'f': [{'filename': r, 'body': {'type': 'TEXT', 'value': open(os.path.join(TEMA_DIR, r)).read()}}]})
        e = d['themeFilesUpsert']['userErrors']
        print(('ERROR ' + json.dumps(e, ensure_ascii=False)) if e else 'subido', r)

def medios(rutas):
    ids = {}
    for ruta in rutas:
        mime = mimetypes.guess_type(ruta)[0]; video = mime.startswith('video/')
        t = gql('''mutation($i:[StagedUploadInput!]!){ stagedUploadsCreate(input:$i){ stagedTargets{ url resourceUrl parameters{ name value } } userErrors{ message } } }''',
                {'i': [{'filename': os.path.basename(ruta), 'mimeType': mime, 'resource': 'VIDEO' if video else 'IMAGE',
                        'httpMethod': 'POST', 'fileSize': str(os.path.getsize(ruta))}]})['stagedUploadsCreate']['stagedTargets'][0]
        args = ['-o', '/dev/null', '-w', '%{http_code}', '-X', 'POST', t['url']]
        for p in t['parameters']: args += ['-F', f"{p['name']}={p['value']}"]
        codigo = _curl(args + ['-F', f'file=@{ruta};type={mime}'])
        if codigo not in ('200', '201', '204'): raise SystemExit(f'subida fallida {ruta}: {codigo}')
        d = gql('''mutation($f:[FileCreateInput!]!){ fileCreate(files:$f){ files{ id } userErrors{ message } } }''',
                {'f': [{'originalSource': t['resourceUrl'], 'contentType': 'VIDEO' if video else 'IMAGE', 'filename': os.path.basename(ruta)}]})
        if d['fileCreate']['userErrors']: raise SystemExit(d['fileCreate']['userErrors'])
        ids[ruta] = d['fileCreate']['files'][0]['id']
    for _ in range(60):
        nodos = gql('''query($i:[ID!]!){ nodes(ids:$i){ ... on MediaImage{ id fileStatus image{ url } } ... on Video{ id fileStatus sources{ url } } } }''',
                    {'i': list(ids.values())})['nodes']
        if all(n['fileStatus'] in ('READY', 'FAILED') for n in nodos): break
        time.sleep(4)
    for n in nodos: print(json.dumps(n, ensure_ascii=False))
    print('En el tema se usan como shopify://shop_images/<nombre-del-fichero>')

if __name__ == '__main__':
    orden, resto = sys.argv[1], sys.argv[2:]
    if orden == 'gql': print(json.dumps(gql(resto[0], json.loads(resto[1]) if len(resto) > 1 else None), ensure_ascii=False, indent=1))
    elif orden == 'temas': temas()
    elif orden == 'bajar': bajar(resto[0], resto[1:])
    elif orden == 'subir': subir(resto[0], resto[1:])
    elif orden == 'medios': medios(resto)
    else: raise SystemExit('orden desconocida: ' + orden)
