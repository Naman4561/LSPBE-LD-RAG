from __future__ import annotations

import json
from pathlib import Path

from .qasper import QasperMethodConfig
from .qasper_model_selection import (
    DEFAULT_CONTEXT_BUDGET,
    DEFAULT_PROGRESS_EVERY_PAPERS,
    DEFAULT_PROGRESS_EVERY_SECONDS,
    DEFAULT_SAVE_EVERY,
    Bucket4MethodSpec,
    RetrievalIndexSpec,
    build_retrieval_markdown,
)
from .qasper_protocol import LOCKED_SEGMENTATION_MODE
from .run_control import portable_path_text

TARGET_REPAIR_METHODS = (
    "flat_hybrid_current",
    "bridge_final_current",
    "bridge_from_flat_seeds_current",
    "bridge_from_flat_seeds_selective_current",
)


def build_bucket4_5_method_specs() -> tuple[dict[str, RetrievalIndexSpec], list[Bucket4MethodSpec]]:
    index_specs = {
        "current": RetrievalIndexSpec(
            name="current",
            segmentation_mode=LOCKED_SEGMENTATION_MODE,
            representation_mode="current",
            chunking_mode="paragraph_pair",
            notes="Bucket 4.5 keeps the Bucket 4 mainline representation fixed.",
        )
    }
    method_specs = [
        Bucket4MethodSpec(
            name="bridge_from_flat_seeds_current",
            label="Bridge from flat seeds on current representation",
            family="bridge_repair",
            index_name="current",
            config=QasperMethodConfig(
                name="bridge_from_flat_seeds_current",
                label="Bridge from flat seeds current",
                method="bridge_v21",
                k=DEFAULT_CONTEXT_BUDGET,
                context_budget=DEFAULT_CONTEXT_BUDGET,
                bridge_weights=(1.0, 1.0, 0.0),
                max_skip_distance=2,
                top_per_seed=1,
                seed_retrieval_mode="hybrid",
                seed_dense_weight=1.0,
                seed_sparse_weight=0.5,
                continuity_mode="idf_overlap",
                section_mode="none",
                trigger_mode="always",
                trigger_threshold=0.12,
                local_rerank_mode="none",
                diversify_final_context=False,
                notes=(
                    "Stage 1 repair variant: reuse the exact flat_hybrid_current top-20 hybrid seed stage, "
                    "then apply the bridge_final-style skip-local expansion within the same 20-segment budget."
                ),
            ),
            notes=(
                "Fairness repair: same top-20 hybrid paragraph-pair seeds as flat_hybrid_current, then "
                "bridge-style local expansion with the final context budget still capped at 20."
            ),
        ),
        Bucket4MethodSpec(
            name="bridge_from_flat_seeds_selective_current",
            label="Selective bridge from flat seeds on current representation",
            family="bridge_repair_selective",
            index_name="current",
            config=QasperMethodConfig(
                name="bridge_from_flat_seeds_selective_current",
                label="Bridge from flat seeds selective current",
                method="bridge_v21",
                k=DEFAULT_CONTEXT_BUDGET,
                context_budget=DEFAULT_CONTEXT_BUDGET,
                bridge_weights=(1.0, 1.0, 0.0),
                max_skip_distance=2,
                top_per_seed=1,
                seed_retrieval_mode="hybrid",
                seed_dense_weight=1.0,
                seed_sparse_weight=0.5,
                continuity_mode="idf_overlap",
                section_mode="none",
                trigger_mode="targeted_bridge_repair",
                trigger_threshold=0.12,
                local_rerank_mode="none",
                diversify_final_context=False,
                notes=(
                    "Stage 2 repair variant: same flat seed stage as Stage 1, but only trigger bridge expansion "
                    "for likely nonlocal or uncertain cases using question-form markers plus a small relative seed-gap gate."
                ),
            ),
            notes=(
                "Selective expansion gate: expand for how/which questions, table/figure/compare-style prompts, "
                "or when the top two flat-seed scores are close."
            ),
        ),
    ]
    return index_specs, method_specs


def method_specs_for_stage(
    all_method_specs: list[Bucket4MethodSpec],
    stage_name: str,
) -> list[Bucket4MethodSpec]:
    if stage_name == "stage1":
        return [spec for spec in all_method_specs if spec.name == "bridge_from_flat_seeds_current"]
    if stage_name == "stage2":
        return [spec for spec in all_method_specs if spec.name == "bridge_from_flat_seeds_selective_current"]
    raise ValueError(f"Unsupported Bucket 4.5 stage: {stage_name}")


def load_bucket4_baseline_validation(path: str | Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    path_obj = Path(path)
    repo_root = next((parent for parent in path_obj.resolve(strict=False).parents if (parent / "pyproject.toml").exists()), None)
    methods = {
        row["method"]: row
        for row in payload.get("methods", [])
        if row.get("method") in {"flat_hybrid_current", "bridge_final_current"}
    }
    missing = {"flat_hybrid_current", "bridge_final_current"} - set(methods)
    if missing:
        raise ValueError(f"Missing Bucket 4 baseline methods in {path}: {sorted(missing)}")
    return {
        "source_path": portable_path_text(path_obj, repo_root=repo_root),
        "metadata": payload.get("metadata", {}),
        "methods": methods,
    }


def attach_baseline_reference(
    payload: dict[str, object],
    baseline_validation: dict[str, object],
) -> dict[str, object]:
    copied = json.loads(json.dumps(payload))
    copied.setdefault("metadata", {})
    copied["metadata"]["baseline_reference"] = {
        "source_path": baseline_validation["source_path"],
        "methods": ["flat_hybrid_current", "bridge_final_current"],
        "bucket4_stage": baseline_validation.get("metadata", {}).get("stage"),
    }
    return copied


def build_stage_markdown(
    title: str,
    payload: dict[str, object],
    baseline_validation: dict[str, object] | None = None,
) -> str:
    base = build_retrieval_markdown(title, payload).rstrip()
    if baseline_validation is None:
        return base + "\n"

    lines = [base, "", "## Baseline Reference", ""]
    lines.append(f"- source: `{baseline_validation['source_path']}`")
    for method_name in ("flat_hybrid_current", "bridge_final_current"):
        overall = baseline_validation["methods"][method_name]["overall"]
        first_rank = overall["first_evidence_rank"]
        first_rank_text = "n/a" if first_rank is None else f"{first_rank:.4f}"
        lines.append(
            f"- `{method_name}`: hit `{overall['evidence_hit_rate']:.4f}`, coverage `{overall['evidence_coverage_rate']:.4f}`, "
            f"seed_hit `{overall['seed_hit_rate']:.4f}`, first_rank `{first_rank_text}`"
        )
    return "\n".join(lines).rstrip() + "\n"


def _metric_delta(left: dict[str, object], right: dict[str, object], metric_name: str) -> float | None:
    left_value = left.get(metric_name)
    right_value = right.get(metric_name)
    if left_value is None or right_value is None:
        return None
    return float(left_value) - float(right_value)


def build_bridge_repair_comparison(
    *,
    baseline_validation: dict[str, object],
    stage1_validation: dict[str, object],
    stage2_validation: dict[str, object],
) -> dict[str, object]:
    stage1_method = stage1_validation["methods"][0]
    stage2_method = stage2_validation["methods"][0]
    rows = [
        {
            "method": "flat_hybrid_current",
            "source": "bucket4_baseline",
            "overall": baseline_validation["methods"]["flat_hybrid_current"]["overall"],
            "subset_metrics": baseline_validation["methods"]["flat_hybrid_current"]["subset_metrics"],
            "question_type_metrics": baseline_validation["methods"]["flat_hybrid_current"]["question_type_metrics"],
        },
        {
            "method": "bridge_final_current",
            "source": "bucket4_baseline",
            "overall": baseline_validation["methods"]["bridge_final_current"]["overall"],
            "subset_metrics": baseline_validation["methods"]["bridge_final_current"]["subset_metrics"],
            "question_type_metrics": baseline_validation["methods"]["bridge_final_current"]["question_type_metrics"],
        },
        {
            "method": stage1_method["method"],
            "source": "bucket4_5_stage1",
            "overall": stage1_method["overall"],
            "subset_metrics": stage1_method["subset_metrics"],
            "question_type_metrics": stage1_method["question_type_metrics"],
        },
        {
            "method": stage2_method["method"],
            "source": "bucket4_5_stage2",
            "overall": stage2_method["overall"],
            "subset_metrics": stage2_method["subset_metrics"],
            "question_type_metrics": stage2_method["question_type_metrics"],
        },
    ]
    flat_overall = baseline_validation["methods"]["flat_hybrid_current"]["overall"]
    old_bridge_overall = baseline_validation["methods"]["bridge_final_current"]["overall"]
    stage1_overall = stage1_method["overall"]
    stage2_overall = stage2_method["overall"]
    return {
        "metadata": {
            "baseline_validation_source": baseline_validation["source_path"],
            "stage1_validation_source": stage1_validation["metadata"].get("artifact_path"),
            "stage2_validation_source": stage2_validation["metadata"].get("artifact_path"),
            "representation_mode": "current",
            "segmentation_mode": LOCKED_SEGMENTATION_MODE,
        },
        "methods": rows,
        "deltas": {
            "stage1_vs_flat": {
                "evidence_hit_rate": _metric_delta(stage1_overall, flat_overall, "evidence_hit_rate"),
                "evidence_coverage_rate": _metric_delta(stage1_overall, flat_overall, "evidence_coverage_rate"),
                "seed_hit_rate": _metric_delta(stage1_overall, flat_overall, "seed_hit_rate"),
                "first_evidence_rank": _metric_delta(stage1_overall, flat_overall, "first_evidence_rank"),
            },
            "stage1_vs_old_bridge": {
                "evidence_hit_rate": _metric_delta(stage1_overall, old_bridge_overall, "evidence_hit_rate"),
                "evidence_coverage_rate": _metric_delta(stage1_overall, old_bridge_overall, "evidence_coverage_rate"),
                "seed_hit_rate": _metric_delta(stage1_overall, old_bridge_overall, "seed_hit_rate"),
                "first_evidence_rank": _metric_delta(stage1_overall, old_bridge_overall, "first_evidence_rank"),
            },
            "stage2_vs_stage1": {
                "evidence_hit_rate": _metric_delta(stage2_overall, stage1_overall, "evidence_hit_rate"),
                "evidence_coverage_rate": _metric_delta(stage2_overall, stage1_overall, "evidence_coverage_rate"),
                "seed_hit_rate": _metric_delta(stage2_overall, stage1_overall, "seed_hit_rate"),
                "first_evidence_rank": _metric_delta(stage2_overall, stage1_overall, "first_evidence_rank"),
            },
            "stage2_vs_old_bridge": {
                "evidence_hit_rate": _metric_delta(stage2_overall, old_bridge_overall, "evidence_hit_rate"),
                "evidence_coverage_rate": _metric_delta(stage2_overall, old_bridge_overall, "evidence_coverage_rate"),
                "seed_hit_rate": _metric_delta(stage2_overall, old_bridge_overall, "seed_hit_rate"),
                "first_evidence_rank": _metric_delta(stage2_overall, old_bridge_overall, "first_evidence_rank"),
            },
            "stage2_vs_flat": {
                "evidence_hit_rate": _metric_delta(stage2_overall, flat_overall, "evidence_hit_rate"),
                "evidence_coverage_rate": _metric_delta(stage2_overall, flat_overall, "evidence_coverage_rate"),
                "seed_hit_rate": _metric_delta(stage2_overall, flat_overall, "seed_hit_rate"),
                "first_evidence_rank": _metric_delta(stage2_overall, flat_overall, "first_evidence_rank"),
            },
        },
        "conclusions": {
            "stage1_reused_exact_flat_seed_stage": True,
            "stage1_closed_seed_hit_gap_vs_old_bridge": stage1_overall["seed_hit_rate"] >= flat_overall["seed_hit_rate"],
            "stage1_improved_vs_old_bridge": stage1_overall["evidence_hit_rate"] >= old_bridge_overall["evidence_hit_rate"],
            "stage2_helped_vs_stage1": stage2_overall["evidence_hit_rate"] >= stage1_overall["evidence_hit_rate"]
            and stage2_overall["evidence_coverage_rate"] >= stage1_overall["evidence_coverage_rate"],
            "bucket5_should_remain_flat": flat_overall["evidence_hit_rate"] >= max(
                stage1_overall["evidence_hit_rate"],
                stage2_overall["evidence_hit_rate"],
            ),
        },
    }


def build_bridge_repair_comparison_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# Bucket 4.5 Bridge Repair Comparison",
        "",
        f"- baseline_validation_source: `{payload['metadata']['baseline_validation_source']}`",
        f"- stage1_validation_source: `{payload['metadata']['stage1_validation_source']}`",
        f"- stage2_validation_source: `{payload['metadata']['stage2_validation_source']}`",
        "",
        "## Overall",
        "",
    ]
    for row in payload["methods"]:
        overall = row["overall"]
        first_rank = overall["first_evidence_rank"]
        first_rank_text = "n/a" if first_rank is None else f"{first_rank:.4f}"
        lines.append(
            f"- `{row['method']}` ({row['source']}): hit `{overall['evidence_hit_rate']:.4f}`, "
            f"coverage `{overall['evidence_coverage_rate']:.4f}`, seed_hit `{overall['seed_hit_rate']:.4f}`, "
            f"first_rank `{first_rank_text}`"
        )
    lines.extend(["", "## Key Deltas", ""])
    for name, metrics in payload["deltas"].items():
        first_rank_value = metrics["first_evidence_rank"]
        first_rank_text = "n/a" if first_rank_value is None else f"{first_rank_value:+.4f}"
        lines.append(
            f"- `{name}`: hit `{metrics['evidence_hit_rate']:+.4f}`, coverage `{metrics['evidence_coverage_rate']:+.4f}`, "
            f"seed_hit `{metrics['seed_hit_rate']:+.4f}`, first_rank `{first_rank_text}`"
        )
    lines.extend(
        [
            "",
            "## Decision Flags",
            "",
            f"- stage1_reused_exact_flat_seed_stage: `{payload['conclusions']['stage1_reused_exact_flat_seed_stage']}`",
            f"- stage1_closed_seed_hit_gap_vs_old_bridge: `{payload['conclusions']['stage1_closed_seed_hit_gap_vs_old_bridge']}`",
            f"- stage1_improved_vs_old_bridge: `{payload['conclusions']['stage1_improved_vs_old_bridge']}`",
            f"- stage2_helped_vs_stage1: `{payload['conclusions']['stage2_helped_vs_stage1']}`",
            f"- bucket5_should_remain_flat: `{payload['conclusions']['bucket5_should_remain_flat']}`",
            "",
        ]
    )
    return "\n".join(lines)


def build_bucket4_5_summary_markdown(
    *,
    comparison_payload: dict[str, object],
    stage1_smoke_payload: dict[str, object],
    stage1_validation_payload: dict[str, object],
    stage2_smoke_payload: dict[str, object],
    stage2_validation_payload: dict[str, object],
) -> str:
    stage1 = stage1_validation_payload["methods"][0]["overall"]
    stage2 = stage2_validation_payload["methods"][0]["overall"]
    flat = comparison_payload["methods"][0]["overall"]
    old_bridge = comparison_payload["methods"][1]["overall"]
    stage2_helped = comparison_payload["conclusions"]["stage2_helped_vs_stage1"]
    lines = [
        "# Bucket 4.5 Bridge Repair Summary",
        "",
        "## Implementation",
        "",
        "- Stage 1 method: `bridge_from_flat_seeds_current`",
        "- Stage 1 seed reuse: exact same `flat_hybrid_current` top-20 hybrid paragraph-pair seed stage and same final 20-segment context budget.",
        "- Stage 1 bridge behavior: `bridge_final`-style skip-local expansion on top of those flat seeds using `idf_overlap`, no section scoring, and no reranker.",
        "- Stage 2 method: `bridge_from_flat_seeds_selective_current`",
        "- Stage 2 selective rule: expand only for `how` / `which` questions, table-or-figure style prompts, or low-separation seed rankings where the top-two relative gap is below `0.12`.",
        "",
        "## Retrieval Outcome",
        "",
        f"- prior `flat_hybrid_current`: hit `{flat['evidence_hit_rate']:.4f}`, coverage `{flat['evidence_coverage_rate']:.4f}`, seed_hit `{flat['seed_hit_rate']:.4f}`",
        f"- prior `bridge_final_current`: hit `{old_bridge['evidence_hit_rate']:.4f}`, coverage `{old_bridge['evidence_coverage_rate']:.4f}`, seed_hit `{old_bridge['seed_hit_rate']:.4f}`",
        f"- Stage 1 `bridge_from_flat_seeds_current`: hit `{stage1['evidence_hit_rate']:.4f}`, coverage `{stage1['evidence_coverage_rate']:.4f}`, seed_hit `{stage1['seed_hit_rate']:.4f}`",
        f"- Stage 2 `bridge_from_flat_seeds_selective_current`: hit `{stage2['evidence_hit_rate']:.4f}`, coverage `{stage2['evidence_coverage_rate']:.4f}`, seed_hit `{stage2['seed_hit_rate']:.4f}`",
        "",
        "## Conclusion",
        "",
        (
            "- Weak bridge seeds were a real fairness problem because Stage 1 exactly inherits flat's seed hit rate by construction."
            if stage1["seed_hit_rate"] >= flat["seed_hit_rate"]
            else "- Stage 1 did not fully inherit flat's seed advantage, so there is still a seed-stage mismatch to investigate."
        ),
        (
            "- Always-on bridge expansion still did not fully close the flat gap once the seed stage was repaired."
            if stage1["evidence_hit_rate"] < flat["evidence_hit_rate"]
            else "- Once seeds were matched to flat, always-on bridge expansion became competitive with flat."
        ),
        (
            "- Selective expansion helped over always-on expansion."
            if stage2_helped
            else "- Selective expansion did not beat the always-on Stage 1 repair variant."
        ),
        (
            "- Bucket 5 should remain unchanged with `flat_hybrid_current` as the selected path."
            if comparison_payload["conclusions"]["bucket5_should_remain_flat"]
            else "- Bucket 5 should be revisited because a repaired bridge variant matched or beat the current flat winner."
        ),
        "",
        "## Run Status",
        "",
        f"- Stage 1 smoke questions: `{stage1_smoke_payload['metadata']['questions']}`",
        f"- Stage 1 validation questions: `{stage1_validation_payload['metadata']['questions']}`",
        f"- Stage 2 smoke questions: `{stage2_smoke_payload['metadata']['questions']}`",
        f"- Stage 2 validation questions: `{stage2_validation_payload['metadata']['questions']}`",
        "",
    ]
    return "\n".join(lines)


def build_bridge_repair_takeaways_markdown(comparison_payload: dict[str, object]) -> str:
    stage1_vs_old = comparison_payload["deltas"]["stage1_vs_old_bridge"]
    stage2_vs_stage1 = comparison_payload["deltas"]["stage2_vs_stage1"]
    stage2_vs_flat = comparison_payload["deltas"]["stage2_vs_flat"]
    lines = [
        "# Bridge Repair Takeaways",
        "",
        f"- Stage 1 vs old bridge: hit `{stage1_vs_old['evidence_hit_rate']:+.4f}`, coverage `{stage1_vs_old['evidence_coverage_rate']:+.4f}`, seed_hit `{stage1_vs_old['seed_hit_rate']:+.4f}`.",
        f"- Stage 2 vs Stage 1: hit `{stage2_vs_stage1['evidence_hit_rate']:+.4f}`, coverage `{stage2_vs_stage1['evidence_coverage_rate']:+.4f}`, seed_hit `{stage2_vs_stage1['seed_hit_rate']:+.4f}`.",
        f"- Stage 2 vs flat: hit `{stage2_vs_flat['evidence_hit_rate']:+.4f}`, coverage `{stage2_vs_flat['evidence_coverage_rate']:+.4f}`, seed_hit `{stage2_vs_flat['seed_hit_rate']:+.4f}`.",
        "- Interpretation: Bucket 4.5 is retrieval-only, so these takeaways are intentionally limited to evidence hit, coverage, seed hit, and seed-rank behavior.",
        "",
    ]
    return "\n".join(lines)


def default_bridge_repair_config() -> dict[str, object]:
    return {
        "save_every": DEFAULT_SAVE_EVERY,
        "progress_every_papers": DEFAULT_PROGRESS_EVERY_PAPERS,
        "progress_every_seconds": DEFAULT_PROGRESS_EVERY_SECONDS,
        "context_budget": DEFAULT_CONTEXT_BUDGET,
        "stage2_trigger_threshold": 0.12,
    }
