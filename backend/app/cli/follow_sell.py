#!/usr/bin/env python3
"""跟卖查询 CLI 入口。"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys
from pathlib import Path

from utils import (
    bootstrap_app,
    count_non_empty_lines,
    normalize_store,
    print_result,
)

bootstrap_app()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="跟卖查询")
    parser.add_argument("--skc", action="append", default=[], help="单个 SKC，可重复传入")
    parser.add_argument("--skc-file", help="包含 SKC 列表的文本文件")
    parser.add_argument("--store", required=True, choices=["EP", "DM", "PZ"], help="店铺代码")
    parser.add_argument("--output", help="输出 JSON 文件路径")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    return parser


def collect_skcs(raw_skcs: list[str], skc_file: str | None) -> list[str]:
    values: list[str] = []
    for item in raw_skcs:
        if item is None:
            continue
        parts = [part.strip().upper() for part in str(item).split(",") if part.strip()]
        values.extend(parts)

    if skc_file:
        file_path = Path(skc_file)
        if not file_path.exists():
            raise FileNotFoundError(f"SKC file not found: {file_path}")
        values.extend(value.strip().upper() for value in count_non_empty_lines(file_path))

    deduped: list[str] = []
    seen = set()
    for value in values:
        if value not in seen:
            seen.add(value)
            deduped.append(value)
    return deduped


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    result = {
        "success": False,
        "results": [],
        "not_found": [],
        "errors": [],
    }

    try:
        skcs = collect_skcs(args.skc, args.skc_file)
        if not skcs:
            raise ValueError("At least one SKC is required.")

        store = normalize_store(args.store)
        with contextlib.redirect_stdout(io.StringIO()):
            from app.core.follow_sell_processor import FollowSellProcessor
            processor = FollowSellProcessor()

        for skc in skcs:
            with contextlib.redirect_stdout(io.StringIO()):
                item = processor.process_skc(skc=skc, store_prefix=store)
            if item.get("success"):
                result["results"].append(
                    {
                        "skc": item["skc"],
                        "old_style": item["old_style"],
                        "sizes": item["sizes"],
                        "source_files": item["source_files"],
                    }
                )
            else:
                result["not_found"].append(item["skc"])
                if item.get("message"):
                    result["errors"].append(f"{item['skc']}: {item['message']}")

        result["success"] = not result["errors"]

        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

        print_result(result, json_mode=args.json or not args.output)
        return 0 if result["success"] else 1
    except Exception as exc:
        result["errors"].append(str(exc))
        print_result(result, json_mode=args.json or not args.output)
        return 1


if __name__ == "__main__":
    sys.exit(main())
