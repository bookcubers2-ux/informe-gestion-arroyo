/* ====================================================================
   Informe de gestión | Motor del libro
   --------------------------------------------------------------------
   Usa StPageFlip (page-flip, licencia MIT). Cada hoja está diseñada a
   600 x 850 y se escala entera al tamaño real que le da el libro, así
   el diseño se ve igual en un celular chico y en una pantalla grande.

   Accesibilidad: si la persona prefiere movimiento reducido, se arranca
   en vista de lista (páginas apiladas, sin animación). En cualquier
   momento se puede cambiar de vista con el botón de la cabecera.
   ==================================================================== */
(function () {
  'use strict';

  var ANCHO = 600, ALTO = 850;
  var libro = null;
  var contenedor = document.getElementById('flipbook');
  var paginas = Array.prototype.slice.call(document.querySelectorAll('.page'));
  var total = paginas.length;
  var indicador = document.getElementById('indicador');
  var btnAnt = document.getElementById('btnAnterior');
  var btnSig = document.getElementById('btnSiguiente');
  var btnVista = document.getElementById('btnVista');
  var pista = document.getElementById('pista');
  var prefiereQuieto = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var enLista = false;

  /* La escala real de la hoja: ancho que le dio el libro entre 600. */
  function fijarEscala() {
    var ref = document.querySelector('.page');
    if (!ref) return;
    var w = ref.getBoundingClientRect().width;
    if (!w) return;
    document.documentElement.style.setProperty('--s', (w / ANCHO).toFixed(4));
  }

  function actualizarControles() {
    if (!libro) return;
    var i = libro.getCurrentPageIndex();
    var orient = libro.getOrientation();
    var texto;
    if (orient === 'landscape' && i > 0 && i < total - 1) {
      /* En pantalla ancha se ven dos hojas: la izquierda es par (indice impar) */
      var izq = (i % 2 === 1) ? i : i - 1;
      texto = (izq + 1) + ' y ' + (izq + 2) + ' / ' + total;
    } else {
      texto = (i + 1) + ' / ' + total;
    }
    indicador.textContent = texto;
    btnAnt.disabled = (i === 0);
    btnSig.disabled = (i >= total - 1);
  }

  /* Copias limpias de las hojas, tomadas antes de que la librería las
     toque. Cada vista (libro o lista) se arma desde estas copias, así
     nunca arrastra estilos ni clases que la librería deja puestos. */
  var plantillas = paginas.map(function (p) { return p.cloneNode(true); });

  function hojasNuevas() {
    return plantillas.map(function (p) { return p.cloneNode(true); });
  }

  /* La librería convierte el contenedor en su "stf__parent" y al
     destruirse lo saca del documento: se garantiza uno limpio. */
  function contenedorLimpio() {
    var escenario = document.getElementById('libro');
    if (!contenedor || !document.body.contains(contenedor)) {
      contenedor = document.createElement('div');
      contenedor.id = 'flipbook';
      escenario.appendChild(contenedor);
    }
    contenedor.className = 'libro';
    contenedor.removeAttribute('style');
    contenedor.innerHTML = '';
    return contenedor;
  }

  function crearLibro() {
    contenedorLimpio();
    paginas = hojasNuevas();
    paginas.forEach(function (p) { contenedor.appendChild(p); });
    libro = new St.PageFlip(contenedor, {
      width: ANCHO,
      height: ALTO,
      size: 'stretch',
      /* 2 x minWidth supera el ancho máximo del libro (600): siempre
         una hoja a la vez, para que panorámica y láminas vayan en orden. */
      minWidth: 301,
      maxWidth: 600,
      minHeight: 427,
      maxHeight: 850,
      usePortrait: true,
      autoSize: true,
      showCover: true,
      mobileScrollSupport: false,
      drawShadow: true,
      maxShadowOpacity: 0.45,
      flippingTime: 800,
      swipeDistance: 24,
      /* Tocar la hoja no la pasa: así los enlaces y botones de las
         páginas funcionan sin sorpresas. Se pasa deslizando, con las
         flechas o con el teclado. */
      disableFlipByClick: true,
      clickEventForward: true,
      showPageCorners: true
    });
    libro.loadFromHTML(paginas);
    libro.on('flip', actualizarControles);
    libro.on('changeOrientation', function () { fijarEscala(); actualizarControles(); });
    libro.on('init', function () { fijarEscala(); actualizarControles(); });
    setTimeout(function () { fijarEscala(); actualizarControles(); }, 60);
  }

  function destruirLibro() {
    if (!libro) return;
    try { libro.destroy(); } catch (e) {}
    libro = null;
    contenedorLimpio();
    paginas = hojasNuevas();
    paginas.forEach(function (p) { contenedor.appendChild(p); });
  }

  /* Vista de lista: hojas apiladas, escaladas al ancho disponible. */
  function fijarEscalaLista() {
    var w = Math.min(contenedor.getBoundingClientRect().width, ANCHO);
    document.documentElement.style.setProperty('--s', (w / ANCHO).toFixed(4));
  }

  function verLista() {
    enLista = true;
    destruirLibro();
    document.body.classList.add('lista');
    btnVista.textContent = 'Ver como libro';
    btnVista.setAttribute('aria-pressed', 'true');
    fijarEscalaLista();
  }

  function verLibro() {
    enLista = false;
    document.body.classList.remove('lista');
    btnVista.textContent = 'Ver como lista';
    btnVista.setAttribute('aria-pressed', 'false');
    crearLibro();
  }

  btnVista.addEventListener('click', function () {
    if (enLista) verLibro(); else verLista();
  });

  /* Pasar de hoja con flechas o teclado. La librería, con
     disableFlipByClick activo, solo acepta pasar página si el punto que
     simula cae en una esquina visible; en el celular (una hoja a la vez)
     la esquina de "atrás" queda fuera de pantalla y la orden se descarta.
     Por eso se levanta ese bloqueo solo durante la orden. */
  function pasar(direccion) {
    if (!libro) return;
    var ajustes = libro.getSettings();
    var bloqueo = ajustes.disableFlipByClick;
    ajustes.disableFlipByClick = false;
    try {
      if (direccion < 0) libro.flipPrev(); else libro.flipNext();
    } finally {
      ajustes.disableFlipByClick = bloqueo;
    }
  }

  btnAnt.addEventListener('click', function () { pasar(-1); });
  btnSig.addEventListener('click', function () { pasar(1); });

  document.addEventListener('keydown', function (ev) {
    if (!libro) return;
    if (ev.key === 'ArrowRight' || ev.key === 'PageDown') { pasar(1); ev.preventDefault(); }
    if (ev.key === 'ArrowLeft'  || ev.key === 'PageUp')   { pasar(-1); ev.preventDefault(); }
  });

  var reloj = null;
  window.addEventListener('resize', function () {
    clearTimeout(reloj);
    reloj = setTimeout(function () {
      if (enLista) fijarEscalaLista(); else fijarEscala();
    }, 120);
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

  if (typeof St === 'undefined' || !St.PageFlip) {
    /* Sin la librería, el informe se lee igual, apilada. */
    pista.textContent = '';
    verLista();
  } else if (prefiereQuieto) {
    pista.textContent = 'Tu dispositivo prefiere menos movimiento: el informe se muestra como lista. Puedes cambiar a libro arriba a la derecha.';
    verLista();
  } else {
    verLibro();
  }
})();
