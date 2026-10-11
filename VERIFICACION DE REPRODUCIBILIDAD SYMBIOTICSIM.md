# Verificación de reproducibilidad: PNLIO SymbioticSim

© 2026 Gonzalo Mauricio De la Rivera Arellano · Apache 2.0

**Fecha de esta verificación:** 11 de octubre de 2026 (reemplaza la del 6 de agosto de 2026)
**Código verificado:** `pnlio_symbiotic_sim.py`, `pnlio_controles.py`, `pnlio_barrido.py`, `pnlio_campo_medio.py`, `pnlio_figuras.py`
**Entorno:** Python 3.13, NumPy 2.5, Matplotlib 3.11.
**Método:** ejecución directa de los scripts con las semillas indicadas en `paper.md`. Realizada con asistencia de Claude (Anthropic) a pedido del autor.

> Es una verificación de reproducibilidad computacional del mismo código. No es revisión por pares ni validación por terceros independientes.

## Resultado

Las cifras del paper coinciden con la salida de los scripts:

| Métrica (caso base, semilla 42) | En el paper | Salida del script |
|---|---|---|
| θ inicial real (antes del paso 1) | 13.0057 bits | 13.005689 |
| θ tras el paso 1 | 12.9945 bits | 12.994496 |
| θ final | 12.6997 bits | 12.699663 |
| Δθ (final − inicial real) | −0.3060 bits | −0.306026 |
| Δθ (final − tras el paso 1) | −0.2948 bits | −0.294833 |
| C media | −0.00102 bits/paso | −0.001020 |
| Grilla final (media) | 0.0538 | 0.0538 |
| Máx. \|φ − M\| en la corrida | 0.2712 | 0.2712 |
| Corr. lag-1 / MI vecinas / MI barajado | 0.0153 / 0.0171 / 0.0165 | 0.0153 / 0.0171 / 0.0165 |

Las tablas de controles (Cuadros 5 y 6), del barrido de σ_c (Cuadro 7) y del campo medio (Cuadro 8 y Sección 6.6) se regeneran con los scripts y quedan en `resultados_controles.md`, `resultados_barrido.md` y `resultados_campo_medio.md`. Los valores numéricos de los cuadros del paper se cotejaron automáticamente contra esos archivos.

La verificación del 6 de agosto de 2026 sobre la versión original del script confirmó los mismos valores de θ, Δθ (medido desde el paso 1) y C. La dinámica no cambió en la versión actual: solo se añadieron registros de métricas y parámetros opcionales (los valores por defecto reproducen la versión original).

## Cómo reproducir

```
pip install -r requirements.txt
python pnlio_symbiotic_sim.py
python pnlio_controles.py
python pnlio_barrido.py
python pnlio_campo_medio.py
python pnlio_figuras.py
python construir_pdf.py     # requiere pandoc y xelatex
```

## Qué demuestra

- El código publicado genera los números del paper (determinista con la semilla fija).
- Los resultados son robustos frente a la semilla (20 semillas en el caso base, 10 en el barrido).
- La Proposición 1 (campo medio) coincide con la simulación sin ruido ni recorte.

## Qué NO demuestra

- No valida la analogía con el entrelazamiento cuántico (formal, no ontológica).
- No mide estructura espacial en el caso base: la información mutua entre vecinas coincide con la línea base barajada.
- No mide reducción de alucinaciones: el modelo no incluye LLM ni RAG.
- Los resultados del barrido son exploratorios y no confirman las hipótesis H1 a H3.
- No constituye peer review.
