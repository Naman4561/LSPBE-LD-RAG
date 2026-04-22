#!/usr/bin/env python3
"""Diagnostic section/diversification study behind the locked final model.

Use `scripts/run_qasper_final_model.py` for the clean default evaluation path.
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
MASTER_JSON = ROOT / "artifacts" / "mve_doc_constrained_50_streamlined_master_results.json"
MASTER_CSV = ROOT / "artifacts" / "mve_doc_constrained_50_streamlined_master_results.csv"
OUTCOMES_CSV = ROOT / "artifacts" / "mve_doc_constrained_50_streamlined_question_outcomes.csv"
SUMMARY_MD = ROOT / "artifacts" / "mve_doc_constrained_50_streamlined_summary.md"
EXAMPLES_MD = ROOT / "artifacts" / "mve_doc_constrained_50_streamlined_examples.md"


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
    section_mode: str = "current"
    diversify_final_context: bool = False
    diversity_weight: float = 0.15

    @property
    def config_id(self) -> str:
        return (
            f"{self.name}|method={self.method}|k={self.k}|seed_mode={self.seed_retrieval_mode}|"
            f"dense_w={self.seed_dense_weight:.2f}|sparse_w={self.seed_sparse_weight:.2f}|"
            f"section={self.section_mode}|diversify={int(self.diversify_final_context)}:{self.diversity_weight:.2f}"
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


def build_configs() -> list[SweepConfig]:
    configs = [
        SweepConfig(name="adjacency_baseline", method="adjacency", k=8),
        SweepConfig(name="bridge_v1_baseline", method="bridge_v1_full", k=8, bridge_weights=(1.0, 1.0, 1.0)),
        SweepConfig(name="bridge_v2_baseline", method="bridge_v2_baseline", k=10),
        SweepConfig(
            name="bridge_v21_hybrid_soft",
            method="bridge_v21_streamlined",
            k=10,
            seed_retrieval_mode="hybrid",
            seed_sparse_weight=0.5,
            section_mode="current",
        ),
    ]
    for section_mode in ["none", "current", "improved"]:
        configs.append(
            SweepConfig(
                name=f"bridge_v21_streamlined_{section_mode}",
                method="bridge_v21_streamlined",
                k=10,
                seed_retrieval_mode="hybrid",
                seed_sparse_weight=0.5,
                section_mode=section_mode,
            )
        )
        configs.append(
            SweepConfig(
                name=f"bridge_v21_streamlined_{section_mode}_diverse",
                method="bridge_v21_streamlined",
                k=10,
                seed_retrieval_mode="hybrid",
                seed_sparse_weight=0.5,
                section_mode=section_mode,
                diversify_final_context=True,
                diversity_weight=0.15,
            )
        )
    return configs


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
        dense_scores = retriever._cosine_scores(query_matrix[qa_index], retriever._segment_matrix[allowed_idx])
        sparse_scores = np.asarray(
            [sparse_score_from_vector(sparse_queries[qa_index], retriever._sparse_vectors[idx]) for idx in allowed_idx],
            dtype=np.float32,
        )
        for request in requests:
            k, seed_mode, dense_weight, sparse_weight = request
            if seed_mode == "dense":
                final_scores = dense_scores
            elif seed_mode == "hybrid":
                final_scores = dense_weight * dense_scores + sparse_weight * sparse_scores
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


def detail_string(details: dict[tuple[str, int], object]) -> str:
    parts: list[str] = []
    for _, detail in sorted(details.items()):
        if isinstance(detail, BridgeV21ScoreDetail):
            parts.append(
                f"{detail.segment_id}@seed{detail.seed_segment_id}:bridge={detail.bridge_score:.3f},"
                f"query={detail.query_relevance:.3f},cont={detail.seed_continuity:.3f},"
                f"section={detail.section_similarity:.3f},dist={detail.distance}"
            )
        elif isinstance(detail, BridgeV2ScoreDetail):
            parts.append(
                f"{detail.segment_id}@seed{detail.seed_segment_id}:total={detail.total_score:.3f},"
                f"query={detail.query_relevance:.3f},cont={detail.seed_continuity:.3f},"
                f"section={detail.section_similarity:.3f},dist={detail.distance}"
            )
        elif isinstance(detail, BridgeScoreDetail):
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
    if config.method == "bridge_v21_streamlined":
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
            trigger_mode="always",
            local_rerank_mode="none",
            diversify_final_context=config.diversify_final_context,
            diversity_weight=config.diversity_weight,
            section_mode=config.section_mode,
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
                "name": config.name,
                "method": config.method,
                "seed_retrieval_mode": config.seed_retrieval_mode,
                "section_mode": config.section_mode,
                "diversify_final_context": int(config.diversify_final_context),
                "k": config.k,
                "hit": int(hit),
                "first_evidence_distance": distance_bucket(distance),
                "first_evidence_segment_rank": first_rank if first_rank is not None else "",
                "seed_segment_ids": ";".join(str(item.segment.segment_id) for item in rank),
                "adjacency_added_segments": segment_key_list(retrieved, adjacency_keys),
                "bridge_added_segments": segment_key_list(retrieved, bridge_keys),
                "bridge_component_scores": detail_string(details),
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
        "section_mode": config.section_mode,
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


def slice_hit_rate(outcomes: list[dict[str, object]], indices: set[int]) -> float:
    if not indices:
        return 0.0
    hits = sum(int(outcomes[index]["hit"]) for index in indices)
    return hits / len(indices)


def summarize_question_types(outcomes: list[dict[str, object]], config_id: str) -> list[str]:
    filtered = [row for row in outcomes if row["config_id"] == config_id]
    grouped: dict[str, list[int]] = {}
    for row in filtered:
        grouped.setdefault(str(row["question_type"]), []).append(int(row["hit"]))
    return [
        f"- `{qtype}`: {sum(values) / len(values):.3f} hit rate over {len(values)} questions"
        for qtype, values in sorted(grouped.items())
    ]


def build_examples(
    qas: list[QAExample],
    improved_cfg: dict[str, object],
    current_cfg: dict[str, object],
    none_cfg: dict[str, object],
    best_streamlined: dict[str, object],
    diverse_variant: dict[str, object],
    baseline_cfg: dict[str, object],
    payloads: dict[str, dict[int, dict[str, object]]],
) -> str:
    improved_id = str(improved_cfg["config_id"])
    current_id = str(current_cfg["config_id"])
    none_id = str(none_cfg["config_id"])
    best_id = str(best_streamlined["config_id"])
    diverse_id = str(diverse_variant["config_id"])
    baseline_id = str(baseline_cfg["config_id"])
    categories = {
        "Improved Section Helps": lambda idx: payloads[improved_id][idx]["hit"] and not payloads[current_id][idx]["hit"],
        "No-Section Helps": lambda idx: payloads[none_id][idx]["hit"] and not payloads[current_id][idx]["hit"],
        "Current and Improved Tie": lambda idx: payloads[current_id][idx]["hit"] and payloads[improved_id][idx]["hit"],
        "Diversification Helps": lambda idx: payloads[diverse_id][idx]["hit"] and not payloads[best_id][idx]["hit"],
        "Failure Case": lambda idx: (not payloads[best_id][idx]["hit"]) and (not payloads[baseline_id][idx]["hit"]),
    }

    def block(title: str, payload: dict[str, object]) -> list[str]:
        lines = [f"### {title}"]
        lines.append(f"- section_mode: `{payload['metadata'].get('section_mode', 'n/a')}`")
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
                    f"section=`{detail.section_similarity:.3f}`, distance=`{detail.distance}`"
                )
            else:
                lines.append("- score_detail: bridge detail available")
            lines.append("")
        return lines

    lines = [
        "# Streamlined Bridge Qualitative Examples",
        "",
        f"Current-section streamlined config: `{current_id}`",
        f"Improved-section streamlined config: `{improved_id}`",
        f"No-section streamlined config: `{none_id}`",
        f"Best streamlined config: `{best_id}`",
        f"Diversified comparison config: `{diverse_id}`",
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
        if title == "Improved Section Helps":
            lines.extend(block("Current Section", payloads[current_id][idx]))
            lines.extend(block("Improved Section", payloads[improved_id][idx]))
        elif title == "No-Section Helps":
            lines.extend(block("Current Section", payloads[current_id][idx]))
            lines.extend(block("No Section", payloads[none_id][idx]))
        elif title == "Current and Improved Tie":
            lines.extend(block("Current Section", payloads[current_id][idx]))
            lines.extend(block("Improved Section", payloads[improved_id][idx]))
        elif title == "Diversification Helps":
            lines.extend(block("Best Streamlined Without Diversification", payloads[best_id][idx]))
            lines.extend(block("Diversified Variant", payloads[diverse_id][idx]))
        else:
            lines.extend(block("Current Bridge v2 Baseline", payloads[baseline_id][idx]))
            lines.extend(block("Best Streamlined", payloads[best_id][idx]))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_summary(
    rows: list[dict[str, object]],
    outcomes: list[dict[str, object]],
    best_adjacency: dict[str, object],
    best_bridge_v1: dict[str, object],
    best_bridge_v2: dict[str, object],
    best_hybrid_soft: dict[str, object],
    best_streamlined: dict[str, object],
    best_streamlined_diverse: dict[str, object],
    beyond_indices: set[int],
) -> str:
    outcomes_by_config: dict[str, list[dict[str, object]]] = {}
    for row in outcomes:
        outcomes_by_config.setdefault(str(row["config_id"]), []).append(row)

    lines = [
        "# Streamlined Bridge Summary",
        "",
        "## Best Configs",
        "",
        f"- adjacency baseline: `{best_adjacency['config_id']}` with evidence_hit_rate `{best_adjacency['evidence_hit_rate']:.4f}`",
        f"- bridge v1 baseline: `{best_bridge_v1['config_id']}` with evidence_hit_rate `{best_bridge_v1['evidence_hit_rate']:.4f}`",
        f"- current Bridge v2 baseline: `{best_bridge_v2['config_id']}` with evidence_hit_rate `{best_bridge_v2['evidence_hit_rate']:.4f}`",
        f"- best v2.1 hybrid_soft baseline: `{best_hybrid_soft['config_id']}` with evidence_hit_rate `{best_hybrid_soft['evidence_hit_rate']:.4f}`",
        f"- best streamlined model: `{best_streamlined['config_id']}` with evidence_hit_rate `{best_streamlined['evidence_hit_rate']:.4f}`",
        "",
        "## Answers",
        "",
        f"1. what should be the final streamlined default model? `{best_streamlined['config_id']}`",
        "2. should section structure be removed, kept, or improved? "
        + (
            "improved"
            if str(best_streamlined["section_mode"]) == "improved"
            else ("removed" if str(best_streamlined["section_mode"]) == "none" else "kept as-is")
        ),
        f"3. is diversification worth keeping? {'yes' if float(best_streamlined_diverse['evidence_hit_rate']) > float(best_streamlined['evidence_hit_rate']) else 'no'}",
        f"4. best streamlined vs adjacency: `{float(best_streamlined['evidence_hit_rate']) - float(best_adjacency['evidence_hit_rate']):.4f}`",
        f"5. best streamlined vs bridge v1: `{float(best_streamlined['evidence_hit_rate']) - float(best_bridge_v1['evidence_hit_rate']):.4f}`",
        f"6. best streamlined vs current Bridge v2 baseline: `{float(best_streamlined['evidence_hit_rate']) - float(best_bridge_v2['evidence_hit_rate']):.4f}`",
        f"7. best streamlined vs best v2.1 hybrid_soft baseline: `{float(best_streamlined['evidence_hit_rate']) - float(best_hybrid_soft['evidence_hit_rate']):.4f}`",
        "",
        "## Section Study",
        "",
    ]
    for section_mode in ["none", "current", "improved"]:
        best_for_mode = select_best(rows, lambda row, mode=section_mode: row["method"] == "bridge_v21_streamlined" and row["section_mode"] == mode)
        lines.append(
            f"- `{section_mode}`: overall `{best_for_mode['evidence_hit_rate']:.4f}`, beyond-adjacency `{slice_hit_rate(outcomes_by_config[str(best_for_mode['config_id'])], beyond_indices):.4f}`"
        )
    lines.extend(
        [
            "",
            "## Diversification Check",
            "",
            f"- best no-diversification streamlined config: `{best_streamlined['config_id']}` with `{best_streamlined['evidence_hit_rate']:.4f}`",
            f"- best diversified streamlined config: `{best_streamlined_diverse['config_id']}` with `{best_streamlined_diverse['evidence_hit_rate']:.4f}`",
            "",
            "## Beyond-Adjacency Subset",
            "",
            f"- subset size: `{len(beyond_indices)}` questions",
            f"- current Bridge v2 baseline: `{slice_hit_rate(outcomes_by_config[str(best_bridge_v2['config_id'])], beyond_indices):.4f}`",
            f"- best v2.1 hybrid_soft baseline: `{slice_hit_rate(outcomes_by_config[str(best_hybrid_soft['config_id'])], beyond_indices):.4f}`",
            f"- best streamlined: `{slice_hit_rate(outcomes_by_config[str(best_streamlined['config_id'])], beyond_indices):.4f}`",
            "",
            "## Question-Type Slices",
            "",
            f"- best streamlined for `{best_streamlined['config_id']}`:",
        ]
    )
    lines.extend(summarize_question_types(outcomes, str(best_streamlined["config_id"])))
    lines.extend(
        [
            "",
            "## Final Interpretation",
            "",
            "- The streamlined study deliberately keeps only the components that looked justified in the v2.1 diagnostics.",
            "- Hybrid seed retrieval remains the backbone of the simplified model.",
            "- The section-mode sweep answers whether section information is worth keeping once isolated from the noisier v2.1 extras.",
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

    configs = build_configs()
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

    rows_sorted = sorted(rows, key=lambda row: str(row["config_id"]))
    outcomes_by_config: dict[str, list[dict[str, object]]] = {}
    for row in outcomes:
        outcomes_by_config.setdefault(str(row["config_id"]), []).append(row)

    best_adjacency = select_best(rows_sorted, lambda row: row["name"] == "adjacency_baseline")
    best_bridge_v1 = select_best(rows_sorted, lambda row: row["name"] == "bridge_v1_baseline")
    best_bridge_v2 = select_best(rows_sorted, lambda row: row["name"] == "bridge_v2_baseline")
    best_hybrid_soft = select_best(rows_sorted, lambda row: row["name"] == "bridge_v21_hybrid_soft")
    best_streamlined = select_best(rows_sorted, lambda row: row["method"] == "bridge_v21_streamlined" and int(row["diversify_final_context"]) == 0)
    best_streamlined_diverse = select_best(rows_sorted, lambda row: row["method"] == "bridge_v21_streamlined" and int(row["diversify_final_context"]) == 1)
    current_cfg = select_best(rows_sorted, lambda row: row["name"] == "bridge_v21_streamlined_current")
    improved_cfg = select_best(rows_sorted, lambda row: row["name"] == "bridge_v21_streamlined_improved")
    none_cfg = select_best(rows_sorted, lambda row: row["name"] == "bridge_v21_streamlined_none")
    diverse_variant = select_best(
        rows_sorted,
        lambda row: row["method"] == "bridge_v21_streamlined"
        and int(row["diversify_final_context"]) == 1
        and row["section_mode"] == best_streamlined["section_mode"],
    )

    beyond_indices = {
        index
        for index, row in enumerate(outcomes_by_config[str(best_bridge_v2["config_id"])])
        if row["first_evidence_distance"] in {"distance_2", "distance_3_plus"}
    }

    outcomes_sorted = sorted(
        [row for rows_for_config in outcomes_by_config.values() for row in rows_for_config],
        key=lambda row: (str(row["config_id"]), str(row["paper_id"]), str(row["question"])),
    )

    write_json(MASTER_JSON, {"subset_path": str(SUBSET_PATH), "results": rows_sorted})
    write_csv(MASTER_CSV, rows_sorted)
    write_csv(OUTCOMES_CSV, outcomes_sorted)
    SUMMARY_MD.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_MD.write_text(
        build_summary(
            rows_sorted,
            outcomes_sorted,
            best_adjacency,
            best_bridge_v1,
            best_bridge_v2,
            best_hybrid_soft,
            best_streamlined,
            best_streamlined_diverse,
            beyond_indices,
        ),
        encoding="utf-8",
    )
    EXAMPLES_MD.parent.mkdir(parents=True, exist_ok=True)
    EXAMPLES_MD.write_text(
        build_examples(
            qas,
            improved_cfg,
            current_cfg,
            none_cfg,
            best_streamlined,
            diverse_variant,
            best_bridge_v2,
            payloads,
        ),
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "best_streamlined": best_streamlined,
                "best_streamlined_diverse": best_streamlined_diverse,
                "best_hybrid_soft": best_hybrid_soft,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


