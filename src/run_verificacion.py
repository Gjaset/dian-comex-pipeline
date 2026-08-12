#!/usr/bin/env python3
"""Genera notebooks/00_verificacion.ipynb con outputs sintéticos (sin docker).
El notebook en producción corre dentro del contenedor Jupyter con la BD disponible.
Aquí solo creamos el .ipynb con la estructura correcta; el estudiante lo ejecuta
la primera vez dentro del contenedor con `docker compose up`.
"""
import os, nbformat as nbf

nb = nbf.v4.new_notebook()
nb.metadata.kernelspec = {"display_name":"Python 3 (ipykernel)","language":"python","name":"python3"}
nb.metadata.language_info = {"name":"python","version":"3.12"}

def md(s): nb.cells.append(nbf.v4.new_markdown_cell(source=s))
def code(s): nb.cells.append(nbf.v4.new_code_cell(source=s))

nb.cells = []

md("""# 00 · Verificación del entorno

**Proyecto:** DIAN — Bases Estadísticas de Comercio Exterior (Importaciones).  
**Curso:** IFPN0025 · Big Data e Ingeniería de Datos · Universidad Ean.

Este cuaderno **arranca siempre aquí**. Confirma que el entorno Docker levantó
bien y que tanto las dependencias como la conexión a Postgres funcionan. Si
algo falla aquí, el problema está en el entorno, no en el análisis.""")

md("""## 1. Versiones de las librerías instaladas por `requirements.txt`""")

code("""import sys
print(f'Python: {sys.version.split()[0]}')
import pandas, numpy, openpyxl, requests, sqlalchemy, dotenv
import psycopg2
print(f'pandas     {pandas.__version__}')
print(f'numpy      {numpy.__version__}')
print(f'openpyxl   {openpyxl.__version__}')
print(f'requests   {requests.__version__}')
print(f'SQLAlchemy {sqlalchemy.__version__}')
print(f'psycopg2   {psycopg2.__version__}')
print(f'dotenv     {getattr(dotenv, "__version__", "n/d")}')
import os
print()
print('Variables de entorno (enmascaradas):')
for k in ('POSTGRES_DB','POSTGRES_USER','POSTGRES_HOST','POSTGRES_PORT','JUPYTER_PORT'):
    print(f'  {k} = {os.environ.get(k, "<no definida>")}')
print(f'  POSTGRES_PASSWORD = {"<set>" if os.environ.get("POSTGRES_PASSWORD") else "<VACIO - Postgres no arrancará>"}')""")

md("""## 2. Conexión a Postgres

Verifico que el servicio `db` del `docker-compose.yml` responde desde el
cuaderno y reporto la versión del motor.""")

code("""from sqlalchemy import text
from sqlalchemy import create_engine
import os

url = (
    f"postgresql+psycopg2://"
    f"{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}"
    f"@{os.environ.get('POSTGRES_HOST', 'db')}:"
    f"{os.environ.get('POSTGRES_PORT', '5432')}"
    f"/{os.environ['POSTGRES_DB']}"
)
engine = create_engine(url, pool_pre_ping=True)
with engine.connect() as conn:
    version = conn.execute(text('SELECT version();')).scalar()
    print('Conexión OK. Versión de Postgres:')
    print(version)""")

md("""## 3. Sanity check — acceso a los datos del proyecto

Confirmo que el volumen `./data` está montado en el contenedor y que puedo ver
tanto `raw/` (datos crudos, no versionados) como `mediciones.json` (cifras
medidas en T1, versionadas).""")

code("""import os, json
print('Contenido de /home/jovyan/work/data:')
for root, dirs, files in os.walk('/home/jovyan/work/data'):
    depth = root.replace('/home/jovyan/work/data', '').count('/')
    if depth > 2: continue
    print('  ' * depth + os.path.basename(root) + '/')
    for f in sorted(files)[:10]:
        sz = os.path.getsize(os.path.join(root, f)) / 1024**2
        print('  ' * (depth+1) + f + f'  ({sz:.2f} MB)' if sz < 100 else f'  ({sz/1024:.2f} GB)')
# mediciones.json debe existir y contener las cifras medidas en T1
mp = '/home/jovyan/work/data/mediciones.json'
if os.path.exists(mp):
    m = json.load(open(mp))
    print()
    print('mediciones.json OK. Cifras medidas en T1:')
    print(f"  Filas 2023: {m['filas_por_anio']['2023']:,}")
    print(f"  Filas 2024: {m['filas_por_anio']['2024']:,}")
    print(f"  k = {m['k']:.4f}")
    print(f"  M = {m['M_GB']:.4f} GB")
    print(f"  g anual = {m['g_anual']*100:+.2f}%")
    print(f"  t* = {m.get('t_estrella', float('nan')):.2f} años")
else:
    print('AVISO: data/mediciones.json no existe. Corra src/run_medicion.py para generarlo.')""")

md("""## 4. Carga de utilidades propias (`src/`)

Verifico que puedo importar el módulo `src.db` que se usará en cuadernos
posteriores.""")

code("""import sys
sys.path.insert(0, '/home/jovyan/work')
try:
    from src.db import engine, get_connection
    print('Import OK: src.db.engine, src.db.get_connection')
    with get_connection() as conn:
        v = conn.execute(__import__('sqlalchemy').text('SELECT current_database();')).scalar()
        print(f'Conexión a base: {v}')
except Exception as e:
    print(f'Import src.db falló: {type(e).__name__}: {e}')
    print('Si va a usar src.db en otros notebooks, revise src/db.py y POSTGRES_* en .env.')""")

md("""## 5. Veredicto

Si TODAS las celdas anteriores corrieron sin excepción, el entorno está
listo. Proceda a `notebooks/medicion.ipynb` (T1) y a `notebooks/01_proyeccion_t3.ipynb` (T3).

Si la celda de conexión a Postgres falló:
- Confirme que `.env` tiene `POSTGRES_PASSWORD` no vacío.
- Confirme que corrió `docker compose up` (no `docker compose up jupyter` solo).
- Revise `docker compose logs db` para ver si Postgres reportó algún error.""")

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'notebooks', '00_verificacion.ipynb')
with open(path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)
print(f"Generado: {path} ({len(nb.cells)} celdas)")
