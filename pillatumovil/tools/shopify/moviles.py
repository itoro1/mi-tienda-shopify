# Crea (o actualiza) en Pillatumovil los 18 iPhone que vende IToroStore.
#
# Decisiones del dueño (01/11/2026):
# - Mismos precios que IToroStore, sin precio «antes» (compareAt): en
#   Pillatumovil no hay rebajas sobre precios de referencia (Omnibus).
# - Pago completo online. Garantía: 1 año segunda mano, 3 años nuevos.
# - 10 unidades por variante.
# - Plazo como IToroStore: 24-48 h si está en stock; si no, 3-5 días hábiles.
# - Fotos: las mismas de IToroStore (renders de Apple). Va contra la regla de
#   la marca («sin imágenes oficiales de Apple»), pero lo decidió el dueño.
#   No se copian las fotos reales de IToroStore porque llevan su tarjeta.
#
# Los datos se copiaron de IToroStore (Admin API, 01/11/2026). Uso:
#   python3 moviles.py            crea o actualiza los 18 (productSet por handle)
#   python3 moviles.py iphone-13  solo uno
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ptm import gql

CDN = 'https://cdn.shopify.com/s/files/1/1032/6048/8005/files/'
UBICACION = 'gid://shopify/Location/123170586972'
TIENDA_ONLINE = 'gid://shopify/Publication/377165349212'
UNIDADES = 10

# handle: (modelo, nuevo?, entradilla, [puntos], {capacidad: precio}, {(cap, color): precio excepción},
#          [colores], portada, {color: foto}, código para la referencia)
M = {
 'iphone-13': ('iPhone 13', False, 'El clásico que sigue siendo una apuesta segura. Chip A15 Bionic, cámara dual mejorada y batería que aguanta todo el día.',
   ['Pantalla Super Retina XDR OLED de 6,1"', 'Chip A15 Bionic', 'Cámara dual de 12 MP', '5G'],
   {'128GB': 279, '256GB': 309}, {}, ['Medianoche', 'Luz Estelar', 'Azul', 'Rosa', 'Rojo'], 'cover_iphone-13.jpg',
   {'Medianoche': '13_midnight.jpg', 'Luz Estelar': '13_starlight.jpg', 'Azul': '13_blue.jpg', 'Rosa': '13_pink.jpg', 'Rojo': '13_red.jpg'}, '13'),
 'iphone-13-pro': ('iPhone 13 Pro', False, 'El primer iPhone con pantalla ProMotion de 120 Hz y triple cámara.',
   ['Pantalla Super Retina XDR ProMotion de 120 Hz y 6,1"', 'Chip A15 Bionic con GPU de 5 núcleos', 'Triple cámara de 12 MP', '5G'],
   {'128GB': 349, '256GB': 389, '512GB': 549}, {}, ['Grafito', 'Oro', 'Plata', 'Sierra Azul'], 'cover_iphone-13-pro.jpg',
   {'Grafito': '13pro_graphite.jpg', 'Oro': '13pro_gold.jpg', 'Plata': '13pro_silver.jpg', 'Sierra Azul': '13pro_blue.jpg'}, '13P'),
 'iphone-13-pro-max': ('iPhone 13 Pro Max', False, 'Pantalla de 6,7", la mejor batería de su generación y triple cámara con zoom óptico 3x.',
   ['Pantalla Super Retina XDR ProMotion de 120 Hz y 6,7"', 'Chip A15 Bionic', 'Triple cámara de 12 MP con zoom óptico 3x'],
   {'128GB': 399, '256GB': 449, '512GB': 489}, {}, ['Grafito', 'Oro', 'Plata', 'Sierra Azul'], 'cov_13pm.jpg',
   {'Grafito': '13pm_graphite.jpg', 'Oro': 'cov_13pm.jpg', 'Plata': '13pm_silver.jpg', 'Sierra Azul': '13pm_blue.jpg'}, '13PM'),
 'iphone-14': ('iPhone 14', False, 'Detección de accidentes, SOS vía satélite y el fiable chip A15 Bionic.',
   ['Pantalla Super Retina XDR OLED de 6,1"', 'Chip A15 Bionic · SOS vía satélite', 'Cámara dual de 12 MP con modo Acción'],
   {'128GB': 339, '256GB': 389}, {}, ['Medianoche', 'Luz Estelar', 'Azul', 'Morado', 'Rojo'], 'cover_iphone-14.jpg',
   {'Medianoche': 'hq_14_medianoche.jpg', 'Luz Estelar': 'hq_14_luzestelar.jpg', 'Azul': 'hq_14_azul.jpg', 'Morado': 'hq_14_morado.jpg', 'Rojo': 'hq_14_rojo.jpg'}, '14'),
 'iphone-14-pro': ('iPhone 14 Pro', False, 'Estrena la Dynamic Island, la cámara de 48 MP y la pantalla siempre activa.',
   ['Pantalla Super Retina XDR ProMotion de 120 Hz y 6,1"', 'Chip A16 Bionic · Dynamic Island · Siempre activa', 'Cámara de 48 MP y teleobjetivo 3x'],
   {'128GB': 439, '256GB': 489, '512GB': 689}, {}, ['Negro Espacial', 'Plata', 'Oro', 'Morado Oscuro'], 'cover_iphone-14-pro.jpg',
   {'Negro Espacial': 'hq_14pro_negro.jpg', 'Plata': 'hq_14pro_plata.jpg', 'Oro': 'hq_14pro_oro.jpg', 'Morado Oscuro': 'hq_14pro_morado.jpg'}, '14P'),
 'iphone-14-pro-max': ('iPhone 14 Pro Max', False, 'La pantalla más grande con Dynamic Island y la mejor batería de su generación.',
   ['Pantalla Super Retina XDR ProMotion de 120 Hz y 6,7"', 'Chip A16 Bionic · Dynamic Island · Siempre activa', 'Cámara de 48 MP y teleobjetivo 3x'],
   {'128GB': 519, '256GB': 599, '512GB': 769}, {}, ['Negro Espacial', 'Plata', 'Oro', 'Morado Oscuro'], 'cover_iphone-14-pro-max.jpg',
   {'Negro Espacial': 'hq_14pm_negro.jpg', 'Plata': 'hq_14pm_plata.jpg', 'Oro': 'hq_14pm_oro.jpg', 'Morado Oscuro': 'hq_14pm_morado.jpg'}, '14PM'),
 'iphone-15': ('iPhone 15', False, 'Por fin USB-C y Dynamic Island para todos, con cámara de 48 MP.',
   ['Pantalla Super Retina XDR OLED de 6,1"', 'Chip A16 Bionic · Dynamic Island · USB-C', 'Cámara de 48 MP'],
   {'128GB': 419, '256GB': 499, '512GB': 649}, {}, ['Negro', 'Azul', 'Verde', 'Amarillo', 'Rosa'], 'cover_iphone-15.jpg',
   {'Negro': '15_black.jpg', 'Azul': '15_blue.jpg', 'Verde': '15_green.jpg', 'Amarillo': '15_yellow.jpg', 'Rosa': '15_pink.jpg'}, '15'),
 'iphone-15-pro': ('iPhone 15 Pro', False, 'Titanio aeroespacial, botón de Acción y el potente chip A17 Pro.',
   ['Pantalla Super Retina XDR ProMotion de 120 Hz y 6,1"', 'Chip A17 Pro · Titanio · Botón de Acción', 'Cámara de 48 MP y teleobjetivo 3x · USB-C'],
   {'128GB': 569, '256GB': 599, '512GB': 859}, {}, ['Titanio Negro', 'Titanio Blanco', 'Titanio Azul', 'Titanio Natural'], 'cover_iphone-15-pro.jpg',
   {'Titanio Negro': 'hq_15pro_negro.jpg', 'Titanio Blanco': 'hq_15pro_blanco.jpg', 'Titanio Azul': 'hq_15pro_azul.jpg', 'Titanio Natural': 'hq_15pro_natural.jpg'}, '15P'),
 'iphone-15-pro-max': ('iPhone 15 Pro Max', False, 'Teleobjetivo 5x exclusivo y la mejor pantalla de su generación.',
   ['Pantalla Super Retina XDR ProMotion de 120 Hz y 6,7"', 'Chip A17 Pro · Titanio · Teleobjetivo 5x', 'USB-C · Botón de Acción'],
   {'256GB': 649, '512GB': 959}, {}, ['Titanio Negro', 'Titanio Blanco', 'Titanio Azul', 'Titanio Natural'], 'cover_iphone-15-pro-max.jpg',
   {'Titanio Negro': 'hq_15pm_negro.jpg', 'Titanio Blanco': 'hq_15pm_blanco.jpg', 'Titanio Azul': 'hq_15pm_azul.jpg', 'Titanio Natural': 'hq_15pm_natural.jpg'}, '15PM'),
 'iphone-16': ('iPhone 16', False, 'Diseñado para Apple Intelligence, con chip A18 y el nuevo Control de Cámara.',
   ['Pantalla Super Retina XDR OLED de 6,1"', 'Chip A18 · Apple Intelligence · Control de Cámara', 'Cámara de 48 MP · USB-C · 5G'],
   {'128GB': 589, '256GB': 659, '512GB': 799}, {('128GB', 'Rosa'): 569}, ['Negro', 'Blanco', 'Azul', 'Verde Agua', 'Rosa'], 'cover_iphone-16.jpg',
   {'Negro': 'n_16_black.jpg', 'Blanco': 'n_16_white.jpg', 'Azul': 'n_16_ultra.jpg', 'Verde Agua': 'n_16_teal.jpg', 'Rosa': 'n_16_pink.jpg'}, '16'),
 'iphone-16-pro': ('iPhone 16 Pro', False, 'Pantalla de 6,3", teleobjetivo 5x y el chip A18 Pro.',
   ['Pantalla Super Retina XDR ProMotion de 120 Hz y 6,3"', 'Chip A18 Pro · Apple Intelligence · Control de Cámara', 'Cámara de 48 MP y teleobjetivo 5x · Titanio'],
   {'128GB': 689, '256GB': 729, '512GB': 1029}, {}, ['Titanio Negro', 'Titanio Blanco', 'Titanio Desierto', 'Titanio Natural'], 'cover_iphone-16-pro.jpg',
   {'Titanio Negro': 'n_16pro_black.jpg', 'Titanio Blanco': 'n_16pro_white.jpg', 'Titanio Desierto': 'n_16pro_desert.jpg', 'Titanio Natural': 'n_16pro_natural.jpg'}, '16P'),
 'iphone-16-pro-max': ('iPhone 16 Pro Max', False, 'La pantalla más grande (6,9"), teleobjetivo 5x y la mejor batería.',
   ['Pantalla Super Retina XDR ProMotion de 120 Hz y 6,9"', 'Chip A18 Pro · Apple Intelligence · Control de Cámara', 'Cámara de 48 MP y teleobjetivo 5x · Titanio'],
   {'256GB': 849, '512GB': 1159}, {}, ['Titanio Negro', 'Titanio Blanco', 'Titanio Desierto', 'Titanio Natural'], 'cover_iphone-16-pro-max.jpg',
   {'Titanio Negro': 'n_16pm_black.jpg', 'Titanio Blanco': 'n_16pm_white.jpg', 'Titanio Desierto': 'n_16pm_desert.jpg', 'Titanio Natural': 'n_16pm_natural.jpg'}, '16PM'),
 'iphone-17': ('iPhone 17', True, 'Chip A19, pantalla de 120 Hz y cámara mejorada.',
   ['Pantalla Super Retina XDR OLED de 6,1" y 120 Hz', 'Chip A19 · Apple Intelligence', 'Cámara de 48 MP · USB-C · 5G'],
   {'256GB': 899, '512GB': 999}, {}, ['Negro', 'Blanco', 'Azul Neblina', 'Verde Salvia', 'Lavanda'], 'cover_iphone-17.jpg',
   {'Negro': 'hq_17_negro.jpg', 'Blanco': 'hq_17_blanco.jpg', 'Azul Neblina': 'hq_17_mistblue.jpg', 'Verde Salvia': 'hq_17_sage.jpg', 'Lavanda': 'hq_17_lavanda.jpg'}, '17'),
 'iphone-17-segunda-mano': ('iPhone 17', False, 'El iPhone 17 a precio de segunda mano. Chip A19, pantalla de 6,1" y 120 Hz y cámara rediseñada.',
   ['Pantalla Super Retina XDR OLED de 6,1" y 120 Hz', 'Chip A19 · Apple Intelligence · USB-C', 'Cámara de 48 MP'],
   {'256GB': 799, '512GB': 899}, {}, ['Negro', 'Blanco', 'Azul Neblina', 'Verde Salvia', 'Lavanda'], 'cover_iphone-17.jpg',
   {'Negro': 'iphone-17-black-select-202509_6ae4741a-a335-4177-9c93-09268f3e4196.jpg', 'Blanco': 'iphone-17-white-select-202509_66794861-cdf0-4a54-9cae-82ab26bacb4f.jpg',
    'Azul Neblina': 'colors_mist_blue__700uff6zu2qa_large_03debe2d-bfb3-4ad1-b52f-bf12363fdce2.jpg', 'Verde Salvia': 'iphone-17-sage-select-202509_dfa09885-61bd-427f-a407-4f77cb3d4d81.jpg',
    'Lavanda': 'iphone-17-lavender-select-202509_6cd83bb5-dbf3-435c-bbeb-80589da9908f.jpg'}, '17SM'),
 'iphone-17-pro': ('iPhone 17 Pro', True, 'Chip A19 Pro, sistema de cámara rediseñado y cuerpo de titanio.',
   ['Pantalla Super Retina XDR ProMotion de 120 Hz y 6,3"', 'Chip A19 Pro · Apple Intelligence', 'Triple cámara rediseñada y teleobjetivo 5x', 'Titanio · Botón de Acción · USB-C'],
   {'256GB': 1099, '512GB': 1229}, {}, ['Naranja Cósmico', 'Azul Profundo', 'Plata'], 'cover_iphone-17-pro.jpg',
   {'Naranja Cósmico': 'hq_17_orange.jpg', 'Azul Profundo': 'hq_17_blue.jpg', 'Plata': 'hq_17_silver.jpg'}, '17P'),
 'iphone-17-pro-max': ('iPhone 17 Pro Max', True, 'Chip A19 Pro, pantalla de 6,9", sistema de cámara rediseñado y batería para todo el día.',
   ['Pantalla Super Retina XDR ProMotion de 120 Hz y 6,9"', 'Sistema de cámara Pro rediseñado', 'Chip A19 Pro', 'Cuerpo de titanio'],
   {'256GB': 1249, '512GB': 1389}, {('256GB', 'Azul Profundo'): 1179}, ['Naranja Cósmico', 'Azul Profundo', 'Plata'], 'cover_iphone-17-pro-max.jpg',
   {'Naranja Cósmico': 'hq_17_orange_c3428b30-757d-4401-bb2d-6b676e05a724.jpg', 'Azul Profundo': 'hq_17_blue_09f2492a-14e8-496d-9141-509326e275b6.jpg', 'Plata': 'hq_17_silver_69eb2bbf-e4bd-4b82-9fc4-cc88a5297ca2.jpg'}, '17PM'),
 'iphone-18-pro': ('iPhone 18 Pro', True, 'La nueva generación Pro de Apple, presentada el 9 de septiembre de 2026. Chip A20 Pro de 2 nanómetros e iOS 20.',
   ['Cuatro acabados: Negro, Plata, Azul glacial y Burdeos', 'Capacidades de 256 GB y 512 GB', 'Chip A20 Pro, el primero de Apple fabricado en 2 nm'],
   {'256GB': 1470, '512GB': 1950}, {}, ['Negro', 'Plata', 'Azul glacial', 'Burdeos'], 'iphone-18-pro-finish-select-burgundy-202609.png',
   {'Negro': 'iphone-18-pro-finish-select-black-202609.png', 'Plata': 'iphone-18-pro-finish-select-silver-202609.png', 'Azul glacial': 'iphone-18-pro-finish-select-glacier-202609.png', 'Burdeos': 'iphone-18-pro-finish-select-burgundy-202609.png'}, '18P'),
 'iphone-18-pro-max': ('iPhone 18 Pro Max', True, 'La nueva generación Pro de Apple, presentada el 9 de septiembre de 2026. Chip A20 Pro de 2 nanómetros e iOS 20.',
   ['Cuatro acabados: Negro, Plata, Azul glacial y Burdeos', 'Capacidades de 256 GB y 512 GB', 'Chip A20 Pro, el primero de Apple fabricado en 2 nm'],
   {'256GB': 1649, '512GB': 2099}, {}, ['Negro', 'Plata', 'Azul glacial', 'Burdeos'], 'iphone-18-pro-max-finish-select-burgundy-202609.png',
   {'Negro': 'iphone-18-pro-max-finish-select-black-202609.png', 'Plata': 'iphone-18-pro-max-finish-select-silver-202609.png', 'Azul glacial': 'iphone-18-pro-max-finish-select-glacier-202609.png', 'Burdeos': 'iphone-18-pro-max-finish-select-burgundy-202609.png'}, '18PM'),
}

def descripcion(modelo, nuevo, entradilla, puntos):
    estado = ('Nuevo, precintado de fábrica y 100&nbsp;% original de Apple.' if nuevo
              else 'Segunda mano, revisado y verificado: 100&nbsp;% funcional.')
    garantia = '3 años de garantía' if nuevo else '1 año de garantía'
    return (f'<p>{entradilla}</p><ul>' + ''.join(f'<li>{p}</li>' for p in puntos) + '</ul>'
            f'<p><strong>Estado:</strong> {estado}</p>'
            '<p><strong>Entrega:</strong> si el color y la capacidad que elige están en stock, sale en 24-48&nbsp;h; si no, en 3-5 días hábiles. Le avisamos por WhatsApp en cuanto salga.</p>'
            '<p><strong>Su compra en Pillatumovil incluye:</strong></p><ul>'
            f'<li>{garantia}</li><li>Envío gratis con seguimiento</li><li>14 días para devolverlo</li><li>Pago seguro y factura</li></ul>')

def color_ref(c):
    return ''.join(ch for ch in c.upper().replace(' ', '') if ch.isalnum()).replace('Ó', 'O')[:10]

def crear(handle):
    modelo, nuevo, entradilla, puntos, precios, excep, colores, portada, fotos, cod = M[handle]
    titulo = f'{modelo} nuevo' if nuevo else f'{modelo} de segunda mano'
    caps = list(precios)
    archivos, vistos = [], set()
    def foto(nombre, alt):
        if nombre in vistos: return
        vistos.add(nombre); archivos.append({'originalSource': CDN + nombre, 'alt': alt, 'contentType': 'IMAGE'})
    foto(portada, f'{modelo}: vista trasera, frontal y lateral')
    for c in colores: foto(fotos[c], f'{modelo} {c}')
    variantes = []
    for cap in caps:
        for c in colores:
            variantes.append({
                'optionValues': [{'optionName': 'Almacenamiento', 'name': cap}, {'optionName': 'Color', 'name': c}],
                'price': str(excep.get((cap, c), precios[cap])),
                'sku': f'IPH-{cod}-{cap.replace("GB", "")}-{color_ref(c)}',
                'inventoryPolicy': 'DENY',
                'inventoryItem': {'tracked': True},
                'inventoryQuantities': [{'locationId': UBICACION, 'name': 'available', 'quantity': UNIDADES}],
                'file': {'originalSource': CDN + fotos[c], 'alt': f'{modelo} {c}', 'contentType': 'IMAGE'},
            })
    estado_txt = 'nuevo y precintado' if nuevo else 'de segunda mano, revisado'
    entrada = {
        'handle': handle, 'title': titulo, 'vendor': 'Apple', 'productType': 'Smartphone', 'status': 'ACTIVE',
        'descriptionHtml': descripcion(modelo, nuevo, entradilla, puntos),
        'tags': ['apple', 'iphone', 'movil', handle.replace('-segunda-mano', ''), 'nuevo' if nuevo else 'segunda-mano'] + (['precintado'] if nuevo else []) + (['usb-c'] if any(x in modelo for x in ('15', '16', '17', '18')) else ['lightning']),
        'seo': {'title': f'{titulo} | Pillatumovil',
                'description': f'{modelo} {estado_txt}. Desde {min(precios.values())} €. Envío gratis, {"3 años" if nuevo else "1 año"} de garantía y 14 días para devolverlo.'},
        'productOptions': [{'name': 'Almacenamiento', 'values': [{'name': c} for c in caps]},
                           {'name': 'Color', 'values': [{'name': c} for c in colores]}],
        'files': archivos, 'variants': variantes,
    }
    d = gql('''mutation($i:ProductSetInput!,$id:ProductSetIdentifiers){ productSet(input:$i, identifier:$id, synchronous:true){
              product{ id handle title variantsCount{ count } } userErrors{ field message code } } }''',
            {'i': entrada, 'id': {'handle': handle}})
    r = d['productSet']
    if r['userErrors']: print('ERROR', handle, json.dumps(r['userErrors'], ensure_ascii=False)); return None
    p = r['product']
    g = gql('''mutation($id:ID!,$p:[PublicationInput!]!){ publishablePublish(id:$id, input:$p){ userErrors{ message } } }''',
            {'id': p['id'], 'p': [{'publicationId': TIENDA_ONLINE}]})
    print('ok', p['handle'], '·', p['title'], '·', p['variantsCount']['count'], 'variantes', g['publishablePublish']['userErrors'] or '')
    return p['id']

if __name__ == '__main__':
    for h in (sys.argv[1:] or list(M)): crear(h)
