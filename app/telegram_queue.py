"""
telegram_queue.py  –  Telegram send helper with SQLite offline queue.

Step 10 features:
  • send_photo_telegram() — tries to send immediately; queues on failure
  • test_connection() — verify bot token / chat id with getMe + getChat
  • SQLite queue table in inspection_history.db — survives app restarts
  • sync_queue() — retry every queued message; returns (sent, failed) counts
  • get_queue() — list all pending items
  • delete_queued() — remove a single queued item
  • Queue stores: image bytes (base64), caption, timestamp, retry_count, last_error
"""

import base64
import io
import sqlite3
import threading
from datetime import datetime
from pathlib import Path

import requests
from PIL import Image

DB_PATH = Path(__file__).resolve().parent / "inspection_history.db"
_lock = threading.Lock()
_TIMEOUT = 20  # seconds


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------

def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_telegram_queue() -> None:
    """Create the telegram_queue table if it does not exist."""
    with _lock:
        conn = _get_conn()
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS telegram_queue (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at    TEXT    NOT NULL,
                image_b64     TEXT,
                caption       TEXT,
                token_hint    TEXT,
                chat_id_hint  TEXT,
                retry_count   INTEGER DEFAULT 0,
                last_error    TEXT,
                status        TEXT DEFAULT 'pending'
            )
            """
        )
        conn.commit()


# ---------------------------------------------------------------------------
# Core Telegram API helpers
# ---------------------------------------------------------------------------

def _do_send_photo(token: str, chat_id: str, jpeg_bytes: bytes, caption: str) -> tuple[bool, str]:
    """Low-level POST to Telegram sendPhoto. Returns (success, message)."""
    r = requests.post(
        f"https://api.telegram.org/bot{token}/sendPhoto",
        data={"chat_id": chat_id, "caption": caption[:1024]},
        files={"photo": ("report.jpg", jpeg_bytes, "image/jpeg")},
        timeout=_TIMEOUT,
    )
    return r.ok, r.text[:300]


def test_connection(token: str, chat_id: str) -> tuple[bool, str]:
    """Verify token and chat_id by calling getMe + getChat.

    Returns (success, human-readable message).
    """
    if not token or not chat_id:
        return False, "Token and Chat ID are both required."
    try:
        r_me = requests.get(
            f"https://api.telegram.org/bot{token}/getMe",
            timeout=_TIMEOUT,
        )
        if not r_me.ok:
            return False, f"Invalid bot token. Telegram says: {r_me.text[:200]}"

        bot_name = r_me.json().get("result", {}).get("first_name", "Bot")

        r_chat = requests.post(
            f"https://api.telegram.org/bot{token}/getChat",
            data={"chat_id": chat_id},
            timeout=_TIMEOUT,
        )
        if not r_chat.ok:
            return False, f"Chat ID '{chat_id}' not reachable. {r_chat.text[:200]}"

        chat_title = r_chat.json().get("result", {}).get("title") or r_chat.json().get("result", {}).get("first_name", chat_id)
        return True, f"✅ Connected — Bot: {bot_name} → Chat: {chat_title}"
    except requests.ConnectionError:
        return False, "No internet connection."
    except requests.Timeout:
        return False, "Telegram API timed out."
    except Exception as e:
        return False, f"Error: {e}"


def send_test_message(token: str, chat_id: str) -> tuple[bool, str]:
    """Send a small text-only test ping to verify the full pipeline."""
    if not token or not chat_id:
        return False, "Token and Chat ID are required."
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data={
                "chat_id": chat_id,
                "text": "🌿 AgriVision Paddy Inspector — connection test OK!",
                "parse_mode": "HTML",
            },
            timeout=_TIMEOUT,
        )
        if r.ok:
            return True, "✅ Test message delivered!"
        return False, f"Telegram error: {r.text[:200]}"
    except requests.ConnectionError:
        return False, "No internet connection."
    except Exception as e:
        return False, str(e)


# ---------------------------------------------------------------------------
# Send with auto-queue on failure
# ---------------------------------------------------------------------------

def _pil_to_jpeg_bytes(photo_rgb) -> bytes:
    """Convert a numpy RGB array or PIL Image to JPEG bytes."""
    if isinstance(photo_rgb, Image.Image):
        pil = photo_rgb
    else:
        pil = Image.fromarray(photo_rgb)
    buf = io.BytesIO()
    pil.save(buf, format="JPEG", quality=90)
    return buf.getvalue()


def send_photo_telegram(
    token: str,
    chat_id: str,
    photo_rgb,
    caption: str,
    *,
    queue_on_fail: bool = True,
) -> tuple[bool, str]:
    """Try to send a photo report via Telegram.

    If sending fails and queue_on_fail is True, the message is saved to the
    SQLite offline queue for later retry.

    Returns (sent_now: bool, message: str).
    """
    jpeg_bytes = _pil_to_jpeg_bytes(photo_rgb)

    try:
        ok, msg = _do_send_photo(token, chat_id, jpeg_bytes, caption)
        if ok:
            return True, "✅ Sent to Telegram."
        # API returned an error but we had connectivity
        if queue_on_fail:
            _enqueue(jpeg_bytes, caption, token, chat_id, last_error=msg)
            return False, f"⚠️ Telegram rejected the message — queued for retry. ({msg})"
        return False, f"Telegram error: {msg}"

    except (requests.ConnectionError, requests.Timeout) as exc:
        if queue_on_fail:
            _enqueue(jpeg_bytes, caption, token, chat_id, last_error=str(exc))
            return False, "📴 Offline — message queued. Use 'Sync now' when you have internet."
        return False, f"Network error: {exc}"

    except Exception as exc:
        if queue_on_fail:
            _enqueue(jpeg_bytes, caption, token, chat_id, last_error=str(exc))
            return False, f"⚠️ Unexpected error — queued. ({exc})"
        return False, str(exc)


def _enqueue(jpeg_bytes: bytes, caption: str, token: str, chat_id: str, last_error: str = "") -> None:
    """Insert a failed message into the offline queue."""
    init_telegram_queue()
    b64 = base64.b64encode(jpeg_bytes).decode("ascii")
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    # Store a safe hint (last 8 chars of token, full chat_id)
    token_hint = f"...{token[-8:]}" if len(token) > 8 else "***"
    with _lock:
        conn = _get_conn()
        conn.execute(
            """
            INSERT INTO telegram_queue (created_at, image_b64, caption, token_hint, chat_id_hint, last_error)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (now, b64, caption[:1024], token_hint, chat_id, last_error[:300]),
        )
        conn.commit()


# ---------------------------------------------------------------------------
# Queue management
# ---------------------------------------------------------------------------

def get_queue() -> list[dict]:
    """Return all pending queue items, oldest first."""
    init_telegram_queue()
    with _lock:
        conn = _get_conn()
        rows = conn.execute(
            "SELECT id, created_at, caption, token_hint, chat_id_hint, retry_count, last_error, status "
            "FROM telegram_queue WHERE status = 'pending' ORDER BY id ASC"
        ).fetchall()
    return [dict(r) for r in rows]


def sync_queue(token: str, chat_id: str) -> tuple[int, int]:
    """Retry all pending queued messages.

    Returns (sent_count, failed_count).
    """
    init_telegram_queue()
    with _lock:
        conn = _get_conn()
        rows = conn.execute(
            "SELECT id, image_b64, caption FROM telegram_queue WHERE status = 'pending' ORDER BY id ASC"
        ).fetchall()

    sent = 0
    failed = 0

    for row in rows:
        row_id = row["id"]
        jpeg_bytes = base64.b64decode(row["image_b64"]) if row["image_b64"] else None
        caption = row["caption"] or ""

        try:
            if jpeg_bytes:
                ok, msg = _do_send_photo(token, chat_id, jpeg_bytes, caption)
            else:
                # Text-only fallback
                r = requests.post(
                    f"https://api.telegram.org/bot{token}/sendMessage",
                    data={"chat_id": chat_id, "text": caption[:4096]},
                    timeout=_TIMEOUT,
                )
                ok, msg = r.ok, r.text[:300]

            with _lock:
                conn = _get_conn()
                if ok:
                    conn.execute(
                        "UPDATE telegram_queue SET status = 'sent' WHERE id = ?", (row_id,)
                    )
                    sent += 1
                else:
                    conn.execute(
                        "UPDATE telegram_queue SET retry_count = retry_count + 1, last_error = ? WHERE id = ?",
                        (msg[:300], row_id),
                    )
                    failed += 1
                conn.commit()

        except Exception as exc:
            with _lock:
                conn = _get_conn()
                conn.execute(
                    "UPDATE telegram_queue SET retry_count = retry_count + 1, last_error = ? WHERE id = ?",
                    (str(exc)[:300], row_id),
                )
                conn.commit()
            failed += 1

    return sent, failed


def delete_queued(queue_id: int) -> bool:
    """Remove a single item from the queue."""
    init_telegram_queue()
    with _lock:
        conn = _get_conn()
        cur = conn.execute("DELETE FROM telegram_queue WHERE id = ?", (queue_id,))
        conn.commit()
    return cur.rowcount > 0


def clear_sent() -> int:
    """Remove all items with status='sent'. Returns count removed."""
    init_telegram_queue()
    with _lock:
        conn = _get_conn()
        cur = conn.execute("DELETE FROM telegram_queue WHERE status = 'sent'")
        conn.commit()
    return cur.rowcount


def queue_count() -> int:
    """Return count of pending (unsent) items."""
    init_telegram_queue()
    with _lock:
        conn = _get_conn()
        return conn.execute(
            "SELECT COUNT(*) FROM telegram_queue WHERE status = 'pending'"
        ).fetchone()[0]
