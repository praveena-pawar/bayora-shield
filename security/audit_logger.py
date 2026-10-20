import hashlib
import json
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


GENESIS_HASH = "0" * 64


class AuditLogger:
    """Maintain an in-memory, hash-chained audit log."""

    def __init__(self) -> None:
        self._events: list[dict[str, Any]] = []

    @property
    def events(self) -> list[dict[str, Any]]:
        """Return a copy of the recorded events."""
        return [event.copy() for event in self._events]

    @staticmethod
    def _calculate_hash(event: dict[str, Any]) -> str:
        """Calculate a deterministic SHA-256 hash for an event."""
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
        """Record an event linked to the preceding event."""
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

        self._events.append(event)

        return event.copy()

    def verify_chain(self) -> bool:
        """Verify event hashes and links throughout the chain."""
        expected_previous_hash = GENESIS_HASH

        for event in self._events:
            if event["previous_hash"] != expected_previous_hash:
                return False

            event_without_hash = {
                key: value
                for key, value in event.items()
                if key != "event_hash"
            }

            calculated_hash = self._calculate_hash(event_without_hash)

            if event["event_hash"] != calculated_hash:
                return False

            expected_previous_hash = event["event_hash"]

        return True