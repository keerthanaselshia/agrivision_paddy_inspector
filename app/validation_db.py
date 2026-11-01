"""
validation_db.py  –  SQLite persistence for severity validation and IRRI benchmarking.

Stores paired measurements:
  • inspection_id (optional, references history inspection)
  • image_hash / image_path
  • device_severity (OpenCV computed %)
  • manual_irri_score (0-9 integer)
  • manual_severity_pct (expert visual estimate %)
  • evaluator_name
  • disease_class
  • notes
  • timestamp
"""

import sqlite3
import threading
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "inspection_history.db"
_lock = threading.Lock()


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_validation_table() -> None:
    """Create the severity_validations table if not already present."""
    with _lock:
        conn = get_connection()
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS severity_validations (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at          TEXT NOT NULL,
                inspection_id       INTEGER,
                disease_class       TEXT,
                device_severity     REAL NOT NULL,
                manual_irri_score   INTEGER NOT NULL,
                manual_severity_pct REAL,
                evaluator_name      TEXT,
                notes               TEXT,
                image_path          TEXT
            )
            """
        )
        conn.commit()


def save_validation(
    device_severity: float,
    manual_irri_score: int,
    *,
    manual_severity_pct: float | None = None,
    inspection_id: int | None = None,
    disease_class: str | None = None,
    evaluator_name: str | None = None,
    notes: str | None = None,
    image_path: str | None = None,
) -> int:
    """Insert one validation record. Returns new row id."""
    init_validation_table()
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    with _lock:
        conn = get_connection()
        cur = conn.execute(
            """
            INSERT INTO severity_validations (
                created_at, inspection_id, disease_class, device_severity,
                manual_irri_score, manual_severity_pct, evaluator_name, notes, image_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                now,
                inspection_id,
                disease_class,
                float(device_severity),
                int(manual_irri_score),
                float(manual_severity_pct) if manual_severity_pct is not None else None,
                evaluator_name or "Expert Evaluator",
                notes or "",
                image_path or "",
            ),
        )
        conn.commit()
        return cur.lastrowid


def get_validations() -> list[dict]:
    """Return all validation pairs, newest first."""
    init_validation_table()
    with _lock:
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM severity_validations ORDER BY id DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def delete_validation(val_id: int) -> bool:
    """Delete a validation record by id."""
    init_validation_table()
    with _lock:
        conn = get_connection()
        cur = conn.execute("DELETE FROM severity_validations WHERE id = ?", (val_id,))
        conn.commit()
        return cur.rowcount > 0
