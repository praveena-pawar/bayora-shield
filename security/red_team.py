from dataclasses import dataclass
from enum import Enum


class AttackCategory(str, Enum):
    INSTRUCTION_OVERRIDE = "instruction_override"
    SYSTEM_PROMPT_DISCLOSURE = "system_prompt_disclosure"
    SAFETY_BYPASS = "safety_bypass"
    NORMAL_PROMPT = "normal_prompt"
    EMPTY_INPUT = "empty_input"


class ExpectedDecision(str, Enum):
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    FLAG = "FLAG"


@dataclass(frozen=True)
class RedTeamPayload:
    payload_id: str
    content: str
    category: AttackCategory
    expected_decision: ExpectedDecision


def create_test_payload(
    payload_id: str,
    content: str,
    category: AttackCategory = AttackCategory.INSTRUCTION_OVERRIDE,
    expected_decision: ExpectedDecision = ExpectedDecision.BLOCK,
) -> RedTeamPayload:
    """Create a categorized payload for controlled security evaluation."""

    if not payload_id.strip():
        raise ValueError("payload_id must not be empty")

    if not content.strip():
        raise ValueError("content must not be empty")

    return RedTeamPayload(
        payload_id=payload_id,
        content=content,
        category=category,
        expected_decision=expected_decision,
    )