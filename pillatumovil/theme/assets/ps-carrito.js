/* Pillatumovil: anadir al carrito sin salir de la pagina.

   Los formularios con data-ps-anadir (portada, colecciones, sugerencias
   del carrito) se envian por AJAX como lo hace la ficha de Dawn
   (assets/product-form.js) y abren el carrito lateral con lo que devuelve
   Shopify. Si no hay carrito lateral, fetch falla o Shopify responde con un
   error, el formulario se envia normal y lleva a la pagina del carrito. */
(function () {
  document.addEventListener('submit', function (e) {
    var form = e.target;
    if (!form.matches || !form.matches('form[data-ps-anadir]')) return;
    var cart = document.querySelector('cart-drawer');
    if (!cart || !window.fetch || !window.routes || typeof cart.renderContents !== 'function') return;
    e.preventDefault();

    var btn = form.querySelector('[type="submit"]');
    if (btn) { btn.disabled = true; btn.setAttribute('aria-busy', 'true'); }
    var viejo = form.querySelector('.ps-tar__error');
    if (viejo) viejo.remove();

    var datos = new FormData(form);
    datos.delete('return_to');
    datos.append('sections', cart.getSectionsToRender().map(function (s) { return s.id; }));
    datos.append('sections_url', window.location.pathname);

    fetch(window.routes.cart_add_url, {
      method: 'POST',
      headers: { 'X-Requested-With': 'XMLHttpRequest', Accept: 'application/javascript' },
      body: datos
    })
      .then(function (r) { return r.json(); })
      .then(function (res) {
        if (res.status) {
          var p = document.createElement('p');
          p.className = 'ps-tar__error';
          p.setAttribute('role', 'alert');
          p.textContent = res.description || res.message || 'No se ha podido añadir.';
          form.appendChild(p);
          return;
        }
        if (cart.classList.contains('is-empty')) cart.classList.remove('is-empty');
        cart.renderContents(res);
        // PUB_SUB_EVENTS es un const global de Dawn (constants.js), no cuelga de window.
        if (typeof publish === 'function' && typeof PUB_SUB_EVENTS !== 'undefined') publish(PUB_SUB_EVENTS.cartUpdate, { source: 'ps-carrito', cartData: res });
      })
      .catch(function () { form.submit(); })
      .finally(function () {
        if (btn) { btn.disabled = false; btn.removeAttribute('aria-busy'); }
      });
  });
})();
