#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import platform
import re
import shutil
import subprocess
import sys
from importlib import metadata
from pathlib import Path

def _repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "pyproject.toml").exists() and (parent / "src").exists():
            return parent
    raise RuntimeError("Could not locate repo root.")


ROOT = _repo_root()
ARTIFACT_DIR = ROOT / "artifacts" / "current" / "environment"


def read_python_requirement() -> str | None:
    pyproject = ROOT / "pyproject.toml"
    if not pyproject.exists():
        return None
    match = re.search(r'requires-python\s*=\s*"([^"]+)"', pyproject.read_text(encoding="utf-8"))
    return match.group(1) if match else None


def python_satisfies(requirement: str | None) -> bool | None:
    if requirement is None:
        return None
    match = re.fullmatch(r">=\s*(\d+)\.(\d+)", requirement.strip())
    if not match:
        return None
    major = int(match.group(1))
    minor = int(match.group(2))
    return sys.version_info[:2] >= (major, minor)


def package_version(name: str) -> dict[str, object]:
    try:
        return {"installed": True, "version": metadata.version(name)}
    except metadata.PackageNotFoundError:
        return {"installed": False, "version": None}


def run_command(args: list[str], cwd: Path) -> dict[str, object]:
    try:
        completed = subprocess.run(args, cwd=str(cwd), capture_output=True, text=True, check=False)
        return {
            "ok": completed.returncode == 0,
            "returncode": completed.returncode,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
            "command": args,
        }
    except Exception as exc:
        return {
            "ok": False,
            "returncode": None,
            "stdout": "",
            "stderr": f"{type(exc).__name__}: {exc}",
            "command": args,
        }


def write_outputs(payload: dict[str, object], markdown: str) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    (ARTIFACT_DIR / "env_preflight_report.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (ARTIFACT_DIR / "env_preflight_report.md").write_text(markdown, encoding="utf-8")


def main() -> int:
    packages = {
        "pytest": package_version("pytest"),
        "numpy": package_version("numpy"),
        "torch": package_version("torch"),
        "transformers": package_version("transformers"),
        "datasets": package_version("datasets"),
        "sentence-transformers": package_version("sentence-transformers"),
        "scikit-learn": package_version("scikit-learn"),
    }
    pytest_cli = run_command(["pytest", "--version"], ROOT)
    pytest_module = run_command([sys.executable, "-m", "pytest", "--version"], ROOT)
    git_status = run_command(["git", "status", "--short"], ROOT)

    key_dataset_files = {
        "train_fast50": ROOT / "data" / "qasper_train_fast50.json",
        "validation": ROOT / "data" / "qasper_validation_full.json",
        "test": ROOT / "data" / "qasper_test_full.json",
        "train_dev": ROOT / "data" / "qasper_train_dev.json",
        "train_lockbox": ROOT / "data" / "qasper_train_lockbox.json",
    }
    active_artifact_dirs = {
        "bucket1_protocol": ROOT / "artifacts" / "current" / "bucket1_protocol",
        "manual_review": ROOT / "artifacts" / "current" / "manual_review",
        "bucket2_answer_eval": ROOT / "artifacts" / "current" / "bucket2_answer_eval",
        "bucket2_cache": ROOT / "artifacts" / "current" / "bucket2_answer_eval" / "cache",
        "environment": ARTIFACT_DIR,
    }

    disk_root = shutil.disk_usage(ROOT)
    python_requirement = read_python_requirement()
    python_requirement_ok = python_satisfies(python_requirement)
    healthy = all(
        [
            ROOT.exists(),
            git_status["ok"],
            python_requirement_ok is not False,
            packages["numpy"]["installed"],
            packages["torch"]["installed"],
            packages["transformers"]["installed"],
            packages["datasets"]["installed"],
            active_artifact_dirs["bucket2_answer_eval"].exists(),
        ]
    )

    notes: list[str] = []
    if not pytest_cli["ok"] and not pytest_module["ok"]:
        notes.append("`pytest` is not runnable in this runtime. Use direct Python smoke checks until it is installed into the active interpreter.")
    if not git_status["ok"]:
        notes.append("`git status` failed in this runtime; repository cleanliness checks are degraded.")
    if python_requirement_ok is False:
        notes.append(
            f"The active interpreter is Python {sys.version_info.major}.{sys.version_info.minor}, "
            f"but `pyproject.toml` requires `{python_requirement}`."
        )
    if not healthy:
        notes.append("The environment is not fully healthy for long runs. Inspect the failing checks before starting a heavy job.")

    payload = {
        "repo_root": str(ROOT),
        "python": {
            "executable": sys.executable,
            "version": sys.version,
            "version_info": list(sys.version_info[:3]),
            "requires_python": python_requirement,
            "requires_python_satisfied": python_requirement_ok,
        },
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        },
        "packages": packages,
        "commands": {
            "pytest_cli": pytest_cli,
            "pytest_module": pytest_module,
            "git_status": git_status,
        },
        "environment_variables": {
            "HF_HOME": os.environ.get("HF_HOME"),
            "TRANSFORMERS_CACHE": os.environ.get("TRANSFORMERS_CACHE"),
            "HF_HUB_OFFLINE": os.environ.get("HF_HUB_OFFLINE"),
            "TRANSFORMERS_OFFLINE": os.environ.get("TRANSFORMERS_OFFLINE"),
        },
        "key_dataset_files": {name: {"path": str(path), "exists": path.exists()} for name, path in key_dataset_files.items()},
        "active_artifact_dirs": {name: {"path": str(path), "exists": path.exists()} for name, path in active_artifact_dirs.items()},
        "disk_space": {
            "total_bytes": disk_root.total,
            "used_bytes": disk_root.used,
            "free_bytes": disk_root.free,
        },
        "repo_healthy_for_long_runs": healthy,
        "notes": notes,
    }

    markdown = "\n".join(
        [
            "# Environment Preflight",
            "",
            f"- repo_root: `{payload['repo_root']}`",
            f"- python_executable: `{payload['python']['executable']}`",
            f"- python_version: `{payload['python']['version_info']}`",
            f"- requires_python: `{payload['python']['requires_python']}`",
            f"- requires_python_satisfied: `{payload['python']['requires_python_satisfied']}`",
            f"- platform: `{payload['platform']['system']} {payload['platform']['release']} {payload['platform']['machine']}`",
            f"- repo_healthy_for_long_runs: `{payload['repo_healthy_for_long_runs']}`",
            f"- pytest_cli_ok: `{payload['commands']['pytest_cli']['ok']}`",
            f"- pytest_module_ok: `{payload['commands']['pytest_module']['ok']}`",
            f"- git_status_ok: `{payload['commands']['git_status']['ok']}`",
            f"- HF_HOME: `{payload['environment_variables']['HF_HOME']}`",
            f"- TRANSFORMERS_CACHE: `{payload['environment_variables']['TRANSFORMERS_CACHE']}`",
            f"- disk_free_bytes: `{payload['disk_space']['free_bytes']}`",
            "",
            "## Packages",
            "",
        ]
        + [
            f"- `{name}`: installed `{info['installed']}`, version `{info['version']}`"
            for name, info in payload["packages"].items()
        ]
        + [
            "",
            "## Dataset Files",
            "",
        ]
        + [
            f"- `{name}`: exists `{info['exists']}` at `{info['path']}`"
            for name, info in payload["key_dataset_files"].items()
        ]
        + [
            "",
            "## Notes",
            "",
        ]
        + ([f"- {note}" for note in notes] if notes else ["- No blocking preflight notes."])
        + [""]
    )

    write_outputs(payload, markdown)
    print(json.dumps({"json": str(ARTIFACT_DIR / "env_preflight_report.json"), "md": str(ARTIFACT_DIR / "env_preflight_report.md")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

