import sqlite3
from datetime import datetime, timezone

DB_PATH = "database/logs.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            event_type TEXT,
            content_id TEXT,
            creator_id TEXT,
            attribution TEXT,
            confidence REAL,
            llm_score REAL,
            heuristic_score REAL,
            label TEXT,
            status TEXT,
            appeal_reasoning TEXT
        )
    """)

    conn.commit()
    conn.close()


def add_log_entry(entry):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO audit_log (
            timestamp, event_type, content_id, creator_id, attribution,
            confidence, llm_score, heuristic_score, label, status, appeal_reasoning
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now(timezone.utc).isoformat(),
        entry.get("event_type"),
        entry.get("content_id"),
        entry.get("creator_id"),
        entry.get("attribution"),
        entry.get("confidence"),
        entry.get("llm_score"),
        entry.get("heuristic_score"),
        entry.get("label"),
        entry.get("status"),
        entry.get("appeal_reasoning"),
    ))

    conn.commit()
    conn.close()


def get_logs(limit=20):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM audit_log
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def add_appeal(content_id, creator_reasoning):
    add_log_entry({
        "event_type": "appeal",
        "content_id": content_id,
        "status": "under_review",
        "appeal_reasoning": creator_reasoning
    })