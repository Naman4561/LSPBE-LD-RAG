#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

def _repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "pyproject.toml").exists() and (parent / "src").exists():
            return parent
    raise RuntimeError("Could not locate repo root.")


ROOT = _repo_root()
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lspbe.mve import QAExample, _evidence_hit, debug_trace_query, evaluate_retrieval, load_qasper_subset
from lspbe.retrieval import BGERetriever, HashingEmbedder
from lspbe.types import DocumentSegment, RetrievedSegment


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a small inspectable MVE debug experiment.")
    parser.add_argument("--qasper-path", required=True, help="Path to the QASPER subset JSON file")
    parser.add_argument("--results-path", required=True, help="Path to write metrics JSON")
    parser.add_argument("--examples-path", required=True, help="Path to write human-inspection markdown")
    parser.add_argument("--max-papers", type=int, default=10)
    parser.add_argument("--max-qas", type=int, default=100)
    parser.add_argument("--examples", type=int, default=5, help="Number of QA examples to render")
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--radius", type=int, default=1)
    parser.add_argument("--top-m", type=int, default=2)
    parser.add_argument("--context-budget", type=int, default=20)
    parser.add_argument("--embedder", choices=["bge", "hash"], default="bge")
    parser.add_argument("--restrict-to-doc", action="store_true", help="Rank only segments from the QA's own paper")
    parser.add_argument(
        "--methods",
        default="flat,adjacency,bridge",
        help="Comma-separated methods, e.g. flat,adjacency,bridge_adj_entity,bridge_adj_section,bridge_full",
    )
    return parser.parse_args()


def _parse_methods(raw_methods: str) -> list[str]:
    methods = [method.strip() for method in raw_methods.split(",") if method.strip()]
    if not methods:
        raise ValueError("At least one method must be provided.")
    return methods


def _segment_block(seg: DocumentSegment, prefix: str = "") -> str:
    text = seg.text.replace("\n", " ").strip()
    return (
        f"{prefix}- section: `{seg.section}`\n"
        f"{prefix}- segment_id: `{seg.segment_id}`\n"
        f"{prefix}- text: {text}"
    )


def _bridge_detail_line(trace: dict[str, object], seg: DocumentSegment) -> str:
    details = trace["bridge_details"].get(trace["_current_method"], {})
    detail = details.get((seg.doc_id, seg.segment_id))
    if detail is None:
        return "- bridge_detail: seed segment or not added via bridge scoring"
    return (
        "- bridge_detail: "
        f"seed=`{detail.seed_segment_id}`, total=`{detail.total_score:.3f}`, "
        f"adjacency=`{detail.adjacency:.3f}`, entity_overlap=`{detail.entity_overlap:.3f}`, "
        f"section_continuity=`{detail.section_continuity:.3f}`"
    )


def _method_hit(segments: list[DocumentSegment], evidence_texts: list[str]) -> bool:
    return _evidence_hit(segments, evidence_texts)


def _note_for_example(trace: dict[str, object], qa: QAExample, methods: list[str]) -> str:
    method_hits = {
        method: _method_hit(trace["methods"][method], qa.evidence_texts)
        for method in methods
    }
    hit_methods = [method for method, hit in method_hits.items() if hit]
    if len(hit_methods) == 1:
        return f"`{hit_methods[0]}` looks best qualitatively here because it is the only method hitting the gold evidence."
    if len(hit_methods) > 1:
        return f"No clear single winner here; evidence-hit is shared by: {', '.join(hit_methods)}."
    return "No method hits the gold evidence here under the current evidence-hit proxy."


def _format_method(name: str, method_key: str, segments: list[DocumentSegment], trace: dict[str, object]) -> str:
    lines = [f"### {name}"]
    for seg in segments:
        lines.append(_segment_block(seg))
        if method_key.startswith("bridge"):
            trace["_current_method"] = method_key
            lines.append(_bridge_detail_line(trace, seg))
        lines.append("")
    return "\n".join(lines).rstrip()


def _write_examples(
    examples_path: Path,
    qas: list[QAExample],
    traces: list[dict[str, object]],
    methods: list[str],
) -> None:
    lines: list[str] = [
        "# MVE Debug Examples",
        "",
        "These examples show the cleaned gold evidence and the retrieved context for each method.",
        "The goal is qualitative inspection, so segments are listed with section names and ids.",
        "",
    ]

    for idx, (qa, trace) in enumerate(zip(qas, traces), start=1):
        lines.append(f"## Example {idx}")
        lines.append("")
        lines.append(f"- paper_id: `{qa.doc_id}`")
        lines.append(f"- question: {qa.query}")
        lines.append("- gold evidence:")
        for ev in qa.evidence_texts:
            lines.append(f"  - {ev}")
        lines.append(f"- note: {_note_for_example(trace, qa, methods)}")
        lines.append("")
        for method in methods:
            display_name = method.replace("_", " ")
            lines.append(_format_method(display_name, method, trace["methods"][method], trace))
            lines.append("")

    examples_path.parent.mkdir(parents=True, exist_ok=True)
    examples_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    methods = _parse_methods(args.methods)

    segments, qas = load_qasper_subset(args.qasper_path, max_papers=args.max_papers, max_qas=args.max_qas)
    if args.embedder == "bge":
        retriever = BGERetriever(segments)
    else:
        retriever = BGERetriever(segments, embedder=HashingEmbedder())

    results = {
        "subset_path": str(Path(args.qasper_path)),
        "embedder": args.embedder,
        "restrict_to_doc": args.restrict_to_doc,
        "max_papers": args.max_papers,
        "max_qas": args.max_qas,
        "k": args.k,
        "radius": args.radius,
        "top_m": args.top_m,
        "context_budget": args.context_budget,
        "methods": methods,
        "metrics": {
            method: evaluate_retrieval(
                retriever,
                qas,
                context_budget=args.context_budget,
                method=method,
                k=args.k,
                radius=args.radius,
                top_m=args.top_m,
                restrict_to_doc=args.restrict_to_doc,
            )
            for method in methods
        },
    }

    traces = [
        debug_trace_query(
            retriever,
            qa,
            context_budget=args.context_budget,
            k=args.k,
            radius=args.radius,
            top_m=args.top_m,
            restrict_to_doc=args.restrict_to_doc,
            methods=methods,
        )
        for qa in qas[: args.examples]
    ]

    results_path = Path(args.results_path)
    results_path.parent.mkdir(parents=True, exist_ok=True)
    results_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    _write_examples(Path(args.examples_path), qas[: args.examples], traces, methods)
    print(json.dumps(results["metrics"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

