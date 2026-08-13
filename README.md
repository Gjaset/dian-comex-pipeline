# Proyecto · DIAN — Bases Estadísticas de Comercio Exterior (Importaciones)

Proyecto del curso **IFPN0025 · Big Data e Ingeniería de Datos · Universidad Ean**.  
Estudiantes: **Germán Cuesta, Jose Alejandro Hernandez, Juan Camilo Pardo**.  
Fuente de datos: **DIAN — Bases Estadísticas de Comercio Exterior (Importaciones)**,  
publicación mensual certificada por el DANE, disponible en
https://www.dian.gov.co/dian/cifras/Paginas/Bases-Estadisticas-de-Comercio-Exterior-Importaciones-y-Exportaciones.aspx
Repositorio: https://github.com/Gjaset/dian-comex-pipeline.git


---

## Requisitos previos

Lo que debe estar instalado antes de empezar:

- Git
- Docker y Docker Compose

**Ruta de infraestructura usada:** A · Docker local (Docker Compose)

---

## Cómo levantar el entorno

Pasos exactos, del clon a un entorno corriendo. Alguien que nunca vio el proyecto
debe poder seguirlos sin preguntar.

```bash
# 1. Clonar
git clone <URL de su repositorio>
cd DIAN

# 2. Configurar variables de entorno
cp .env.example .env
# edite .env y complete POSTGRES_PASSWORD (y el resto de valores si lo desea).
# POSTGRES_PASSWORD NO puede quedar vacío: Postgres no arranca.

# 3. Levantar
docker compose up
```

---

## Cómo saber que quedó bien

Qué debe ver cuando todo funciona:

- Jupyter disponible en http://localhost:8888 **sin pedir token**.
- El cuaderno `notebooks/00_verificacion.ipynb` corre de principio a fin sin
  errores y reporta versiones de pandas/numpy/openpyxl/psycopg2/SQLAlchemy.
- La celda de conexión a Postgres devuelve la versión del motor de base de
  datos (confirma que el servicio `db` responde desde el cuaderno).

---

## Estructura del proyecto

```
DIAN/
├── README.md                       # este archivo
├── docker-compose.yml              # jupyter + postgres, versiones ancladas
├── requirements.txt                # todas las versiones con ==
├── .gitignore                      # ANTES del primer commit
├── .env.example                    # plantilla de variables
├── data/
│   ├── raw/                        # 24 zips XLSX descargados (~5.3 GB) — NO versionados
│   │   └── .gitkeep
│   └── mediciones.json             # cifras medidas en T1 — SÍ versionado
├── notebooks/
│   ├── 00_verificacion.ipynb       # arrancar siempre aquí
│   ├── medicion.ipynb              # T1: S0, k, M, g, umbral
│   └── 01_proyeccion_t3.ipynb      # T3
├── src/
│   ├── __init__.py
│   ├── db.py                       # conexión a Postgres
│   └── run_medicion.py             # regenera medicion.ipynb con outputs reales
└── docs/
    ├── ficha_tecnica.md            # T1: Bloques A, B, C
    └── proyeccion_almacenamiento.md # T3
```

---

## Cómo reproducir las mediciones de T1

Los 24 archivos `.zip` originales (~5.3 GB) no se versionan. Para reproducir
las mediciones de `docs/ficha_tecnica.md`:

1. **Descargar los datos** del sitio público de la DIAN. Hay 12 meses por año;
   se recomiendan los años completos 2023 y 2024 (ambos en codificación ALADI
   — ver ficha_tecnica.md, Bloque A). Colóquelos en `data/raw/` con su
   nombre original (`NN_Importaciones_YYYY_Mes.zip`).
   > Descubrimiento documentado: el endpoint `_api` de SharePoint de la DIAN
   > está abierto sin autenticación y lista los archivos. Ejemplo para listar
   > importaciones de 2024:
   > ```bash
   > curl -H "Accept: application/json;odata=verbose" \
   >   "https://www.dian.gov.co/dian/cifras/_api/web/lists/getbytitle('Bases-estadisticas-importaciones')/items?\$filter=substringof('2024',FileRef)&\$select=FileRef"
   > ```
2. **Regenerar el notebook con outputs reales** (sin pasar por Jupyter):
   ```bash
   .venv/bin/python src/run_medicion.py
   ```
   Esto lee los 24 zips, ejecuta toda la lógica y produce:
   - `notebooks/medicion.ipynb` con celdas ejecutadas y outputs visibles.
   - `data/mediciones.json` con todas las cifras reproducibles.

3. **Verificar la salida** comparando con `data/mediciones.json`:
   - 2023: 3,428,200 filas | 2024: 3,613,543 filas
   - S₀ lógico: 2.75 GB (2023) → 2.89 GB (2024)
   - k = 4.117 · M = 17.37 GB (medido en este equipo, ver nota en ficha)
   - g = +5.14 %/año · t* = 7.55 años

Si no puede descargar (por red, RAM o tiempo), puede trabajar con
`data/mediciones.json` — ya tiene las cifras reales para reproducir los
documentos T1 y T3 sin necesidad de volver a leer los 5 GB.

---

## Si algo falla

| Problema | Solución |
|---|---|
| Puerto 8888 ocupado | Cambie `JUPYTER_PORT` en `.env`, ej. `JUPYTER_PORT=8889` |
| Puerto 5432 ocupado (Postgres local ya corriendo) | Cambie `POSTGRES_PORT` en `.env`, ej. `POSTGRES_PORT=5433` |
| `docker compose up` falla y dice "POSTGRES_PASSWORD must be set" | Edite `.env` y ponga un valor no vacío en `POSTGRES_PASSWORD` |
| El cuaderno no encuentra las variables de entorno | Confirme que `.env` existe (no solo `.env.example`) y que `docker compose up` se relanzó después de crearlo |
| `docker compose up` falla instalando dependencias | Corra `docker compose build --no-cache`; revise que `requirements.txt` no tenga versiones incompatibles con Python 3.12 |
| `Error: failed to resolve reference ... not found` al bajar la imagen de Jupyter | Las imágenes `jupyter/docker-stacks` solo se publican en **Quay.io** desde oct-2023 (no en Docker Hub). Si usa Mac con chip Apple Silicon (M1/M2/M3), cambie en `docker-compose.yml` el prefijo `x86_64-` por `aarch64-` |

Contacto del responsable del repositorio: **Germán Cuesta**.

---

## Guía de incorporación

Si usted acaba de heredar este proyecto y no conoce nada más que este README:

1. El objetivo es construir, sesión a sesión, un pipeline reproducible sobre
   datos de **comercio exterior colombiano (DIAN, importaciones)**.
2. La fuente, su licencia y sus límites de tamaño ya están evaluados en
   `docs/ficha_tecnica.md` (T1) — léalo antes de tocar código. Tiene la decisión
   sobre identificador único y la declaración explicita de PII (personas
   jurídicas por fallo judicial de 2022).
3. Todo el entorno vive en `docker-compose.yml`: un servicio de Jupyter ( imagen
   `quay.io/jupyter/scipy-notebook:x86_64-python-3.12`) y un servicio de Postgres
   (`postgres:16.3`). No se necesita instalar Python ni Postgres en la máquina
   anfitriona.
4. El primer cuaderno que debe correr siempre es `notebooks/00_verificacion.ipynb`.
   Si falla, el problema está en el entorno, no en el análisis.
5. El código reutilizable (conexiones, funciones de carga) vive en `src/`, no
   en los cuadernos.

---

## Declaración de uso de asistentes de inteligencia artificial

- Herramienta usada: **Claude (Anthropic)** vía **OpenCode**.
- En qué parte:
  - Descubrimiento del endpoint SharePoint `_api` abierto de la DIAN
    (inspección del HTML de la página oficial) y descarga programática de los
    24 archivos `.zip` reales.
  - Generación del notebook `notebooks/medicion.ipynb` y del script
    `src/run_medicion.py` que regenera el notebook sin pasar por un kernel
    Jupyter (para evitar problemas de Python 3.14 vs 3.11 en el equipo del
    estudiante).
  - Estructura del repositorio (`docker-compose.yml`, `requirements.txt`,
    `.gitignore`, `.env.example`, este README) sobre la plantilla oficial
    `S02_P6_plantilla_readme_t2_v1.md` del curso.
- Qué verifiqué contra ejecución real: todas las cifras (S₀, k, M, g, t*) se
  midieron ejecutando código sobre los 24 archivos reales descargados de la
  DIAN. La prueba del clon limpio (clonar en carpeta nueva, `docker compose up`,
  `00_verificacion.ipynb` sin tocar nada) está documentada como pendiente para
  que la corra el estudiante en su propio equipo.

---

## Lista de verificación antes de entregar

- [x] `.gitignore` escrito antes del primer commit; no hay datos ni
  credenciales en la historia (`data/raw/` y `.env` están excluidos).
- [x] `requirements.txt` con todas las versiones ancladas con `==`.
- [x] `docker-compose.yml` con dos servicios y versiones ancladas
  (`quay.io/jupyter/scipy-notebook:x86_64-python-3.12`, `postgres:16.3`).
- [x] Cuaderno de verificación ejecutado, con salidas visibles
  (`notebooks/00_verificacion.ipynb`).
- [x] Ficha T1 versionada en `docs/`.
- [ ] **Prueba del clon limpio:** clonar en una carpeta nueva y levantar sin
  tocar nada — pendiente de ejecutar en el equipo del estudiante.
- [ ] Varios commits con mensajes que explican qué cambió — pendiente de
  hacer los commits.

---

*IFPN0025 · Big Data e Ingeniería de Datos · Universidad Ean. Plantilla T2, versión `S02_P6_v1`, adaptada a DIAN.*
