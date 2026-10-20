import hashlib
import json
import sqlite3
import threading

from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


GENESIS_HASH = "0" * 64


class AuditLogger:
    """Maintain a persistent, hash-chained audit log."""

    def __init__(self, db_path: str = ":memory:") -> None:
        self.db_path = db_path
        self._lock = threading.RLock()

        if db_path != ":memory:":
            Path(db_path).parent.mkdir(
                parents=True,
                exist_ok=True,
            )

        self._connection = sqlite3.connect(
            db_path,
            check_same_thread=False,
        )

        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_events (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                event_json TEXT NOT NULL
            )
            """
        )
        self._connection.commit()

        self._events: list[dict[str, Any]] = []
        self._load_events()

    def _load_events(self) -> None:
        """Load previously recorded events from SQLite."""
        with self._lock:
            rows = self._connection.execute(
                """
                SELECT event_json
                FROM audit_events
                ORDER BY sequence ASC
                """
            ).fetchall()

            self._events = [
                json.loads(row[0])
                for row in rows
            ]

    @property
    def events(self) -> list[dict[str, Any]]:
        """Return copies of the recorded events."""
        with self._lock:
            return [
                event.copy()
                for event in self._events
            ]

    @staticmethod
    def _calculate_hash(event: dict[str, Any]) -> str:
        """Calculate a deterministic SHA-256 hash."""
        serialized = json.dumps(
            event,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

        return hashlib.sha256(serialized).hexdigest()

    def record_event(
        self,
        *,
        decision: str,
        reason: str,
    ) -> dict[str, Any]:
        """Persist an event linked to the preceding event."""

        with self._lock:
            previous_hash = (
                self._events[-1]["event_hash"]
                if self._events
                else GENESIS_HASH
            )

            event = {
                "event_id": str(uuid4()),
                "timestamp": datetime.now(UTC).isoformat(),
                "decision": decision,
                "reason": reason,
                "previous_hash": previous_hash,
            }

            event["event_hash"] = self._calculate_hash(event)

            serialized = json.dumps(
                event,
                sort_keys=True,
                separators=(",", ":"),
            )

            try:
                self._connection.execute(
                    """
                    INSERT INTO audit_events (event_json)
                    VALUES (?)
                    """,
                    (serialized,),
                )
                self._connection.commit()
            except sqlite3.Error:
                self._connection.rollback()
                raise

            self._events.append(event)

            return event.copy()

    def verify_chain(self) -> bool:
        """Verify event hashes and links throughout the chain."""

        with self._lock:
            expected_previous_hash = GENESIS_HASH

            for event in self._events:
                if event.get("previous_hash") != expected_previous_hash:
                    return False

                stored_hash = event.get("event_hash")

                event_without_hash = {
                    key: value
                    for key, value in event.items()
                    if key != "event_hash"
                }

                calculated_hash = self._calculate_hash(
                    event_without_hash
                )

                if stored_hash != calculated_hash:
                    return False

                expected_previous_hash = stored_hash

            return True

    def close(self) -> None:
        """Close the SQLite connection."""
        with self._lock:
            self._connection.close()