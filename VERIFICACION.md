# Verificación independiente — PNLIO SymbioticSim

**Fecha de verificación:** 6 de agosto de 2026
**Código verificado:** `pnlio_symbiotic_sim.py`
**Método:** re-ejecución directa del script tal como fue publicado, sin modificaciones, con `seed=42`, `size=100`, `creativity=0.05`, `steps=300`.

## Resultado

Los valores obtenidos al re-ejecutar el script coinciden **exactamente** con los reportados en `paper.md` (Sección 5.1):

| Métrica | Valor reportado en el paper | Valor reproducido |
|---|---|---|
| θ inicial | 12.9945 bits | 12.994496 bits |
| θ final | 12.6997 bits | 12.699663 bits |
| Δθ total | −0.2948 bits | −0.294833 bits |
| C media | −0.00102 bits/paso | −0.001020 bits/paso |

## Qué demuestra esto

- El código fuente publicado es el mismo que generó los números del paper — no hay discrepancia entre lo documentado y lo ejecutable.
- Los resultados son determinísticos y reproducibles dado el seed fijo (comportamiento esperado, ya que `np.random.seed(42)` fija el generador de números aleatorios).

## Qué NO demuestra esto

- No valida la analogía con entrelazamiento cuántico como fenómeno físico real (el propio paper aclara en la Sección 6.3 que la analogía es formal, no ontológica).
- No mide reducción de alucinaciones en un sistema RAG real con un LLM — esta simulación es un autómata celular aislado, sin conexión a Ollama ni a ningún modelo de lenguaje.
- No constituye peer review ni validación por terceros independientes a este proyecto — es una verificación de reproducibilidad computacional, nada más.
