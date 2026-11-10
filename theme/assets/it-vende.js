/* ITorostore · Vende tu iPhone (sections/it-vende.liquid). Vanilla.
   Pasos: 1 iPhone → 2 estado (calculado, no elegido) → 3 requisitos → 4 oferta.
   Precios en el JSON de la sección. Progreso en localStorage, sin datos
   personales. Atrás del navegador = paso anterior. */
(function () {
'use strict';

var raiz = document.querySelector('[data-itv]');
if (!raiz || raiz.getAttribute('data-itv-listo')) return;
raiz.setAttribute('data-itv-listo', '1');

/* == Configuración == */
var cfg = {};
try { cfg = JSON.parse(raiz.querySelector('[data-itv-cfg]').textContent); } catch (e) { cfg = {}; }
var MULT = (cfg.mult || [100, 92, 84, 75, 60, 40]).map(function (n) { return n / 100; });
var BAT = cfg.bat || [3, 6, 12];
var CAJA = +cfg.caja || 0, FACTURA = +cfg.factura || 0;
var WA = cfg.wa || '34624150603';
var CAPS = ['64 GB', '128 GB', '256 GB', '512 GB', '1 TB', '2 TB'];
var GRADOS = ['Precintado', 'Excelente', 'Muy bueno', 'Bueno', 'Aceptable', 'Con daños'];
var CLAVE = 'itv-tasacion-v1';
var MOV = !window.matchMedia || !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
function suave() { return MOV ? 'smooth' : 'auto'; }

/* Modelos: normalizados, ordenados y agrupados por generación. */
var MODELOS = (cfg.precios || []).filter(function (m) {
  return m && m.n && (m.p || []).some(function (v) { return v > 0; });
}).sort(function (a, b) { return (a.o || 99) - (b.o || 99); }).map(function (m) {
  var g = (m.n.match(/iphone\s*(\d+|x)/i) || [])[1] || 'Otros';
  return { n: m.n, p: m.p, g: g.toUpperCase(), k: norm(m.n) };
});
var GENS = [];
MODELOS.forEach(function (m) { if (GENS.indexOf(m.g) < 0) GENS.push(m.g); });

/* == Preguntas (textos en el JSON de la sección) == */
var Q = cfg.q || {};
var SELLADO = Q.sellado, ESTADO = Q.estado || [];
var REQ = (Q.req || []).filter(function (p) { return (p.k !== 'canje' || cfg.canje) && (p.k !== 'entrega' || cfg.mano); });

/* == Estado == */
function vacio() {
  return { v: 1, paso: 1, modelo: '', cap: -1, color: '', gen: '', r: {}, bat: '', batNs: false, ok: false, fotos: [] };
}
var st = vacio();
var ICO_CAM = '<svg class="itv-ico"><use href="#itv-i-camera"/></svg>';
var blobs = [];         /* fotos comprimidas: solo en memoria */
var empezado = false;   /* para el evento vende_inicio */

/* == Utilidades == */
function $(sel, ctx) { return (ctx || raiz).querySelector(sel); }
function $$(sel, ctx) { return Array.prototype.slice.call((ctx || raiz).querySelectorAll(sel)); }
function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return '&#' + c.charCodeAt(0) + ';'; }); }
function eur(n) { return String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, '.'); }
function norm(s) {
  return String(s).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '')
    .replace(/iphone|apple|\d+\s*gb/g, '').replace(/[^a-z0-9]/g, '')
    .replace(/pm$/, 'promax').replace(/pmax$/, 'promax');
}
function modelo() { return MODELOS.filter(function (m) { return m.n === st.modelo; })[0] || null; }
function maxDe(m) { return Math.max.apply(null, m.p.map(function (v) { return v || 0; })); }

function guardar() {
  try { localStorage.setItem(CLAVE, JSON.stringify(st)); } catch (e) { /* sin almacenamiento: seguimos igual */ }
}
function leer() {
  try { var d = JSON.parse(localStorage.getItem(CLAVE) || 'null'); return d && d.v === 1 ? d : null; } catch (e) { return null; }
}
function borrar() { try { localStorage.removeItem(CLAVE); } catch (e) {} }

/* gtag (GA4/Ads) y fbq (Meta) los carga la tienda. */
var META = { vende_inicio: 'VendeInicio', vende_precio_mostrado: 'VendePrecio', vende_whatsapp: 'Contact', vende_formulario: 'Lead' };
function medir(evento, extra) {
  var c = calcular();
  var d = { modelo: st.modelo || null, capacidad: st.cap >= 0 ? CAPS[st.cap] : null, value: c ? c.total : 0, currency: 'EUR' };
  for (var k in extra || {}) d[k] = extra[k];
  try { if (window.gtag) gtag('event', evento, d); } catch (e) {}
  try { var f = META[evento]; if (f && window.fbq) fbq(/^[A-Z][a-z]+$/.test(f) ? 'track' : 'trackCustom', f, { content_name: d.modelo, value: d.value, currency: 'EUR' }); } catch (e) {}
}
function inicio() {
  if (empezado) return;
  empezado = true;
  var r = $('[data-itv-resume]'); if (r) r.hidden = true;  /* empieza de cero: fuera el aviso */
  medir('vende_inicio');
}

/* == Cálculo del precio ==
   Nivel 0 = precintado … 5 = con daños. Lo que no se ha respondido no
   resta, por eso la cifra en vivo es siempre "hasta". */
function nivel() {
  var r = st.r;
  if (r.precintado !== 'no') return 0;
  var leves = (r.pantalla === 'leves') + (r.cuerpo === 'leves');
  var n = leves === 2 ? 3 : leves === 1 ? 2 : 1;
  if (r.cuerpo === 'golpes') n = Math.max(n, 4);
  if (r.piezas === 'si') n = Math.max(n, 3);
  if (r.pantalla === 'rota' || r.faceid === 'no' || r.camaras === 'no' || r.agua === 'si') n = 5;
  return n;
}
function descBateria() {
  var b = parseInt(st.bat, 10);
  if (st.r.precintado !== 'no' || st.batNs || !(b >= 1 && b <= 100)) return 0;
  return b >= 90 ? 0 : b >= 85 ? BAT[0] : b >= 80 ? BAT[1] : BAT[2];
}
function calcular() {
  var m = modelo();
  if (!m || st.cap < 0 || !m.p[st.cap]) return null;
  var base = m.p[st.cap], n = nivel();
  var trasEstado = Math.round(base * MULT[n]);
  var lineas = [[m.n + ' · ' + CAPS[st.cap] + ' (máximo)', base]];
  if (n > 0) lineas.push(['Estado calculado: ' + GRADOS[n], trasEstado - base]);
  var db = descBateria();
  if (db) lineas.push(['Batería al ' + parseInt(st.bat, 10) + ' %', -Math.round(trasEstado * db / 100)]);
  if (st.r.caja === 'si' && CAJA) lineas.push(['Caja original', CAJA]);
  if (st.r.factura === 'si' && FACTURA) lineas.push(['Factura de compra', FACTURA]);
  var total = lineas.reduce(function (s, l) { return s + l[1]; }, 0);
  return { base: base, nivel: n, lineas: lineas, total: Math.max(0, total) };
}

/* == Pintado: paso 1 == */
function pintarGens() {
  var g = st.gen || (modelo() || {}).g || GENS[0];
  $('[data-itv-gens]').innerHTML = GENS.map(function (x) {
    var on = x === g;
    return '<button type="button" role="tab" class="itv-gen" aria-selected="' + on + '" data-gen="' + esc(x) + '">' + (x === 'X' ? 'X / XR / XS' : esc(x)) + '</button>';
  }).join('');
}
function pintarModelos() {
  var q = norm($('[data-itv-q]').value || '');
  var gensEl = $('[data-itv-gens]'), cont = $('[data-itv-models]');
  var lista;
  if (q) {
    gensEl.hidden = true;
    lista = MODELOS.filter(function (m) { return m.k.indexOf(q) === 0 || (q.length > 2 && m.k.indexOf(q) > 0); })
      .sort(function (a, b) { return (b.k === q) - (a.k === q); });
  } else {
    gensEl.hidden = false;
    var g = st.gen || (modelo() || {}).g || GENS[0];
    lista = MODELOS.filter(function (m) { return m.g === g; });
  }
  if (!lista.length) {
    cont.innerHTML = '<div class="itv-empty"><p>No encontramos «' + esc($('[data-itv-q]').value.trim()) + '».</p><p>Prueba con «13 Pro» o «15 Pro Max», o <a href="https://wa.me/' + WA + '?text=' + encodeURIComponent('Hola, quiero vender mi iPhone y no lo encuentro en la web. Es un: ') + '" target="_blank" rel="noopener">escríbenos por WhatsApp</a>.</p></div>';
    return;
  }
  cont.innerHTML = '<div class="itv-mlist" role="radiogroup" aria-label="Modelo">' + lista.map(function (m) {
    var on = m.n === st.modelo;
    return '<label class="itv-model' + (on ? ' is-on' : '') + '"><input type="radio" name="itv-modelo" value="' + esc(m.n) + '"' + (on ? ' checked' : '') + '>' +
      '<svg class="itv-ico" aria-hidden="true"><use href="#itv-i-phone"/></svg><span class="itv-model__n">' + esc(m.n) + '</span>' +
      '<span class="itv-model__p">hasta ' + eur(maxDe(m)) + ' €</span></label>';
  }).join('') + '</div>';
}
function pintarCaps() {
  var m = modelo(), wrap = $('[data-itv-caps-wrap]');
  wrap.hidden = !m;
  if (!m) return;
  $('[data-itv-caps]').innerHTML = m.p.map(function (v, i) {
    if (!v) return '';
    var on = i === st.cap;
    return '<label class="itv-cap' + (on ? ' is-on' : '') + '"><input type="radio" name="itv-cap" value="' + i + '"' + (on ? ' checked' : '') + '>' +
      '<b>' + CAPS[i] + '</b><small>hasta ' + eur(v) + ' €</small></label>';
  }).join('');
  $('[data-itv-color]').value = st.color;
}

/* == Pintado: preguntas (pasos 2 y 3) == */
function grupo(p) {
  var sel = st.r[p.k];
  return '<fieldset class="itv-q" data-q="' + p.k + '"><legend class="itv-q__t">' + esc(p.t) + '</legend>' +
    (p.a ? '<p class="itv-q__a">' + esc(p.a) + '</p>' : '') +
    '<div class="itv-opts itv-opts--' + p.o.length + '">' + p.o.map(function (o) {
      return '<label class="itv-opt' + (sel === o[0] ? ' is-on' : '') + '"><input type="radio" name="itv-' + p.k + '" value="' + o[0] + '"' + (sel === o[0] ? ' checked' : '') + '><span>' + esc(o[1]) + '</span></label>';
    }).join('') + '</div><p class="itv-err" hidden></p></fieldset>';
}
function pintarEstado() {
  $('[data-itv-sellado]').innerHTML = grupo(SELLADO);
  $('[data-itv-usado]').hidden = st.r.precintado !== 'no';
  $('[data-itv-estado-a]').innerHTML = grupo(ESTADO[0]);
  $('[data-itv-estado-b]').innerHTML = ESTADO.slice(1).map(grupo).join('');
  var bat = $('[data-itv-bat]');
  bat.value = st.bat; bat.disabled = st.batNs;
  $('[data-itv-batns]').checked = st.batNs;
}
function pintarReq() {
  $('[data-itv-req]').innerHTML = REQ.map(function (p) {
    if (p.k === 'cobro' && st.r.canje === 'canje') return '';
    return grupo(p);
  }).join('') + (st.r.icloud === 'no' ? '<p class="itv-warn itv-warn--in">Puedes seguir, pero tendrás que desactivarlo antes de enviárnoslo.</p>' : '');
  $('[data-itv-ok]').checked = !!st.ok;
}

/* == Precio en vivo == */
var ultimoVivo = null;
function pintarVivo() {
  var m = modelo(), live = $('[data-itv-live]');
  var c = calcular();
  var valor = c ? c.total + (st.r.caja ? 0 : CAJA) + (st.r.factura ? 0 : FACTURA) : m ? maxDe(m) + CAJA + FACTURA : null;
  var visible = valor !== null && st.paso < 4;
  live.hidden = !visible;
  document.body.classList.toggle('itv-bar-on', visible);
  if (!visible) return;
  $('[data-itv-live-p]').textContent = eur(valor);
  $('[data-itv-live-m]').textContent = st.modelo + (st.cap >= 0 ? ' · ' + CAPS[st.cap] : '');
  if (ultimoVivo !== null && ultimoVivo !== valor && MOV) {
    var p = $('.itv-live__p');
    p.classList.remove('is-tick'); void p.offsetWidth; p.classList.add('is-tick');
  }
  ultimoVivo = valor;
}

/* == Validación == */
function marcar(clave, msg) {
  var fs = $('[data-q="' + clave + '"]');
  if (!fs) return null;
  var e = $('.itv-err', fs);
  e.hidden = !msg; e.textContent = msg || '';
  fs.classList.toggle('is-bad', !!msg);
  return msg ? fs : null;
}
function validar(paso) {
  var malos = [];
  function req(clave, ok, msg) { var f = marcar(clave, ok ? '' : msg); if (f) malos.push(f); }
  if (paso === 1) {
    req('modelo', !!st.modelo, 'Elige tu modelo para seguir.');
    if (st.modelo) req('cap', st.cap >= 0, 'Elige la capacidad.');
  }
  if (paso === 2) {
    req('precintado', !!st.r.precintado, 'Dinos si está precintado.');
    if (st.r.precintado === 'no') {
      ESTADO.forEach(function (p) { req(p.k, !!st.r[p.k], 'Elige una opción.'); });
      var b = parseInt(st.bat, 10);
      req('bat', st.batNs || (/^\d{1,3}$/.test(st.bat) && b >= 1 && b <= 100), 'Escribe un número del 1 al 100, o marca «No lo sé».');
    }
  }
  if (paso === 3) {
    REQ.forEach(function (p) {
      if (p.k === 'cobro' && st.r.canje === 'canje') return;
      req(p.k, !!st.r[p.k], 'Elige una opción.');
    });
    req('ok', st.ok, 'Necesitamos que lo confirmes para poder comprarlo.');
  }
  malos.sort(function (a, b) { return a.compareDocumentPosition(b) & 2 ? 1 : -1; });
  if (malos[0]) {
    malos[0].scrollIntoView({ behavior: suave(), block: 'center' });
    var foco = malos[0].querySelector('input:not([disabled])');
    if (foco) foco.focus({ preventScroll: true });
  }
  return !malos.length;
}
/* == Navegación entre pasos == */
var TITULOS = ['Tu iPhone', 'Su estado', 'Requisitos y entrega', 'Tu oferta'];
function ir(n, apilar) {
  if (n > st.paso) {
    for (var p = st.paso; p < n; p++) { if (!validar(p)) return; }
  }
  var antes = st.paso;
  st.paso = n;
  pintarPaso(antes !== n);
  if (apilar && antes !== n) { try { history.pushState({ itv: n }, ''); } catch (e) {} }
  guardar();
  if (antes !== n) medir('vende_paso', { paso: n });
  if (n === 4 && antes !== 4) medir('vende_precio_mostrado');
}
function pintarPaso(animar) {
  var n = st.paso;
  $('[data-itv-app]').setAttribute('data-paso', n);
  $$('.itv-step').forEach(function (el) {
    var on = +el.getAttribute('data-step') === n;
    el.hidden = !on;
    if (on && animar && MOV) { el.classList.remove('is-in'); void el.offsetWidth; el.classList.add('is-in'); }
  });
  var bar = $('.itv-prog__bar');
  bar.setAttribute('aria-valuenow', Math.min(n, 3));
  bar.style.setProperty('--itv-prog', (n >= 4 ? 100 : (n - 1) / 3 * 100 + 12) + '%');
  $('[data-itv-prog]').hidden = n >= 4;
  $('[data-itv-prog-n]').textContent = Math.min(n, 3);
  $('[data-itv-prog-t]').textContent = TITULOS[n - 1];
  if (n === 1) { pintarGens(); pintarModelos(); pintarCaps(); }
  if (n === 2) pintarEstado();
  if (n === 3) pintarReq();
  if (n === 4) pintarResultado(animar);
  pintarVivo();
  if (animar) {
    var h = $('.itv-step[data-step="' + n + '"] [tabindex="-1"]');
    var top = $('[data-itv-app]').getBoundingClientRect().top;
    if (top < 0 || top > window.innerHeight * 0.6) $('[data-itv-app]').scrollIntoView({ behavior: suave(), block: 'start' });
    if (h) h.focus({ preventScroll: true });
  }
}

/* == Resultado == */
function txt(lista, clave) {
  var p = lista.filter(function (x) { return x.k === clave; })[0];
  var o = p && p.o.filter(function (x) { return x[0] === st.r[clave]; })[0];
  return o ? o[1] : 'sin indicar';
}
function informe(c) {
  var L = ['Hola, quiero vender mi iPhone. Esta es mi tasación de itorostore.com:', ''];
  L.push('*Modelo:* ' + st.modelo + ' · ' + CAPS[st.cap] + (st.color ? ' · ' + st.color : ''));
  L.push('*Estado calculado:* ' + GRADOS[c.nivel]);
  if (st.r.precintado === 'no') {
    ESTADO.forEach(function (p) { L.push('- ' + p.t.replace(/[¿?]/g, '') + ': ' + txt(ESTADO, p.k)); });
    L.push('*Batería:* ' + (st.batNs ? 'no lo sé' : parseInt(st.bat, 10) + ' %'));
  }
  L.push('', '*Requisitos y entrega:*');
  REQ.forEach(function (p) {
    if (p.k === 'cobro' && st.r.canje === 'canje') return;
    L.push('- ' + p.t.replace(/[¿?«»]/g, '') + ': ' + txt(REQ, p.k));
  });
  if (!cfg.mano) L.push('- Entrega: recogida gratis con Correos');
  L.push('- Mayor de edad, iPhone propio y DNI: confirmado');
  L.push('', '*Desglose:*');
  c.lineas.forEach(function (l) { L.push('- ' + l[0] + ': ' + (l[1] > 0 && l !== c.lineas[0] ? '+' : '') + eur(l[1]) + ' €'); });
  L.push('*Oferta orientativa: ' + eur(c.total) + ' €* (a falta de revisar el iPhone)');
  if (raiz.querySelector('[data-itv-fotos]')) L.push('', 'Ahora te adjunto las 6 fotos.');
  return L.join('\n');
}
function pintarResultado(animar) {
  var c = calcular();
  if (!c) { st.paso = 1; pintarPaso(false); return; }
  $('[data-itv-res-model]').textContent = st.modelo + ' · ' + CAPS[st.cap] + (st.color ? ' · ' + st.color : '') + ' · ' + GRADOS[c.nivel];
  $('[data-itv-break]').innerHTML = c.lineas.map(function (l, i) {
    var signo = i === 0 ? '' : l[1] > 0 ? '+' : l[1] < 0 ? '−' : '';
    return '<li><span>' + esc(l[0]) + '</span><b>' + signo + eur(Math.abs(l[1])) + ' €</b></li>';
  }).join('') + '<li class="itv-break__t"><span>Oferta orientativa</span><b>' + eur(c.total) + ' €</b></li>';
  $('[data-itv-icloud]').hidden = st.r.icloud !== 'no';
  var texto = informe(c);
  $('[data-itv-wa]').href = 'https://wa.me/' + WA + '?text=' + encodeURIComponent(texto);
  var body = $('[data-itv-body]');
  if (body) body.value = texto.replace(/\*/g, '');
  pintarFotos();
  contar(c.total, animar);
}
/* El momento memorable: la cifra sube hasta la oferta. */
function contar(total, animar) {
  var el = $('[data-itv-total]');
  if (!animar || !MOV || !window.requestAnimationFrame) { el.textContent = eur(total); return; }
  var t0 = null, dur = 900;
  $('.itv-offer').classList.remove('is-reveal'); void el.offsetWidth; $('.itv-offer').classList.add('is-reveal');
  function paso(t) {
    if (!t0) t0 = t;
    var k = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - k, 3);
    el.textContent = eur(total * e);
    if (k < 1) requestAnimationFrame(paso);
  }
  requestAnimationFrame(paso);
}

/* == Fotos guiadas == */
function pintarFotos() {
  var ol = $('[data-itv-fotos]');
  if (!ol) return;
  $$('[data-itv-fok]').forEach(function (cb) { cb.checked = !!st.fotos[+cb.getAttribute('data-itv-fok')]; });
  var n = st.fotos.filter(Boolean).length;
  $('[data-itv-fotos-n]').textContent = n + ' de 6 hechas';
  var sh = $('[data-itv-share]');
  if (sh) sh.hidden = !(blobs.filter(Boolean).length && navigator.canShare);
}
function comprimir(file) {
  return new Promise(function (ok) {
    var img = new Image(), url = URL.createObjectURL(file);
    img.onload = function () {
      var k = Math.min(1, 1600 / Math.max(img.naturalWidth, img.naturalHeight));
      var cv = document.createElement('canvas');
      cv.width = Math.round(img.naturalWidth * k); cv.height = Math.round(img.naturalHeight * k);
      cv.getContext('2d').drawImage(img, 0, 0, cv.width, cv.height);
      URL.revokeObjectURL(url);
      cv.toBlob(function (b) { ok(b || file); }, 'image/jpeg', 0.82);
    };
    img.onerror = function () { URL.revokeObjectURL(url); ok(file); };  /* p. ej. HEIC en Chrome */
    img.src = url;
  });
}
function ponerFoto(i, file) {
  var li = $('[data-foto="' + i + '"]'), th = $('.itv-foto__th', li);
  comprimir(file).then(function (b) {
    blobs[i] = b;
    th.innerHTML = '<img alt="" src="' + URL.createObjectURL(b) + '">';
    li.classList.add('is-on');
    st.fotos[i] = true; guardar(); pintarFotos();
  });
}
function compartir() {
  var files = blobs.map(function (b, i) { return b && new File([b], 'iphone-' + (i + 1) + '.jpg', { type: b.type || 'image/jpeg' }); }).filter(Boolean);
  if (!files.length || !navigator.canShare || !navigator.canShare({ files: files })) return;
  navigator.share({ files: files }).catch(function () {});
}

/* == Formulario de recogida == */
function enviarForm(e) {
  var f = e.target;
  e.preventDefault();
  var err = $('[data-itv-form-err]'), btn = $('[data-itv-submit]');
  err.hidden = true;
  if (!f.checkValidity()) {
    var malo = f.querySelector(':invalid');
    err.textContent = malo && malo.type === 'checkbox' ? 'Marca la casilla de privacidad para enviarlo.' : 'Revisa el campo marcado: falta o no es válido.';
    err.hidden = false; if (malo) malo.focus();
    return;
  }
  btn.disabled = true; btn.textContent = 'Enviando…';
  fetch(f.action, { method: 'POST', body: new FormData(f) }).then(function (r) {
    if (/challenge/.test(r.url)) { f.submit(); return; }   /* Shopify pide captcha: envío normal */
    if (!r.ok || !/contact_posted=true|posted_successfully/.test(r.url)) throw new Error('envio');
    $('[data-itv-formbox]').innerHTML = '<p class="itv-ok" role="status">Solicitud enviada. Te escribimos en breve para confirmar la oferta y la recogida.</p>';
    medir('vende_formulario');
  }).catch(function () {
    btn.disabled = false; btn.textContent = 'Enviar solicitud';
    err.innerHTML = 'No se ha podido enviar. Inténtalo otra vez o <a href="' + $('[data-itv-wa]').href + '" target="_blank" rel="noopener">mándalo por WhatsApp</a>.';
    err.hidden = false;
  });
}

/* == Eventos == */
raiz.addEventListener('click', function (e) {
  var t = e.target.closest('button, a');
  if (!t || !raiz.contains(t)) return;
  if (t.hasAttribute('data-gen')) {
    st.gen = t.getAttribute('data-gen'); pintarGens(); pintarModelos(); inicio(); return;
  }
  if (t.hasAttribute('data-itv-go')) { inicio(); ir(+t.getAttribute('data-itv-go'), true); return; }
  if (t.hasAttribute('data-itv-back')) {
    if (history.state && history.state.itv > 1) history.back(); else ir(Math.max(1, st.paso - 1), false);
    return;
  }
  if (t.hasAttribute('data-itv-wa')) { medir('vende_whatsapp'); return; }
  if (t.hasAttribute('data-itv-form-open')) {
    var box = $('[data-itv-formbox]'); box.hidden = !box.hidden;
    t.setAttribute('aria-expanded', !box.hidden);
    if (!box.hidden) { box.scrollIntoView({ behavior: suave(), block: 'start' }); var i = $('input:not([type=hidden])', box); if (i) i.focus({ preventScroll: true }); }
    return;
  }
  if (t.hasAttribute('data-itv-share')) { compartir(); return; }
  if (t.hasAttribute('data-itv-reset')) { borrar(); st = vacio(); blobs = []; $$('.itv-foto').forEach(function (li) { li.classList.remove('is-on'); $('.itv-foto__th', li).innerHTML = ICO_CAM; }); $('[data-itv-q]').value = ''; ir(1, true); return; }
  if (t.hasAttribute('data-itv-resume-ok')) { reanudar(); return; }
  if (t.hasAttribute('data-itv-resume-no')) { borrar(); $('[data-itv-resume]').hidden = true; return; }
});

raiz.addEventListener('change', function (e) {
  var t = e.target, n = t.name || '';
  inicio();
  if (n === 'itv-modelo') {
    st.modelo = t.value; st.cap = -1; st.gen = (modelo() || {}).g || st.gen;
    var mm = modelo(); var caps = mm ? mm.p.filter(Boolean) : [];
    if (caps.length === 1) st.cap = mm.p.indexOf(caps[0]);  /* una sola capacidad: elegida */
    $$('.itv-model').forEach(function (l) { l.classList.toggle('is-on', l.contains(t)); });
    marcar('modelo', '');
    pintarCaps();
    var w = $('[data-itv-caps-wrap]');
    if (w.getBoundingClientRect().top > window.innerHeight - 140) w.scrollIntoView({ behavior: suave(), block: 'center' });
  } else if (n === 'itv-cap') {
    st.cap = +t.value; marcar('cap', '');
    $$('.itv-cap').forEach(function (l) { l.classList.toggle('is-on', l.contains(t)); });
  } else if (n.indexOf('itv-') === 0 && t.type === 'radio') {
    var k = n.slice(4);
    st.r[k] = t.value; marcar(k, '');
    $$('input[name="' + n + '"]').forEach(function (i) { i.parentNode.classList.toggle('is-on', i.checked); });
    if (k === 'precintado') pintarEstado();
    if (k === 'icloud' || k === 'canje') pintarReq();
  } else if (t.hasAttribute('data-itv-batns')) {
    st.batNs = t.checked; var b = $('[data-itv-bat]'); b.disabled = t.checked; marcar('bat', '');
  } else if (t.hasAttribute('data-itv-ok')) {
    st.ok = t.checked; marcar('ok', '');
  } else if (t.hasAttribute('data-itv-file')) {
    if (t.files && t.files[0]) ponerFoto(+t.getAttribute('data-itv-file'), t.files[0]);
    return;
  } else if (t.hasAttribute('data-itv-fok')) {
    st.fotos[+t.getAttribute('data-itv-fok')] = t.checked; pintarFotos();
  }
  guardar(); pintarVivo();
});

raiz.addEventListener('input', function (e) {
  var t = e.target;
  if (t.hasAttribute('data-itv-q')) { inicio(); pintarModelos(); }
  else if (t.hasAttribute('data-itv-color')) { st.color = t.value.trim().slice(0, 40); guardar(); }
  else if (t.hasAttribute('data-itv-bat')) {
    t.value = t.value.replace(/\D/g, '').slice(0, 3);
    st.bat = t.value; marcar('bat', ''); guardar(); pintarVivo();
  }
});

/* Intro: si queda un modelo, se elige. */
raiz.addEventListener('keydown', function (e) {
  if (e.key === 'Enter' && e.target.hasAttribute('data-itv-q')) {
    e.preventDefault();
    var r = $$('[name="itv-modelo"]');
    if (r.length === 1) { r[0].checked = true; r[0].dispatchEvent(new Event('change', { bubbles: true })); }
  }
});

var form = document.getElementById('itv-form');
if (form) form.addEventListener('submit', enviarForm);

window.addEventListener('popstate', function (e) {
  var n = e.state && e.state.itv ? e.state.itv : 1;
  if (n !== st.paso) { st.paso = Math.min(n, st.paso); pintarPaso(true); guardar(); }
});

/* == Arranque == */
function reanudar() {
  var d = leer();
  $('[data-itv-resume]').hidden = true;
  if (!d) return;
  st = Object.assign(vacio(), d);
  if (!calcular() && st.paso > 1) st.paso = 1;
  try { history.replaceState({ itv: 1 }, ''); if (st.paso > 1) history.pushState({ itv: st.paso }, ''); } catch (e) {}
  pintarPaso(true);
}

if (!MODELOS.length) {
  $('[data-itv-sinprecios]').hidden = false;
  return;
}
try { history.replaceState({ itv: 1 }, ''); } catch (e) {}
pintarPaso(false);

var previo = leer();
if (previo && previo.modelo) {
  if (/contact_posted=true/.test(location.search)) {
    reanudar();                                  /* vuelve de un envío normal del formulario */
    var bx = $('[data-itv-formbox]');
    if (bx) { bx.hidden = false; }
  } else {
    $('[data-itv-resume-txt]').textContent = 'Continuar tasación de tu ' + previo.modelo + '.';
    $('[data-itv-resume]').hidden = false;
  }
}
})();
