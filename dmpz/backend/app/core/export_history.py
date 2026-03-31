"""
通用导出历史记录 SQLite 存储
"""
from __future__ import annotations

import json
import os
import sqlite3
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.config import HISTORY_DB_PATH, UPLOADS_DIR


class ExportHistoryStore:
    """导出历史记录存储层（全模块通用）"""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or (UPLOADS_DIR / "export_history.db")
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
                        CREATE TABLE IF NOT EXISTS export_history (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          module TEXT NOT NULL,
                          template_type TEXT,
                          input_data TEXT,
                          filename TEXT NOT NULL UNIQUE,
                          file_size INTEGER,
                          processed_count INTEGER DEFAULT 0,
                          status TEXT DEFAULT 'success',
                          created_by TEXT,
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                        """
                    )
                    conn.execute(
                        "CREATE INDEX IF NOT EXISTS idx_export_history_created_at "
                        "ON export_history(created_at DESC)"
                    )
                    conn.execute(
                        "CREATE INDEX IF NOT EXISTS idx_export_history_module "
                        "ON export_history(module)"
                    )
            finally:
                conn.close()

    def add_record(
        self,
        module: str,
        filename: str,
        template_type: Optional[str] = None,
        input_data: Optional[Dict[str, Any]] = None,
        file_size: Optional[int] = None,
        processed_count: int = 0,
        status: str = "success",
        created_by: Optional[str] = None,
    ) -> int:
        self.init_db()
        conn = self._connect()
        try:
            with conn:
                cursor = conn.execute(
                    """
                    INSERT INTO export_history (
                        module, template_type, input_data, filename, file_size, processed_count, status, created_by
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        module,
                        template_type,
                        json.dumps(input_data or {}, ensure_ascii=False),
                        filename,
                        file_size,
                        max(0, int(processed_count or 0)),
                        status,
                        created_by,
                    ),
                )
                return int(cursor.lastrowid)
        finally:
            conn.close()

    def list_records(
        self,
        page: int = 1,
        page_size: int = 20,
        module: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        self.init_db()
        page = max(1, int(page))
        page_size = max(1, min(100, int(page_size)))
        offset = (page - 1) * page_size

        where_parts: List[str] = []
        params: List[Any] = []
        if module:
            where_parts.append("module = ?")
            params.append(str(module).strip())
        if search:
            search_text = f"%{str(search).strip()}%"
            where_parts.append("(input_data LIKE ? OR filename LIKE ? OR template_type LIKE ?)")
            params.extend([search_text, search_text, search_text])

        where_clause = ""
        if where_parts:
            where_clause = "WHERE " + " AND ".join(where_parts)

        conn = self._connect()
        try:
            count_sql = f"SELECT COUNT(1) AS cnt FROM export_history {where_clause}"
            total = int(conn.execute(count_sql, params).fetchone()["cnt"])
            data_sql = (
                "SELECT id, module, template_type, input_data, filename, file_size, processed_count, status, created_at "
                f"FROM export_history {where_clause} "
                "ORDER BY created_at DESC, id DESC LIMIT ? OFFSET ?"
            )
            rows = conn.execute(data_sql, [*params, page_size, offset]).fetchall()
        finally:
            conn.close()

        records: List[Dict[str, Any]] = []
        for row in rows:
            input_data_raw = str(row["input_data"] or "{}")
            try:
                input_data_obj: Dict[str, Any] = json.loads(input_data_raw)
            except (json.JSONDecodeError, TypeError):
                input_data_obj = {}

            records.append(
                {
                    "id": int(row["id"]),
                    "module": str(row["module"] or ""),
                    "template_type": str(row["template_type"] or ""),
                    "input_data": input_data_obj,
                    "filename": str(row["filename"] or ""),
                    "file_size": int(row["file_size"] or 0),
                    "processed_count": int(row["processed_count"] or 0),
                    "status": str(row["status"] or "success"),
                    "created_at": str(row["created_at"] or ""),
                }
            )
        return records, total

    def get_record(self, record_id: int) -> Optional[Dict[str, Any]]:
        self.init_db()
        conn = self._connect()
        try:
            row = conn.execute(
                """
                SELECT id, module, template_type, input_data, filename, file_size, processed_count, status, created_at
                FROM export_history
                WHERE id = ?
                """,
                (record_id,),
            ).fetchone()
        finally:
            conn.close()

        if not row:
            return None
        input_data_raw = str(row["input_data"] or "{}")
        try:
            input_data_obj: Dict[str, Any] = json.loads(input_data_raw)
        except (json.JSONDecodeError, TypeError):
            input_data_obj = {}

        return {
            "id": int(row["id"]),
            "module": str(row["module"] or ""),
            "template_type": str(row["template_type"] or ""),
            "input_data": input_data_obj,
            "filename": str(row["filename"] or ""),
            "file_size": int(row["file_size"] or 0),
            "processed_count": int(row["processed_count"] or 0),
            "status": str(row["status"] or "success"),
            "created_at": str(row["created_at"] or ""),
        }

    def update_status(self, record_id: int, status: str) -> bool:
        self.init_db()
        conn = self._connect()
        try:
            with conn:
                cursor = conn.execute(
                    "UPDATE export_history SET status = ? WHERE id = ?",
                    (status, record_id),
                )
                return cursor.rowcount > 0
        finally:
            conn.close()

    def delete_record(self, record_id: int) -> Optional[Dict[str, Any]]:
        self.init_db()
        conn = self._connect()
        try:
            with conn:
                row = conn.execute(
                    """
                    SELECT id, module, template_type, input_data, filename, file_size, processed_count, status, created_at
                    FROM export_history
                    WHERE id = ?
                    """,
                    (record_id,),
                ).fetchone()
                if not row:
                    return None
                conn.execute("DELETE FROM export_history WHERE id = ?", (record_id,))
        finally:
            conn.close()

        input_data_raw = str(row["input_data"] or "{}")
        try:
            input_data_obj: Dict[str, Any] = json.loads(input_data_raw)
        except (json.JSONDecodeError, TypeError):
            input_data_obj = {}
        return {
            "id": int(row["id"]),
            "module": str(row["module"] or ""),
            "template_type": str(row["template_type"] or ""),
            "input_data": input_data_obj,
            "filename": str(row["filename"] or ""),
            "file_size": int(row["file_size"] or 0),
            "processed_count": int(row["processed_count"] or 0),
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
                    SELECT id, filename FROM export_history
                    WHERE created_at < ?
                    ORDER BY created_at ASC, id ASC
                    """,
                    (cutoff,),
                ).fetchall()
                if expired_rows:
                    conn.executemany(
                        "DELETE FROM export_history WHERE id = ?",
                        [(row["id"],) for row in expired_rows],
                    )
                    to_delete.extend(expired_rows)

                total = int(conn.execute("SELECT COUNT(1) AS cnt FROM export_history").fetchone()["cnt"])
                if total > max_records:
                    overflow = total - max_records
                    overflow_rows = conn.execute(
                        """
                        SELECT id, filename FROM export_history
                        ORDER BY created_at ASC, id ASC
                        LIMIT ?
                        """,
                        (overflow,),
                    ).fetchall()
                    if overflow_rows:
                        conn.executemany(
                            "DELETE FROM export_history WHERE id = ?",
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


export_history = ExportHistoryStore(HISTORY_DB_PATH)
