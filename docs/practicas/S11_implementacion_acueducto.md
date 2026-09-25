# Práctica S11 — Implementación y medición del acueducto (evidencia de sesión)

> **Aviso de alcance.** Esto es la **práctica S11** (guía `md/practica/BiD_S11_P4_guia_practica_v1.md`), sobre el caso didáctico del **acueducto** en **DuckDB**. La implementación del modelo del **proyecto propio DIAN** sobre Postgres es la tarea **T11** y vive aparte en `src/modelo/t11_modelo_fisico.py` + `docs/T11_modelo_fisico.md`.

**Guion ejecutable:** `scripts/practica_s11/estrella_acueducto.py` (semilla fija 42; DuckDB 1.5.5 embebido).
**Salidas guardadas:** `scripts/practica_s11/resultados_s11.json`. Todas las cifras de este documento salen de esa ejecución real.

Repetir:
```bash
.venv/bin/python scripts/practica_s11/estrella_acueducto.py
```

## Nivel 1 · Modelo creado, cargado, tipo 1 vs tipo 2

Muestra: 200 medidores × 120 días × 24 h = **576.000 hechos** (`hechos_lectura`), más `dim_tiempo` (2.880), `dim_medidor` (200) y `dim_sector` (4).

- **Tipo 1** (`dim_sector`): `UPDATE` que corrige `SEC1` → `S-NORTE-CENTRO`. Verificado en la corrida: tras el UPDATE el valor viejo no existe (`tipo1.sec1_tras_update = "S-NORTE-CENTRO"`).
- **Tipo 2** (`dim_medidor`): `MED0001` cambia a `S-SUR` el 2024-03-01: se cierra la versión vigente (`fecha_fin`, `es_actual=FALSE`) y se abre otra con la clave subrogada nueva `sk_medidor = 201`. Verificado: `MED0001` queda con **2 versiones**, y las lecturas cargadas con `sk_medidor = 1` siguen atribuidas a la versión del norte.

## Nivel 2 · Cinco consultas medidas (mediana de 5 corridas)

| # | Consulta | Mediana |
|---|---|---|
| Q1 | Consumo total por sector | 3,1 ms |
| Q2 | Presión media por hora del día | 3,0 ms |
| Q3 | Consumo total por estrato | 2,7 ms |
| Q4 | Medidor de mayor consumo | 3,4 ms |
| Q5 | **Consumo mensual por sector (línea base)** | **9,0 ms** |

## Tabla agregada, justificada por el número

`agg_consumo_mensual` preagrega Q5. Medición antes/después:

| Consulta mensual por sector | Tiempo |
|---|---|
| Sobre el grano fino (576 mil filas, dos uniones) | 9,0 ms |
| Sobre la tabla agregada | 0,68 ms |
| **Aceleración** | **13,3×** |

La tabla agregada existe **porque el número lo muestra**, no por precaución. Advertencia de sincronización: es dato derivado; si `hechos_lectura` cambia, hay que recalcularla (en la práctica, tras cada ingesta incremental — ver S12).

## Nivel 3 · Desnormalización controlada — medida y rechazada

Candidato: repetir `codigo_sector` dentro de `hechos_lectura` para evitar la unión en consultas como Q1/Q5.

| Variante (consumo por sector) | Tiempo |
|---|---|
| Con unión a `dim_sector` | 2,7 ms |
| Sin unión (atributo ya en hechos) | 8,0 ms |

**Resultado honesto: la desnormalización es 0,34×, es decir, más lenta.** Al ensanchar `hechos_lectura` con un `VARCHAR`, el motor lee más bytes por fila que lo que ahorra en la unión (la dimensión de 4 filas cabe en caché). Además, su costo de consistencia es alto: si un `codigo_sector` cambiara, habría que actualizar las **576.000 filas** de hechos. Se documentó y se **rechaza**: un ejemplo de por qué se mide antes de optimizar. La columna quedó agregada solo en la base en memoria de la corrida; no hay cambio persistente.

## Reto de diseño · Tabla de decisión tipo 1 / tipo 2

| Dimensión | Tipo | Por qué | Costo aceptado |
|---|---|---|---|
| `dim_tiempo` | Ninguno (estable) | El tiempo no cambia: ni corrección ni historia. | — |
| `dim_sector` | **Tipo 1** | Sus cambios son correcciones de nombre/dato; al negocio no le importa el nombre pasado del sector para facturar. | Se renuncia a la historia de nombres. |
| `dim_medidor` | **Tipo 2** | El sector asignado sí cambia de verdad y determina a qué sector se atribuyen las lecturas viejas: la historia importa. | La tabla crece una fila por cada reasignación real. |

Regla aplicada: tipo 2 solo donde la historia importa de verdad; el resto, tipo 1 o nada.

---

*Referencias: Kimball & Ross (2013); Reis & Housley (2022).*
