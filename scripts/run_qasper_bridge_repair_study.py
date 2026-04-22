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

from lspbe.qasper_bridge_repair import (
    attach_baseline_reference,
    build_bridge_repair_comparison,
    build_bridge_repair_comparison_markdown,
    build_bucket4_5_method_specs,
    build_bucket4_5_summary_markdown,
    build_bridge_repair_takeaways_markdown,
    build_stage_markdown,
    default_bridge_repair_config,
    load_bucket4_baseline_validation,
    method_specs_for_stage,
)
from lspbe.qasper_model_selection import (
    BucketLogger,
    prepare_bucket4_bundle,
    run_retrieval_stage,
    write_json,
    write_markdown,
)
from lspbe.run_control import build_run_manifest, utc_now_iso

CURRENT_BUCKET4_5_DIR = ROOT / "artifacts" / "current" / "bucket4_5_bridge_repair"
CURRENT_BUCKET4_DIR = ROOT / "artifacts" / "current" / "bucket4_model_selection"


def parse_args() -> argparse.Namespace:
    defaults = default_bridge_repair_config()
    parser = argparse.ArgumentParser(description="Run the Bucket 4.5 QASPER bridge-repair retrieval study.")
    parser.add_argument("--smoke-dataset-path", default="data/qasper_train_fast50.json")
    parser.add_argument("--validation-dataset-path", default="data/qasper_validation_full.json")
    parser.add_argument(
        "--bucket4-validation-path",
        default=str(CURRENT_BUCKET4_DIR / "qasper_model_selection_validation.json"),
    )
    parser.add_argument("--output-dir", default=str(CURRENT_BUCKET4_5_DIR))
    parser.add_argument("--stage", default="all", choices=["stage1", "stage2", "all"])
    parser.add_argument("--run-scope", default="all", choices=["smoke", "validation", "all"])
    parser.add_argument("--max-smoke-questions", type=int, default=150)
    parser.add_argument("--max-smoke-papers", type=int, default=50)
    parser.add_argument("--max-validation-questions", type=int, default=1_000_000)
    parser.add_argument("--max-validation-papers", type=int, default=1_000_000)
    parser.add_argument("--save-every", type=int, default=int(defaults["save_every"]))
    parser.add_argument("--progress-every-papers", type=int, default=int(defaults["progress_every_papers"]))
    parser.add_argument("--progress-every-seconds", type=int, default=int(defaults["progress_every_seconds"]))
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def _artifact_paths(output_dir: Path) -> dict[str, Path]:
    return {
        "stage1_smoke_json": output_dir / "qasper_bridge_repair_stage1_smoke.json",
        "stage1_smoke_md": output_dir / "qasper_bridge_repair_stage1_smoke.md",
        "stage1_validation_json": output_dir / "qasper_bridge_repair_stage1_validation.json",
        "stage1_validation_md": output_dir / "qasper_bridge_repair_stage1_validation.md",
        "stage2_smoke_json": output_dir / "qasper_bridge_repair_stage2_smoke.json",
        "stage2_smoke_md": output_dir / "qasper_bridge_repair_stage2_smoke.md",
        "stage2_validation_json": output_dir / "qasper_bridge_repair_stage2_validation.json",
        "stage2_validation_md": output_dir / "qasper_bridge_repair_stage2_validation.md",
        "comparison_json": output_dir / "qasper_bridge_repair_comparison.json",
        "comparison_md": output_dir / "qasper_bridge_repair_comparison.md",
        "summary_md": output_dir / "bucket4_5_bridge_repair_summary.md",
        "takeaways_md": output_dir / "bridge_repair_takeaways.md",
        "manifest_json": output_dir / "qasper_bridge_repair.run_manifest.json",
    }


def _load_json_if_exists(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _log_stage_marker(logger: BucketLogger, marker: str, state: str) -> None:
    logger.log(f"stage marker {state} | {marker}")


def _prepare_bundle(
    *,
    logger: BucketLogger,
    marker_name: str,
    dataset_path: str,
    index_specs: dict[str, object],
    method_specs: list[object],
    max_papers: int,
    max_questions: int,
) -> dict[str, object]:
    _log_stage_marker(logger, marker_name, "start")
    bundle = prepare_bucket4_bundle(
        dataset_path,
        max_papers=max_papers,
        max_qas=max_questions,
        index_specs=index_specs,
        method_specs=method_specs,
    )
    logger.log(
        f"loaded retrieval bundle | dataset={dataset_path} | questions={len(bundle['questions'])} | "
        f"papers={len({question.paper_id for question in bundle['questions']})} | "
        f"methods={','.join(method.name for method in method_specs)}"
    )
    _log_stage_marker(logger, marker_name, "end")
    return bundle


def _run_single_stage(
    *,
    logger: BucketLogger,
    bundle: dict[str, object],
    method_specs: list[object],
    stage_name: str,
    cache_root: Path,
    save_every: int,
    progress_every_papers: int,
    progress_every_seconds: int,
    resume: bool,
    overwrite: bool,
    output_json: Path,
    output_md: Path,
    baseline_validation: dict[str, object] | None,
) -> dict[str, object]:
    _log_stage_marker(logger, stage_name, "start")
    payload = run_retrieval_stage(
        stage_name=stage_name,
        bundle=bundle,
        method_specs=method_specs,
        selected_question_ids=[question.question_id for question in bundle["questions"]],
        cache_root=cache_root,
        logger=logger,
        resume=resume,
        overwrite=overwrite,
        save_every=save_every,
        progress_every_papers=progress_every_papers,
        progress_every_seconds=progress_every_seconds,
        screening_subset=None,
    )
    payload["metadata"]["artifact_path"] = str(output_json)
    if baseline_validation is not None:
        payload = attach_baseline_reference(payload, baseline_validation)
    write_json(output_json, payload)
    write_markdown(
        output_md,
        build_stage_markdown(
            title=output_md.stem.replace("_", " ").title(),
            payload=payload,
            baseline_validation=baseline_validation,
        ),
    )
    logger.log(
        f"completed retrieval bundle | stage={stage_name} | output_json={output_json} | output_md={output_md}"
    )
    _log_stage_marker(logger, stage_name, "end")
    return payload


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    logs_dir = output_dir / "logs"
    cache_dir = output_dir / "cache"
    logger = BucketLogger(logs_dir / "qasper_bridge_repair_study.log")
    paths = _artifact_paths(output_dir)

    started_at = utc_now_iso()
    logger.log("starting Bucket 4.5 bridge-repair study")

    _log_stage_marker(logger, "loading baseline artifacts", "start")
    baseline_validation = load_bucket4_baseline_validation(args.bucket4_validation_path)
    logger.log(
        f"loaded prior baseline bundle | source={baseline_validation['source_path']} | "
        "methods=flat_hybrid_current,bridge_final_current"
    )
    _log_stage_marker(logger, "loading baseline artifacts", "end")

    index_specs, all_method_specs = build_bucket4_5_method_specs()

    smoke_bundle = None
    validation_bundle = None
    if args.run_scope in {"smoke", "all"}:
        smoke_bundle = _prepare_bundle(
            logger=logger,
            marker_name="loading smoke retrieval bundle",
            dataset_path=args.smoke_dataset_path,
            index_specs=index_specs,
            method_specs=all_method_specs,
            max_papers=args.max_smoke_papers,
            max_questions=args.max_smoke_questions,
        )
    if args.run_scope in {"validation", "all"}:
        validation_bundle = _prepare_bundle(
            logger=logger,
            marker_name="loading validation retrieval bundle",
            dataset_path=args.validation_dataset_path,
            index_specs=index_specs,
            method_specs=all_method_specs,
            max_papers=args.max_validation_papers,
            max_questions=args.max_validation_questions,
        )

    stage1_smoke_payload = _load_json_if_exists(paths["stage1_smoke_json"])
    stage1_validation_payload = _load_json_if_exists(paths["stage1_validation_json"])
    stage2_smoke_payload = _load_json_if_exists(paths["stage2_smoke_json"])
    stage2_validation_payload = _load_json_if_exists(paths["stage2_validation_json"])

    if args.stage in {"stage1", "all"}:
        stage1_specs = method_specs_for_stage(all_method_specs, "stage1")
        if smoke_bundle is not None:
            stage1_smoke_payload = _run_single_stage(
                logger=logger,
                bundle=smoke_bundle,
                method_specs=stage1_specs,
                stage_name="stage1 smoke retrieval",
                cache_root=cache_dir,
                save_every=args.save_every,
                progress_every_papers=args.progress_every_papers,
                progress_every_seconds=args.progress_every_seconds,
                resume=args.resume,
                overwrite=args.overwrite,
                output_json=paths["stage1_smoke_json"],
                output_md=paths["stage1_smoke_md"],
                baseline_validation=None,
            )
        if validation_bundle is not None:
            stage1_validation_payload = _run_single_stage(
                logger=logger,
                bundle=validation_bundle,
                method_specs=stage1_specs,
                stage_name="stage1 full validation retrieval",
                cache_root=cache_dir,
                save_every=args.save_every,
                progress_every_papers=args.progress_every_papers,
                progress_every_seconds=args.progress_every_seconds,
                resume=args.resume,
                overwrite=args.overwrite,
                output_json=paths["stage1_validation_json"],
                output_md=paths["stage1_validation_md"],
                baseline_validation=baseline_validation,
            )

    if args.stage in {"stage2", "all"}:
        logger.log(
            f"prior stage artifact status | stage1_validation_loaded={'yes' if stage1_validation_payload else 'no'} | "
            f"stage1_smoke_loaded={'yes' if stage1_smoke_payload else 'no'}"
        )
        stage2_specs = method_specs_for_stage(all_method_specs, "stage2")
        if smoke_bundle is not None:
            stage2_smoke_payload = _run_single_stage(
                logger=logger,
                bundle=smoke_bundle,
                method_specs=stage2_specs,
                stage_name="stage2 smoke retrieval",
                cache_root=cache_dir,
                save_every=args.save_every,
                progress_every_papers=args.progress_every_papers,
                progress_every_seconds=args.progress_every_seconds,
                resume=args.resume,
                overwrite=args.overwrite,
                output_json=paths["stage2_smoke_json"],
                output_md=paths["stage2_smoke_md"],
                baseline_validation=None,
            )
        if validation_bundle is not None:
            stage2_validation_payload = _run_single_stage(
                logger=logger,
                bundle=validation_bundle,
                method_specs=stage2_specs,
                stage_name="stage2 full validation retrieval",
                cache_root=cache_dir,
                save_every=args.save_every,
                progress_every_papers=args.progress_every_papers,
                progress_every_seconds=args.progress_every_seconds,
                resume=args.resume,
                overwrite=args.overwrite,
                output_json=paths["stage2_validation_json"],
                output_md=paths["stage2_validation_md"],
                baseline_validation=baseline_validation,
            )

    if stage1_validation_payload is None or stage2_validation_payload is None:
        logger.log("skipping consolidated comparison because stage1 and stage2 validation artifacts are both required")
    else:
        _log_stage_marker(logger, "consolidated comparison writing", "start")
        comparison_payload = build_bridge_repair_comparison(
            baseline_validation=baseline_validation,
            stage1_validation=stage1_validation_payload,
            stage2_validation=stage2_validation_payload,
        )
        write_json(paths["comparison_json"], comparison_payload)
        write_markdown(paths["comparison_md"], build_bridge_repair_comparison_markdown(comparison_payload))
        logger.log(f"wrote comparison artifacts | json={paths['comparison_json']} | md={paths['comparison_md']}")
        _log_stage_marker(logger, "consolidated comparison writing", "end")

        if stage1_smoke_payload is not None and stage2_smoke_payload is not None:
            _log_stage_marker(logger, "final artifact writing", "start")
            write_markdown(
                paths["summary_md"],
                build_bucket4_5_summary_markdown(
                    comparison_payload=comparison_payload,
                    stage1_smoke_payload=stage1_smoke_payload,
                    stage1_validation_payload=stage1_validation_payload,
                    stage2_smoke_payload=stage2_smoke_payload,
                    stage2_validation_payload=stage2_validation_payload,
                ),
            )
            write_markdown(paths["takeaways_md"], build_bridge_repair_takeaways_markdown(comparison_payload))
            logger.log(
                f"wrote final artifacts | summary_md={paths['summary_md']} | takeaways_md={paths['takeaways_md']}"
            )
            _log_stage_marker(logger, "final artifact writing", "end")

    ended_at = utc_now_iso()
    manifest = build_run_manifest(
        script_name=Path(__file__).name,
        started_at=started_at,
        ended_at=ended_at,
        status="completed",
        resumed=bool(args.resume),
        output_paths={name: str(path) for name, path in paths.items()} | {"logs_dir": str(logs_dir)},
        config={
            "smoke_dataset_path": args.smoke_dataset_path,
            "validation_dataset_path": args.validation_dataset_path,
            "bucket4_validation_path": args.bucket4_validation_path,
            "stage": args.stage,
            "run_scope": args.run_scope,
            "max_smoke_questions": args.max_smoke_questions,
            "max_smoke_papers": args.max_smoke_papers,
            "max_validation_questions": args.max_validation_questions,
            "max_validation_papers": args.max_validation_papers,
            "save_every": args.save_every,
            "progress_every_papers": args.progress_every_papers,
            "progress_every_seconds": args.progress_every_seconds,
            "methods": [method.name for method in all_method_specs],
        },
        counters={
            "stage1_smoke_questions": None if stage1_smoke_payload is None else stage1_smoke_payload["metadata"]["questions"],
            "stage1_validation_questions": None if stage1_validation_payload is None else stage1_validation_payload["metadata"]["questions"],
            "stage2_smoke_questions": None if stage2_smoke_payload is None else stage2_smoke_payload["metadata"]["questions"],
            "stage2_validation_questions": None if stage2_validation_payload is None else stage2_validation_payload["metadata"]["questions"],
        },
    )
    write_json(paths["manifest_json"], manifest)
    logger.log("Bucket 4.5 complete")
    print(
        json.dumps(
            {
                "output_dir": str(output_dir),
                "stage1_smoke_completed": stage1_smoke_payload is not None,
                "stage1_validation_completed": stage1_validation_payload is not None,
                "stage2_smoke_completed": stage2_smoke_payload is not None,
                "stage2_validation_completed": stage2_validation_payload is not None,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
