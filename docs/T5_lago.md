# T5 · El lago del proyecto

**IFPN0025 · Big Data e Ingeniería de Datos · Universidad Ean**
Fuente del proyecto: `DIAN Importaciones 2023-2024`

---

## 1. El mapa del lago

| Cubo | Qué contiene | Estado en el proyecto hoy |
|---|---|---|
| `cruda` | `el dato tal como llegó de la fuente, sin transformar` | `poblado con T5` |
| `refinada` | `el dato limpio, tipado y validado` | `vacío por ahora; se poblará más adelante` |
| `consolidada` | `el dato modelado y agregado, listo para consumir` | `vacío por ahora` |

---

## 2. La convención de rutas

**Plantilla de la ruta en la capa cruda**
```
cruda/«fuente»/anio=YYYY/mes=MM/dia=DD/«archivo».«ext»
```

**Un ejemplo real de su dato**
```
cruda/importaciones_dian/anio=2023/mes=01/dia=01/importaciones_sample.csv
```

**La convención de las otras dos capas · nivel Frontera, opcional**
```
refinada/importaciones_dian/anio=YYYY/mes=MM/dia=DD/importaciones_clean.parquet
consolidada/importaciones_dian/anio=YYYY/mes=MM/dia=DD/importaciones_agg.parquet
```

---

## 3. La partición

**Por qué particionamos así**
`Particionamos por año/mes/día porque las consultas típicas de análisis de importaciones se filtran por periodos específicos (ej: mensual o anual). Esta partición permite eliminando datos no relevantes mediante predicas de partición en motores como Spark o Presto, mejorando el rendimiento y reduciendo costos.`

---

## 4. La regla de la capa cruda

**Declaración de inmutabilidad**
`La capa cruda es inmutable: guarda el dato tal como llegó y no se edita.`

**Dónde se corrigen los errores**
`Los errores y las limpiezas se hacen en la capa refinada, nunca en la cruda.`

---

## 5. Evidencia del versionado · nivel Extensión

**Versionado activo en la capa cruda**
`Sí. Configurado con put_bucket_versioning, Status Enabled.`

**Prueba de que una versión anterior sigue recuperable**
```
VersionId: 1640995384363584 | Ultima: False
VersionId: 1640995384363585 | Ultima: True
```
*(Tras sobrescribir el mismo objeto, aparecen dos VersionId, siendo la última marcada como True y la anterior como False)*

**Por qué el versionado protege la inmutabilidad**
`Una versión anterior sigue recuperable, por lo que un error de carga no destruye el dato original; siempre se puede volver a la versión previa sin pérdida de información.`

---

## 6. Cómo encontrar un dato · la prueba del analista

**Pregunta de ejemplo**
`Un analista necesita el dato de la fuente importaciones_dian del día 2023-01-15. ¿Cuál es la ruta?`

**Respuesta, derivada solo de la convención**
```
cruda/importaciones_dian/anio=2023/mes=01/dia=15/importaciones_sample.csv
```

Si pudieron escribir esta ruta usando solo la convención de la sección 2, el lago es navegable. Esa es la evidencia del reto Power Humanise.

---

## 7. Reproducibilidad

**Comandos exactos para reconstruir el lago**
```
docker compose -f docker-compose.minio.yml up -d
python3 src/ingesta/cargar_cruda.py
```

**Declaración**
`Confirmamos que otra persona, con un clon limpio del repositorio y estos comandos, obtiene el mismo lago: los mismos cubos, las mismas rutas y el versionado activo.`

---

