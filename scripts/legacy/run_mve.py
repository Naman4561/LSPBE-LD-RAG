#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

from lspbe.mve import run_mve


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run LSPBE MVE on a QASPER subset.")
    parser.add_argument("--qasper-path", required=True, help="Path to QASPER JSON subset file")
    parser.add_argument("--max-papers", type=int, default=100)
    parser.add_argument("--max-qas", type=int, default=300)
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--radius", type=int, default=1)
    parser.add_argument("--top-m", type=int, default=2)
    parser.add_argument("--context-budget", type=int, default=20)
    parser.add_argument("--embedder", choices=["bge", "hash"], default="bge")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = run_mve(
        qasper_path=args.qasper_path,
        max_papers=args.max_papers,
        max_qas=args.max_qas,
        k=args.k,
        radius=args.radius,
        top_m=args.top_m,
        context_budget=args.context_budget,
        embedder=args.embedder,
    )
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
