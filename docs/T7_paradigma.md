# T7 · Decisión de paradigma del proyecto

**Equipo:** DIAN Importaciones
**Integrantes:** Germán Cuesta, Jose Alejandro Hernandez, Juan Camilo Pardo
**Proyecto:** Pipeline de Importaciones DIAN
**Fecha:** 2026-09-01

---

## 0. Supuestos declarados

Todo supuesto que tomen para decidir va aquí, no escondido en el texto. Ejemplo: si un requisito es ambiguo entre lotes nocturnos y casi real, digan cuál supusieron y por qué.

- Supuesto 1: Los datos de importaciones DIAN se publican mensualmente con un rezago de aproximadamente 45 días, por lo que no requieren actualización en tiempo real para la mayoría de los análisis estadísticos.
- Supuesto 2: Los requisitos de detección de anomalías y alertas se benefician de una latencia menor, pero no necesitan estrictamente tiempo real (segundos), ya que los patrones fraudulentos pueden detectarse con datos de minutos o horas de antigüedad sin impacto crítico.

---

## Parte A · Tabla de asignación de paradigma

Al menos tres requisitos de dato del proyecto. Las cifras pueden ser órdenes de magnitud; lo que importa es que nazcan del caso.

| Requisito | Frescura exigida | Volumen por ciclo | Paradigma | Justificación en una frase |
|---|---|---|---|---|
| Procesamiento mensual de declaraciones de importación | días | ~2.89 GB/mes | lotes | Los datos se publican mensualmente y el análisis de tendencias no se ve afectado por esperar el rezago oficial de publicación. |
| Validación y calidad de datos entrantes | horas | ~2.89 GB/mes | casi real | Se ejecuta poco después de la descarga para detectar problemas temprano, pero no requiere segundos ya que los archivos se procesan como unidad. |
| Dashboard de monitoreo de tendencias comerciales | horas | ~100 MB/día | lotes | Las tendencias mensuales o trimestrales no requieren actualización subdiaria; se actualizan con los datos procesados mensualmente. |
| Sistema de alertas para patrones sospechosos | minutos | ~10 KB/hora | flujo | La detección oportuna de anomalías justifica el costo de flujo para responder rápidamente a posibles fraudes o errores sistémicos. |
| API de consulta de estadísticas históricas | días | variable según consulta | lotes | Los usuarios consultan datos históricos agregados; la frescura de días es suficiente ya que los datos fuente se actualizan mensualmente. |

**Paradigma del proyecto en conjunto:** híbrido. Los requisitos de procesamiento mensual, validación de datos, dashboard y API histórica van por lotes/casi real, mientras que el sistema de alertas va por flujo. El híbrido no es indecisión: es la respuesta correcta cuando los requisitos exigen frescuras distintas.

---

## Parte B · Compromiso del teorema CAP

Elijan un requisito real del proyecto, imaginen una caída de la red entre nodos y declaren su compromiso.

- **Requisito sobre el que se decide:** Sistema de alertas para patrones sospechosos
- **Bajo una partición de red, elegimos:** disponibilidad (seguir respondiendo con el último valor conocido, que puede estar desactualizado)
- **Por qué en este requisito:** en un sistema de detección de fraudes, es preferible generar una alerta basada en datos ligeramente antiguos que no generar ninguna alerta. Perder una detección por insistir en consistencia podría permitir que una actividad fraudulenta continúe sin intervención, mientras que una alerta basada en datos recientes pero no instantáneos aún permite una respuesta oportuna.

---

## Parte C · Defensa ante la gerencia

Media página. La gerencia ve el costo de la parte por flujo y objeta: "¿por qué no ponemos todo por lotes, que es más barato?". Respondan cubriendo los cuatro puntos.

**El requisito crítico.** El sistema de alertas para patrones sospechosos exige frescura de minutos porque está diseñado para detectar actividades inusuales como posibles fraudes en declaraciones de importación o fallos sistémicos en el proceso de ingreso de datos.

**El costo de no tenerla.** Si los datos de alertas llegan tarde (por ejemplo, en lotes diarios), una anomalía que debería investigarse inmediatamente podría pasar desapercibida durante horas, permitiendo que se repitan operaciones fraudulentas o que se acumulen errores en el procesamiento que podrían afectar reportes oficiales.

**El resto por lotes.** Los demás requisitos (procesamiento mensual, validación de datos, dashboard de tendencias y API histórica) sí pueden ir por lotes porque tratan con datos que ya están consolidados y publicados oficialmente por la DIAN. Al procesarlos por lotes, aprovechamos la eficiencia económica de ejecutar trabajos intensivos en recursos solo cuando es necesario, en lugar de mantener sistemas de flujo encendidos continuamente.

**La conclusión.** El enfoque híbrido cuesta menos que todo flujo porque limita el costo elevado de los sistemas de streaming solo al requisito que realmente lo necesita (alertas). Arriesga menos que todo lotes porque mantiene la capacidad de detección oportuna para el requisito crítico, mientras que un enfoque puramente por lotes dejaría sin protección oportuna contra fraudes o fallos en tiempo cercano al presente.

---

## Autoverificación antes de entregar

Marquen cada casilla. Si una queda sin marcar, la tarea se devuelve.

- [x] Hay al menos tres requisitos, cada uno con paradigma y una frase de justificación.
- [x] Cada requisito tiene sus dos cifras: frescura exigida y volumen por ciclo, sin celdas vacías.
- [x] La frescura declarada es la exigida por el negocio, no la deseable. No todo quedó en segundos sin razón.
- [x] Se nombra un compromiso CAP concreto, aplicado a un requisito real, con su porqué.
- [x] La defensa sostiene la decisión con qué se rompe sin la frescura crítica, no con la novedad del tiempo real.
- [x] Los supuestos que se tomaron están declarados en la sección 0.

---

## Referencias

Brewer, E. A. (2012). CAP twelve years later: How the "rules" have changed. *Computer, 45*(2), 23-29. https://doi.org/10.1109/MC.2012.37

Kleppmann, M. (2017). *Designing data-intensive applications*. O'Reilly Media.