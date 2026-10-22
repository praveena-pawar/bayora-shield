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


# Explainable heuristic rules for the prototype.
DETECTION_RULES = [
    (
        re.compile(
            r"\b(ignore|disregard|forget|override)\s+"
            r"(all\s+)?(the\s+)?"
            r"(previous|prior|earlier|old|existing|"
            r"original|everything)\b"
            r"(\s+you\s+were\s+told)?"
            r"(\s+(instructions|directions|rules|"
            r"commands|guidelines))?",
            re.IGNORECASE,
        ),
        "Possible instruction override attempt",
    ),
    (
        re.compile(
            r"\b(reveal|show|print|display|disclose|expose)\s+"
            r"(me\s+)?(your\s+)?"
            r"(hidden\s+|internal\s+|secret\s+)?"
            r"(system\s+prompt|instructions|directions|"
            r"rules|guidelines)\b",
            re.IGNORECASE,
        ),
        "Possible system-instruction disclosure attempt",
    ),
    (
        re.compile(
            r"\b(show|disclose|expose|print|reveal|display)\b"
            r".{0,80}\b(hidden|internal|secret)\b"
            r".{0,80}\b(instructions|system\s+prompt|"
            r"guidelines|rules)\b",
            re.IGNORECASE,
        ),
        "Possible hidden-instruction disclosure attempt",
    ),
    (
        re.compile(
            r"\b(bypass|disable|deactivate|turn\s+off|"
            r"switch\s+off|circumvent)\s+"
            r"(the\s+|your\s+)?"
            r"(safety\s+)?"
            r"(filters?|guardrails|safety\s+controls|"
            r"safeguards|content\s+filters)\b",
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
