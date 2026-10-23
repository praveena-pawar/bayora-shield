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
    # Rule 1: Instruction manipulation
    (
        re.compile(
            r"\b("
            r"ignore|disregard|forget|override|"
            r"replace|supersede|abandon"
            r")\s+"
            r"(?:(?:all|the|your|any)\s+)*"
            r"(?:"
            r"previous|prior|earlier|old|existing|original|"
            r"everything|earlier\s+given|"
            r"earlier\s+provided"
            r")\b"
            r"(?:\s+(?:you\s+were\s+told|you\s+received))?"
            r"(?:\s+(?:instructions|directions|rules|"
            r"commands|guidelines))?",
            re.IGNORECASE,
        ),
        "Possible instruction override attempt",
    ),

    # Rule 2: Direct system-instruction disclosure
    (
        re.compile(
            r"\b("
            r"reveal|show|print|display|disclose|expose|"
            r"tell\s+me|provide|share|"
            r"what\s+(?:are|were|is|was)"
            r")\b"
            r".{0,100}\b("
            r"hidden|internal|secret|private|confidential|"
            r"system\s+prompt|instructions|directions|"
            r"rules|guidelines|configuration|"
            r"messages?"
            r")\b",
            re.IGNORECASE,
        ),
        "Possible system-instruction disclosure attempt",
    ),

    # Rule 3: Indirect hidden-instruction disclosure
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

    # Rule 4: Safety-control bypass
    (
        re.compile(
            r"\b("
            r"bypass|circumvent|evade|"
            r"turn\s+off|switch\s+off|"
            r"stop\s+applying|"
            r"find\s+a\s+way\s+around"
            r")\b"
            r".{0,100}\b("
            r"safety|safeguards?|guardrails|"
            r"filters?|restrictions?|"
            r"protections?|controls?|"
            r"content\s+polic(?:y|ies)"
            r")\b"
            r"|"
            r"\b("
            r"disable|deactivate"
            r")\s+"
            r"(?:your\s+|the\s+)?"
            r"(?:safety\s+)?"
            r"(?:filters?|guardrails|safeguards?|"
            r"protections?|controls?)\b",
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
