"""
chat_history.py – SQLite-backed shared chat history store.
No login required. All chats are shared/public (visible to everyone).
"""

import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "chat_history.db")


def _get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist."""
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id  TEXT NOT NULL,
                started_at  TEXT NOT NULL,
                title       TEXT NOT NULL DEFAULT 'New Conversation'
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id  TEXT NOT NULL,
                role        TEXT NOT NULL,
                content     TEXT NOT NULL,
                created_at  TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_session
            ON chat_messages(session_id)
        """)
        conn.commit()


def create_session(session_id: str, title: str = "New Conversation") -> None:
    with _get_conn() as conn:
        conn.execute(
            "INSERT INTO chat_sessions (session_id, started_at, title) VALUES (?, ?, ?)",
            (session_id, datetime.utcnow().isoformat(), title)
        )
        conn.commit()


def session_exists(session_id: str) -> bool:
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM chat_sessions WHERE session_id = ?", (session_id,)
        ).fetchone()
        return row is not None


def update_session_title(session_id: str, title: str) -> None:
    with _get_conn() as conn:
        conn.execute(
            "UPDATE chat_sessions SET title = ? WHERE session_id = ?",
            (title[:60], session_id)
        )
        conn.commit()


def save_message(session_id: str, role: str, content: str) -> None:
    with _get_conn() as conn:
        conn.execute(
            "INSERT INTO chat_messages (session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
            (session_id, role, content, datetime.utcnow().isoformat())
        )
        conn.commit()


def load_messages(session_id: str) -> list[dict]:
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT role, content, created_at FROM chat_messages WHERE session_id = ? ORDER BY id",
            (session_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def list_sessions(limit: int = 30) -> list[dict]:
    """Return the most recent sessions (public – all visible to everyone)."""
    with _get_conn() as conn:
        rows = conn.execute(
            """
            SELECT s.session_id, s.title, s.started_at,
                   COUNT(m.id) as message_count
            FROM chat_sessions s
            LEFT JOIN chat_messages m ON s.session_id = m.session_id
            GROUP BY s.session_id
            ORDER BY s.started_at DESC
            LIMIT ?
            """,
            (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


def delete_session(session_id: str) -> None:
    with _get_conn() as conn:
        conn.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id,))
        conn.execute("DELETE FROM chat_sessions WHERE session_id = ?", (session_id,))
        conn.commit()