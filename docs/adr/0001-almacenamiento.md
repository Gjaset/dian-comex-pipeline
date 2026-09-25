# ADR 0001 · Paradigma de almacenamiento del proyecto

---

## Título y estado

**Título:** Paradigma de almacenamiento del proyecto DIAN Importaciones
**Estado:** Aceptado
**Fecha:** 2026-09-11
**Equipo:** DIAN Importaciones · Germán Cuesta, Jose Alejandro Hernandez, Juan Camilo Pardo

---

## Contexto

El proyecto ya tiene un lago por capas operativo (MinIO, convención `importaciones_dian/anio=YYYY/mes=MM/dia=DD/`, Parquet zstd en refinada, versionado en cruda) y su arquitectura de T8 es vía única con flujo acotado: cuatro requisitos por lotes (frescura de días/horas, ~2.89 GB/mes) y uno de flujo (alertas, minutos). Debemos decidir si mantener el lago tal cual, endurecerlo a lakehouse o migrar a almacén, antes del modelado dimensional de las sesiones 10-11.

---

## Decisión

**Opción elegida:** Lago (mantener el lago por capas actual, sin transacciones).

### Matriz de criterios ponderados

Calificación de 1 a 5 por opción (5 = mejor). Pesos suman 100.

| Criterio | Peso | Justificación del peso | Almacén | Lago | Lakehouse |
|---|---|---|---|---|---|
| Costo de almacenamiento | 20 % | Equipo pequeño sin presupuesto de infraestructura dedicada; cada GB y cada pieza cuentan | 2 | 5 | 3 |
| Flexibilidad de esquema | 20 % | El esquema ya cambió dos veces (166→162 columnas; ALADI→M49): lo rígido duele aquí | 1 | 5 | 4 |
| Rendimiento de consulta analítica | 20 % | Lecturas selectivas por mes/aduana sobre 2.9 GB: lo columnar basta, pero un motor optimizado ayuda | 4 | 3 | 5 |
| Soporte transaccional y viaje en el tiempo | 10 % | Sin escritores concurrentes; las cifras provisionales se reprocesan, no se transaccionan | 4 | 1 | 5 |
| Complejidad operativa | 20 % | Tres personas que ya operan YARN/MinIO/Postgres: cada pieza nueva compite por el mismo tiempo | 2 | 5 | 2 |
| Adecuación al volumen y la frescura | 10 % | Lote mensual de ~2.9 GB: encaja en las tres opciones, no discrimina mucho | 2 | 5 | 3 |
| **Puntaje ponderado** | **100 %** | | **2.40** | **4.20** | **3.60** |

Cálculo: almacén = .2(2+1+4)+.1(4)+.2(2)+.1(2) = 2.40; lago = .2(5+5+3)+.1(1)+.2(5)+.1(5) = 4.20; lakehouse = .2(3+4+5)+.1(5)+.2(2)+.1(3) = 3.60.

**Lectura de ingeniería.** El lago gana por costo, flexibilidad y simplicidad operativa, no por rendimiento: el lakehouse lo supera en consulta analítica (5 vs 3) y transacciones (5 vs 1), pero esas son justo las dimensiones de menor peso para un lote mensual de 2.9 GB sin escritores concurrentes. La diferencia (4.20 vs 3.60) está en la complejidad: montar Delta/Iceberg + Spark + catálogo para ganar transacciones que ningún requisito pide sería pagar de más. No se eligió lakehouse por defecto aunque era la opción "moderna".

---

## Consecuencias

**Lo que se gana.** Costo mínimo (MinIO local + Parquet zstd que comprime el CSV ~88 %: 5.32 GiB crudos → ~1.0 GiB refinados), esquema flexible ante los cambios de la DIAN (la cruda intacta permite reprocesar cualquier cambio M49/columnas), y una operación que el equipo ya domina (recetas verificadas T4/T5/T6).

**Lo que se sacrifica.** Sin transacciones ACID ni viaje en el tiempo: dos escrituras concurrentes a la refinada podrían corromperla, y no hay rollback declarativo (solo versiones S3 en cruda y recomputo). Sin motor de consulta optimizado: las lecturas selectivas dependen de poda de particiones manual, no de índices. Renuncia razonable porque hoy hay un solo escritor (el pipeline mensual) y un solo equipo.

**Cuándo reabrir la decisión.** Si aparecen escritores concurrentes o requisitos de auditoría que exijan transacciones (pasar a lakehouse); si el volumen llega a TB con SLA sub-segundo (revaluar almacén/lakehouse); si el equipo crece a múltiples dominios con dueños independientes (revaluar malla, ver T8 §3).

---

## Referencias

Kleppmann, M. (2017). *Designing data-intensive applications*. O'Reilly Media.

Reis, J., y Housley, M. (2022). *Fundamentals of data engineering*. O'Reilly Media.

---

## Autoverificación antes de entregar

- [x] El ADR tiene las cuatro partes: título y estado, contexto, decisión y consecuencias.
- [x] La matriz ponderada está dentro del ADR, con pesos justificados que suman 100.
- [x] La decisión es coherente con la arquitectura de T8 y cita las cifras de T7.
- [x] Las consecuencias nombran al menos un costo aceptado y cuándo reabrir la decisión.
- [x] No se eligió lakehouse por defecto: la matriz respalda la decisión.
- [x] Los pesos no se ajustaron para forzar un resultado predeterminado.
- [ ] El ADR está versionado en el repositorio, con historial en Git (pendiente: commit del equipo antes del cierre).
