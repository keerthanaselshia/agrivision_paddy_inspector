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
            timeout=30.0,
            check_same_thread=False,
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        _conn.row_factory = sqlite3.Row
        try:
            _conn.execute("PRAGMA journal_mode=WAL;")
        except Exception:
            pass
    return _conn


# ---------------------------------------------------------------------------
# Schema helpers
# ---------------------------------------------------------------------------
_CURRENT_SCHEMA_VERSION = 4

# Column definitions for a fresh table (schema v4)
_CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS inspections (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        inspected_at     TEXT    NOT NULL,
        disease          TEXT    NOT NULL,
        confidence       REAL,
        severity         REAL,
        severity_grade   TEXT,
        location         TEXT,
        image_hash       TEXT    UNIQUE,
        probabilities_json TEXT,
        uncertain        INTEGER DEFAULT 0,
        source           TEXT,
        model_version    TEXT,
        notes            TEXT,
        created_at       TEXT,
        latitude         REAL,
        longitude        REAL,
        sent_to_telegram INTEGER DEFAULT 0,
        image_path       TEXT,
        qa_history_json  TEXT
    )
"""

_CREATE_UNANSWERED_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS unanswered_questions (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        question   TEXT NOT NULL,
        disease    TEXT,
        lang       TEXT DEFAULT 'en',
        created_at TEXT NOT NULL
    )
"""

# Columns added in v2
_V2_COLUMNS = [
    ("image_hash",         "TEXT"),
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

# Columns added in v3
_V3_COLUMNS = [
    ("image_path", "TEXT"),
]

# Columns added in v4
_V4_COLUMNS = [
    ("qa_history_json", "TEXT"),
]


def _add_column_if_missing(conn: sqlite3.Connection, col: str, typedef: str) -> None:
    """ALTER TABLE inspections ADD COLUMN only when the column is absent."""
    existing = {row[1] for row in conn.execute("PRAGMA table_info(inspections)")}
    if col not in existing:
        conn.execute(f"ALTER TABLE inspections ADD COLUMN {col} {typedef}")


def _migrate(conn: sqlite3.Connection) -> None:
    """Bring an existing database up to the current schema version."""
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    if version >= _CURRENT_SCHEMA_VERSION:
        return

    if version < 2:
        for col, typedef in _V2_COLUMNS:
            _add_column_if_missing(conn, col, typedef)
        conn.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_image_hash "
            "ON inspections (image_hash)"
        )

    if version < 3:
        for col, typedef in _V3_COLUMNS:
            _add_column_if_missing(conn, col, typedef)

    if version < 4:
        for col, typedef in _V4_COLUMNS:
            _add_column_if_missing(conn, col, typedef)

    conn.execute(_CREATE_UNANSWERED_TABLE_SQL)
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
    image_path: str | None = None,   # relative path under history/images/
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
            sent_to_telegram, image_path
        ) VALUES (
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?
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
        image_path,
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


def get_inspection_by_id(inspection_id: int) -> dict | None:
    """Return a single inspection record as a dict, or None if not found."""
    with _lock:
        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM inspections WHERE id = ?", (inspection_id,)
        ).fetchone()
    return dict(row) if row else None


def delete_inspection(inspection_id: int, delete_image: bool = True) -> bool:
    """Delete one inspection record by id.

    If delete_image is True and the record has an image_path, the image file
    is also removed from disk.  Returns True if a row was deleted, False if
    the id was not found.
    """
    # First fetch so we can optionally remove the image file
    rec = get_inspection_by_id(inspection_id)
    if rec is None:
        return False

    if delete_image and rec.get("image_path"):
        img_file = Path(__file__).resolve().parent.parent / rec["image_path"]
        try:
            if img_file.exists():
                img_file.unlink()
        except OSError:
            pass  # best-effort

    with _lock:
        conn = get_connection()
        cur = conn.execute(
            "DELETE FROM inspections WHERE id = ?", (inspection_id,)
        )
        conn.commit()
    return cur.rowcount > 0


def delete_inspections(ids: list[int], delete_images: bool = True) -> int:
    """Delete multiple inspections by id list.  Returns count deleted."""
    return sum(delete_inspection(i, delete_images) for i in ids)


def get_schema_version() -> int:
    """Return the PRAGMA user_version stored in the database."""
    with _lock:
        return get_connection().execute("PRAGMA user_version").fetchone()[0]


def update_inspection_qa(image_hash: str, qa_history: list[dict]) -> bool:
    """Save or update Q&A conversation history for a given inspection."""
    if not image_hash:
        return False
    qa_json = json.dumps(qa_history, ensure_ascii=False)
    with _lock:
        conn = get_connection()
        cur = conn.execute(
            "UPDATE inspections SET qa_history_json = ? WHERE image_hash = ?",
            (qa_json, image_hash),
        )
        conn.commit()
    return cur.rowcount > 0


def log_unanswered_question(question: str, disease: str | None = None, lang: str = "en") -> bool:
    """Record an unanswered user question to the database for future knowledge-base updates."""
    if not question or not question.strip():
        return False
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    with _lock:
        conn = get_connection()
        conn.execute(
            "INSERT INTO unanswered_questions (question, disease, lang, created_at) VALUES (?, ?, ?, ?)",
            (question.strip(), disease, lang, now),
        )
        conn.commit()
    return True


def get_unanswered_questions() -> list[dict]:
    """Retrieve all logged unanswered questions."""
    with _lock:
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM unanswered_questions ORDER BY created_at DESC, id DESC"
        ).fetchall()
    return [dict(row) for row in rows]

