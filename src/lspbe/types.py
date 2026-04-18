from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentSegment:
    """A section-aware document segment."""

    doc_id: str
    segment_id: int
    section: str
    text: str


@dataclass(frozen=True)
class RetrievedSegment:
    """Segment with a retrieval score."""

    segment: DocumentSegment
    score: float
