/* Videos de la ficha de producto: se reproducen solos, sin sonido y en bucle
   en cuanto entran en pantalla, y se pausan al salir. El cliente puede
   tocarlos para verlos con controles o pararlos.

   Dawn guarda cada video dentro de <deferred-media> y solo lo carga al hacer
   clic. Aqui se carga con loadContent(false) (sin robar el foco) cuando el
   video es visible. */
(function () {
  if (window.__itVideoAuto) return; window.__itVideoAuto = true;

  function prep(v) {
    v.muted = true; v.setAttribute('muted', '');
    v.loop = true; v.setAttribute('loop', '');
    v.playsInline = true; v.setAttribute('playsinline', '');
    v.autoplay = true; v.setAttribute('autoplay', '');
  }
  function play(v) { prep(v); var p = v.play(); if (p && p.catch) p.catch(function () {}); }

  function videoOf(dm) {
    var v = dm.querySelector('video');
    if (!v && typeof dm.loadContent === 'function') {
      try { dm.loadContent(false); } catch (e) {}
      v = dm.querySelector('video');
    }
    return v;
  }

  function visible(el) {
    var li = el.closest('li, .product__media-item');
    if (li && getComputedStyle(li).display === 'none') return false;
    return true;
  }

  var io = 'IntersectionObserver' in window ? new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      var dm = e.target;
      if (e.isIntersecting && visible(dm)) {
        var v = videoOf(dm); if (v) play(v);
      } else {
        var v2 = dm.querySelector('video'); if (v2 && !v2.paused) v2.pause();
      }
    });
  }, { threshold: 0.5 }) : null;

  var seen = new WeakSet();
  function scan() {
    document.querySelectorAll('media-gallery deferred-media').forEach(function (dm) {
      if (seen.has(dm)) return;
      var tpl = dm.querySelector('template');
      var isVideo = dm.querySelector('video') || (tpl && tpl.innerHTML.indexOf('<video') !== -1);
      if (!isVideo) return;
      seen.add(dm);
      if (io) io.observe(dm); else { var v = videoOf(dm); if (v) play(v); }
    });
  }

  function boot() {
    scan();
    // Dawn vuelve a pintar la galeria al cambiar de variante.
    new MutationObserver(scan).observe(document.body, { childList: true, subtree: true });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
