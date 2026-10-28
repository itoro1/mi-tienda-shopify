/* Pone una etiqueta "−50 €" en el boton del color mas barato del selector de
   variantes. Lee el dato que deja snippets/price.liquid en .it-cheap-data, y
   como Dawn repinta el precio y el selector al cambiar de variante, se vuelve a
   aplicar con un MutationObserver. */
(function () {
  if (window.__itCheap) return; window.__itCheap = true;
  function apply() {
    var d = document.querySelector('.it-cheap-data');
    document.querySelectorAll('.it-cheap-pill').forEach(function (b) {
      if (!d || b.getAttribute('data-for') !== d.getAttribute('data-color')) b.remove();
    });
    if (!d) return;
    var color = d.getAttribute('data-color'), diff = d.getAttribute('data-diff');
    document.querySelectorAll('variant-selects input[type="radio"], variant-radios input[type="radio"]').forEach(function (inp) {
      if (inp.value !== color) return;
      var lab = document.querySelector('label[for="' + inp.id + '"]');
      if (!lab || lab.querySelector('.it-cheap-pill')) return;
      var s = document.createElement('span');
      s.className = 'it-cheap-pill'; s.setAttribute('data-for', color); s.textContent = diff;
      lab.appendChild(s);
    });
  }
  function boot() {
    apply();
    var t = null;
    new MutationObserver(function () { clearTimeout(t); t = setTimeout(apply, 60); })
      .observe(document.body, { childList: true, subtree: true });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
