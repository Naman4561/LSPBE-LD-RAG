#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

CURRENT_BUCKET1_DIR = ROOT / "artifacts" / "current" / "bucket1_protocol"
CURRENT_MANUAL_REVIEW_DIR = ROOT / "artifacts" / "current" / "manual_review"

from lspbe.qasper_protocol import build_document_text
from lspbe.segmentation import segment_document_with_mode
from lspbe.subsets import build_subset_label, local_regions, unique_evidence_units

SEGMENTATION_MODE = "paragraph_pair"
FLOAT_TABLE_PATTERN = re.compile(r"\b(?:figure|fig|table|tab|caption)\b|FIGREF|TABREF", re.IGNORECASE)


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_papers(path: Path) -> list[dict[str, object]]:
    raw = load_json(path)
    if isinstance(raw, dict):
        return list(raw.values())
    return list(raw)


def paper_lookup(papers: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    return {str(paper["paper_id"]): paper for paper in papers}


def label_lookup(labels_payload: dict[str, object]) -> dict[str, dict[str, object]]:
    return {str(label["qa_id"]): label for label in labels_payload["labels"]}


def evidence_match_sources(
    evidence_texts: list[str],
    matched_segments: list[dict[str, object]],
) -> dict[str, object]:
    evidence_hit = any(FLOAT_TABLE_PATTERN.search(text) for text in evidence_texts)
    segment_hit = any(bool(segment["float_table_signal"]) for segment in matched_segments)
    return {
        "evidence_text_regex_hit": evidence_hit,
        "matched_segment_regex_hit": segment_hit,
    }


def build_index(split_name: str, papers: list[dict[str, object]], labels_by_qa_id: dict[str, dict[str, object]] | None) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    for paper in papers:
        paper_id = str(paper["paper_id"])
        doc_text = build_document_text(list(paper.get("full_text", [])))
        segments = segment_document_with_mode(paper_id, doc_text, mode=SEGMENTATION_MODE)
        segment_by_id = {segment.segment_id: segment for segment in segments}
        for question_index, qa in enumerate(paper.get("qas", [])):
            qa_id = f"{paper_id}::q{question_index}"
            evidence_texts = []
            for answer in qa.get("answers", []):
                evidence_texts.extend(answer.get("answer", {}).get("evidence", []))
            evidence_texts = unique_evidence_units(evidence_texts)
            label = labels_by_qa_id.get(qa_id) if labels_by_qa_id else None
            if label is None:
                label = build_subset_label(
                    qa_id=qa_id,
                    doc_id=paper_id,
                    question=qa.get("question", ""),
                    evidence_texts=evidence_texts,
                    doc_segments=segments,
                )

            evidence_segment_ids = list(label.get("gold_evidence_segment_ids", []))
            regions = local_regions(set(evidence_segment_ids))
            matched_segments = []
            for segment_id in evidence_segment_ids:
                segment = segment_by_id.get(segment_id)
                if segment is None:
                    continue
                haystack = f"{segment.section}\n{segment.text}"
                matched_segments.append(
                    {
                        "segment_id": segment.segment_id,
                        "section": segment.section,
                        "text": segment.text,
                        "float_table_signal": bool(FLOAT_TABLE_PATTERN.search(haystack)),
                    }
                )
            region_lengths = [len(region) for region in regions]
            region_gaps = [
                regions[index + 1][0] - regions[index][-1]
                for index in range(len(regions) - 1)
            ]
            item = {
                "split": split_name,
                "paper_id": paper_id,
                "qa_id": qa_id,
                "question_id": qa_id,
                "question_text": qa.get("question", ""),
                "question_type": label["question_type"],
                "subset_labels": {
                    "adjacency_easy": bool(label["adjacency_easy"]),
                    "skip_local": bool(label["skip_local"]),
                    "multi_span": bool(label["multi_span"]),
                    "float_table": bool(label["float_table"]),
                },
                "gold_evidence_texts": evidence_texts,
                "gold_evidence_segment_ids": evidence_segment_ids,
                "gold_evidence_region_count": int(label["gold_evidence_region_count"]),
                "evidence_unit_count": int(label["evidence_unit_count"]),
                "local_regions": regions,
                "region_lengths": region_lengths,
                "region_gap_sizes": region_gaps,
                "max_evidence_gap": max(region_gaps) if region_gaps else 0,
                "matched_segments": matched_segments,
                "float_table_match_sources": evidence_match_sources(evidence_texts, matched_segments),
            }
            items.append(item)
    return items


def sample_category(
    items: list[dict[str, object]],
    used_ids: set[str],
    *,
    predicate,
    target_count: int,
    note: str,
) -> list[dict[str, object]]:
    chosen: list[dict[str, object]] = []
    for prefer_unused in (True, False):
        for split_name in ("validation", "train_fast50"):
            candidates = [
                item
                for item in items
                if item["split"] == split_name
                and predicate(item)
                and (not prefer_unused or item["qa_id"] not in used_ids)
            ]
            candidates.sort(
                key=lambda item: (
                    item["split"] != "validation",
                    item["paper_id"],
                    item["qa_id"],
                )
            )
            for item in candidates:
                if len(chosen) >= target_count:
                    break
                if prefer_unused and item["qa_id"] in used_ids:
                    continue
                if item["qa_id"] in {sample["qa_id"] for sample in chosen}:
                    continue
                sampled = dict(item)
                sampled["sample_note"] = note
                chosen.append(sampled)
                used_ids.add(item["qa_id"])
            if len(chosen) >= target_count:
                break
        if len(chosen) >= target_count:
            break
    return chosen


def build_markdown(sample_bundle: dict[str, object]) -> str:
    lines = [
        "# QASPER Subset Manual Review Sample",
        "",
        "Validation is preferred; `train_fast50` is only used as fallback.",
        "",
    ]
    for section_name in ("subset_categories", "question_type_categories"):
        heading = "Subset Labels" if section_name == "subset_categories" else "Question Type"
        lines.extend([f"## {heading}", ""])
        groups = sample_bundle[section_name]
        for category_name, items in groups.items():
            lines.extend([f"### {category_name}", ""])
            for item in items:
                labels = ", ".join(
                    name for name, value in item["subset_labels"].items() if value
                ) or "none"
                lines.extend(
                    [
                        f"- split: `{item['split']}`",
                        f"- paper_id: `{item['paper_id']}`",
                        f"- question_id: `{item['question_id']}`",
                        f"- question_type: `{item['question_type']}`",
                        f"- subset_labels: `{labels}`",
                        f"- gold_evidence_segment_ids: `{item['gold_evidence_segment_ids']}`",
                        f"- gold_evidence_region_count: `{item['gold_evidence_region_count']}`",
                        f"- local_regions: `{item['local_regions']}`",
                        f"- region_gap_sizes: `{item['region_gap_sizes']}`",
                        f"- float_table_match_sources: `{json.dumps(item['float_table_match_sources'], sort_keys=True)}`",
                        f"- why_this_was_sampled: {item['sample_note']}",
                        f"- question: {item['question_text']}",
                        "- gold_evidence_texts:",
                    ]
                )
                for evidence in item["gold_evidence_texts"]:
                    lines.append(f"  - {evidence}")
                lines.append("- matched_segments:")
                for segment in item["matched_segments"]:
                    lines.append(
                        f"  - segment `{segment['segment_id']}` | section `{segment['section']}` | "
                        f"float_table_signal `{segment['float_table_signal']}` | text: {segment['text']}"
                    )
                lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_checklist() -> str:
    return "\n".join(
        [
            "# QASPER Subset Manual Review Checklist",
            "",
            "## adjacency_easy",
            "",
            "- Should look like all gold evidence is inside one immediate local neighborhood.",
            "- Red flags: evidence ids spread across distant segments or multiple far-apart regions.",
            "",
            "## skip_local",
            "",
            "- Should include at least one distance-2-or-more jump between gold evidence segments.",
            "- Red flags: only one segment, or only tightly adjacent evidence despite the label.",
            "",
            "## multi_span",
            "",
            "- Should show two or more disjoint local evidence regions.",
            "- Red flags: all evidence sits in one continuous segment block.",
            "",
            "## float_table",
            "",
            "- Should show figure/table/caption style evidence or evidence-bearing segments with those markers.",
            "- Red flags: label fires only because of broad document context with no obvious table/figure signal in the evidence area.",
            "",
            "## question_type",
            "",
            "- Should match the first-token heuristic: boolean, what, how, which, or other.",
            "- Red flags: obvious mismatch between the question wording and the assigned coarse type.",
            "",
        ]
    ).rstrip() + "\n"


def main() -> int:
    validation_labels_payload = load_json(CURRENT_BUCKET1_DIR / "qasper_subset_labels_validation.json")
    validation_papers = load_papers(ROOT / "data" / "qasper_validation_full.json")
    train_fast50_papers = load_papers(ROOT / "data" / "qasper_train_fast50.json")

    validation_items = build_index(
        "validation",
        validation_papers,
        label_lookup(validation_labels_payload),
    )

    train_fast50_items = build_index(
        "train_fast50",
        train_fast50_papers,
        None,
    )

    items = validation_items + train_fast50_items
    used_ids: set[str] = set()

    def non_empty(item: dict[str, object]) -> bool:
        return bool(item["gold_evidence_segment_ids"])

    subset_categories = {
        "adjacency_easy": sample_category(
            items,
            used_ids,
            predicate=lambda item: non_empty(item) and item["subset_labels"]["adjacency_easy"],
            target_count=5,
            note="sampled as adjacency_easy positive example",
        ),
        "skip_local": sample_category(
            items,
            used_ids,
            predicate=lambda item: non_empty(item) and item["subset_labels"]["skip_local"],
            target_count=5,
            note="sampled as skip_local positive example",
        ),
        "multi_span": sample_category(
            items,
            used_ids,
            predicate=lambda item: non_empty(item) and item["subset_labels"]["multi_span"],
            target_count=5,
            note="sampled as multi_span positive example",
        ),
        "float_table": sample_category(
            items,
            used_ids,
            predicate=lambda item: non_empty(item) and item["subset_labels"]["float_table"],
            target_count=5,
            note="sampled as float_table positive example",
        ),
    }

    question_type_categories = {}
    for question_type in ("boolean", "what", "how", "which", "other"):
        question_type_categories[question_type] = sample_category(
            items,
            used_ids,
            predicate=lambda item, qt=question_type: non_empty(item) and item["question_type"] == qt,
            target_count=2,
            note=f"sampled as question_type={question_type} example",
        )

    sample_bundle = {
        "source_priority": ["validation", "train_fast50"],
        "subset_categories": subset_categories,
        "question_type_categories": question_type_categories,
    }

    write_json(CURRENT_MANUAL_REVIEW_DIR / "qasper_subset_manual_review_sample.json", sample_bundle)
    (CURRENT_MANUAL_REVIEW_DIR / "qasper_subset_manual_review_sample.md").write_text(
        build_markdown(sample_bundle),
        encoding="utf-8",
    )
    (CURRENT_MANUAL_REVIEW_DIR / "qasper_subset_manual_review_checklist.md").write_text(
        build_checklist(),
        encoding="utf-8",
    )

    print(json.dumps({key: {k: len(v) for k, v in value.items()} for key, value in sample_bundle.items() if isinstance(value, dict)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
