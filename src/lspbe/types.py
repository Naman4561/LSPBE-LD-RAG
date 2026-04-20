from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class DocumentSegment:
    """A section-aware document segment."""

    doc_id: str
    segment_id: int
    section: str
    text: str
    unit_type: str = "paragraph"
    anchor_segment_id: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RetrievedSegment:
    """Segment with a retrieval score."""

    segment: DocumentSegment
    score: float
