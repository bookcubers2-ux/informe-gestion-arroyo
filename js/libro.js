/* ====================================================================
   Informe de gestión | Motor del libro
   --------------------------------------------------------------------
   El libro alterna dos tipos de vista: a doble hoja (dos fotografías
   contiguas que se leen como una sola imagen panorámica, 1200 x 850) y
   de una hoja (600 x 850). Cada vista se escala entera al espacio que
   hay en pantalla, así el diseño se ve igual en celular y computadora.

   Accesibilidad: si la persona prefiere movimiento reducido, las hojas
   cambian sin animación.
   ==================================================================== */
(function () {
  'use strict';

  var ANCHO = 600, ALTO = 850;
  var visor = document.getElementById('visor');
  var vistas = Array.prototype.slice.call(visor.querySelectorAll('.vista'));
  var total = vistas.length;
  var actual = 0;
  var ocupado = false;
  var indicador = document.getElementById('indicador');
  var btnAnt = document.getElementById('btnAnterior');
  var btnSig = document.getElementById('btnSiguiente');
  var prefiereQuieto = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function alto(sel) {
    var el = document.querySelector(sel);
    return el ? el.offsetHeight : 0;
  }

  /* Escala de cada tipo de vista según el espacio libre. En pantallas
     muy bajas (celular acostado) se deja crecer y se desplaza. */
  function medir() {
    var anchoDisp = visor.clientWidth;
    var altoDisp = window.innerHeight - alto('.cabecera') - alto('.pista') - alto('.control') - 36;
    altoDisp = Math.max(altoDisp, window.innerHeight * 0.85, 240);
    var eUna = Math.min(anchoDisp / ANCHO, altoDisp / ALTO, 1.15);
    var eDoble = Math.min(anchoDisp / (ANCHO * 2), altoDisp / ALTO, 1.15);
    visor.style.height = Math.round(ALTO * eUna) + 'px';
    vistas.forEach(function (v) {
      v.style.setProperty('--e', (v.classList.contains('v-doble') ? eDoble : eUna).toFixed(4));
    });
  }

  function actualizarControles() {
    indicador.textContent = (actual + 1) + ' / ' + total;
    btnAnt.disabled = (actual === 0);
    btnSig.disabled = (actual >= total - 1);
  }

  /* Pasar de vista: la hoja de arriba gira sobre su lomo (borde
     izquierdo) y deja ver la siguiente; hacia atrás, vuelve a caer. */
  function ir(n) {
    if (ocupado || n < 0 || n >= total || n === actual) return;
    var sale = vistas[actual], entra = vistas[n];
    var adelante = n > actual;
    entra.classList.add('visible');

    function terminar() {
      sale.classList.remove('visible');
      sale.style.zIndex = entra.style.zIndex = '';
      actual = n;
      ocupado = false;
      actualizarControles();
    }

    var gira = adelante ? sale : entra;
    var cuerpo = gira.firstElementChild;
    if (prefiereQuieto || !cuerpo.animate) { terminar(); return; }

    ocupado = true;
    gira.style.zIndex = 3;
    (adelante ? entra : sale).style.zIndex = 2;
    var pasos = [
      { transform: 'rotateY(0deg)', opacity: 1 },
      { transform: 'rotateY(-84deg)', opacity: 1, offset: 0.85 },
      { transform: 'rotateY(-96deg)', opacity: 0 }
    ];
    if (!adelante) {
      pasos = [
        { transform: 'rotateY(-96deg)', opacity: 0 },
        { transform: 'rotateY(-84deg)', opacity: 1, offset: 0.15 },
        { transform: 'rotateY(0deg)', opacity: 1 }
      ];
    }
    var anim = cuerpo.animate(pasos, { duration: 700, easing: 'ease-in-out' });
    anim.onfinish = terminar;
    anim.oncancel = terminar;
  }

  function pasar(direccion) { ir(actual + direccion); }

  btnAnt.addEventListener('click', function () { pasar(-1); });
  btnSig.addEventListener('click', function () { pasar(1); });

  document.addEventListener('keydown', function (ev) {
    if (ev.key === 'ArrowRight' || ev.key === 'PageDown') { pasar(1); ev.preventDefault(); }
    if (ev.key === 'ArrowLeft'  || ev.key === 'PageUp')   { pasar(-1); ev.preventDefault(); }
  });

  /* Deslizar con el dedo; un toque en el lado derecho o izquierdo del
     libro también pasa la hoja. */
  var x0 = null, y0 = null, deslizo = false;
  visor.addEventListener('touchstart', function (ev) {
    x0 = ev.touches[0].clientX; y0 = ev.touches[0].clientY; deslizo = false;
  }, { passive: true });
  visor.addEventListener('touchend', function (ev) {
    if (x0 === null) return;
    var dx = ev.changedTouches[0].clientX - x0;
    var dy = ev.changedTouches[0].clientY - y0;
    x0 = null;
    if (Math.abs(dx) > 40 && Math.abs(dx) > Math.abs(dy)) {
      deslizo = true;
      pasar(dx < 0 ? 1 : -1);
    }
  }, { passive: true });
  visor.addEventListener('click', function (ev) {
    if (deslizo) { deslizo = false; return; }
    if (ev.target.closest && ev.target.closest('a, button')) return;
    var caja = visor.getBoundingClientRect();
    var pos = (ev.clientX - caja.left) / caja.width;
    if (pos > 0.6) pasar(1); else if (pos < 0.4) pasar(-1);
  });

  var reloj = null;
  window.addEventListener('resize', function () {
    clearTimeout(reloj);
    reloj = setTimeout(medir, 120);
  });

  /* Compartir con el menú nativo del teléfono cuando existe */
  var btnCompartir = document.getElementById('btnCompartir');
  if (navigator.share && btnCompartir) {
    btnCompartir.addEventListener('click', function (ev) {
      ev.preventDefault();
      navigator.share({
        title: 'Informe de Gestión, Dr. PhD Carlos Mauricio Arroyo Balboa',
        text: 'Informe de Gestión del Dr. PhD Carlos Mauricio Arroyo Balboa, Director de Carrera de Relaciones Internacionales de la UAGRM.',
        url: location.href.split('#')[0]
      }).catch(function () {});
    });
  }

  /* Para revisar una vista concreta: index.html#5 abre la quinta. */
  var pedida = parseInt(location.hash.slice(1), 10);
  if (pedida >= 1 && pedida <= total) {
    vistas[0].classList.remove('visible');
    actual = pedida - 1;
    vistas[actual].classList.add('visible');
  }

  medir();
  actualizarControles();
})();
