#!/usr/bin/env python3
"""跟卖查询 CLI 入口。"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys
from datetime import datetime
from pathlib import Path

from utils import (
    STORE_TO_TEMPLATE,
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
    parser.add_argument("--export-excel", action="store_true", help="导出跟卖结果为 Excel")
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


def resolve_follow_sell_source_files(store: str) -> list[str]:
    from app.config import STORE_CONFIGS, UPLOADS_DIR

    template_type = STORE_TO_TEMPLATE[store]
    store_config = STORE_CONFIGS.get(template_type, {})
    source_files = [name for name in store_config.get("source_files", []) if (UPLOADS_DIR / name).exists()]
    listing_report = str(store_config.get("listing_report", "")).strip()
    if listing_report and (UPLOADS_DIR / listing_report).exists():
        source_files.append(listing_report)
    return source_files


def build_follow_sell_filename(tag: str) -> str:
    from app.config import RESULTS_DIR

    normalized = "".join(ch for ch in str(tag or "").strip().upper() if ch.isalnum()) or "UNKNOWN"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"followsell_{normalized}_{timestamp}.xlsx"
    output_path = RESULTS_DIR / filename
    suffix = 1
    while output_path.exists():
        filename = f"followsell_{normalized}_{timestamp}_{suffix}.xlsx"
        output_path = RESULTS_DIR / filename
        suffix += 1
    return filename


def rename_follow_sell_export(original_filename: str, tag: str) -> str:
    from app.config import RESULTS_DIR, UPLOADS_DIR

    source_path = RESULTS_DIR / original_filename
    if not source_path.exists():
        source_path = UPLOADS_DIR / original_filename
    if not source_path.exists():
        raise FileNotFoundError(f"Export file not found: {original_filename}")

    target_filename = build_follow_sell_filename(tag)
    target_path = RESULTS_DIR / target_filename
    source_path.rename(target_path)
    return str(target_path)


def export_follow_sell_results(
    processor,
    store: str,
    successful_results: list[dict[str, object]],
    requested_skcs: list[str],
) -> tuple[str, int]:
    from app.config import RESULTS_DIR
    from app.core.excel_processor import ExcelProcessor

    if not successful_results:
        raise ValueError("No successful follow-sell results to export.")

    template_type = STORE_TO_TEMPLATE[store]
    generated_skus: list[str] = []
    selected_prefixes: list[str] = []
    seen = set()

    for item in successful_results:
        new_style = str(item.get("new_style", "")).strip().upper()
        if new_style and new_style not in selected_prefixes:
            selected_prefixes.append(new_style)
        for size_item in item.get("size_details", []):
            sku = str(size_item.get("sku", "")).strip().upper()
            if len(sku) >= 11 and sku not in seen:
                seen.add(sku)
                generated_skus.append(sku)

    if not generated_skus:
        raise ValueError("No valid generated SKUs found for export.")

    source_files = resolve_follow_sell_source_files(store)
    from app.config import STORE_CONFIGS
    _template_type = STORE_TO_TEMPLATE[store]
    _required = STORE_CONFIGS.get(_template_type, {}).get("source_files", [])
    _found_xlsm = [f for f in source_files if not f.endswith(".txt")]
    _missing = [f for f in _required if f not in _found_xlsm]
    if _missing:
        raise FileNotFoundError(f"Missing data files for follow-sell export: {', '.join(_missing)}")

    source_style_map = {
        str(item.get("new_style", "")).strip().upper(): str(item.get("old_style", "")).strip().upper()
        for item in successful_results
        if item.get("new_style") and item.get("old_style")
    }

    with contextlib.redirect_stdout(io.StringIO()):
        excel_processor = ExcelProcessor()
        output_filename, _processed_count = excel_processor.process_excel(
            template_type=template_type,
            filenames=source_files,
            selected_prefixes=selected_prefixes,
            generated_skus=generated_skus,
            target_color=None,
            target_size=None,
            source_style_map=source_style_map,
            clear_image_urls=True,
            follow_sell_mode=True,
        )

    export_tag = requested_skcs[0] if len(requested_skcs) == 1 else "batch"
    export_path = rename_follow_sell_export(output_filename, export_tag)
    if not Path(export_path).exists():
        raise FileNotFoundError(f"Export file not found after rename: {export_path}")
    return export_path, len(generated_skus)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    result = {
        "success": False,
        "results": [],
        "not_found": [],
        "errors": [],
        "export": None,
    }

    try:
        skcs = collect_skcs(args.skc, args.skc_file)
        if not skcs:
            raise ValueError("At least one SKC is required.")

        store = normalize_store(args.store)
        with contextlib.redirect_stdout(io.StringIO()):
            from app.core.follow_sell_processor import FollowSellProcessor
            processor = FollowSellProcessor()

        successful_items: list[dict[str, object]] = []
        for skc in skcs:
            with contextlib.redirect_stdout(io.StringIO()):
                query_result = processor.find_sizes_for_skc(skc=skc, template_type=STORE_TO_TEMPLATE[store])
            if query_result.get("success"):
                source_files = processor._find_source_files(  # noqa: SLF001
                    store_prefix=store,
                    old_style=str(query_result.get("old_style", "")).strip().upper(),
                    color_code=str(query_result.get("color_code", "")).strip().upper(),
                )
                normalized_item = {
                    "skc": str(query_result.get("skc", skc)).strip().upper(),
                    "new_style": str(query_result.get("new_style", "")).strip().upper(),
                    "old_style": str(query_result.get("old_style", "")).strip().upper(),
                    "color_code": str(query_result.get("color_code", "")).strip().upper(),
                    "sizes": [
                        str(size_item.get("size", "")).strip()
                        for size_item in query_result.get("sizes", [])
                        if str(size_item.get("size", "")).strip()
                    ],
                    "size_details": [
                        {
                            "size": str(size_item.get("size", "")).strip(),
                            "suffix": str(size_item.get("suffix", "")).strip().upper(),
                            "sku": str(size_item.get("sku", "")).strip().upper(),
                        }
                        for size_item in query_result.get("sizes", [])
                        if str(size_item.get("size", "")).strip()
                    ],
                    "source_files": source_files,
                    "total_sizes": len(query_result.get("sizes", [])),
                    "message": str(query_result.get("message", "")).strip(),
                }
                successful_items.append(normalized_item)
                result["results"].append(normalized_item)
            else:
                normalized_skc = str(query_result.get("skc", skc)).strip().upper()
                result["not_found"].append(normalized_skc)
                if query_result.get("message"):
                    result["errors"].append(f"{normalized_skc}: {query_result['message']}")

        if args.export_excel and successful_items:
            try:
                export_path, total_skus = export_follow_sell_results(
                    processor=processor,
                    store=store,
                    successful_results=successful_items,
                    requested_skcs=skcs,
                )
                result["export"] = {
                    "output_file": export_path,
                    "total_skus": total_skus,
                    "success_skcs": len(successful_items),
                    "failed_skcs": len(result["not_found"]),
                }
            except Exception as exc:
                result["errors"].append(f"Export failed: {exc}")

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
