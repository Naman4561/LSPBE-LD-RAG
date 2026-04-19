#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lspbe.qasper import LOCKED_QASPER_RESULTS_50, canonical_qasper_methods
from lspbe.qasper_eval import evaluate_methods, load_qasper_eval_context, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the canonical QASPER baseline bundle once and write final + comparison artifacts."
    )
    parser.add_argument("--qasper-path", required=True, help="QASPER JSON file to evaluate.")
    parser.add_argument("--max-papers", type=int, default=50)
    parser.add_argument("--max-qas", type=int, default=10_000)
    parser.add_argument(
        "--segmentation-mode",
        choices=["seg_paragraph", "seg_paragraph_pair", "seg_micro_chunk"],
        default="seg_paragraph",
        help="Segmentation strategy to apply before retrieval.",
    )
    parser.add_argument("--tag", required=True, help="Artifact tag, for example final_qasper_50paper or final_qasper_full.")
    parser.add_argument("--artifacts-dir", default=str(ROOT / "artifacts"))
    return parser.parse_args()


def result_by_name(results: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    return {str(result["name"]): result for result in results}


def build_compare_markdown(
    subset_path: str,
    segmentation_mode: str,
    results: list[dict[str, object]],
    locked_reference: dict[str, float] | None,
) -> str:
    by_name = result_by_name(results)
    lines = [
        "# QASPER Baseline Comparison",
        "",
        f"- subset_path: `{subset_path}`",
        f"- segmentation_mode: `{segmentation_mode}`",
        "",
        "## Results",
        "",
    ]
    for name in ["adjacency", "bridge_v1", "bridge_v2", "bridge_final"]:
        metric = float(by_name[name]["evidence_hit_rate"])
        line = f"- `{name}`: `{metric:.4f}`"
        if locked_reference is not None and name in locked_reference:
            expected = float(locked_reference[name])
            status = "match" if abs(metric - expected) < 5e-5 else f"mismatch vs `{expected:.4f}`"
            line += f" ({status})"
        lines.append(line)
    return "\n".join(lines).rstrip() + "\n"


def build_final_markdown(
    subset_path: str,
    segmentation_mode: str,
    final_result: dict[str, object],
    locked_reference: dict[str, float] | None,
    source_compare_file: str,
) -> str:
    metric = float(final_result["evidence_hit_rate"])
    lines = [
        "# QASPER Final Model Summary",
        "",
        f"- subset_path: `{subset_path}`",
        f"- segmentation_mode: `{segmentation_mode}`",
        f"- canonical model: `bridge_final`",
        f"- evidence_hit_rate: `{metric:.4f}`",
    ]
    if locked_reference is not None:
        expected = float(locked_reference["bridge_final"])
        status = "match" if abs(metric - expected) < 5e-5 else f"mismatch vs `{expected:.4f}`"
        lines.append(f"- locked historical check: {status}")
    lines.extend(
        [
            f"- derived_from: `{source_compare_file}`",
            "",
            "## Locked Config",
            "",
            "- hybrid seed retrieval",
            "- dense weight `1.00`",
            "- sparse weight `0.50`",
            "- Bridge v2 skip-local design",
            "- continuity `idf_overlap`",
            "- no section scoring",
            "- no adaptive trigger",
            "- no reranker",
            "- no diversification",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = parse_args()
    artifacts_dir = Path(args.artifacts_dir)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    context = load_qasper_eval_context(
        args.qasper_path,
        max_papers=args.max_papers,
        max_qas=args.max_qas,
        segmentation_mode=args.segmentation_mode,
    )
    methods = canonical_qasper_methods()
    results = evaluate_methods(context, methods)
    by_name = result_by_name(results)

    compare_json_path = artifacts_dir / f"{args.tag}_baseline_compare.json"
    compare_md_path = artifacts_dir / f"{args.tag}_baseline_compare.md"
    final_json_path = artifacts_dir / f"{args.tag}_model_results.json"
    final_md_path = artifacts_dir / f"{args.tag}_model_summary.md"

    locked_reference = LOCKED_QASPER_RESULTS_50 if Path(args.qasper_path).name == "qasper_subset_debug_50.json" else None

    compare_payload = {
        "subset_path": str(args.qasper_path),
        "segmentation_mode": args.segmentation_mode,
        "methods": [method.as_dict() for method in methods],
        "results": results,
        "locked_reference": locked_reference,
    }
    final_payload = {
        "subset_path": str(args.qasper_path),
        "segmentation_mode": args.segmentation_mode,
        "method": by_name["bridge_final"]["config"],
        "metrics": by_name["bridge_final"],
        "locked_reference": (
            {
                "evidence_hit_rate": LOCKED_QASPER_RESULTS_50["bridge_final"],
                "beyond_adjacency_subset_hit_rate": LOCKED_QASPER_RESULTS_50["beyond_adjacency_subset_hit_rate"],
            }
            if locked_reference is not None
            else None
        ),
    }

    write_json(compare_json_path, compare_payload)
    write_json(final_json_path, final_payload)
    compare_md_path.write_text(
        build_compare_markdown(str(args.qasper_path), args.segmentation_mode, results, locked_reference),
        encoding="utf-8",
    )
    final_md_path.write_text(
        build_final_markdown(
            str(args.qasper_path),
            args.segmentation_mode,
            by_name["bridge_final"],
            locked_reference,
            compare_json_path.name,
        ),
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "compare_json": str(compare_json_path),
                "compare_md": str(compare_md_path),
                "final_json": str(final_json_path),
                "final_md": str(final_md_path),
                "results": results,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
