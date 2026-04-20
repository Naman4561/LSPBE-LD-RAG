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

CURRENT_BUCKET1_DIR = ROOT / "artifacts" / "current" / "bucket1_protocol"

from lspbe.qasper import ADJACENCY_BASELINE, BRIDGE_FINAL, BRIDGE_V2_BASELINE
from lspbe.qasper_eval import evaluate_methods_detailed, load_qasper_eval_context, write_json
from lspbe.qasper_protocol import LOCKED_SEGMENTATION_MODE


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the serious-redo QASPER protocol sanity check.")
    parser.add_argument("--train-fast50-path", default=str(ROOT / "data" / "qasper_train_fast50.json"))
    parser.add_argument("--validation-path", default=str(ROOT / "data" / "qasper_validation_full.json"))
    parser.add_argument("--segmentation-mode", default=LOCKED_SEGMENTATION_MODE)
    parser.add_argument("--also-validation", action="store_true")
    return parser.parse_args()


def build_markdown(split_name: str, results: list[dict[str, object]], metadata: dict[str, object]) -> str:
    by_name = {row["name"]: row for row in results}
    lines = [
        f"# QASPER Protocol Sanity Check ({split_name})",
        "",
        f"- segmentation_mode: `{metadata['segmentation_mode']}`",
        f"- queries: `{metadata['queries']}`",
        f"- subset_counts: `{json.dumps(metadata['subset_counts'], sort_keys=True)}`",
        "",
        "## Headline Metrics",
        "",
    ]
    for name in ("adjacency", "bridge_v2", "bridge_final"):
        row = by_name[name]
        lines.extend(
            [
                f"### {name}",
                "",
                f"- evidence_hit_rate: `{row['evidence_hit_rate']:.4f}`",
                f"- evidence_coverage_rate: `{row['evidence_coverage_rate']:.4f}`",
                f"- seed_hit_rate: `{row['seed_hit_rate']:.4f}`",
                f"- first_evidence_rank: `{row['first_evidence_rank'] if row['first_evidence_rank'] is not None else 'null'}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Hard Subsets",
            "",
        ]
    )
    for subset_name in ("adjacency_easy", "skip_local", "multi_span", "float_table"):
        lines.append(f"### {subset_name}")
        lines.append("")
        for name in ("adjacency", "bridge_v2", "bridge_final"):
            subset_row = by_name[name]["subset_metrics"].get(subset_name)
            if not subset_row:
                continue
            lines.append(
                f"- `{name}`: queries `{int(subset_row['queries'])}`, evidence `{subset_row['evidence_hit_rate']:.4f}`, "
                f"coverage `{subset_row['evidence_coverage_rate']:.4f}`, seed `{subset_row['seed_hit_rate']:.4f}`"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def run_one(split_name: str, path: str, segmentation_mode: str) -> dict[str, object]:
    context = load_qasper_eval_context(
        path,
        max_papers=1_000_000,
        max_qas=1_000_000,
        segmentation_mode=segmentation_mode,
    )
    results, metadata = evaluate_methods_detailed(
        context,
        [ADJACENCY_BASELINE, BRIDGE_V2_BASELINE, BRIDGE_FINAL],
    )
    return {
        "split": split_name,
        "path": path,
        "segmentation_mode": segmentation_mode,
        "results": results,
        "metadata": metadata,
    }


def main() -> int:
    args = parse_args()
    train_payload = run_one("train_fast50", args.train_fast50_path, args.segmentation_mode)
    train_json = CURRENT_BUCKET1_DIR / "qasper_protocol_sanity_check_train_fast50.json"
    train_md = CURRENT_BUCKET1_DIR / "qasper_protocol_sanity_check_train_fast50.md"
    write_json(train_json, train_payload)
    train_md.write_text(
        build_markdown("train_fast50", train_payload["results"], train_payload["metadata"]),
        encoding="utf-8",
    )

    outputs = {"train_fast50_json": str(train_json), "train_fast50_md": str(train_md)}
    if args.also_validation:
        validation_payload = run_one("validation", args.validation_path, args.segmentation_mode)
        validation_json = CURRENT_BUCKET1_DIR / "qasper_protocol_sanity_check_validation.json"
        validation_md = CURRENT_BUCKET1_DIR / "qasper_protocol_sanity_check_validation.md"
        write_json(validation_json, validation_payload)
        validation_md.write_text(
            build_markdown("validation", validation_payload["results"], validation_payload["metadata"]),
            encoding="utf-8",
        )
        outputs["validation_json"] = str(validation_json)
        outputs["validation_md"] = str(validation_md)

    print(json.dumps(outputs, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
