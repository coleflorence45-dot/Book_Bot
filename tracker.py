# tracker.py — Seen items persistence (Books Bot)
# Uses SQLite so seen items survive bot restarts.
# Falls back gracefully if the DB is locked or corrupt.

import os
import sqlite3

DB_FILE   = "seen_items.db"
SEEN_FILE = "seen_items.txt"   # legacy — migrated on first run


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE, timeout=5)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS seen (item_id TEXT PRIMARY KEY, ts DATETIME DEFAULT CURRENT_TIMESTAMP)"
    )
    conn.commit()
    return conn


def _migrate_legacy():
    """One-time migration of seen_items.txt → SQLite on first run."""
    if not os.path.exists(SEEN_FILE):
        return
    try:
        with open(SEEN_FILE, "r") as f:
            ids = [line.strip() for line in f if line.strip()]
        if not ids:
            return
        conn = _connect()
        conn.executemany(
            "INSERT OR IGNORE INTO seen (item_id) VALUES (?)",
            [(i,) for i in ids]
        )
        conn.commit()
        conn.close()
        os.rename(SEEN_FILE, SEEN_FILE + ".migrated")
        print(f"  📦 Migrated {len(ids)} seen items from text file to SQLite")
    except Exception as e:
        print(f"  [tracker] Migration failed: {e}")


# Run migration once at import time
_migrate_legacy()


def load_seen() -> set:
    try:
        conn  = _connect()
        rows  = conn.execute("SELECT item_id FROM seen").fetchall()
        conn.close()
        return {r[0] for r in rows}
    except Exception as e:
        print(f"  [tracker] load_seen error: {e}")
        return set()


def save_seen(seen_ids: set):
    """Bulk-save a full set of IDs — used at end of scan to persist new items."""
    try:
        conn = _connect()
        conn.executemany(
            "INSERT OR IGNORE INTO seen (item_id) VALUES (?)",
            [(i,) for i in seen_ids]
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"  [tracker] save_seen error: {e}")


def mark_seen(item_id) -> None:
    """Mark a single item as seen immediately — call as soon as item is processed."""
    try:
        conn = _connect()
        conn.execute("INSERT OR IGNORE INTO seen (item_id) VALUES (?)", (str(item_id),))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"  [tracker] mark_seen error: {e}")


def is_new(item_id, seen_ids: set) -> bool:
    return str(item_id) not in seen_ids