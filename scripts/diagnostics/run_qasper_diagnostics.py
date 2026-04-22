#!/usr/bin/env python3
from __future__ import annotations

import argparse

import run_bridge_streamlined_section_study as streamlined_section_study
import run_bridge_v21_doc_constrained_sweep as legacy_v21_sweep


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run optional QASPER diagnostic studies.")
    parser.add_argument(
        "--study",
        choices=["streamlined", "legacy_v21"],
        default="streamlined",
        help="Which non-canonical diagnostic study to run.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.study == "streamlined":
        return streamlined_section_study.main()
    return legacy_v21_sweep.main()


if __name__ == "__main__":
    raise SystemExit(main())
