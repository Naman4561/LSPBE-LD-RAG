from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

# Allow `python tests/test_pipeline.py` from the repo root without requiring
# an editable install first.
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lspbe.expansion import adjacency_expand, bridge_expand
from lspbe.retrieval import BGERetriever
from lspbe.segmentation import segment_document
from lspbe.types import DocumentSegment


class FakeEmbedder:
    def encode(self, texts: list[str]) -> np.ndarray:
        out = []
        for t in texts:
            t = t.lower()
            out.append(
                [
                    1.0 if "model" in t else 0.0,
                    1.0 if "accuracy" in t else 0.0,
                    1.0 if "dataset" in t else 0.0,
                ]
            )
        return np.asarray(out, dtype=np.float32)


def test_section_aware_segmentation_heading_boundaries() -> None:
    text = "# Intro\nshort para\n\nthis paragraph has enough words to avoid merge " + "word " * 45 + "\n\n# Method\nthis is method paragraph " + "token " * 50
    segments = segment_document("d1", text)
    assert len(segments) >= 2
    assert segments[0].section == "Intro"
    assert any(seg.section == "Method" for seg in segments)


def test_flat_retrieval_and_expansion() -> None:
    segments = [
        DocumentSegment("d1", 0, "Intro", "model overview"),
        DocumentSegment("d1", 1, "Intro", "model accuracy gains"),
        DocumentSegment("d1", 2, "Method", "dataset and training"),
    ]
    retriever = BGERetriever(segments, embedder=FakeEmbedder())
    rank = retriever.retrieve("model accuracy", k=2)
    assert len(rank.ranked) == 2

    by_doc = {"d1": segments}
    adj = adjacency_expand(rank.ranked, by_doc, context_budget=5)
    assert any(s.segment_id == 0 for s in adj)
    assert any(s.segment_id == 1 for s in adj)

    bridge = bridge_expand(rank.ranked, by_doc, context_budget=5, radius=1, top_m=1)
    assert len(bridge) >= 2


if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([__file__]))
