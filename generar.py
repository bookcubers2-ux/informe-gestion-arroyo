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


def mosaico(asp, W, H, fijo=False):
    """Reparte las fotos en filas o en columnas buscando el arreglo que menos las recorta.
    Devuelve (deformación, celdas, alto natural); celdas = (índice, x, y, ancho, alto)."""
    mejor = None
    for orden in ([tuple(range(len(asp)))] if fijo else permutations(range(len(asp)))):
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

# ---------------------------------------------------------------------------------------
# Fotografías nuevas (zip del Canva del Dr. Arroyo): ../FOTOS-NUEVAS/NN.jpg, una por página original,
# cada una con su banner (mes + actividad) arriba. Se recorta el banner y cada foto lleva su
# leyenda. El orden es el del PDF del Canva (páginas 1 a 84), sin alterarlo.
# (mes, leyenda) de cada página, en el orden del PDF.
T = [
    ('Marzo', 'Presentación de proyecto'), ('Marzo', 'Presentación de proyecto'),
    ('Abril', 'Alianza con Goethe-Zentrum, Centro de Idiomas Alemán'), ('Abril', 'Presentación de proyectos'),
    *[('Abril', 'Estrecho de Ormuz')] * 2, *[('Abril', 'Conversatorio: Estrecho de Ormuz')] * 6,
    ('Abril', 'Cumbre Departamental de Justicia'), *[('Abril', 'Reunión de coordinación con el CBA')] * 2,
    ('Mayo', 'Sala de cómputo'), *[('Mayo', 'Evento cultural')] * 2, ('Mayo', 'Reunión de rediseño curricular'),
    *[('Mayo', 'Visita del Cónsul de Brasil')] * 2, *[('Mayo', 'Inauguración de biblioteca')] * 9,
    *[('Mayo', 'Izamiento de bandera e inauguración de la Semana de la Carrera')] * 3,
    *[('Mayo', 'Celebración eucarística · Semana de la Carrera')] * 3,
    ('Mayo', 'Reconocimiento a estudiantes destacados · Semana de la Carrera'),
    ('Mayo', 'Conferencia internacional · Semana de la Carrera'),
    *[('Mayo', 'Feria de emprendedores · Semana de la Carrera')] * 3,
    *[('Mayo', 'Feria cultural · Semana de la Carrera')] * 9,
    ('Mayo', 'Danza académica · Semana de la Carrera'), ('Mayo', 'Semana de la Carrera'),
    ('Junio', 'Defensa de maestría: Evaluación de la calidad y procesos de certificación en educación superior'),
    *[('Junio', 'Cónsul de Ucrania')] * 2, ('Junio', 'Conversatorio: Sistema político chino'),
    *[('Junio', 'Inauguración de sala de cómputo')] * 3,
    *[('Julio', 'Dotación de libros para la biblioteca')] * 2,
    *[('Julio', 'Feria cultural: Estudiantes de Relaciones Internacionales')] * 4,
    ('Agosto', 'Reunión de coordinación'), ('Agosto', 'Reunión de coordinación del InterMUN'),
    *[('Agosto', 'Feria de orientación vocacional')] * 5,
    *[('Septiembre', 'Reunión de coordinación: CONCICRUZ')] * 2,
    *[('Septiembre', 'Firma de convenio con la Alianza Francesa')] * 3,
    ('Septiembre', 'Invitación a seminario internacional'), ('Septiembre', 'Reunión con los cónsules de China'),
    ('Septiembre', 'Firma de convenio con SENAVEX'), *[('Septiembre', 'Disertación internacional')] * 3,
    ('Septiembre', 'Cumbre Departamental de Justicia'),
]
assert len(T) == 84


def agrupar():
    """Hojas de hasta 4 fotos en el orden exacto del PDF. Una actividad larga se reparte en
    hojas parejas; las actividades cortas seguidas del mismo mes comparten hoja."""
    tramos, i = [], 0
    while i < len(T):
        j = i
        while j < len(T) and T[j] == T[i]:
            j += 1
        k = -(-(j - i) // 4)
        cortes = [i + round((j - i) * c / k) for c in range(k + 1)]
        tramos += [list(range(a + 1, b + 1)) for a, b in zip(cortes, cortes[1:])]
        i = j
    hojas = []
    for t in tramos:
        if hojas and len(hojas[-1]) + len(t) <= 3 and T[hojas[-1][0] - 1][0] == T[t[0] - 1][0]                 and len(t) == 1 and len(hojas[-1]) <= 2:
            hojas[-1] += t
        else:
            hojas.append(list(t))
    grupos = []
    for nums in hojas:
        meses = list(dict.fromkeys(T[n - 1][0] for n in nums))
        tits = list(dict.fromkeys(T[n - 1][1].split(' · ')[0] for n in nums))
        grupos.append((tits[0] if len(tits) == 1 else 'Actividades de la Carrera', ' y '.join(meses), nums))
    return grupos


GRUPOS = agrupar()


def sin_banner(num):
    """Abre FOTOS-NUEVAS/NN.jpg sin el banner superior (se detecta la barra azul del título)."""
    import numpy as np
    im = Image.open(os.path.join(AQUI, '..', 'FOTOS-NUEVAS', f'{num:02d}.jpg')).convert('RGB')
    a = np.asarray(im).astype(int)
    fila = ((a[:, :, 2] > 130) & (a[:, :, 0] < 60) & (a[:, :, 1] < 100)).mean(axis=1)
    ys = [y for y in range(im.height // 2) if fila[y] > 0.5]
    y0 = (ys[-1] + 6) if ys else 0
    return im.crop((0, y0, im.width, im.height))


def hoja_grupo(g, titulo, mes, nums):
    asp, archivos = [], []
    for k, num in enumerate(nums, 1):
        im = sin_banner(num)
        im.thumbnail((800, 800))
        nombre = f'img/g/f{g:02d}-{k}.jpg'
        im.save(os.path.join(AQUI, nombre), quality=80, optimize=True, progressive=True)
        asp.append(im.width / im.height); archivos.append(nombre)
    W, H = AREA
    f, celdas, nat = mosaico(asp, W, H, True)
    if f > 1.15:
        H = nat * 1.15
    elif f < 0.87:
        W = W * H / (nat * 0.87)
    if (W, H) != AREA:
        f, celdas, nat = mosaico(asp, W, H, True)
    ox = 14 + (AREA[0] - W) / 2; oy = 14 + (AREA[1] - H) / 2
    fotos = ''.join(
        f'\n            <figure class="foto" style="left:{x + ox:.0f}px;top:{y + oy:.0f}px;width:{w:.0f}px;height:{h:.0f}px">'
        f'<img src="{archivos[i]}" alt="{T[nums[i] - 1][1]}, {T[nums[i] - 1][0].lower()}">'
        f'<figcaption>{T[nums[i] - 1][1]}</figcaption></figure>'
        for i, x, y, w, h in celdas)
    pie = f'<div class="pie-foto"><span class="pf-tit">{titulo}</span><span class="pf-sub">{mes} · Relaciones Internacionales · UAGRM</span></div>'
    return f'''<div class="hoja h-mosaico">
          <div class="mosaico">{fotos}
          </div>
          {pie}
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
# Las 14 láminas viejas ya no se muestran (pedido 2026-10-20): solo las fotos en el orden del PDF.
for a in range(1, n + 1, 2) if False else []:
    b = a + 1
    if b <= n:
        vistas += vista('v-doble', f'Láminas {a} y {b} juntas', hoja(a) + '\n        ' + hoja(b))
        total += 1
    for i in (a, b):
        if i <= n:
            vistas += vista('v-una', f'Fotografías de la lámina {i}', hoja_mosaico(i) if i in RECORTES else hoja(i))
            total += 1

def panoramica(k, grupos):
    """Doble hoja de apertura (como las láminas del Canva): collage a sangre con todas las fotos
    del par de hojas, en orden, y un título grande encima. Se parte en dos mitades de 600 x 850."""
    from PIL import ImageDraw, ImageFont, ImageFilter
    nums = [n for _, _, ns in grupos for n in ns]
    ims = [sin_banner(n) for n in nums]
    asp = [im.width / im.height for im in ims]
    E = 2  # escala: el collage se dibuja a 2400 x 1700
    f, celdas, nat = mosaico(asp, 1200, 850, True)
    lienzo = Image.new('RGB', (1200 * E, 850 * E), (4, 6, 53))
    for i, x, y, w, h in celdas:
        W_, H_ = round(w * E), round(h * E)
        im = ims[i]; r = W_ / H_
        if im.width / im.height > r:
            cw = im.height * r; im = im.crop(((im.width - cw) / 2, 0, (im.width + cw) / 2, im.height))
        else:
            ch = im.width / r; y0 = (im.height - ch) * 0.3; im = im.crop((0, y0, im.width, y0 + ch))
        lienzo.paste(im.resize((W_, H_)), (round(x * E), round(y * E)))
    d = ImageDraw.Draw(lienzo)
    for i, x, y, w, h in celdas:
        d.rectangle((x * E, y * E, (x + w) * E, (y + h) * E), outline='white', width=6)
    # título: la actividad con más fotos del par; debajo, los meses
    cuenta = {}
    for n in nums:
        t = T[n - 1][1].split(' · ')[0].split(':')[0]
        cuenta[t] = cuenta.get(t, 0) + 1
    titulo = max(cuenta, key=lambda t: (cuenta[t], -nums.index(next(n for n in nums if T[n - 1][1].startswith(t)))))
    meses = ' y '.join(dict.fromkeys(T[n - 1][0] for n in nums)) + ' 2026'
    fuente = 'C:/Windows/Fonts/seguibli.ttf'
    tam = 150
    while True:
        F1 = ImageFont.truetype(fuente, tam)
        lineas, linea = [], ''
        for pal in titulo.split():
            prueba = (linea + ' ' + pal).strip()
            if d.textlength(prueba, font=F1) > 1900 and linea:
                lineas.append(linea); linea = pal
            else:
                linea = prueba
        lineas.append(linea)
        if len(lineas) <= 2 or tam < 90:
            break
        tam -= 10
    F2 = ImageFont.truetype(fuente, 80)
    alto = len(lineas) * tam * 1.15 + 110
    y = (1700 - alto) / 2
    sombra = Image.new('RGBA', lienzo.size, (0, 0, 0, 0)); ds = ImageDraw.Draw(sombra)
    ds.rounded_rectangle((180, y - 50, 2220, y + alto + 40), 40, fill=(4, 6, 53, 170))
    lienzo = Image.alpha_composite(lienzo.convert('RGBA'), sombra.filter(ImageFilter.GaussianBlur(30))).convert('RGB')
    d = ImageDraw.Draw(lienzo)
    for ln in lineas:
        d.text((1200, y), ln, font=F1, fill=(230, 20, 30), anchor='ma', stroke_width=10, stroke_fill='white')
        y += tam * 1.15
    d.text((1200, y + 10), meses, font=F2, fill=(255, 196, 40), anchor='ma', stroke_width=6, stroke_fill=(4, 6, 53))
    mitades = []
    for lado in (0, 1):
        nombre = f'img/g/pan{k:02d}-{lado + 1}.jpg'
        lienzo.crop((1200 * lado, 0, 1200 * (lado + 1), 1700)).resize((900, 1275)).save(os.path.join(AQUI, nombre), quality=80, optimize=True, progressive=True)
        mitades.append(f'''<div class="hoja h-foto">
          <img class="lamina lamina-plena" src="{nombre}" alt="{titulo}, {meses}" width="600" height="850">
        </div>''')
    return mitades


hojas_g = [hoja_grupo(g, t, m, nums) for g, (t, m, nums) in enumerate(GRUPOS, 1)]
for k in range(0, len(hojas_g), 2):
    par = GRUPOS[k:k + 2]
    izq, der = panoramica(k // 2 + 1, par)
    vistas += vista('v-doble', f'Apertura: {", ".join(t for t, _, _ in par)}', izq + '\n        ' + der)
    total += 1
    for j in range(k, min(k + 2, len(hojas_g))):
        vistas += vista('v-una', f'Fotografías, hoja {j + 1}', hojas_g[j])
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
# Las fotos se bajan a medida que se pasan las páginas (js/libro.js), no todas de golpe.
html = html.replace(' src="img/g/', ' data-src="img/g/')
open(os.path.join(AQUI, 'index.html'), 'w', encoding='utf-8', newline='\n').write(html)
print('index.html listo:', n, 'laminas,', total, 'vistas')
