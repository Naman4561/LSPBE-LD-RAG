#!/usr/bin/env python3
"""Legacy diagnostic sweep for Bridge v2.1 components.

Use `scripts/run_qasper_final_model.py` for the locked final model and
`scripts/run_qasper_baseline_compare.py` for the main reproducible comparison.
"""
from __future__ import annotations

import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

def _repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "pyproject.toml").exists() and (parent / "src").exists():
            return parent
    raise RuntimeError("Could not locate repo root.")


ROOT = _repo_root()
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lspbe.expansion import (
    BridgeScoreDetail,
    BridgeV2ScoreDetail,
    BridgeV21ScoreDetail,
    adjacency_expand,
    bridge_expand_with_details,
    bridge_v2_expand_with_details,
    bridge_v21_expand_with_details,
    build_segment_idf,
)
from lspbe.mve import QAExample, _build_segments_by_doc, _evidence_hit, load_qasper_subset
from lspbe.retrieval import BGERetriever
from lspbe.types import DocumentSegment, RetrievedSegment

SUBSET_PATH = ROOT / "data" / "archive_debug" / "qasper_subset_debug_50.json"
MASTER_JSON = ROOT / "artifacts" / "mve_doc_constrained_50_bridge_v21_master_results.json"
MASTER_CSV = ROOT / "artifacts" / "mve_doc_constrained_50_bridge_v21_master_results.csv"
OUTCOMES_CSV = ROOT / "artifacts" / "mve_doc_constrained_50_bridge_v21_question_outcomes.csv"
SUMMARY_MD = ROOT / "artifacts" / "mve_doc_constrained_50_bridge_v21_summary.md"
EXAMPLES_MD = ROOT / "artifacts" / "mve_doc_constrained_50_bridge_v21_examples.md"


@dataclass(frozen=True)
class SweepConfig:
    name: str
    method: str
    k: int
    context_budget: int = 20
    radius: int = 1
    top_m: int = 2
    bridge_weights: tuple[float, float, float] = (1.0, 1.0, 0.5)
    bridge_v2_max_skip_distance: int = 2
    bridge_v2_top_per_seed: int = 1
    seed_retrieval_mode: str = "dense"
    seed_dense_weight: float = 1.0
    seed_sparse_weight: float = 0.0
    continuity_mode: str = "idf_overlap"
    bridge_trigger_mode: str = "always"
    bridge_trigger_threshold: float = 0.72
    local_rerank_mode: str = "none"
    diversify_final_context: bool = False
    diversity_weight: float = 0.15

    @property
    def config_id(self) -> str:
        return (
            f"{self.name}|method={self.method}|k={self.k}|context_budget={self.context_budget}|"
            f"seed_mode={self.seed_retrieval_mode}|dense_w={self.seed_dense_weight:.2f}|"
            f"sparse_w={self.seed_sparse_weight:.2f}|cont={self.continuity_mode}|"
            f"trigger={self.bridge_trigger_mode}:{self.bridge_trigger_threshold:.2f}|"
            f"rerank={self.local_rerank_mode}|diversify={int(self.diversify_final_context)}:{self.diversity_weight:.2f}"
        )


def question_type(question: str) -> str:
    first = question.strip().lower().split()
    if not first:
        return "other"
    token = first[0]
    return {
        "what": "what",
        "how": "how",
        "which": "which",
        "is": "boolean",
        "are": "boolean",
        "was": "boolean",
        "were": "boolean",
        "do": "boolean",
        "does": "boolean",
        "did": "boolean",
    }.get(token, "other")


def build_initial_configs() -> list[SweepConfig]:
    baseline = SweepConfig(
        name="bridge_v2_baseline",
        method="bridge_v2_baseline",
        k=10,
    )
    return [
        SweepConfig(name="adjacency_baseline", method="adjacency", k=8),
        SweepConfig(name="bridge_v1_baseline", method="bridge_v1_full", k=8, bridge_weights=(1.0, 1.0, 1.0)),
        baseline,
        SweepConfig(name="hybrid_soft", method="bridge_v21", k=10, seed_retrieval_mode="hybrid", seed_sparse_weight=0.5),
        SweepConfig(name="hybrid_equal", method="bridge_v21", k=10, seed_retrieval_mode="hybrid", seed_sparse_weight=1.0),
        SweepConfig(name="continuity_query_weighted", method="bridge_v21", k=10, continuity_mode="query_weighted_overlap"),
        SweepConfig(name="trigger_low_conf", method="bridge_v21", k=10, bridge_trigger_mode="low_confidence", bridge_trigger_threshold=0.72),
        SweepConfig(name="trigger_small_gap", method="bridge_v21", k=10, bridge_trigger_mode="small_gap", bridge_trigger_threshold=0.05),
        SweepConfig(name="rerank_only", method="bridge_v21", k=10, local_rerank_mode="lightweight"),
        SweepConfig(name="diversify_only", method="bridge_v21", k=10, diversify_final_context=True, diversity_weight=0.15),
        SweepConfig(
            name="rerank_plus_diversify",
            method="bridge_v21",
            k=10,
            local_rerank_mode="lightweight",
            diversify_final_context=True,
            diversity_weight=0.15,
        ),
    ]


def sparse_score_from_vector(query_vec: dict[str, float], doc_vec: dict[str, float]) -> float:
    return float(sum(weight * doc_vec.get(token, 0.0) for token, weight in query_vec.items()))


def build_rank_cache(
    retriever: BGERetriever,
    qas: list[QAExample],
    requests: set[tuple[int, str, float, float]],
) -> tuple[dict[tuple[int, tuple[int, str, float, float]], list[RetrievedSegment]], list[object]]:
    query_matrix = retriever.embedder.encode([qa.query for qa in qas])
    sparse_queries = [retriever.sparse_query_vector(qa.query) for qa in qas]
    cache: dict[tuple[int, tuple[int, str, float, float]], list[RetrievedSegment]] = {}
    for qa_index, qa in enumerate(qas):
        allowed_idx = retriever._doc_to_indices.get(qa.doc_id, [])
        if not allowed_idx:
            for request in requests:
                cache[(qa_index, request)] = []
            continue
        dense_scores = retriever._cosine_scores(
            query_matrix[qa_index],
            retriever._segment_matrix[allowed_idx],
        )
        sparse_scores = [
            sparse_score_from_vector(sparse_queries[qa_index], retriever._sparse_vectors[idx])
            for idx in allowed_idx
        ]
        sparse_scores_arr = np.asarray([float(score) for score in sparse_scores], dtype=np.float32)
        for request in requests:
            k, seed_mode, dense_weight, sparse_weight = request
            if seed_mode == "dense":
                final_scores = dense_scores
            elif seed_mode == "hybrid":
                final_scores = dense_weight * dense_scores + sparse_weight * sparse_scores_arr
            else:
                raise ValueError(f"Unsupported seed retrieval mode: {seed_mode}")
            top_local = list(sorted(range(len(allowed_idx)), key=lambda idx: float(final_scores[idx]), reverse=True)[:k])
            cache[(qa_index, request)] = [
                RetrievedSegment(segment=retriever.segments[allowed_idx[pos]], score=float(final_scores[pos]))
                for pos in top_local
            ]
    return cache, list(query_matrix)


def evidence_segment_ids(doc_segments: list[DocumentSegment], evidence_texts: list[str]) -> set[int]:
    ids: set[int] = set()
    for seg in doc_segments:
        lower = seg.text.lower()
        if any(ev.lower()[:80] in lower for ev in evidence_texts if ev):
            ids.add(seg.segment_id)
    return ids


def first_evidence_rank(retrieved: list[DocumentSegment], evidence_ids: set[int]) -> int | None:
    for rank, seg in enumerate(retrieved, start=1):
        if seg.segment_id in evidence_ids:
            return rank
    return None


def min_seed_distance(rank: list[RetrievedSegment], evidence_ids: set[int]) -> int | None:
    if not rank or not evidence_ids:
        return None
    best_seed = rank[0].segment.segment_id
    return min(abs(best_seed - evidence_id) for evidence_id in evidence_ids)


def distance_bucket(distance: int | None) -> str:
    if distance is None:
        return "unknown"
    if distance == 0:
        return "seed"
    if distance == 1:
        return "distance_1"
    if distance == 2:
        return "distance_2"
    return "distance_3_plus"


def segment_key_list(segments: list[DocumentSegment], allowed_keys: set[tuple[str, int]]) -> str:
    selected = [str(seg.segment_id) for seg in segments if (seg.doc_id, seg.segment_id) in allowed_keys]
    return ";".join(selected)


def detail_string(
    details: dict[tuple[str, int], BridgeV21ScoreDetail | BridgeV2ScoreDetail | BridgeScoreDetail],
) -> str:
    parts: list[str] = []
    for _, detail in sorted(details.items()):
        if isinstance(detail, BridgeV21ScoreDetail):
            parts.append(
                f"{detail.segment_id}@seed{detail.seed_segment_id}:bridge={detail.bridge_score:.3f},"
                f"query={detail.query_relevance:.3f},cont={detail.seed_continuity:.3f},"
                f"section={detail.section_similarity:.3f},q_overlap={detail.exact_query_overlap:.3f},"
                f"rerank={detail.rerank_score:.3f},dist={detail.distance}"
            )
        elif isinstance(detail, BridgeV2ScoreDetail):
            parts.append(
                f"{detail.segment_id}@seed{detail.seed_segment_id}:total={detail.total_score:.3f},"
                f"query={detail.query_relevance:.3f},cont={detail.seed_continuity:.3f},"
                f"section={detail.section_similarity:.3f},dist={detail.distance}"
            )
        else:
            parts.append(
                f"{detail.segment_id}@seed{detail.seed_segment_id}:total={detail.total_score:.3f},"
                f"adj={detail.adjacency:.3f},entity={detail.entity_overlap:.3f},section={detail.section_continuity:.3f}"
            )
    return " | ".join(parts)


def apply_config(
    config: SweepConfig,
    qa: QAExample,
    rank: list[RetrievedSegment],
    query_vector,
    segments_by_doc: dict[str, list[DocumentSegment]],
    segment_vectors: dict[tuple[str, int], object],
    idf_map: dict[str, float],
) -> tuple[list[DocumentSegment], dict[tuple[str, int], object], set[tuple[str, int]], set[tuple[str, int]], dict[str, object]]:
    if config.method == "adjacency":
        retrieved = adjacency_expand(rank, segments_by_doc, context_budget=config.context_budget)
        keys = {(seg.doc_id, seg.segment_id) for seg in retrieved}
        return retrieved, {}, keys, set(), {}

    if config.method == "bridge_v1_full":
        adjacency_segments = adjacency_expand(rank, segments_by_doc, context_budget=config.context_budget)
        adjacency_keys = {(seg.doc_id, seg.segment_id) for seg in adjacency_segments}
        retrieved, details = bridge_expand_with_details(
            rank,
            segments_by_doc,
            context_budget=config.context_budget,
            radius=config.radius,
            top_m=config.top_m,
            alpha=config.bridge_weights[0],
            beta=config.bridge_weights[1],
            gamma=config.bridge_weights[2],
        )
        retrieved_keys = {(seg.doc_id, seg.segment_id) for seg in retrieved}
        return retrieved, details, adjacency_keys & retrieved_keys, retrieved_keys - adjacency_keys, {}

    if config.method == "bridge_v2_baseline":
        retrieved, details, adjacency_keys, bridge_keys = bridge_v2_expand_with_details(
            rank,
            segments_by_doc,
            context_budget=config.context_budget,
            query_vector=query_vector,
            segment_vectors=segment_vectors,
            idf_map=idf_map,
            max_skip_distance=config.bridge_v2_max_skip_distance,
            top_per_seed=config.bridge_v2_top_per_seed,
            query_weight=config.bridge_weights[0],
            seed_weight=config.bridge_weights[1],
            section_weight=config.bridge_weights[2],
        )
        return retrieved, details, adjacency_keys, bridge_keys, {}

    if config.method == "bridge_v21":
        return bridge_v21_expand_with_details(
            rank,
            segments_by_doc,
            context_budget=config.context_budget,
            query=qa.query,
            query_vector=query_vector,
            segment_vectors=segment_vectors,
            idf_map=idf_map,
            max_skip_distance=config.bridge_v2_max_skip_distance,
            top_per_seed=config.bridge_v2_top_per_seed,
            query_weight=config.bridge_weights[0],
            seed_weight=config.bridge_weights[1],
            section_weight=config.bridge_weights[2],
            continuity_mode=config.continuity_mode,
            trigger_mode=config.bridge_trigger_mode,
            trigger_threshold=config.bridge_trigger_threshold,
            question_type=question_type(qa.query),
            local_rerank_mode=config.local_rerank_mode,
            diversify_final_context=config.diversify_final_context,
            diversity_weight=config.diversity_weight,
        )

    raise ValueError(f"Unsupported method: {config.method}")


def evaluate_config(
    config: SweepConfig,
    subset_path: Path,
    qas: list[QAExample],
    segments_by_doc: dict[str, list[DocumentSegment]],
    segment_vectors: dict[tuple[str, int], object],
    idf_map: dict[str, float],
    rank_cache: dict[tuple[int, tuple[int, str, float, float]], list[RetrievedSegment]],
    query_vectors: list[object],
    evidence_ids_by_qa: list[set[int]],
) -> tuple[dict[str, object], list[dict[str, object]], dict[int, dict[str, object]]]:
    hits = 0
    rr_sum = 0.0
    evidence_hits = 0
    seed_hits = 0
    outcomes: list[dict[str, object]] = []
    payloads: dict[int, dict[str, object]] = {}
    request_key = (config.k, config.seed_retrieval_mode, config.seed_dense_weight, config.seed_sparse_weight)

    for qa_index, qa in enumerate(qas):
        rank = rank_cache[(qa_index, request_key)]
        retrieved, details, adjacency_keys, bridge_keys, metadata = apply_config(
            config,
            qa,
            rank,
            query_vectors[qa_index],
            segments_by_doc,
            segment_vectors,
            idf_map,
        )
        hit = _evidence_hit(retrieved, qa.evidence_texts)
        if retrieved:
            hits += 1
            rr_sum += 1.0
        if hit:
            evidence_hits += 1
        evidence_ids = evidence_ids_by_qa[qa_index]
        distance = min_seed_distance(rank, evidence_ids)
        if distance == 0:
            seed_hits += 1
        first_rank = first_evidence_rank(retrieved, evidence_ids)
        payloads[qa_index] = {
            "retrieved": retrieved,
            "details": details,
            "adjacency_keys": adjacency_keys,
            "bridge_keys": bridge_keys,
            "metadata": metadata,
            "hit": hit,
        }
        outcomes.append(
            {
                "config_id": config.config_id,
                "paper_id": qa.doc_id,
                "question": qa.query,
                "question_type": question_type(qa.query),
                "method": config.method,
                "seed_retrieval_mode": config.seed_retrieval_mode,
                "seed_dense_weight": config.seed_dense_weight,
                "seed_sparse_weight": config.seed_sparse_weight,
                "continuity_mode": config.continuity_mode,
                "bridge_trigger_mode": config.bridge_trigger_mode,
                "bridge_trigger_threshold": config.bridge_trigger_threshold,
                "local_rerank_mode": config.local_rerank_mode,
                "diversify_final_context": int(config.diversify_final_context),
                "diversity_weight": config.diversity_weight,
                "k": config.k,
                "context_budget": config.context_budget,
                "hit": int(hit),
                "first_evidence_distance": distance_bucket(distance),
                "first_evidence_segment_rank": first_rank if first_rank is not None else "",
                "seed_segment_ids": ";".join(str(item.segment.segment_id) for item in rank),
                "adjacency_added_segments": segment_key_list(retrieved, adjacency_keys),
                "bridge_added_segments": segment_key_list(retrieved, bridge_keys),
                "bridge_component_scores": detail_string(details),
                "trigger_applied": int(bool(metadata.get("trigger_applied", True))),
                "trigger_reason": str(metadata.get("trigger_reason", "")),
                "improved_only_win": 0,
            }
        )

    total = max(len(qas), 1)
    row = {
        "subset_path": str(subset_path),
        "config_id": config.config_id,
        "name": config.name,
        "method": config.method,
        "seed_retrieval_mode": config.seed_retrieval_mode,
        "seed_dense_weight": config.seed_dense_weight,
        "seed_sparse_weight": config.seed_sparse_weight,
        "continuity_mode": config.continuity_mode,
        "bridge_trigger_mode": config.bridge_trigger_mode,
        "bridge_trigger_threshold": config.bridge_trigger_threshold,
        "local_rerank_mode": config.local_rerank_mode,
        "diversify_final_context": int(config.diversify_final_context),
        "diversity_weight": config.diversity_weight,
        "k": config.k,
        "radius": config.radius,
        "top_m": config.top_m,
        "bridge_v2_max_skip_distance": config.bridge_v2_max_skip_distance,
        "bridge_v2_top_per_seed": config.bridge_v2_top_per_seed,
        "context_budget": config.context_budget,
        "queries": float(len(qas)),
        "seed_hit_rate": seed_hits / total,
        "recall_at_k": hits / total,
        "mrr": rr_sum / total,
        "evidence_hit_rate": evidence_hits / total,
    }
    return row, outcomes, payloads


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def select_best(rows: list[dict[str, object]], predicate) -> dict[str, object]:
    candidates = [row for row in rows if predicate(row)]
    return sorted(
        candidates,
        key=lambda row: (-float(row["evidence_hit_rate"]), -float(row["seed_hit_rate"]), str(row["config_id"])),
    )[0]


def summarize_question_types(outcomes: list[dict[str, object]], config_id: str) -> list[str]:
    filtered = [row for row in outcomes if row["config_id"] == config_id]
    grouped: dict[str, list[int]] = {}
    for row in filtered:
        grouped.setdefault(str(row["question_type"]), []).append(int(row["hit"]))
    return [
        f"- `{qtype}`: {sum(values) / len(values):.3f} hit rate over {len(values)} questions"
        for qtype, values in sorted(grouped.items())
    ]


def build_follow_up_configs(rows: list[dict[str, object]]) -> list[SweepConfig]:
    best_hybrid = select_best(rows, lambda row: row["name"] in {"hybrid_soft", "hybrid_equal"})
    best_trigger = select_best(rows, lambda row: row["name"] in {"trigger_low_conf", "trigger_small_gap"})
    best_continuity = select_best(rows, lambda row: row["name"] in {"bridge_v2_baseline", "continuity_query_weighted"})

    return [
        SweepConfig(
            name="tier1_combo",
            method="bridge_v21",
            k=10,
            seed_retrieval_mode=str(best_hybrid["seed_retrieval_mode"]),
            seed_dense_weight=float(best_hybrid["seed_dense_weight"]),
            seed_sparse_weight=float(best_hybrid["seed_sparse_weight"]),
            continuity_mode=str(best_continuity["continuity_mode"]),
            bridge_trigger_mode=str(best_trigger["bridge_trigger_mode"]),
            bridge_trigger_threshold=float(best_trigger["bridge_trigger_threshold"]),
        ),
        SweepConfig(
            name="tier1_plus_rerank",
            method="bridge_v21",
            k=10,
            seed_retrieval_mode=str(best_hybrid["seed_retrieval_mode"]),
            seed_dense_weight=float(best_hybrid["seed_dense_weight"]),
            seed_sparse_weight=float(best_hybrid["seed_sparse_weight"]),
            continuity_mode=str(best_continuity["continuity_mode"]),
            bridge_trigger_mode=str(best_trigger["bridge_trigger_mode"]),
            bridge_trigger_threshold=float(best_trigger["bridge_trigger_threshold"]),
            local_rerank_mode="lightweight",
        ),
        SweepConfig(
            name="tier1_plus_diversify",
            method="bridge_v21",
            k=10,
            seed_retrieval_mode=str(best_hybrid["seed_retrieval_mode"]),
            seed_dense_weight=float(best_hybrid["seed_dense_weight"]),
            seed_sparse_weight=float(best_hybrid["seed_sparse_weight"]),
            continuity_mode=str(best_continuity["continuity_mode"]),
            bridge_trigger_mode=str(best_trigger["bridge_trigger_mode"]),
            bridge_trigger_threshold=float(best_trigger["bridge_trigger_threshold"]),
            diversify_final_context=True,
            diversity_weight=0.15,
        ),
        SweepConfig(
            name="full_upgraded_pipeline",
            method="bridge_v21",
            k=10,
            seed_retrieval_mode=str(best_hybrid["seed_retrieval_mode"]),
            seed_dense_weight=float(best_hybrid["seed_dense_weight"]),
            seed_sparse_weight=float(best_hybrid["seed_sparse_weight"]),
            continuity_mode=str(best_continuity["continuity_mode"]),
            bridge_trigger_mode=str(best_trigger["bridge_trigger_mode"]),
            bridge_trigger_threshold=float(best_trigger["bridge_trigger_threshold"]),
            local_rerank_mode="lightweight",
            diversify_final_context=True,
            diversity_weight=0.15,
        ),
    ]


def beyond_indices_from_baseline(outcomes_by_config: dict[str, list[dict[str, object]]], baseline_config_id: str) -> set[int]:
    return {
        index
        for index, row in enumerate(outcomes_by_config[baseline_config_id])
        if row["first_evidence_distance"] in {"distance_2", "distance_3_plus"}
    }


def slice_hit_rate(outcomes: list[dict[str, object]], indices: set[int]) -> float:
    if not indices:
        return 0.0
    hits = sum(int(outcomes[index]["hit"]) for index in indices)
    return hits / len(indices)


def method_block(title: str, payload: dict[str, object], method: str) -> list[str]:
    lines = [f"### {title}"]
    lines.append(f"- trigger: `{payload['metadata'].get('trigger_reason', 'n/a')}`")
    for seg in payload["retrieved"]:
        lines.append(f"- section: `{seg.section}`")
        lines.append(f"- segment_id: `{seg.segment_id}`")
        lines.append(f"- text: {seg.text.replace(chr(10), ' ').strip()}")
        detail = payload["details"].get((seg.doc_id, seg.segment_id))
        if detail is None:
            lines.append("- score_detail: seed or adjacency segment")
        elif isinstance(detail, BridgeV21ScoreDetail):
            lines.append(
                "- score_detail: "
                f"seed=`{detail.seed_segment_id}`, bridge=`{detail.bridge_score:.3f}`, "
                f"query=`{detail.query_relevance:.3f}`, continuity=`{detail.seed_continuity:.3f}`, "
                f"section=`{detail.section_similarity:.3f}`, query_overlap=`{detail.exact_query_overlap:.3f}`, "
                f"rerank=`{detail.rerank_score:.3f}`, distance=`{detail.distance}`"
            )
        elif isinstance(detail, BridgeV2ScoreDetail):
            lines.append(
                "- score_detail: "
                f"seed=`{detail.seed_segment_id}`, total=`{detail.total_score:.3f}`, "
                f"query=`{detail.query_relevance:.3f}`, continuity=`{detail.seed_continuity:.3f}`, "
                f"section=`{detail.section_similarity:.3f}`, distance=`{detail.distance}`"
            )
        else:
            lines.append(
                "- score_detail: "
                f"seed=`{detail.seed_segment_id}`, total=`{detail.total_score:.3f}`, "
                f"adjacency=`{detail.adjacency:.3f}`, entity=`{detail.entity_overlap:.3f}`, "
                f"section=`{detail.section_continuity:.3f}`"
            )
        lines.append("")
    return lines


def build_examples(
    qas: list[QAExample],
    best_baseline: dict[str, object],
    best_upgraded: dict[str, object],
    rerank_component: dict[str, object],
    diversify_component: dict[str, object],
    payloads: dict[str, dict[int, dict[str, object]]],
) -> str:
    baseline_id = str(best_baseline["config_id"])
    improved_id = str(best_upgraded["config_id"])
    rerank_id = str(rerank_component["config_id"])
    diversify_id = str(diversify_component["config_id"])
    categories = {
        "Improved Pipeline Win Over Current Bridge v2": lambda idx: payloads[improved_id][idx]["hit"] and not payloads[baseline_id][idx]["hit"],
        "Current Bridge v2 Win Over Improved Pipeline": lambda idx: payloads[baseline_id][idx]["hit"] and not payloads[improved_id][idx]["hit"],
        "Tie": lambda idx: payloads[baseline_id][idx]["hit"] and payloads[improved_id][idx]["hit"],
        "Failure Case": lambda idx: (not payloads[baseline_id][idx]["hit"]) and (not payloads[improved_id][idx]["hit"]),
        "Reranking Clearly Helps": lambda idx: payloads[rerank_id][idx]["hit"] and not payloads[baseline_id][idx]["hit"],
        "Diversification Clearly Helps": lambda idx: payloads[diversify_id][idx]["hit"] and not payloads[baseline_id][idx]["hit"],
    }

    lines = [
        "# Bridge v2.1 Qualitative Examples",
        "",
        f"Current Bridge v2 baseline: `{baseline_id}`",
        f"Best upgraded pipeline: `{improved_id}`",
        f"Rerank component example config: `{rerank_id}`",
        f"Diversify component example config: `{diversify_id}`",
        "",
    ]

    for title, predicate in categories.items():
        lines.append(f"## {title}")
        lines.append("")
        idx = next((i for i in range(len(qas)) if predicate(i)), None)
        if idx is None:
            lines.append("No example found for this category.")
            lines.append("")
            continue
        qa = qas[idx]
        lines.append(f"- paper_id: `{qa.doc_id}`")
        lines.append(f"- question: {qa.query}")
        lines.append("- gold evidence:")
        for evidence in qa.evidence_texts:
            lines.append(f"  - {evidence}")
        lines.append("")
        lines.extend(method_block("Current Bridge v2", payloads[baseline_id][idx], "bridge_v2"))
        lines.extend(method_block("Best Upgraded Pipeline", payloads[improved_id][idx], "bridge_v21"))
        if title == "Reranking Clearly Helps":
            lines.extend(method_block("Best Rerank Config", payloads[rerank_id][idx], "bridge_v21"))
        if title == "Diversification Clearly Helps":
            lines.extend(method_block("Best Diversify Config", payloads[diversify_id][idx], "bridge_v21"))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_summary(
    rows: list[dict[str, object]],
    outcomes: list[dict[str, object]],
    best_adjacency: dict[str, object],
    best_bridge_v1: dict[str, object],
    best_bridge_v2: dict[str, object],
    best_upgraded: dict[str, object],
    beyond_indices: set[int],
) -> str:
    outcomes_by_config: dict[str, list[dict[str, object]]] = {}
    for row in outcomes:
        outcomes_by_config.setdefault(str(row["config_id"]), []).append(row)

    best_overall_v21 = select_best(rows, lambda row: row["method"] == "bridge_v21")
    best_hybrid = select_best(rows, lambda row: row["name"] in {"hybrid_soft", "hybrid_equal"})
    best_continuity = select_best(rows, lambda row: row["name"] in {"bridge_v2_baseline", "continuity_query_weighted"})
    best_trigger = select_best(rows, lambda row: row["name"] in {"trigger_low_conf", "trigger_small_gap"})
    rerank_component = select_best(rows, lambda row: row["name"] == "rerank_only")
    diversify_component = select_best(rows, lambda row: row["name"] == "diversify_only")

    lines = [
        "# Bridge v2.1 Summary",
        "",
        "## Best Configs",
        "",
        f"- best adjacency: `{best_adjacency['config_id']}` with evidence_hit_rate `{best_adjacency['evidence_hit_rate']:.4f}`",
        f"- best bridge v1: `{best_bridge_v1['config_id']}` with evidence_hit_rate `{best_bridge_v1['evidence_hit_rate']:.4f}`",
        f"- best current Bridge v2: `{best_bridge_v2['config_id']}` with evidence_hit_rate `{best_bridge_v2['evidence_hit_rate']:.4f}`",
        f"- best overall Bridge v2.1 variant: `{best_overall_v21['config_id']}` with evidence_hit_rate `{best_overall_v21['evidence_hit_rate']:.4f}`",
        f"- best upgraded pipeline: `{best_upgraded['config_id']}` with evidence_hit_rate `{best_upgraded['evidence_hit_rate']:.4f}`",
        "",
        "## Component Answers",
        "",
        f"1. does hybrid retrieval improve seed quality? {'yes' if float(best_hybrid['seed_hit_rate']) > float(best_bridge_v2['seed_hit_rate']) else 'no'}",
        f"2. does stronger continuity help? {'yes' if float(best_continuity['evidence_hit_rate']) > float(best_bridge_v2['evidence_hit_rate']) else 'no'}",
        f"3. does adaptive triggering help? {'yes' if float(best_trigger['evidence_hit_rate']) > float(best_bridge_v2['evidence_hit_rate']) else 'no'}",
        "4. does local reranking help? "
        + ("yes, but only in combination" if float(best_upgraded['evidence_hit_rate']) > float(best_bridge_v2['evidence_hit_rate']) and float(rerank_component['evidence_hit_rate']) <= float(best_bridge_v2['evidence_hit_rate']) else ("yes" if float(rerank_component['evidence_hit_rate']) > float(best_bridge_v2['evidence_hit_rate']) else "no")),
        f"5. does diversification help? {'yes' if float(diversify_component['evidence_hit_rate']) > float(best_bridge_v2['evidence_hit_rate']) else 'no'}",
        f"6. what is the best full upgraded pipeline? `{best_upgraded['config_id']}`",
        f"7. how much does it beat current Bridge v2? `{float(best_upgraded['evidence_hit_rate']) - float(best_bridge_v2['evidence_hit_rate']):.4f}` evidence_hit_rate",
        f"8. does it improve the beyond-adjacency subset? {'yes' if slice_hit_rate(outcomes_by_config[str(best_upgraded['config_id'])], beyond_indices) > slice_hit_rate(outcomes_by_config[str(best_bridge_v2['config_id'])], beyond_indices) else 'no'}",
        "",
        "## Beyond-Adjacency Subset",
        "",
        f"- subset size: `{len(beyond_indices)}` questions",
        f"- current Bridge v2 hit rate: `{slice_hit_rate(outcomes_by_config[str(best_bridge_v2['config_id'])], beyond_indices):.4f}`",
        f"- best overall Bridge v2.1 hit rate: `{slice_hit_rate(outcomes_by_config[str(best_overall_v21['config_id'])], beyond_indices):.4f}`",
        f"- best upgraded pipeline hit rate: `{slice_hit_rate(outcomes_by_config[str(best_upgraded['config_id'])], beyond_indices):.4f}`",
        "",
        "## What Helped Most",
        "",
        f"- best hybrid-only config: `{best_hybrid['config_id']}` with overall `{best_hybrid['evidence_hit_rate']:.4f}` and seed hit `{best_hybrid['seed_hit_rate']:.4f}`",
        f"- best continuity-only config: `{best_continuity['config_id']}` with overall `{best_continuity['evidence_hit_rate']:.4f}`",
        f"- best trigger-only config: `{best_trigger['config_id']}` with overall `{best_trigger['evidence_hit_rate']:.4f}`",
        f"- rerank-only config: `{rerank_component['config_id']}` with overall `{rerank_component['evidence_hit_rate']:.4f}`",
        f"- diversify-only config: `{diversify_component['config_id']}` with overall `{diversify_component['evidence_hit_rate']:.4f}`",
        "",
        "## Question-Type Slices",
        "",
        f"- current Bridge v2 for `{best_bridge_v2['config_id']}`:",
    ]
    lines.extend(summarize_question_types(outcomes, str(best_bridge_v2["config_id"])))
    lines.append(f"- best upgraded pipeline for `{best_upgraded['config_id']}`:")
    lines.extend(summarize_question_types(outcomes, str(best_upgraded["config_id"])))
    lines.extend(
        [
            "",
            "## Final Interpretation",
            "",
            "- Tier 1 is about putting better seeds and better bridge triggers into the same skip-local bridge design.",
            "- Tier 2 is about ordering and selecting that local pool more intelligently without adding a heavy reranker.",
            f"- The strongest single v2.1 change was `{best_overall_v21['name']}` at `{best_overall_v21['evidence_hit_rate']:.4f}`.",
            f"- Current Bridge v2 reaches `{best_bridge_v2['evidence_hit_rate']:.4f}`; the best upgraded pipeline reaches `{best_upgraded['evidence_hit_rate']:.4f}`.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    segments, qas = load_qasper_subset(SUBSET_PATH, max_papers=50, max_qas=10_000)
    retriever = BGERetriever(segments)
    segments_by_doc = _build_segments_by_doc(segments)
    idf_map = build_segment_idf(segments)
    segment_vectors = {
        (segment.doc_id, segment.segment_id): retriever._segment_matrix[index]
        for index, segment in enumerate(segments)
    }
    evidence_ids_by_qa = [
        evidence_segment_ids(segments_by_doc.get(qa.doc_id, []), qa.evidence_texts)
        for qa in qas
    ]

    configs = build_initial_configs()
    requests = {
        (config.k, config.seed_retrieval_mode, config.seed_dense_weight, config.seed_sparse_weight)
        for config in configs
    }
    rank_cache, query_vectors = build_rank_cache(retriever, qas, requests)

    rows: list[dict[str, object]] = []
    outcomes: list[dict[str, object]] = []
    payloads: dict[str, dict[int, dict[str, object]]] = {}
    for config in configs:
        row, outcome_rows, config_payloads = evaluate_config(
            config,
            subset_path=SUBSET_PATH,
            qas=qas,
            segments_by_doc=segments_by_doc,
            segment_vectors=segment_vectors,
            idf_map=idf_map,
            rank_cache=rank_cache,
            query_vectors=query_vectors,
            evidence_ids_by_qa=evidence_ids_by_qa,
        )
        rows.append(row)
        outcomes.extend(outcome_rows)
        payloads[config.config_id] = config_payloads

    follow_up = build_follow_up_configs(rows)
    new_requests = {
        (config.k, config.seed_retrieval_mode, config.seed_dense_weight, config.seed_sparse_weight)
        for config in follow_up
    }
    missing_requests = new_requests - set(rank_cache_key for _, rank_cache_key in rank_cache.keys())
    if missing_requests:
        extra_cache, _ = build_rank_cache(retriever, qas, missing_requests)
        rank_cache.update(extra_cache)

    seen = {row["config_id"] for row in rows}
    for config in follow_up:
        if config.config_id in seen:
            continue
        row, outcome_rows, config_payloads = evaluate_config(
            config,
            subset_path=SUBSET_PATH,
            qas=qas,
            segments_by_doc=segments_by_doc,
            segment_vectors=segment_vectors,
            idf_map=idf_map,
            rank_cache=rank_cache,
            query_vectors=query_vectors,
            evidence_ids_by_qa=evidence_ids_by_qa,
        )
        rows.append(row)
        outcomes.extend(outcome_rows)
        payloads[config.config_id] = config_payloads

    rows_sorted = sorted(rows, key=lambda row: str(row["config_id"]))
    outcomes_by_config: dict[str, list[dict[str, object]]] = {}
    for row in outcomes:
        outcomes_by_config.setdefault(str(row["config_id"]), []).append(row)

    best_adjacency = select_best(rows_sorted, lambda row: row["name"] == "adjacency_baseline")
    best_bridge_v1 = select_best(rows_sorted, lambda row: row["name"] == "bridge_v1_baseline")
    best_bridge_v2 = select_best(rows_sorted, lambda row: row["name"] == "bridge_v2_baseline")
    best_upgraded = select_best(
        rows_sorted,
        lambda row: row["method"] == "bridge_v21" and row["name"] not in {"hybrid_soft", "hybrid_equal", "continuity_query_weighted", "trigger_low_conf", "trigger_small_gap", "rerank_only", "diversify_only"},
    )
    rerank_component = select_best(rows_sorted, lambda row: row["name"] == "rerank_only")
    diversify_component = select_best(rows_sorted, lambda row: row["name"] == "diversify_only")
    beyond_indices = beyond_indices_from_baseline(outcomes_by_config, str(best_bridge_v2["config_id"]))

    baseline_hits = outcomes_by_config[str(best_bridge_v2["config_id"])]
    for config_id, config_outcomes in outcomes_by_config.items():
        for idx, row in enumerate(config_outcomes):
            row["improved_only_win"] = int(int(row["hit"]) == 1 and int(baseline_hits[idx]["hit"]) == 0)

    outcomes_sorted = sorted(
        [row for rows_for_config in outcomes_by_config.values() for row in rows_for_config],
        key=lambda row: (str(row["config_id"]), str(row["paper_id"]), str(row["question"])),
    )

    write_json(MASTER_JSON, {"subset_path": str(SUBSET_PATH), "results": rows_sorted})
    write_csv(MASTER_CSV, rows_sorted)
    write_csv(OUTCOMES_CSV, outcomes_sorted)
    SUMMARY_MD.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_MD.write_text(
        build_summary(rows_sorted, outcomes_sorted, best_adjacency, best_bridge_v1, best_bridge_v2, best_upgraded, beyond_indices),
        encoding="utf-8",
    )
    EXAMPLES_MD.parent.mkdir(parents=True, exist_ok=True)
    EXAMPLES_MD.write_text(
        build_examples(qas, best_bridge_v2, best_upgraded, rerank_component, diversify_component, payloads),
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "best_adjacency": best_adjacency,
                "best_bridge_v1": best_bridge_v1,
                "best_bridge_v2_baseline": best_bridge_v2,
                "best_upgraded_pipeline": best_upgraded,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


