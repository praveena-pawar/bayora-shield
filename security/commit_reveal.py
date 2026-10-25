import hashlib
import hmac
import json
import secrets
from dataclasses import dataclass


@dataclass(frozen=True)
class Commitment:
    commitment_hash: str
    nonce: str


def create_commitment(payload: str) -> Commitment:
    """Create a SHA-256 commitment using a random nonce."""

    if not isinstance(payload, str) or not payload:
        raise ValueError("Payload must not be empty.")

    nonce = secrets.token_hex(32)

    commitment_data = json.dumps(
        {
            "payload": payload,
            "nonce": nonce,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    commitment_hash = hashlib.sha256(
        commitment_data
    ).hexdigest()

    return Commitment(
        commitment_hash=commitment_hash,
        nonce=nonce,
    )


def verify_commitment(
    payload: str,
    nonce: str,
    expected_hash: str,
) -> bool:
    """Verify that a revealed payload matches its commitment."""

    if not isinstance(payload, str) or not payload:
        return False

    if not isinstance(nonce, str) or not nonce:
        return False

    if not isinstance(expected_hash, str):
        return False

    commitment_data = json.dumps(
        {
            "payload": payload,
            "nonce": nonce,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    calculated_hash = hashlib.sha256(
        commitment_data
    ).hexdigest()

    return hmac.compare_digest(
        calculated_hash,
        expected_hash,
    )
