# Práctica S10 — Modelo dimensional del acueducto (evidencia de sesión)

> **Aviso de alcance.** Esto es la **práctica S10** (guía `md/practica/BiD_S10_P4_guia_practica_v1.md`), sobre el caso didáctico del **acueducto**. El modelo dimensional del **proyecto propio DIAN** es la tarea **T10** y vive aparte en `docs/T10_modelo_dimensional.md` + `docs/estrella.drawio`. No se mezclan.
>
> **Herramienta:** draw.io (editable en `docs/practicas/s10_estrella_acueducto.drawio`; imagen `s10_estrella_acueducto.png`, regenerable con `python3 scripts/practica_s10/render_s10.py`).

---

## Nivel 1 · El grano y la tabla de hechos

**Grano (una frase, sin "y"):**

> **Una fila es la lectura de un medidor en una hora.**

Validación con las tres pruebas de la guía:

| Prueba | Resultado |
|---|---|
| Se dice en una frase sin "y" | Cumple: una lectura, de un medidor, en una hora. |
| Toda medida existe a ese nivel | `consumo_m3` y `presion_bar` se registran por lectura horaria. Un promedio mensual **no** cabría aquí: iría en otra tabla de hechos agregada (ver S11). |
| Toda dimensión aplica a cada fila | Toda lectura tiene tiempo, medidor y sector; ninguna dim queda sin valor. |

Tabla de hechos:

| `hechos_lectura` | Tipo | Papel |
|---|---|---|
| sk_tiempo | Clave foránea | Enlaza con `dim_tiempo` |
| sk_medidor | Clave foránea | Enlaza con `dim_medidor` |
| sk_sector | Clave foránea | Enlaza con `dim_sector` |
| consumo_m3 | Medida | m³ consumidos en la hora (sumable) |
| presion_bar | Medida | Presión media de la hora (promediable) |

## Nivel 2 · Estrella con tres dimensiones conformadas

| Dimensión | Clave subrogada | Atributos | Clave de origen (conservada como atributo) |
|---|---|---|---|
| `dim_tiempo` | sk_tiempo | fecha, hora, dia_semana, mes, anio | — (el tiempo no tiene clave de negocio) |
| `dim_medidor` | sk_medidor | codigo_medidor, tipo, fecha_instalacion | `codigo_medidor` (MED0001, …) |
| `dim_sector` | sk_sector | nombre_sector, zona, estrato | `codigo_sector` (SEC1, …) |

Criterio de correctitud verificado: las tres dimensiones conectan **directo** a `hechos_lectura`, sin subtablas intermedias; ninguna medida quedó en una dimensión ni ningún atributo descriptivo en los hechos; las claves que enlazan son las subrogadas, no las de origen. Diagrama: `s10_estrella_acueducto.{drawio,png}`.

## Nivel 3 · Copo de nieve: análisis honesto

Candidato: `dim_sector` tiene una jerarquía clara (sector → zona → ciudad). Normalizarla daría `dim_sector(sk_sector, codigo, nombre, estrato, sk_zona)` + `dim_zona(sk_zona, nombre, sk_ciudad)` + `dim_ciudad(...)`.

**Conclusión: no se justifica en este proyecto.** `dim_sector` tiene 4 filas (y en el proyecto del curso, del orden de decenas): la repetición de `zona`/`ciudad` pesa bytes, y cada consulta pagaría dos uniones más por nada. La jerarquía tampoco se comparte con otros modelos. Se deja el estrella plano; el copo de nieve se adoptaría solo si la dimensión creciera a miles de filas con jerarquía estable y compartida.

## Reto de diseño (media página)

**Pregunta de gerencia:** consumo mensual por sector, para facturación. ¿El grano por hora la responde?

Sí. El grano horario es más fino que lo pedido, y desde un grano fino siempre se agrega hacia arriba:

```sql
SELECT t.anio, t.mes, s.codigo_sector, sum(h.consumo_m3)
FROM hechos_lectura h
JOIN dim_tiempo t USING (sk_tiempo)
JOIN dim_sector s USING (sk_sector)
GROUP BY 1, 2, 3;
```

Reutiliza las dimensiones conformadas `dim_tiempo` y `dim_sector` **sin crear nada nuevo** — exactamente para lo que sirve una dimensión conformada. Solo haría falta una tabla de hechos agregada si la medición mostrara que esa consulta sobre cientos de miles de filas no alcanza el tiempo esperado; esa decisión, con su número, se toma en S11 (`docs/practicas/S11_implementacion_acueducto.md`, § tabla agregada: se midió 9,0 ms vs 0,68 ms y la agregada quedó justificada por 13,3×).

---

*Referencia: Kimball & Ross (2013), The Data Warehouse Toolkit, 3.ª ed.*
