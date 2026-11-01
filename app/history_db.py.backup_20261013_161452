
import sqlite3
from pathlib import Path
from datetime import datetime

# Store the database inside the app folder
DB_PATH = Path(__file__).resolve().parent / "inspection_history.db"


def init_db():
    """Create the inspection history table if it does not exist."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS inspections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inspected_at TEXT NOT NULL,
                disease TEXT NOT NULL,
                confidence REAL,
                severity REAL,
                severity_grade TEXT,
                location TEXT
            )
        """)


def save_inspection(
    disease,
    confidence,
    severity,
    severity_grade,
    location
):
    """Save one completed inspection."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO inspections (
                inspected_at,
                disease,
                confidence,
                severity,
                severity_grade,
                location
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().astimezone().isoformat(timespec="seconds"),
            str(disease),
            float(confidence) if confidence is not None else None,
            float(severity) if severity is not None else None,
            str(severity_grade) if severity_grade else None,
            str(location) if location else ""
        ))


def get_inspections():
    """Return saved inspections, newest first."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT *
            FROM inspections
            ORDER BY inspected_at DESC, id DESC
        """).fetchall()

    return [dict(row) for row in rows]
