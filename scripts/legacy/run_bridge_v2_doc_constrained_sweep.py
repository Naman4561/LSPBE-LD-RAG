#!/usr/bin/env python3
"""Legacy Bridge v2 study kept for reproducibility.

Use `scripts/run_qasper_baseline_compare.py` for the main current comparison.
"""
from __future__ import annotations

import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path

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
    adjacency_expand,
    bridge_expand_with_details,
    bridge_v2_expand_with_details,
    build_segment_idf,
)
from lspbe.mve import QAExample, _build_segments_by_doc, _evidence_hit, load_qasper_subset
from lspbe.retrieval import BGERetriever
from lspbe.types import DocumentSegment, RetrievedSegment


SUBSET_PATH = ROOT / "data" / "archive_debug" / "qasper_subset_debug_50.json"
MASTER_JSON = ROOT / "artifacts" / "mve_doc_constrained_50_bridge_v2_master_results.json"
MASTER_CSV = ROOT / "artifacts" / "mve_doc_constrained_50_bridge_v2_master_results.csv"
OUTCOMES_CSV = ROOT / "artifacts" / "mve_doc_constrained_50_bridge_v2_question_outcomes.csv"
SUMMARY_MD = ROOT / "artifacts" / "mve_doc_constrained_50_bridge_v2_summary.md"
EXAMPLES_MD = ROOT / "artifacts" / "mve_doc_constrained_50_bridge_v2_examples.md"


@dataclass(frozen=True)
class SweepConfig:
    method: str
    weights: tuple[float, float, float] | None
    k: int = 8
    radius: int = 1
    top_m: int = 2
    context_budget: int = 20
    bridge_v2_max_skip_distance: int | None = None
    bridge_v2_top_per_seed: int | None = None

    @property
    def config_id(self) -> str:
        return (
            f"{self.method}|weights={format_weights(self.weights)}|k={self.k}|radius={self.radius}|top_m={self.top_m}|"
            f"context_budget={self.context_budget}|bridge_v2_max_skip_distance={self.bridge_v2_max_skip_distance or 'na'}|"
            f"bridge_v2_top_per_seed={self.bridge_v2_top_per_seed or 'na'}"
        )


def format_weights(weights: tuple[float, float, float] | None) -> str:
    if weights is None:
        return "na"
    return ",".join(f"{value:.2f}" for value in weights)


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


def parse_weights(raw: str) -> tuple[float, float, float] | None:
    if raw == "na":
        return None
    parts = [float(part) for part in raw.split(",")]
    return parts[0], parts[1], parts[2]


def select_best(rows: list[dict[str, object]], methods: set[str]) -> dict[str, object]:
    candidates = [row for row in rows if row["method"] in methods]
    return sorted(
        candidates,
        key=lambda row: (
            -float(row["evidence_hit_rate"]),
            -float(row["mrr"]),
            str(row["config_id"]),
        ),
    )[0]


def build_configs() -> list[SweepConfig]:
    configs: dict[str, SweepConfig] = {}

    def add(config: SweepConfig) -> None:
        configs[config.config_id] = config

    # Baselines.
    add(SweepConfig(method="flat", weights=None))
    add(SweepConfig(method="adjacency", weights=None))
    add(SweepConfig(method="bridge_v1_full", weights=(1.0, 1.0, 1.0)))
    add(SweepConfig(method="bridge_v2_skip2", weights=(1.0, 1.0, 1.0), bridge_v2_max_skip_distance=2, bridge_v2_top_per_seed=1))
    add(SweepConfig(method="bridge_v2_full", weights=(1.0, 1.0, 1.0), bridge_v2_max_skip_distance=3, bridge_v2_top_per_seed=1))

    weight_sweep = [
        (1.0, 1.0, 0.5),
        (1.0, 1.0, 1.0),
        (1.0, 2.0, 1.0),
        (1.0, 1.0, 2.0),
        (1.0, 2.0, 2.0),
        (2.0, 1.0, 1.0),
        (2.0, 2.0, 1.0),
        (2.0, 1.0, 2.0),
    ]
    for weights in weight_sweep:
        add(SweepConfig(method="bridge_v2_skip2", weights=weights, bridge_v2_max_skip_distance=2, bridge_v2_top_per_seed=1))
        add(SweepConfig(method="bridge_v2_full", weights=weights, bridge_v2_max_skip_distance=3, bridge_v2_top_per_seed=1))

    for top_per_seed in [1, 2]:
        add(SweepConfig(method="bridge_v2_skip2", weights=(1.0, 1.0, 1.0), bridge_v2_max_skip_distance=2, bridge_v2_top_per_seed=top_per_seed))
        add(SweepConfig(method="bridge_v2_full", weights=(1.0, 1.0, 1.0), bridge_v2_max_skip_distance=3, bridge_v2_top_per_seed=top_per_seed))

    return list(configs.values())


def build_rank_cache(
    retriever: BGERetriever,
    qas: list[QAExample],
    ks: set[int],
) -> tuple[dict[tuple[int, int], list[RetrievedSegment]], list[object]]:
    query_matrix = retriever.embedder.encode([qa.query for qa in qas])
    doc_to_indices: dict[str, list[int]] = {}
    for idx, seg in enumerate(retriever.segments):
        doc_to_indices.setdefault(seg.doc_id, []).append(idx)

    cache: dict[tuple[int, int], list[RetrievedSegment]] = {}
    for qa_index, qa in enumerate(qas):
        indices = doc_to_indices.get(qa.doc_id, [])
        if not indices:
            for k in ks:
                cache[(qa_index, k)] = []
            continue
        scores = retriever._cosine_scores(query_matrix[qa_index], retriever._segment_matrix[indices])
        sorted_local = list(scores.argsort()[::-1])
        ranking = [indices[pos] for pos in sorted_local]
        score_by_idx = {indices[pos]: float(scores[pos]) for pos in range(len(indices))}
        for k in ks:
            chosen = ranking[:k]
            cache[(qa_index, k)] = [
                RetrievedSegment(segment=retriever.segments[idx], score=score_by_idx[idx])
                for idx in chosen
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


def bridge_detail_string(details: dict[tuple[str, int], BridgeV2ScoreDetail | BridgeScoreDetail]) -> str:
    parts: list[str] = []
    for key, detail in sorted(details.items()):
        if isinstance(detail, BridgeV2ScoreDetail):
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
    rank: list[RetrievedSegment],
    query_vector,
    segments_by_doc: dict[str, list[DocumentSegment]],
    segment_vectors: dict[tuple[str, int], object],
    idf_map: dict[str, float],
) -> tuple[list[DocumentSegment], dict[tuple[str, int], BridgeV2ScoreDetail | BridgeScoreDetail], set[tuple[str, int]], set[tuple[str, int]]]:
    if config.method == "flat":
        retrieved = [item.segment for item in rank][: config.context_budget]
        return retrieved, {}, set(), set()
    if config.method == "adjacency":
        retrieved = adjacency_expand(rank, segments_by_doc, context_budget=config.context_budget)
        keys = {(seg.doc_id, seg.segment_id) for seg in retrieved}
        return retrieved, {}, keys, set()
    if config.method == "bridge_v1_full":
        adjacency_segments = adjacency_expand(rank, segments_by_doc, context_budget=config.context_budget)
        adjacency_keys = {(seg.doc_id, seg.segment_id) for seg in adjacency_segments}
        retrieved, details = bridge_expand_with_details(
            rank,
            segments_by_doc,
            context_budget=config.context_budget,
            radius=config.radius,
            top_m=config.top_m,
            alpha=config.weights[0],
            beta=config.weights[1],
            gamma=config.weights[2],
        )
        retrieved_keys = {(seg.doc_id, seg.segment_id) for seg in retrieved}
        return retrieved, details, adjacency_keys & retrieved_keys, retrieved_keys - adjacency_keys
    if config.method in {"bridge_v2_skip2", "bridge_v2_full"}:
        retrieved, details, adjacency_keys, bridge_keys = bridge_v2_expand_with_details(
            rank,
            segments_by_doc,
            context_budget=config.context_budget,
            query_vector=query_vector,
            segment_vectors=segment_vectors,
            idf_map=idf_map,
            max_skip_distance=config.bridge_v2_max_skip_distance or 2,
            top_per_seed=config.bridge_v2_top_per_seed or 1,
            query_weight=config.weights[0],
            seed_weight=config.weights[1],
            section_weight=config.weights[2],
        )
        return retrieved, details, adjacency_keys, bridge_keys
    raise ValueError(f"Unsupported method: {config.method}")


def evaluate_config(
    config: SweepConfig,
    subset_path: Path,
    qas: list[QAExample],
    segments_by_doc: dict[str, list[DocumentSegment]],
    segment_vectors: dict[tuple[str, int], object],
    idf_map: dict[str, float],
    rank_cache: dict[tuple[int, int], list[RetrievedSegment]],
    query_vectors: list[object],
    evidence_ids_by_qa: list[set[int]],
) -> tuple[dict[str, object], list[dict[str, object]], dict[int, dict[str, object]]]:
    hits = 0
    rr_sum = 0.0
    evidence_hits = 0
    outcome_rows: list[dict[str, object]] = []
    payloads: dict[int, dict[str, object]] = {}

    for qa_index, qa in enumerate(qas):
        rank = rank_cache[(qa_index, config.k)]
        retrieved, details, adjacency_keys, bridge_keys = apply_config(
            config,
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
        first_rank = first_evidence_rank(retrieved, evidence_ids)
        distance = min_seed_distance(rank, evidence_ids)

        payloads[qa_index] = {
            "retrieved": retrieved,
            "details": details,
            "adjacency_keys": adjacency_keys,
            "bridge_keys": bridge_keys,
            "hit": hit,
            "distance": distance,
        }

        outcome_rows.append(
            {
                "config_id": config.config_id,
                "paper_id": qa.doc_id,
                "question": qa.query,
                "question_type": question_type(qa.query),
                "method": config.method,
                "weights": format_weights(config.weights),
                "k": config.k,
                "radius": config.radius,
                "top_m": config.top_m,
                "bridge_v2_max_skip_distance": config.bridge_v2_max_skip_distance or "",
                "bridge_v2_top_per_seed": config.bridge_v2_top_per_seed or "",
                "context_budget": config.context_budget,
                "hit": int(hit),
                "first_evidence_distance": distance_bucket(distance),
                "first_evidence_segment_rank": first_rank if first_rank is not None else "",
                "seed_segment_ids": ";".join(str(item.segment.segment_id) for item in rank),
                "adjacency_added_segments": segment_key_list(retrieved, adjacency_keys),
                "bridge_added_segments": segment_key_list(retrieved, bridge_keys),
                "bridge_component_scores": bridge_detail_string(details),
                "bridge_only_win": 0,
            }
        )

    total = max(len(qas), 1)
    metric_row = {
        "subset_path": str(subset_path),
        "config_id": config.config_id,
        "method": config.method,
        "weights": format_weights(config.weights),
        "k": config.k,
        "radius": config.radius,
        "top_m": config.top_m,
        "bridge_v2_max_skip_distance": config.bridge_v2_max_skip_distance or "",
        "bridge_v2_top_per_seed": config.bridge_v2_top_per_seed or "",
        "context_budget": config.context_budget,
        "queries": float(len(qas)),
        "recall_at_k": hits / total,
        "mrr": rr_sum / total,
        "evidence_hit_rate": evidence_hits / total,
    }
    return metric_row, outcome_rows, payloads


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def matched_adjacency_id(config: dict[str, object]) -> str:
    return SweepConfig(
        method="adjacency",
        weights=None,
        k=int(config["k"]),
        radius=int(config["radius"]),
        top_m=int(config["top_m"]),
        context_budget=int(config["context_budget"]),
    ).config_id


def matched_bridge_v1_id(config: dict[str, object]) -> str:
    return SweepConfig(
        method="bridge_v1_full",
        weights=(1.0, 1.0, 1.0),
        k=int(config["k"]),
        radius=1,
        top_m=2,
        context_budget=int(config["context_budget"]),
    ).config_id


def beyond_adjacency_indices(outcomes_by_config: dict[str, list[dict[str, object]]], adjacency_config_id: str) -> set[int]:
    indices: set[int] = set()
    for index, row in enumerate(outcomes_by_config[adjacency_config_id]):
        if row["first_evidence_distance"] in {"distance_2", "distance_3_plus"}:
            indices.add(index)
    return indices


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
        f"- `{question}`: {sum(values) / len(values):.3f} hit rate over {len(values)} questions"
        for question, values in sorted(grouped.items())
    ]


def method_block(title: str, payload: dict[str, object], method: str) -> list[str]:
    lines = [f"### {title}"]
    for seg in payload["retrieved"]:
        lines.append(f"- section: `{seg.section}`")
        lines.append(f"- segment_id: `{seg.segment_id}`")
        lines.append(f"- text: {seg.text.replace(chr(10), ' ').strip()}")
        if method.startswith("bridge"):
            detail = payload["details"].get((seg.doc_id, seg.segment_id))
            if detail is None:
                lines.append("- bridge_detail: seed segment or not added via bridge scoring")
            elif isinstance(detail, BridgeV2ScoreDetail):
                lines.append(
                    "- bridge_detail: "
                    f"seed=`{detail.seed_segment_id}`, total=`{detail.total_score:.3f}`, "
                    f"query=`{detail.query_relevance:.3f}`, seed_cont=`{detail.seed_continuity:.3f}`, "
                    f"section_sim=`{detail.section_similarity:.3f}`, distance=`{detail.distance}`"
                )
            else:
                lines.append(
                    "- bridge_detail: "
                    f"seed=`{detail.seed_segment_id}`, total=`{detail.total_score:.3f}`, "
                    f"adjacency=`{detail.adjacency:.3f}`, entity=`{detail.entity_overlap:.3f}`, "
                    f"section=`{detail.section_continuity:.3f}`"
                )
        lines.append("")
    return lines


def build_examples(
    qas: list[QAExample],
    best_bridge_v1: dict[str, object],
    best_bridge_v2_skip2: dict[str, object],
    best_bridge_v2_full: dict[str, object],
    best_adjacency: dict[str, object],
    all_payloads: dict[str, dict[int, dict[str, object]]],
) -> str:
    categories = {
        "Bridge v2 Win Over Adjacency": lambda idx, bridge_id: all_payloads[bridge_id][idx]["hit"] and not all_payloads[str(best_adjacency["config_id"])][idx]["hit"],
        "Adjacency Win Over Bridge v2": lambda idx, bridge_id: all_payloads[str(best_adjacency["config_id"])][idx]["hit"] and not all_payloads[bridge_id][idx]["hit"],
        "Bridge v2 Win Over Bridge v1": lambda idx, bridge_id: all_payloads[bridge_id][idx]["hit"] and not all_payloads[str(best_bridge_v1["config_id"])][idx]["hit"],
        "Tie": lambda idx, bridge_id: all_payloads[str(best_adjacency["config_id"])][idx]["hit"] and all_payloads[bridge_id][idx]["hit"],
        "Total Failure": lambda idx, bridge_id: (not all_payloads[str(best_adjacency["config_id"])][idx]["hit"]) and (not all_payloads[bridge_id][idx]["hit"]),
    }

    chosen_bridge = best_bridge_v2_full if float(best_bridge_v2_full["evidence_hit_rate"]) >= float(best_bridge_v2_skip2["evidence_hit_rate"]) else best_bridge_v2_skip2
    bridge_id = str(chosen_bridge["config_id"])

    lines = [
        "# Bridge v2 Qualitative Examples",
        "",
        f"Best adjacency config: `{best_adjacency['config_id']}`",
        f"Best bridge v1 config: `{best_bridge_v1['config_id']}`",
        f"Best bridge_v2_skip2 config: `{best_bridge_v2_skip2['config_id']}`",
        f"Best bridge_v2_full config: `{best_bridge_v2_full['config_id']}`",
        "",
    ]

    for title, predicate in categories.items():
        lines.append(f"## {title}")
        lines.append("")
        idx = next((i for i in range(len(qas)) if predicate(i, bridge_id)), None)
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
        lines.extend(method_block("Adjacency", all_payloads[str(best_adjacency['config_id'])][idx], "adjacency"))
        lines.extend(method_block("Bridge v1", all_payloads[str(best_bridge_v1['config_id'])][idx], "bridge_v1_full"))
        lines.extend(method_block("Bridge v2", all_payloads[bridge_id][idx], str(chosen_bridge["method"])))
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def build_summary(
    rows: list[dict[str, object]],
    outcomes: list[dict[str, object]],
    best_adjacency: dict[str, object],
    best_bridge_v1: dict[str, object],
    best_bridge_v2_skip2: dict[str, object],
    best_bridge_v2_full: dict[str, object],
    beyond_indices: set[int],
) -> str:
    best_flat = select_best(rows, {"flat"})
    best_v2 = best_bridge_v2_full if float(best_bridge_v2_full["evidence_hit_rate"]) >= float(best_bridge_v2_skip2["evidence_hit_rate"]) else best_bridge_v2_skip2
    outcomes_by_config: dict[str, list[dict[str, object]]] = {}
    for row in outcomes:
        outcomes_by_config.setdefault(str(row["config_id"]), []).append(row)

    lines = [
        "# Bridge v2 Summary",
        "",
        "## Best Configs",
        "",
        f"- best flat: `{best_flat['config_id']}` with evidence_hit_rate `{best_flat['evidence_hit_rate']:.4f}`",
        f"- best adjacency: `{best_adjacency['config_id']}` with evidence_hit_rate `{best_adjacency['evidence_hit_rate']:.4f}`",
        f"- best bridge v1: `{best_bridge_v1['config_id']}` with evidence_hit_rate `{best_bridge_v1['evidence_hit_rate']:.4f}`",
        f"- best bridge_v2_skip2: `{best_bridge_v2_skip2['config_id']}` with evidence_hit_rate `{best_bridge_v2_skip2['evidence_hit_rate']:.4f}`",
        f"- best bridge_v2_full: `{best_bridge_v2_full['config_id']}` with evidence_hit_rate `{best_bridge_v2_full['evidence_hit_rate']:.4f}`",
        "",
        "## Main Answers",
        "",
        f"1. does Bridge v2 beat adjacency overall? {'yes' if float(best_v2['evidence_hit_rate']) > float(best_adjacency['evidence_hit_rate']) else 'no'}",
        f"2. does Bridge v2 beat bridge v1? {'yes' if float(best_v2['evidence_hit_rate']) > float(best_bridge_v1['evidence_hit_rate']) else 'no'}",
        f"3. does Bridge v2 help on the beyond-adjacency subset? {'yes' if slice_hit_rate(outcomes_by_config[str(best_v2['config_id'])], beyond_indices) > slice_hit_rate(outcomes_by_config[str(best_adjacency['config_id'])], beyond_indices) else 'no'}",
        f"4. which Bridge v2 variant is better: {'skip2' if float(best_bridge_v2_skip2['evidence_hit_rate']) > float(best_bridge_v2_full['evidence_hit_rate']) else 'full'}",
        f"5. which weights work best? best skip2 `{best_bridge_v2_skip2['weights']}`, best full `{best_bridge_v2_full['weights']}`",
        f"6. does query relevance matter more than continuity? {'likely yes' if float(best_bridge_v2_full['evidence_hit_rate']) >= float(best_bridge_v2_skip2['evidence_hit_rate']) else 'unclear'}",
        "7. do section signals help at all? " + ("yes" if float(best_bridge_v2_full['evidence_hit_rate']) > float(best_bridge_v2_skip2['evidence_hit_rate']) else "no clear evidence"),
        "8. does adding distance-3 candidates help or just add noise? " + ("helps" if float(best_bridge_v2_full['evidence_hit_rate']) > float(best_bridge_v2_skip2['evidence_hit_rate']) else "no clear gain"),
        "",
        "## Beyond-Adjacency Subset",
        "",
        f"- subset size: `{len(beyond_indices)}` questions",
        f"- adjacency hit rate: `{slice_hit_rate(outcomes_by_config[str(best_adjacency['config_id'])], beyond_indices):.4f}`",
        f"- bridge v1 hit rate: `{slice_hit_rate(outcomes_by_config[str(best_bridge_v1['config_id'])], beyond_indices):.4f}`",
        f"- bridge_v2_skip2 hit rate: `{slice_hit_rate(outcomes_by_config[str(best_bridge_v2_skip2['config_id'])], beyond_indices):.4f}`",
        f"- bridge_v2_full hit rate: `{slice_hit_rate(outcomes_by_config[str(best_bridge_v2_full['config_id'])], beyond_indices):.4f}`",
        "",
        "## Question-Type Slices",
        "",
        f"- adjacency for `{best_adjacency['config_id']}`:",
    ]
    lines.extend(summarize_question_types(outcomes, str(best_adjacency["config_id"])))
    lines.append(f"- best bridge_v2 for `{best_v2['config_id']}`:")
    lines.extend(summarize_question_types(outcomes, str(best_v2["config_id"])))
    lines.extend([
        "",
        "## Final Interpretation",
        "",
        "- Bridge v2 was designed to only score non-immediate skip-local candidates, so any gain here is genuinely beyond adjacency.",
        f"- Best adjacency reached `{best_adjacency['evidence_hit_rate']:.4f}` while best Bridge v2 reached `{best_v2['evidence_hit_rate']:.4f}`.",
        "- If those values still tie, the redesigned bridge still is not buying measurable evidence recovery on this QASPER slice.",
    ])
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

    ks = {5, 8, 10}
    rank_cache, query_vectors = build_rank_cache(retriever, qas, ks)
    evidence_ids_by_qa = [
        evidence_segment_ids(segments_by_doc.get(qa.doc_id, []), qa.evidence_texts)
        for qa in qas
    ]

    configs = build_configs()
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

    best_skip2 = select_best(rows, {"bridge_v2_skip2"})
    best_full = select_best(rows, {"bridge_v2_full"})

    follow_up: list[SweepConfig] = []
    for k in [5, 8, 10]:
        follow_up.append(
            SweepConfig(
                method="bridge_v2_skip2",
                weights=parse_weights(str(best_skip2["weights"])),
                k=k,
                bridge_v2_max_skip_distance=2,
                bridge_v2_top_per_seed=int(best_skip2["bridge_v2_top_per_seed"] or 1),
            )
        )
        follow_up.append(
            SweepConfig(
                method="bridge_v2_full",
                weights=parse_weights(str(best_full["weights"])),
                k=k,
                bridge_v2_max_skip_distance=3,
                bridge_v2_top_per_seed=int(best_full["bridge_v2_top_per_seed"] or 1),
            )
        )

    best_bridge_v1 = select_best(rows, {"bridge_v1_full"})
    for context_budget in [20, 30]:
        follow_up.append(SweepConfig(method="adjacency", weights=None, k=8, context_budget=context_budget))
        follow_up.append(SweepConfig(method="bridge_v1_full", weights=(1.0, 1.0, 1.0), k=8, context_budget=context_budget))
        follow_up.append(
            SweepConfig(
                method="bridge_v2_skip2",
                weights=parse_weights(str(best_skip2["weights"])),
                k=8,
                context_budget=context_budget,
                bridge_v2_max_skip_distance=2,
                bridge_v2_top_per_seed=int(best_skip2["bridge_v2_top_per_seed"] or 1),
            )
        )
        follow_up.append(
            SweepConfig(
                method="bridge_v2_full",
                weights=parse_weights(str(best_full["weights"])),
                k=8,
                context_budget=context_budget,
                bridge_v2_max_skip_distance=3,
                bridge_v2_top_per_seed=int(best_full["bridge_v2_top_per_seed"] or 1),
            )
        )

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
        seen.add(config.config_id)

    rows_sorted = sorted(rows, key=lambda row: str(row["config_id"]))
    outcomes_by_config: dict[str, list[dict[str, object]]] = {}
    for row in outcomes:
        outcomes_by_config.setdefault(str(row["config_id"]), []).append(row)

    best_adjacency = select_best(rows_sorted, {"adjacency"})
    best_bridge_v1 = select_best(rows_sorted, {"bridge_v1_full"})
    best_skip2 = select_best(rows_sorted, {"bridge_v2_skip2"})
    best_full = select_best(rows_sorted, {"bridge_v2_full"})
    beyond_indices = beyond_adjacency_indices(outcomes_by_config, str(best_adjacency["config_id"]))
    fallback_adjacency_id = str(best_adjacency["config_id"])

    for config_id, config_outcomes in outcomes_by_config.items():
        config_meta = next(row for row in rows_sorted if row["config_id"] == config_id)
        if str(config_meta["method"]).startswith("bridge_v2"):
            adjacency_id = matched_adjacency_id(config_meta)
            if adjacency_id not in outcomes_by_config:
                adjacency_id = fallback_adjacency_id
            adjacency_hits = outcomes_by_config[adjacency_id]
            for index, row in enumerate(config_outcomes):
                row["bridge_only_win"] = int(int(row["hit"]) == 1 and int(adjacency_hits[index]["hit"]) == 0)

    outcomes_sorted = sorted(
        [row for rows_for_config in outcomes_by_config.values() for row in rows_for_config],
        key=lambda row: (str(row["config_id"]), str(row["paper_id"]), str(row["question"])),
    )

    write_json(MASTER_JSON, {"subset_path": str(SUBSET_PATH), "results": rows_sorted})
    write_csv(MASTER_CSV, rows_sorted)
    write_csv(OUTCOMES_CSV, outcomes_sorted)
    SUMMARY_MD.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_MD.write_text(
        build_summary(rows_sorted, outcomes_sorted, best_adjacency, best_bridge_v1, best_skip2, best_full, beyond_indices),
        encoding="utf-8",
    )
    EXAMPLES_MD.parent.mkdir(parents=True, exist_ok=True)
    EXAMPLES_MD.write_text(
        build_examples(qas, best_bridge_v1, best_skip2, best_full, best_adjacency, payloads),
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "best_adjacency": best_adjacency,
                "best_bridge_v1": best_bridge_v1,
                "best_bridge_v2_skip2": best_skip2,
                "best_bridge_v2_full": best_full,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


