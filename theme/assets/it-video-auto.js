/* Videos de la ficha de producto: se reproducen solos, sin sonido y en bucle
   en cuanto entran en pantalla, y se pausan al salir. Si el cliente los toca,
   se abren en grande con controles (sonido, pausa) como hasta ahora.

   En la galeria de Dawn el video solo es una foto de portada: el <video> real
   vive en un <template> y se carga al hacer clic. Aqui se clona ese video y
   se pone encima de la portada, en silencio y en bucle. */
(function () {
  if (window.__itVideoAuto) return; window.__itVideoAuto = true;

  function inline(li) {
    var v = li.querySelector('video.it-vauto');
    if (v) return v;
    var tpl = li.querySelector('deferred-media template, template');
    var src = tpl && tpl.content && tpl.content.querySelector('video');
    var box = li.querySelector('.product__media');
    if (!src || !box) return null;
    v = src.cloneNode(true);
    v.className = 'it-vauto';
    v.removeAttribute('controls');
    v.muted = true; v.setAttribute('muted', '');
    v.loop = true; v.setAttribute('loop', '');
    v.playsInline = true; v.setAttribute('playsinline', '');
    v.setAttribute('preload', 'metadata');
    v.setAttribute('aria-hidden', 'true');
    v.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;object-fit:cover;pointer-events:none;';
    box.appendChild(v);
    var ic = li.querySelector('.product__media-icon'); if (ic) ic.style.display = 'none';
    return v;
  }

  function play(v) { if (!v) return; v.muted = true; var p = v.play(); if (p && p.catch) p.catch(function () {}); }

  var io = 'IntersectionObserver' in window ? new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) play(inline(e.target));
      else { var v = e.target.querySelector('video.it-vauto'); if (v && !v.paused) v.pause(); }
    });
  }, { threshold: 0.5 }) : null;

  var seen = new WeakSet();
  function scan() {
    document.querySelectorAll('media-gallery li[data-media-id]').forEach(function (li) {
      if (seen.has(li)) return;
      var tpl = li.querySelector('template');
      if (!tpl || tpl.innerHTML.indexOf('<video') === -1) return;
      seen.add(li);
      if (io) io.observe(li); else play(inline(li));
    });
  }

  function boot() {
    scan();
    /* Dawn vuelve a pintar la galeria al cambiar de variante. */
    new MutationObserver(scan).observe(document.body, { childList: true, subtree: true });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
