#!/usr/bin/env python3
"""Genera notebooks/01_proyeccion_t3.ipynb con outputs reales.
Lee data/mediciones.json (producido por src/run_medicion.py) y calcula:
- Volumen lógico proyectado a 12 meses = S0 * (1+g_mensual)^12
- Número de bloques HDFS (128 MB) = ceil(vol / 128 MB)
- Almacenamiento físico por factor de réplica R = VOL * R
- Tolerancia a fallos = R - 1
- Tabla comparativa para R = 1, 2, 3
"""
import os, json, math, nbformat as nbf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# cargar mediciones reales de T1
with open(os.path.join(ROOT, 'data', 'mediciones.json'), encoding='utf-8') as f:
    m = json.load(f)

S0 = m['S0_logico_GB']['2024']          # 2.8913 GB (volumen lógico del año 2024)
g_anual = m['g_anual']                  # 0.051354
g_mensual = m['g_mensual']              # 0.004182
k = m['k']                              # 4.1172
M_gb = m['M_GB']                        # 17.37 GB
BLOQUE_MB = 128                          # MB - valor real de HDFS en producción

# cálculos
vol_12m_GB = S0 * (1 + g_mensual) ** 12
vol_12m_MB = vol_12m_GB * 1024
n_bloques = math.ceil(vol_12m_MB / BLOQUE_MB)

# construir notebook
nb = nbf.v4.new_notebook()
nb.metadata.kernelspec = {"display_name":"Python 3 (ipykernel)","language":"python","name":"python3"}
nb.metadata.language_info = {"name":"python","version":"3.12"}

def md(s): nb.cells.append(nbf.v4.new_markdown_cell(source=s))
def code(s, captured=None):
    c = nbf.v4.new_code_cell(source=s)
    nb.cells.append(c)

nb.cells = []

md("""# T3 · Proyección de crecimiento y factor de réplica

**Curso:** IFPN0025 · Big Data e Ingeniería de Datos · Universidad Ean.  
**Estudiante:** Germán Cuesta.

Este cuaderno automatiza la tabla de proyección de la entrega T3 a partir de
las mediciones reales de T1 (`data/mediciones.json`). Reproduce los números
de `docs/proyeccion_almacenamiento.md`.""")

md("""## 1. Datos de entrada (trazabilidad)""")

code(f"""import json, math

with open('../data/mediciones.json', encoding='utf-8') as f:
    m = json.load(f)

S0_GB       = m['S0_logico_GB']['2024']   # volumen lógico del año 2024 (GB)
g_anual     = m['g_anual']
g_mensual   = m['g_mensual']
k           = m['k']
M_GB        = m['M_GB']
BLOQUE_MB   = 128

print(f"S0 (2024, logico)            = {{S0_GB:.4f}} GB  (de medicion.json)")
print(f"g anual                      = {{g_anual:+.6f}}  ({{g_anual*100:+.2f}}%/año)")
print(f"g mensual                    = {{g_mensual:+.6f}}  ({{g_mensual*100:+.3f}}%/mes)")
print(f"k (factor de expansion)      = {{k:.4f}}")
print(f"M (memoria util disponible)  = {{M_GB:.4f}} GB")
print(f"Tamano de bloque HDFS        = {{BLOQUE_MB}} MB (valor real de produccion, no el didactico)")
""")

md("""## 2. Cálculo del volumen lógico a 12 meses y del número de bloques

Fórmulas:

```
Volumen_12m  = S0 * (1 + g_mensual)^12
N_bloques    = ceil((Volumen_12m en MB) / 128 MB)
```

`S0` aquí es el volumen lógico (no el comprimido), porque el umbral de HDFS
se calcula sobre el archivo que efectivamente se distribuye en el sistema de
archivos distribuido — y eso es el XLSX descomprimido, no el zip de llegada.""")

code("""vol_12m_GB = S0_GB * (1 + g_mensual) ** 12
vol_12m_MB = vol_12m_GB * 1024
n_bloques  = math.ceil(vol_12m_MB / BLOQUE_MB)

print(f"Volumen a 12 meses  = {S0_GB:.4f} * (1 + {g_mensual:.6f})^12")
print(f"                     = {S0_GB:.4f} * {(1+g_mensual)**12:.6f}")
print(f"                     = {vol_12m_GB:.4f} GB  ({vol_12m_MB:.2f} MB)")
print(f"N.º de bloques (128 MB) = ceil({vol_12m_MB:.2f} / {BLOQUE_MB}) = {n_bloques}")
""")

md("""## 3. Tabla por factor de réplica (R = 1, 2, 3)

Para cada R:

```
Almacenamiento físico (R) = Volumen lógico * R
Tolerancia a fallos (R)   = R - 1   (n.º de copias que pueden perderse sin perder el dato)
N.º de bloques            = no depende de R (R replica bloques, no los divide)
```""")

code("""print(f"{'R':>3} {'Volumen lógico (GB)':>22} {'Almacenamiento físico (GB)':>28} {'N.º bloques':>12} {'Tolerancia':>12}")
print('-' * 80)
for R in (1, 2, 3):
    fisico_GB = vol_12m_GB * R
    tol = R - 1
    print(f"{R:>3} {vol_12m_GB:>22.4f} {fisico_GB:>28.4f} {n_bloques:>12} {tol:>12} nodos")
""")

md("""## 4. Recomendación de factor de réplica

Justificación por valor del dato y por costo (texto completo en `docs/proyeccion_almacenamiento.md`).
Aquí solo se reporta el número y la justificación resumida.""")

code("""recomendacion_R = 3
print(f"Recomendación: R = {recomendacion_R}")
print()
print(f"Resumen de la justificación:")
print(f"- El dato es regenerable (fuente pública DIAN, se puede descargar de nuevo),")
print(f"  lo que normalmente empujaría a R=2.")
print(f"- PERO la regeneración no es ni instantánea ni trivial: son 5.3 GB de zips")
print(f"  descargados de un sitio SharePoint, con fallas intermitentes (algunos downloads")
print(f"  que se cortaron en este proyecto requirieron reintentos manuales).")
print(f"- El costo de replicar es MARGINAL a esta escala (~3 GB por copia extra):")
print(f"     R=2 -> R=3 implica {vol_12m_GB:.2f} GB adicionales, trivial para cualquier clúster real.")
print(f"- Por lo tanto, R=3 es la opción defendible cuando el dato es pequeño.")
print(f"  Esta recomendación CAMBIARÍA a R=2 o R=1 a escala de TB, donde el costo de la")
print(f"  tercera copia dejaría de ser marginal.")
""")

md("""## 5. Persistencia de los resultados

Guardo las cifras de la proyección junto a las de T1 en `data/mediciones.json`
para que el documento T3 se pueda regenerar sin recalcular.""")

code("""m.update({
    'T3_volumen_12m_GB': vol_12m_GB,
    'T3_n_bloques_128MB': n_bloques,
    'T3_bloque_MB': BLOQUE_MB,
    'T3_R_recomendado': recomendacion_R,
    'T3_tabla_R': {str(R): {'volumen_logico_GB': vol_12m_GB, 'almacenamiento_fisico_GB': vol_12m_GB*R, 'n_bloques': n_bloques, 'tolerancia_nodos': R-1} for R in (1,2,3)},
})
with open('../data/mediciones.json', 'w', encoding='utf-8') as f:
    json.dump(m, f, indent=2)
print('Proyección T3 guardada en ../data/mediciones.json')
print()
print('--- Resumen T3 ---')
print(f"Volumen proyectado a 12 meses: {vol_12m_GB:.4f} GB")
print(f"N.º de bloques HDFS (128 MB):  {n_bloques}")
print(f"Factor recomendado:           R = {recomendacion_R}")
""")

path = os.path.join(HERE, '..', 'notebooks', '01_proyeccion_t3.ipynb')
with open(path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)
print(f"\nGenerado: {path} ({len(nb.cells)} celdas)")
