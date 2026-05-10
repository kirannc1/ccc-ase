from __future__ import annotations

import json
import os
import sqlite3
import time
from pathlib import Path
from typing import Any


class SqliteStore:
    def __init__(self, db_path: str) -> None:
        self.db_path = self._resolve_path(db_path)
        self._memory_connection: sqlite3.Connection | None = None
        if self.db_path != ":memory:":
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    def _resolve_path(self, db_path: str) -> str:
        if db_path == ":memory:":
            return db_path
        path = Path(db_path)
        base_dir = Path(os.getenv("SRCGCC_SQLITE_DIR", Path.home() / ".srcgcc-sqlite"))
        if path.is_absolute():
            if path.drive.upper() == "D:":
                return str((base_dir / path.name).resolve())
            return str(path)
        return str((base_dir / path.name).resolve())

    def connect(self) -> sqlite3.Connection:
        if self.db_path == ":memory:":
            if self._memory_connection is None:
                self._memory_connection = sqlite3.connect(self.db_path, check_same_thread=False, timeout=5)
                self._memory_connection.row_factory = sqlite3.Row
                self._memory_connection.execute("pragma journal_mode=MEMORY")
                self._memory_connection.execute("pragma busy_timeout=5000")
            return self._memory_connection
        last_error: Exception | None = None
        for _ in range(3):
            try:
                connection = sqlite3.connect(self.db_path, check_same_thread=False, timeout=5)
                connection.row_factory = sqlite3.Row
                connection.execute("pragma journal_mode=WAL")
                connection.execute("pragma busy_timeout=5000")
                return connection
            except sqlite3.OperationalError as exc:
                last_error = exc
                time.sleep(0.1)
        raise last_error if last_error else sqlite3.OperationalError("unable to open database")

    def execute(self, statement: str, parameters: tuple[Any, ...] = ()) -> None:
        with self.connect() as connection:
            connection.execute(statement, parameters)
            connection.commit()

    def executescript(self, script: str) -> None:
        with self.connect() as connection:
            connection.executescript(script)
            connection.commit()

    def fetch_all(self, statement: str, parameters: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        with self.connect() as connection:
            cursor = connection.execute(statement, parameters)
            return [dict(row) for row in cursor.fetchall()]

    def fetch_one(self, statement: str, parameters: tuple[Any, ...] = ()) -> dict[str, Any] | None:
        with self.connect() as connection:
            cursor = connection.execute(statement, parameters)
            row = cursor.fetchone()
            return dict(row) if row else None

    def json(self, payload: Any) -> str:
        return json.dumps(payload, separators=(",", ":"), default=str)
