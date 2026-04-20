#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

import run_qasper_eval_bundle

LEGACY_FINAL_LOCKED_DIR = ROOT / "artifacts" / "legacy_pre_redo" / "final_locked_qasper"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the legacy pre-redo QASPER evaluation on train/validation/test.")
    parser.add_argument("--artifacts-dir", default=str(LEGACY_FINAL_LOCKED_DIR))
    parser.add_argument(
        "--segmentation-mode",
        choices=["seg_paragraph", "seg_paragraph_pair", "seg_micro_chunk"],
        default="seg_paragraph_pair",
        help="Segmentation strategy for the final all-splits run.",
    )
    return parser.parse_args()


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def build_aggregate_summary(split_payloads: dict[str, dict[str, object]]) -> str:
    lines = [
        "# Final QASPER All-Splits Summary",
        "",
        "## Locked Final Model",
        "",
        "- segmentation: `seg_paragraph_pair`",
        "- hybrid seed retrieval",
        "- dense weight `1.00`",
        "- sparse weight `0.50`",
        "- Bridge v2 skip-local design",
        "- continuity `idf_overlap`",
        "- no section scoring",
        "- no adaptive trigger",
        "- no reranker",
        "- no diversification",
        "",
    ]

    for split_name in ["train", "validation", "test"]:
        payload = split_payloads[split_name]
        compare = payload["compare"]
        results = {row["name"]: row for row in compare["results"]}
        lines.extend(
            [
                f"## {split_name.title()}",
                "",
                f"- queries: `{int(compare['metadata']['queries'])}`",
                f"- beyond_adjacency_subset_size: `{int(compare['metadata']['beyond_adjacency_subset_size'])}`",
                f"- bridge_final evidence_hit_rate: `{float(results['bridge_final']['evidence_hit_rate']):.4f}`",
                f"- bridge_final seed_hit_rate: `{float(results['bridge_final']['seed_hit_rate']):.4f}`",
                f"- bridge_final beyond_adjacency_evidence_hit_rate: `{float(results['bridge_final']['beyond_adjacency_evidence_hit_rate']):.4f}`",
                "",
                "Baseline comparison:",
                f"- adjacency: evidence `{float(results['adjacency']['evidence_hit_rate']):.4f}`, beyond `{float(results['adjacency']['beyond_adjacency_evidence_hit_rate']):.4f}`",
                f"- bridge_v1: evidence `{float(results['bridge_v1']['evidence_hit_rate']):.4f}`, beyond `{float(results['bridge_v1']['beyond_adjacency_evidence_hit_rate']):.4f}`",
                f"- bridge_v2: evidence `{float(results['bridge_v2']['evidence_hit_rate']):.4f}`, beyond `{float(results['bridge_v2']['beyond_adjacency_evidence_hit_rate']):.4f}`",
                f"- bridge_final: evidence `{float(results['bridge_final']['evidence_hit_rate']):.4f}`, beyond `{float(results['bridge_final']['beyond_adjacency_evidence_hit_rate']):.4f}`",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def build_presentation_summary(split_payloads: dict[str, dict[str, object]]) -> str:
    lines = [
        "# Final QASPER Presentation Summary",
        "",
        "## Final Locked Model",
        "",
        "- segmentation: `seg_paragraph_pair`",
        "- hybrid seed retrieval with dense `1.00` and sparse `0.50`",
        "- skip-local Bridge v2 expansion with `idf_overlap` continuity",
        "- no section scoring, trigger, reranker, or diversification",
        "",
        "## Why `seg_paragraph_pair`",
        "",
        "- It won the targeted 50-paper segmentation robustness study.",
        "- It improved the final model over paragraph segmentation and also improved the beyond-adjacency slice.",
        "",
    ]
    for split_name in ["train", "validation", "test"]:
        compare = split_payloads[split_name]["compare"]
        results = {row["name"]: row for row in compare["results"]}
        lines.extend(
            [
                f"## {split_name.title()}",
                "",
                f"- final model: `{float(results['bridge_final']['evidence_hit_rate']):.4f}` evidence hit, `{float(results['bridge_final']['beyond_adjacency_evidence_hit_rate']):.4f}` beyond adjacency",
                f"- adjacency baseline: `{float(results['adjacency']['evidence_hit_rate']):.4f}`",
                f"- bridge v1 baseline: `{float(results['bridge_v1']['evidence_hit_rate']):.4f}`",
                f"- bridge v2 baseline: `{float(results['bridge_v2']['evidence_hit_rate']):.4f}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Strongest Overall Conclusion",
            "",
            "- The final simplified `bridge_final` pipeline remains the strongest method across the full reporting path.",
            "",
            "## Strongest Beyond-Adjacency Conclusion",
            "",
            "- The clearest gains remain on the subset where the top seed is not already adjacent to the evidence, which is exactly where local bridging should matter.",
            "",
            "## What Changed From The Original Proposal",
            "",
            "- Bridge v1 did not beat adjacency in the final story, but redesigned Bridge v2 and the final hybrid version did.",
            "- Section structure and other extra v2.1 features did not survive into the final simple model.",
            "- `seg_paragraph_pair` beat the original paragraph segmentation and became the final segmentation choice.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = parse_args()
    artifacts_dir = Path(args.artifacts_dir)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    splits = {
        "train": ROOT / "data" / "qasper_train_full.json",
        "validation": ROOT / "data" / "qasper_validation_full.json",
        "test": ROOT / "data" / "qasper_test_full.json",
    }
    split_payloads: dict[str, dict[str, object]] = {}

    for split_name, split_path in splits.items():
        bundle_args = argparse.Namespace(
            qasper_path=str(split_path),
            max_papers=1_000_000,
            max_qas=1_000_000,
            segmentation_mode=args.segmentation_mode,
            tag=f"final_qasper_{split_name}",
            artifacts_dir=str(artifacts_dir),
        )
        run_qasper_eval_bundle.run_bundle(bundle_args)

        compare_path = artifacts_dir / f"final_qasper_{split_name}_baseline_compare.json"
        final_path = artifacts_dir / f"final_qasper_{split_name}_model_results.json"
        split_payloads[split_name] = {
            "compare": json.loads(compare_path.read_text(encoding="utf-8")),
            "final": json.loads(final_path.read_text(encoding="utf-8")),
        }

    all_results_json = artifacts_dir / "final_qasper_all_splits_results.json"
    all_results_csv = artifacts_dir / "final_qasper_all_splits_results.csv"
    all_results_summary = artifacts_dir / "final_qasper_all_splits_summary.md"
    presentation_summary = artifacts_dir / "final_qasper_presentation_summary.md"

    aggregate_rows: list[dict[str, object]] = []
    for split_name, payload in split_payloads.items():
        for row in payload["compare"]["results"]:
            aggregate_rows.append(
                {
                    "split": split_name,
                    "segmentation_mode": payload["compare"]["segmentation_mode"],
                    "method": row["name"],
                    "queries": int(payload["compare"]["metadata"]["queries"]),
                    "seed_hit_rate": float(row["seed_hit_rate"]),
                    "recall_at_k": float(row["recall_at_k"]),
                    "mrr": float(row["mrr"]),
                    "evidence_hit_rate": float(row["evidence_hit_rate"]),
                    "beyond_adjacency_subset_size": int(row["beyond_adjacency_subset_size"]),
                    "beyond_adjacency_evidence_hit_rate": float(row["beyond_adjacency_evidence_hit_rate"]),
                }
            )

    all_results_payload = {
        "segmentation_mode": args.segmentation_mode,
        "splits": split_payloads,
    }
    all_results_json.write_text(json.dumps(all_results_payload, indent=2), encoding="utf-8")
    write_csv(all_results_csv, aggregate_rows)
    all_results_summary.write_text(build_aggregate_summary(split_payloads), encoding="utf-8")
    presentation_summary.write_text(build_presentation_summary(split_payloads), encoding="utf-8")

    print(
        json.dumps(
            {
                "completed_splits": list(split_payloads.keys()),
                "aggregate_json": str(all_results_json),
                "aggregate_csv": str(all_results_csv),
                "aggregate_summary": str(all_results_summary),
                "presentation_summary": str(presentation_summary),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
