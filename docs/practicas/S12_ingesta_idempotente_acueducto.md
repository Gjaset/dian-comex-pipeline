# Práctica S12 — Ingesta idempotente del acueducto (evidencia de sesión)

> **Aviso de alcance.** Esto es la **práctica S12** (guía `md/practica/BiD_S12_P4_guia_practica_v1.md`). El **ejemplo guiado del acueducto** corre aquí sobre DuckDB embebido (patrón SQL idéntico a Postgres; guía sec. 1.3). El **"su turno" del proyecto propio DIAN** corre contra el contenedor PostgreSQL real y su evidencia vive en la tarea **T12**: `src/ingesta/ingesta_incremental.py` + `docs/T12_entrega.md` + `docs/T12_bitacora.md`. El memo del reto (cifras propias DIAN) es `docs/T12_memo_reto.md`.

**Guion ejecutable:** `scripts/practica_s12/ingesta_casos.py` (semilla fija 42, 25 medidores, 4 sectores).
**Salidas guardadas:** `scripts/practica_s12/resultados_s12.json`. Todos los conteos de este documento salen de esa ejecución real.

Repetir:
```bash
.venv/bin/python scripts/practica_s12/ingesta_casos.py
```

## Nivel 1 · Acueducto guiado

Tablas creadas con los **nombres exactos obligatorios**: `stg_lecturas` (PK `(meter_id, "timestamp")`) y `estado_ingesta` con **centinela `2000-01-01` nunca NULL** (`GREATEST(NULL, x)` devuelve NULL y rompería el filtro).

Función `ingest_lote`: un lote, **una transacción** (`INSERT … WHERE timestamp > marca_agua ON CONFLICT DO NOTHING` y `UPDATE estado_ingesta … GREATEST(...)` dentro del mismo `engine.begin()`).

Resultados de la corrida real:

| Prueba | Cifra | Estado |
|---|---|---|
| Lote día 1 (25 med. × 24 h) | 600 filas cargadas; total `stg_lecturas` = 600 | OK |
| **Doble ejecución** (misma corrida exacta, mismo lote) | 600 → **600**, 0 filas nuevas | **Superada** |
| Día 2 con reentregas (5 %) y tardíos (2 %): lote de 642 filas | 600 genuinamente nuevas; total 1.200 = esperado | Sin duplicar |

**Su turno (proyecto propio DIAN):** mismo patrón contra Postgres real — doble ejecución del lote 2023-01: 273.092 → **273.092** (+0); con el lote de febrero: 539.168; marca de agua `2000-01-01` → `2023-02-28`. Evidencia completa en `docs/T12_bitacora.md`.

## Nivel 2 · Reproceso de ventana (acueducto)

Función `reprocesar_ventana`, distinta de la ingesta normal: ignora **a propósito** el filtro de marca de agua (documentado en el docstring) y confía solo en `ON CONFLICT`. Corrida real sobre el día 1 con la marca ya avanzada al día 2:

| Momento | Conteo `stg_lecturas` | Marca de agua |
|---|---|---|
| Antes del reproceso | 1.200 | 2024-06-02 23:00 |
| Después del reproceso del día 1 | **1.200** (+0) | 2024-06-02 23:00 (no retrocedió) |

Su equivalente del proyecto propio (`--reprocesar` sobre enero-2023 con la marca en febrero): 539.168 → **539.168**, bitácora T12.

## Nivel 3 · Clave de deduplicación sin marca temporal confiable

Fuente `generar_fuente_legacy` (solo fecha, 33 filas: 30 legítimas + 1 reentrega exacta + 2 lecturas legítimas trampa de `LEG900` el 2024-06-03 con contenido idéntico). Corrida real:

| Estrategia | 33 filas → | Qué pasó con el caso trampa |
|---|---|---|
| Clave natural `(meter_id, fecha)` | 30 | Colapsa las dos lecturas legítimas de `LEG900` |
| Huella de fila (MD5 del contenido) | 31 | Colapsa igual |

**Decisión y su límite, por escrito:** con las columnas disponibles **ninguna clave calculable distingue** las dos lecturas legítimas (ambas estrategias las colapsan por igual: son bit a bit idénticas). Si hubiera que elegir, la clave natural es preferible por simple y auditable, pero la decisión defendible es la otra: documentar el riesgo residual y **pedir a la fuente un campo adicional** (consecutivo de radicado o identificador de captura), no forzar una clave que no existe. En el proyecto propio DIAN el caso es distinto — sí hay marca temporal y clave natural compuesta con unicidad verificada en muestra (T1); su análisis está en `docs/T12_bitacora.md` § Decisión de clave.

## Reto de diseño · Memo de reanudación

El memo con cifras propias del proyecto (7,04 M filas acumuladas, Δn ≈ 273 mil/lote, costo evitado de recargar el histórico completo) es **`docs/T12_memo_reto.md`**, versionado, tal como pide la rúbrica de ambas S12 y T12. Estrategia de reanudación: la marca de agua de `estado_ingesta` dice desde dónde retomar y `ON CONFLICT` garantiza que un reintento parcial no duplique — demostrado arriba con la doble ejecución.

---

*Referencias: Densmore (2021); Kleppmann (2017); Reis & Housley (2022).*
