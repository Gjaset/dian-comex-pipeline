# T10 · Modelo lógico dimensional del proyecto

**Equipo:** DIAN Importaciones
**Integrantes:** Germán Cuesta, Jose Alejandro Hernandez, Juan Camilo Pardo
**Proyecto:** Bases Estadísticas de Comercio Exterior — Importaciones DIAN 2023–2024
**Fecha:** 2026-09-21

---

## 1. El grano

> Una frase, sin la conjunción "y". Qué representa exactamente una fila de la tabla de hechos.

**Grano:** una fila es una declaración de importación DIAN.

*(El identificador físico de ese grano ya fue verificado en T1 por prueba de unicidad: la clave compuesta `CODIGO_SUCURSAL + CODIGO_CAJERO + CONSECUTIVO_CAJERO + NIT_IMPORTADOR` no repite en la muestra medida. Todo lo demás en este documento existe o no existe según ese grano.)*

---

## 2. La tabla de hechos

> Las medidas que existen a ese grano y las claves foráneas a las dimensiones.

| `hechos_declaracion` | Tipo | Descripción |
|---|---|---|
| sk_tiempo | Clave foránea | Enlaza con `dim_tiempo` (día de `FECHA_PRESENTACION`) |
| sk_aduana | Clave foránea | Enlaza con `dim_aduana` (aduana donde se presentó) |
| sk_pais | Clave foránea | Enlaza con `dim_pais` (país de origen de la mercancía) |
| sk_importador | Clave foránea | Enlaza con `dim_importador` (empresa importadora, persona jurídica) |
| sk_subpartida | Clave foránea | Enlaza con `dim_subpartida` (posición arancelaria) |
| valor_fob_usd | Medida | Valor en aduana del país exportador, USD (columna `VALOR_FOB_USD`) |
| valor_fletes_usd | Medida | Fletes internacionales, USD (`VALOR_FLETES_USD`) |
| valor_seguros_usd | Medida | Seguros internacionales, USD (`VALOR_SEGUROS_USD`) |
| valor_aduana_usd | Medida | Base gravable CIF, USD (`VALOR_ADUANA_USD`) |
| peso_neto_kg | Medida | Peso neto de la mercancía, kg (`PESO_NETO`) |
| peso_bruto_kg | Medida | Peso bruto de la mercancía, kg (`PESO_BRUTO`) |
| cantidad | Medida | Cantidad en la unidad comercial declarada (`CANTIDAD`) |

**Verificación de cada medida contra el grano.** Las siete se registran sobre la declaración individual: cada fila XLSX de la DIAN trae su propio FOB, flete, seguro, CIF y pesos. Ninguna es un promedio ni un total mensual (eso no existiría al grano de una declaración; viviría en una tabla agregada aparte como `agg_mes_aduana` de T11).

---

## 3. Las dimensiones

> Conformadas, planas en estrella. Cada una con su clave subrogada. Todas aplican a toda fila de hechos: toda declaración tiene fecha, aduana, país de origen, importador y subpartida obligatorias en el formulario DIAN.

### `dim_tiempo`
- **Clave subrogada:** `sk_tiempo`
- **Clave de origen conservada como atributo:** `fecha` (de `FECHA_PRESENTACION`)
- **Atributos:** `anio`, `mes`, `dia`, `nombre_mes`, `trimestre`, `anio_mes` (para el patrón de consulta mensual del proyecto)

### `dim_aduana`
- **Clave subrogada:** `sk_aduana`
- **Clave de origen conservada como atributo:** `cod_aduana` (`COD_ADUANA_PRESENTADA`)
- **Atributos:** `nombre_aduana` (`ADUANA_PRESENTADA`), circunscripción

### `dim_pais`
- **Clave subrogada:** `sk_pais`
- **Clave de origen conservada como atributo:** `cod_pais` (`CODIGO_PAIS_ORIGEN`, ALADI en 2023-2024)
- **Atributos:** `nombre_pais` (`PAIS_ORIGEN`)

### `dim_importador`
- **Clave subrogada:** `sk_importador`
- **Clave de origen conservada como atributo:** `nit` (`NIT_IMPORTADOR`)
- **Atributos:** `razon_social` (`NOMBRE_IMPORTADOR`, solo personas jurídicas — ver nota PII de la ficha T1), `ciudad` (`CIUDAD_PAIS_IMPORTADOR`), `cod_departamento` (`CODIGO_DEPTO_IMPORTADOR`)

### `dim_subpartida`
- **Clave subrogada:** `sk_subpartida`
- **Clave de origen conservada como atributo:** `cod_subpartida` (`SUBPARTIDA_ARANCELARIA`)
- **Atributos:** `capitulo_arancelario` (primeros 2 dígitos), `partida` (primeros 4 dígitos)

---

## 4. El diagrama del esquema estrella

![Esquema estrella DIAN importaciones](estrella.png)

Archivo editable en el repositorio: `docs/estrella.drawio` (formato drawio; el PNG se regenera con `docs/render_estrella.py`).

---

## 5. Nivel Frontera, si lo abordaron

**Dimensión candidata a copo de nieve:** `dim_pais`, normalizándola contra el catálogo geográfico (`dim_pais` → `dim_region` → `dim_bloque_comercial`).

**Análisis:** convendría si el catálogo geográfico tuviera jerarquía mantenida por un tercero y se reutilizara en varios procesos con actualización frecuente. En este proyecto no es así: `dim_pais` tiene unas 200 filas, los nombres de país cambian casi nunca, y el cambio ALADI→M49 (enero 2025) se absorbe mejor con dimensión plana más atributo de catálogo vigente que con un copo de nieve que habría que rehacer completo al cambiar de estándar. **Decisión: mantener estrella plana.** La justificación del caso general queda: solo se normaliza una dimensión cuando su jerarquía crece de volumen o de mantenimiento independiente; aquí no cumple ninguna de las dos condiciones.

---

## Autoverificación antes de entregar

- [x] El grano se dice en una frase, sin la conjunción "y".
- [x] Toda medida de la tabla de hechos existe al grano declarado.
- [x] Toda dimensión aplica a cada fila de hechos.
- [x] Hay al menos tres dimensiones conformadas en esquema estrella (hay cinco).
- [x] Cada dimensión tiene su clave subrogada, distinta de la clave de origen.
- [x] Ninguna medida quedó en una dimensión, ni ningún atributo descriptivo en los hechos.
- [x] El diagrama editable está en el repositorio, no solo como imagen.

---

## Referencias

Kimball, R., y Ross, M. (2013). *The data warehouse toolkit: The definitive guide to dimensional modeling* (3.ª ed.). John Wiley & Sons.

Reis, J., y Housley, M. (2022). *Fundamentals of data engineering*. O'Reilly Media.
