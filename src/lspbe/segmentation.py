from __future__ import annotations

import re
from typing import Iterable

from .types import DocumentSegment

_MIN_WORDS = 40
_MAX_WORDS = 220
_MICRO_MAX_WORDS = 120


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


def _split_micro_chunks(paragraph: str, max_words: int = _MICRO_MAX_WORDS) -> list[str]:
    """Greedy sentence-group splitting for finer-grained long-paragraph chunks."""

    words = paragraph.split()
    if len(words) <= max_words:
        return [paragraph.strip()]

    sentences = [sent.strip() for sent in re.split(r"(?<=[.!?])\s+", paragraph.strip()) if sent.strip()]
    if len(sentences) <= 1:
        chunks: list[str] = []
        current: list[str] = []
        for word in words:
            current.append(word)
            if len(current) >= max_words:
                chunks.append(" ".join(current).strip())
                current = []
        if current:
            chunks.append(" ".join(current).strip())
        return chunks

    chunks: list[str] = []
    current_sentences: list[str] = []
    current_words = 0
    for sentence in sentences:
        sentence_words = len(sentence.split())
        if current_sentences and current_words + sentence_words > max_words:
            chunks.append(" ".join(current_sentences).strip())
            current_sentences = [sentence]
            current_words = sentence_words
        else:
            current_sentences.append(sentence)
            current_words += sentence_words

    if current_sentences:
        chunks.append(" ".join(current_sentences).strip())
    return chunks


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


def _collect_section_paragraphs(text: str) -> list[tuple[str, list[str]]]:
    lines = [line.rstrip() for line in text.splitlines()]
    current_section = "ROOT"
    section_paragraphs: list[str] = []
    sections: list[tuple[str, list[str]]] = []

    def flush() -> None:
        nonlocal section_paragraphs
        if section_paragraphs:
            sections.append((current_section, section_paragraphs))
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
    return sections


def _normalize_section_paragraphs(paragraphs: list[str], split_mode: str) -> list[str]:
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
    for paragraph in merged:
        if split_mode == "paragraph":
            split_segments.extend(_split_long_paragraph(paragraph))
        elif split_mode == "micro_chunk":
            split_segments.extend(_split_micro_chunks(paragraph))
        else:
            raise ValueError(f"Unsupported split mode: {split_mode}")
    return [segment for segment in split_segments if segment]


def _pair_adjacent_segments(segments: list[str]) -> list[str]:
    if len(segments) <= 1:
        return segments
    return [
        f"{segments[idx]} {segments[idx + 1]}".strip()
        for idx in range(len(segments) - 1)
    ]


def segment_document_with_mode(doc_id: str, text: str, mode: str = "paragraph") -> list[DocumentSegment]:
    """Section-aware segmentation variants for the QASPER robustness study."""

    sections = _collect_section_paragraphs(text)
    segments: list[DocumentSegment] = []
    next_id = 0

    for section, paragraphs in sections:
        if mode == "paragraph":
            section_segments = _normalize_section_paragraphs(paragraphs, split_mode="paragraph")
        elif mode == "paragraph_pair":
            base_segments = _normalize_section_paragraphs(paragraphs, split_mode="paragraph")
            section_segments = _pair_adjacent_segments(base_segments)
        elif mode == "micro_chunk":
            section_segments = _normalize_section_paragraphs(paragraphs, split_mode="micro_chunk")
        else:
            raise ValueError(f"Unsupported segmentation mode: {mode}")

        for chunk in section_segments:
            segments.append(DocumentSegment(doc_id=doc_id, segment_id=next_id, section=section, text=chunk))
            next_id += 1
    return segments


def segment_document(doc_id: str, text: str) -> list[DocumentSegment]:
    """Section-aware paragraph segmentation per project spec."""
    return segment_document_with_mode(doc_id, text, mode="paragraph")


def segment_documents(raw_documents: Iterable[tuple[str, str]]) -> list[DocumentSegment]:
    all_segments: list[DocumentSegment] = []
    for doc_id, text in raw_documents:
        all_segments.extend(segment_document(doc_id, text))
    return all_segments
