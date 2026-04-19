#!/usr/bin/env python3
"""Convert Hugging Face QASPER into the minimal JSON schema used by LSPBE MVE.

This script downloads one split from ``allenai/qasper`` via the ``datasets``
 library and writes a lightweight paper-centric JSON file shaped exactly for
 ``lspbe.mve.load_qasper_subset(...)``.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from itertools import zip_longest
from pathlib import Path
from typing import Any


def _string_list(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    return [value for value in values if isinstance(value, str)]


def is_obvious_evidence_artifact(text: str) -> bool:
    """Return True only for evidence strings that are almost certainly labels.

    This cleanup is intentionally narrow: we remove obvious annotation artifacts
    from evidence supervision, not from the paper text itself. The goal is to
    avoid making the benchmark artificially easier through aggressive corpus
    normalization while still dropping strings that are extremely likely to be
    non-prose labels.
    """

    stripped = text.strip()
    if not stripped:
        return False

    if stripped.startswith("FLOAT SELECTED:"):
        remainder = stripped.removeprefix("FLOAT SELECTED:").strip()
        if not remainder:
            return True
        if len(remainder.split()) <= 12 and not re.search(r"[.!?]", remainder):
            return True

    # Keep raw section names and messy labels by default. Only remove the most
    # obvious standalone figure/table labels with no prose attached.
    if len(stripped.split()) <= 6 and not re.search(r"[.!?]", stripped):
        if re.fullmatch(r"(Table|Figure|Fig\.|Appendix|Section)\s+[A-Za-z0-9.\-]+", stripped):
            return True

    return False


def clean_evidence_list(evidence_list: list[str]) -> tuple[list[str], dict[str, int]]:
    """Apply light evidence cleanup without rewriting the underlying corpus.

    We only trim whitespace, drop empty strings, remove exact duplicates within
    the same QA, and filter obvious label artifacts. We intentionally keep raw
    prose, citation placeholders, section names inside document text, and other
    messy QASPER content so the converted benchmark stays realistic.
    """

    cleaned: list[str] = []
    seen: set[str] = set()
    stats = {
        "raw_evidence": 0,
        "retained_evidence": 0,
        "removed_duplicates": 0,
        "removed_empty_or_artifact": 0,
    }

    for evidence in evidence_list:
        stats["raw_evidence"] += 1
        stripped = evidence.strip()
        if not stripped or is_obvious_evidence_artifact(stripped):
            stats["removed_empty_or_artifact"] += 1
            continue
        if stripped in seen:
            stats["removed_duplicates"] += 1
            continue
        seen.add(stripped)
        cleaned.append(stripped)
        stats["retained_evidence"] += 1

    return cleaned, stats


def _normalize_full_text(full_text: Any) -> list[dict[str, object]]:
    """Normalize QASPER full-text sections into loader-compatible records."""

    sections: list[dict[str, object]] = []

    if isinstance(full_text, list):
        for section in full_text:
            if not isinstance(section, dict):
                continue
            section_name = section.get("section_name")
            sections.append(
                {
                    "section_name": section_name if isinstance(section_name, str) else "SECTION",
                    "paragraphs": _string_list(section.get("paragraphs")),
                }
            )
        return sections

    if isinstance(full_text, dict):
        names = _string_list(full_text.get("section_name"))
        paragraphs = full_text.get("paragraphs", [])
        if not isinstance(paragraphs, list):
            paragraphs = []

        for name, para_group in zip_longest(names, paragraphs, fillvalue=[]):
            sections.append(
                {
                    "section_name": name if isinstance(name, str) and name else "SECTION",
                    "paragraphs": _string_list(para_group),
                }
            )

    return sections


def _normalize_answers(answers: Any) -> tuple[list[dict[str, object]], dict[str, int]]:
    """Extract only answer.evidence from multiple possible QASPER answer shapes."""

    normalized: list[dict[str, object]] = []
    raw_evidence: list[str] = []

    if isinstance(answers, list):
        for answer_entry in answers:
            if not isinstance(answer_entry, dict):
                continue
            answer_obj = answer_entry.get("answer", {})
            if not isinstance(answer_obj, dict):
                answer_obj = {}
            raw_evidence.extend(_string_list(answer_obj.get("evidence")))
        cleaned, stats = clean_evidence_list(raw_evidence)
        normalized.append({"answer": {"evidence": cleaned}})
        return normalized, stats

    if isinstance(answers, dict):
        raw_answers = answers.get("answer", [])
        if isinstance(raw_answers, list):
            for answer_obj in raw_answers:
                if not isinstance(answer_obj, dict):
                    continue
                raw_evidence.extend(_string_list(answer_obj.get("evidence")))

    cleaned, stats = clean_evidence_list(raw_evidence)
    normalized.append({"answer": {"evidence": cleaned}})
    return normalized, stats


def _empty_cleanup_stats() -> dict[str, int]:
    return {
        "raw_evidence": 0,
        "retained_evidence": 0,
        "removed_duplicates": 0,
        "removed_empty_or_artifact": 0,
    }


def _merge_cleanup_stats(left: dict[str, int], right: dict[str, int]) -> dict[str, int]:
    for key, value in right.items():
        left[key] = left.get(key, 0) + value
    return left


def _normalize_qas(qas: Any) -> tuple[list[dict[str, object]], dict[str, int]]:
    """Normalize question-answer groups into the minimal MVE-compatible schema."""

    normalized: list[dict[str, object]] = []
    stats = _empty_cleanup_stats()

    if isinstance(qas, list):
        for qa in qas:
            if not isinstance(qa, dict):
                continue
            question = qa.get("question")
            normalized_answers, answer_stats = _normalize_answers(qa.get("answers"))
            _merge_cleanup_stats(stats, answer_stats)
            normalized.append(
                {
                    "question": question if isinstance(question, str) else "",
                    "answers": normalized_answers,
                }
            )
        return normalized, stats

    if isinstance(qas, dict):
        questions = qas.get("question", [])
        answers = qas.get("answers", [])
        if not isinstance(questions, list):
            questions = []
        if not isinstance(answers, list):
            answers = []

        for question, answer_group in zip_longest(questions, answers, fillvalue=[]):
            normalized_answers, answer_stats = _normalize_answers(answer_group)
            _merge_cleanup_stats(stats, answer_stats)
            normalized.append(
                {
                    "question": question if isinstance(question, str) else "",
                    "answers": normalized_answers,
                }
            )

    return normalized, stats


def _normalize_paper(record: dict[str, Any]) -> tuple[dict[str, object], dict[str, int]]:
    """Project a Hugging Face QASPER record into the local subset schema."""

    paper_id = record.get("id")
    normalized_qas, stats = _normalize_qas(record.get("qas"))
    return {
        "paper_id": paper_id if isinstance(paper_id, str) else "",
        "full_text": _normalize_full_text(record.get("full_text")),
        "qas": normalized_qas,
    }, stats


def _sum_selected_qas(papers: list[dict[str, object]]) -> int:
    total = 0
    for paper in papers:
        paper_qas = paper.get("qas", [])
        if isinstance(paper_qas, list):
            total += len(paper_qas)
    return total


def _apply_limits(
    papers_with_stats: list[tuple[dict[str, object], dict[str, int]]],
    max_papers: int | None,
    max_qas: int | None,
) -> tuple[list[dict[str, object]], int, dict[str, int]]:
    """Apply global paper and QA limits while keeping output paper-centric."""

    selected: list[dict[str, object]] = []
    cleanup_stats = _empty_cleanup_stats()

    for paper, paper_stats in papers_with_stats:
        if max_papers is not None and len(selected) >= max_papers:
            break

        paper_qas = paper.get("qas", [])
        if not isinstance(paper_qas, list):
            paper_qas = []

        if max_qas is None:
            selected.append(paper)
            _merge_cleanup_stats(cleanup_stats, paper_stats)
            continue

        qa_count = _sum_selected_qas(selected)
        remaining = max_qas - qa_count
        if remaining <= 0:
            break

        trimmed_qas = paper_qas[:remaining]
        trimmed_paper = {
            "paper_id": paper.get("paper_id", ""),
            "full_text": paper.get("full_text", []),
            "qas": trimmed_qas,
        }
        selected.append(trimmed_paper)

        if len(trimmed_qas) == len(paper_qas):
            _merge_cleanup_stats(cleanup_stats, paper_stats)
        else:
            partial_stats = _empty_cleanup_stats()
            for qa in trimmed_qas:
                for answer in qa.get("answers", []):
                    answer_obj = answer.get("answer", {})
                    if isinstance(answer_obj, dict):
                        retained = answer_obj.get("evidence", [])
                        if isinstance(retained, list):
                            partial_stats["retained_evidence"] += len(retained)
                            partial_stats["raw_evidence"] += len(retained)
            _merge_cleanup_stats(cleanup_stats, partial_stats)

    return selected, _sum_selected_qas(selected), cleanup_stats


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert Hugging Face QASPER into the local MVE subset format.")
    parser.add_argument("--split", choices=["train", "validation", "test"], required=True, help="QASPER split to download")
    parser.add_argument("--max-papers", type=int, default=None, help="Optional cap on the number of papers to write")
    parser.add_argument("--max-qas", type=int, default=None, help="Optional global cap on the number of QA pairs to write")
    parser.add_argument("--output", required=True, help="Path to the output JSON file")
    parser.add_argument("--seed", type=int, default=None, help="Optional random seed for reproducible paper-order shuffling")
    args = parser.parse_args()

    if args.max_papers is not None and args.max_papers < 1:
        parser.error("--max-papers must be >= 1")
    if args.max_qas is not None and args.max_qas < 1:
        parser.error("--max-qas must be >= 1")

    return args


def main() -> int:
    args = parse_args()

    try:
        from datasets import load_dataset
    except ImportError as exc:
        print("Missing dependency: install `datasets` to run this converter.", file=sys.stderr)
        raise SystemExit(1) from exc

    try:
        dataset = load_dataset("allenai/qasper", split=args.split)
    except Exception as exc:  # pragma: no cover - depends on external environment.
        print(f"Failed to load QASPER split '{args.split}': {exc}", file=sys.stderr)
        return 1

    papers_with_stats: list[tuple[dict[str, object], dict[str, int]]] = []
    for record in dataset:
        paper, paper_stats = _normalize_paper(dict(record))
        papers_with_stats.append((paper, paper_stats))

    if args.seed is not None:
        random.Random(args.seed).shuffle(papers_with_stats)

    selected, qa_count, cleanup_stats = _apply_limits(
        papers_with_stats,
        max_papers=args.max_papers,
        max_qas=args.max_qas,
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        output_path.write_text(json.dumps(selected, indent=2), encoding="utf-8")
    except OSError as exc:
        print(f"Failed to write output file '{output_path}': {exc}", file=sys.stderr)
        return 1

    print(f"Papers: {len(selected)}")
    print(f"QA pairs: {qa_count}")
    print(f"Raw evidence strings: {cleanup_stats['raw_evidence']}")
    print(f"Evidence retained: {cleanup_stats['retained_evidence']}")
    print(f"Evidence removed as duplicates: {cleanup_stats['removed_duplicates']}")
    print(f"Evidence removed as empty/artifact: {cleanup_stats['removed_empty_or_artifact']}")
    print(f"Output: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
