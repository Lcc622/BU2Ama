#!/usr/bin/env python3
"""Shared helpers for backend CLI scripts."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


STORE_CODES = ("EP", "DM", "PZ")
STORE_TO_TEMPLATE = {
    "EP": "EPUS",
    "DM": "DaMaUS",
    "PZ": "PZUS",
}


def find_project_root() -> Path | None:
    """Locate the repository root by checking for backend/app/config.py."""
    search_roots = [Path.cwd(), Path(__file__).resolve()]

    for start in search_roots:
        current = start if start.is_dir() else start.parent
        for candidate in (current, *current.parents):
            if (candidate / "backend" / "app" / "config.py").exists():
                return candidate
    return None


def bootstrap_app() -> Path:
    """Ensure backend package imports work when running scripts directly."""
    project_root = find_project_root()
    if project_root is None:
        raise RuntimeError("Unable to locate project root via backend/app/config.py.")

    backend_root = project_root / "backend"
    backend_root_text = str(backend_root)
    if backend_root_text not in sys.path:
        sys.path.insert(0, backend_root_text)
    return project_root


def normalize_store(store: str | None) -> str:
    """Normalize store code, handling DA -> DM fallback."""
    normalized = str(store or "").strip().upper()
    if normalized == "DA":
        normalized = "DM"
    if normalized not in STORE_CODES:
        raise ValueError(f"Unsupported store: {store}. Expected one of {', '.join(STORE_CODES)}.")
    return normalized


def infer_store_from_filename(filename: str | None) -> str | None:
    """Infer store code from a filename prefix such as EP-0.xlsm."""
    text = str(filename or "").strip().upper()
    for store in STORE_CODES:
        if text.startswith(f"{store}-") or text.startswith(f"{store}_"):
            return store
    if text.startswith("DA-") or text.startswith("DA_") or text.startswith("DM-") or text.startswith("DM_"):
        return "DM"
    if "DAMA" in text:
        return "DM"
    return None


def print_result(result: dict[str, Any], json_mode: bool = False) -> None:
    """Print CLI output in JSON or concise text form."""
    if json_mode:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    print(json.dumps(result, indent=2, ensure_ascii=False))


def count_non_empty_lines(file_path: Path) -> list[str]:
    """Read trimmed, non-empty lines from a UTF-8 text file."""
    values: list[str] = []
    with file_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            value = line.strip()
            if value:
                values.append(value)
    return values
