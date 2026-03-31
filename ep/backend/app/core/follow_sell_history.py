"""
跟卖历史记录 SQLite 存储
"""
from __future__ import annotations

import os
import sqlite3
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from app.config import UPLOADS_DIR


class FollowSellHistoryStore:
    """跟卖历史记录存储层"""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or (UPLOADS_DIR / "follow_sell_history.db")
        self._init_lock = threading.Lock()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        return conn

    def init_db(self) -> None:
        with self._init_lock:
            conn = self._connect()
            try:
                with conn:
                    conn.execute(
                        """
                        CREATE TABLE IF NOT EXISTS follow_sell_history (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          skc TEXT NOT NULL,
                          new_style TEXT,
                          old_style TEXT,
                          color_code TEXT,
                          filename TEXT NOT NULL UNIQUE,
                          file_size INTEGER,
                          status TEXT DEFAULT 'success',
                          created_by TEXT,
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                        """
                    )
                    conn.execute(
                        "CREATE INDEX IF NOT EXISTS idx_follow_sell_history_created_at "
                        "ON follow_sell_history(created_at DESC)"
                    )
                    conn.execute(
                        "CREATE INDEX IF NOT EXISTS idx_follow_sell_history_skc "
                        "ON follow_sell_history(skc)"
                    )
            finally:
                conn.close()

    def add_record(
        self,
        skc: str,
        filename: str,
        new_style: str = "",
        old_style: str = "",
        color_code: str = "",
        file_size: Optional[int] = None,
        status: str = "success",
        created_by: Optional[str] = None,
    ) -> int:
        self.init_db()
        conn = self._connect()
        try:
            with conn:
                cursor = conn.execute(
                    """
                    INSERT INTO follow_sell_history (
                        skc, new_style, old_style, color_code, filename, file_size, status, created_by
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        skc,
                        new_style or "",
                        old_style or "",
                        color_code or "",
                        filename,
                        file_size,
                        status,
                        created_by,
                    ),
                )
                return int(cursor.lastrowid)
        finally:
            conn.close()

    def list_records(self, page: int = 1, page_size: int = 20, skc: Optional[str] = None) -> Tuple[List[Dict], int]:
        self.init_db()
        page = max(1, int(page))
        page_size = max(1, min(100, int(page_size)))
        offset = (page - 1) * page_size

        where_clause = ""
        params: List[object] = []
        if skc:
            where_clause = "WHERE skc LIKE ?"
            params.append(f"%{str(skc).strip().upper()}%")

        conn = self._connect()
        try:
            count_sql = f"SELECT COUNT(1) AS cnt FROM follow_sell_history {where_clause}"
            total = int(conn.execute(count_sql, params).fetchone()["cnt"])

            data_sql = (
                "SELECT id, skc, new_style, old_style, color_code, filename, file_size, status, created_at "
                f"FROM follow_sell_history {where_clause} "
                "ORDER BY created_at DESC, id DESC LIMIT ? OFFSET ?"
            )
            rows = conn.execute(data_sql, [*params, page_size, offset]).fetchall()
        finally:
            conn.close()

        records: List[Dict] = []
        for row in rows:
            records.append(
                {
                    "id": int(row["id"]),
                    "skc": str(row["skc"] or ""),
                    "new_style": str(row["new_style"] or ""),
                    "old_style": str(row["old_style"] or ""),
                    "color_code": str(row["color_code"] or ""),
                    "filename": str(row["filename"] or ""),
                    "file_size": int(row["file_size"] or 0),
                    "status": str(row["status"] or "success"),
                    "created_at": str(row["created_at"] or ""),
                }
            )
        return records, total

    def get_record(self, record_id: int) -> Optional[Dict]:
        self.init_db()
        conn = self._connect()
        try:
            row = conn.execute(
                """
                SELECT id, skc, new_style, old_style, color_code, filename, file_size, status, created_at
                FROM follow_sell_history
                WHERE id = ?
                """,
                (record_id,),
            ).fetchone()
        finally:
            conn.close()

        if not row:
            return None
        return {
            "id": int(row["id"]),
            "skc": str(row["skc"] or ""),
            "new_style": str(row["new_style"] or ""),
            "old_style": str(row["old_style"] or ""),
            "color_code": str(row["color_code"] or ""),
            "filename": str(row["filename"] or ""),
            "file_size": int(row["file_size"] or 0),
            "status": str(row["status"] or "success"),
            "created_at": str(row["created_at"] or ""),
        }

    def update_status(self, record_id: int, status: str) -> bool:
        self.init_db()
        conn = self._connect()
        try:
            with conn:
                cursor = conn.execute(
                    "UPDATE follow_sell_history SET status = ? WHERE id = ?",
                    (status, record_id),
                )
                return cursor.rowcount > 0
        finally:
            conn.close()

    def delete_record(self, record_id: int) -> Optional[Dict]:
        self.init_db()
        conn = self._connect()
        try:
            with conn:
                row = conn.execute(
                    """
                    SELECT id, skc, new_style, old_style, color_code, filename, file_size, status, created_at
                    FROM follow_sell_history
                    WHERE id = ?
                    """,
                    (record_id,),
                ).fetchone()
                if not row:
                    return None
                conn.execute("DELETE FROM follow_sell_history WHERE id = ?", (record_id,))
        finally:
            conn.close()

        return {
            "id": int(row["id"]),
            "skc": str(row["skc"] or ""),
            "new_style": str(row["new_style"] or ""),
            "old_style": str(row["old_style"] or ""),
            "color_code": str(row["color_code"] or ""),
            "filename": str(row["filename"] or ""),
            "file_size": int(row["file_size"] or 0),
            "status": str(row["status"] or "success"),
            "created_at": str(row["created_at"] or ""),
        }

    def cleanup(self, retention_days: int = 90, max_records: int = 1000) -> Dict[str, int]:
        """自动清理：删除超期记录和超过上限的旧记录，并同步删除文件。"""
        self.init_db()
        to_delete: List[sqlite3.Row] = []
        cutoff = (datetime.utcnow() - timedelta(days=retention_days)).strftime("%Y-%m-%d %H:%M:%S")

        conn = self._connect()
        try:
            with conn:
                expired_rows = conn.execute(
                    """
                    SELECT id, filename FROM follow_sell_history
                    WHERE created_at < ?
                    ORDER BY created_at ASC, id ASC
                    """,
                    (cutoff,),
                ).fetchall()
                if expired_rows:
                    conn.executemany(
                        "DELETE FROM follow_sell_history WHERE id = ?",
                        [(row["id"],) for row in expired_rows],
                    )
                    to_delete.extend(expired_rows)

                total = int(conn.execute("SELECT COUNT(1) AS cnt FROM follow_sell_history").fetchone()["cnt"])
                if total > max_records:
                    overflow = total - max_records
                    overflow_rows = conn.execute(
                        """
                        SELECT id, filename FROM follow_sell_history
                        ORDER BY created_at ASC, id ASC
                        LIMIT ?
                        """,
                        (overflow,),
                    ).fetchall()
                    if overflow_rows:
                        conn.executemany(
                            "DELETE FROM follow_sell_history WHERE id = ?",
                            [(row["id"],) for row in overflow_rows],
                        )
                        to_delete.extend(overflow_rows)
        finally:
            conn.close()

        deleted_files = 0
        for row in to_delete:
            filename = str(row["filename"] or "")
            if not filename:
                continue
            file_path = UPLOADS_DIR / filename
            if file_path.exists():
                try:
                    os.remove(file_path)
                    deleted_files += 1
                except OSError:
                    continue

        return {"deleted_records": len(to_delete), "deleted_files": deleted_files}


follow_sell_history = FollowSellHistoryStore()
