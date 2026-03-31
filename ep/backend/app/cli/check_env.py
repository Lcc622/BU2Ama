#!/usr/bin/env python3
"""BU2Ama backend environment validation script."""

from __future__ import annotations

import importlib
import json
import platform
import sys
from pathlib import Path
from typing import Any


STORE_CODES = ("EP", "DM", "PZ")
DEPENDENCIES = ("openpyxl", "fastapi", "pydantic")


def find_project_root() -> Path | None:
    """Locate the repository root by checking for backend/app/config.py."""
    search_roots = [Path.cwd(), Path(__file__).resolve()]

    for start in search_roots:
        current = start if start.is_dir() else start.parent
        for candidate in (current, *current.parents):
            if (candidate / "backend" / "app" / "config.py").exists():
                return candidate
    return None


def check_dependencies() -> tuple[dict[str, str], list[str]]:
    """Return dependency installation states and related errors."""
    dependencies: dict[str, str] = {}
    errors: list[str] = []

    for package_name in DEPENDENCIES:
        try:
            importlib.import_module(package_name)
        except ImportError:
            dependencies[package_name] = "missing"
            errors.append(f"Missing dependency: {package_name}")
        else:
            dependencies[package_name] = "installed"

    return dependencies, errors


def check_required_paths(project_root: Path) -> tuple[dict[str, str], list[str], list[str]]:
    """Check required files and directories."""
    required_paths = {
        "backend/data/colorMapping.json": project_root / "backend" / "data" / "colorMapping.json",
        "backend/uploads/新老款映射信息(1).xlsx": project_root / "backend" / "uploads" / "新老款映射信息(1).xlsx",
        "backend/uploads": project_root / "backend" / "uploads",
        "backend/results": project_root / "backend" / "results",
    }
    files: dict[str, str] = {}
    warnings: list[str] = []
    errors: list[str] = []

    for label, path in required_paths.items():
        exists = path.exists()
        files[label] = "exists" if exists else "missing"
        if exists:
            continue

        if path.suffix:
            errors.append(f"Missing required file: {label}")
        else:
            errors.append(f"Missing required directory: {label}")

    return files, warnings, errors


def check_indexes(project_root: Path) -> tuple[dict[str, dict[str, str]], list[str]]:
    """Check store index database files under backend/uploads."""
    uploads_dir = project_root / "backend" / "uploads"
    indexes: dict[str, dict[str, str]] = {}
    warnings: list[str] = []

    for store_code in STORE_CODES:
        excel_index = uploads_dir / f"excel_index_{store_code}.db"
        ep_index = uploads_dir / f"ep_index_{store_code}.db"
        store_result = {
            "excel_index": "exists" if excel_index.exists() else "missing",
            "ep_index": "exists" if ep_index.exists() else "missing",
        }
        indexes[store_code] = store_result

        missing_items = [name for name, status in store_result.items() if status == "missing"]
        if len(missing_items) == 1:
            warnings.append(f"Store {store_code} index is incomplete: missing {missing_items[0]}.")
        elif len(missing_items) == 2:
            warnings.append(f"Store {store_code} indexes are missing.")

    return indexes, warnings


def check_environment() -> dict[str, Any]:
    """Run all environment checks and return a JSON-serializable result."""
    result: dict[str, Any] = {
        "valid": True,
        "project_root": None,
        "python_version": platform.python_version(),
        "dependencies": {},
        "files": {},
        "indexes": {},
        "warnings": [],
        "errors": [],
    }

    project_root = find_project_root()
    if project_root is None:
        result["valid"] = False
        result["errors"].append("Unable to locate project root via backend/app/config.py.")
        return result

    result["project_root"] = str(project_root)

    dependencies, dependency_errors = check_dependencies()
    result["dependencies"] = dependencies
    result["errors"].extend(dependency_errors)

    files, file_warnings, file_errors = check_required_paths(project_root)
    result["files"] = files
    result["warnings"].extend(file_warnings)
    result["errors"].extend(file_errors)

    indexes, index_warnings = check_indexes(project_root)
    result["indexes"] = indexes
    result["warnings"].extend(index_warnings)

    result["valid"] = not result["errors"]
    return result


def main() -> int:
    """CLI entrypoint."""
    result = check_environment()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
