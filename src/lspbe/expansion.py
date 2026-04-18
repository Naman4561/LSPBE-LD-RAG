from __future__ import annotations

import re
from collections import defaultdict

from .types import DocumentSegment, RetrievedSegment

_STOPWORDS = {
    "the", "a", "an", "and", "or", "for", "of", "to", "in", "on", "is", "are", "was", "were",
    "be", "as", "by", "with", "that", "this", "it", "from", "at", "we", "our", "their", "can",
}


def _token_set(text: str) -> set[str]:
    tokens = re.findall(r"[A-Za-z][A-Za-z\-]+", text.lower())
    return {t for t in tokens if t not in _STOPWORDS and len(t) > 2}


def _entity_like_set(text: str) -> set[str]:
    cap_chunks = re.findall(r"\b[A-Z][a-zA-Z0-9\-]{2,}(?:\s+[A-Z][a-zA-Z0-9\-]{2,})*", text)
    if cap_chunks:
        return {chunk.lower() for chunk in cap_chunks}
    return _token_set(text)


def _adjacency_score(i: int, j: int) -> float:
    distance = abs(i - j)
    if distance == 0:
        return 0.0
    return 1.0 / distance


def _entity_overlap(seed: DocumentSegment, cand: DocumentSegment) -> float:
    a = _entity_like_set(seed.text)
    b = _entity_like_set(cand.text)
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _section_continuity(seed: DocumentSegment, cand: DocumentSegment) -> float:
    return 1.0 if seed.section == cand.section else 0.0


def adjacency_expand(
    seeds: list[RetrievedSegment],
    segments_by_doc: dict[str, list[DocumentSegment]],
    context_budget: int,
) -> list[DocumentSegment]:
    collected: dict[tuple[str, int], DocumentSegment] = {}
    for seed in seeds:
        segment = seed.segment
        doc_segments = segments_by_doc[segment.doc_id]
        idx = segment.segment_id
        for neighbor_idx in (idx - 1, idx, idx + 1):
            if 0 <= neighbor_idx < len(doc_segments):
                seg = doc_segments[neighbor_idx]
                collected[(seg.doc_id, seg.segment_id)] = seg

    result = sorted(collected.values(), key=lambda s: (s.doc_id, s.segment_id))
    return result[:context_budget]


def bridge_expand(
    seeds: list[RetrievedSegment],
    segments_by_doc: dict[str, list[DocumentSegment]],
    context_budget: int,
    radius: int = 1,
    top_m: int = 2,
    alpha: float = 1.0,
    beta: float = 1.0,
    gamma: float = 1.0,
) -> list[DocumentSegment]:
    selected: dict[tuple[str, int], DocumentSegment] = {}
    candidate_scores: defaultdict[tuple[str, int], float] = defaultdict(float)

    for seed in seeds:
        s = seed.segment
        doc_segments = segments_by_doc[s.doc_id]
        selected[(s.doc_id, s.segment_id)] = s

        local_scores: list[tuple[float, DocumentSegment]] = []
        for offset in range(-radius, radius + 1):
            if offset == 0:
                continue
            j = s.segment_id + offset
            if j < 0 or j >= len(doc_segments):
                continue
            cand = doc_segments[j]
            bridge_score = (
                alpha * _adjacency_score(s.segment_id, cand.segment_id)
                + beta * _entity_overlap(s, cand)
                + gamma * _section_continuity(s, cand)
            )
            local_scores.append((bridge_score, cand))

        local_scores.sort(key=lambda x: x[0], reverse=True)
        for score, cand in local_scores[:top_m]:
            candidate_scores[(cand.doc_id, cand.segment_id)] = max(candidate_scores[(cand.doc_id, cand.segment_id)], score)

    for key, _ in sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True):
        selected[key] = segments_by_doc[key[0]][key[1]]
        if len(selected) >= context_budget:
            break

    return sorted(selected.values(), key=lambda s: (s.doc_id, s.segment_id))[:context_budget]
