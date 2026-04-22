#!/usr/bin/env python3
"""Legacy early doc-constrained sweep kept for reproducibility."""
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

from lspbe.expansion import BridgeScoreDetail, adjacency_expand, bridge_expand_with_details
from lspbe.mve import QAExample, _build_segments_by_doc, _evidence_hit, load_qasper_subset
from lspbe.retrieval import BGERetriever
from lspbe.types import DocumentSegment, RetrievedSegment


SUBSET_SOURCE = ROOT / "data" / "qasper_train_full.json"
SUBSET_PATH = ROOT / "data" / "archive_debug" / "qasper_subset_debug_50.json"
MASTER_JSON = ROOT / "artifacts" / "mve_doc_constrained_50_master_results.json"
MASTER_CSV = ROOT / "artifacts" / "mve_doc_constrained_50_master_results.csv"
OUTCOMES_CSV = ROOT / "artifacts" / "mve_doc_constrained_50_question_outcomes.csv"
SUMMARY_MD = ROOT / "artifacts" / "mve_doc_constrained_50_summary.md"
EXAMPLES_MD = ROOT / "artifacts" / "mve_doc_constrained_50_examples.md"


@dataclass(frozen=True)
class SweepConfig:
    method: str
    weights: tuple[float, float, float] | None
    k: int = 5
    radius: int = 1
    top_m: int = 2
    context_budget: int = 20

    @property
    def config_id(self) -> str:
        return (
            f"{self.method}|weights={format_weights(self.weights)}|k={self.k}|radius={self.radius}|"
            f"top_m={self.top_m}|context_budget={self.context_budget}"
        )


def format_weights(weights: tuple[float, float, float] | None) -> str:
    if weights is None:
        return "na"
    return ",".join(f"{value:.2f}" for value in weights)


def ensure_subset(source_path: Path, subset_path: Path, max_papers: int) -> None:
    papers = json.loads(source_path.read_text(encoding="utf-8"))
    subset_path.parent.mkdir(parents=True, exist_ok=True)
    subset_path.write_text(json.dumps(papers[:max_papers], indent=2), encoding="utf-8")


def question_type(question: str) -> str:
    first = question.strip().lower().split()
    if not first:
        return "other"
    token = first[0]
    mapping = {
        "what": "what",
        "which": "which",
        "why": "why",
        "how": "how",
        "when": "when",
        "where": "where",
        "who": "who",
        "is": "boolean",
        "are": "boolean",
        "was": "boolean",
        "were": "boolean",
        "do": "boolean",
        "does": "boolean",
        "did": "boolean",
        "can": "boolean",
        "could": "boolean",
        "should": "boolean",
        "would": "boolean",
    }
    return mapping.get(token, "other")


def weight_preference(method: str, weights: tuple[float, float, float] | None) -> tuple[float, int, str]:
    if weights is None:
        return (0.0, 0, method)
    distance = sum(abs(value - 1.0) for value in weights)
    method_priority = {
        "bridge_full": 0,
        "bridge_adj_entity": 1,
        "bridge_adj_section": 2,
    }.get(method, 9)
    return (distance, method_priority, method)


def select_best(rows: list[dict[str, object]], methods: set[str]) -> dict[str, object]:
    filtered = [row for row in rows if row["method"] in methods]
    return sorted(
        filtered,
        key=lambda row: (
            -float(row["evidence_hit_rate"]),
            -float(row["recall_at_k"]),
            -float(row["mrr"]),
            weight_preference(str(row["method"]), parse_weights(str(row["weights"]))),
            str(row["config_id"]),
        ),
    )[0]


def parse_weights(raw: str) -> tuple[float, float, float] | None:
    if raw == "na":
        return None
    parts = [float(part) for part in raw.split(",")]
    return (parts[0], parts[1], parts[2])


def default_weights_for_method(method: str) -> tuple[float, float, float] | None:
    if method == "flat" or method == "adjacency":
        return None
    if method == "bridge_full":
        return (1.0, 1.0, 1.0)
    if method == "bridge_adj_entity":
        return (1.0, 1.0, 0.0)
    if method == "bridge_adj_section":
        return (1.0, 0.0, 1.0)
    raise ValueError(f"Unsupported method: {method}")


def build_configs() -> list[SweepConfig]:
    configs: dict[str, SweepConfig] = {}

    def add(config: SweepConfig) -> None:
        configs[config.config_id] = config

    # A. Core comparison.
    for method in ["flat", "adjacency", "bridge_adj_entity", "bridge_adj_section", "bridge_full"]:
        add(SweepConfig(method=method, weights=default_weights_for_method(method)))

    # B. Full bridge weight sweep.
    for weights in [
        (1.0, 1.0, 1.0),
        (1.0, 0.5, 0.5),
        (1.0, 2.0, 2.0),
        (0.5, 1.0, 1.0),
        (0.25, 1.0, 1.0),
        (0.5, 2.0, 2.0),
        (1.0, 2.0, 1.0),
        (1.0, 1.0, 2.0),
        (0.5, 2.0, 1.0),
        (0.5, 1.0, 2.0),
    ]:
        add(SweepConfig(method="bridge_full", weights=weights))

    # C. Signal-isolation sweeps.
    for adjacency_weight, entity_weight in [
        (1.0, 0.5),
        (1.0, 1.0),
        (1.0, 2.0),
        (0.5, 1.0),
        (0.25, 1.0),
    ]:
        add(SweepConfig(method="bridge_adj_entity", weights=(adjacency_weight, entity_weight, 0.0)))

    for adjacency_weight, section_weight in [
        (1.0, 0.5),
        (1.0, 1.0),
        (1.0, 2.0),
        (0.5, 1.0),
        (0.25, 1.0),
    ]:
        add(SweepConfig(method="bridge_adj_section", weights=(adjacency_weight, 0.0, section_weight)))

    return list(configs.values())


def apply_method(
    config: SweepConfig,
    rank: list[RetrievedSegment],
    segments_by_doc: dict[str, list[DocumentSegment]],
) -> tuple[list[DocumentSegment], dict[tuple[str, int], BridgeScoreDetail]]:
    if config.method == "flat":
        return [item.segment for item in rank][: config.context_budget], {}
    if config.method == "adjacency":
        return adjacency_expand(rank, segments_by_doc, context_budget=config.context_budget), {}
    if config.weights is None:
        raise ValueError(f"Bridge config requires weights: {config.method}")
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
    return retrieved, details


def build_rank_cache(
    retriever: BGERetriever,
    qas: list[QAExample],
    ks: set[int],
) -> dict[tuple[int, int], list[RetrievedSegment]]:
    query_matrix = retriever.embedder.encode([qa.query for qa in qas])
    cache: dict[tuple[int, int], list[RetrievedSegment]] = {}
    doc_to_indices: dict[str, list[int]] = {}
    for index, seg in enumerate(retriever.segments):
        doc_to_indices.setdefault(seg.doc_id, []).append(index)

    for qa_index, qa in enumerate(qas):
        doc_indices = doc_to_indices.get(qa.doc_id, [])
        if not doc_indices:
            for k in ks:
                cache[(qa_index, k)] = []
            continue
        scores = retriever._cosine_scores(query_matrix[qa_index], retriever._segment_matrix[doc_indices])
        sorted_local_idx = list(scores.argsort()[::-1])
        ranking = [doc_indices[idx] for idx in sorted_local_idx]
        score_by_segment_idx = {doc_indices[idx]: float(scores[idx]) for idx in range(len(doc_indices))}
        for k in ks:
            chosen = ranking[:k]
            cache[(qa_index, k)] = [
                RetrievedSegment(segment=retriever.segments[idx], score=score_by_segment_idx[idx])
                for idx in chosen
            ]
    return cache


def evidence_segment_ids(doc_segments: list[DocumentSegment], evidence_texts: list[str]) -> set[int]:
    ids: set[int] = set()
    for seg in doc_segments:
        seg_text = seg.text.lower()
        if any(ev.lower()[:80] in seg_text for ev in evidence_texts if ev):
            ids.add(seg.segment_id)
    return ids


def first_evidence_rank(retrieved: list[DocumentSegment], evidence_ids: set[int]) -> int | None:
    for rank, seg in enumerate(retrieved, start=1):
        if seg.segment_id in evidence_ids:
            return rank
    return None


def seed_to_evidence_distance(rank: list[RetrievedSegment], evidence_ids: set[int]) -> int | None:
    if not rank or not evidence_ids:
        return None
    distances = [
        abs(item.segment.segment_id - evidence_id)
        for item in rank
        for evidence_id in evidence_ids
    ]
    return min(distances) if distances else None


def evaluate_config(
    config: SweepConfig,
    subset_path: Path,
    qas: list[QAExample],
    segments_by_doc: dict[str, list[DocumentSegment]],
    rank_cache: dict[tuple[int, int], list[RetrievedSegment]],
    evidence_ids_by_qa: list[set[int]],
) -> tuple[dict[str, object], list[dict[str, object]], dict[int, dict[str, object]]]:
    outcome_rows: list[dict[str, object]] = []
    example_payloads: dict[int, dict[str, object]] = {}
    hits = 0
    rr_sum = 0.0
    evidence_hits = 0

    for qa_index, qa in enumerate(qas):
        rank = rank_cache[(qa_index, config.k)]
        retrieved, details = apply_method(config, rank, segments_by_doc)
        evidence_ids = evidence_ids_by_qa[qa_index]
        hit = _evidence_hit(retrieved, qa.evidence_texts)
        if retrieved:
            hits += 1
            rr_sum += 1.0
        if hit:
            evidence_hits += 1

        first_rank = first_evidence_rank(retrieved, evidence_ids)
        distance = seed_to_evidence_distance(rank, evidence_ids)
        row = {
            "config_id": config.config_id,
            "paper_id": qa.doc_id,
            "question": qa.query,
            "question_type": question_type(qa.query),
            "method": config.method,
            "weights": format_weights(config.weights),
            "k": config.k,
            "radius": config.radius,
            "top_m": config.top_m,
            "context_budget": config.context_budget,
            "hit": int(hit),
            "gold_evidence_count": len(qa.evidence_texts),
            "first_evidence_segment_rank": first_rank if first_rank is not None else "",
            "seed_to_evidence_distance": distance if distance is not None else "",
        }
        outcome_rows.append(row)
        example_payloads[qa_index] = {
            "retrieved": retrieved,
            "bridge_details": details,
            "hit": hit,
            "first_evidence_rank": first_rank,
            "seed_to_evidence_distance": distance,
        }

    total = max(len(qas), 1)
    metric_row = {
        "subset_path": str(subset_path),
        "config_id": config.config_id,
        "method": config.method,
        "weights": format_weights(config.weights),
        "k": config.k,
        "radius": config.radius,
        "top_m": config.top_m,
        "context_budget": config.context_budget,
        "queries": float(len(qas)),
        "recall_at_k": hits / total,
        "mrr": rr_sum / total,
        "evidence_hit_rate": evidence_hits / total,
    }
    return metric_row, outcome_rows, example_payloads


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def matched_adjacency_config(config: dict[str, object]) -> str:
    return SweepConfig(
        method="adjacency",
        weights=None,
        k=int(config["k"]),
        radius=int(config["radius"]),
        top_m=int(config["top_m"]),
        context_budget=int(config["context_budget"]),
    ).config_id


def method_block(
    title: str,
    method_key: str,
    payload: dict[str, object],
) -> list[str]:
    lines = [f"### {title}"]
    for seg in payload["retrieved"]:
        lines.append(f"- section: `{seg.section}`")
        lines.append(f"- segment_id: `{seg.segment_id}`")
        lines.append(f"- text: {seg.text.replace(chr(10), ' ').strip()}")
        if method_key.startswith("bridge"):
            detail = payload["bridge_details"].get((seg.doc_id, seg.segment_id))
            if detail is None:
                lines.append("- bridge_detail: seed segment or not added via bridge scoring")
            else:
                lines.append(
                    "- bridge_detail: "
                    f"seed=`{detail.seed_segment_id}`, total=`{detail.total_score:.3f}`, "
                    f"adjacency=`{detail.adjacency:.3f}`, entity_overlap=`{detail.entity_overlap:.3f}`, "
                    f"section_continuity=`{detail.section_continuity:.3f}`"
                )
        lines.append("")
    return lines


def build_examples(
    best_bridge: dict[str, object],
    best_flat: dict[str, object],
    all_payloads: dict[str, dict[int, dict[str, object]]],
    qas: list[QAExample],
) -> str:
    bridge_id = str(best_bridge["config_id"])
    adjacency_id = matched_adjacency_config(best_bridge)
    flat_id = SweepConfig(
        method="flat",
        weights=None,
        k=int(best_bridge["k"]),
        radius=int(best_bridge["radius"]),
        top_m=int(best_bridge["top_m"]),
        context_budget=int(best_bridge["context_budget"]),
    ).config_id
    if flat_id not in all_payloads:
        flat_id = str(best_flat["config_id"])

    categories = {
        "Bridge Win Over Adjacency": lambda idx: all_payloads[bridge_id][idx]["hit"] and not all_payloads[adjacency_id][idx]["hit"],
        "Adjacency Win Over Bridge": lambda idx: all_payloads[adjacency_id][idx]["hit"] and not all_payloads[bridge_id][idx]["hit"],
        "Tie": lambda idx: all_payloads[adjacency_id][idx]["hit"] and all_payloads[bridge_id][idx]["hit"],
        "Total Failure": lambda idx: (not all_payloads[adjacency_id][idx]["hit"]) and (not all_payloads[bridge_id][idx]["hit"]),
    }

    lines = [
        "# 50-Paper Doc-Constrained Examples",
        "",
        f"Best bridge config used in comparisons: `{bridge_id}`",
        "",
    ]

    for title, predicate in categories.items():
        lines.append(f"## {title}")
        lines.append("")
        chosen = next((idx for idx in range(len(qas)) if predicate(idx)), None)
        if chosen is None:
            lines.append("No example of this category was found in the 50-paper study.")
            lines.append("")
            continue
        qa = qas[chosen]
        lines.append(f"- paper_id: `{qa.doc_id}`")
        lines.append(f"- question: {qa.query}")
        lines.append("- gold evidence:")
        for evidence in qa.evidence_texts:
            lines.append(f"  - {evidence}")
        lines.append(
            f"- note: adjacency hit=`{int(all_payloads[adjacency_id][chosen]['hit'])}`, "
            f"bridge hit=`{int(all_payloads[bridge_id][chosen]['hit'])}`"
        )
        lines.append("")
        lines.extend(method_block("Flat", "flat", all_payloads[flat_id][chosen]))
        lines.extend(method_block("Adjacency", "adjacency", all_payloads[adjacency_id][chosen]))
        lines.extend(method_block("Best Bridge", str(best_bridge["method"]), all_payloads[bridge_id][chosen]))
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def summarize_question_types(
    outcomes: list[dict[str, object]],
    method: str,
    config_id: str,
) -> list[str]:
    filtered = [row for row in outcomes if row["method"] == method and row["config_id"] == config_id]
    by_type: dict[str, list[int]] = {}
    for row in filtered:
        by_type.setdefault(str(row["question_type"]), []).append(int(row["hit"]))
    lines: list[str] = []
    for q_type in sorted(by_type):
        values = by_type[q_type]
        lines.append(f"- `{q_type}`: {sum(values) / len(values):.3f} hit rate over {len(values)} questions")
    return lines


def summarize_distance(
    outcomes: list[dict[str, object]],
    config_id: str,
) -> list[str]:
    filtered = [row for row in outcomes if row["config_id"] == config_id and row["seed_to_evidence_distance"] != ""]
    if not filtered:
        return ["- No seed-to-evidence distance values were available."]
    buckets = {"0": [], "1": [], "2": [], "3+": []}
    for row in filtered:
        distance = int(row["seed_to_evidence_distance"])
        key = "3+" if distance >= 3 else str(distance)
        buckets[key].append(int(row["hit"]))
    lines = []
    for bucket in ["0", "1", "2", "3+"]:
        values = buckets[bucket]
        if values:
            lines.append(f"- distance `{bucket}`: {sum(values) / len(values):.3f} hit rate over {len(values)} questions")
    return lines


def build_summary(
    rows: list[dict[str, object]],
    outcomes: list[dict[str, object]],
    best_bridge: dict[str, object],
    best_full: dict[str, object],
    best_entity: dict[str, object],
    best_section: dict[str, object],
) -> str:
    best_flat = select_best(rows, {"flat"})
    best_adjacency = select_best(rows, {"adjacency"})
    best_overall = sorted(rows, key=lambda row: (-float(row["evidence_hit_rate"]), -float(row["mrr"]), str(row["config_id"])))[0]

    lower_adjacency_rows = [
        row for row in rows
        if str(row["method"]).startswith("bridge") and row["weights"] != "na" and parse_weights(str(row["weights"]))[0] < 1.0
    ]
    best_lower_adjacency = max(lower_adjacency_rows, key=lambda row: float(row["evidence_hit_rate"]))

    summary_lines = [
        "# 50-Paper Doc-Constrained Summary",
        "",
        "## Best Overall Configs",
        "",
        f"- best overall: `{best_overall['config_id']}` with evidence_hit_rate `{best_overall['evidence_hit_rate']:.4f}`",
        f"- best flat: `{best_flat['config_id']}` with evidence_hit_rate `{best_flat['evidence_hit_rate']:.4f}`",
        f"- best adjacency: `{best_adjacency['config_id']}` with evidence_hit_rate `{best_adjacency['evidence_hit_rate']:.4f}`",
        f"- best bridge overall: `{best_bridge['config_id']}` with evidence_hit_rate `{best_bridge['evidence_hit_rate']:.4f}`",
        f"- best bridge_adj_entity: `{best_entity['config_id']}` with evidence_hit_rate `{best_entity['evidence_hit_rate']:.4f}`",
        f"- best bridge_adj_section: `{best_section['config_id']}` with evidence_hit_rate `{best_section['evidence_hit_rate']:.4f}`",
        f"- best bridge_full: `{best_full['config_id']}` with evidence_hit_rate `{best_full['evidence_hit_rate']:.4f}`",
        "",
        "## Interpretation",
        "",
        f"- local expansion still beats flat: best adjacency `{best_adjacency['evidence_hit_rate']:.4f}` vs best flat `{best_flat['evidence_hit_rate']:.4f}`",
        f"- any bridge config beats adjacency: {'yes' if float(best_bridge['evidence_hit_rate']) > float(best_adjacency['evidence_hit_rate']) else 'no'}",
        f"- entity overlap helps: {'yes' if float(best_entity['evidence_hit_rate']) > float(best_adjacency['evidence_hit_rate']) else 'no'}",
        f"- section continuity helps: {'yes' if float(best_section['evidence_hit_rate']) > float(best_adjacency['evidence_hit_rate']) else 'no'}",
        f"- reducing adjacency weight helps: {'yes' if float(best_lower_adjacency['evidence_hit_rate']) > float(best_full['evidence_hit_rate']) else 'no'}",
        "",
        "## Sensitivity",
        "",
    ]

    radius_rows = [row for row in rows if int(row["radius"]) in {1, 2, 3}]
    for method in ["adjacency", str(best_entity["method"]), str(best_section["method"]), str(best_full["method"])]:
        matching = [row for row in radius_rows if row["method"] == method]
        if matching:
            best = max(matching, key=lambda row: float(row["evidence_hit_rate"]))
            summary_lines.append(f"- best radius for `{method}`: `{best['radius']}` with evidence_hit_rate `{best['evidence_hit_rate']:.4f}`")

    topm_rows = [row for row in rows if int(row["top_m"]) in {1, 2, 3}]
    for method in ["adjacency", str(best_bridge["method"])]:
        matching = [row for row in topm_rows if row["method"] == method]
        if matching:
            best = max(matching, key=lambda row: float(row["evidence_hit_rate"]))
            summary_lines.append(f"- best top_m for `{method}`: `{best['top_m']}` with evidence_hit_rate `{best['evidence_hit_rate']:.4f}`")

    for method in ["flat", "adjacency", str(best_bridge["method"])]:
        k_rows = [row for row in rows if row["method"] == method and int(row["k"]) in {3, 5, 8}]
        if k_rows:
            best = max(k_rows, key=lambda row: float(row["evidence_hit_rate"]))
            summary_lines.append(f"- best k for `{method}`: `{best['k']}` with evidence_hit_rate `{best['evidence_hit_rate']:.4f}`")

    for method in ["flat", "adjacency", str(best_bridge["method"])]:
        budget_rows = [row for row in rows if row["method"] == method and int(row["context_budget"]) in {10, 20, 30}]
        if budget_rows:
            best = max(budget_rows, key=lambda row: float(row["evidence_hit_rate"]))
            summary_lines.append(f"- best context_budget for `{method}`: `{best['context_budget']}` with evidence_hit_rate `{best['evidence_hit_rate']:.4f}`")

    summary_lines.extend([
        "",
        "## Question-Type Breakdown",
        "",
        f"- adjacency breakdown for `{best_adjacency['config_id']}`:",
    ])
    summary_lines.extend(summarize_question_types(outcomes, str(best_adjacency["method"]), str(best_adjacency["config_id"])))
    summary_lines.append(f"- best bridge breakdown for `{best_bridge['config_id']}`:")
    summary_lines.extend(summarize_question_types(outcomes, str(best_bridge["method"]), str(best_bridge["config_id"])))

    summary_lines.extend([
        "",
        "## Distance-to-Evidence",
        "",
        f"- adjacency distance profile for `{best_adjacency['config_id']}`:",
    ])
    summary_lines.extend(summarize_distance(outcomes, str(best_adjacency["config_id"])))
    summary_lines.append(f"- best bridge distance profile for `{best_bridge['config_id']}`:")
    summary_lines.extend(summarize_distance(outcomes, str(best_bridge["config_id"])))

    summary_lines.extend([
        "",
        "## Final Interpretation",
        "",
        "- The 50-paper doc-constrained study is the right place to compare local expansion methods because cross-paper contamination is removed.",
        f"- On this study, adjacency reaches `{best_adjacency['evidence_hit_rate']:.4f}` and the best bridge reaches `{best_bridge['evidence_hit_rate']:.4f}`.",
        "- If those values tie, the bridge signals are currently acting as weak tie-breakers rather than adding measurable retrieval lift.",
    ])
    return "\n".join(summary_lines).rstrip() + "\n"


def main() -> int:
    ensure_subset(SUBSET_SOURCE, SUBSET_PATH, max_papers=50)
    segments, qas = load_qasper_subset(SUBSET_PATH, max_papers=50, max_qas=10_000)
    retriever = BGERetriever(segments)
    segments_by_doc = _build_segments_by_doc(segments)

    ks = {3, 5, 8}
    rank_cache = build_rank_cache(retriever, qas, ks)
    evidence_ids_by_qa = [
        evidence_segment_ids(segments_by_doc.get(qa.doc_id, []), qa.evidence_texts)
        for qa in qas
    ]

    configs = build_configs()

    core_rows: list[dict[str, object]] = []
    all_outcomes: list[dict[str, object]] = []
    all_payloads: dict[str, dict[int, dict[str, object]]] = {}

    for config in configs:
        metric_row, outcome_rows, payloads = evaluate_config(
            config,
            subset_path=SUBSET_PATH,
            qas=qas,
            segments_by_doc=segments_by_doc,
            rank_cache=rank_cache,
            evidence_ids_by_qa=evidence_ids_by_qa,
        )
        core_rows.append(metric_row)
        all_outcomes.extend(outcome_rows)
        all_payloads[config.config_id] = payloads

    best_entity = select_best(core_rows, {"bridge_adj_entity"})
    best_section = select_best(core_rows, {"bridge_adj_section"})
    best_full = select_best(core_rows, {"bridge_full"})
    best_bridge_overall = select_best(core_rows, {"bridge_full", "bridge_adj_entity", "bridge_adj_section"})

    follow_up_configs: list[SweepConfig] = []
    for radius in [1, 2, 3]:
        follow_up_configs.append(SweepConfig(method="adjacency", weights=None, radius=radius))
        follow_up_configs.append(SweepConfig(method="bridge_adj_entity", weights=parse_weights(str(best_entity["weights"])), radius=radius))
        follow_up_configs.append(SweepConfig(method="bridge_adj_section", weights=parse_weights(str(best_section["weights"])), radius=radius))
        follow_up_configs.append(SweepConfig(method="bridge_full", weights=parse_weights(str(best_full["weights"])), radius=radius))

    for top_m in [1, 2, 3]:
        follow_up_configs.append(SweepConfig(method="adjacency", weights=None, top_m=top_m))
        follow_up_configs.append(
            SweepConfig(
                method=str(best_bridge_overall["method"]),
                weights=parse_weights(str(best_bridge_overall["weights"])),
                top_m=top_m,
            )
        )

    for k in [3, 5, 8]:
        follow_up_configs.append(SweepConfig(method="flat", weights=None, k=k))
        follow_up_configs.append(SweepConfig(method="adjacency", weights=None, k=k))
        follow_up_configs.append(
            SweepConfig(
                method=str(best_bridge_overall["method"]),
                weights=parse_weights(str(best_bridge_overall["weights"])),
                k=k,
            )
        )

    for context_budget in [10, 20, 30]:
        follow_up_configs.append(SweepConfig(method="flat", weights=None, context_budget=context_budget))
        follow_up_configs.append(SweepConfig(method="adjacency", weights=None, context_budget=context_budget))
        follow_up_configs.append(
            SweepConfig(
                method=str(best_bridge_overall["method"]),
                weights=parse_weights(str(best_bridge_overall["weights"])),
                context_budget=context_budget,
            )
        )

    seen_ids = {row["config_id"] for row in core_rows}
    for config in follow_up_configs:
        if config.config_id in seen_ids:
            continue
        metric_row, outcome_rows, payloads = evaluate_config(
            config,
            subset_path=SUBSET_PATH,
            qas=qas,
            segments_by_doc=segments_by_doc,
            rank_cache=rank_cache,
            evidence_ids_by_qa=evidence_ids_by_qa,
        )
        core_rows.append(metric_row)
        all_outcomes.extend(outcome_rows)
        all_payloads[config.config_id] = payloads
        seen_ids.add(config.config_id)

    core_rows_sorted = sorted(core_rows, key=lambda row: str(row["config_id"]))
    outcomes_sorted = sorted(
        all_outcomes,
        key=lambda row: (str(row["config_id"]), str(row["paper_id"]), str(row["question"])),
    )

    write_json(
        MASTER_JSON,
        {
            "subset_path": str(SUBSET_PATH),
            "results": core_rows_sorted,
        },
    )
    write_csv(MASTER_CSV, core_rows_sorted)
    write_csv(OUTCOMES_CSV, outcomes_sorted)

    best_entity = select_best(core_rows_sorted, {"bridge_adj_entity"})
    best_section = select_best(core_rows_sorted, {"bridge_adj_section"})
    best_full = select_best(core_rows_sorted, {"bridge_full"})
    best_bridge_overall = select_best(core_rows_sorted, {"bridge_full", "bridge_adj_entity", "bridge_adj_section"})
    best_flat = select_best(core_rows_sorted, {"flat"})

    SUMMARY_MD.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_MD.write_text(
        build_summary(core_rows_sorted, outcomes_sorted, best_bridge_overall, best_full, best_entity, best_section),
        encoding="utf-8",
    )
    EXAMPLES_MD.parent.mkdir(parents=True, exist_ok=True)
    EXAMPLES_MD.write_text(build_examples(best_bridge_overall, best_flat, all_payloads, qas), encoding="utf-8")

    print(json.dumps({"best_bridge": best_bridge_overall, "best_adjacency": select_best(core_rows_sorted, {"adjacency"})}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


