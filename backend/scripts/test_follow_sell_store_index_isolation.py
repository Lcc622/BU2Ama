#!/usr/bin/env python3
"""
测试跟卖功能分店铺索引隔离。

目标：
1) 调用 follow_sell_processor.find_sizes_for_skc(skc='ES01819NT', template_type=...)
2) 校验是否访问了对应 ep_index_{store}.db
3) 输出店铺对比表
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path
from typing import Dict, List


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.follow_sell_processor import follow_sell_processor  # noqa: E402


SKC = "ES01819NT"
STORES = [
    {"name": "EP", "template_type": "EPUS"},
    {"name": "DM", "template_type": "DaMaUS"},
    {"name": "PZ", "template_type": "PZUS"},
]


def _source_file_prefix_ok(store_prefix: str, source_files: List[str]) -> bool:
    if not source_files:
        return True
    upper_files = [name.upper() for name in source_files]
    if store_prefix == "EP":
        return all(name.startswith("EP-") for name in upper_files)
    if store_prefix == "DM":
        return all(name.startswith("DA-") or name.startswith("DM-") for name in upper_files)
    if store_prefix == "PZ":
        return all(name.startswith("PZ-") for name in upper_files)
    return False


def _query_source_files(index_db: Path, store_prefix: str, old_style: str, color_code: str) -> List[str]:
    if not index_db.exists() or not old_style or not color_code:
        return []
    conn = sqlite3.connect(index_db)
    try:
        rows = conn.execute(
            """
            SELECT DISTINCT source_file
            FROM ep_sku_index
            WHERE store_prefix = ?
              AND style = ?
              AND substr(sku, 8, 2) = ?
            ORDER BY source_file
            """,
            (store_prefix, old_style, color_code),
        ).fetchall()
    finally:
        conn.close()
    return [str(row[0]) for row in rows]


def run_store_case(template_type: str, store_name: str) -> Dict:
    store_prefix = follow_sell_processor.get_store_prefix(template_type)
    expected_db = follow_sell_processor.get_index_db_path(store_prefix).resolve()
    accessed_paths: List[Path] = []

    original_connect_db = follow_sell_processor._connect_db

    def tracked_connect_db(prefix: str):
        path = follow_sell_processor.get_index_db_path(prefix).resolve()
        accessed_paths.append(path)
        return original_connect_db(prefix)

    follow_sell_processor._connect_db = tracked_connect_db  # type: ignore[method-assign]
    try:
        result = follow_sell_processor.find_sizes_for_skc(skc=SKC, template_type=template_type)
    finally:
        follow_sell_processor._connect_db = original_connect_db  # type: ignore[method-assign]

    unique_accessed_paths = sorted({path for path in accessed_paths})
    accessed_expected_only = bool(unique_accessed_paths) and all(path == expected_db for path in unique_accessed_paths)

    parsed = follow_sell_processor.parse_skc(SKC)
    color_code = parsed[1] if parsed else ""
    old_style = str(result.get("old_style") or "")
    source_files = _query_source_files(expected_db, store_prefix, old_style, color_code)

    issues: List[str] = []
    if not accessed_expected_only:
        issues.append(
            f"{store_name}: 索引库访问异常，期望 {expected_db.name}，实际 {[p.name for p in unique_accessed_paths] or ['<none>']}"
        )
    if not _source_file_prefix_ok(store_prefix, source_files):
        issues.append(f"{store_name}: 来源文件前缀与店铺不匹配 -> {source_files}")

    return {
        "store": store_name,
        "template_type": template_type,
        "store_prefix": store_prefix,
        "success": bool(result.get("success")),
        "message": str(result.get("message") or ""),
        "size_count": len(result.get("sizes") or []),
        "sizes": [item.get("size", "") for item in (result.get("sizes") or [])],
        "index_db": expected_db.name,
        "accessed_dbs": [path.name for path in unique_accessed_paths],
        "source_files": source_files,
        "issues": issues,
    }


def main() -> int:
    print(f"开始测试 SKC: {SKC}")

    results = [run_store_case(item["template_type"], item["name"]) for item in STORES]

    print("\n店铺详细结果：")
    for row in results:
        size_list_text = ",".join(row["sizes"]) if row["sizes"] else "(空)"
        source_text = ",".join(row["source_files"]) if row["source_files"] else "(无)"
        print(
            f"- {row['store']} ({row['template_type']}) | success={row['success']} | "
            f"sizes={size_list_text} | index={row['index_db']} | source={source_text} | msg={row['message']}"
        )

    print("\n| 店铺 | 成功 | 尺码数量 | 索引库 | 来源文件 |")
    print("|------|------|---------|--------|---------|")
    for row in results:
        source_text = ",".join(row["source_files"]) if row["source_files"] else "(无)"
        print(
            f"| {row['store']} | {str(row['success'])} | {row['size_count']} | "
            f"{row['index_db']} | {source_text} |"
        )

    all_issues: List[str] = []
    for row in results:
        all_issues.extend(row["issues"])

    print("\n索引库访问校验：")
    for row in results:
        print(
            f"- {row['store']}: 期望 {row['index_db']}，实际访问 {row['accessed_dbs'] or ['<none>']}"
        )

    if all_issues:
        print("\n发现问题：")
        for issue in all_issues:
            print(f"- {issue}")
        return 1

    print("\n未发现跨店铺串值或索引库访问错误。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
