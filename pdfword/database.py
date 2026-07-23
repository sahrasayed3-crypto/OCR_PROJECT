import os
import sqlite3
from contextlib import closing, contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from clouda_contracts.storage import StorageRoots

DEFAULT_DB_PATH = StorageRoots.from_env().database_path
SCHEMA_VERSION = 3
FINAL_STATUSES = {"completed", "failed", "manual_review", "cancelled"}
ALLOWED_STATUS_TRANSITIONS = {
    "pending": {"processing", "failed", "cancelled"},
    "processing": {"pending", "completed", "failed", "manual_review", "cancelled"},
    "failed": {"pending"},
    "cancelled": {"pending"},
    "manual_review": set(),
    "completed": set(),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Database:
    def __init__(self, path: str | Path | None = None) -> None:
        configured_path = (
            path
            if path is not None
            else os.getenv("CLOUDA_DATABASE_PATH") or os.getenv("DATABASE_PATH")
        )
        self.path = Path(configured_path or DEFAULT_DB_PATH)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=30)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute("PRAGMA busy_timeout = 30000")
        return connection

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        connection = self.connect()
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.transaction() as connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS schema_meta (
                    version INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                    created_at TEXT NOT NULL,
                    last_login TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS conversions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT NOT NULL UNIQUE,
                    username TEXT NOT NULL,
                    original_pdf_name TEXT NOT NULL,
                    stored_pdf_path TEXT NOT NULL,
                    output_docx_name TEXT,
                    stored_docx_path TEXT,
                    page_from INTEGER,
                    page_to INTEGER,
                    file_type TEXT,
                    text_quality_score REAL,
                    layout_quality_score REAL,
                    final_quality_score REAL,
                    winning_engine TEXT,
                    winning_model TEXT,
                    total_cost REAL NOT NULL DEFAULT 0,
                    processing_time REAL NOT NULL DEFAULT 0,
                    status TEXT NOT NULL,
                    hidden INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    error_message TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_conversions_user_created
                    ON conversions(username, created_at DESC);
                CREATE TABLE IF NOT EXISTS attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversion_id INTEGER NOT NULL REFERENCES conversions(id) ON DELETE CASCADE,
                    engine_name TEXT,
                    model_name TEXT,
                    engine_type TEXT NOT NULL,
                    attempt_number INTEGER NOT NULL,
                    quality_score REAL,
                    cost REAL NOT NULL DEFAULT 0,
                    cost_is_estimated INTEGER NOT NULL DEFAULT 0,
                    prompt_tokens INTEGER NOT NULL DEFAULT 0,
                    completion_tokens INTEGER NOT NULL DEFAULT 0,
                    processing_time REAL NOT NULL DEFAULT 0,
                    success INTEGER NOT NULL DEFAULT 1,
                    failure_reason TEXT,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS project_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    type TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS correction_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern TEXT NOT NULL,
                    replacement TEXT NOT NULL,
                    rule_type TEXT NOT NULL,
                    occurrences INTEGER NOT NULL DEFAULT 1,
                    approved INTEGER NOT NULL DEFAULT 0,
                    enabled INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    UNIQUE(pattern, replacement, rule_type)
                );
                CREATE TABLE IF NOT EXISTS correction_revisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    stored_path TEXT NOT NULL,
                    file_hash TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    uploaded_at TEXT NOT NULL,
                    uploaded_by TEXT NOT NULL,
                    comparison_status TEXT NOT NULL DEFAULT 'pending',
                    learning_status TEXT NOT NULL DEFAULT 'review_only',
                    change_count INTEGER NOT NULL DEFAULT 0,
                    UNIQUE(job_id, version),
                    UNIQUE(job_id, file_hash)
                );
                CREATE TABLE IF NOT EXISTS correction_examples (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    revision_id INTEGER NOT NULL REFERENCES correction_revisions(id) ON DELETE CASCADE,
                    job_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    wrong_text TEXT NOT NULL,
                    correct_text TEXT NOT NULL,
                    context_before TEXT NOT NULL DEFAULT '',
                    context_after TEXT NOT NULL DEFAULT '',
                    paragraph_index INTEGER,
                    sentence_index INTEGER,
                    change_type TEXT NOT NULL,
                    language TEXT NOT NULL,
                    is_sensitive INTEGER NOT NULL DEFAULT 0,
                    status TEXT NOT NULL DEFAULT 'proposed'
                        CHECK(status IN ('proposed','approved','rejected','ignored')),
                    approved_by TEXT,
                    approved_at TEXT,
                    rejected_at TEXT,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS correction_memory_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    wrong_text TEXT NOT NULL,
                    correct_text TEXT NOT NULL,
                    context_pattern TEXT NOT NULL DEFAULT '',
                    scope TEXT NOT NULL DEFAULT 'global',
                    scope_value TEXT NOT NULL DEFAULT '',
                    language TEXT NOT NULL DEFAULT 'unknown',
                    document_type TEXT NOT NULL DEFAULT '',
                    source_count INTEGER NOT NULL DEFAULT 0,
                    occurrence_count INTEGER NOT NULL DEFAULT 0,
                    accepted_count INTEGER NOT NULL DEFAULT 0,
                    rejected_count INTEGER NOT NULL DEFAULT 0,
                    confidence REAL NOT NULL DEFAULT 0,
                    is_sensitive INTEGER NOT NULL DEFAULT 0,
                    approved INTEGER NOT NULL DEFAULT 0,
                    enabled INTEGER NOT NULL DEFAULT 0,
                    approved_by TEXT,
                    approved_at TEXT,
                    last_applied_at TEXT,
                    success_count INTEGER NOT NULL DEFAULT 0,
                    failure_count INTEGER NOT NULL DEFAULT 0,
                    updated_at TEXT NOT NULL,
                    UNIQUE(wrong_text, correct_text, context_pattern, scope, scope_value)
                );
                CREATE TABLE IF NOT EXISTS correction_applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT NOT NULL,
                    rule_id INTEGER NOT NULL,
                    before_text TEXT NOT NULL,
                    after_text TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    context_match INTEGER NOT NULL,
                    applied_at TEXT NOT NULL,
                    outcome TEXT NOT NULL DEFAULT 'unknown'
                );
                CREATE TABLE IF NOT EXISTS correction_evaluations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    revision_id INTEGER NOT NULL,
                    job_id TEXT NOT NULL,
                    dataset_split TEXT NOT NULL CHECK(dataset_split IN ('training','evaluation')),
                    pre_word_accuracy REAL,
                    pre_char_accuracy REAL,
                    post_word_accuracy REAL,
                    post_char_accuracy REAL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS backup_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    backup_path TEXT NOT NULL,
                    status TEXT NOT NULL,
                    size_bytes INTEGER NOT NULL DEFAULT 0,
                    error_message TEXT,
                    created_at TEXT NOT NULL
                );
                """)
            columns = {
                row["name"]
                for row in connection.execute(
                    "PRAGMA table_info(conversions)"
                ).fetchall()
            }
            if "corrected_docx_path" not in columns:
                connection.execute(
                    "ALTER TABLE conversions ADD COLUMN corrected_docx_path TEXT"
                )
            if "page_numbers" not in columns:
                connection.execute(
                    "ALTER TABLE conversions ADD COLUMN page_numbers TEXT"
                )
            if "actual_char_accuracy" not in columns:
                connection.execute(
                    "ALTER TABLE conversions ADD COLUMN actual_char_accuracy REAL"
                )
            if "actual_word_accuracy" not in columns:
                connection.execute(
                    "ALTER TABLE conversions ADD COLUMN actual_word_accuracy REAL"
                )
            additions = {
                "attempt_count": "INTEGER NOT NULL DEFAULT 0",
                "started_at": "TEXT",
                "completed_at": "TEXT",
                "worker_name": "TEXT",
                "last_heartbeat": "TEXT",
                "rq_job_id": "TEXT",
            }
            for name, definition in additions.items():
                if name not in columns:
                    connection.execute(
                        f"ALTER TABLE conversions ADD COLUMN {name} {definition}"
                    )
            connection.execute(
                "UPDATE conversions SET status = 'pending' WHERE status = 'queued'"
            )
            row = connection.execute(
                "SELECT version FROM schema_meta LIMIT 1"
            ).fetchone()
            if row is None:
                connection.execute(
                    "INSERT INTO schema_meta(version) VALUES (?)", (SCHEMA_VERSION,)
                )
            else:
                connection.execute(
                    "UPDATE schema_meta SET version = ?", (SCHEMA_VERSION,)
                )

    def login(self, username: str) -> None:
        clean = username.strip()
        if not clean:
            raise ValueError("اسم المستخدم مطلوب")
        now = utc_now()
        with self.transaction() as connection:
            connection.execute(
                """
                INSERT INTO users(username, created_at, last_login)
                VALUES (?, ?, ?)
                ON CONFLICT(username) DO UPDATE SET last_login = excluded.last_login
                """,
                (clean, now, now),
            )

    def mark_incomplete_as_interrupted(self) -> int:
        """Legacy compatibility; distributed pending jobs must survive UI restarts."""
        with self.transaction() as connection:
            cursor = connection.execute(
                """
                UPDATE conversions
                SET status = 'pending', updated_at = ?,
                    error_message = COALESCE(error_message, 'ستعاد المهمة إلى عامل المعالجة')
                WHERE status = 'interrupted'
                """,
                (utc_now(),),
            )
            return cursor.rowcount

    def create_conversion(self, values: dict) -> int:
        fields = ", ".join(values)
        placeholders = ", ".join("?" for _ in values)
        with self.transaction() as connection:
            cursor = connection.execute(
                f"INSERT INTO conversions ({fields}) VALUES ({placeholders})",
                tuple(values.values()),
            )
            if cursor.lastrowid is None:
                raise RuntimeError("Conversion insert did not return an id")
            return int(cursor.lastrowid)

    def list_conversions(
        self, username: str | None, include_hidden: bool = False
    ) -> list[dict]:
        hidden_clause = "" if include_hidden else "AND hidden = 0"
        where_clause = "WHERE username = ?" if username is not None else "WHERE 1 = 1"
        params = (username,) if username is not None else ()
        with closing(self.connect()) as connection:
            rows = connection.execute(
                f"""
                SELECT * FROM conversions
                {where_clause} {hidden_clause}
                ORDER BY created_at DESC
                """,
                params,
            ).fetchall()
        return [dict(row) for row in rows]

    def get_conversion(self, job_id: str, username: str | None = None) -> dict | None:
        sql = "SELECT * FROM conversions WHERE job_id = ?"
        params: tuple = (job_id,)
        if username is not None:
            sql += " AND username = ?"
            params = (job_id, username)
        with closing(self.connect()) as connection:
            row = connection.execute(sql, params).fetchone()
        return dict(row) if row else None

    def list_pending_conversions(self) -> list[dict]:
        with closing(self.connect()) as connection:
            rows = connection.execute(
                "SELECT * FROM conversions WHERE status = 'pending' ORDER BY created_at"
            ).fetchall()
        return [dict(row) for row in rows]

    def update_conversion(self, conversion_id: int, values: dict) -> None:
        allowed = {
            "stored_docx_path",
            "file_type",
            "text_quality_score",
            "layout_quality_score",
            "final_quality_score",
            "winning_engine",
            "winning_model",
            "total_cost",
            "processing_time",
            "status",
            "hidden",
            "updated_at",
            "error_message",
            "corrected_docx_path",
            "actual_char_accuracy",
            "actual_word_accuracy",
            "attempt_count",
            "started_at",
            "completed_at",
            "worker_name",
            "last_heartbeat",
            "rq_job_id",
        }
        updates = {key: value for key, value in values.items() if key in allowed}
        if not updates:
            return
        assignments = ", ".join(f"{key} = ?" for key in updates)
        with self.transaction() as connection:
            connection.execute(
                f"UPDATE conversions SET {assignments} WHERE id = ?",
                (*updates.values(), conversion_id),
            )

    def transition_conversion(
        self,
        job_id: str,
        target_status: str,
        *,
        worker_name: str | None = None,
        error_message: str | None = None,
        extra: dict | None = None,
    ) -> dict:
        if target_status not in ALLOWED_STATUS_TRANSITIONS:
            raise ValueError(f"Unsupported status: {target_status}")
        now = utc_now()
        with self.transaction() as connection:
            row = connection.execute(
                "SELECT * FROM conversions WHERE job_id = ?", (job_id,)
            ).fetchone()
            if row is None:
                raise KeyError(job_id)
            current = row["status"]
            if (
                current != target_status
                and target_status not in ALLOWED_STATUS_TRANSITIONS.get(current, set())
            ):
                raise ValueError(
                    f"Invalid status transition: {current} -> {target_status}"
                )
            values: dict[str, Any] = {
                "status": target_status,
                "updated_at": now,
                "error_message": error_message,
            }
            if worker_name is not None:
                values["worker_name"] = worker_name
            if target_status == "processing":
                values["started_at"] = now
                values["last_heartbeat"] = now
                values["attempt_count"] = int(row["attempt_count"] or 0) + 1
            if target_status in FINAL_STATUSES:
                values["completed_at"] = now
            for key, value in (extra or {}).items():
                if key in {
                    "stored_docx_path",
                    "file_type",
                    "text_quality_score",
                    "layout_quality_score",
                    "final_quality_score",
                    "winning_engine",
                    "winning_model",
                    "total_cost",
                    "processing_time",
                    "rq_job_id",
                    "last_heartbeat",
                }:
                    values[key] = value
            assignments = ", ".join(f"{key} = ?" for key in values)
            connection.execute(
                f"UPDATE conversions SET {assignments} WHERE id = ?",
                (*values.values(), row["id"]),
            )
        result = self.get_conversion(job_id)
        assert result is not None
        return result

    def heartbeat(self, job_id: str, worker_name: str) -> None:
        with self.transaction() as connection:
            cursor = connection.execute(
                """
                UPDATE conversions
                SET last_heartbeat = ?, updated_at = ?, worker_name = ?
                WHERE job_id = ? AND status = 'processing'
                """,
                (utc_now(), utc_now(), worker_name, job_id),
            )
            if cursor.rowcount != 1:
                raise ValueError("Job is not processing")

    def record_attempt(self, values: dict) -> int:
        fields = ", ".join(values)
        placeholders = ", ".join("?" for _ in values)
        with self.transaction() as connection:
            cursor = connection.execute(
                f"INSERT INTO attempts ({fields}) VALUES ({placeholders})",
                tuple(values.values()),
            )
            connection.execute(
                """
                UPDATE conversions
                SET total_cost = (
                    SELECT COALESCE(SUM(cost), 0) FROM attempts WHERE conversion_id = ?
                ), updated_at = ?
                WHERE id = ?
                """,
                (values["conversion_id"], utc_now(), values["conversion_id"]),
            )
            if cursor.lastrowid is None:
                raise RuntimeError("Attempt insert did not return an id")
            return int(cursor.lastrowid)

    def list_attempts(self, conversion_id: int) -> list[dict]:
        with closing(self.connect()) as connection:
            rows = connection.execute(
                "SELECT * FROM attempts WHERE conversion_id = ? ORDER BY attempt_number, id",
                (conversion_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_setting_rows(self) -> dict[str, dict]:
        with closing(self.connect()) as connection:
            rows = connection.execute("SELECT * FROM project_settings").fetchall()
        return {row["key"]: dict(row) for row in rows}

    def set_setting(self, key: str, value: str, value_type: str) -> None:
        with self.transaction() as connection:
            connection.execute(
                """
                INSERT INTO project_settings(key, value, type, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    type = excluded.type,
                    updated_at = excluded.updated_at
                """,
                (key, value, value_type, utc_now()),
            )

    def clear_settings(self) -> None:
        with self.transaction() as connection:
            connection.execute("DELETE FROM project_settings")

    def daily_cost(self) -> float:
        today = datetime.now(timezone.utc).date().isoformat()
        with closing(self.connect()) as connection:
            row = connection.execute(
                "SELECT COALESCE(SUM(cost), 0) AS value FROM attempts WHERE created_at >= ?",
                (today,),
            ).fetchone()
        return float(row["value"] or 0)

    def statistics(
        self,
        username: str | None = None,
        file_type: str | None = None,
        engine: str | None = None,
    ) -> dict:
        clauses: list[str] = []
        params_list: list = []
        if username:
            clauses.append("username = ?")
            params_list.append(username)
        if file_type:
            clauses.append("file_type = ?")
            params_list.append(file_type)
        if engine:
            clauses.append("winning_engine = ?")
            params_list.append(engine)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        params = tuple(params_list)
        with closing(self.connect()) as connection:
            summary = connection.execute(
                f"""
                SELECT
                    COUNT(*) AS total,
                    SUM(CASE WHEN created_at >= date('now') THEN 1 ELSE 0 END) AS today,
                    SUM(CASE WHEN created_at >= date('now', '-6 days') THEN 1 ELSE 0 END) AS week,
                    SUM(CASE WHEN created_at >= date('now', 'start of month') THEN 1 ELSE 0 END) AS month,
                    AVG(text_quality_score) AS avg_text,
                    AVG(layout_quality_score) AS avg_layout,
                    AVG(final_quality_score) AS avg_final,
                    AVG(processing_time) AS avg_time,
                    SUM(total_cost) AS total_cost,
                    SUM(CASE WHEN created_at >= date('now') THEN total_cost ELSE 0 END) AS cost_today,
                    SUM(CASE WHEN created_at >= date('now', '-6 days') THEN total_cost ELSE 0 END) AS cost_week,
                    SUM(CASE WHEN created_at >= date('now', 'start of month') THEN total_cost ELSE 0 END) AS cost_month,
                    SUM(CASE WHEN status = 'completed' AND text_quality_score >= 90 THEN 1 ELSE 0 END) AS completed,
                    SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failed,
                    SUM(CASE WHEN text_quality_score < 90 THEN 1 ELSE 0 END) AS below_text_threshold,
                    SUM(CASE WHEN file_type = 'digital' THEN 1 ELSE 0 END) AS digital,
                    SUM(CASE WHEN file_type = 'scan' THEN 1 ELSE 0 END) AS scan
                FROM conversions {where}
                """,
                params,
            ).fetchone()
            winner_where = (
                f"{where} {'AND' if where else 'WHERE'} winning_engine IS NOT NULL"
            )
            winner = connection.execute(
                f"""
                SELECT winning_engine, COUNT(*) AS uses
                FROM conversions {winner_where}
                GROUP BY winning_engine ORDER BY uses DESC LIMIT 1
                """,
                params,
            ).fetchone()
            failure = connection.execute("""
                SELECT failure_reason, COUNT(*) AS uses
                FROM attempts
                WHERE success = 0 AND failure_reason IS NOT NULL
                GROUP BY failure_reason ORDER BY uses DESC LIMIT 1
                """).fetchone()
            failed_attempts = connection.execute(
                "SELECT COUNT(*) AS value FROM attempts WHERE success = 0"
            ).fetchone()
        result = dict(summary)
        total = int(result.get("total") or 0)
        result["success_rate"] = (
            (int(result.get("completed") or 0) / total * 100.0) if total else 0.0
        )
        result["top_engine"] = winner["winning_engine"] if winner else None
        result["failed_attempts"] = int(failed_attempts["value"] or 0)
        result["top_failure"] = failure["failure_reason"] if failure else None
        return result

    def export_conversions_csv(self, username: str | None = None) -> str:
        import csv
        import io

        rows = self.list_conversions(username, include_hidden=True) if username else []
        if username is None:
            with closing(self.connect()) as connection:
                rows = [
                    dict(row)
                    for row in connection.execute(
                        "SELECT * FROM conversions ORDER BY created_at DESC"
                    )
                ]
        if not rows:
            return ""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
        return output.getvalue()

    def add_correction_rule(
        self, pattern: str, replacement: str, rule_type: str
    ) -> None:
        with self.transaction() as connection:
            connection.execute(
                """
                INSERT INTO correction_rules(pattern, replacement, rule_type, created_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(pattern, replacement, rule_type)
                DO UPDATE SET occurrences = occurrences + 1
                """,
                (pattern, replacement, rule_type, utc_now()),
            )

    def list_correction_rules(self) -> list[dict]:
        with closing(self.connect()) as connection:
            rows = connection.execute(
                "SELECT * FROM correction_rules ORDER BY occurrences DESC, id DESC"
            ).fetchall()
        return [dict(row) for row in rows]

    def enabled_correction_rules(self) -> list[dict]:
        with closing(self.connect()) as connection:
            rows = connection.execute("""
                SELECT * FROM correction_rules
                WHERE approved = 1 AND enabled = 1
                ORDER BY occurrences DESC, id
                """).fetchall()
        return [dict(row) for row in rows]

    def set_correction_rule_state(
        self, rule_id: int, approved: bool, enabled: bool
    ) -> None:
        with self.transaction() as connection:
            connection.execute(
                "UPDATE correction_rules SET approved = ?, enabled = ? WHERE id = ?",
                (int(approved), int(enabled and approved), rule_id),
            )

    def delete_correction_rule(self, rule_id: int) -> None:
        with self.transaction() as connection:
            connection.execute("DELETE FROM correction_rules WHERE id = ?", (rule_id,))

    def create_correction_revision(
        self,
        job_id: str,
        username: str,
        stored_path: str,
        file_hash: str,
        file_size: int,
        learning_status: str = "review_only",
    ) -> dict:
        row = self.get_conversion(job_id, username)
        if row is None:
            raise PermissionError("Conversion does not belong to this user")
        with self.transaction() as connection:
            version = int(
                connection.execute(
                    "SELECT COALESCE(MAX(version), 0) + 1 FROM correction_revisions WHERE job_id = ?",
                    (job_id,),
                ).fetchone()[0]
            )
            cursor = connection.execute(
                """
                INSERT INTO correction_revisions(
                    job_id,user_id,version,stored_path,file_hash,file_size,uploaded_at,
                    uploaded_by,comparison_status,learning_status
                ) VALUES(?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    job_id,
                    username,
                    version,
                    stored_path,
                    file_hash,
                    file_size,
                    utc_now(),
                    username,
                    "pending",
                    learning_status,
                ),
            )
            revision_id = cursor.lastrowid
            if revision_id is None:
                raise RuntimeError("Correction revision insert did not return an id")
        revision = self.get_correction_revision(int(revision_id), username)
        if revision is None:
            raise RuntimeError("Correction revision was not persisted")
        return revision

    def get_correction_revision(
        self, revision_id: int, username: str | None = None
    ) -> dict | None:
        sql = "SELECT * FROM correction_revisions WHERE id = ?"
        params: tuple = (revision_id,)
        if username is not None:
            sql += " AND user_id = ?"
            params += (username,)
        with closing(self.connect()) as connection:
            row = connection.execute(sql, params).fetchone()
        return dict(row) if row else None

    def list_correction_revisions(self, job_id: str, username: str) -> list[dict]:
        with closing(self.connect()) as connection:
            rows = connection.execute(
                """
                SELECT * FROM correction_revisions
                WHERE job_id = ? AND user_id = ? ORDER BY version DESC
                """,
                (job_id, username),
            ).fetchall()
        return [dict(row) for row in rows]

    def update_correction_revision(self, revision_id: int, **values) -> None:
        allowed = {
            "stored_path",
            "comparison_status",
            "learning_status",
            "change_count",
        }
        clean = {key: value for key, value in values.items() if key in allowed}
        if not clean:
            return
        assignments = ", ".join(f"{key} = ?" for key in clean)
        with self.transaction() as connection:
            connection.execute(
                f"UPDATE correction_revisions SET {assignments} WHERE id = ?",
                (*clean.values(), revision_id),
            )

    def replace_revision_examples(
        self, revision_id: int, job_id: str, username: str, examples: list[dict]
    ) -> None:
        if self.get_correction_revision(revision_id, username) is None:
            raise PermissionError("Revision does not belong to this user")
        with self.transaction() as connection:
            connection.execute(
                "DELETE FROM correction_examples WHERE revision_id = ?", (revision_id,)
            )
            for example in examples:
                connection.execute(
                    """
                    INSERT INTO correction_examples(
                        revision_id,job_id,user_id,wrong_text,correct_text,context_before,
                        context_after,paragraph_index,sentence_index,change_type,language,
                        is_sensitive,status,created_at
                    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """,
                    (
                        revision_id,
                        job_id,
                        username,
                        example.get("wrong_text", ""),
                        example.get("correct_text", ""),
                        example.get("context_before", ""),
                        example.get("context_after", ""),
                        example.get("paragraph_index"),
                        example.get("sentence_index"),
                        example["change_type"],
                        example.get("language", "unknown"),
                        int(bool(example.get("is_sensitive"))),
                        "proposed",
                        utc_now(),
                    ),
                )
        self.update_correction_revision(
            revision_id, comparison_status="completed", change_count=len(examples)
        )

    def list_correction_examples(
        self, revision_id: int | None = None, status: str | None = None
    ) -> list[dict]:
        clauses: list[str] = []
        params: list[object] = []
        if revision_id is not None:
            clauses.append("revision_id = ?")
            params.append(revision_id)
        if status:
            clauses.append("status = ?")
            params.append(status)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        with closing(self.connect()) as connection:
            rows = connection.execute(
                "SELECT * FROM correction_examples" + where + " ORDER BY id", params
            ).fetchall()
        return [dict(row) for row in rows]

    def review_correction_example(
        self, example_id: int, action: str, reviewer: str
    ) -> None:
        if action not in {"approved", "rejected", "ignored"}:
            raise ValueError("Invalid review action")
        with self.transaction() as connection:
            row = connection.execute(
                """
                SELECT e.*,r.learning_status AS revision_learning_status
                FROM correction_examples e
                JOIN correction_revisions r ON r.id=e.revision_id
                WHERE e.id = ?
                """,
                (example_id,),
            ).fetchone()
            if row is None:
                raise KeyError(example_id)
            if row["user_id"].casefold() != reviewer.casefold():
                raise PermissionError("Example does not belong to this user")
            approved_at = utc_now() if action == "approved" else None
            rejected_at = utc_now() if action == "rejected" else None
            connection.execute(
                """
                UPDATE correction_examples SET status=?,approved_by=?,approved_at=?,rejected_at=?
                WHERE id=?
                """,
                (
                    action,
                    reviewer if action == "approved" else None,
                    approved_at,
                    rejected_at,
                    example_id,
                ),
            )
            if (
                action == "approved"
                and row["revision_learning_status"] == "learning"
                and not row["is_sensitive"]
                and row["wrong_text"]
                and row["correct_text"]
                and not str(row["change_type"]).startswith("formatting:")
            ):
                context = (row["context_before"] or "")[-30:]
                connection.execute(
                    """
                    INSERT INTO correction_memory_rules(
                        wrong_text,correct_text,context_pattern,scope,language,source_count,
                        occurrence_count,accepted_count,confidence,updated_at
                    ) VALUES(?,?,?,?,?,?,?,?,?,?)
                    ON CONFLICT(wrong_text,correct_text,context_pattern,scope,scope_value)
                    DO UPDATE SET
                        occurrence_count=occurrence_count+1,
                        accepted_count=accepted_count+1,
                        source_count=(
                            SELECT COUNT(DISTINCT job_id) FROM correction_examples
                            WHERE wrong_text=excluded.wrong_text AND correct_text=excluded.correct_text
                              AND status='approved'
                        ),
                        updated_at=excluded.updated_at
                    """,
                    (
                        row["wrong_text"],
                        row["correct_text"],
                        context,
                        "global",
                        row["language"],
                        1,
                        1,
                        1,
                        0.0,
                        utc_now(),
                    ),
                )
        self.recalculate_correction_confidence()

    def recalculate_correction_confidence(self) -> None:
        with self.transaction() as connection:
            connection.execute("""
                UPDATE correction_memory_rules SET confidence =
                    MIN(0.99, (accepted_count * 1.0 / MAX(1, accepted_count + rejected_count))
                    * MIN(1.0, source_count / 3.0))
                """)

    def list_memory_rules(self) -> list[dict]:
        with closing(self.connect()) as connection:
            rows = connection.execute(
                "SELECT * FROM correction_memory_rules ORDER BY confidence DESC,id"
            ).fetchall()
        return [dict(row) for row in rows]

    def set_memory_rule_state(
        self, rule_id: int, approved: bool, enabled: bool, reviewer: str
    ) -> None:
        with self.transaction() as connection:
            connection.execute(
                """
                UPDATE correction_memory_rules
                SET approved=?,enabled=?,approved_by=?,approved_at=?,updated_at=?
                WHERE id=? AND is_sensitive=0
                """,
                (
                    int(approved),
                    int(approved and enabled),
                    reviewer if approved else None,
                    utc_now() if approved else None,
                    utc_now(),
                    rule_id,
                ),
            )

    def active_memory_rules(
        self, min_sources: int = 3, threshold: float = 0.9
    ) -> list[dict]:
        with closing(self.connect()) as connection:
            rows = connection.execute(
                """
                SELECT * FROM correction_memory_rules
                WHERE approved=1 AND enabled=1 AND is_sensitive=0
                  AND source_count>=? AND confidence>=?
                ORDER BY confidence DESC,id
                """,
                (min_sources, threshold),
            ).fetchall()
        return [dict(row) for row in rows]

    def record_correction_applications(
        self, job_id: str, applications: list[dict]
    ) -> None:
        with self.transaction() as connection:
            for item in applications:
                connection.execute(
                    """
                    INSERT INTO correction_applications(
                        job_id,rule_id,before_text,after_text,confidence,context_match,applied_at
                    ) VALUES(?,?,?,?,?,?,?)
                    """,
                    (
                        job_id,
                        item["rule_id"],
                        item["before"],
                        item["after"],
                        item["confidence"],
                        int(bool(item["context_match"])),
                        utc_now(),
                    ),
                )

    def correction_readiness(self) -> dict:
        with closing(self.connect()) as connection:
            corrected = connection.execute(
                "SELECT COUNT(DISTINCT job_id) FROM correction_revisions"
            ).fetchone()[0]
            learning = connection.execute(
                "SELECT COUNT(DISTINCT job_id) FROM correction_revisions WHERE learning_status='learning'"
            ).fetchone()[0]
            examples = connection.execute(
                "SELECT COUNT(*) FROM correction_examples"
            ).fetchone()[0]
            trusted = connection.execute(
                "SELECT COUNT(*) FROM correction_memory_rules WHERE approved=1 AND enabled=1"
            ).fetchone()[0]
            evaluation = connection.execute(
                "SELECT COUNT(*) FROM correction_evaluations WHERE dataset_split='evaluation'"
            ).fetchone()[0]
        label = (
            "insufficient"
            if corrected < 10
            else "early" if corrected < 50 else "evaluation_ready"
        )
        return {
            "corrected_files": corrected,
            "learning_files": learning,
            "examples": examples,
            "trusted_rules": trusted,
            "evaluation_size": evaluation,
            "readiness": label,
        }

    def record_correction_evaluation(
        self,
        revision_id: int,
        job_id: str,
        dataset_split: str,
        pre_metrics: dict,
        post_metrics: dict,
    ) -> None:
        if dataset_split not in {"training", "evaluation"}:
            raise ValueError("Invalid dataset split")
        with self.transaction() as connection:
            connection.execute(
                """
                INSERT INTO correction_evaluations(
                    revision_id,job_id,dataset_split,pre_word_accuracy,pre_char_accuracy,
                    post_word_accuracy,post_char_accuracy,created_at
                ) VALUES(?,?,?,?,?,?,?,?)
                """,
                (
                    revision_id,
                    job_id,
                    dataset_split,
                    pre_metrics.get("word_accuracy"),
                    pre_metrics.get("char_accuracy"),
                    post_metrics.get("word_accuracy"),
                    post_metrics.get("char_accuracy"),
                    utc_now(),
                ),
            )

    def correction_evaluation_summary(self) -> dict:
        with closing(self.connect()) as connection:
            row = connection.execute("""
                SELECT COUNT(*) AS samples,AVG(pre_word_accuracy) AS before_accuracy,
                       AVG(post_word_accuracy) AS after_accuracy
                FROM correction_evaluations WHERE dataset_split='evaluation'
                """).fetchone()
        result = dict(row)
        before = result.get("before_accuracy")
        after = result.get("after_accuracy")
        result["improvement"] = (
            None if before is None or after is None else after - before
        )
        return result

    def export_approved_dataset(self) -> str:
        import hashlib
        import json

        with closing(self.connect()) as connection:
            rows = connection.execute("""
                SELECT e.wrong_text,e.correct_text,e.context_before,e.context_after,e.language,
                       e.change_type,r.job_id
                FROM correction_examples e
                JOIN correction_revisions r ON r.id=e.revision_id
                WHERE e.status='approved' AND e.is_sensitive=0
                ORDER BY e.id
                """).fetchall()
        output = []
        for row in rows:
            item = dict(row)
            job_id = item.pop("job_id")
            item["context"] = (
                f"{item.pop('context_before')} … {item.pop('context_after')}".strip()
            )
            item["scope"] = "global"
            item["document_type"] = ""
            item["source_job_hash"] = hashlib.sha256(job_id.encode()).hexdigest()[:16]
            output.append(item)
        return "\n".join(json.dumps(item, ensure_ascii=False) for item in output)

    def record_backup(
        self,
        path: str,
        status: str,
        size_bytes: int = 0,
        error_message: str | None = None,
    ) -> None:
        with self.transaction() as connection:
            connection.execute(
                """
                INSERT INTO backup_history(backup_path, status, size_bytes, error_message, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (path, status, size_bytes, error_message, utc_now()),
            )

    def last_backup(self) -> dict | None:
        with closing(self.connect()) as connection:
            row = connection.execute(
                "SELECT * FROM backup_history ORDER BY id DESC LIMIT 1"
            ).fetchone()
        return dict(row) if row else None

    def hide_conversion(self, job_id: str, username: str) -> bool:
        with self.transaction() as connection:
            cursor = connection.execute(
                """
                UPDATE conversions
                SET hidden = 1, updated_at = ?
                WHERE job_id = ? AND username = ?
                """,
                (utc_now(), job_id, username),
            )
            return cursor.rowcount == 1
