/* Carrusel de valoraciones: flechas, puntos y teclado. */
(function () {
  function init(root) {
    if (root.dataset.itRevReady) return;
    root.dataset.itRevReady = '1';
    var track = root.querySelector('[data-it-track]');
    var prev = root.querySelector('[data-it-prev]');
    var next = root.querySelector('[data-it-next]');
    var dotsBox = root.querySelector('[data-it-dots]');
    if (!track) return;
    var cards = Array.prototype.slice.call(track.children);
    if (!cards.length) return;

    var dots = cards.map(function (card, i) {
      var d = document.createElement('button');
      d.type = 'button';
      d.className = 'it-rev__dot';
      d.setAttribute('aria-label', 'Ir a la valoracion ' + (i + 1));
      d.addEventListener('click', function () { scrollToCard(i); });
      if (dotsBox) dotsBox.appendChild(d);
      return d;
    });

    function step() {
      var w = cards[0].getBoundingClientRect().width;
      var gap = parseFloat(getComputedStyle(track).columnGap || '16') || 16;
      return w + gap;
    }
    function current() {
      return Math.round(track.scrollLeft / step());
    }
    function scrollToCard(i) {
      track.scrollTo({ left: i * step(), behavior: 'smooth' });
    }
    function sync() {
      var i = Math.max(0, Math.min(current(), cards.length - 1));
      dots.forEach(function (d, n) { d.setAttribute('aria-current', n === i ? 'true' : 'false'); });
      var max = track.scrollWidth - track.clientWidth - 2;
      if (prev) prev.disabled = track.scrollLeft <= 2;
      if (next) next.disabled = track.scrollLeft >= max;
    }

    if (prev) prev.addEventListener('click', function () { scrollToCard(Math.max(0, current() - 1)); });
    if (next) next.addEventListener('click', function () { scrollToCard(Math.min(cards.length - 1, current() + 1)); });
    track.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') { e.preventDefault(); scrollToCard(Math.min(cards.length - 1, current() + 1)); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); scrollToCard(Math.max(0, current() - 1)); }
    });

    var tick;
    track.addEventListener('scroll', function () {
      clearTimeout(tick);
      tick = setTimeout(sync, 60);
    }, { passive: true });
    window.addEventListener('resize', sync);
    sync();
  }

  function boot() {
    document.querySelectorAll('[data-it-rev]').forEach(init);
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
  document.addEventListener('shopify:section:load', boot);
})();
