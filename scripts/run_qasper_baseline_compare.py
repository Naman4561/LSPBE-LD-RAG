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
    parser = argparse.ArgumentParser(description="Run the legacy QASPER baseline comparison.")
    parser.add_argument(
        "--qasper-path",
        default=str(ROOT / "data" / "qasper_subset_debug_50.json"),
        help="QASPER subset JSON to evaluate.",
    )
    parser.add_argument("--max-papers", type=int, default=50)
    parser.add_argument("--max-qas", type=int, default=10_000)
    parser.add_argument(
        "--segmentation-mode",
        choices=["seg_paragraph", "seg_paragraph_pair", "seg_micro_chunk"],
        default="seg_paragraph",
        help="Segmentation strategy to apply before retrieval.",
    )
    parser.add_argument(
        "--output-json",
        default="",
        help="Optional path to save the comparison payload as JSON.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    context = load_qasper_eval_context(
        args.qasper_path,
        max_papers=args.max_papers,
        max_qas=args.max_qas,
        segmentation_mode=args.segmentation_mode,
    )
    methods = canonical_qasper_methods()
    results = evaluate_methods(context, methods)
    payload = {
        "subset_path": str(args.qasper_path),
        "segmentation_mode": args.segmentation_mode,
        "methods": [method.as_dict() for method in methods],
        "results": results,
        "locked_50_paper_reference": LOCKED_QASPER_RESULTS_50,
    }
    if args.output_json:
        write_json(args.output_json, payload)
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
