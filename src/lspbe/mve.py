from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .expansion import adjacency_expand, bridge_expand
from .retrieval import BGERetriever, HashingEmbedder, RankResult
from .segmentation import segment_document
from .types import DocumentSegment


@dataclass(frozen=True)
class QAExample:
    doc_id: str
    query: str
    evidence_texts: list[str]


def load_qasper_subset(path: str | Path, max_papers: int = 100, max_qas: int = 300) -> tuple[list[DocumentSegment], list[QAExample]]:
    """Load a lightweight subset from QASPER-like JSON format.

    Expected shape per paper (subset):
    {
      "paper_id": "...",
      "full_text": [{"section_name":"Intro","paragraphs":[...]}, ...],
      "qas": [{"question":"...", "answers":[{"answer":{"evidence":["..."]}}]}]
    }
    """

    raw = json.loads(Path(path).read_text())
    if isinstance(raw, dict):
        papers = list(raw.values())
    else:
        papers = raw

    segments: list[DocumentSegment] = []
    qas: list[QAExample] = []

    for paper in papers[:max_papers]:
        doc_id = paper.get("paper_id") or paper.get("id") or str(len(segments))
        full_text = paper.get("full_text", [])
        doc_text_parts: list[str] = []
        for section in full_text:
            section_name = section.get("section_name") or "SECTION"
            doc_text_parts.append(f"# {section_name}")
            doc_text_parts.extend(section.get("paragraphs", []))
            doc_text_parts.append("")

        doc_text = "\n".join(doc_text_parts)
        segments.extend(segment_document(doc_id, doc_text))

        for qa in paper.get("qas", []):
            if len(qas) >= max_qas:
                break
            evidence: list[str] = []
            for ans in qa.get("answers", []):
                answer_obj = ans.get("answer", {})
                evidence.extend(answer_obj.get("evidence", []))
            qas.append(QAExample(doc_id=doc_id, query=qa.get("question", ""), evidence_texts=evidence))

        if len(qas) >= max_qas:
            break

    return segments, qas


def _build_segments_by_doc(segments: list[DocumentSegment]) -> dict[str, list[DocumentSegment]]:
    grouped: dict[str, list[DocumentSegment]] = {}
    for seg in segments:
        grouped.setdefault(seg.doc_id, []).append(seg)
    for doc_id in grouped:
        grouped[doc_id] = sorted(grouped[doc_id], key=lambda x: x.segment_id)
    return grouped


def _evidence_hit(retrieved: list[DocumentSegment], evidence_texts: list[str]) -> bool:
    if not evidence_texts:
        return False
    joined = "\n".join(seg.text.lower() for seg in retrieved)
    return any(ev.lower()[:80] in joined for ev in evidence_texts if ev)


def evaluate_retrieval(
    retriever: BGERetriever,
    qas: list[QAExample],
    context_budget: int,
    method: str,
    k: int = 5,
    radius: int = 1,
    top_m: int = 2,
) -> dict[str, float]:
    segments_by_doc = _build_segments_by_doc(retriever.segments)

    hits = 0
    rr_sum = 0.0
    evidence_hits = 0
    total = max(len(qas), 1)

    for qa in qas:
        rank: RankResult = retriever.retrieve(qa.query, k=k)

        if method == "flat":
            retrieved = [r.segment for r in rank.ranked][:context_budget]
        elif method == "adjacency":
            retrieved = adjacency_expand(rank.ranked, segments_by_doc, context_budget=context_budget)
        elif method == "bridge":
            retrieved = bridge_expand(
                rank.ranked,
                segments_by_doc,
                context_budget=context_budget,
                radius=radius,
                top_m=top_m,
            )
        else:
            raise ValueError(f"Unsupported method: {method}")

        ranked_doc = [s for s in retrieved if s.doc_id == qa.doc_id]
        if ranked_doc:
            hits += 1
            rr_sum += 1.0

        if _evidence_hit(retrieved, qa.evidence_texts):
            evidence_hits += 1

    return {
        "queries": float(len(qas)),
        "recall_at_k": hits / total,
        "mrr": rr_sum / total,
        "evidence_hit_rate": evidence_hits / total,
    }


def run_mve(
    qasper_path: str | Path,
    embedder: str = "bge",
    max_papers: int = 100,
    max_qas: int = 300,
    k: int = 5,
    radius: int = 1,
    top_m: int = 2,
    context_budget: int = 20,
) -> dict[str, dict[str, float]]:
    segments, qas = load_qasper_subset(qasper_path, max_papers=max_papers, max_qas=max_qas)
    if embedder == "bge":
        retriever = BGERetriever(segments)
    elif embedder == "hash":
        retriever = BGERetriever(segments, embedder=HashingEmbedder())
    else:
        raise ValueError(f"Unsupported embedder: {embedder}")

    results = {
        "flat": evaluate_retrieval(retriever, qas, context_budget=context_budget, method="flat", k=k, radius=radius, top_m=top_m),
        "adjacency": evaluate_retrieval(retriever, qas, context_budget=context_budget, method="adjacency", k=k, radius=radius, top_m=top_m),
        "bridge": evaluate_retrieval(retriever, qas, context_budget=context_budget, method="bridge", k=k, radius=radius, top_m=top_m),
    }
    return results
