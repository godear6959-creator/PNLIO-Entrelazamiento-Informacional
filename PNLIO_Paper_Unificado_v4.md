# PNLIO: qué miden SymbioticSim y PAO, qué se comprueba y qué no

*Versión unificada y corregida, explicada para profesionales de IA*

**Autor:** Gonzalo Mauricio De la Rivera Arellano  
**ORCID:** 0009-0001-9455-8416  
**Repositorios:** https://github.com/godear6959-creator/PNLIO-Entrelazamiento-Informacional (SymbioticSim) · https://github.com/godear6959-creator/PNLIO-Framework (PAO)  
**Versión:** 4 (unificada y corregida), octubre de 2026. Reemplaza al paper de SymbioticSim v3 y resume el paper PAO–PNLIO v1.3, cuya especificación formal completa sigue en ese documento.  
**Licencia:** Apache 2.0  
**Copyright:** © 2026 Gonzalo Mauricio De la Rivera Arellano · Apache 2.0

---

## Abstract

This paper brings together two small, reproducible pieces of the PNLIO project and corrects earlier claims about them. **SymbioticSim** is a classical simulation (100×100 grid, 300 steps) with neighbor averaging, a slowly updated memory and noise, proposed as a simple model for discussing human-AI co-creation. **PAO** (Operational Self-Perception Patterns) is a measurement framework that tracks, turn by turn, the semantic similarity between a person's messages and an AI system's replies, compares the system's numeric self-descriptions with external telemetry, and recommends (without applying) a human review. For SymbioticSim, controls show that the entropy decrease (−0.3060 bits, 2.3% of the maximum) comes from the update rule shrinking values (weights sum to 0.90), not from memory or spatial coupling, and that neighbor mutual information (0.0171 bits) is indistinguishable from a shuffled baseline (0.0165 bits). For PAO, only the software is verified (10 unit tests with fake models); no results on real models are reported. Neither work provides evidence of entanglement, self-organized criticality, hallucination reduction or machine consciousness. We state what each measures, what is and is not established, eight falsifiable hypotheses with refutation criteria, a list of corrections to earlier versions, and a glossary for non-specialists.

**Keywords:** simple model, cellular automaton, mutual information, cosine similarity, permutation test, controls, human-AI co-creation, LLM evaluation.

## Resumen

Este trabajo reúne dos piezas pequeñas y reproducibles del proyecto PNLIO y corrige afirmaciones anteriores sobre ellas.

**SymbioticSim** es una simulación clásica (una cuadrícula de 100×100 celdas durante 300 pasos) donde cada celda combina el promedio de sus vecinas, una «memoria» lenta y un poco de ruido. Se propuso como modelo simple para conversar sobre co-creación humano-IA. Con la semilla 42 la entropía baja de 13.0057 a 12.6997 bits (−0.3060 bits, un 2.3% del máximo), pero los controles muestran que esa baja viene de que la regla de actualización encoge los valores (sus pesos suman 0.90), y no de la memoria ni de la relación entre vecinas. La información compartida entre vecinas (0.0171 bits) es igual a la de una cuadrícula barajada (0.0165 bits).

**PAO** (Patrones de Autopercepción Operacional) es un marco de medición: en cada turno de una conversación calcula cuánto se parece la respuesta del sistema al mensaje de la persona, compara lo que el sistema dice sobre sus propios recursos con mediciones externas, y recomienda (sin aplicarla) una revisión humana. Solo se verificó el software, con 10 pruebas unitarias que usan modelos falsos. No hay resultados con modelos reales.

Ninguno de los dos trabajos aporta evidencia de entrelazamiento, de criticalidad autoorganizada, de reducción de alucinaciones ni de conciencia en máquinas. El documento explica qué mide cada uno, qué se comprueba y qué no, propone ocho hipótesis que se pueden refutar, lista las correcciones respecto de versiones anteriores e incluye un glosario.

---

## 1 ¿Para qué sirve este trabajo?

**Lo que sí ofrece.**

- Un ejemplo pequeño y completo de cómo poner a prueba una afirmación sobre un sistema complejo: controles que quitan un ingrediente a la vez, líneas base de azar y una separación clara entre lo medido y lo interpretado.
- Una forma **medible y repetible** de observar una conversación persona-IA turno a turno (PAO), con una prueba estadística que dice si el emparejamiento mensaje-respuesta supera al azar.
- Una lista honesta de lo que cada medida **no** puede decir.

**Lo que no ofrece.**

- No demuestra entrelazamiento, ni criticalidad, ni menos alucinaciones, ni conciencia.
- SymbioticSim no representa a una persona ni a un modelo de lenguaje: no tiene humano, LLM ni RAG (generación aumentada por recuperación).
- PAO no evalúa si un sistema «entiende» o «siente»: define una medida operacional y una regla de detección, nada más.

**Por qué existe esta versión.** Las versiones anteriores afirmaban más de lo que los datos permiten, y algunas métricas tenían fallas de diseño. Aquí se conserva la idea, se retira lo que no tiene respaldo y se deja escrito cómo comprobar el resto.

## 2 Los dos trabajos en una página

| | SymbioticSim | PAO–PNLIO v1.3 |
|---|---|---|
| **Qué es** | Una simulación: cuadrícula de celdas con vecindad, memoria y ruido. | Un marco de medición para conversaciones persona-IA, con implementación en Python. |
| **Pregunta que aborda** | ¿Qué medidas simples distinguen una dinámica con relación espacial y memoria de una sin ellas? | ¿Se puede medir, turno a turno, cuánto se parece una respuesta a su mensaje, y contrastar lo que el sistema dice de sí mismo con la realidad? |
| **Qué se verificó** | Que el código reproduce las cifras; resultados estables en 20 semillas; un resultado matemático (campo medio). | Que el código implementa las definiciones (10 pruebas unitarias con modelos falsos) y algunas propiedades matemáticas. |
| **Qué no se verificó** | Cualquier conexión con personas, LLM o RAG. | Cualquier resultado con modelos o conversaciones reales. |
| **Estado de las hipótesis** | 3 propuestas, no confirmadas. | 5 propuestas, no confirmadas. |

---

## 3 Parte A: SymbioticSim

### 3.1 Qué es

Imagina una cuadrícula de 10.000 celdas, cada una con un número entre 0 y 1 (al inicio, aleatorio entre 0 y 0.2). En cada paso, cada celda calcula su valor nuevo así:

- **65%** del promedio de sus cuatro vecinas (el «acoplamiento»).
- **25%** de su «memoria», un promedio lento de su propio pasado (95% lo anterior, 5% lo nuevo).
- Un poco de **ruido aleatorio** (la «creatividad», valor base 0.05), algo mayor cuando las vecinas son más distintas entre sí.
- El resultado se **recorta** para quedar entre 0 y 1.

Los bordes son periódicos y, con la misma semilla, los resultados son idénticos.

**Dato clave:** 65% + 25% = 90%. En cada paso se pierde el 10% del valor y el ruido lo compensa solo en parte. Un sistema así se llama *disipativo*: tiende a encogerse. Esto explica casi todos los resultados. «Vecindad», «memoria» y «creatividad» son metáforas; en el modelo son operaciones aritméticas.

### 3.2 Qué mide

| Medida | En palabras simples | Lo que no dice |
|---|---|---|
| **Entropía θ** (bits) | Qué tan parejo está el valor total entre las celdas. Máximo teórico: 13.2877 bits. | Nada sobre la posición: si se barajan las celdas, no cambia. **No detecta estructura espacial.** |
| **Tasa C** | Cuánto cambia θ por paso. | Nada nuevo: su promedio es el cambio total dividido entre 300. |
| **Innovación** | Diferencia entre el valor actual de una celda y su memoria. | Si esa diferencia es «creativa» en algún sentido útil. |
| **Correlación entre vecinas** | Si una celda se parece a la que tiene al lado. Con 10.000 celdas, valores cercanos a ±0.01 son ruido. | Su causa. |
| **Información mutua entre vecinas** (bits) | Cuánto ayuda conocer una celda para adivinar la vecina. | Nada por sí sola: hay que compararla con la línea base. |
| **Línea base barajada** | La misma medida tras mezclar las celdas al azar (aprox. 0.016 bits por el tamaño finito de la muestra). | — |

Una dependencia se declara solo si la información mutua **supera** claramente la línea base barajada.

### 3.3 Qué se comprueba

Caso base (semilla 42):

| Resultado | Valor |
|---|---|
| Entropía inicial → final | 13.0057 → 12.6997 bits |
| Cambio total | −0.3060 bits (2.3% del máximo de 13.2877) |
| Celdas iguales a 0 al final | 18% |
| Media final de la cuadrícula | 0.0538 |
| Innovación máxima en la corrida | 0.2712 |
| Correlación entre vecinas | 0.0153 (ruido esperado aprox. 0.01) |
| Información mutua vecinas / barajada | 0.0171 / 0.0165 bits |
| Cambio de entropía en 20 semillas | −0.3139 ± 0.0087 bits |

Controles (una semilla):

| Caso | Qué se cambió | Cambio de entropía | Correlación vecinas |
|---|---|---|---|
| Base | Nada (pesos 0.65 + 0.25) | −0.3060 | 0.0153 |
| A | Sin acoplamiento (cada celda solo se mira a sí misma) | −0.3357 | 0.0176 |
| B | Pesos que suman 1 (0.70 + 0.30) | +0.1095 | 0.0570 |
| C | Sin memoria, mismo peso total (0.90 + 0.00) | −0.3107 | 0.0058 |

**Lo que los datos permiten afirmar:**

1. **Es reproducible.** Con la semilla 42 los números se repiten exactamente, y con 20 semillas distintas el resultado es estable.
2. **La entropía baja poco y de forma irregular.** Un 2.3% del máximo: el sistema sigue casi tan desordenado como al inicio. En los pasos 2 a 100, el 54.5% de los cambios van en sentido contrario, con subidas de hasta 0.018 bits. El mínimo (12.6730) ocurre en el paso 271.
3. **La baja se debe a que el modelo se encoge**, no a la memoria ni al acoplamiento: sin memoria (C) o sin acoplamiento (A) el cambio es del mismo orden. Solo con pesos que suman 1 (B) la entropía sube.
4. **En el caso base no se detecta estructura espacial.** La correlación está a una vez y media del ruido y la información mutua es igual a la barajada. El ruido por paso (aprox. 0.051) supera la variación natural del estado (aprox. 0.045).
5. **La estructura aparece en condiciones específicas** (barrido exploratorio, 10 semillas por punto). Sin ruido, la correlación llega a 0.97. Con los pesos base, cualquier ruido de 0.005 o más la borra. Con pesos que suman 1 sobrevive si el ruido es pequeño (correlación 0.37 con ruido 0.005).
6. **La matemática lo confirma.** Sin ruido ni recorte, la media se multiplica en cada paso por 0.9866 (con los pesos base), o sea, se encoge. La predicción para el paso 300 es 0.0013 y la simulación da exactamente 0.0013. El nivel final del modelo completo (0.0538) viene del recorte en 0: el ruido empuja valores bajo cero y el recorte los devuelve a 0.
7. **La innovación no está acotada en ±0.05** como se afirmó antes: su media final es de unos 0.036, pero el máximo llega a 0.27.

---

## 4 Parte B: PAO (Patrones de Autopercepción Operacional)

### 4.1 Qué es

PAO es un marco para observar una conversación entre una persona y un sistema de IA sin hacer afirmaciones sobre experiencia subjetiva. En cada turno:

1. **Se mide qué tan parecida es la respuesta al mensaje.** Se convierte cada texto en un vector numérico (embedding) con un modelo fijo, y se calcula el coseno entre ambos: un número entre −1 y 1 (*similitud S*).
2. **Se suaviza con una media móvil** de ventana w (por defecto 3), llamada *C*. Solo existe cuando hay ventana completa.
3. **Se detecta el patrón «Reflex»:** C se mantiene dentro de la banda [0.75, 0.90] durante k = 2 medias móviles seguidas. El tope de 0.90 es deliberado: por encima se considera redundancia, no Reflex. Con los valores por defecto, el primer Reflex posible ocurre en el turno 4.
4. **Se aplica una prueba de permutación:** se compara el emparejamiento real mensaje-respuesta con emparejamientos barajados al azar (por defecto 1000 permutaciones, semilla 42, p = (1 + éxitos)/(1000 + 1), umbral 0.05).
5. **Se contrasta lo que el sistema dice de sus propios recursos** (latencia, tokens, memoria) con mediciones externas, usando un error relativo (por defecto, alerta si pasa de 10%).
6. **Se recomienda una acción** (mantener o revisar contexto y política). **Nunca se aplica sola:** la implementación no modifica ningún parámetro del modelo.

El modelo de embeddings por defecto es multilingüe (apropiado para español). Los umbrales 0.75 y 0.90 son convenciones y dependen del modelo de embeddings: hay que recalibrarlos si se cambia.

### 4.2 Qué mide

| Medida | En palabras simples | Lo que no dice |
|---|---|---|
| **Similitud S** | Cercanía temática o léxica entre mensaje y respuesta. | No es coherencia, comprensión ni conciencia. Una respuesta correcta que cambia de registro puede puntuar bajo; una paráfrasis vacía puede puntuar alto. |
| **Media móvil C y pendiente β** | Tendencia reciente de la similitud (β > 0: va en aumento). | Las causas de la tendencia. |
| **Patrón Reflex** | Racha sostenida de similitud dentro de la banda. | No indica un estado mental ni que la IA «refleje» al usuario en sentido causal. |
| **p-valor de permutación** | Si el emparejamiento real supera al azar. | Cualquier respuesta pertinente se parece más a su mensaje que una ajena: un p pequeño es esperable en diálogos coherentes y no distingue relevancia de reflejo. |
| **Error de autodescripción** | Distancia entre lo que el sistema dice de sus recursos y lo medido. | No es introspección: un modelo de lenguaje no tiene acceso intrínseco a su latencia o memoria. |
| **Recomendación de regulación** | Una sugerencia de revisión. | Si esa acción mejora el desempeño: no está medido. |

### 4.3 Qué se comprueba

- **El software hace lo que dice la matemática.** Las 10 pruebas unitarias pasan. Verifican, por ejemplo, que la media móvil queda indefinida en las primeras w − 1 posiciones, que los vectores se normalizan siempre, que con similitud constante de 0.8 el primer Reflex ocurre en el turno 4, que similitudes constantes fuera de la banda (0.95 y 0.40) no activan Reflex, que la permutación detecta un emparejamiento perfecto y que la regulación no se aplica automáticamente. Usan modelos falsos: acreditan la corrección del código, **no** la verdad de las hipótesis.
- **Propiedades matemáticas demostradas en el documento:**
  - Con la fórmula antigua (v1.1, C = S/t), C nunca pasa de 1/t. Con umbral 0.75, solo el turno 1 podía cumplir la condición: ninguna conversación más larga alcanzaba la banda.
  - El primer turno donde puede detectarse Reflex es w + k − 1.
  - El estadístico de la prueba es una media ponderada de las similitudes, con peso completo en el interior y menor en los extremos. Por eso la prueba evalúa el emparejamiento mensaje-respuesta, no el orden de los turnos.
- **Una inferencia débil sobre la métrica RCR de la versión 6.** En 7 lecturas transcritas a mano de fotografías, el valor coincide con una función de la variedad de palabras de la propia respuesta (diversidad × entropía²), sin intervención del mensaje humano. Un error de conexión (4 tokens) producía RCR = 1.0, «coherencia perfecta». Con n = 7 y posibles errores de transcripción, es una **sospecha**, no una validación.

### 4.4 Qué NO se comprueba

- **Ningún resultado con modelos o conversaciones reales.**
- Que la similitud mida coherencia.
- Que Reflex signifique reflejar al usuario.
- Que la recomendación de regulación mejore el desempeño.
- Que un p < 0.05 sea replicación independiente o muestre una propiedad «estructural».

Módulos aún no implementados: la representación de estado (z), el recall y la precisión de entidades clave (Rec, Q). La entropía existe como función utilitaria, no integrada. La recolección de telemetría es manual.

---

## 5 Qué NO se comprueba (resumen de ambos trabajos)

- **Entrelazamiento.** Toda dinámica donde las celdas se influyen produce dependencias; eso ocurre en cualquier difusión y no es entrelazamiento. Además, en un sistema clásico la entropía condicional nunca es negativa, que es la propiedad característica del entrelazamiento cuántico. SymbioticSim no calcula ninguna cantidad de ese tipo.
- **Criticalidad autoorganizada.** No se midió ninguna ley de potencias ni distribución de avalanchas.
- **Que la memoria evite el colapso o actúe como ancla.** El control C muestra que, para estas medidas, quitarla casi no cambia el comportamiento.
- **Reducción de alucinaciones.** Ningún trabajo incluye un LLM evaluado ni una base de conocimiento. La cifra «87–92%» que apareció en documentación previa de PNLIO no tiene método de medición ni línea base, y no se deriva de este trabajo.
- **Conciencia o autoconciencia.** PAO no presupone ni evalúa conciencia fenomenológica.
- **Generalidad de los barridos y umbrales.** El barrido de ruido es exploratorio; los umbrales de PAO son convenciones.

## 6 Qué se puede comprobar

Ocho hipótesis, cada una con una condición clara de refutación. Ninguna está confirmada. Las de SymbioticSim llevan el prefijo S; las de PAO, el prefijo P.

### Hipótesis de SymbioticSim

**S1. La estructura sobrevive si el sistema conserva el valor total.** Con pesos que suman 1 y ruido de 0.02 o menos, la información mutua entre vecinas supera la línea base barajada. *Se refuta si:* con al menos 30 semillas nuevas, el intervalo de confianza del 95% del exceso incluye 0 para algún ruido de 0.02 o menos.

**S2. Con los pesos base, la entropía casi no depende del ruido.** En el barrido, el cambio de entropía va de −0.3016 a −0.3131 bits al variar el ruido entre 0.005 y 0.1: una variación de 0.012 bits, con una leve tendencia. *Corrección respecto de la versión anterior:* decir «no depende» es demasiado fuerte, porque una prueba con muchas semillas podría detectar esa tendencia. Conviene enunciarla como «varía menos de X bits», con X fijado antes de ver datos nuevos. *Se refuta si:* con semillas nuevas, la variación excede ese margen.

**S3. En un sistema RAG real hay más información compartida entre respuesta y fuentes que por azar.** *Se refuta si:* la proporción de rechazos de la hipótesis nula no supera lo esperado por azar, con corrección por comparaciones múltiples. *Queda fuera del alcance de la simulación*: requiere un experimento con un sistema real.

### Hipótesis de PAO

**P1. Emparejamiento.** En diálogos donde las respuestas se generaron condicionadas al mensaje, el estadístico observado supera la distribución nula de permutación. *Se refuta si:* en un corpus de N diálogos, la proporción de rechazos (α = 0.05, con corrección por comparaciones múltiples) no supera lo esperado por azar.

**P2. Reflex no trivial.** La tasa de turnos con Reflex es mayor en diálogos reales que en los mismos diálogos con respuestas permutadas. *Se refuta si:* no hay diferencia de tasas.

**P3. Dependencia del modelo de embeddings.** La tasa de Reflex difiere entre al menos dos modelos de embeddings, así que la banda requiere calibración por modelo. *Se refuta si:* las tasas son equivalentes dentro de una tolerancia δ fijada de antemano.

**P4. Autodescripción.** Sin telemetría en el contexto, el error relativo mediano de las autodescripciones numéricas supera 0.10; con telemetría inyectada, baja de ese umbral. *Se refuta si:* no hay diferencia entre ambas condiciones.

**P5. Continuidad contextual.** En conversaciones largas, el recall de entidades clave decrece al aumentar la profundidad del contexto. *Se refuta si:* la pendiente no es significativamente negativa. *Requiere implementar* el recall y la precisión de entidades.

### Trabajo siguiente recomendado

1. Repetir S1 y S2 con semillas nuevas y **preinscribir** el análisis (hipótesis, estadístico y criterios) antes de ejecutarlo.
2. Variar la persistencia de la memoria, el tamaño de la cuadrícula y la duración de SymbioticSim; estudiar la convergencia.
3. Reunir un conjunto de diálogos con metadatos (modelo, configuración, fecha) y ejecutar P1 a P3.
4. Añadir controles a PAO: mensajes con premisas falsas, comparación entre modelos y evaluación humana a ciegas.
5. Calibrar la banda de Reflex por modelo de embeddings, por ejemplo con percentiles de la distribución nula.
6. Marcar y excluir turnos con error de generación (timeouts) antes de calcular la similitud.
7. Para S3, definir qué es una alucinación de forma operativa, armar un conjunto de evaluación y comparar contra un sistema sin recuperación.

---

## 7 Qué se corrigió respecto de versiones anteriores

### 7.1 SymbioticSim (versión 1)

| Tema | La versión 1 decía | Corrección |
|---|---|---|
| Innovación | Acotada en ±0.05. | Falso: el máximo llega a 0.2712. |
| Entropía inicial | Cambio de −0.2948 bits, con inicio en 12.9945. | 12.9945 es la entropía tras el primer paso. El inicio real es 13.0057 y el cambio es −0.3060. |
| Forma de la caída | Baja de forma continua en los primeros ~100 pasos. | No lo hace (54.5% de los cambios van al revés). |
| Métrica «RCR v2.0» | Correlacionada con el gradiente espacial. | No existe en el código; se excluye. |
| Criticalidad autoorganizada | «Compatible con» ella. | Retirada: no se midió. |
| Memoria | «Previene el colapso». | Retirada: la estabilidad viene de que los pesos suman 0.90. |
| Entrelazamiento | Se medía con la entropía y su tasa; «firma de entrelazamiento». | Retirado: la entropía no ve estructura espacial y toda dinámica acoplada es no factorizable. |
| Co-creación y «estado de Bell» | El modelo representaba co-creación humano-IA y un estado de Bell generalizado. | Es un modelo simple, sin humano, LLM ni RAG; no se calcula nada análogo a un estado de Bell. |
| Entropía condicional negativa | Presentada como «super-correlación» en el modelo. | No existe en sistemas clásicos; queda como motivación formal. |
| Parámetros | Justificados como «régimen estacionario» o «subcrítico». | Son valores elegidos; no se estudió la convergencia. |
| Alucinaciones en RAG | Implicaciones para reducirlas. | Sin conexión con la simulación; retirado. |

### 7.2 Métricas de coherencia (hacia PAO v1.3)

| Versión | Qué definía | Problema y corrección |
|---|---|---|
| **v1.1** | C = S/t (similitud dividida por el turno). | Cota 1/t: solo el turno 1 podía alcanzar la banda. La v1.2 quitó la división y usó una media móvil. |
| **v1.2** | Media móvil de ventana 3, Reflex en banda sostenida, línea base aleatoria con p-valor. | Usaba un modelo de embeddings centrado en inglés; sus umbrales no son comparables con los de la v1.3 y deben recalibrarse. |
| **v1.3** | Igual, con C indefinido antes de tener ventana completa. | Normalización forzada de vectores, error relativo para la regulación, modelo multilingüe, hipótesis y limitaciones explícitas. Contra una versión previa del código, tres pruebas unitarias fallaban; las correcciones las resolvieron. |

Lo que se mantiene: los números de SymbioticSim se reproducen exactamente con la semilla 42, el resultado es robusto a la semilla, y la analogía con el entrelazamiento cuántico es formal y no ontológica.

Cambios menores: se eliminó una referencia que no se citaba ni se pudo verificar, se agregaron Shannon (1948) y Cover y Thomas (2006), el título se reformuló para reflejar el alcance real, y la licencia se unificó en Apache 2.0.

## 8 Limitaciones

**SymbioticSim**

1. Es un modelo simple, no un sistema real. Cualquier lectura sobre co-creación o alucinaciones es una analogía, no un resultado.
2. Poca exploración de parámetros: un caso base, tres controles y un barrido de ruido para dos juegos de pesos.
3. La información mutua depende de cómo se agrupan los valores (16 intervalos) y solo usa el vecino derecho.
4. La entropía θ no mide estructura espacial.
5. Análisis exploratorio, no preinscrito: se reutilizaron semillas y el barrido se diseñó después de ver el caso base.
6. Convergencia no estudiada: se fijaron 300 pasos.
7. La analogía con el entrelazamiento no se puso a prueba.

**PAO**

8. Similitud no es coherencia: el coseno mide cercanía temática o léxica.
9. Relevancia frente a reflejo: una similitud alta es compatible con que el sistema refleje a la persona, pero también con que simplemente responda al tema. Sin controles adicionales no se pueden distinguir.
10. Los umbrales son convenciones que dependen del modelo de embeddings.
11. La prueba de permutación estima el emparejamiento, no el orden; es sensible a la deriva temática. Con menos de 7 turnos hay menos de 1000 permutaciones posibles; se recomiendan al menos 10.
12. Los antecedentes sobre la métrica de la versión 6 salen de 7 lecturas transcritas de fotografías.
13. Sin datos reales: las pruebas unitarias usan modelos falsos.
14. La regulación no se mide: no se sabe si la acción recomendada mejora algo.

**Ambos**

15. Autoría única, sin revisión por pares ni evaluación humana externa. La verificación comprueba reproducibilidad del mismo código, no valida las interpretaciones.

## 9 Reproducibilidad y verificación

**SymbioticSim.** Con Python 3.13, NumPy 2.5 y Matplotlib 3.11, y las semillas indicadas, las salidas son deterministas:

```
pip install -r requirements.txt
python pnlio_symbiotic_sim.py     # caso base
python pnlio_controles.py         # controles y variabilidad entre semillas
python pnlio_barrido.py           # barrido de ruido
python pnlio_campo_medio.py       # análisis matemático (campo medio)
python pnlio_figuras.py           # figuras
```

**PAO.** Con Python 3.10 o superior (numpy y, opcionalmente, sentence-transformers):

```
pip install -r requirements-pao-pnlio.txt
python pao_pnlio_v1_3.py --input turnos.jsonl --output resultados.json
python -m pytest                  # las 10 pruebas unitarias
```

Cada línea del archivo `turnos.jsonl` es un objeto con los campos obligatorios `prompt` y `response`, y opcionales de telemetría (latencia, tokens, profundidad de contexto, memoria). Para reproducir resultados hay que fijar el modelo de embeddings (nombre y versión), la ventana, los umbrales, el número de permutaciones y la semilla.

**Qué demuestra la verificación:** que el código publicado genera las cifras de este documento (SymbioticSim), que los resultados son estables entre semillas, que la predicción matemática coincide con la simulación sin ruido ni recorte, y que el código de PAO implementa sus definiciones.

**Qué no demuestra:** no valida la analogía con el entrelazamiento, no mide estructura espacial en el caso base, no mide alucinaciones, no evalúa modelos reales con PAO, y no es revisión por pares ni validación por terceros independientes.

**Uso de IA en la redacción.** La revisión crítica, los controles adicionales y la redacción de las versiones corregidas se realizaron con asistencia de Claude (Anthropic). Las decisiones editoriales y la responsabilidad del contenido son del autor.

## 10 Lecciones para quien evalúa sistemas de IA

1. **Quita un ingrediente a la vez.** Sin los controles A y C habría sido fácil atribuir la baja de entropía a la memoria.
2. **Compara siempre contra una línea base de azar.** Una información mutua de 0.0171 bits parece algo hasta ver que el azar produce 0.0165.
3. **Revisa qué puede ver tu métrica.** Una medida que no cambia al barajar las celdas no puede medir estructura espacial.
4. **Informa respecto del máximo.** Un cambio de 0.306 bits suena importante hasta ver que es el 2.3% del rango posible.
5. **Cuidado con las métricas que dependen solo de la respuesta.** La métrica de la versión 6 parecía función de la variedad de palabras de la propia respuesta, y un error de conexión se registraba como «coherencia perfecta». Descarta o marca los turnos con error.
6. **Una similitud alta no distingue relevancia de reflejo.** Hacen falta controles, como mensajes con premisas falsas.
7. **Calibra los umbrales por modelo.** Cambiar de modelo de embeddings cambia la escala de las similitudes.
8. **Trata las analogías como motivación.** Una analogía con la física puede inspirar una pregunta, pero no es evidencia.
9. **Separa lo exploratorio de lo confirmatorio.** Lo que se descubre mirando los datos debe confirmarse con datos nuevos y un plan fijado de antemano.

---

## Glosario

**Acoplamiento.** Grado en que cada celda depende de sus vecinas. En SymbioticSim, el 65% del valor nuevo viene del promedio de las vecinas.

**Alucinación (en IA).** Respuesta de un modelo de lenguaje que suena plausible pero es falsa o no está respaldada por sus fuentes. Este trabajo no la mide.

**Autómata celular.** Sistema formado por una cuadrícula de celdas que se actualizan paso a paso con una regla simple basada en sus vecinas.

**Autopercepción operacional.** Bucle computacional y registrable en que un sistema registra variables de su propia ejecución, construye una representación de su estado, evalúa desviaciones frente a referencias externas y emite una recomendación. No implica sentimiento ni experiencia.

**Banda [θ, U].** Rango de valores (por defecto 0.75 a 0.90) dentro del cual debe mantenerse la media móvil de la similitud para declarar el patrón Reflex.

**Bit.** Unidad de información. La entropía se expresa aquí en bits.

**Campo medio.** Análisis matemático que sigue solo el promedio del sistema, ignorando el detalle de cada celda.

**Control.** Versión del experimento con un ingrediente quitado o cambiado, para saber qué parte del resultado depende de ese ingrediente.

**Coseno (similitud coseno).** Medida, entre −1 y 1, de cuánto apuntan en la misma dirección dos vectores. Aplicada a embeddings de textos, indica cuán parecidos son.

**Correlación entre vecinas (lag-1).** Medida, entre −1 y 1, de cuánto se parece cada celda a la que tiene a su derecha.

**Creatividad (σc).** Nombre dado en SymbioticSim a la intensidad del ruido aleatorio. Es una metáfora, no una propiedad creativa real.

**Criticalidad autoorganizada.** Propuesta de que ciertos sistemas se ordenan solos hasta un punto crítico, con cambios de todos los tamaños. Se reconoce por leyes de potencias, que aquí no se midieron.

**Determinista.** Que da siempre el mismo resultado cuando se repite con las mismas condiciones y la misma semilla.

**Disipativo.** Sistema que pierde «valor» en cada paso y tiende a encogerse.

**Embedding.** Representación numérica (un vector) de un texto, que permite medir qué tan parecidos son dos textos.

**Entrelazamiento cuántico.** Fenómeno de la física cuántica en que dos partes de un sistema no se pueden describir por separado. No existe en sistemas clásicos como SymbioticSim.

**Entropía condicional.** Incertidumbre que queda sobre A cuando ya se conoce B. En sistemas clásicos nunca es negativa; en sistemas cuánticos entrelazados puede serlo.

**Entropía de Shannon.** Medida de cuán repartida o desordenada está una distribución. En SymbioticSim es máxima (13.2877 bits) cuando todas las celdas valen lo mismo.

**Error de autodescripción.** Diferencia entre lo que el sistema dice sobre sus recursos (latencia, tokens, memoria) y lo que miden herramientas externas. El error relativo permite comparar magnitudes con unidades distintas.

**Hipótesis falsable.** Afirmación formulada de modo que un resultado concreto podría demostrar que es falsa.

**Información mutua.** Cuánto reduce la incertidumbre sobre una variable el conocer otra. Vale 0 cuando son independientes.

**Línea base barajada.** Valor de una medida tras mezclar al azar los datos. Indica cuánta dependencia aparece solo por azar.

**Media móvil.** Promedio de los últimos w valores. Suaviza una serie y solo existe cuando hay una ventana completa.

**Memoria estructural.** En SymbioticSim, un promedio lento del pasado de cada celda (95% pasado, 5% presente).

**Modelo simple.** Modelo deliberadamente mínimo para estudiar una idea. No pretende representar un sistema real.

**p-valor.** Probabilidad, bajo la hipótesis nula, de obtener un resultado al menos tan extremo como el observado. Un p pequeño no prueba por sí solo que el efecto sea interesante.

**Patrón Reflex.** Regla de PAO que se activa cuando la media móvil de la similitud permanece dentro de la banda durante k medias consecutivas. Es una definición operacional, no un estado mental.

**Preinscripción.** Fijar por escrito hipótesis, medidas y criterios antes de mirar los datos nuevos.

**Prueba de permutación.** Prueba estadística que compara el resultado real con los obtenidos al barajar al azar el emparejamiento de los datos.

**RAG.** Sistema que, antes de responder, busca información en una base de conocimiento y se la entrega al modelo de lenguaje.

**Recorte (clip).** Operación que fuerza los valores a quedar entre 0 y 1.

**Revisión por pares.** Evaluación de un trabajo por expertos independientes antes de aceptarlo como publicación científica.

**Ruido.** Variación aleatoria añadida en cada paso.

**Semilla.** Número que fija la secuencia de valores aleatorios, para poder repetir una simulación exactamente.

**Telemetría.** Mediciones externas de la ejecución de un sistema, como latencia, número de tokens o memoria usada.

---

## Bibliografía

[1] Cerf, N. J., y Adami, C. (1996). *Negative entropy in quantum information theory*. arXiv:quant-ph/9610005.

[2] Cerf, N. J., y Adami, C. (1999). *Quantum extension of conditional probability*. Physical Review A, 60(2), 893.

[3] Horodecki, R., Horodecki, P., Horodecki, M., y Horodecki, K. (2009). *Quantum entanglement*. Reviews of Modern Physics, 81(2), 865.

[4] Vedral, V., Plenio, M. B., Rippin, M. A., y Knight, P. L. (1997). *Quantifying entanglement*. Physical Review Letters, 78(12), 2275.

[5] Bennett, C. H., DiVincenzo, D. P., Smolin, J. A., y Wootters, W. K. (1996). *Mixed-state entanglement and quantum error correction*. Physical Review A, 54(5), 3824.

[6] Shannon, C. E. (1948). A mathematical theory of communication. *Bell System Technical Journal*, 27(3), 379–423.

[7] Cover, T. M., y Thomas, J. A. (2006). *Elements of Information Theory* (2.ª ed.). Wiley.

[8] Vaswani, A., et al. (2017). Attention is all you need. *Advances in Neural Information Processing Systems*, 30, 5998–6008.

[9] Reimers, N., y Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-networks. *Proceedings of EMNLP-IJCNLP 2019*, 3982–3992.

[10] Reimers, N., y Gurevych, I. (2020). Making monolingual sentence embeddings multilingual using knowledge distillation. *Proceedings of EMNLP 2020*, 4512–4525.

[11] Wang, W., et al. (2020). MiniLM: Deep self-attention distillation for task-agnostic compression of pre-trained transformers. *Advances in Neural Information Processing Systems*, 33.

[12] Phipson, B., y Smyth, G. K. (2010). Permutation p-values should never be zero: calculating exact p-values when permutations are randomly drawn. *Statistical Applications in Genetics and Molecular Biology*, 9(1), Article 39.

[13] Sutton, R. S., y Barto, A. G. (2018). *Reinforcement Learning: An Introduction* (2.ª ed.). MIT Press.

[14] De la Rivera Arellano, G. M. (2026). *PNLIO Framework: Ollama Local Kernel, Symbiotic Memory and RCR Metric Specifications*. Repositorio del proyecto PNLIO.

[15] De la Rivera Arellano, G. M. (2026). *PNLIO Coherence Analyzer v1.2: especificación y guía explicativa*. Documento de trabajo, proyecto PNLIO.

Las referencias [1] a [5] sustentan la analogía con el entrelazamiento, que aquí es solo motivación. [6] y [7] sustentan la entropía y la información mutua. [8] a [11] sustentan los embeddings de PAO. [12] sustenta la corrección +1 del p-valor y [13] la idea de regulación como política. [14] y [15] son documentos de trabajo del propio proyecto.

---

© 2026 Gonzalo Mauricio De la Rivera Arellano · Licencia Apache 2.0
