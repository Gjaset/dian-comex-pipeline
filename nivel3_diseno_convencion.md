# Diseño de la Convención de Rutas del Lago de Datos
## Nivel 3 · Autónomo · Sesión 5

### 1. Convención de Rutas Completa del Lago

Tras analizar las fuentes de datos disponibles y los requisitos de consulta, propongo la siguiente convención de rutas para cada capa del lago:

#### Capa Cruda (cruda)
```
<fuente>/anio=YYYY/mes=MM/dia=DD/<hora=HH>/<nombre_archivo>.<extension>
```
Ejemplo: `secoop_ii/anio=2026/mes=03/dia=15/hora=14/contratos_20260315_1400.csv`

#### Capa Refinada (refinada)
```
<dominio>/<subdominio>/anio=YYYY/mes=MM/dia=DD/<nombre_archivo>.<extension>
```
Ejemplo: `contratos/proveedores/anio=2026/mes=03/dia=15/contratos_limpios_20260315.parquet`

#### Capa Consolidada (consolidada)
```
<area_negocio>/<metricas_o_dimensiones>/anio=YYYY/mes=MM/<nombre_archivo>.<extension>
```
Ejemplo: `finanzas/gasto_mensual/anio=2026/mes=03/resumen_gastos_202603.parquet`

### 2. Justificación de la Partición

He elegido particionar por fecha (año, mes, día) y, en la capa cruda, también por hora porque:

1. **Patrones de consulta predominantes**: La mayoría de las analíticas en este dominio involucran filtros temporales (¿cuánto se gastó en marzo? ¿cómo evolucionó el número de contratos semanalmente?).

2. **Velocidad de llegada de los datos**: Los datos se ingresan de forma casi continua durante el día, por lo que particionar por hora en la capa cruda permite una ingestión más eficiente y evita conflictos de escritura.

3. **Granularidad adecuada**: 
   - En cruda: Hora permite particiones pequeñas y manejables para datos transaccionales
   - En refinada: Día es suficiente después de los procesos de limpieza y deduplicación
   - En consolidada: Mes es apropiado para reportes agregados y métricas tendenciales

4. **Escalabilidad**: Esta partición distribuye uniformemente los datos y evita "hot spots" en el almacenamiento.

### 3. Documentación de las Capas

#### Capa CRUDA
- **Qué contiene**: Datos tal como provienen de las fuentes externas, sin transformación alguna.
- **Características**:
  - Inmutable: Una vez escritos, los objetos nunca se modifican
  - Versionado activado: Cada sobrescritura genera una nueva versión recuperable
  - Formato original: Preserva el formato exacto de ingreso (CSV, JSON, XML, etc.)
  - Metadatos mínimos: Solo los imposibles de derivar (timestamp de ingestion)
- **Propósito**: Servir como fuente de verdad y permitir reprocesamiento completo si es necesario.

#### Capa REFINADA
- **Qué contiene**: Datos limpios, estructurados y listo para análisis, pero aún a nivel transaccional.
- **Características**:
  - Esquema definido y consistente
  - Limpieza aplicada: valores nulos manejados, tipos de datos correctos, duplicados eliminados
  - Enriquecimiento básico: posible unión con tablas de referencia estáticas
  - Formato columnar recomendado (Parquet) para eficiencia de consulta
  - Particionado optimizado para los patrones de consulta comunes
- **Propósito**: Capa de trabajo para data scientists y analistas que necesitan datos confiables pero aún detallados.

#### Capa CONSOLIDADA
- **Qué contiene**: Datos agregados, resumidos y listo para consumo directo en reportes y dashboards.
- **Características**:
  - Nivel de agregación adecuado para métricas de negocio
  - Pre-cálculo de métricas complejas que son costosas de calcular en tiempo real
  - Diseñado para consultas de BI y reporting
  - Puede incluir datos de múltiples fuentes ya integrados
  - Formato optimizado para lectura (Parquet con compresión adecuada)
- **Propósito**: Entregar datos "listos para usar" a usuarios de negocio y aplicaciones de reporting.

### 4. Declaración de Inmutabilidad

**Por qué la cruda no se toca:**
La capa cruda representa el acto de fe en el proceso de ingesta: confiamos en que lo que recibimos de la fuente es correcto en ese momento. Modificarla rompería la cadena de custodia de los datos y haría imposible verificar si las transformaciones posteriores fueron aplicadas correctamente.

**Dónde se corrigen los errores:**
Los errores se corrigen en las capas superiores:
- Errores de formato o corruptibilidad: Se manejan durante la ingesta a refinada (los registros problemáticos se isolan en un "dead letter queue")
- Errores de contenido (valores incorrectos): Se corrigen en la capa refinada mediante reglas de limpieza y validación
- Errores de lógica de negocio: Se abordan en las transformaciones que producen la capa consolidada
- En todos los casos, la versión original en cruda permanece intacta para auditoría y reprocesamiento

### 5. Beneficios de esta Convención

1. **Predecibilidad**: Un nuevo analista puede adivinar dónde está un dato sin preguntar
2. **Automatización sencilla**: Los pipelines pueden construir rutas dinámicamente basadas en fechas
3. **Eficiencia de consulta**: El particionamiento permite que los motores de consulta lean solo lo necesario
4. **Gestión del ciclo de vida**: Políticas de retención pueden aplicarse fácilmente por capa y periodo
5. **Linaje claro**: Es fácil rastrear desde un reporte consolidado hasta los datos crudos originales

### 6. Ejemplo Completo de Trazabilidad

Supongamos que necesitamos analizar el gasto en contrataciones públicas del 15 de marzo de 2026:

1. **Consulta en consolidada**: 
   ```
   s3://consolidada/finanzas/gasto_mensual/anio=2026/mes=03/resumen_gastos_202603.parquet
   ```
   Muestra un total de $1,250,000 para marzo.

2. **Investigación en refinada** (vemos que parece alto para una quincena):
   ```
   s3://refinada/contratos/proveedores/anio=2026/mes=03/dia=15/contratos_limpios_20260315.parquet
   ```
   Encontramos 127 contratos con un promedio de $9,800 cada uno.

3. **Verificación en cruda** (para asegurar que no hubo pérdida en el procesamiento):
   ```
   s3://cruda/secoop_ii/anio=2026/mes=03/dia=15/hora=14/contratos_20260315_1400.csv
   s3://cruda/secoop_ii/anio=2026/mes=03/dia=15/hora=15/contratos_20260315_1500.csv
   ... (todas las horas del día)
   ```
   Confirmamos que hay exactamente 127 registros en cruda, validando que el proceso de refinada no perdió datos.

Esta trazabilidad completa es posible precisamente porque mantenemos la inmutabilidad de la capa cruda y documentamos claramente la transformación en cada paso.