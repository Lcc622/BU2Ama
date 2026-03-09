#!/usr/bin/env python3
"""文件上传 CLI 入口。"""

from __future__ import annotations

import argparse
import contextlib
import io
import shutil
import sys
from pathlib import Path

from utils import bootstrap_app, infer_store_from_filename, normalize_store, print_result

bootstrap_app()

from app.config import UPLOADS_DIR


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="上传源文件到 uploads 目录")
    parser.add_argument("--file", required=True, help="待上传文件路径")
    parser.add_argument("--store", choices=["EP", "DM", "PZ"], help="店铺代码")
    parser.add_argument("--rebuild-index", action="store_true", help="上传后重建索引")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    return parser


def rebuild_indexes(store: str) -> int:
    """Rebuild Excel and follow-sell indexes for the selected store."""
    with contextlib.redirect_stdout(io.StringIO()):
        from app.core.excel_processor import ExcelProcessor
        from app.core.follow_sell_processor import FollowSellProcessor
        excel_processor = ExcelProcessor()
        follow_sell_processor = FollowSellProcessor()

        store_files = excel_processor._build_store_data_files([], store).get(store, [])  # noqa: SLF001
        if store_files:
            excel_processor._build_source_index_cached(store_files, store)  # noqa: SLF001
        follow_sell_processor._ensure_store_index(store)  # noqa: SLF001
        conn = follow_sell_processor._connect_db(store)  # noqa: SLF001
    try:
        row = conn.execute(
            "SELECT COUNT(DISTINCT sku) FROM ep_sku_index WHERE store_prefix = ?",
            (store,),
        ).fetchone()
    finally:
        conn.close()
    return int(row[0]) if row and row[0] is not None else 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    result = {
        "success": False,
        "file_saved": None,
        "store": None,
        "index_rebuilt": False,
        "sku_count": 0,
        "errors": [],
    }

    try:
        source_path = Path(args.file).expanduser().resolve()
        if not source_path.exists():
            raise FileNotFoundError(f"Upload file not found: {source_path}")
        if not source_path.is_file():
            raise ValueError(f"Upload path is not a file: {source_path}")

        inferred_store = infer_store_from_filename(source_path.name)
        store = normalize_store(args.store or inferred_store) if (args.store or inferred_store) else None

        destination_path = UPLOADS_DIR / source_path.name
        if source_path != destination_path.resolve():
            shutil.copy2(source_path, destination_path)

        result["success"] = True
        result["file_saved"] = str(destination_path)
        result["store"] = store

        if args.rebuild_index:
            if store is None:
                raise ValueError("Store is required for --rebuild-index when it cannot be inferred from filename.")
            result["sku_count"] = rebuild_indexes(store)
            result["index_rebuilt"] = True

        print_result(result, json_mode=args.json)
        return 0
    except Exception as exc:
        result["errors"].append(str(exc))
        print_result(result, json_mode=args.json)
        return 1


if __name__ == "__main__":
    sys.exit(main())
