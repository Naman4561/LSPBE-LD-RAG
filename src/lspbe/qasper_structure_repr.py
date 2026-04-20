from __future__ import annotations

import csv
import json
from pathlib import Path
from statistics import median
from typing import Any

from .qasper import QasperMethodConfig, apply_qasper_method
from .qasper_eval import build_rank_cache, load_qasper_eval_context
from .run_control import atomic_write_json, atomic_write_text
from .structure_repr import build_float_structure_metadata, collapse_retrieved_to_backbone
from .subsets import evidence_coverage, evidence_hit, evidence_matching_segments, evidence_segment_ids

TARGET_SUBSETS = (
    "skip_local",
    "multi_span",
    "float_table",
    "float_direct",
    "float_reference",
    "float_adjacent_prose",
)


def _mean(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def _rank_stats(ranks: list[int]) -> dict[str, Any]:
    if not ranks:
        return {"count": 0, "mean": None, "median": None, "min": None, "max": None}
    return {
        "count": len(ranks),
        "mean": sum(ranks) / len(ranks),
        "median": float(median(ranks)),
        "min": min(ranks),
        "max": max(ranks),
    }


def _subset_memberships(label: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for subset_name in TARGET_SUBSETS:
        if bool(label.get(subset_name)):
            names.append(subset_name)
    signal_mode = str(label.get("float_signal_mode") or "none")
    names.append(f"float_signal_mode::{signal_mode}")
    return names


def _aggregate_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    seed_ranks = [int(row["first_evidence_rank"]) for row in rows if row["first_evidence_rank"] is not None]
    return {
        "queries": total,
        "seed_hit_rate": sum(bool(row["seed_hit"]) for row in rows) / max(total, 1),
        "evidence_hit_rate": sum(bool(row["evidence_hit"]) for row in rows) / max(total, 1),
        "evidence_coverage_rate": sum(float(row["evidence_coverage"]) for row in rows) / max(total, 1),
        "first_evidence_rank": _mean([float(rank) for rank in seed_ranks]),
        "first_evidence_rank_stats": _rank_stats(seed_ranks),
    }


def evaluate_representation_mode(
    *,
    dataset_path: str | Path,
    methods: list[QasperMethodConfig],
    segmentation_mode: str,
    representation_mode: str,
    max_questions: int,
    max_papers: int = 1_000_000,
) -> dict[str, Any]:
    context = load_qasper_eval_context(
        subset_path=dataset_path,
        max_papers=max_papers,
        max_qas=max_questions,
        segmentation_mode=segmentation_mode,
        representation_mode=representation_mode,
    )
    qas = context["qas"]
    qa_records = context["qa_records"]
    subset_labels = context["subset_labels"]
    requests = {method.seed_request for method in methods}
    rank_cache, query_vectors = build_rank_cache(context["retriever"], qas, requests)
    evidence_ids_by_qa = [
        evidence_segment_ids(context["segments_by_doc"].get(qa.doc_id, []), qa.evidence_texts)
        for qa in qas
    ]

    method_rows: dict[str, list[dict[str, Any]]] = {}
    method_summaries: list[dict[str, Any]] = []

    for method in methods:
        rows: list[dict[str, Any]] = []
        for qa_index, qa in enumerate(qas):
            rank = rank_cache[(qa_index, method.seed_request)]
            collapsed_rank = collapse_retrieved_to_backbone(rank, context["segments_by_doc"], max_results=method.k)
            retrieved, _, _, _, _ = apply_qasper_method(
                method,
                qa,
                rank,
                query_vectors[qa_index],
                context["segments_by_doc"],
                context["segment_vectors"],
                context["idf_map"],
            )
            evidence_ids = evidence_ids_by_qa[qa_index]
            first_rank = None
            for position, seed in enumerate(collapsed_rank, start=1):
                if seed.segment.segment_id in evidence_ids:
                    first_rank = position
                    break

            matched_segments = evidence_matching_segments(retrieved, qa.evidence_texts)
            retrieval_float_metadata = build_float_structure_metadata(matched_segments, qa.evidence_texts)
            label = subset_labels[qa_index]
            record = qa_records[qa_index]
            rows.append(
                {
                    "paper_id": str(record["paper_id"]),
                    "question_id": str(record["qa_id"]),
                    "question": str(record["question"]),
                    "representation_mode": representation_mode,
                    "retrieval_method": method.name,
                    "seed_hit": first_rank is not None,
                    "evidence_hit": evidence_hit(retrieved, qa.evidence_texts),
                    "evidence_coverage": evidence_coverage(retrieved, qa.evidence_texts),
                    "first_evidence_rank": first_rank,
                    "question_type": str(label["question_type"]),
                    "adjacency_easy": bool(label["adjacency_easy"]),
                    "skip_local": bool(label["skip_local"]),
                    "multi_span": bool(label["multi_span"]),
                    "float_table": bool(label["float_table"]),
                    "float_direct": bool(label.get("float_direct")),
                    "float_reference": bool(label.get("float_reference")),
                    "float_adjacent_prose": bool(label.get("float_adjacent_prose")),
                    "gold_float_signal_mode": str(label.get("float_signal_mode", "none")),
                    "gold_matched_unit_types": " || ".join(label.get("gold_matched_unit_types", [])),
                    "retrieved_float_signal_mode": str(retrieval_float_metadata["float_signal_mode"]),
                    "retrieved_matched_unit_types": " || ".join(retrieval_float_metadata["matched_unit_types"]),
                    "retrieved_has_caption_unit": bool(retrieval_float_metadata["retrieved_has_caption_unit"]),
                    "retrieved_has_inline_ref_unit": bool(retrieval_float_metadata["retrieved_has_inline_ref_unit"]),
                    "retrieved_has_float_like_unit": bool(retrieval_float_metadata["retrieved_has_float_like_unit"]),
                    "evidence_contains_reference": bool(retrieval_float_metadata["evidence_contains_reference"]),
                    "answer_eval_ran": False,
                }
            )

        subset_rows: dict[str, dict[str, Any]] = {}
        for subset_name in sorted({name for label in subset_labels for name in _subset_memberships(label)}):
            filtered = [row for row in rows if bool(row.get(subset_name.replace("float_signal_mode::", "")))] if not subset_name.startswith("float_signal_mode::") else [
                row for row in rows if row["gold_float_signal_mode"] == subset_name.split("::", 1)[1]
            ]
            subset_rows[subset_name] = _aggregate_rows(filtered)

        method_rows[method.name] = rows
        method_summaries.append(
            {
                "representation_mode": representation_mode,
                "method": method.name,
                "overall": _aggregate_rows(rows),
                "subset_metrics": subset_rows,
            }
        )

    structure_corpus_summary: dict[str, Any] = {
        "doc_count": len(context["structure_docs"]),
        "link_count": sum(int(doc["metadata"]["link_count"]) for doc in context["structure_docs"].values()),
        "unit_type_counts": {},
    }
    for doc in context["structure_docs"].values():
        for unit_type, count in doc["metadata"]["unit_type_counts"].items():
            structure_corpus_summary["unit_type_counts"][unit_type] = structure_corpus_summary["unit_type_counts"].get(unit_type, 0) + int(count)

    return {
        "metadata": {
            "dataset_path": str(dataset_path),
            "segmentation_mode": segmentation_mode,
            "representation_mode": representation_mode,
            "questions": len(qas),
            "structure_corpus_summary": structure_corpus_summary,
            "subset_counts": context.get("subset_labels") and {
                key: sum(bool(label.get(key)) for label in subset_labels)
                for key in ("adjacency_easy", "skip_local", "multi_span", "float_table", "float_direct", "float_reference", "float_adjacent_prose")
            },
        },
        "methods": method_summaries,
        "per_method_records": method_rows,
    }


def compare_representation_modes(
    *,
    dataset_path: str | Path,
    methods: list[QasperMethodConfig],
    segmentation_mode: str,
    representation_modes: list[str],
    max_questions: int,
    max_papers: int = 1_000_000,
) -> dict[str, Any]:
    payloads = {
        mode: evaluate_representation_mode(
            dataset_path=dataset_path,
            methods=methods,
            segmentation_mode=segmentation_mode,
            representation_mode=mode,
            max_questions=max_questions,
            max_papers=max_papers,
        )
        for mode in representation_modes
    }

    comparisons: list[dict[str, Any]] = []
    if len(representation_modes) >= 2:
        base_mode = representation_modes[0]
        compare_mode = representation_modes[1]
        for method in methods:
            base_summary = next(item for item in payloads[base_mode]["methods"] if item["method"] == method.name)
            compare_summary = next(item for item in payloads[compare_mode]["methods"] if item["method"] == method.name)
            comparisons.append(
                {
                    "method": method.name,
                    "base_representation": base_mode,
                    "compare_representation": compare_mode,
                    "overall_delta": {
                        metric: (
                            float(compare_summary["overall"][metric]) - float(base_summary["overall"][metric])
                            if base_summary["overall"][metric] is not None and compare_summary["overall"][metric] is not None
                            else None
                        )
                        for metric in ("seed_hit_rate", "evidence_hit_rate", "evidence_coverage_rate", "first_evidence_rank")
                    },
                    "subset_delta": {
                        subset_name: {
                            metric: (
                                float(compare_summary["subset_metrics"][subset_name][metric]) - float(base_summary["subset_metrics"][subset_name][metric])
                                if base_summary["subset_metrics"][subset_name][metric] is not None
                                and compare_summary["subset_metrics"][subset_name][metric] is not None
                                else None
                            )
                            for metric in ("seed_hit_rate", "evidence_hit_rate", "evidence_coverage_rate", "first_evidence_rank")
                        }
                        for subset_name in compare_summary["subset_metrics"]
                    },
                }
            )

    return {
        "metadata": {
            "dataset_path": str(dataset_path),
            "segmentation_mode": segmentation_mode,
            "representation_modes": representation_modes,
            "max_questions": max_questions,
            "methods": [method.name for method in methods],
        },
        "payloads_by_representation": payloads,
        "comparisons": comparisons,
    }


def flatten_per_question_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for rep_payload in payload["payloads_by_representation"].values():
        for method_name, method_rows in rep_payload["per_method_records"].items():
            for row in method_rows:
                rows.append(dict(row))
    rows.sort(key=lambda row: (row["paper_id"], row["question_id"], row["representation_mode"], row["retrieval_method"]))
    return rows


def build_structure_repr_markdown(title: str, payload: dict[str, Any], *, focus_subsets: list[str] | None = None) -> str:
    focus = focus_subsets or list(TARGET_SUBSETS)
    lines = [
        f"# {title}",
        "",
        f"- dataset_path: `{payload['metadata']['dataset_path']}`",
        f"- segmentation_mode: `{payload['metadata']['segmentation_mode']}`",
        f"- representation_modes: `{', '.join(payload['metadata']['representation_modes'])}`",
        f"- methods: `{', '.join(payload['metadata']['methods'])}`",
        f"- max_questions: `{payload['metadata']['max_questions']}`",
        "",
        "## Overall",
        "",
    ]

    for rep_mode, rep_payload in payload["payloads_by_representation"].items():
        corpus = rep_payload["metadata"]["structure_corpus_summary"]
        lines.extend(
            [
                f"### {rep_mode}",
                "",
                f"- unit_type_counts: `{json.dumps(corpus['unit_type_counts'], sort_keys=True)}`",
                f"- link_count: `{corpus['link_count']}`",
                "",
            ]
        )
        for method_summary in rep_payload["methods"]:
            overall = method_summary["overall"]
            lines.append(
                f"- `{method_summary['method']}`: seed-hit `{overall['seed_hit_rate']:.4f}`, "
                f"evidence-hit `{overall['evidence_hit_rate']:.4f}`, coverage `{overall['evidence_coverage_rate']:.4f}`, "
                f"first-rank `{overall['first_evidence_rank']:.4f}`" if overall["first_evidence_rank"] is not None else
                f"- `{method_summary['method']}`: seed-hit `{overall['seed_hit_rate']:.4f}`, evidence-hit `{overall['evidence_hit_rate']:.4f}`, coverage `{overall['evidence_coverage_rate']:.4f}`, first-rank `n/a`"
            )
        lines.append("")

    if payload["comparisons"]:
        lines.extend(["## Deltas", ""])
        for comparison in payload["comparisons"]:
            delta = comparison["overall_delta"]
            lines.append(
                f"- `{comparison['method']}` {comparison['base_representation']} -> {comparison['compare_representation']}: "
                f"seed-hit `{delta['seed_hit_rate']:+.4f}`, evidence-hit `{delta['evidence_hit_rate']:+.4f}`, "
                f"coverage `{delta['evidence_coverage_rate']:+.4f}`, first-rank "
                f"`{delta['first_evidence_rank']:+.4f}`" if delta["first_evidence_rank"] is not None else
                f"- `{comparison['method']}` {comparison['base_representation']} -> {comparison['compare_representation']}: "
                f"seed-hit `{delta['seed_hit_rate']:+.4f}`, evidence-hit `{delta['evidence_hit_rate']:+.4f}`, coverage `{delta['evidence_coverage_rate']:+.4f}`, first-rank `n/a`"
            )
        lines.append("")

    lines.extend(["## Targeted Subsets", ""])
    for subset_name in focus:
        lines.append(f"### {subset_name}")
        lines.append("")
        for rep_mode, rep_payload in payload["payloads_by_representation"].items():
            for method_summary in rep_payload["methods"]:
                row = method_summary["subset_metrics"].get(subset_name, {"queries": 0, "seed_hit_rate": 0.0, "evidence_hit_rate": 0.0, "evidence_coverage_rate": 0.0, "first_evidence_rank": None})
                first_rank_text = f"{row['first_evidence_rank']:.4f}" if row["first_evidence_rank"] is not None else "n/a"
                lines.append(
                    f"- `{rep_mode}` / `{method_summary['method']}`: queries `{row['queries']}`, seed-hit `{row['seed_hit_rate']:.4f}`, "
                    f"evidence-hit `{row['evidence_hit_rate']:.4f}`, coverage `{row['evidence_coverage_rate']:.4f}`, first-rank `{first_rank_text}`"
                )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def write_json(path: str | Path, payload: Any) -> None:
    atomic_write_json(path, payload)


def write_markdown(path: str | Path, content: str) -> None:
    atomic_write_text(path, content)


def write_per_question_csv(path: str | Path, rows: list[dict[str, Any]]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = output_path.with_suffix(output_path.suffix + ".tmp")
    fieldnames = [
        "paper_id",
        "question_id",
        "question",
        "representation_mode",
        "retrieval_method",
        "seed_hit",
        "evidence_hit",
        "evidence_coverage",
        "first_evidence_rank",
        "question_type",
        "adjacency_easy",
        "skip_local",
        "multi_span",
        "float_table",
        "float_direct",
        "float_reference",
        "float_adjacent_prose",
        "gold_float_signal_mode",
        "gold_matched_unit_types",
        "retrieved_float_signal_mode",
        "retrieved_matched_unit_types",
        "retrieved_has_caption_unit",
        "retrieved_has_inline_ref_unit",
        "retrieved_has_float_like_unit",
        "evidence_contains_reference",
        "answer_eval_ran",
    ]
    with tmp_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    if output_path.exists():
        output_path.unlink()
    tmp_path.replace(output_path)
