import sqlite3
import os
from pathlib import Path


class AppDatabase:
    def __init__(self, db_path: str):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.execute("PRAGMA journal_mode = WAL")
        self._run_migrations()

    def _run_migrations(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                applied_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        from db.schema import MIGRATIONS
        for version, sql in MIGRATIONS:
            row = self.conn.execute(
                "SELECT 1 FROM schema_migrations WHERE version = ?", (version,)
            ).fetchone()
            if not row:
                self.conn.executescript(sql)
                self.conn.execute(
                    "INSERT INTO schema_migrations(version) VALUES (?)", (version,)
                )
        self.conn.commit()

    def execute(self, sql: str, params: tuple | dict | None = None) -> "Statement":
        return Statement(self.conn, sql, params)

    def transaction(self):
        return TransactionContext(self.conn)

    def close(self):
        self.conn.close()


class Statement:
    def __init__(self, conn: sqlite3.Connection, sql: str, params: tuple | dict | None = None):
        self.conn = conn
        self.sql = sql
        self.params = params

    def all(self, params: tuple | list | dict | None = None) -> list[dict]:
        p = params if params is not None else (self.params or ())
        cur = self.conn.execute(self.sql, p)
        return [dict(row) for row in cur.fetchall()]

    def get(self, params: tuple | list | dict | None = None) -> dict | None:
        p = params if params is not None else (self.params or ())
        cur = self.conn.execute(self.sql, p)
        row = cur.fetchone()
        return dict(row) if row else None

    def run(self, params: tuple | list | dict | None = None) -> int:
        p = params if params is not None else (self.params or ())
        cur = self.conn.execute(self.sql, p)
        self.conn.commit()
        return cur.rowcount


class TransactionContext:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def __enter__(self):
        self.conn.execute("BEGIN")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
