# Guía del Lago de Datos para Nuevos Analistas
## Reto de Negocio · Sesión 5

### 🗺️ El mapa del lago

Nuestro lago de datos tiene tres capas claramente diferenciadas:

- **Capa cruda (cruda)**: Los datos tal como llegaron de las fuentes, sin tocar. Aquí guardamos lo original para poder reprocesar si es necesario.
- **Capa refinada (refinada)**: Datos limpios y estructurados, listos para análisis. Aquí eliminamos duplicados, corregimos formatos y aplicamos reglas de calidad.
- **Capa consolidada (consolidada)**: Métricas y reportes pre-calculados. Lo que usan los dashboards y los reportes ejecutivos.

### 🛣️ La convención de rutas

Todos los archivos siguen este patrón predecible:

```
<capa>/<dominio>/[particiones]/<nombre_descriptivo>.<formato>
```

**Ejemplos reales:**

- *Cruda*: `cruda/secoop_ii/anio=2026/mes=03/dia=15/hora=09/contratos_raw.csv`
- *Refinada*: `refinada/contratos/proveedores/anio=2026/mes=03/dia=15/contratos_limpios.parquet`
- *Consolidada*: `consolidada/finanzas/gasto_mensual/anio=2026/mes=03/resumen.gasto.parquet`

**Particiones que verás:**
- `anio=YYYY` (por ejemplo: anio=2026)
- `mes=MM` (por ejemplo: mes=03)
- `dia=DD` (por ejemplo: dia=15)
- En cruda también: `hora=HH` (por ejemplo: hora=14)

### 🔒 La regla de la cruda

**Nunca toques nada en la capa cruda.**
Esta capa es sagrada e inmutable: lo que se escribe ahí permanece para siempre tal como vino de la fuente. Si encuentras un error:
1. No intentes corregir el archivo en cruda
2. Documenta el problema
3. La corrección se aplica en la capa refinada mediante reglas de limpieza
4. Si es necesario reprocesar todo, usamos exactamente lo que está en cruda

### 🔍 Cómo encontrar un dato

**Sigamos un ejemplo práctico:**

*Necesitas los datos de contrataciones del SECOP II del 15 de marzo de 2026.*

1. **Piensa en la capa**: Si quieres los datos originales para hacer tu propio procesamiento → capa cruda
2. **Aplica la convención**: 
   - Fuente: secoop_ii
   - Fecha: 15/03/2026 → anio=2026/mes=03/dia=15
   - En cruda también necesitas la hora (elige cualquiera o procesa todas)
3. **Construye la ruta**: 
   `cruda/secoop_ii/anio=2026/mes=03/dia=15/hora=*/contratos_*.csv`
4. **Verifica en la consola**: Ve a http://localhost:9001, navega al bucket cruda y busca coincidencias

**Para datos ya listos para analizar** (limpios y estructurados):
`refinada/contratos/proveedores/anio=2026/mes=03/dia=15/*.parquet`

**Para métricas ya calculadas** (listos para reportes):
`consolidada/finanzas/*/anio=2026/mes=03/*.parquet`

### ✅ Tips de navegación

- Siempre empieza desde la capa correcta según lo que necesitas (original → cruda, listo para analizar → refinada, listo para reportar → consolidada)
- Las particiones son tus filtros: si quieres marzo de 2026, busca `mes=03/anio=2026`
- En consola web de MinIO (puerto 9001), puedes usar la barra de búsqueda filtrando por prefijo
- Si no encuentras algo, verifica que escribiste la partición exactamente: `mes=03` no es lo mismo que `mes=3`

**Recuerda**: Si puedes predecir la ruta sin preguntar, la convención funciona. Esta guía está diseñada para que, en tu primer día, puedas encontrar lo que necesitas sin interrumpir a nadie.