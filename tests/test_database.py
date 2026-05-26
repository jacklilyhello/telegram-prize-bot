from __future__ import annotations

import sqlite3

from app.database import ClaimsRepository


def test_init_db_creates_table(tmp_path):
    db_path = tmp_path / "claims.db"
    repo = ClaimsRepository(db_path)
    repo.init()

    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='claims'"
        ).fetchone()
    assert row is not None


def test_first_claim_success_second_fails(tmp_path):
    repo = ClaimsRepository(tmp_path / "claims.db")
    repo.init()
    assert repo.try_claim(123, "prize-a") is True
    assert repo.try_claim(123, "prize-a") is False


def test_has_claimed_state(tmp_path):
    repo = ClaimsRepository(tmp_path / "claims.db")
    repo.init()
    assert repo.has_claimed(999) is False
    assert repo.try_claim(999, "prize") is True
    assert repo.has_claimed(999) is True
