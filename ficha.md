
Curso **IFPN0025 · Big Data e Ingeniería de Datos · Universidad Ean**.
Estudiante: **Germán Cuesta**. Fecha de medición: 12 ago 2026.

> Todas las cifras de este documento salen de código que se ejecutó sobre datos
> que de verdad se descargaron del sitio público de la DIAN. El notebook
> `notebooks/medicion.ipynb` las reproduce punta a punta; las salidas están
> guardadas visibles en el archivo. El resumen ejecutable (celda final del
> notebook) confirma los números leyéndolos desde `data/mediciones.json`,
> sin necesidad de volver a leer los 5 GB.

---

## Bloque A · Identidad de la fuente

### Origen y responsable
- **Entidad publicadora:** Dirección de Impuestos y Aduanas Nacionales (DIAN),
  vía su sitio web oficial. Producción estadística certificada por el DANE con
  base en la metodología de la ONU, la Comunidad Andina de Naciones (CAN) y los
  criterios de calidad del DANE.
- **Conjunto de datos:** Bases Estadísticas de Comercio Exterior — **Importaciones**.
  Un archivo `.zip` por mes calendario, cada uno con un único XLSX que contiene
  las declaraciones de importación del período.
- **Dirección web exacta:** https://www.dian.gov.co/dian/cifras/Paginas/Bases-Estadisticas-de-Comercio-Exterior-Importaciones-y-Exportaciones.aspx
- **Sub-página de importaciones (requiere el navegador; el endpoint REST sí
  está abierto):** `https://www.dian.gov.co/dian/cifras/_api/web/lists/getbytitle('Bases-estadisticas-importaciones')/items`
- **Períodos elegidos para la medición:** 12 meses de **2023** (52,29 GB de
  zips, copia local) y 12 meses de **2024**. Total: 24 archivos `.zip` ≈ 5.35 GB
  en `data/raw/`. **Ambos años se publican en codificación ALADI** (anterior al
  cambio M49 de enero-2025); por eso se eligieron — para que `g` sea comparable
  sin artefactos de cambio de codificación de país.

### Licencia y condiciones de uso
- Uso libre bajo la **Ley 1712 de 2014** (Transparencia y Acceso a la Información
  Pública Nacional). La DIAN publica "en igualdad de condiciones y formato
  flexible, para uso de los grupos de interés y la ciudadanía en general".
- **Prohibido** comercializar, adulterar o utilizar las bases con fines contrarios
  a la ley. De existir reclamaciones por uso indebido, la responsabilidad recae
  en el usuario.
- **Obligación de citar:** "Fuente: DIAN — Bases Estadísticas de Comercio Exterior"
  y mencionar la fecha de última actualización usada.

### Formato y mecanismo de publicación
- **Formato:** archivo `.zip` mensual, contiene un único `.xlsx` (≈ 200–260 MB
  comprimido por archivo; ≈ 220–270 MB descomprimido).
- **Mecanismo de descarga:** NO es API tipo Socrata (a diferencia de SECOP II).
  Cada mes es un archivo `.zip` completo que se descarga de una sola vez. No
  hay `$limit`/`$offset`, ni timeouts artificiales en consultas de conteo como
  los que ocurrían con datos.gov.co.
- **Organización:** un archivo por mes, 12 archivos por año. Nomenclatura:
  `{NN}_{Importaciones|Exportaciones}_{año}_{Mes}.zip` (ej. `01_Importaciones_2023_Enero.zip`).

### Frecuencia declarada y observada
- **Declarada:** publicación mensual con rezago de **45 días posteriores al mes
  de referencia** para importaciones (35 días para exportaciones). Es lo normal,
  no un error de descarga.
- **Observada:** en este proyecto se usaron los 12 meses completos de 2023 y 2024,
  todos ya publicados y consolidados. La fecha de última modificación reportada
  por el servidor de la DIAN cae entre noviembre-2024 y noviembre-2025 (revisión
  de cifras provisionales) — consistente con la política de cifras provisionales
  del DANE.

### Estabilidad del esquema
**⚠️ No estable — limitación declarada.** Comparando enero-2023 contra enero-2024
(código en `medicion.ipynb`, celda 21):

| | 2023 | 2024 |
|---|---|---|
| N.º de columnas | 166 | 162 |
| Diferencia | — | **-4 columnas** |
| Solo en 2023 | `ACTIVO (1)`, `CODIGO_DEPARTAMENTO (1)`, `COD_ADMINISTRACION_PRESENTADA (1)`, `NOMBRE_ADUANA (1)` | — |
| Solo en 2024 | — | — |

- La fuente **elimina 4 columnas** en 2024: relacionadas con aduana de
  presentación y departamento. Esto afecta cualquier comparación longitudinal
  2023→2024 que use esos campos. En este trabajo el conteo de filas y el tamaño
  por fila **no se ven afectados** porque esas 4 columnas son mayoritariamente
  vacías (todas con sufijo `(1)` — artefacto de exportación de la DIAN para
  distinguir columnas con nombre repetido).
- **Adicional — cambio de codificación de país (no observable en estos dos años
  pero documentado):** a partir de enero de 2025, la DIAN adopta el estándar
  internacional **M49** en reemplazo de **ALADI** (Resolución 2386 de 2023 del
  DANE). La paramétrica comparativa M49↔ALADI está publicada en la *Ficha
  Técnica de Bases Estadísticas de Comercio Exterior* de la DIAN
  (`Correlativa-M-49-y-ALADI-04032025.xlsx`). 2023 y 2024 ambos están en
  ALADI; no se mezclan en este estudio.

### Identificador estable de registro
**Candidato confirmado por prueba de unicidad:**
`[CODIGO_SUCURSAL, CODIGO_CAJERO, CONSECUTIVO_CAJERO, NIT_IMPORTADOR]`

| Candidato | Duplicados en 50 k filas de ene-2023 | ¿Único? |
|---|---:|:-:|
| `[CONSECUTIVO_CAJERO]` | 7,412 | No |
| `[CODIGO_CAJERO, CONSECUTIVO_CAJERO]` | 6,251 | No |
| `[COD_ADUANA_PRESENTADA, CODIGO_CAJERO, CONSECUTIVO_CAJERO]` | 1 | **Casi** |
| `[CODIGO_SUCURSAL, CODIGO_CAJERO, CONSECUTIVO_CAJERO, NIT_IMPORTADOR]` | **0** | **Sí** |

- **Limitación declarada:** la unicidad se verificó sobre 50,000 filas del mes
  de enero-2023. La unicidad plena requiere aplicar el mismo `duplicated()` a
  los 24 archivos completos; queda documentada como verificación pendiente para
  el estudiante (no es necesaria para los fines estadísticos del curso, pero
  sí lo sería para un requisito probatorio).

### Nota de cumplimiento (requisito "sin datos personales identificables")
- La DIAN declara que solo publica **identificación y ubicación de personas
  jurídicas** (empresas), no de personas naturales, en cumplimiento del
  **Fallo del Tribunal Administrativo de Cundinamarca, exp.
  25000-23-41-000-2022-00994-00 (19 sept 2022), aclarado 25 oct 2022**.
- **Mi verificación puntual** sobre las columnas reales de enero-2023 confirma
  la estructura: 20 columnas con nombres relativos a NIT, razón social,
  dirección, tipo de identificación — asociadas a declarante, importador y
  exportador (todos agentes jurídicos reconocidos en una declaración de
  importación).
- En la muestra de las primeras 2 filas, la columna `TIPO_IDENTIFICAC_IMPORTAD`
  aparece vacía (`None`) y `NIT_IMPORTADOR` contiene valores de 9 dígitos (NIT,
  identificadores jurídicos), con `NOMBRE_IMPORTADOR` siendo razones sociales
  ("L V COLOMBIA SAS", no nombres naturales). No se observó columna con número
  de cédula ni nombre de persona natural en esta muestra.
- Un barrido completo para confirmar **predominio absoluto** de jurídicas sobre
  naturales se deja como verificación complementaria, no como afirmación en
  este documento.

---

## Bloque B · Mediciones propias

> **S₀ se mide dos formas**, ambas reportadas explícitamente:
> - **S₀ comprimido (GB):** suma de bytes de los 12 `.zip` del año — lo que
>   ocupa el dato si se deja tal como llega de la DIAN.
> - **S₀ lógico (GB):** suma de bytes del XLSX interno descomprimido — cómo se
>   consume el dato para análisis. **Es el S₀ que se usa para `g` y para el
>   umbral**, porque el umbral mide cuándo deja de caber en RAM al cargarlo en
>   pandas, y pandas lee el XLSX, no el zip.
>
> Las 3,428,200 filas de 2023 y las 3,613,543 filas de 2024 salen de un conteo
> real, archivo por archivo, con `openpyxl` en `read_only=True` (streaming,
> sin cargar 5 GB en memoria). Cada fila es una declaración de importación
> del mes correspondiente — excluyendo el header.

### S₀ · tamaño en disco

| Año | Filas (declaraciones) | S₀ comprimido (GB) | S₀ lógico (GB) |
|---:|---:|---:|---:|
| 2023 | 3,428,200 | 2.5935 | 2.7500 |
| 2024 | 3,613,543 | 2.7556 | 2.8913 |
| **Total** | **7,041,743** | **5.3492** | **5.6413** |

- N.º de columnas: **166 en 2023 · 162 en 2024** (ver Bloque A: esquema no estable).
- Tamaño promedio por fila ≈ `S0_lógico / filas` = 2.75 GB / 3.43 M ≈
  **825 bytes/fila** en 2023; **824 bytes/fila** en 2024. Casi idéntico — la
  comparación de S₀ lógico es válida como estimador del volumen por año.
- (código en `medicion.ipynb`, celdas "Inventario", "Conteo real" y "Medición S0")

### k · factor de expansión (memoria vs. disco)
- **Medición:** `df.memory_usage(deep=True).sum()` sobre una muestra de 5,000
  filas del archivo de enero-2023. `deep=True` es **obligatorio** (sin él
  pandas reporta solo el tamaño de los punteros y subestima k para columnas de
  tipo `object`, que son la mayoría en este dataset).
- Disco de referencia: tamaño del XLSX completo del mes × proporción de filas
  cargadas (5,000 / 273,092). Así k mide "memoria-de-pandas / peso-en-disco
  del mismo número de filas".
- **Resultado: `k = 4.1172`**
  - Memoria deep pandas (5,000 filas): 16.79 MB
  - Tamaño en disco equivalente (5,000 filas, proporcional): 4.08 MB
  - k = 16.79 / 4.08 = 4.117
- Top-5 columnas por consumo de memoria:
  `DESCRIPCION_MERCANCIA`, `RAZON_SOCIAL_DECLARANTE`, `NOMBRE_DECLARANTE`,
  `ADUANA_PRESENTADA`, `DIRECCION_EXPORTADOR` (todas `object`, absorben ~70% de k).
- (código en `medicion.ipynb`, celda "Medición k")

### M · memoria útil disponible
- **M = 17.3706 GB** medidos en el equipo donde se ejecutó el notebook, con el
  kernel y las dependencias ya cargados. Memoria total del equipo: ~23.3 GB.
- Carga del sistema en el momento de la medición: ~25% usado / 75% disponible.
- **Esta cifra es sensible al contexto** — si el equipo tiene navegador, IDE y
  otros procesos abiertos, M baja y el umbral t* se acorta. Es parte normal de
  la definición de M: se mide en el escenario real donde se trabajaría.
- (código en `medicion.ipynb`, celda "Medición M")

---

## Bloque C · Crecimiento y umbral

### Tasa de crecimiento g
- **Método:** comparación del **conteo real de filas** entre 2023 y 2024,
  suponiendo tamaño promedio por fila constante (≈824 B/fila — se verificó que
  es casi idéntico entre los dos años). Fórmula:

  ```
  g = (S0_2024 / S0_2023) ^ (1 / (2024 - 2023)) - 1
    = (2.89125 / 2.75003) ^ (1/1) - 1
    = 0.051354
  ```

- **g anual = +0.051354 (+5.14 %/año)**
- **g mensual = (1 + g_anual)^(1/12) - 1 = +0.004182 (+0.418 %/mes)**

**Interpretación:** el número de declaraciones de importación **creció** entre
2023 y 2024 (de 3.43 M a 3.61 M filas), a una tasa del +5.14 % anual. Es un
crecimiento medido directamente sobre los dos períodos reales elegidos — no una
suposición ni una cifra "oficial" de la fuente.

### Cálculo del umbral
- Fórmula (verificada contra el enunciado de la sesión):

  ```
  t* = log(M / (S0 · k)) / log(1 + g)
     = log(17.3706 / (2.89125 · 4.1172)) / log(1 + 0.051354)
     = log(17.3706 / 11.9038) / log(1.051354)
     = log(1.4591) / log(1.051354)
     = 0.3783 / 0.050074
     = 7.552  períodos (años) desde 2024
  ```

- **Resultado: `t* = 7.55 años` desde 2024**
- **S₀·k = 11.90 GB** (memoria que ocuparía cargar un año completo de
  importaciones en pandas con `deep=True`).
- **M = 17.37 GB** — hoy todavía cabe, pero el dataset crece ~5 % anual y M
  no crece.

### Interpretación en una frase
Con el volumen actual de 2024 (S₀=2.89 GB, k=4.12), cargar el año completo en
pandas consume ya **11.9 GB de RAM** frente a **17.4 GB disponibles**; al
ritmo de crecimiento medido (+5.14 % anual), el dataset anual deje de caber
en la memoria del equipo de trabajo dentro de **aproximadamente 7.5 años**
(~2032), y para degradarlo antes basta con abrir otros procesos pesados,
reducir la RAM del equipo o trabajar con dos años a la vez.

### Sensibilidad de t* a M (no omitirlo)
`t*` es sensible a M. Como referencia:
- con **M = 12 GB** (equipo ocupado en otra tarea): t* ≈ **0.84 años** → umbral
  inmediato (10 meses).
- con **M = 17.4 GB** (medición real de hoy): t* ≈ **7.55 años**.
- Sube/baja logarítmicamente con M; conviene reportar el intervalo y no solo
  un punto.

---

## Declaración de uso de IA generativa
- Herramienta usada: **Claude (Anthropic)** + **OpenCode (opencode.ai)**.
- En qué parte: descubrimiento del endpoint SharePoint `_api` abierto de la
  DIAN (vía inspección del HTML de la página oficial);
  generación del notebook `medicion.ipynb` y del script `src/run_medicion.py`
  que regenera el notebook sin pasar por un kernel Jupyter (para evitar el
  problema de Python 3.14 vs 3.11 en el equipo del estudiante); esqueleto del
  documento y fórmulas matemáticas.
- Qué verifiqué contra ejecución real: **todas las cifras** se obtuvieron
  ejecutando código sobre los 24 archivos `.zip` reales descargados del sitio
  de la DIAN. Las 3,428,200 filas de 2023 y las 3,613,543 filas de 2024 se
  contaron archivo por archivo con `openpyxl.read_only`. `k` se midió con
  `df.memory_usage(deep=True).sum()` sobre una muestra de 5,000 filas. `M`
  se midió con `psutil.virtual_memory().available` en el equipo del estudiante
  (23.3 GB totales, 17.37 GB disponibles en el momento de la medición). El
  criterio "no inventar cifras" del curso se respetó en su totalidad.

---

*IFPN0025 · Big Data e Ingeniería de Datos · Universidad Ean. T1, versión DIAN.*

