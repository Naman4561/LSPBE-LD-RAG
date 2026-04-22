from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def atomic_write_text(path: str | Path, content: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = target.with_suffix(target.suffix + ".tmp")
    tmp_path.write_text(content, encoding="utf-8")
    if target.exists():
        target.unlink()
    tmp_path.replace(target)


def atomic_write_json(path: str | Path, payload: Any) -> None:
    atomic_write_text(path, json.dumps(payload, indent=2, sort_keys=False))


def append_jsonl(path: str | Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=False) + "\n")


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    target = Path(path)
    if not target.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in target.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def duration_seconds(started_at: str, ended_at: str) -> float:
    started = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
    ended = datetime.fromisoformat(ended_at.replace("Z", "+00:00"))
    return max((ended - started).total_seconds(), 0.0)


_WINDOWS_DRIVE_RE = re.compile(r"^[A-Za-z]:[\\/]")


def portable_path_text(path: str | Path, repo_root: str | Path | None = None) -> str:
    raw = str(path)
    normalized = raw.replace("\\", "/")
    candidate = Path(raw)
    repo = Path(repo_root).resolve() if repo_root is not None else None
    home = Path.home().resolve()

    if candidate.is_absolute():
        resolved = candidate.resolve(strict=False)
        if repo is not None:
            try:
                return resolved.relative_to(repo).as_posix()
            except ValueError:
                pass
        try:
            relative_home = resolved.relative_to(home)
        except ValueError:
            return resolved.as_posix()
        return f"~/{relative_home.as_posix()}"

    if repo is not None and not _WINDOWS_DRIVE_RE.match(raw):
        try:
            resolved = (repo / candidate).resolve(strict=False)
            return resolved.relative_to(repo).as_posix()
        except ValueError:
            return normalized

    return normalized


def sanitize_portable_value(value: Any, repo_root: str | Path | None = None) -> Any:
    if isinstance(value, Path):
        return portable_path_text(value, repo_root=repo_root)
    if isinstance(value, dict):
        return {key: sanitize_portable_value(item, repo_root=repo_root) for key, item in value.items()}
    if isinstance(value, list):
        return [sanitize_portable_value(item, repo_root=repo_root) for item in value]
    if isinstance(value, tuple):
        return [sanitize_portable_value(item, repo_root=repo_root) for item in value]
    if isinstance(value, str):
        looks_path_like = (
            "/" in value
            or "\\" in value
            or value.startswith(".")
            or value.startswith("~")
            or bool(_WINDOWS_DRIVE_RE.match(value))
        )
        return portable_path_text(value, repo_root=repo_root) if looks_path_like else value
    return value


def reset_directory_contents(path: str | Path) -> None:
    root = Path(path)
    root.mkdir(parents=True, exist_ok=True)
    for child in root.iterdir():
        if child.is_dir():
            reset_directory_contents(child)
            child.rmdir()
        else:
            child.unlink()


@dataclass
class IndexedJsonlStore:
    root: Path
    key_field: str
    save_every: int = 10
    records_path: Path = field(init=False)
    state_path: Path = field(init=False)
    metadata_path: Path = field(init=False)
    _records: dict[str, dict[str, Any]] = field(init=False, default_factory=dict)
    _buffer: list[dict[str, Any]] = field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.records_path = self.root / "records.jsonl"
        self.state_path = self.root / "state.json"
        self.metadata_path = self.root / "metadata.json"
        for row in read_jsonl(self.records_path):
            key = str(row[self.key_field])
            self._records[key] = row

    @property
    def completed_keys(self) -> set[str]:
        return set(self._records)

    def reset(self) -> None:
        reset_directory_contents(self.root)
        self._records = {}
        self._buffer = []

    def has(self, key: str) -> bool:
        return key in self._records

    def get(self, key: str) -> dict[str, Any] | None:
        return self._records.get(key)

    def write_metadata(self, payload: dict[str, Any]) -> None:
        atomic_write_json(self.metadata_path, payload)

    def add(self, row: dict[str, Any]) -> None:
        key = str(row[self.key_field])
        self._records[key] = row
        self._buffer.append(row)
        if len(self._buffer) >= self.save_every:
            self.flush()

    def flush(self) -> None:
        if self._buffer:
            append_jsonl(self.records_path, self._buffer)
            self._buffer = []
        atomic_write_json(
            self.state_path,
            {
                "schema_version": 1,
                "key_field": self.key_field,
                "completed_count": len(self._records),
                "completed_keys": sorted(self._records),
                "updated_at": utc_now_iso(),
            },
        )

    def values(self) -> list[dict[str, Any]]:
        return list(self._records.values())


def build_run_manifest(
    *,
    script_name: str,
    started_at: str,
    ended_at: str,
    status: str,
    resumed: bool,
    output_paths: dict[str, str | None],
    config: dict[str, Any],
    counters: dict[str, Any],
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    return {
        "script_name": script_name,
        "started_at": started_at,
        "ended_at": ended_at,
        "duration_seconds": duration_seconds(started_at, ended_at),
        "status": status,
        "resumed": resumed,
        "output_paths": sanitize_portable_value(output_paths, repo_root=repo_root),
        "config": sanitize_portable_value(config, repo_root=repo_root),
        "counters": sanitize_portable_value(counters, repo_root=repo_root),
    }
