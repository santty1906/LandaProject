from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .config import DB_PATH


@dataclass(slots=True)
class UserRecord:
    id: int
    username: str
    full_name: str
    password_hash: str
    face_enabled: bool


class Storage:
    def __init__(self, db_path: Path = DB_PATH) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    @contextmanager
    def _connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        try:
            connection.execute("PRAGMA foreign_keys = ON;")
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    full_name TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    face_enabled INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    last_login_at TEXT
                );

                CREATE TABLE IF NOT EXISTS face_samples (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    pose_label TEXT NOT NULL,
                    image_blob BLOB NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS security_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    event_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    similarity REAL,
                    note TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
                );
                """
            )

    def create_user(self, username: str, full_name: str, password_hash: str) -> UserRecord:
        timestamp = datetime.now(timezone.utc).isoformat()
        with self._connect() as connection:
            try:
                cursor = connection.execute(
                    """
                    INSERT INTO users(username, full_name, password_hash, face_enabled, created_at)
                    VALUES (?, ?, ?, 0, ?)
                    """,
                    (username, full_name, password_hash, timestamp),
                )
            except sqlite3.IntegrityError as exc:
                raise ValueError("El nombre de usuario ya existe") from exc
            return UserRecord(id=cursor.lastrowid, username=username, full_name=full_name, password_hash=password_hash, face_enabled=False)

    def get_user_by_username(self, username: str) -> UserRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT id, username, full_name, password_hash, face_enabled FROM users WHERE username = ?",
                (username,),
            ).fetchone()
            if row is None:
                return None
            return UserRecord(
                id=row["id"],
                username=row["username"],
                full_name=row["full_name"],
                password_hash=row["password_hash"],
                face_enabled=bool(row["face_enabled"]),
            )

    def get_user_by_id(self, user_id: int) -> UserRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT id, username, full_name, password_hash, face_enabled FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
            if row is None:
                return None
            return UserRecord(
                id=row["id"],
                username=row["username"],
                full_name=row["full_name"],
                password_hash=row["password_hash"],
                face_enabled=bool(row["face_enabled"]),
            )

    def update_password(self, user_id: int, password_hash: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (password_hash, user_id),
            )

    def set_face_enabled(self, user_id: int, enabled: bool) -> None:
        with self._connect() as connection:
            connection.execute(
                "UPDATE users SET face_enabled = ? WHERE id = ?",
                (1 if enabled else 0, user_id),
            )

    def mark_login(self, user_id: int) -> None:
        timestamp = datetime.now(timezone.utc).isoformat()
        with self._connect() as connection:
            connection.execute(
                "UPDATE users SET last_login_at = ? WHERE id = ?",
                (timestamp, user_id),
            )

    def save_face_sample(self, user_id: int, pose_label: str, image_blob: bytes) -> int:
        timestamp = datetime.now(timezone.utc).isoformat()
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO face_samples(user_id, pose_label, image_blob, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, pose_label, image_blob, timestamp),
            )
            return cursor.lastrowid

    def list_face_samples(self, user_id: int | None = None) -> list[sqlite3.Row]:
        with self._connect() as connection:
            if user_id is None:
                rows = connection.execute(
                    """
                    SELECT fs.id, fs.user_id, fs.pose_label, fs.image_blob, fs.created_at,
                           u.username, u.full_name
                    FROM face_samples fs
                    JOIN users u ON u.id = fs.user_id
                    ORDER BY fs.created_at ASC
                    """
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    SELECT fs.id, fs.user_id, fs.pose_label, fs.image_blob, fs.created_at,
                           u.username, u.full_name
                    FROM face_samples fs
                    JOIN users u ON u.id = fs.user_id
                    WHERE fs.user_id = ?
                    ORDER BY fs.created_at ASC
                    """,
                    (user_id,),
                ).fetchall()
            return list(rows)

    def face_sample_count(self, user_id: int) -> int:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT COUNT(*) AS total FROM face_samples WHERE user_id = ?",
                (user_id,),
            ).fetchone()
            return int(row["total"] if row is not None else 0)

    def record_event(
        self,
        event_type: str,
        status: str,
        note: str,
        user_id: int | None = None,
        similarity: float | None = None,
    ) -> None:
        timestamp = datetime.now(timezone.utc).isoformat()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO security_events(user_id, event_type, status, similarity, note, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (user_id, event_type, status, similarity, note, timestamp),
            )

    def recent_events(self, limit: int = 12) -> list[sqlite3.Row]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT se.id, se.event_type, se.status, se.similarity, se.note, se.created_at,
                       u.username, u.full_name
                FROM security_events se
                LEFT JOIN users u ON u.id = se.user_id
                ORDER BY se.created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            return list(rows)
