# Baja TODOS los archivos de texto de un tema a una carpeta (para comparar o
# trabajar). uso: python3 bajar_todo.py TEMA_ID CARPETA
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ptm import gql, gid
tema, dest = sys.argv[1], sys.argv[2]
q = '''query($t:ID!,$a:String){ theme(id:$t){ files(first:100, after:$a){ pageInfo{ hasNextPage endCursor }
  nodes{ filename body{ ... on OnlineStoreThemeFileBodyText{ content } } } } } }'''
a, n = None, 0
while True:
    f = gql(q, {'t': gid(tema), 'a': a})['theme']['files']
    for x in f['nodes']:
        b = x['body'] or {}
        if 'content' not in b: continue
        p = os.path.join(dest, x['filename']); os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'w').write(b['content']); n += 1
    if not f['pageInfo']['hasNextPage']: break
    a = f['pageInfo']['endCursor']
print(n, 'archivos en', dest)
