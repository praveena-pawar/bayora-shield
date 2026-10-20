from dataclasses import dataclass


@dataclass(frozen=True)
class RedTeamPayload:
    payload_id: str
    content: str


def create_test_payload(
    payload_id: str,
    content: str,
) -> RedTeamPayload:
    """Create a controlled payload for security evaluation."""
    if not payload_id.strip():
        raise ValueError("payload_id must not be empty")

    if not content.strip():
        raise ValueError("content must not be empty")

    return RedTeamPayload(
        payload_id=payload_id,
        content=content,
    )