#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "artifacts" / "current" / "environment"


def candidate_cache_roots() -> list[Path]:
    roots: list[Path] = []
    env_values = [os.environ.get("HF_HOME"), os.environ.get("TRANSFORMERS_CACHE")]
    for value in env_values:
        if value:
            roots.append(Path(value))
    roots.append(Path.home() / ".cache" / "huggingface")

    resolved: list[Path] = []
    for root in roots:
        if root.name == "hub":
            resolved.append(root)
        else:
            resolved.extend([root, root / "hub"])

    unique: list[Path] = []
    seen: set[str] = set()
    for path in resolved:
        key = str(path.resolve()) if path.exists() else str(path)
        if key not in seen:
            seen.add(key)
            unique.append(path)
    return unique


def classify_model(repo_name: str, snapshot_dir: Path, config_payload: dict[str, object]) -> str:
    lowered = repo_name.lower()
    architectures = " ".join(str(item).lower() for item in config_payload.get("architectures", []))
    model_type = str(config_payload.get("model_type", "")).lower()
    if (snapshot_dir / "modules.json").exists() or any(token in lowered for token in ("bge", "gte", "e5", "minilm", "mpnet", "sentence")):
        return "embeddings"
    if "questionanswering" in architectures or "question-answering" in lowered:
        return "qa"
    if any(token in architectures for token in ("causallm", "seq2seqlm")) or any(token in model_type for token in ("t5", "bart", "gpt", "llama", "mistral")):
        return "generation"
    return "unknown"


def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    try:
        from transformers import AutoConfig, AutoTokenizer
    except Exception as exc:
        payload = {
            "cache_roots": [str(path) for path in candidate_cache_roots()],
            "transformers_available": False,
            "error": f"{type(exc).__name__}: {exc}",
            "models": [],
        }
        (ARTIFACT_DIR / "local_model_audit.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
        (ARTIFACT_DIR / "local_model_audit.md").write_text(
            "# Local Model Audit\n\n- transformers_available: `False`\n- models_found: `0`\n",
            encoding="utf-8",
        )
        return 0

    models: list[dict[str, object]] = []
    for root in candidate_cache_roots():
        if not root.exists():
            continue
        for model_root in sorted(root.glob("models--*")):
            snapshots_dir = model_root / "snapshots"
            if not snapshots_dir.exists():
                continue
            snapshot_candidates = [path for path in snapshots_dir.iterdir() if path.is_dir()]
            if not snapshot_candidates:
                continue
            snapshot_dir = sorted(snapshot_candidates)[-1]
            repo_name = model_root.name.replace("models--", "").replace("--", "/")
            config_path = snapshot_dir / "config.json"
            config_payload: dict[str, object] = {}
            if config_path.exists():
                try:
                    config_payload = json.loads(config_path.read_text(encoding="utf-8"))
                except Exception:
                    config_payload = {}

            config_status = {"ok": False, "error": None}
            tokenizer_status = {"ok": False, "error": None}
            try:
                AutoConfig.from_pretrained(snapshot_dir, local_files_only=True, trust_remote_code=False)
                config_status = {"ok": True, "error": None}
            except Exception as exc:
                config_status = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}

            try:
                AutoTokenizer.from_pretrained(snapshot_dir, local_files_only=True, trust_remote_code=False)
                tokenizer_status = {"ok": True, "error": None}
            except Exception as exc:
                tokenizer_status = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}

            models.append(
                {
                    "repo_name": repo_name,
                    "cache_root": str(root),
                    "snapshot_dir": str(snapshot_dir),
                    "classification": classify_model(repo_name, snapshot_dir, config_payload),
                    "offline_load": {
                        "config": config_status,
                        "tokenizer": tokenizer_status,
                    },
                    "has_modules_json": (snapshot_dir / "modules.json").exists(),
                    "has_config_json": config_path.exists(),
                    "model_type": config_payload.get("model_type"),
                    "architectures": config_payload.get("architectures", []),
                }
            )

    summary = {
        "cache_roots": [str(path) for path in candidate_cache_roots()],
        "transformers_available": True,
        "models_found": len(models),
        "class_counts": {
            "embeddings": sum(model["classification"] == "embeddings" for model in models),
            "qa": sum(model["classification"] == "qa" for model in models),
            "generation": sum(model["classification"] == "generation" for model in models),
            "unknown": sum(model["classification"] == "unknown" for model in models),
        },
        "models": models,
    }

    markdown_lines = [
        "# Local Model Audit",
        "",
        f"- transformers_available: `{summary['transformers_available']}`",
        f"- models_found: `{summary['models_found']}`",
        f"- class_counts: `{json.dumps(summary['class_counts'], sort_keys=True)}`",
        "",
        "## Models",
        "",
    ]
    if models:
        for model in models:
            markdown_lines.extend(
                [
                    f"### {model['repo_name']}",
                    "",
                    f"- classification: `{model['classification']}`",
                    f"- snapshot_dir: `{model['snapshot_dir']}`",
                    f"- offline_config_ok: `{model['offline_load']['config']['ok']}`",
                    f"- offline_tokenizer_ok: `{model['offline_load']['tokenizer']['ok']}`",
                    "",
                ]
            )
    else:
        markdown_lines.append("- No cached local models were discovered in the inspected Hugging Face cache roots.")
        markdown_lines.append("")

    (ARTIFACT_DIR / "local_model_audit.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (ARTIFACT_DIR / "local_model_audit.md").write_text("\n".join(markdown_lines), encoding="utf-8")
    print(json.dumps({"json": str(ARTIFACT_DIR / "local_model_audit.json"), "md": str(ARTIFACT_DIR / "local_model_audit.md")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
