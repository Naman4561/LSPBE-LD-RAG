from __future__ import annotations

import re
from typing import Iterable

from .types import DocumentSegment

_MIN_WORDS = 40
_MAX_WORDS = 220


def _is_heading(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if stripped.startswith("#"):
        return True
    if re.match(r"^\d+(\.\d+)*\s+", stripped):
        return True
    return stripped.isupper() and len(stripped.split()) <= 12


def _split_long_paragraph(paragraph: str, max_words: int = _MAX_WORDS) -> list[str]:
    words = paragraph.split()
    if len(words) <= max_words:
        return [paragraph.strip()]

    sentences = re.split(r"(?<=[.!?])\s+", paragraph.strip())
    if len(sentences) <= 1:
        midpoint = len(words) // 2
        return [" ".join(words[:midpoint]).strip(), " ".join(words[midpoint:]).strip()]

    left, right = [], []
    left_words = 0
    target = len(words) // 2
    for sent in sentences:
        sent_words = len(sent.split())
        if left_words < target:
            left.append(sent)
            left_words += sent_words
        else:
            right.append(sent)

    if not right:
        midpoint = len(words) // 2
        return [" ".join(words[:midpoint]).strip(), " ".join(words[midpoint:]).strip()]
    return [" ".join(left).strip(), " ".join(right).strip()]


def _flush_section_paragraphs(section: str, paragraphs: list[str], doc_id: str, start_id: int) -> tuple[list[DocumentSegment], int]:
    merged: list[str] = []
    idx = 0
    while idx < len(paragraphs):
        current = paragraphs[idx].strip()
        wc = len(current.split())
        if wc < _MIN_WORDS and idx + 1 < len(paragraphs):
            current = f"{current} {paragraphs[idx + 1].strip()}".strip()
            idx += 1
        merged.append(current)
        idx += 1

    split_segments: list[str] = []
    for p in merged:
        split_segments.extend(_split_long_paragraph(p))

    segments: list[DocumentSegment] = []
    next_id = start_id
    for text in split_segments:
        if not text:
            continue
        segments.append(DocumentSegment(doc_id=doc_id, segment_id=next_id, section=section, text=text))
        next_id += 1
    return segments, next_id


def segment_document(doc_id: str, text: str) -> list[DocumentSegment]:
    """Section-aware paragraph segmentation per project spec."""

    lines = [line.rstrip() for line in text.splitlines()]
    current_section = "ROOT"
    section_paragraphs: list[str] = []
    segments: list[DocumentSegment] = []
    next_id = 0

    def flush() -> None:
        nonlocal segments, next_id, section_paragraphs, current_section
        if not section_paragraphs:
            return
        new_segments, next_id_local = _flush_section_paragraphs(current_section, section_paragraphs, doc_id, next_id)
        segments.extend(new_segments)
        next_id = next_id_local
        section_paragraphs = []

    buffer: list[str] = []
    for line in lines + [""]:
        if _is_heading(line):
            if buffer:
                section_paragraphs.append(" ".join(buffer).strip())
                buffer = []
            flush()
            current_section = line.strip().lstrip("#").strip() or "ROOT"
            continue

        if line.strip() == "":
            if buffer:
                section_paragraphs.append(" ".join(buffer).strip())
                buffer = []
        else:
            buffer.append(line.strip())

    if buffer:
        section_paragraphs.append(" ".join(buffer).strip())
    flush()

    return segments


def segment_documents(raw_documents: Iterable[tuple[str, str]]) -> list[DocumentSegment]:
    all_segments: list[DocumentSegment] = []
    for doc_id, text in raw_documents:
        all_segments.extend(segment_document(doc_id, text))
    return all_segments
