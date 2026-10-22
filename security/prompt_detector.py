import re
from dataclasses import dataclass
from enum import Enum


class SecurityDecision(str, Enum):
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    FLAG = "FLAG"


@dataclass(frozen=True)
class DetectionResult:
    decision: SecurityDecision
    reason: str


# Initial heuristic rules for our prototype.
DETECTION_RULES = [
    (
        re.compile(
            r"\b(ignore|disregard|forget|override)\s+"
            r"(all\s+)?(the\s+)?"
            r"(previous|prior|earlier|everything)\b"
            r"(\s+you\s+were\s+told)?"
            r"(\s+(instructions|directions|rules))?",
            re.IGNORECASE,
        ),
        "Possible instruction override attempt",
    ),
    (
        re.compile(
            r"\breveal\s+(your\s+)?system\s+prompt\b",
            re.IGNORECASE,
        ),
        "Possible system-prompt disclosure attempt",
    ),
    (
        re.compile(
            r"\b(bypass|disable)\s+(the\s+)?safety\s+"
            r"(filter|filters|guardrails)\b",
            re.IGNORECASE,
        ),
        "Possible safety-control bypass attempt",
    ),
    (
        re.compile(
            r"\b(disregard|forget|override)\s+"
            r"(all\s+)?(the\s+)?"
            r"(previous|prior|earlier|everything)\s+"
            r"(instructions|directions|rules|"
            r"everything\s+you\s+were\s+told)\b",
            re.IGNORECASE,
        ),
        "Possible instruction override attempt",
    ),
    (
        re.compile(
            r"\b(show|disclose|expose|print|reveal)\b"
            r".{0,50}\b(hidden|internal|secret)\b"
            r".{0,80}\b(instructions|system\s+prompt)\b",
            re.IGNORECASE,
        ),
        "Possible hidden-instruction disclosure attempt",
    ),
    (
        re.compile(
            r"\b(turn\s+off|disable|deactivate)\s+"
            r"(your\s+)?(safety\s+)?"
            r"(guardrails|safety\s+controls|safety\s+filters)\b",
            re.IGNORECASE,
        ),
        "Possible safety-control bypass attempt",
    ),
]


def inspect_prompt(prompt: str) -> DetectionResult:
    """Inspect a prompt using simple, explainable heuristic rules."""

    if not prompt.strip():
        return DetectionResult(
            decision=SecurityDecision.FLAG,
            reason="Empty prompt requires validation",
        )

    for pattern, reason in DETECTION_RULES:
        if pattern.search(prompt):
            return DetectionResult(
                decision=SecurityDecision.BLOCK,
                reason=reason,
            )

    return DetectionResult(
        decision=SecurityDecision.ALLOW,
        reason="No configured suspicious pattern detected",
    )
