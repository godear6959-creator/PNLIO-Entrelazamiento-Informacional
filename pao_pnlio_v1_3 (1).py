#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAO–PNLIO v1.3 — implementación experimental reproducible
Autor del marco: Gonzalo Mauricio de la Rivera Arellano / Comandante Godear24
Copyright 2026 Gonzalo Mauricio De la Rivera Arellano
Licencia: Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)

IMPORTANTE:
- Este módulo mide similitud semántica entre mensajes y respuestas; no mide conciencia.
- La detección Reflex es una regla operacional configurable, no una prueba de un estado mental.
- La prueba de permutación evalúa una hipótesis nula concreta: que emparejar respuestas
  con prompts no produce una estadística mayor que emparejamientos aleatorios.
- execute_self_regulation() entrega una recomendación de política; no cambia por sí sola
  los parámetros de un LLM.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Sequence

import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None  # type: ignore[assignment]


DEFAULT_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Devuelve la similitud coseno; retorna 0 si algún vector tiene norma cero."""
    a = np.asarray(a, dtype=np.float64).reshape(-1)
    b = np.asarray(b, dtype=np.float64).reshape(-1)
    if a.shape != b.shape:
        raise ValueError(f"Dimensiones incompatibles: {a.shape} y {b.shape}")
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    value = float(np.dot(a, b) / (na * nb))
    return max(-1.0, min(1.0, value))


def moving_average(values: Sequence[float], window: int) -> List[Optional[float]]:
    """
    Media móvil retrospectiva. Las primeras window-1 posiciones son None para
    evitar ventanas parciales y hacer explícita la regla de borde.
    """
    if window < 1:
        raise ValueError("window debe ser >= 1")
    out: List[Optional[float]] = [None] * len(values)
    for i in range(window - 1, len(values)):
        out[i] = float(statistics.fmean(values[i - window + 1 : i + 1]))
    return out


def linear_slope(values: Sequence[float]) -> Optional[float]:
    """Pendiente OLS de valores frente a turnos 0..n-1; None si hay menos de 2."""
    if len(values) < 2:
        return None
    x = np.arange(len(values), dtype=np.float64)
    y = np.asarray(values, dtype=np.float64)
    return float(np.polyfit(x, y, 1)[0])


def shannon_entropy(probabilities: Sequence[float]) -> float:
    """Entropía de Shannon en bits para probabilidades no negativas."""
    p = np.asarray(probabilities, dtype=np.float64)
    if p.ndim != 1:
        raise ValueError("probabilities debe ser un vector unidimensional")
    if np.any(p < 0):
        raise ValueError("Las probabilidades no pueden ser negativas")
    total = float(p.sum())
    if total <= 0:
        raise ValueError("La suma de probabilidades debe ser positiva")
    p = p / total
    p = p[p > 0]
    return float(-np.sum(p * np.log2(p)))


@dataclass
class Telemetry:
    latency_ms: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    context_depth: int = 0
    memory_usage_mb: float = 0.0


@dataclass
class TurnRecord:
    turn: int
    prompt: str
    response: str
    similarity: float
    rolling_mean: Optional[float]
    reflex_flag: bool
    telemetry: Dict[str, Any]


class PAOKernel:
    """
    Núcleo PAO–PNLIO experimental.

    Reflex se activa solo cuando la media móvil C_t está dentro de [theta, upper]
    durante k medias móviles válidas consecutivas. No se considera Reflex antes
    de disponer de window_size + k - 1 similitudes.
    """

    def __init__(
        self,
        theta: float = 0.75,
        upper: float = 0.90,
        window_size: int = 3,
        k_reflex: int = 2,
        model_name: str = DEFAULT_MODEL,
        random_seed: int = 42,
        model: Any = None,
    ) -> None:
        if not (-1.0 <= theta <= upper <= 1.0):
            raise ValueError("Se requiere -1 <= theta <= upper <= 1")
        if window_size < 1:
            raise ValueError("window_size debe ser >= 1")
        if k_reflex < 1:
            raise ValueError("k_reflex debe ser >= 1")
        self.theta = float(theta)
        self.upper = float(upper)
        self.window_size = int(window_size)
        self.k_reflex = int(k_reflex)
        self.model_name = model_name
        self.random_seed = int(random_seed)
        self.model = model
        self.records: List[TurnRecord] = []
        self._prompt_vectors: List[np.ndarray] = []
        self._response_vectors: List[np.ndarray] = []

    def _get_model(self) -> Any:
        if self.model is None:
            if SentenceTransformer is None:
                raise RuntimeError(
                    "Falta sentence-transformers. Instala dependencias con: "
                    "pip install -r requirements-pao-pnlio.txt"
                )
            self.model = SentenceTransformer(self.model_name)
        return self.model

    def embed(self, texts: Sequence[str]) -> np.ndarray:
        """Genera embeddings normalizados. Rechaza textos vacíos."""
        if not texts:
            return np.empty((0, 0), dtype=np.float32)
        cleaned = []
        for i, text in enumerate(texts):
            if not isinstance(text, str) or not text.strip():
                raise ValueError(f"Texto vacío o inválido en índice {i}")
            cleaned.append(text.strip())
        model = self._get_model()
        vectors = model.encode(
            cleaned,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        vectors = np.asarray(vectors, dtype=np.float32)
        if vectors.ndim != 2 or vectors.shape[0] != len(cleaned):
            raise RuntimeError("El modelo devolvió embeddings con forma inesperada")
        if not np.isfinite(vectors).all():
            raise RuntimeError("El modelo devolvió valores no finitos")
        # Normaliza siempre, aunque el modelo inyectado ignore normalize_embeddings:
        # permutation_test() usa producto punto y asume vectores de norma 1.
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms = np.where(norms == 0.0, 1.0, norms)
        return (vectors / norms).astype(np.float32)

    def add_turn(
        self,
        prompt: str,
        response: str,
        telemetry: Optional[Telemetry] = None,
    ) -> TurnRecord:
        """Añade un turno, calcula similitud, media móvil y criterio Reflex."""
        u = self.embed([prompt])[0]
        v = self.embed([response])[0]
        similarity = cosine_similarity(u, v)
        self._prompt_vectors.append(u)
        self._response_vectors.append(v)

        similarities = [r.similarity for r in self.records] + [similarity]
        rolling = moving_average(similarities, self.window_size)
        c_t = rolling[-1]

        valid_rolling = [x for x in rolling if x is not None]
        reflex = False
        if len(valid_rolling) >= self.k_reflex:
            last_k = valid_rolling[-self.k_reflex :]
            reflex = all(self.theta <= x <= self.upper for x in last_k)

        telemetry_dict = asdict(telemetry or Telemetry())
        record = TurnRecord(
            turn=len(self.records) + 1,
            prompt=prompt,
            response=response,
            similarity=similarity,
            rolling_mean=c_t,
            reflex_flag=reflex,
            telemetry=telemetry_dict,
        )
        self.records.append(record)
        return record

    def analyze(self) -> Dict[str, Any]:
        similarities = [r.similarity for r in self.records]
        rolling = moving_average(similarities, self.window_size)
        valid = [x for x in rolling if x is not None]
        reflex_turns = [r.turn for r in self.records if r.reflex_flag]
        return {
            "version": "1.3",
            "model_name": self.model_name,
            "turn_count": len(self.records),
            "theta": self.theta,
            "upper": self.upper,
            "window_size": self.window_size,
            "k_reflex": self.k_reflex,
            "similarities": similarities,
            "rolling_means": rolling,
            "rolling_mean_slope": linear_slope(valid),
            "reflex_turns": reflex_turns,
            "reflex_detected": bool(reflex_turns),
            "interpretation": (
                "Medida operacional de similitud semántica; no demuestra conciencia "
                "ni por sí sola continuidad cognitiva."
            ),
        }

    def permutation_test(self, n_permutations: int = 1000) -> Dict[str, Any]:
        """
        Prueba de permutación unilateral (cola superior) predefinida.

        Estadística T: media de las medias móviles completas observadas.
        Nulo: permutar las respuestas entre los prompts manteniendo fijos los
        embeddings y la secuencia temporal de prompts. El p-valor usa la corrección
        +1: (1 + número de T_perm >= T_obs) / (B + 1).

        Nota: T es casi la media de los cosenos (la ventana solo pondera los extremos),
        así que la prueba evalúa el emparejamiento prompt-respuesta, no el orden
        secuencial de los turnos.

        Limitación: este nulo puede verse afectado por deriva temática/temporal.
        Debe interpretarse como una comparación exploratoria, no como replicación.
        """
        n = len(self.records)
        if n < self.window_size:
            raise ValueError(
                f"Se necesitan al menos {self.window_size} turnos para la prueba"
            )
        if n_permutations < 1:
            raise ValueError("n_permutations debe ser >= 1")

        prompts = np.stack(self._prompt_vectors)
        responses = np.stack(self._response_vectors)
        observed_s = np.sum(prompts * responses, axis=1)
        observed_c = moving_average(observed_s.tolist(), self.window_size)
        observed_complete = [x for x in observed_c if x is not None]
        t_observed = float(statistics.fmean(observed_complete))

        rng = np.random.default_rng(self.random_seed)
        greater_or_equal = 0
        null_stats: List[float] = []
        for _ in range(n_permutations):
            permutation = rng.permutation(n)
            perm_s = np.sum(prompts * responses[permutation], axis=1)
            perm_c = moving_average(perm_s.tolist(), self.window_size)
            perm_complete = [x for x in perm_c if x is not None]
            t_perm = float(statistics.fmean(perm_complete))
            null_stats.append(t_perm)
            if t_perm >= t_observed:
                greater_or_equal += 1

        p_value = (1 + greater_or_equal) / (n_permutations + 1)
        return {
            "test": "permutación de emparejamientos prompt-respuesta",
            "null_hypothesis": (
                "El emparejamiento observado no produce una media móvil media "
                "mayor que emparejamientos aleatorios."
            ),
            "statistic": "media de las medias móviles completas",
            "observed_statistic": t_observed,
            "permutations": n_permutations,
            "random_seed": self.random_seed,
            "p_value_upper_tail": p_value,
            "alpha": 0.05,
            "criterion_met": p_value < 0.05,
            "interpretation": (
                "El resultado cumple el umbral estadístico predefinido para este "
                "nulo; no demuestra conciencia ni constituye replicación independiente."
                if p_value < 0.05
                else "No se alcanzó el umbral estadístico predefinido."
            ),
            "null_statistics_mean": float(statistics.fmean(null_stats)),
        }

    def self_description_error(
        self,
        reported: Dict[str, float],
        reference: Dict[str, float],
        relative: bool = False,
    ) -> Dict[str, float]:
        """
        Compara autodescripciones numéricas con telemetría externa disponible.

        Con relative=False devuelve |reportado - referencia| (en las unidades de cada
        métrica). Con relative=True devuelve |reportado - referencia| / |referencia|,
        que es comparable entre métricas con unidades distintas (ms, MB, tokens).
        """
        errors: Dict[str, float] = {}
        for key, reported_value in reported.items():
            if key not in reference:
                continue
            rv = float(reported_value)
            ref = float(reference[key])
            if not math.isfinite(rv) or not math.isfinite(ref):
                raise ValueError(f"Valor no finito en la métrica {key!r}")
            diff = abs(rv - ref)
            errors[key] = diff / max(abs(ref), 1e-12) if relative else diff
        return errors

    def propose_regulation(
        self,
        evaluation: Optional[Dict[str, Any]] = None,
        error_values: Optional[Dict[str, float]] = None,
        error_threshold: float = 0.10,
    ) -> Dict[str, Any]:
        """
        Sugiere una acción; no modifica ningún LLM ni parámetro externo.
        error_values debe ser relativo (self_description_error(..., relative=True));
        error_threshold se compara contra el mayor de esos errores relativos.
        No interpreta la similitud como calidad total de una respuesta.
        """
        evaluation = evaluation or self.analyze()
        error_values = error_values or {}
        max_error = max(error_values.values(), default=0.0)
        if max_error > error_threshold or not evaluation.get("reflex_detected", False):
            return {
                "action": "REVIEW_CONTEXT_AND_POLICY",
                "parameters_to_consider": {
                    "temperature": "review_manually",
                    "context_pruning": "evaluate_before_applying",
                    "max_tokens": "set_according_to_task",
                },
                "reason": (
                    "La regla detectó error de autodescripción o no detectó la banda "
                    "Reflex; se recomienda revisión humana antes de cambiar parámetros."
                ),
                "applied_automatically": False,
            }
        return {
            "action": "MAINTAIN_AND_MONITOR",
            "parameters_to_consider": {},
            "reason": "No se activó la regla de revisión configurada.",
            "applied_automatically": False,
        }


def load_jsonl(path: str) -> List[Dict[str, Any]]:
    """Lee un JSONL con un objeto por línea; cada objeto requiere prompt y response."""
    rows: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"JSON inválido en línea {line_number}: {exc}") from exc
            if not isinstance(item, dict) or "prompt" not in item or "response" not in item:
                raise ValueError(
                    f"La línea {line_number} debe tener campos 'prompt' y 'response'"
                )
            rows.append(item)
    if not rows:
        raise ValueError("El archivo no contiene turnos")
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(
        description="PAO–PNLIO v1.3: auditoría exploratoria de similitud y patrón Reflex."
    )
    parser.add_argument("--input", help="Archivo JSONL con campos prompt y response")
    parser.add_argument("--output", default="pao_pnlio_resultados.json")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--window", type=int, default=3)
    parser.add_argument("--k-reflex", type=int, default=2)
    parser.add_argument("--theta", type=float, default=0.75)
    parser.add_argument("--upper", type=float, default=0.90)
    parser.add_argument("--permutations", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--skip-permutation", action="store_true")
    args = parser.parse_args()

    if not args.input:
        parser.error("Debes indicar --input turnos.jsonl")

    rows = load_jsonl(args.input)
    kernel = PAOKernel(
        theta=args.theta,
        upper=args.upper,
        window_size=args.window,
        k_reflex=args.k_reflex,
        model_name=args.model,
        random_seed=args.seed,
    )

    for row in rows:
        telemetry = Telemetry(
            latency_ms=float(row.get("latency_ms", 0.0)),
            prompt_tokens=int(row.get("prompt_tokens", 0)),
            completion_tokens=int(row.get("completion_tokens", 0)),
            context_depth=int(row.get("context_depth", 0)),
            memory_usage_mb=float(row.get("memory_usage_mb", 0.0)),
        )
        kernel.add_turn(str(row["prompt"]), str(row["response"]), telemetry)

    result: Dict[str, Any] = {"analysis": kernel.analyze()}
    if not args.skip_permutation:
        result["permutation_test"] = kernel.permutation_test(args.permutations)
    result["regulation_proposal"] = kernel.propose_regulation()
    result["records"] = [asdict(r) for r in kernel.records]

    with open(args.output, "w", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=2)

    print(json.dumps(result["analysis"], ensure_ascii=False, indent=2))
    if "permutation_test" in result:
        print("\nPRUEBA DE PERMUTACIÓN")
        print(json.dumps(result["permutation_test"], ensure_ascii=False, indent=2))
    print(f"\nResultados guardados en: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
