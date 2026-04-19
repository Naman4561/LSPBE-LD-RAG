#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

import run_qasper_eval_bundle


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the canonical full-QASPER evaluation bundle.")
    parser.add_argument(
        "--qasper-path",
        default=str(ROOT / "data" / "qasper_train_full.json"),
        help="Full converted QASPER JSON file.",
    )
    parser.add_argument("--max-papers", type=int, default=1000000)
    parser.add_argument("--max-qas", type=int, default=1000000)
    parser.add_argument("--tag", default="final_qasper_full")
    parser.add_argument(
        "--segmentation-mode",
        choices=["seg_paragraph", "seg_paragraph_pair", "seg_micro_chunk"],
        default="seg_paragraph_pair",
        help="Segmentation strategy for the full canonical run. Defaults to the study winner.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    sys.argv = [
        "run_qasper_eval_bundle.py",
        "--qasper-path",
        args.qasper_path,
        "--max-papers",
        str(args.max_papers),
        "--max-qas",
        str(args.max_qas),
        "--segmentation-mode",
        args.segmentation_mode,
        "--tag",
        args.tag,
    ]
    return run_qasper_eval_bundle.main()


if __name__ == "__main__":
    raise SystemExit(main())
