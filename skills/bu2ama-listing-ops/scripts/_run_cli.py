#!/usr/bin/env python3
"""Dispatch skill wrapper scripts to BU2Ama backend CLI entrypoints."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def find_project_root() -> Path:
    """Locate the BU2Ama repo root from env, cwd, or wrapper location."""
    candidates: list[Path] = []

    env_root = os.getenv("BU2AMA_ROOT")
    if env_root:
        candidates.append(Path(env_root).expanduser().resolve())

    cwd = Path.cwd().resolve()
    candidates.extend([cwd, *cwd.parents])

    wrapper_path = Path(__file__).resolve()
    candidates.extend([wrapper_path.parent, *wrapper_path.parents])

    seen: set[Path] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        if (candidate / "backend" / "app" / "config.py").exists():
            return candidate

    raise SystemExit(
        "Unable to locate the BU2Ama project root. Run the command from the BU2Ama repo "
        "or set BU2AMA_ROOT=/absolute/path/to/BU2Ama."
    )


def stage_media_file(file_path: str) -> str:
    """Copy exported files into an OpenClaw-approved local media directory."""
    source = Path(file_path).expanduser().resolve()
    if not source.exists() or not source.is_file():
        return file_path

    media_root = Path.home() / ".openclaw" / "media" / "bu2ama"
    media_root.mkdir(parents=True, exist_ok=True)

    target = media_root / source.name
    if target.exists():
        target = media_root / f"{source.stem}_{source.stat().st_mtime_ns}{source.suffix}"

    shutil.copy2(source, target)
    return str(target)


def rewrite_export_paths(payload: object) -> object:
    """Rewrite known export file paths so Telegram can attach them."""
    if not isinstance(payload, dict):
        return payload

    output_file = payload.get("output_file")
    if isinstance(output_file, str):
        staged = stage_media_file(output_file)
        if staged != output_file:
            payload["original_output_file"] = output_file
            payload["output_file"] = staged

    export = payload.get("export")
    if isinstance(export, dict):
        export_output = export.get("output_file")
        if isinstance(export_output, str):
            staged = stage_media_file(export_output)
            if staged != export_output:
                export["original_output_file"] = export_output
                export["output_file"] = staged

    return payload


def run_cli(script_name: str) -> int:
    """Run a backend/app/cli script with the current Python interpreter."""
    project_root = find_project_root()
    target = project_root / "backend" / "app" / "cli" / script_name
    if not target.exists():
        raise SystemExit(f"CLI script not found: {target}")

    wants_json = "--json" in sys.argv[1:]
    completed = subprocess.run(
        [sys.executable, str(target), *sys.argv[1:]],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )

    stdout = completed.stdout
    if wants_json and completed.returncode == 0 and stdout.strip():
        try:
            payload = json.loads(stdout)
        except json.JSONDecodeError:
            pass
        else:
            stdout = json.dumps(rewrite_export_paths(payload), ensure_ascii=False, indent=2)
            if not stdout.endswith("\n"):
                stdout += "\n"

    if stdout:
        sys.stdout.write(stdout)
    if completed.stderr:
        sys.stderr.write(completed.stderr)
    return int(completed.returncode)
