/* Sello flotante con las valoraciones de Google y Wallapop.
   Los datos llegan en el <script type="application/json" id="it-tb-data">
   que escribe snippets/it-schema-org.liquid, para no repetir cifras aqui. */
(function () {
  var KEY = 'it_tb_hidden_until';
  var SVG = 'http://www.w3.org/2000/svg';

  function cfg() {
    var el = document.getElementById('it-tb-data');
    if (!el) return null;
    try { return JSON.parse(el.textContent); } catch (e) { return null; }
  }
  function hidden() {
    try {
      var v = localStorage.getItem(KEY);
      return v && Date.now() < parseInt(v, 10);
    } catch (e) { return false; }
  }
  function hide() {
    try { localStorage.setItem(KEY, String(Date.now() + 7 * 864e5)); } catch (e) {}
  }
  function stars(n, color) {
    var wrap = document.createElement('span');
    wrap.className = 'it-tb__stars';
    for (var i = 1; i <= 5; i++) {
      var s = document.createElementNS(SVG, 'svg');
      s.setAttribute('width', '11'); s.setAttribute('height', '11');
      s.setAttribute('viewBox', '0 0 24 24');
      s.setAttribute('fill', i <= Math.round(n) ? color : '#d6d6d6');
      var p = document.createElementNS(SVG, 'polygon');
      p.setAttribute('points', '12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2');
      s.appendChild(p); wrap.appendChild(s);
    }
    return wrap;
  }
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
    top.appendChild(stars(parseFloat(String(src.avg).replace(',', '.')), src.color));
    var score = document.createElement('span');
    score.className = 'it-tb__score';
    score.textContent = src.avg;
    top.appendChild(score);
    var count = document.createElement('span');
    count.className = 'it-tb__count';
    count.innerHTML = '<b>' + src.label + '</b> \u00b7 ' + src.count;
    meta.appendChild(top);
    meta.appendChild(count);

    r.appendChild(logo);
    r.appendChild(meta);
    r.setAttribute('aria-label', src.label + ': ' + src.avg + ' sobre 5, ' + src.count);
    return r;
  }

  function build(c) {
    var box = document.createElement('aside');
    box.className = 'it-tb';
    box.setAttribute('role', 'complementary');
    box.setAttribute('aria-label', 'Valoraciones de clientes');

    var head = document.createElement('div');
    head.className = 'it-tb__head';
    var eye = document.createElement('span');
    eye.className = 'it-tb__eyebrow';
    eye.textContent = 'Opiniones verificadas';
    var x = document.createElement('button');
    x.className = 'it-tb__x';
    x.type = 'button';
    x.setAttribute('aria-label', 'Cerrar');
    x.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12"/></svg>';
    x.addEventListener('click', function (e) {
      e.stopPropagation(); e.preventDefault();
      hide(); box.removeAttribute('data-show');
      setTimeout(function () { box.remove(); }, 350);
    });
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
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });

    box.appendChild(head); box.appendChild(rows);
    document.body.appendChild(box);
    setTimeout(function () { box.setAttribute('data-show', '1'); }, c.delay || 1200);
  }

  function boot() {
    if (hidden() || document.querySelector('.it-tb')) return;
    var c = cfg();
    if (c && c.sources && c.sources.length) build(c);
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else { boot(); }
})();
