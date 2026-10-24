/* Pillatumovil — portada cinematografica.

   [data-pt-caja]     Caja 3D que se gira arrastrando, con flechas o con los
                      botones [data-pt-girar]. Entra con un giro de camara.
   [data-pt-historia] Historia que avanza con el scroll: pone --p (0..1) en
                      la seccion, marca el capitulo activo y mueve la bateria.

   Sin dependencias. Con "reducir movimiento" no hay giros automaticos ni
   animaciones ligadas al scroll: todo se queda quieto y legible. */
(function () {
  'use strict';
  var quieto = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- Caja 3D ---------- */
  function caja(stage) {
    var box = stage.querySelector('.pt-box');
    if (!box) return;
    var ry = quieto ? -24 : -62, rx = -8, vy = 0, arrastrando = false, x0 = 0, y0 = 0, ultimo = 0;
    var objetivo = null, reposo = !quieto;

    function pintar() { box.style.transform = 'rotateX(' + rx + 'deg) rotateY(' + ry + 'deg)'; }
    pintar();

    function animar(t) {
      if (!arrastrando) {
        if (objetivo !== null) {
          var d = objetivo - ry;
          ry += d * 0.09;
          if (Math.abs(d) < 0.2) { ry = objetivo; objetivo = null; }
        } else if (Math.abs(vy) > 0.01) {
          ry += vy; vy *= 0.94;
        } else if (reposo) {
          ry += Math.sin(t / 2600) * 0.06; // balanceo muy lento en reposo
        }
        rx += (-8 - rx) * 0.06;
      }
      pintar();
      requestAnimationFrame(animar);
    }

    // Entrada de camara: de perfil y a oscuras a tres cuartos e iluminada.
    if (!quieto) {
      stage.classList.add('is-entrando');
      setTimeout(function () { objetivo = -24; }, 350);
      setTimeout(function () { stage.classList.remove('is-entrando'); }, 2600);
    }
    requestAnimationFrame(animar);

    stage.addEventListener('pointerdown', function (e) {
      arrastrando = true; reposo = false; objetivo = null;
      x0 = e.clientX; y0 = e.clientY; ultimo = e.clientX;
      stage.setPointerCapture(e.pointerId);
      stage.classList.add('is-girando');
    });
    stage.addEventListener('pointermove', function (e) {
      if (!arrastrando) return;
      var dx = e.clientX - ultimo; ultimo = e.clientX;
      ry += dx * 0.45; vy = dx * 0.45;
      rx = Math.max(-22, Math.min(10, -8 - (e.clientY - y0) * 0.12));
    });
    function soltar() { arrastrando = false; stage.classList.remove('is-girando'); }
    stage.addEventListener('pointerup', soltar);
    stage.addEventListener('pointercancel', soltar);

    stage.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
        e.preventDefault(); reposo = false;
        objetivo = (objetivo === null ? ry : objetivo) + (e.key === 'ArrowLeft' ? -30 : 30);
      }
    });

    var sec = stage.closest('section') || document;
    sec.querySelectorAll('[data-pt-girar]').forEach(function (b) {
      b.addEventListener('click', function () {
        reposo = false;
        var cara = b.getAttribute('data-pt-girar') === 'trasera' ? 180 : 0;
        // camino mas corto hasta la cara pedida, dejandola a tres cuartos
        var base = cara - 18, vueltas = Math.round((ry - base) / 360);
        objetivo = base + vueltas * 360;
        sec.querySelectorAll('[data-pt-girar]').forEach(function (o) { o.setAttribute('aria-pressed', o === b ? 'true' : 'false'); });
      });
    });
  }

  /* ---------- Historia con scroll ---------- */
  function historia(sec) {
    var caps = sec.querySelectorAll('[data-capitulo]');
    var n = caps.length;
    if (!n) return;
    sec.classList.add('is-js');
    if (quieto) { sec.classList.add('is-quieto'); return; }
    var bateria = sec.querySelector('[data-pt-bateria]');
    var minutos = sec.querySelector('[data-pt-minutos]');
    var pct = sec.querySelector('[data-pt-pct]');
    var tope = bateria ? parseFloat(bateria.getAttribute('data-tope') || '50') : 50;
    var mins = bateria ? parseFloat(bateria.getAttribute('data-minutos') || '30') : 30;
    var pendiente = false;

    function medir() {
      pendiente = false;
      var r = sec.getBoundingClientRect();
      var recorrido = r.height - window.innerHeight;
      var p = recorrido > 0 ? Math.min(1, Math.max(0, -r.top / recorrido)) : 0;
      sec.style.setProperty('--p', p.toFixed(4));
      var activo = Math.min(n - 1, Math.floor(p * n));
      caps.forEach(function (c, i) { c.classList.toggle('is-activo', i === activo); });
      sec.setAttribute('data-activo', caps[activo].getAttribute('data-capitulo'));
      if (bateria) {
        // la bateria se carga en el tramo de su capitulo
        var idx = Array.prototype.indexOf.call(caps, bateria.closest('[data-capitulo]') || caps[n - 1]);
        var local = Math.min(1, Math.max(0, p * n - idx) * 1.25);
        var v = local * tope;
        sec.style.setProperty('--carga', v.toFixed(2) + '%');
        if (pct) pct.textContent = Math.round(v) + ' %';
        if (minutos) minutos.textContent = Math.round(local * mins) + ' min';
      }
    }
    function pedir() { if (!pendiente) { pendiente = true; requestAnimationFrame(medir); } }
    window.addEventListener('scroll', pedir, { passive: true });
    window.addEventListener('resize', pedir);
    medir();
  }

  /* ---------- Escena que se inclina (oferta del pack) ---------- */
  function inclinar(escena) {
    var grupo = escena.querySelector('.pt-of__grupo');
    var sec = escena.closest('section');
    if (!grupo || !sec || escena.dataset.ptListo) return;
    escena.dataset.ptListo = '1';
    var BY = -34, BX = -13;
    function poner(x, y) { grupo.style.setProperty('--ry', y.toFixed(2) + 'deg'); grupo.style.setProperty('--rx', x.toFixed(2) + 'deg'); }
    if (quieto) { poner(BX, BY); return; }

    var ry = -64, rx = -3, ty = BY, tx = BX, ultimo = 0, arrastre = null, visible = true, corriendo = false;
    function arrancar() { if (!corriendo) { corriendo = true; requestAnimationFrame(paso); } }
    sec.classList.add('is-entrando');
    setTimeout(function () { sec.classList.remove('is-entrando'); }, 3400);

    sec.addEventListener('pointermove', function (e) {
      if (e.pointerType !== 'mouse') return;
      var r = sec.getBoundingClientRect();
      ty = BY + ((e.clientX - r.left) / r.width - 0.5) * 26;
      tx = BX - ((e.clientY - r.top) / r.height - 0.5) * 8;
      ultimo = performance.now();
    });
    sec.addEventListener('pointerleave', function () { ty = BY; tx = BX; });
    escena.addEventListener('pointerdown', function (e) {
      if (e.pointerType === 'mouse') return;
      arrastre = { x: e.clientX, ry: ty };
    });
    escena.addEventListener('pointermove', function (e) {
      if (!arrastre) return;
      ty = Math.max(-70, Math.min(20, arrastre.ry + (e.clientX - arrastre.x) * 0.35));
      ultimo = performance.now();
    });
    ['pointerup', 'pointercancel'].forEach(function (n) { escena.addEventListener(n, function () { arrastre = null; }); });

    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (es) { visible = es[0].isIntersecting; if (visible) arrancar(); }).observe(sec);
    }
    function paso(t) {
      if (!visible) { corriendo = false; return; }
      var ox = 0, oy = 0;
      if (t - ultimo > 2500 && !arrastre) { oy = Math.sin(t / 2800) * 9; ox = Math.sin(t / 3700) * 2; }
      ry += (ty + oy - ry) * 0.05; rx += (tx + ox - rx) * 0.05;
      poner(rx, ry);
      requestAnimationFrame(paso);
    }
    arrancar();
  }

  function iniciar(raiz) {
    (raiz || document).querySelectorAll('[data-pt-caja]').forEach(caja);
    (raiz || document).querySelectorAll('[data-pt-historia]').forEach(historia);
    (raiz || document).querySelectorAll('[data-pt-tilt]').forEach(inclinar);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function () { iniciar(); });
  else iniciar();
  // En el editor de temas las secciones se recargan sueltas.
  document.addEventListener('shopify:section:load', function (e) { iniciar(e.target); });
})();
