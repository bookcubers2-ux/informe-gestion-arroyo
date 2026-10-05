# Arma index.html del informe de gestión: portada, por cada par de fotografías su vista
# panorámica y luego las dos láminas, y contraportada. Genera también las panorámicas.
# Uso: python generar.py   (desde esta carpeta; las fotos van en img/01.jpg, 02.jpg, ...)
import glob, os

AQUI = os.path.dirname(os.path.abspath(__file__))
URL = 'https://bookcubers2-ux.github.io/informe-gestion-arroyo/'
NOMBRE = 'Dr. PhD Carlos Mauricio Arroyo Balboa'
GESTION = 'Gestión 2025-2030'

n = len(glob.glob(os.path.join(AQUI, 'img', '[0-9][0-9].jpg')))

from PIL import Image, ImageFilter, ImageEnhance

def panoramica(a, b):
    """Une dos láminas contiguas en una sola imagen y prepara su fondo desenfocado."""
    ia = Image.open(os.path.join(AQUI, 'img', f'{a:02d}.jpg'))
    ib = Image.open(os.path.join(AQUI, 'img', f'{b:02d}.jpg'))
    pan = Image.new('RGB', (ia.width + ib.width, ia.height))
    pan.paste(ia, (0, 0)); pan.paste(ib, (ia.width, 0))
    pan.save(os.path.join(AQUI, 'img', f'pan-{a:02d}-{b:02d}.jpg'), quality=90)
    alto = 850; ancho = round(pan.width * alto / pan.height)
    f = pan.resize((ancho, alto)).crop(((ancho - 600) // 2, 0, (ancho - 600) // 2 + 600, alto))
    f = ImageEnhance.Brightness(f.filter(ImageFilter.GaussianBlur(22))).enhance(0.45)
    f.save(os.path.join(AQUI, 'img', f'fondo-{a:02d}-{b:02d}.jpg'), quality=70)

def lamina(i, folio):
    return f'''
    <section class="page" aria-label="Lámina {i} de {n}">
      <div class="hoja h-foto">
        <img class="lamina" src="img/{i:02d}.jpg" alt="Lámina {i} del informe de gestión: fotografías de las actividades de la Carrera de Relaciones Internacionales" width="600" height="750">
        <div class="pie-foto"><span class="pf-tit">Lámina {i}</span><span class="pf-sub">Informe de gestión · Relaciones Internacionales UAGRM</span></div>
        <span class="folio claro">{folio}</span>
      </div>
    </section>
'''

# Orden pedido por el Dr. Arroyo: panorámica de cada par, luego sus dos láminas.
fotos = ''
folio = 1
for a in range(1, n + 1, 2):
    b = a + 1
    if b <= n:
        panoramica(a, b)
        folio += 1
        fotos += f'''
    <section class="page" aria-label="Vista panorámica de las láminas {a} y {b}">
      <div class="hoja h-pan" style="background-image:url(img/fondo-{a:02d}-{b:02d}.jpg)">
        <div class="pan-cab"><p class="razon">Vista panorámica</p><h2>Láminas {a} y {b}</h2></div>
        <a class="pan-marco" href="img/pan-{a:02d}-{b:02d}.jpg" target="_blank" rel="noopener"><img src="img/pan-{a:02d}-{b:02d}.jpg" alt="Vista panorámica que une las láminas {a} y {b} del informe de gestión" width="600" height="375"></a>
        <p class="pan-pista">Toca la imagen para verla en grande</p>
        <div class="pie-foto"><span class="pf-tit">Vista panorámica</span><span class="pf-sub">Informe de gestión · Relaciones Internacionales UAGRM</span></div>
        <span class="folio claro">{folio}</span>
      </div>
    </section>
'''
    for i in (a, b):
        if i <= n:
            folio += 1
            fotos += lamina(i, folio)
total = folio + 1

html = f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Informe de Gestión · {NOMBRE}</title>
<meta name="description" content="Informe de gestión del {NOMBRE}, Director de Carrera de Relaciones Internacionales de la UAGRM. {GESTION}.">
<meta name="theme-color" content="#040635">

<!-- Vista previa en WhatsApp, Telegram, Facebook, etc. (Open Graph) -->
<meta property="og:type" content="website">
<meta property="og:locale" content="es_ES">
<meta property="og:site_name" content="Relaciones Internacionales UAGRM">
<meta property="og:title" content="Informe de Gestión · {NOMBRE}">
<meta property="og:description" content="Director de Carrera de Relaciones Internacionales, UAGRM. {GESTION}.">
<meta property="og:url" content="{URL}">
<meta property="og:image" content="{URL}img/og.jpg">
<meta property="og:image:secure_url" content="{URL}img/og.jpg">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Informe de gestión del {NOMBRE}.">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Informe de Gestión · {NOMBRE}">
<meta name="twitter:description" content="Director de Carrera de Relaciones Internacionales, UAGRM. {GESTION}.">
<meta name="twitter:image" content="{URL}img/og.jpg">

<link rel="icon" type="image/jpeg" href="img/retrato.jpg">
<link rel="stylesheet" href="css/estilos.css">
</head>
<body>

<a class="saltar" href="#libro">Saltar al contenido</a>

<header class="cabecera" aria-label="Informe de gestión">
  <img src="img/retrato.jpg" alt="" width="40" height="40">
  <span class="cab-nombre">Informe de Gestión</span>
  <span class="cab-sub">Relaciones Internacionales · UAGRM</span>
  <button type="button" class="cab-btn" id="btnVista" aria-pressed="false">Ver como lista</button>
</header>

<p class="pista" id="pista">Desliza o toca las flechas para pasar la página.</p>

<main id="libro" class="escenario" aria-label="Informe de gestión en formato de libro">
  <div class="libro" id="flipbook">

    <!-- ============ PORTADA ============ -->
    <section class="page portada" data-density="hard" aria-label="Portada">
      <div class="hoja hoja-portada">
        <div class="sello-logo sello-retrato"><img src="img/retrato.jpg" alt="{NOMBRE}"></div>
        <p class="kicker">Universidad Autónoma Gabriel René Moreno</p>
        <h1 class="h1-informe">Informe<br><span>de Gestión</span></h1>
        <p class="portada-nombre">Dr. PhD Carlos Mauricio<br>Arroyo Balboa</p>
        <p class="pill">Director de Carrera · Relaciones Internacionales</p>
        <p class="portada-inv">{GESTION}</p>
        <p class="portada-abre">Desliza para abrir</p>
      </div>
    </section>

    <!-- ============ LÁMINAS (una fotografía por hoja) ============ -->{fotos}
    <!-- ============ CONTRAPORTADA ============ -->
    <section class="page portada" data-density="hard" aria-label="Contraportada">
      <div class="hoja hoja-portada hoja-contra">
        <p class="kicker">Relaciones Internacionales · UAGRM</p>
        <h2 class="grande">Informe<br>de Gestión</h2>
        <div class="sello-logo chico sello-retrato"><img src="img/retrato.jpg" alt=""></div>
        <p class="portada-nombre">Dr. PhD Carlos Mauricio<br>Arroyo Balboa</p>
        <p class="pill">Director de Carrera</p>
        <p class="portada-inv">{GESTION}</p>
      </div>
    </section>

  </div>
</main>

<nav class="control" aria-label="Pasar las páginas">
  <button type="button" id="btnAnterior" aria-label="Página anterior">&#9664;</button>
  <span class="indicador" id="indicador" aria-live="polite">1 / {total}</span>
  <button type="button" id="btnSiguiente" aria-label="Página siguiente">&#9654;</button>
  <a class="compartir" id="btnCompartir" href="https://wa.me/?text=Informe%20de%20Gesti%C3%B3n%20del%20Dr.%20PhD%20Carlos%20Mauricio%20Arroyo%20Balboa%2C%20Director%20de%20Carrera%20de%20Relaciones%20Internacionales%20de%20la%20UAGRM%3A%20https%3A%2F%2Fbookcubers2-ux.github.io%2Finforme-gestion-arroyo%2F" target="_blank" rel="noopener">Compartir</a>
</nav>

<footer class="pie">
  <p>Carrera de Relaciones Internacionales · Universidad Autónoma Gabriel René Moreno · Santa Cruz de la Sierra, Bolivia</p>
</footer>

<script src="js/page-flip.browser.js"></script>
<script src="js/libro.js"></script>
</body>
</html>
'''
open(os.path.join(AQUI, 'index.html'), 'w', encoding='utf-8', newline='\n').write(html)
print('index.html listo:', n, 'laminas,', total, 'hojas')
