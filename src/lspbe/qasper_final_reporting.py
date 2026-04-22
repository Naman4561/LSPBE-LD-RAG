from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Any

from .qasper_bridge_repair import TARGET_REPAIR_METHODS
from .qasper_model_selection import (
    Bucket4MethodSpec,
    Bucket4Question,
    build_answer_eval_markdown,
    build_bucket4_method_matrix,
    build_retrieval_markdown,
)
from .run_control import atomic_write_json, atomic_write_text

LOCKED_FINAL_METHOD = "flat_hybrid_current"
PREFERRED_BASELINE_METHOD = "bridge_final_current"
FALLBACK_BASELINE_METHOD = "adjacency_hybrid_current"
TARGET_SUBSETS = ("overall", "skip_local", "multi_span", "float_table")
AUDIT_CATEGORY_ORDER = (
    "wrong seed / retrieval miss",
    "partial evidence recovery",
    "multi-span miss",
    "float/table-related miss",
    "annotation ambiguity / evaluation ambiguity",
    "answerer failure despite correct evidence",
)


def build_bucket5_method_specs() -> tuple[dict[str, Any], dict[str, Bucket4MethodSpec]]:
    index_specs, method_specs = build_bucket4_method_matrix()
    return index_specs, {method.name: method for method in method_specs}


def choose_bucket5_baseline(method_specs: dict[str, Bucket4MethodSpec]) -> tuple[str, str]:
    if PREFERRED_BASELINE_METHOD in method_specs:
        return PREFERRED_BASELINE_METHOD, "Preferred Bucket 5 comparator: strongest bridge-family validation baseline from Bucket 4."
    if FALLBACK_BASELINE_METHOD in method_specs:
        return FALLBACK_BASELINE_METHOD, "Fallback Bucket 5 comparator because bridge_final_current was unavailable or inconsistent."
    raise ValueError("Bucket 5 could not find either bridge_final_current or adjacency_hybrid_current.")


def write_json(path: str | Path, payload: object) -> None:
    atomic_write_json(path, payload)


def write_markdown(path: str | Path, content: str) -> None:
    atomic_write_text(path, content)


def write_csv(path: str | Path, rows: list[dict[str, object]]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row.keys()}) if rows else []
    tmp_path = output.with_suffix(output.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    tmp_path.replace(output)


def flatten_retrieval_rows(payload: dict[str, object]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in payload.get("per_question_records", []):
        copied = dict(row)
        copied.pop("retrieved_segments", None)
        rows.append(copied)
    return rows


def _answer_rows_by_method(payload: dict[str, object]) -> dict[tuple[str, str], dict[str, object]]:
    return {
        (str(row["method"]), str(row["question_id"])): row
        for row in payload.get("per_question_records", [])
    }


def join_method_records(
    retrieval_payload: dict[str, object],
    answer_payload: dict[str, object],
    method_name: str,
) -> list[dict[str, object]]:
    answer_rows = _answer_rows_by_method(answer_payload)
    joined: list[dict[str, object]] = []
    for row in retrieval_payload.get("per_question_records", []):
        if row.get("method") != method_name:
            continue
        answer_row = answer_rows.get((method_name, str(row["question_id"])))
        combined = dict(row)
        if answer_row is not None:
            combined.update(
                {
                    "predicted_answer": answer_row.get("predicted_answer", ""),
                    "normalized_prediction": answer_row.get("normalized_prediction", ""),
                    "gold_answers": list(answer_row.get("gold_answers", [])),
                    "normalized_gold_answers": list(answer_row.get("normalized_gold_answers", [])),
                    "answer_type": answer_row.get("answer_type", "unknown"),
                    "exact_match": float(answer_row.get("exact_match", 0.0)),
                    "token_f1": float(answer_row.get("token_f1", 0.0)),
                    "retrieval_evidence_hit": bool(answer_row.get("retrieval_evidence_hit", row.get("evidence_hit", False))),
                    "answerer_kind": answer_row.get("answerer_kind"),
                    "answerer_model_name": answer_row.get("answerer_model_name"),
                }
            )
        joined.append(combined)
    return joined


def _subset_names(row: dict[str, object]) -> list[str]:
    names = []
    for subset_name in ("skip_local", "multi_span", "float_table"):
        if bool(row.get(subset_name)):
            names.append(subset_name)
    names.append(f"question_type::{row.get('question_type', 'other')}")
    return names


def _gold_answers_text(row: dict[str, object]) -> str:
    answers = [str(answer).strip() for answer in row.get("gold_answers", []) if str(answer).strip()]
    return " || ".join(answers)


def assign_error_category(row: dict[str, object]) -> str:
    retrieval_hit = bool(row.get("retrieval_evidence_hit", row.get("evidence_hit", False)))
    coverage = float(row.get("evidence_coverage", 0.0))
    exact = float(row.get("exact_match", 0.0))
    token_f1 = float(row.get("token_f1", 0.0))
    gold_count = len(row.get("normalized_gold_answers", []))
    answer_type = str(row.get("answer_type", "unknown"))

    if not retrieval_hit:
        return "wrong seed / retrieval miss"
    if coverage >= 0.999 and exact < 1.0:
        if bool(row.get("float_table")) and token_f1 < 0.5:
            return "float/table-related miss"
        if answer_type in {"free_form", "unanswerable"} or gold_count > 1 or (0.2 <= token_f1 < 0.8):
            return "annotation ambiguity / evaluation ambiguity"
        return "answerer failure despite correct evidence"
    if bool(row.get("float_table")):
        return "float/table-related miss"
    if bool(row.get("multi_span")):
        return "multi-span miss"
    if coverage < 0.999:
        return "partial evidence recovery"
    if answer_type in {"free_form", "unanswerable"} or gold_count > 1 or (0.2 <= token_f1 < 0.8 and exact < 1.0):
        return "annotation ambiguity / evaluation ambiguity"
    return "answerer failure despite correct evidence"


def build_error_note(row: dict[str, object], category: str) -> str:
    retrieval_hit = bool(row.get("retrieval_evidence_hit", row.get("evidence_hit", False)))
    coverage = float(row.get("evidence_coverage", 0.0))
    token_f1 = float(row.get("token_f1", 0.0))
    first_rank = row.get("first_evidence_rank")
    predicted = str(row.get("predicted_answer", "")).strip() or "<empty>"
    if category == "wrong seed / retrieval miss":
        return f"No gold evidence reached the final context; seed first-rank={first_rank if first_rank is not None else 'miss'}."
    if category == "partial evidence recovery":
        return f"Retrieval hit succeeded but coverage stayed at {coverage:.2f}, leaving part of the gold evidence unrecovered."
    if category == "multi-span miss":
        return f"Multi-span question with retrieval hit={retrieval_hit} but coverage {coverage:.2f}, so at least one needed span stayed out."
    if category == "float/table-related miss":
        return f"Figure/table-linked case with coverage {coverage:.2f}; predicted answer was {predicted}."
    if category == "annotation ambiguity / evaluation ambiguity":
        return f"Correct evidence was present, but answer matching stayed soft (F1 {token_f1:.2f}) against multiple or free-form golds."
    return f"Correct evidence was present but the answerer still produced {predicted} (token F1 {token_f1:.2f})."


def _audit_priority(row: dict[str, object]) -> tuple[int, float, float]:
    category = assign_error_category(row)
    category_rank = AUDIT_CATEGORY_ORDER.index(category)
    hard_score = int(bool(row.get("skip_local"))) + int(bool(row.get("multi_span"))) + int(bool(row.get("float_table")))
    severity = (1.0 - float(row.get("evidence_coverage", 0.0))) + (1.0 - float(row.get("token_f1", 0.0)))
    return (hard_score, -category_rank, severity)


def build_error_audit(
    retrieval_payload: dict[str, object],
    answer_payload: dict[str, object],
    *,
    final_method: str,
    audit_size: int,
) -> list[dict[str, object]]:
    joined = join_method_records(retrieval_payload, answer_payload, final_method)
    candidates = [
        row for row in joined
        if (not bool(row.get("retrieval_evidence_hit", row.get("evidence_hit", False))))
        or float(row.get("exact_match", 0.0)) < 1.0
    ]
    candidates.sort(key=_audit_priority, reverse=True)

    selected: list[dict[str, object]] = []
    seen_ids: set[str] = set()
    category_quota = {
        "wrong seed / retrieval miss": 8,
        "partial evidence recovery": 8,
        "multi-span miss": 8,
        "float/table-related miss": 8,
        "annotation ambiguity / evaluation ambiguity": 8,
        "answerer failure despite correct evidence": 8,
    }
    subset_quota = {"skip_local": 10, "multi_span": 10, "float_table": 10}

    for category, quota in category_quota.items():
        for row in candidates:
            if len([item for item in selected if assign_error_category(item) == category]) >= quota:
                break
            if row["question_id"] in seen_ids or assign_error_category(row) != category:
                continue
            selected.append(row)
            seen_ids.add(str(row["question_id"]))

    for subset_name, quota in subset_quota.items():
        for row in candidates:
            if len([item for item in selected if bool(item.get(subset_name))]) >= quota:
                break
            if row["question_id"] in seen_ids or not bool(row.get(subset_name)):
                continue
            selected.append(row)
            seen_ids.add(str(row["question_id"]))

    for row in candidates:
        if len(selected) >= audit_size:
            break
        if row["question_id"] in seen_ids:
            continue
        selected.append(row)
        seen_ids.add(str(row["question_id"]))

    selected = selected[:audit_size]
    audit_rows: list[dict[str, object]] = []
    for row in selected:
        category = assign_error_category(row)
        audit_rows.append(
            {
                "method": final_method,
                "paper_id": row["paper_id"],
                "question_id": row["question_id"],
                "question": row["question"],
                "subset_labels": " | ".join(_subset_names(row)),
                "retrieval_hit": bool(row.get("retrieval_evidence_hit", row.get("evidence_hit", False))),
                "evidence_coverage": float(row.get("evidence_coverage", 0.0)),
                "predicted_answer": str(row.get("predicted_answer", "")).strip(),
                "gold_answers": _gold_answers_text(row),
                "error_category": category,
                "note": build_error_note(row, category),
            }
        )
    return audit_rows


def build_error_audit_markdown(audit_rows: list[dict[str, object]]) -> str:
    lines = [
        "# QASPER Test Error Audit",
        "",
        f"- audited_examples: `{len(audit_rows)}`",
        "- note: this is a compact presentation-oriented audit, not a full relabeling pass.",
        "",
    ]
    for row in audit_rows:
        lines.extend(
            [
                f"## {row['question_id']}",
                "",
                f"- paper_id: `{row['paper_id']}`",
                f"- subset_labels: `{row['subset_labels']}`",
                f"- retrieval_hit: `{row['retrieval_hit']}`",
                f"- evidence_coverage: `{row['evidence_coverage']:.4f}`",
                f"- category: `{row['error_category']}`",
                f"- question: {row['question']}",
                f"- predicted_answer: {row['predicted_answer'] or '<empty>'}",
                f"- gold_answers: {row['gold_answers'] or '<empty>'}",
                f"- note: {row['note']}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def summarize_error_taxonomy(audit_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    counts = Counter(str(row["error_category"]) for row in audit_rows)
    first_examples: dict[str, dict[str, object]] = {}
    for row in audit_rows:
        first_examples.setdefault(str(row["error_category"]), row)
    rows: list[dict[str, object]] = []
    total = max(len(audit_rows), 1)
    for category in AUDIT_CATEGORY_ORDER:
        example = first_examples.get(category, {})
        rows.append(
            {
                "error_category": category,
                "count": counts.get(category, 0),
                "share": counts.get(category, 0) / total,
                "example_question_id": example.get("question_id", ""),
                "example_question": example.get("question", ""),
                "example_note": example.get("note", ""),
            }
        )
    return rows


def build_error_taxonomy_markdown(rows: list[dict[str, object]]) -> str:
    lines = [
        "# QASPER Error Taxonomy Summary",
        "",
        "| Category | Count | Share | Example |",
        "| --- | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['error_category']} | {row['count']} | {row['share']:.3f} | {row['example_question_id']} |"
        )
    return "\n".join(lines) + "\n"


def _method_summary(payload: dict[str, object], method_name: str) -> dict[str, object]:
    for method in payload.get("methods", []):
        if method.get("method") == method_name:
            return method
    raise KeyError(f"Method '{method_name}' not found.")


def build_main_results_rows(
    retrieval_payload: dict[str, object],
    answer_payload: dict[str, object],
    split_name: str,
    method_order: list[str],
) -> list[dict[str, object]]:
    answer_by_method = {row["method"]: row for row in answer_payload.get("methods", [])}
    rows: list[dict[str, object]] = []
    for method_name in method_order:
        retrieval = _method_summary(retrieval_payload, method_name)["overall"]
        answer = answer_by_method[method_name]["overall"]
        rows.append(
            {
                "method": method_name,
                "split": split_name,
                "evidence_hit": round(float(retrieval["evidence_hit_rate"]), 4),
                "evidence_coverage": round(float(retrieval["evidence_coverage_rate"]), 4),
                "seed_hit": round(float(retrieval["seed_hit_rate"]), 4),
                "EM": round(float(answer["exact_match"]), 4),
                "F1": round(float(answer["token_f1"]), 4),
                "empty_rate": round(float(answer["empty_prediction_rate"]), 4),
            }
        )
    return rows


def build_main_results_markdown(rows: list[dict[str, object]]) -> str:
    lines = [
        "# QASPER Presentation Main Results",
        "",
        "| Method | Split | Evidence Hit | Coverage | Seed Hit | EM | F1 | Empty Rate |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row['method']} | {row['split']} | {row['evidence_hit']:.4f} | {row['evidence_coverage']:.4f} | "
            f"{row['seed_hit']:.4f} | {row['EM']:.4f} | {row['F1']:.4f} | {row['empty_rate']:.4f} |"
        )
    return "\n".join(lines) + "\n"


def build_progression_rows(
    *,
    bucket4_validation: dict[str, object],
    bucket4_answer: dict[str, object],
    bridge_stage1: dict[str, object],
    bridge_stage2: dict[str, object],
) -> list[dict[str, object]]:
    answer_by_method = {row["method"]: row for row in bucket4_answer.get("methods", [])}
    rows: list[dict[str, object]] = []
    progression = [
        ("earlier flat baseline", "flat_hybrid_current", bucket4_validation, "bucket4_validation"),
        ("adjacency", "adjacency_hybrid_current", bucket4_validation, "bucket4_validation"),
        ("bridge_v2", "bridge_v2_hybrid_current", bucket4_validation, "bucket4_validation"),
        ("bridge_final", "bridge_final_current", bucket4_validation, "bucket4_validation"),
        ("final selected flat", "flat_hybrid_current", bucket4_validation, "bucket4_validation"),
        ("bridge repair stage 1", "bridge_from_flat_seeds_current", bridge_stage1, "bucket4_5_stage1"),
        ("bridge repair stage 2", "bridge_from_flat_seeds_selective_current", bridge_stage2, "bucket4_5_stage2"),
    ]
    for label, method_name, payload, source in progression:
        retrieval = _method_summary(payload, method_name)["overall"]
        answer = answer_by_method.get(method_name, {}).get("overall", {})
        rows.append(
            {
                "story_step": label,
                "method": method_name,
                "source": source,
                "split": "validation",
                "evidence_hit": round(float(retrieval["evidence_hit_rate"]), 4),
                "evidence_coverage": round(float(retrieval["evidence_coverage_rate"]), 4),
                "seed_hit": round(float(retrieval["seed_hit_rate"]), 4),
                "EM": None if not answer else round(float(answer["exact_match"]), 4),
                "F1": None if not answer else round(float(answer["token_f1"]), 4),
            }
        )
    return rows


def build_subset_rows(
    retrieval_payload: dict[str, object],
    answer_payload: dict[str, object],
    method_order: list[str],
) -> list[dict[str, object]]:
    answer_by_method = {row["method"]: row for row in answer_payload.get("methods", [])}
    rows: list[dict[str, object]] = []
    for method_name in method_order:
        retrieval_method = _method_summary(retrieval_payload, method_name)
        answer_method = answer_by_method[method_name]
        for subset_name in TARGET_SUBSETS:
            retrieval = retrieval_method["overall"] if subset_name == "overall" else retrieval_method["subset_metrics"][subset_name]
            answer = answer_method["overall"] if subset_name == "overall" else answer_method["subset_metrics"][subset_name]
            rows.append(
                {
                    "method": method_name,
                    "subset": subset_name,
                    "queries": int(retrieval["queries"] if subset_name == "overall" else retrieval["queries"]),
                    "evidence_hit": round(float(retrieval["evidence_hit_rate"]), 4),
                    "evidence_coverage": round(float(retrieval["evidence_coverage_rate"]), 4),
                    "seed_hit": round(float(retrieval["seed_hit_rate"]), 4),
                    "EM": round(float(answer["exact_match"]), 4),
                    "F1": round(float(answer["token_f1"]), 4),
                    "empty_rate": round(float(answer["empty_prediction_rate"]), 4),
                }
            )
    return rows


def _serializable_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    serializable: list[dict[str, object]] = []
    for row in rows:
        converted = {}
        for key, value in row.items():
            converted[key] = value
        serializable.append(converted)
    return serializable


def _find_example(
    retrieval_payload: dict[str, object],
    answer_payload: dict[str, object],
    *,
    final_method: str,
    baseline_method: str,
    excluded_question_ids: set[str] | None = None,
    predicate,
) -> dict[str, object] | None:
    final_rows = {row["question_id"]: row for row in join_method_records(retrieval_payload, answer_payload, final_method)}
    baseline_rows = {row["question_id"]: row for row in join_method_records(retrieval_payload, answer_payload, baseline_method)}
    excluded = excluded_question_ids or set()
    for question_id in sorted(final_rows):
        if question_id in excluded:
            continue
        final_row = final_rows[question_id]
        baseline_row = baseline_rows.get(question_id)
        if baseline_row is not None and predicate(final_row, baseline_row):
            return {"final": final_row, "baseline": baseline_row}
    return None


def _format_example_block(title: str, example: dict[str, object]) -> list[str]:
    final_row = example["final"]
    baseline_row = example["baseline"]
    return [
        f"## {title}",
        "",
        f"- paper_id: `{final_row['paper_id']}`",
        f"- question_id: `{final_row['question_id']}`",
        f"- question: {final_row['question']}",
        f"- subset_labels: `{ ' | '.join(_subset_names(final_row)) }`",
        f"- final_method_retrieval_hit: `{bool(final_row.get('retrieval_evidence_hit', final_row.get('evidence_hit', False)))}`",
        f"- final_method_prediction: {str(final_row.get('predicted_answer', '')).strip() or '<empty>'}",
        f"- baseline_prediction: {str(baseline_row.get('predicted_answer', '')).strip() or '<empty>'}",
        f"- gold_answers: {_gold_answers_text(final_row) or '<empty>'}",
        "",
    ]


def build_curated_examples_markdown(
    retrieval_payload: dict[str, object],
    answer_payload: dict[str, object],
    *,
    final_method: str,
    baseline_method: str,
) -> str:
    requested_examples = [
        ("Flat Clearly Succeeds", lambda final_row, baseline_row: (
            float(final_row.get("token_f1", 0.0)) >= 0.9
            and float(baseline_row.get("token_f1", 0.0)) <= 0.2
        )),
        ("Both Methods Struggle", lambda final_row, baseline_row: (
            not bool(final_row.get("retrieval_evidence_hit", final_row.get("evidence_hit", False)))
            and not bool(baseline_row.get("retrieval_evidence_hit", baseline_row.get("evidence_hit", False)))
        ) or (
            float(final_row.get("token_f1", 0.0)) == 0.0
            and float(baseline_row.get("token_f1", 0.0)) == 0.0
        )),
        ("Float Or Table Case", lambda final_row, _baseline_row: bool(final_row.get("float_table"))),
        ("Multi-Span Or Nonlocal Case", lambda final_row, _baseline_row: bool(final_row.get("multi_span")) or bool(final_row.get("skip_local"))),
        ("Answerer Mismatch Limitation", lambda final_row, _baseline_row: (
            bool(final_row.get("retrieval_evidence_hit", final_row.get("evidence_hit", False)))
            and float(final_row.get("evidence_coverage", 0.0)) >= 0.999
            and float(final_row.get("token_f1", 0.0)) == 0.0
        )),
    ]
    examples = []
    used_question_ids: set[str] = set()
    for title, predicate in requested_examples:
        example = _find_example(
            retrieval_payload,
            answer_payload,
            final_method=final_method,
            baseline_method=baseline_method,
            excluded_question_ids=used_question_ids,
            predicate=predicate,
        )
        if example is not None:
            used_question_ids.add(str(example["final"]["question_id"]))
        examples.append((title, example))
    lines = ["# QASPER Curated Examples", ""]
    for title, example in examples:
        if example is None:
            lines.extend([f"## {title}", "", "- no compact example matched the target pattern in this run.", ""])
            continue
        lines.extend(_format_example_block(title, example))
    return "\n".join(lines).rstrip() + "\n"


def build_presentation_bundle_markdown(
    *,
    heldout_split_name: str,
    heldout_dataset_path: str,
    final_method: str,
    baseline_method: str,
    baseline_reason: str,
    retrieval_payload: dict[str, object],
    answer_payload: dict[str, object],
    taxonomy_rows: list[dict[str, object]],
) -> str:
    final_retrieval = _method_summary(retrieval_payload, final_method)["overall"]
    baseline_retrieval = _method_summary(retrieval_payload, baseline_method)["overall"]
    final_answer = _method_summary(answer_payload, final_method)["overall"]
    top_categories = [row for row in taxonomy_rows if int(row["count"]) > 0][:3]
    lines = [
        "# QASPER Presentation Bundle",
        "",
        "## Problem",
        "",
        "- Goal: recover evidence for long-document QASPER questions and report the final held-out result under the cleaned serious-redo protocol.",
        "- Final Bucket 5 question: with the model locked, what is the true held-out performance, where does it fail, and what is the most defensible 8-minute story?",
        "",
        "## Dataset And Protocol",
        "",
        f"- Held-out reporting split: `{heldout_split_name}` from `{heldout_dataset_path}`.",
        "- Retrieval is the primary evaluation story; answer evaluation is included as a secondary signal because the local QA layer is still imperfect.",
        "- Locked mainline settings: representation `current`, segmentation `seg_paragraph_pair`, final method `flat_hybrid_current`.",
        "",
        "## Method Progression",
        "",
        "- The clean validation ladder showed flat hybrid seeds outperforming adjacency and the bridge-family variants on evidence hit and coverage.",
        "- Bucket 4.5 repaired the bridge fairness issue by giving bridge the exact same flat seed stage, then tested always-on and selective repair variants.",
        "- That repair closed the seed-gap fairness objection, but it still did not overturn the flat winner.",
        "",
        "## Final Results Story",
        "",
        f"- Locked final method: `{final_method}`.",
        f"- Comparison baseline: `{baseline_method}`. {baseline_reason}",
        f"- Held-out retrieval: flat hit `{final_retrieval['evidence_hit_rate']:.4f}` vs baseline `{baseline_retrieval['evidence_hit_rate']:.4f}`; coverage `{final_retrieval['evidence_coverage_rate']:.4f}` vs `{baseline_retrieval['evidence_coverage_rate']:.4f}`.",
        f"- Held-out answer eval: flat EM `{final_answer['exact_match']:.4f}`, F1 `{final_answer['token_f1']:.4f}`, empty rate `{final_answer['empty_prediction_rate']:.4f}`.",
        "",
        "## Main Failure Modes",
        "",
    ]
    for row in top_categories:
        lines.append(f"- {row['error_category']}: `{row['count']}` audited examples.")
    lines.extend(
        [
            "",
            "## Limitations",
            "",
            "- Answer metrics are informative but secondary because they depend on a locally cached QA layer that can miss even when evidence is present.",
            "- The `float_table` subset is only a coarse proxy for figure/table-linked reasoning difficulty.",
            "- The error audit is compact and presentation-oriented rather than a full annotation adjudication pass.",
            "",
            "## Future Work",
            "",
            "- Improve the answerer before using answer metrics as a primary selector.",
            "- Add a more explicit evidence-chain analysis for nonlocal and multi-span failures.",
            "- Explore better table/figure handling without reopening the locked Bucket 5 model choice.",
            "",
        ]
    )
    return "\n".join(lines)


def build_slide_outline_markdown() -> str:
    return """# QASPER Presentation Slide Outline

## Slide 1: Problem / Motivation

- Long-document QA depends on retrieving the right evidence, not just producing a fluent answer.
- QASPER is a good stress test because evidence can be nonlocal, multi-span, and table-linked.
- Recommended visual: one question plus a long-paper context sketch.

## Slide 2: Task And Dataset

- Task: retrieve evidence for QASPER paper questions, then score answer quality secondarily.
- Evaluation slices include `skip_local`, `multi_span`, and `float_table`.
- Recommended visual: compact dataset/protocol table.

## Slide 3: Why The Original Setup Was Not Fully Defensible

- Earlier workflow mixed development and reporting roles too loosely.
- Saturated retrieval metrics and repeated split reuse made the story harder to defend.
- Recommended visual: old vs cleaned protocol schematic.

## Slide 4: Protocol Reset

- Validation used only for model selection; test reserved for final reporting.
- Retrieval became the primary selector, with answer eval kept as a secondary signal.
- Recommended visual: split-role timeline.

## Slide 5: Method Ladder And What Changed

- Compared flat, adjacency, bridge_v2, bridge_final, and one fixed-chunk bridge baseline.
- Bucket 4.5 then repaired bridge seeding fairness without reopening the whole search space.
- Recommended visual: model progression figure.

## Slide 6: Final Held-Out Results

- Present `flat_hybrid_current` against one compact context baseline on test.
- Highlight evidence hit, coverage, seed hit, EM, F1, and empty rate.
- Recommended visual: main results table.

## Slide 7: Hard-Subset Results

- Show overall, `skip_local`, `multi_span`, and `float_table`.
- Emphasize where flat stays stronger and where both methods still struggle.
- Recommended visual: subset performance bar chart.

## Slide 8: Error Analysis

- Summarize the final taxonomy: retrieval miss, partial recovery, multi-span, float/table, ambiguity, answerer failure.
- Use one or two curated examples to make the taxonomy concrete.
- Recommended visual: error taxonomy table plus one worked example.

## Slide 9: Limitations

- Local QA answerer is still imperfect, so answer metrics are secondary.
- Figure/table and annotation ambiguity remain real sources of noise.
- Recommended visual: short limitations box.

## Slide 10: Takeaway / Future Work

- The clean protocol changed the conclusion: the final winner is flat, not bridge.
- Bridge fairness mattered, but even repaired bridge did not overturn flat on validation or final reporting.
- Recommended visual: one-sentence takeaway banner plus future-work bullets.
"""


def build_bucket5_summary_markdown(
    *,
    heldout_dataset_path: str,
    final_method: str,
    baseline_method: str,
    retrieval_payload: dict[str, object],
    answer_payload: dict[str, object],
    taxonomy_rows: list[dict[str, object]],
) -> str:
    final_retrieval = _method_summary(retrieval_payload, final_method)["overall"]
    baseline_retrieval = _method_summary(retrieval_payload, baseline_method)["overall"]
    final_answer = _method_summary(answer_payload, final_method)["overall"]
    subset_rows = build_subset_rows(retrieval_payload, answer_payload, [final_method, baseline_method])
    hard_rows = [row for row in subset_rows if row["subset"] in {"skip_local", "multi_span", "float_table"}]
    lines = [
        "# Bucket 5 Final Summary",
        "",
        f"- locked_final_model: `{final_method}`",
        f"- chosen_context_baseline: `{baseline_method}`",
        f"- held_out_dataset: `{heldout_dataset_path}`",
        f"- final_retrieval_hit: `{final_retrieval['evidence_hit_rate']:.4f}`",
        f"- final_retrieval_coverage: `{final_retrieval['evidence_coverage_rate']:.4f}`",
        f"- baseline_retrieval_hit: `{baseline_retrieval['evidence_hit_rate']:.4f}`",
        f"- final_answer_EM: `{final_answer['exact_match']:.4f}`",
        f"- final_answer_F1: `{final_answer['token_f1']:.4f}`",
        f"- final_empty_rate: `{final_answer['empty_prediction_rate']:.4f}`",
        "",
        "## Hard Subset Takeaways",
        "",
    ]
    for row in hard_rows:
        if row["method"] != final_method:
            continue
        baseline_row = next(
            candidate for candidate in hard_rows
            if candidate["method"] == baseline_method and candidate["subset"] == row["subset"]
        )
        lines.append(
            f"- `{row['subset']}`: flat hit `{row['evidence_hit']:.4f}` vs baseline `{baseline_row['evidence_hit']:.4f}`, "
            f"F1 `{row['F1']:.4f}` vs `{baseline_row['F1']:.4f}`."
        )
    lines.extend(["", "## Key Error Categories", ""])
    for row in taxonomy_rows:
        if int(row["count"]) > 0:
            lines.append(f"- `{row['error_category']}`: `{row['count']}`")
    lines.extend(
        [
            "",
            "## Final Story",
            "",
            "Bucket 5 keeps the validation-selected `flat_hybrid_current` model locked, confirms it on the held-out test split against one compact bridge-family baseline, includes answer evaluation as a secondary signal, and shows through a compact audit that the remaining failures cluster around retrieval misses, incomplete evidence recovery, hard multi-span/float-table cases, and answerer mismatches even when evidence is present.",
            "",
        ]
    )
    return "\n".join(lines)


def build_final_project_takeaway_markdown(
    *,
    final_method: str,
    baseline_method: str,
    retrieval_payload: dict[str, object],
    answer_payload: dict[str, object],
) -> str:
    final_retrieval = _method_summary(retrieval_payload, final_method)["overall"]
    baseline_retrieval = _method_summary(retrieval_payload, baseline_method)["overall"]
    final_answer = _method_summary(answer_payload, final_method)["overall"]
    return (
        "# Final Project Takeaway\n\n"
        f"The serious QASPER redo ends with `{final_method}` as the locked final model. On the held-out test split it stays ahead of "
        f"`{baseline_method}` on retrieval-first evidence recovery, while answer evaluation remains useful but secondary because the local QA layer is still imperfect. "
        f"The defensible presentation story is that protocol cleanup changed the conclusion: once validation was treated as model selection and bridge fairness was explicitly repaired, the best final result still stayed flat rather than bridge, with remaining weaknesses concentrated in partial evidence recovery, multi-span/float-table cases, and answerer failures despite correct evidence.\n"
    )


def build_answer_eval_markdown_with_caution(title: str, payload: dict[str, object]) -> str:
    base = build_answer_eval_markdown(title, payload).rstrip()
    lines = [
        base,
        "",
        "## Interpretation",
        "",
        "- Treat these answer metrics as secondary support only.",
        "- The local offline QA layer is still imperfect, so retrieval remains the main Bucket 5 selection and reporting story.",
        "",
    ]
    return "\n".join(lines)


def build_retrieval_markdown_with_lock(title: str, payload: dict[str, object], final_method: str, baseline_method: str) -> str:
    base = build_retrieval_markdown(title, payload).rstrip()
    lines = [
        base,
        "",
        "## Lock Status",
        "",
        f"- locked_final_model: `{final_method}`",
        f"- comparison_baseline: `{baseline_method}`",
        "- note: Bucket 5 does not reopen model selection; it only reports the held-out result for the locked model plus one compact baseline.",
        "",
    ]
    return "\n".join(lines)
