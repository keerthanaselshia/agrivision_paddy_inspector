"""
history_db.py  –  Thread-safe SQLite helper for AgriVision Paddy Inspector.

All DB access goes through get_connection(), which returns a single
module-level connection protected by a threading.Lock.  Streamlit reruns the
whole script on every interaction, so we keep the connection alive at module
level and never close it explicitly (sqlite3 will close it at process exit).

Schema versioning:
    PRAGMA user_version is set to 2 after the Phase-1 migration.
    Future migrations should bump it to 3, 4, … and check accordingly.
"""

import json
import sqlite3
import threading
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Path to the SQLite database (same folder as this file)
# ---------------------------------------------------------------------------
DB_PATH = Path(__file__).resolve().parent / "inspection_history.db"

# ---------------------------------------------------------------------------
# Thread-safe singleton connection
# ---------------------------------------------------------------------------
_lock = threading.Lock()
_conn: sqlite3.Connection | None = None  # module-level singleton


def get_connection() -> sqlite3.Connection:
    """Return the singleton connection, creating it on first call.

    Uses check_same_thread=False because Streamlit may call helpers from
    different threads.  All public functions in this module acquire _lock
    before touching the connection, so concurrent access is safe.
    """
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(
            DB_PATH,
            check_same_thread=False,
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        _conn.row_factory = sqlite3.Row
    return _conn


# ---------------------------------------------------------------------------
# Schema helpers
# ---------------------------------------------------------------------------
_CURRENT_SCHEMA_VERSION = 2

# Column definitions for a fresh table (schema v2)
_CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS inspections (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        inspected_at     TEXT    NOT NULL,          -- ISO-8601 timestamp
        disease          TEXT    NOT NULL,
        confidence       REAL,
        severity         REAL,
        severity_grade   TEXT,
        location         TEXT,
        -- Phase-1 additions ------------------------------------------------
        image_hash       TEXT    UNIQUE,            -- SHA-256 of raw pixels
        probabilities_json TEXT,                    -- JSON array of floats
        uncertain        INTEGER DEFAULT 0,         -- 1 = below conf threshold
        source           TEXT,                      -- 'upload' or 'camera'
        model_version    TEXT,                      -- e.g. 'paddy_int8.tflite'
        notes            TEXT,
        created_at       TEXT,                      -- same as inspected_at (ISO)
        latitude         REAL,
        longitude        REAL,
        sent_to_telegram INTEGER DEFAULT 0
    )
"""

# Columns added in v2 that may be absent in older databases.
# NOTE: SQLite does not allow ALTER TABLE ADD COLUMN … UNIQUE.
# The uniqueness on image_hash is enforced via a separate index (see _migrate).
_V2_COLUMNS = [
    ("image_hash",         "TEXT"),           # unique index added separately
    ("probabilities_json", "TEXT"),
    ("uncertain",          "INTEGER DEFAULT 0"),
    ("source",             "TEXT"),
    ("model_version",      "TEXT"),
    ("notes",              "TEXT"),
    ("created_at",         "TEXT"),
    ("latitude",           "REAL"),
    ("longitude",          "REAL"),
    ("sent_to_telegram",   "INTEGER DEFAULT 0"),
]


def _add_column_if_missing(conn: sqlite3.Connection, col: str, typedef: str) -> None:
    """ALTER TABLE inspections ADD COLUMN … only when the column is absent."""
    existing = {row[1] for row in conn.execute("PRAGMA table_info(inspections)")}
    if col not in existing:
        conn.execute(f"ALTER TABLE inspections ADD COLUMN {col} {typedef}")


def _migrate(conn: sqlite3.Connection) -> None:
    """Bring an existing database up to the current schema version."""
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    if version >= _CURRENT_SCHEMA_VERSION:
        return  # nothing to do

    # Add every v2 column that is missing (safe to call repeatedly).
    for col, typedef in _V2_COLUMNS:
        _add_column_if_missing(conn, col, typedef)

    # SQLite forbids ALTER TABLE ADD COLUMN UNIQUE, so the uniqueness on
    # image_hash is enforced via a separate index created here.
    conn.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_image_hash "
        "ON inspections (image_hash)"
    )

    conn.execute(f"PRAGMA user_version = {_CURRENT_SCHEMA_VERSION}")
    conn.commit()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def init_db() -> None:
    """Create the table (if new) and apply any pending schema migrations.

    Safe to call multiple times; Streamlit calls it on every rerun.
    """
    with _lock:
        conn = get_connection()
        conn.execute(_CREATE_TABLE_SQL)
        conn.commit()
        _migrate(conn)


def save_inspection(
    disease: str,
    confidence: float | None,
    severity: float | None,
    severity_grade: str | None,
    location: str | None,
    *,
    image_hash: str | None = None,
    probabilities: list[float] | None = None,
    uncertain: bool = False,
    source: str | None = None,       # 'upload' or 'camera'
    model_version: str | None = None,
    notes: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    sent_to_telegram: bool = False,
) -> bool:
    """Insert one inspection record.

    Returns True on success, False if the image_hash already exists (duplicate)
    or if any other DB error occurs.

    All keyword arguments beyond the original five are optional so that existing
    call sites continue to work without modification.
    """
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    probs_json = json.dumps(probabilities) if probabilities is not None else None

    sql = """
        INSERT INTO inspections (
            inspected_at, disease, confidence, severity, severity_grade,
            location, image_hash, probabilities_json, uncertain, source,
            model_version, notes, created_at, latitude, longitude,
            sent_to_telegram
        ) VALUES (
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?
        )
    """
    values = (
        now,
        str(disease),
        float(confidence) if confidence is not None else None,
        float(severity)   if severity   is not None else None,
        str(severity_grade) if severity_grade else None,
        str(location) if location else "",
        image_hash,
        probs_json,
        1 if uncertain else 0,
        source,
        model_version,
        notes,
        now,            # created_at mirrors inspected_at
        float(latitude)  if latitude  is not None else None,
        float(longitude) if longitude is not None else None,
        1 if sent_to_telegram else 0,
    )

    try:
        with _lock:
            conn = get_connection()
            conn.execute(sql, values)
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        # UNIQUE constraint on image_hash – this image was already saved
        return False
    except sqlite3.Error as exc:
        # Surface the error to the caller (app.py will display it)
        raise RuntimeError(f"Database error while saving inspection: {exc}") from exc


def get_inspections() -> list[dict]:
    """Return all inspections as a list of dicts, newest first."""
    with _lock:
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM inspections ORDER BY inspected_at DESC, id DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def get_schema_version() -> int:
    """Return the PRAGMA user_version stored in the database."""
    with _lock:
        return get_connection().execute("PRAGMA user_version").fetchone()[0]
