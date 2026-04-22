#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

def _repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "pyproject.toml").exists() and (parent / "src").exists():
            return parent
    raise RuntimeError("Could not locate repo root.")


ROOT = _repo_root()
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

import run_qasper_eval_bundle

LEGACY_FINAL_LOCKED_DIR = ROOT / "artifacts" / "legacy_pre_redo" / "final_locked_qasper"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the legacy pre-redo full-QASPER evaluation bundle.")
    parser.add_argument(
        "--qasper-path",
        default=str(ROOT / "data" / "qasper_train_full.json"),
        help="Full converted QASPER JSON file.",
    )
    parser.add_argument("--max-papers", type=int, default=1000000)
    parser.add_argument("--max-qas", type=int, default=1000000)
    parser.add_argument("--tag", default="final_qasper_full")
    parser.add_argument("--artifacts-dir", default=str(LEGACY_FINAL_LOCKED_DIR))
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
        "--artifacts-dir",
        args.artifacts_dir,
    ]
    return run_qasper_eval_bundle.main()


if __name__ == "__main__":
    raise SystemExit(main())

