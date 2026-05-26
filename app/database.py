from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path


class ClaimsRepository:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def init(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS claims (
                  tg_id INTEGER PRIMARY KEY,
                  prize TEXT NOT NULL,
                  claimed_at TEXT NOT NULL
                );
                """
            )
            conn.commit()

    def has_claimed(self, tg_id: int) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT 1 FROM claims WHERE tg_id = ?", (tg_id,)).fetchone()
            return row is not None

    def try_claim(self, tg_id: int, prize: str) -> bool:
        claimed_at = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            try:
                conn.execute("BEGIN IMMEDIATE")
                conn.execute(
                    "INSERT INTO claims (tg_id, prize, claimed_at) VALUES (?, ?, ?)",
                    (tg_id, prize, claimed_at),
                )
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                conn.rollback()
                return False
