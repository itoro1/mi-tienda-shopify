/* Fotos reales por variante.

   El metacampo de producto custom.fotos_reales dice que fotos son de una unidad
   concreta: {"<id variante>": ["<id media>", ...]}. En la ficha:
   - con esa variante elegida se ven SOLO sus fotos reales;
   - con cualquier otra variante, esas fotos se esconden y se ve la galeria
     estandar.
   Lo pinta snippets/price.liquid; aqui solo se aplica, y se vuelve a aplicar
   cada vez que cambia la variante. */
(function () {
  if (window.__itFotos) return; window.__itFotos = true;
  var last = null;
  function data() {
    var el = document.querySelector('script.it-fotos-data');
    if (!el) return null;
    try { return JSON.parse(el.textContent); } catch (e) { return null; }
  }
  function variantId() {
    var i = document.querySelector('product-info form[action$="/cart/add"] input[name="id"], form[action$="/cart/add"] input[name="id"]');
    if (i && i.value) return String(i.value);
    return new URLSearchParams(location.search).get('variant');
  }
  function mediaOf(el) {
    var v = el.getAttribute('data-media-id') || el.getAttribute('data-target') || '';
    var m = v.match(/(\d+)$/); return m ? m[1] : null;
  }
  function apply(force) {
    var map = data(); if (!map) return;
    var vid = variantId(); if (!vid || (vid === last && !force)) return;
    last = vid;
    var mine = map[vid] || [], all = [];
    Object.keys(map).forEach(function (k) { all = all.concat(map[k]); });
    var firstShown = null;
    document.querySelectorAll('media-gallery [data-media-id], media-gallery [data-target], product-modal [data-media-id]').forEach(function (el) {
      var id = mediaOf(el); if (!id) return;
      var hide = mine.length ? mine.indexOf(id) === -1 : all.indexOf(id) !== -1;
      el.classList.toggle('it-foto-off', hide);
      if (!hide && !firstShown && el.matches('media-gallery [data-media-id]')) firstShown = el;
    });
    var g = document.querySelector('media-gallery');
    var active = g && g.querySelector('[data-media-id].is-active');
    if (g && firstShown && (!active || active.classList.contains('it-foto-off')) && g.setActiveMedia) {
      try { g.setActiveMedia(firstShown.getAttribute('data-media-id'), false); } catch (e) {}
    }
    document.querySelectorAll('media-gallery slider-component').forEach(function (s) {
      try { s.initPages && s.initPages(); s.update && s.update(); } catch (e) {}
    });
  }
  var st = document.createElement('style');
  st.textContent = '.it-foto-off{display:none!important}';
  document.head.appendChild(st);
  function boot() { apply(true); setInterval(function () { apply(false); }, 350); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
