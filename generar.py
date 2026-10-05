# Arma index.html del informe de gestión. Orden pedido por el Dr. Arroyo: portada; por cada
# par de láminas, primero las dos juntas a doble hoja (se leen como una sola imagen
# panorámica) y luego una hoja por lámina con sus fotografías recortadas una por una en
# mosaico; contraportada. Sin rótulos en las hojas.
# Uso: python generar.py   (desde esta carpeta; las láminas van en img/01.jpg, 02.jpg, ...)
import glob, math, os, time
from itertools import permutations
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
URL = 'https://bookcubers2-ux.github.io/informe-gestion-arroyo/'
NOMBRE = 'Dr. PhD Carlos Mauricio Arroyo Balboa'
GESTION = 'Gestión 2025-2030'
# Cambia en cada generación: obliga al navegador a bajar estilos y motor nuevos
# (con los viejos en caché las hojas salen apiladas hacia abajo).
V = time.strftime('%Y%m%d%H%M')

n = len(glob.glob(os.path.join(AQUI, 'img', '[0-9][0-9].jpg')))

# Recortes de las fotografías que componen cada lámina: (lámina, x0, y0, x1, y1) en
# píxeles de la lámina original (1024 x 1280). Las láminas forman una tira continua,
# así que un recorte puede salirse hacia la lámina vecina (x < 0 o x > 1024).
RECORTES = {
    1: [(1, 0, 20, 310, 505), (1, 400, 30, 960, 540), (1, 0, 780, 750, 1280), (1, 750, 770, 1024, 1230)],
    2: [(2, 0, 0, 1024, 535), (2, 0, 545, 495, 1280), (2, 497, 545, 1024, 1280)],
    3: [(3, 0, 0, 535, 425), (3, 520, 40, 800, 500), (3, 0, 430, 535, 965), (3, 0, 975, 510, 1280)],
    4: [(4, 270, 0, 1024, 470), (4, 180, 480, 830, 1280)],
    5: [(5, 0, 200, 1024, 470), (5, 265, 475, 808, 1280)],
    6: [(6, 240, 0, 850, 470), (5, 812, 475, 1404, 1280), (6, 380, 640, 860, 1280)],
    7: [(7, 0, 215, 1024, 1280)],
    8: [(8, 0, 0, 1024, 520), (8, 0, 795, 1024, 1280)],
    9: [(9, 90, 0, 1024, 555), (9, 0, 600, 510, 1160), (9, 512, 560, 1000, 1010)],
    10: [(10, 0, 120, 720, 990), (10, 720, 0, 1344, 740)],
    11: [(11, 325, 0, 830, 640), (11, -300, 770, 790, 1280)],
    12: [(12, -150, 0, 400, 640), (12, 405, 250, 850, 750), (12, 0, 830, 400, 1280), (12, 440, 770, 1024, 1280)],
    13: [(13, 300, 0, 1270, 690), (13, 255, 730, 1410, 1280)],
    14: [(14, 400, 0, 1024, 1280)],
}

tira = Image.new('RGB', (1024 * n, 1280))
for i in range(1, n + 1):
    tira.paste(Image.open(os.path.join(AQUI, 'img', f'{i:02d}.jpg')).resize((1024, 1280)), ((i - 1) * 1024, 0))
os.makedirs(os.path.join(AQUI, 'img', 'f'), exist_ok=True)

SEP = 10           # separación entre fotografías
AREA = (572, 722)  # espacio útil del mosaico dentro de la hoja (600 x 750 menos márgenes)
PIE = '<div class="pie-foto"><span class="pf-tit">Informe de gestión</span><span class="pf-sub">Relaciones Internacionales · UAGRM</span></div>'


def particiones(k):
    if k == 0:
        yield []
        return
    for primero in range(1, k + 1):
        for resto in particiones(k - primero):
            yield [primero] + resto


def mosaico(asp, W, H):
    """Reparte las fotos en filas o en columnas buscando el arreglo que menos las recorta.
    Devuelve (deformación, celdas, alto natural); celdas = (índice, x, y, ancho, alto)."""
    mejor = None
    for orden in permutations(range(len(asp))):
        for tamanos in particiones(len(asp)):
            grupos, k = [], 0
            for t in tamanos:
                grupos.append(orden[k:k + t]); k += t
            # en filas: las fotos de una fila comparten alto
            nat = [(W - SEP * (len(g) - 1)) / sum(asp[i] for i in g) for g in grupos]
            f1 = (H - SEP * (len(grupos) - 1)) / sum(nat)
            celdas, y = [], 0
            for g, h in zip(grupos, nat):
                h *= f1; x = 0
                for i in g:
                    w = (W - SEP * (len(g) - 1)) * asp[i] / sum(asp[j] for j in g)
                    celdas.append((i, x, y, w, h)); x += w + SEP
                y += h + SEP
            candidatos = [(f1, celdas, sum(nat) + SEP * (len(grupos) - 1))]
            # en columnas: las fotos de una columna comparten ancho
            u = [1 / sum(1 / asp[i] for i in g) for g in grupos]
            anchos = [(W - SEP * (len(grupos) - 1)) * v / sum(u) for v in u]
            natc = anchos[0] * sum(1 / asp[i] for i in grupos[0])
            celdas, x = [], 0
            for g, w in zip(grupos, anchos):
                y = 0
                for i in g:
                    h = (H - SEP * (len(g) - 1)) * (1 / asp[i]) / sum(1 / asp[j] for j in g)
                    celdas.append((i, x, y, w, h)); y += h + SEP
                x += w + SEP
            candidatos.append((H / natc, celdas, natc))
            for c in candidatos:
                costo = abs(math.log(c[0])) + (0 if list(orden) == sorted(orden) else 0.02)
                if mejor is None or costo < mejor[0]:
                    mejor = (costo, c)
    return mejor[1]


def hoja_mosaico(lam):
    asp, archivos = [], []
    for k, (l, x0, y0, x1, y1) in enumerate(RECORTES[lam], 1):
        d = (l - 1) * 1024
        x0 = max(0, x0 + d); x1 = min(tira.width, x1 + d)
        nombre = f'img/f/{lam:02d}-{k}.jpg'
        tira.crop((x0, y0, x1, y1)).save(os.path.join(AQUI, nombre), quality=90)
        asp.append((x1 - x0) / (y1 - y0)); archivos.append(nombre)
    W, H = AREA
    f, celdas, nat = mosaico(asp, W, H)
    # Si llenar la hoja obligaría a recortar demasiado, el mosaico se achica y se centra.
    if f > 1.15:
        H = nat * 1.15
    elif f < 0.87:
        W = W * H / (nat * 0.87)
    if (W, H) != AREA:
        f, celdas, nat = mosaico(asp, W, H)
    ox = 14 + (AREA[0] - W) / 2; oy = 14 + (AREA[1] - H) / 2
    fotos = ''.join(
        f'\n            <img src="{archivos[i]}" alt="Fotografía de las actividades de la Carrera de Relaciones Internacionales" style="left:{x + ox:.0f}px;top:{y + oy:.0f}px;width:{w:.0f}px;height:{h:.0f}px">'
        for i, x, y, w, h in celdas)
    return f'''<div class="hoja h-mosaico">
          <div class="mosaico">{fotos}
          </div>
          {PIE}
        </div>'''


def hoja(i):
    return f'''<div class="hoja h-foto">
          <img class="lamina" src="img/{i:02d}.jpg" alt="Lámina {i} del informe de gestión: actividades de la Carrera de Relaciones Internacionales" width="600" height="750">
          {PIE}
        </div>'''


def vista(clase, etiqueta, contenido):
    return f'''
    <section class="vista {clase}" aria-label="{etiqueta}">
      <div class="vista-in">
        {contenido}
      </div>
    </section>
'''


vistas = ''
total = 2
for a in range(1, n + 1, 2):
    b = a + 1
    if b <= n:
        vistas += vista('v-doble', f'Láminas {a} y {b} juntas', hoja(a) + '\n        ' + hoja(b))
        total += 1
    for i in (a, b):
        if i <= n:
            vistas += vista('v-una', f'Fotografías de la lámina {i}', hoja_mosaico(i) if i in RECORTES else hoja(i))
            total += 1

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
<link rel="stylesheet" href="css/estilos.css?v={V}">
</head>
<body>

<a class="saltar" href="#libro">Saltar al contenido</a>

<header class="cabecera" aria-label="Informe de gestión">
  <img src="img/retrato.jpg" alt="" width="40" height="40">
  <span class="cab-nombre">Informe de Gestión</span>
  <span class="cab-sub">Relaciones Internacionales · UAGRM</span>
</header>

<p class="pista" id="pista">Desliza o toca las flechas para pasar la página.</p>

<main id="libro" class="escenario" aria-label="Informe de gestión en formato de libro">
  <div class="visor" id="visor">

    <!-- ============ PORTADA ============ -->
    <section class="vista v-una visible" aria-label="Portada">
      <div class="vista-in">
        <div class="hoja hoja-portada">
          <div class="sello-logo sello-retrato"><img src="img/retrato.jpg" alt="{NOMBRE}"></div>
          <p class="kicker">Universidad Autónoma Gabriel René Moreno</p>
          <h1 class="h1-informe">Informe<br><span>de Gestión</span></h1>
          <p class="portada-nombre">Dr. PhD Carlos Mauricio<br>Arroyo Balboa</p>
          <p class="pill">Director de Carrera · Relaciones Internacionales</p>
          <p class="portada-inv">{GESTION}</p>
          <p class="portada-abre">Desliza para abrir</p>
        </div>
      </div>
    </section>

    <!-- ============ LÁMINAS: el par a doble hoja y luego el mosaico de cada una ============ -->{vistas}
    <!-- ============ CONTRAPORTADA ============ -->
    <section class="vista v-una" aria-label="Contraportada">
      <div class="vista-in">
        <div class="hoja hoja-portada hoja-contra">
          <p class="kicker">Relaciones Internacionales · UAGRM</p>
          <h2 class="grande">Informe<br>de Gestión</h2>
          <div class="sello-logo chico sello-retrato"><img src="img/retrato.jpg" alt=""></div>
          <p class="portada-nombre">Dr. PhD Carlos Mauricio<br>Arroyo Balboa</p>
          <p class="pill">Director de Carrera</p>
          <p class="portada-inv">{GESTION}</p>
        </div>
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

<script src="js/libro.js?v={V}"></script>
</body>
</html>
'''
open(os.path.join(AQUI, 'index.html'), 'w', encoding='utf-8', newline='\n').write(html)
print('index.html listo:', n, 'laminas,', total, 'vistas')
