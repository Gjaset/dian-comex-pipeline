# T4 · Ejecución del Trabajo MapReduce

Este documento contiene los comandos exactos para ejecutar el trabajo MapReduce diseñado en la tarea T4 y reproducir las cifras de mezcla reportadas en `docs/T4_mezcla.md`.

## Requisitos previos

1. Tener descargados los 24 archivos ZIP de DIAN (importaciones 2023-2024) en `data/raw/`
   - Si no tiene los archivos completos, puede trabajar con una muestra representativa
   - Los scripts funcionan tanto con datos de prueba como con los datos reales

2. Tener disponible el entorno Docker con los servicios de Hadoop y YARN
   - El docker-compose para Hadoop está en `docker-compose.hadoop.yml`
   - Las variables de entorno necesarias están en `hadoop.env`

## Paso a paso para ejecutar el trabajo

### 1. Levantar el clúster Hadoop con YARN

```bash
# Usar el compose específico para Hadoop + YARN
docker compose -f docker-compose.hadoop.yml up -d

# Esperar a que todos los servicios estén listos
# El ResourceManager debería estar disponible en http://localhost:8088
# El HistoryServer en http://localhost:8188

# Verificar状态
docker compose -f docker-compose.hadoop.yml ps
```

### 2. Preparar los datos en HDFS

```bash
# Crear directorio de entrada en HDFS
docker compose -f docker-compose.hadoop.yml exec namenode hdfs dfs -mkdir -p /entrada/t4

# OPCIÓN A: Usar datos de prueba (recomendado para validación inicial)
# Crear directorio para la muestra si no existe
mkdir -p muestra

# Copiar una pequeña muestra para pruebas
# Esto usa los datos que ya preprocesamos en /tmp/test_dian.csv
# En una situación real, el estudiante podría crear su propia muestra
cp /tmp/test_dian.csv muestra/

# Subir la muestra a HDFS
docker compose -f docker-compose.hadoop.yml exec namenode hdfs dfs -put muestra/test_dian.csv /entrada/t4/

# OPCIÓN B: Usar datos reales (para ejecución completa)
# NOTA: Los datos reales (~5.3 GB) no están versionados en el repositorio
# El estudiante debe tenerlos descargados en data/raw/ siguiendo las 
# instrucciones en README.md
#
# Para usar datos reales, se necesitaría:
# 1. Extraer un XLSX de uno de los ZIP
# 2. Convertirlo a CSV (manteniendo solo las columnas necesarias)
# 3. Subirlo a HDFS
#
# Ejemplo conceptual (no ejecutar directamente sin adaptar):
# unzip -p data/raw/01_Importaciones_2023_Enero.zip | \
#   python3 -c "
# import sys, pandas as pd
# df = pd.read_excel(sys.stdin)
# df[['FECHA_PRESENTACION', 'VALOR_FOB_USD', 'COD_ADUANA_PRESENTADA']].to_csv(sys.stdout, index=False)
# " > muestra/datos_reales.csv
#
# docker compose -f docker-compose.hadoop.yml exec namenode hdfs dfs -put muestra/datos_reales.csv /entrada/t4/
```

### 3. Ejecutar el trabajo MapReduce

#### 3.1 Ejecutar SIN combinador (para medir mezcla base)

```bash
docker compose -f docker-compose.hadoop.yml exec namenode bash -c '
echo "=== EJECUTANDO TRABAJO MAPREDUCE SIN COMBINADOR ==="
echo "Limpiando salidas anteriores..."
hdfs dfs -rm -r /salida_t4 2>/dev/null || true

echo "Ejecutando trabajo MapReduce..."
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
  -files /home/jovyan/work/src/mapreduce/mapper.py,/home/jovyan/work/src/mapreduce/reducer.py \
  -mapper mapper.py -reducer reducer.py \
  -input /entrada/t4/test_dian.csv -output /salida_t4

echo "Trabajo completado. Verificando resultado..."
hdfs dfs -test -e /salida_t4/_SUCCESS && echo "✓ Trabajo exitoso" || echo "✗ Trabajo falló"

echo ""
echo "Resultado (presión promedio por sector - primeras 5 líneas):"
hdfs dfs -cat /salida_t4/part-00000 | head
'
```

#### 3.2 Ejecutar CON combinador (para medir reducción de mezcla)

```bash
docker compose -f docker-compose.hadoop.yml exec namenode bash -c '
echo "=== EJECUTANDO TRABAJO MAPREDUCE CON COMBINADOR ==="
echo "Limpiando salidas anteriores..."
hdfs dfs -rm -r /salida_t4_con_combiner 2>/dev/null || true

echo "Ejecutando trabajo MapReduce con combinador..."
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
  -files /home/jovyan/work/src/mapreduce/mapper.py,/home/jovyan/work/src/mapreduce/combiner.py,/home/jovyan/work/src/mapreduce/reducer.py \
  -mapper mapper.py -combiner combiner.py -reducer reducer.py \
  -input /entrada/t4/test_dian.csv -output /salida_t4_con_combiner

echo "Trabajo completado. Verificando resultado..."
hdfs dfs -test -e /salida_t4_con_combiner/_SUCCESS && echo "✓ Trabajo exitoso" || echo "✗ Trabajo falló"

echo ""
echo "Resultado (presión promedio por sector - primeras 5 líneas):"
hdfs dfs -cat /salida_t4_con_combiner/part-00000 | head
'
```

### 4. Obtener los contadores de mezcla

Los valores de "Reduce shuffle bytes" se pueden obtener de dos formas:

#### 4.1 Desde la salida de los comandos Hadoop (recomendado para validación inmediata)

Busque en la salida de los comandos `hadoop jar` líneas como:
```
Shuffle Bytes: 123456
```

#### 4.2 Desde la interfaz web del HistoryServer

1. Abra http://localhost:8188 en su navegador
2. Busque el trabajo MapReduce recientemente completado
3. Haga clic en el trabajo para ver sus detalles
4. Busque en la sección de contadores:
   - `org.apache.hadoop.mapreduce.TaskCounter`
   - `SHUFFLE_BYTES` o `Reduce shuffle bytes`

### 5. Comparar resultados y calcular reducción

Guarde los valores de "Reduce shuffle bytes" de ambas ejecuciones y calcule:

```bash
# Fórmula de reducción porcentual
# reducción% = ((bytes_sin_combinador - bytes_con_combinador) / bytes_sin_combinador) * 100

# Ejemplo con valores hipotéticos:
# bytes_sin_combinador = 154500000  # ~154.5 MB
# bytes_con_combinador = 10350      # ~10.1 KB
# reducción% = ((154500000 - 10350) / 154500000) * 100 = 99.99%
```

### 6. Verificar reproducibilidad

Para asegurar que otro estudiante pueda reproducir exactamente los mismos resultados:

1. Todos los scripts están en `src/mapreduce/`:
   - `mapper.py`
   - `reducer.py` 
   - `combiner.py`

2. La documentación teórica está en `docs/T4_mezcla.md`

3. Este documento (`docs/T4_ejecucion.md`) contiene los comandos exactos

4. El entorno está definido por:
   - `docker-compose.hadoop.yml`
   - `hadoop.env`

### 7. Limpiar recursos

Al finalizar, para liberar recursos:

```bash
docker compose -f docker-compose.hadoop.yml down
```

Esto detendrá y eliminará todos los contenedores de Hadoop, liberando memoria y recursos del sistema.

---

## Notas importantes para el estudiante

1. **Datos de prueba vs datos reales**: 
   - Los scripts funcionan tanto con la muestra pequeña (`test_dian.csv`) como con datos reales
   - Para validar el funcionamiento, comience con la muestra de prueba
   - Para la entrega final, use un conjunto de datos representativo (puede ser un mes completo o más)

2. **Tolerancia a errores**:
   - Los manejan líneas malformadas o con datos faltantes
   - El teste previamente indica que funcionan con el formato real de DIAN

3. **Escalabilidad**:
   - El mismo enfoque funciona con gigabytes de datos
   - El combinador reducirá drásticamente el volumen de mezcla sin importar el tamaño de entrada

4. **Verificación de corrección**:
   - Los resultados numéricos deben ser idénticos entre la ejecución con y sin combinador
   - Solo debería variar el volumen de mezcla (bytes shufflueado)
