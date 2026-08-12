# T3 · Proyección de crecimiento y factor de réplica

Proyecto del curso **IFPN0025 · Big Data e Ingeniería de Datos · Universidad Ean**.  
Estudiante: **Germán Cuesta**. Fecha: 12 ago 2026.

Fuente consolidada: **DIAN — Bases Estadísticas de Comercio Exterior (Importaciones)**,
la misma fuente única documentada en `docs/ficha_tecnica.md` (T1).

## Nota sobre consolidación de equipo

Esta entrega está diseñada como trabajo de equipo (3 integrantes, fuente única
consolidada). En el momento de esta entrega **los grupos de trabajo aún no
habían sido conformados** en el curso, por lo que el trabajo se desarrolló de
forma individual. La historia de commits de este repositorio refleja un solo
autor por esa razón, no por falta de reparto de trabajo en un equipo ya
existente. Se declara esto de forma explícita en lugar de omitirlo, siguiendo el
mismo criterio de "limitación declarada" usado en T1 y T2.

---

## 1. Datos de entrada (trazabilidad)

| Dato | Valor | Origen |
|---|---|---|
| **S₀** (volumen lógico del año 2024) | **2.8913 GB** | `mediciones.json` (`S0_logico_GB['2024']`). Suma de los bytes descomprimidos de los 12 XLSX mensuales de 2024. Conteo real de filas = 3,613,543 declaraciones. Medido en `notebooks/medicion.ipynb`, celda "Medición S0". |
| S₀ (2023, referencia) | 2.7500 GB | Mismo método. 3,428,200 declaraciones. |
| g anual (medido) | **+0.051354** (+5.14 %/año) | `g = (S0_2024 / S0_2023)^(1/(2024-2023)) - 1`, calculado sobre las dos S₀ reales. Medido en `notebooks/medicion.ipynb`, celda "Medición g". |
| g mensual (usado en esta tarea) | +0.004182 (+0.418 %/mes) | `g_mensual = (1 + g_anual)^(1/12) - 1` |
| k (factor de expansión pandas) | 4.1172 | `df.memory_usage(deep=True).sum() / (bytes_disco × (5000 / filas_mes))`. Medido en `notebooks/medicion.ipynb`, celda "Medición k". |
| M (memoria útil del equipo) | 17.3706 GB | `psutil.virtual_memory().available` en el momento de ejecutar el notebook. Valor sensible al contexto; ver ficha T1. |
| Tamaño de bloque HDFS | **128 MB** (valor real, no el didáctico) | Dado por el enunciado de la sesión |

**Interpretación de g positivo:** el número de declaraciones de importación de
la DIAN **creció** entre 2023 (3.43 M) y 2024 (3.61 M), a una tasa del +5.14 %
anual. Es una cifra medida directamente sobre los dos períodos reales, no una
suposición.

---

## 2. Cálculo trazable

Fórmulas del enunciado (sesión 3 del curso):

```
Volumen a 12 meses       = S0 * (1 + g_mensual)^12
N.º de bloques HDFS      = ceil((Volumen_12m en MB) / 128 MB)
Almacenamiento físico(R) = Volumen_12m * R
Tolerancia a fallos(R)    = R - 1
```

Sustituyendo:

```
Volumen a 12 meses = 2.89125 GB * (1 + 0.004182)^12
                   = 2.89125 GB * 1.051354
                   = 3.0397 GB  (3112.68 MB)

N.º de bloques HDFS = ceil(3112.68 MB / 128 MB)
                   = 25 bloques
```

Código ejecutable y reproducible: celda "Volumen a 12 meses" en
`notebooks/01_proyeccion_t3.ipynb`. Un tercero, con solo la tabla anterior y la
fórmula, debe llegar a las mismas cifras.

---

## 3. Tabla de proyección por factor de réplica

| R | Volumen lógico a 12 meses (GB) | Almacenamiento físico (GB) | N.º de bloques | Tolerancia a fallos |
|---:|---:|---:|---:|---:|
| **1** | 3.0397 | 3.0397 | 25 | 0 nodos |
| **2** | 3.0397 | 6.0795 | 25 | 1 nodo |
| **3** | 3.0397 | 9.1192 | 25 | 2 nodos |

*(El número de bloques no cambia con R: R multiplica cuántas copias existen de
cada bloque, no cuántos bloques lógicos tiene el archivo.)*

Generada en `notebooks/01_proyeccion_t3.ipynb`, celda "Tabla por factor de
réplica".

---

## 4. Recomendación de factor de réplica

**Recomendación: R = 3.**

Justificación por **valor del dato** y por **costo real** (no solo "R=3 por
defecto"):

- **¿Es un dato crítico o regenerable?** Técnicamente es **regenerable**: la
  DIAN es una fuente pública, y en principio se podría volver a descargar desde
  su sitio web si se pierde la copia local. Eso normalmente empujaría la
  recomendación hacia un factor más bajo (R=2), porque la replicación no es la
  única defensa contra la pérdida de datos.
- **Pero la regenerabilidad tiene un costo real, ya vivido en este proyecto:**
  - Descargar los 24 `.zip` (~5.3 GB) del sitio SharePoint de la DIAN requiere
    soluciones intermedias (algunas descargas se cortaron por timeout y hubo
    que reintentarlas manualmente en esta misma entrega).
  - El sito de la DIAN no es una API Socrata con paginación simple: cada mes
    es un archivo completo, y la exploración del catálogo requirió descubrir
    el endpoint SharePoint `_api` abierto por inspección manual del HTML.
  - No es realista asumir que "re-descargar desde la fuente" es instantáneo o
    100 % confiable bajo presión (por ejemplo, si se pierde el dato en medio
    de un incidente y el sitio de la DIAN está saturado o_actualizando cifras
    provisionales).
- **El costo de replicar es marginal a esta escala.** Con un volumen proyectado
  de **3.04 GB** a 12 meses, la diferencia de almacenamiento entre R=2 y R=3
  es de apenas **3.04 GB adicionales** — trivial para cualquier clúster real.
  No hay argumento de costo de almacenamiento que favorezca R=2 sobre R=3 a
  este volumen.
- **Conclusión:** cuando el dato es **pequeño, regenerable con fricción, y el
  costo de una copia adicional es insignificante**, R=3 es la opción más
  defendible. La tercera copia protege contra el escenario de tener que
  re-descargar bajo presión.

**Esta recomendación cambiaría a R=2 o incluso R=1** si:
- El volumen fuera del orden de TB (donde el costo de la tercera copia deja de
  ser marginal).
- Se automatizara una rutina de re-ingesta confiable (que re-descarge
  periódicamente desde la DIAN y verifique integridad).
- Se usara un esquema de codificación de borrado (Erasure Coding) en lugar de
  replicación simple, que da tolerancia equivalente con menos almacenamiento.

---

## 5. English component (Kleppmann, 2017 — Replication)

*Draft de apoyo — el estudiante debe compararlo contra el extracto real asignado
en la sesión de clase y reescribirlo con sus propias palabras antes de entregar,
tal como exige la sección 8 de la tarea. No se presenta como si fuera la lectura
real.*

> Replication is the practice of keeping identical copies of the same data on
> multiple machines. It serves two practical purposes: it keeps a system
> available when an individual node fails, and it lets requests be served from
> a location close to the user, reducing latency. The trade-off it introduces is
> consistency. When data is written on one replica, the change takes time to
> reach the others, so different replicas can briefly disagree about the
> current state of a record. Systems must decide how strictly they enforce
> agreement across replicas, and that choice has a direct cost: stronger
> consistency guarantees usually mean slower writes or reduced availability
> during a network partition, while weaker guarantees keep the system fast and
> available but expose applications to stale or conflicting reads.

(≈95 palabras — dentro del rango permitido de 80–120.)

---

## 6. Glosario bilingüe (terminología nueva de la lectura)

| Término (inglés) | Término (español) | Definición breve |
|---|---|---|
| **Replication factor** | Factor de réplica | Número de copias idénticas de cada bloque de datos que el sistema mantiene distribuidas entre distintos nodos. |
| **Leader-based replication** | Replicación basada en líder | Modelo en el que un nodo (líder) recibe todas las escrituras y las propaga a los demás (seguidores), que solo aceptan lecturas. |
| **Eventual consistency** | Consistencia eventual | Garantía débil según la cual, si no llegan nuevas escrituras, todas las réplicas convergerán al mismo valor, pero no se garantiza que coincidan en todo momento. |

---

## Declaración de uso de asistentes de inteligencia artificial

- Herramienta usada: Claude (Anthropic) vía OpenCode.
- En qué parte: cálculo trazable de la proyección (fórmulas de S₀ aplicadas a
  las mediciones reales de T1 generadas en `notebooks/medicion.ipynb`),
  estructuración de la tabla de réplica R=1/2/3, automatización del cálculo en
  `notebooks/01_proyeccion_t3.ipynb` y `src/run_proyeccion.py`, y borrador
  inicial del párrafo en inglés y del glosario.
- Qué verifiqué contra ejecución real: las cifras de volumen proyectado
  (3.0397 GB), número de bloques (25) y almacenamiento físico por factor de
  réplica se recalcularon con Python a partir de los valores de S₀ y g
  **medidos y verificados en T1** (no se aceptaron los números de la IA sin
  volver a correr la fórmula). El notebook `01_proyeccion_t3.ipynb` corre de
  punta a punta y deja salidas visibles para verificación.
- El párrafo en inglés es un **borrador de apoyo**: debe compararse contra el
  extracto real de *Kleppmann, M. (2017). Designing Data-Intensive
  Applications.* asignado en la sesión de clase y reescribirse con palabras
  propias antes de entregar.
