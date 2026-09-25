#!/usr/bin/env python3
"""Renderiza los diagramas C4 del Hito A (T8) como PNG con PIL.
Solo ASCII (la fuente bitmap no trae tildes). Regenerar: python3 este script
desde la raiz del repo; sale a docs/c4/.
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1400, 900
BG = "white"
PERSON = (8, 66, 123)
SYSTEM = (17, 104, 189)
EXTERNAL = (120, 120, 120)
CONTAINER = (67, 141, 213)
DB = (27, 99, 168)
TXT = (255, 255, 255)
ARROW = (60, 60, 60)

F = ImageFont.load_default(size=22)
FS = ImageFont.load_default(size=16)
FT = ImageFont.load_default(size=18)


import math


def head(d, x1, y1, dx, dy):
    a = math.atan2(dy, dx)
    L, s = 14, 0.42
    p1 = (x1 - L * math.cos(a - s), y1 - L * math.sin(a - s))
    p2 = (x1 - L * math.cos(a + s), y1 - L * math.sin(a + s))
    d.polygon([(x1, y1), p1, p2], fill=ARROW)


def box(d, xy, fill, title, tech, desc):
    x0, y0, x1, y1 = xy
    d.rounded_rectangle(xy, radius=12, fill=fill, outline=None)
    d.text((x0 + 14, y0 + 10), title, font=F, fill=TXT)
    d.text((x0 + 14, y0 + 40), tech, font=FS, fill=TXT)
    d.text((x0 + 14, y0 + 62), desc, font=FS, fill=TXT)


def label(d, mx, my, text):
    tw = d.textlength(text, font=FS)
    d.rectangle([mx - tw / 2 - 6, my - 20, mx + tw / 2 + 6, my - 2], fill=BG)
    d.text((mx - tw / 2, my - 20), text, font=FS, fill=ARROW)


def arrow(d, x0, y0, x1, y1, text, tpos=None):
    d.line([x0, y0, x1, y1], fill=ARROW, width=3)
    head(d, x1, y1, x1 - x0, y1 - y0)
    if tpos is None:
        tpos = ((x0 + x1) // 2, (y0 + y1) // 2)
    label(d, tpos[0], tpos[1], text)


def poly(d, pts, text, tpos):
    d.line(pts, fill=ARROW, width=3, joint="curve")
    (x0, y0), (x1, y1) = pts[-2], pts[-1]
    head(d, x1, y1, x1 - x0, y1 - y0)
    label(d, tpos[0], tpos[1], text)


def contexto():
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.text((40, 20), "C4 Nivel 1 - Contexto: Plataforma de datos DIAN Importaciones",
           font=FT, fill=(0, 0, 0))
    box(d, (520, 330, 880, 470), SYSTEM, "Plataforma de datos",
        "[Sistema]", "FOB por mes x aduana, informes y alertas")
    box(d, (120, 120, 400, 230), PERSON, "Analista de comercio",
        "[Persona]", "Explora tendencias, arma informes")
    box(d, (1000, 120, 1280, 230), PERSON, "Gerencia",
        "[Persona]", "Decide con reportes, atiende alertas")
    box(d, (120, 600, 400, 710), EXTERNAL, "Portal DIAN",
        "[Sistema externo]", "Publica ZIP mensuales (rezago 45 d)")
    box(d, (1000, 600, 1280, 710), EXTERNAL, "DANE - metodologia",
        "[Sistema externo]", "Marco de calidad (referencia)")
    arrow(d, 400, 665, 520, 430, "ZIP mensuales (HTTPS)")
    arrow(d, 700, 330, 260, 230, "informes y refinada (lotes)")
    arrow(d, 880, 380, 1000, 175, "reportes + alertas")
    arrow(d, 1140, 600, 760, 470, "metodologia (referencia)")
    im.save("docs/c4/contexto.png")


def contenedor():
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.text((40, 16), "C4 Nivel 2 - Contenedor: interior de la Plataforma (hibrido T7)",
           font=FT, fill=(0, 0, 0))
    box(d, (40, 90, 240, 180), EXTERNAL, "Portal DIAN", "[Ext]", "ZIP mensuales")
    box(d, (300, 90, 590, 200), CONTAINER, "Ingesta mensual",
        "[Python + boto3]", "Descarga ZIP, carga cruda (S3)")
    box(d, (650, 90, 1040, 200), DB, "Lago por capas",
        "[MinIO S3]", "cruda/refinada/consolidada + versionado")
    box(d, (1100, 90, 1360, 180), EXTERNAL, "Analista/Gerencia", "[Ext]", "personas")
    box(d, (40, 300, 380, 410), CONTAINER, "Motor batch",
        "[Hadoop Streaming/YARN]", "FOB por mes x aduana + combiner")
    box(d, (440, 300, 780, 410), CONTAINER, "Cuadernos analisis",
        "[Jupyter + pandas]", "Perfil T1/T3, exploracion")
    box(d, (840, 300, 1180, 410), CONTAINER, "Flujo acotado",
        "[Stream, alcance T7]", "Alertas en minutos (1 requisito)")
    box(d, (440, 500, 780, 600), DB, "Base analitica",
        "[PostgreSQL 16.3]", "Agregados para informes (SQL)")
    arrow(d, 240, 135, 300, 135, "ZIP (HTTPS)", tpos=(270, 84))
    arrow(d, 590, 135, 650, 135, "S3 API")
    arrow(d, 650, 200, 210, 300, "lee cruda")
    arrow(d, 610, 300, 700, 200, "explora (S3)")
    arrow(d, 900, 200, 1010, 300, "vigila refinada")
    arrow(d, 1010, 300, 1230, 180, "alertas (minutos)")
    arrow(d, 610, 410, 610, 500, "carga agregados (SQL)")
    poly(d, [(150, 410), (150, 480), (810, 480), (810, 200)],
         "escribe consolidada", (330, 470))
    poly(d, [(780, 550), (1300, 550), (1300, 135), (1352, 135)],
         "informes (SQL)", (1040, 540))
    im.save("docs/c4/contenedor.png")


contexto()
contenedor()
print("PNG generados en docs/c4/")
