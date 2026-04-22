#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path


def _repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "pyproject.toml").exists() and (parent / "src").exists():
            return parent
    raise RuntimeError("Could not locate repo root.")


ROOT = _repo_root().resolve()
HOME = Path.home()

TARGETS = [
    ROOT / "artifacts" / "current",
    ROOT / "artifacts" / "legacy_pre_redo",
    ROOT / "docs" / "bucket6_1_public_path_audit.md",
]
TEXT_EXTENSIONS = {".json", ".md", ".csv", ".txt"}

PYTHON_EXE_RE = re.compile(
    r"C:(?:\\|/)+Users(?:\\|/)+naman(?:\\|/)+AppData(?:\\|/)+Local(?:\\|/)+Programs(?:\\|/)+Python(?:\\|/)+Python39(?:\\|/)+python\.exe",
    re.IGNORECASE,
)
REPO_PATH_RE = re.compile(
    r"/?C:(?:\\|/)+Users(?:\\|/)+naman(?:\\|/)+OneDrive(?:\\|/)+Documents(?:\\|/)+GitHub(?:\\|/)+LSPBE-LD-RAG(?:(?:\\|/)+[A-Za-z0-9_. ()-]+)*",
    re.IGNORECASE,
)
HF_CACHE_RE = re.compile(
    r"C:(?:\\|/)+Users(?:\\|/)+naman(?:\\|/)+\.cache(?:\\|/)+huggingface(?:(?:\\|/)+[A-Za-z0-9_. ()~-]+)*",
    re.IGNORECASE,
)


def _normalize_windowsish_path(raw: str) -> str:
    normalized = raw.replace("\\", "/")
    return re.sub(r"/+", "/", normalized)


def _portable_repo_path(raw: str) -> str:
    normalized = _normalize_windowsish_path(raw).lstrip("/")
    prefix = ROOT.as_posix()
    if normalized.lower().startswith(prefix.lower()):
        rel = normalized[len(prefix) :].lstrip("/")
        return rel
    return normalized


def _portable_home_cache_path(raw: str) -> str:
    normalized = _normalize_windowsish_path(raw).lstrip("/")
    prefix = (HOME / ".cache" / "huggingface").as_posix()
    if normalized.lower().startswith(prefix.lower()):
        rel = normalized[len(prefix) :].lstrip("/")
        return "~/.cache/huggingface" + (f"/{rel}" if rel else "")
    return normalized


def sanitize_text(text: str) -> str:
    updated = PYTHON_EXE_RE.sub("python", text)
    updated = REPO_PATH_RE.sub(lambda match: _portable_repo_path(match.group(0)), updated)
    updated = HF_CACHE_RE.sub(lambda match: _portable_home_cache_path(match.group(0)), updated)
    updated = re.sub(r'"repo_root"\s*:\s*""', '"repo_root": "."', updated)
    updated = re.sub(r"- repo_root:\s*``", "- repo_root: `.`", updated)
    updated = updated.replace("artifacts\\", "artifacts/")
    updated = updated.replace("data\\", "data/")
    updated = updated.replace("docs\\", "docs/")
    updated = updated.replace("scripts\\", "scripts/")
    updated = updated.replace("src\\", "src/")
    updated = updated.replace("tests\\", "tests/")
    updated = updated.replace("~\\", "~/")
    return updated


def iter_target_files() -> list[Path]:
    files: list[Path] = []
    for target in TARGETS:
        if target.is_file():
            files.append(target)
            continue
        for path in target.rglob("*"):
            if path.is_file() and path.suffix.lower() in TEXT_EXTENSIONS:
                files.append(path)
    return sorted(set(files))


def main() -> int:
    changed: list[str] = []
    for path in iter_target_files():
        original = path.read_text(encoding="utf-8")
        sanitized = sanitize_text(original)
        if sanitized != original:
            path.write_text(sanitized, encoding="utf-8")
            changed.append(path.relative_to(ROOT).as_posix())

    for relative in changed:
        print(relative)
    print(f"Changed files: {len(changed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
