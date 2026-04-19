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
import sys
from itertools import zip_longest
from pathlib import Path
from typing import Any


def _string_list(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    return [value for value in values if isinstance(value, str)]


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


def _normalize_answers(answers: Any) -> list[dict[str, object]]:
    """Extract only answer.evidence from multiple possible QASPER answer shapes."""

    normalized: list[dict[str, object]] = []

    if isinstance(answers, list):
        for answer_entry in answers:
            if not isinstance(answer_entry, dict):
                continue
            answer_obj = answer_entry.get("answer", {})
            if not isinstance(answer_obj, dict):
                answer_obj = {}
            normalized.append({"answer": {"evidence": _string_list(answer_obj.get("evidence"))}})
        return normalized

    if isinstance(answers, dict):
        raw_answers = answers.get("answer", [])
        if isinstance(raw_answers, list):
            for answer_obj in raw_answers:
                if not isinstance(answer_obj, dict):
                    continue
                normalized.append({"answer": {"evidence": _string_list(answer_obj.get("evidence"))}})

    return normalized


def _normalize_qas(qas: Any) -> list[dict[str, object]]:
    """Normalize question-answer groups into the minimal MVE-compatible schema."""

    normalized: list[dict[str, object]] = []

    if isinstance(qas, list):
        for qa in qas:
            if not isinstance(qa, dict):
                continue
            question = qa.get("question")
            normalized.append(
                {
                    "question": question if isinstance(question, str) else "",
                    "answers": _normalize_answers(qa.get("answers")),
                }
            )
        return normalized

    if isinstance(qas, dict):
        questions = qas.get("question", [])
        answers = qas.get("answers", [])
        if not isinstance(questions, list):
            questions = []
        if not isinstance(answers, list):
            answers = []

        for question, answer_group in zip_longest(questions, answers, fillvalue=[]):
            normalized.append(
                {
                    "question": question if isinstance(question, str) else "",
                    "answers": _normalize_answers(answer_group),
                }
            )

    return normalized


def _normalize_paper(record: dict[str, Any]) -> dict[str, object]:
    """Project a Hugging Face QASPER record into the local subset schema."""

    paper_id = record.get("id")
    return {
        "paper_id": paper_id if isinstance(paper_id, str) else "",
        "full_text": _normalize_full_text(record.get("full_text")),
        "qas": _normalize_qas(record.get("qas")),
    }


def _apply_limits(
    papers: list[dict[str, object]],
    max_papers: int | None,
    max_qas: int | None,
) -> tuple[list[dict[str, object]], int]:
    """Apply global paper and QA limits while keeping output paper-centric."""

    selected: list[dict[str, object]] = []
    qa_count = 0

    for paper in papers:
        if max_papers is not None and len(selected) >= max_papers:
            break

        paper_qas = paper.get("qas", [])
        if not isinstance(paper_qas, list):
            paper_qas = []

        if max_qas is None:
            selected.append(paper)
            qa_count += len(paper_qas)
            continue

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
        qa_count += len(trimmed_qas)

    return selected, qa_count


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

    papers = [_normalize_paper(dict(record)) for record in dataset]

    if args.seed is not None:
        random.Random(args.seed).shuffle(papers)

    selected, qa_count = _apply_limits(papers, max_papers=args.max_papers, max_qas=args.max_qas)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        output_path.write_text(json.dumps(selected, indent=2), encoding="utf-8")
    except OSError as exc:
        print(f"Failed to write output file '{output_path}': {exc}", file=sys.stderr)
        return 1

    print(f"Papers: {len(selected)}")
    print(f"QA pairs: {qa_count}")
    print(f"Output: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
