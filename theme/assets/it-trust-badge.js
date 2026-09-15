/* Sello flotante con las valoraciones de Google y Wallapop.
   Los datos llegan en el <script type="application/json" id="it-tb-data">
   que escribe snippets/it-schema-org.liquid, para no repetir cifras aqui.

   Arranca plegado en una pildora pequena. Se despliega al tocarla y la X
   vuelve a plegarlo. Se recuerda el estado por visitante, nada mas.

   La clave de localStorage cambio de "it_tb_hidden_until" a "it_tb_state" a
   proposito: la version anterior escondia el sello siete dias en todo el
   sitio a quien pulsara la X una vez, y esa marca seguia viva en el
   navegador. Con la clave nueva ya no cuenta. */
(function () {
  var KEY = 'it_tb_state';
  var SVG = 'http://www.w3.org/2000/svg';

  function cfg() {
    var el = document.getElementById('it-tb-data');
    if (!el) return null;
    try { return JSON.parse(el.textContent); } catch (e) { return null; }
  }
  function remember(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }
  function recall() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }

  function stars(n, color, size) {
    var wrap = document.createElement('span');
    wrap.className = 'it-tb__stars';
    for (var i = 1; i <= 5; i++) {
      var s = document.createElementNS(SVG, 'svg');
      s.setAttribute('width', size); s.setAttribute('height', size);
      s.setAttribute('viewBox', '0 0 24 24');
      s.setAttribute('fill', i <= Math.round(n) ? color : '#d6d6d6');
      var p = document.createElementNS(SVG, 'polygon');
      p.setAttribute('points', '12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2');
      s.appendChild(p); wrap.appendChild(s);
    }
    return wrap;
  }
  function num(v) { return parseFloat(String(v).replace(',', '.')); }

  function row(src) {
    var r = document.createElement('div');
    r.className = 'it-tb__row';
    var logo = document.createElement('span');
    logo.className = 'it-tb__logo';
    logo.innerHTML = src.logo;
    var meta = document.createElement('span');
    meta.className = 'it-tb__meta';
    var top = document.createElement('span');
    top.className = 'it-tb__top';
    top.appendChild(stars(num(src.avg), src.color, '11'));
    var score = document.createElement('span');
    score.className = 'it-tb__score';
    score.textContent = src.avg;
    top.appendChild(score);
    var count = document.createElement('span');
    count.className = 'it-tb__count';
    count.innerHTML = '<b>' + src.label + '</b> · ' + src.count;
    meta.appendChild(top); meta.appendChild(count);
    r.appendChild(logo); r.appendChild(meta);
    r.setAttribute('aria-label', src.label + ': ' + src.avg + ' sobre 5, ' + src.count);
    return r;
  }

  /* La pildora resume las dos fuentes en una sola cifra: la nota mas alta y
     la suma de opiniones. Nada inventado, todo sale del JSON.

     Se devuelven las dos formas de la nota a proposito. "avg" es para leerla
     ("4,9", con coma, como se escribe en espanol) y "num" para calcular. Si se
     le pasa la cadena a stars(), Math.round('4,9') da NaN y las cinco estrellas
     salen grises: es justo el fallo que se veia en la pildora cerrada. */
  function summary(sources) {
    var best = 0, total = 0;
    sources.forEach(function (s) {
      var a = num(s.avg);
      if (a > best) best = a;
      var n = parseInt(String(s.count).replace(/\D/g, ''), 10);
      if (n) total += n;
    });
    return { avg: String(best).replace('.', ','), num: best, total: total };
  }

  function build(c) {
    var sum = summary(c.sources);
    var box = document.createElement('aside');
    box.className = 'it-tb';
    box.setAttribute('aria-label', 'Valoraciones de clientes');

    var pill = document.createElement('button');
    pill.type = 'button';
    pill.className = 'it-tb__pill';
    pill.setAttribute('aria-expanded', 'false');
    pill.appendChild(stars(sum.num, '#fbbc05', '10'));
    var b = document.createElement('b');
    b.textContent = sum.avg;
    var sp = document.createElement('span');
    sp.textContent = sum.total + ' opiniones';
    pill.appendChild(b); pill.appendChild(sp);
    pill.setAttribute('aria-label', sum.avg + ' sobre 5 en ' + sum.total + ' opiniones. Ver detalle.');

    var card = document.createElement('div');
    card.className = 'it-tb__card';
    var head = document.createElement('div');
    head.className = 'it-tb__head';
    var eye = document.createElement('span');
    eye.className = 'it-tb__eyebrow';
    eye.textContent = 'Opiniones verificadas';
    var x = document.createElement('button');
    x.type = 'button';
    x.className = 'it-tb__x';
    x.setAttribute('aria-label', 'Plegar');
    x.innerHTML = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12"/></svg>';
    head.appendChild(eye); head.appendChild(x);

    var rows = document.createElement('a');
    rows.className = 'it-tb__rows';
    rows.href = c.anchor || '/';
    c.sources.forEach(function (s) { rows.appendChild(row(s)); });
    var foot = document.createElement('span');
    foot.className = 'it-tb__foot';
    foot.textContent = 'Ver lo que dicen los clientes →';
    rows.appendChild(foot);
    rows.addEventListener('click', function (e) {
      var target = document.querySelector('.it-rev');
      if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
    });

    card.appendChild(head); card.appendChild(rows);
    box.appendChild(pill); box.appendChild(card);

    function open() { box.setAttribute('data-open', '1'); pill.setAttribute('aria-expanded', 'true'); remember('open'); }
    function close() { box.removeAttribute('data-open'); pill.setAttribute('aria-expanded', 'false'); remember('pill'); }
    pill.addEventListener('click', open);
    x.addEventListener('click', function (e) { e.stopPropagation(); e.preventDefault(); close(); });
    document.addEventListener('click', function (e) {
      if (box.hasAttribute('data-open') && !box.contains(e.target)) close();
    });
    if (recall() === 'open') open();

    document.body.appendChild(box);
    setTimeout(function () { box.setAttribute('data-show', '1'); }, c.delay || 1200);
  }

  function boot() {
    if (document.querySelector('.it-tb')) return;
    var c = cfg();
    if (c && c.sources && c.sources.length) build(c);
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else { boot(); }
})();
