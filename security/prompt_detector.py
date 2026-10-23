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
            r"everything|earlier\s+given|earlier\s+provided"
            r")\b"
            r"(?:\s+(?:you\s+were\s+told|you\s+received))?"
            r"(?:\s+(?:instructions|directions|rules|"
            r"commands|guidelines))?"
            r"|"
            r"\b(set\s+aside)\b"
            r".{0,80}\b(directions|instructions|guidance|rules)\b"
            r".{0,60}\b(earlier|previous|prior)\b"
            r"|"
            r"\btreat\b"
            r".{0,80}\b(guidance|directions|instructions|rules)\b"
            r".{0,80}\b(invalid|obsolete|superseded)\b"
            r"|"
            r"\bfrom\s+now\s+on\b"
            r".{0,50}\bfollow\b"
            r".{0,50}\bonly\b"
            r".{0,50}\b(rules|instructions|directions|guidance)\b"
            r".{0,50}\b(my\s+message|this\s+message)\b",
            re.IGNORECASE,
        ),
        "Possible instruction override attempt",
    ),

    # Rule 2: System-instruction disclosure
    (
        re.compile(
            r"\b("
            r"reveal|show|print|display|disclose|"
            r"tell\s+me|provide|share|summarize|list"
            r")\b"
            r".{0,100}\b("
            r"hidden|internal|secret|private|confidential|"
            r"system\s+prompt|instructions|directions|"
            r"rules|guidelines|configuration|messages?|"
            r"setup|operating"
            r")\b"
            r"|"
            r"\bwhat\b"
            r".{0,40}\b("
            r"hidden|internal|secret|private|confidential"
            r")\b"
            r".{0,60}\b("
            r"configuration|system\s+prompt|instructions|"
            r"directions|rules|guidelines|messages?"
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
            # Pattern A: Requests to bypass or ignore safety controls
            r"\b("
            r"bypass|circumvent|evade|"
            r"turn\s+off|switch\s+off|"
            r"stop\s+applying|"
            r"find\s+a\s+way\s+around|"
            r"disregard|ignore|"
            r"without\s+enforcing"
            r")\b"
            r".{0,100}\b("
            r"safety|safeguards?|guardrails|"
            r"filters?|restrictions?|"
            r"protections?|controls?|"
            r"content\s+polic(?:y|ies)"
            r")\b"
            r"|"
            # Pattern B: Direct requests to disable safety controls
            r"\b("
            r"disable|deactivate"
            r")\s+"
            r"(?:your\s+|the\s+|a\s+|an\s+)?"
            r"(?:safety\s+)?"
            r"(?:filters?|guardrails|safeguards?|"
            r"protections?|controls?)\b"
            r"(?!\s+(?:during|for|in)\s+"
            r"(?:controlled|authorized|approved|"
            r"legitimate|supervised)\s+testing)"
            r"|"
            # Pattern C: Requests to act as if restrictions are lifted
            r"\b("
            r"proceed|respond|act|continue"
            r")\b"
            r".{0,50}\b("
            r"as\s+if|as\s+though"
            r")\b"
            r".{0,50}\b("
            r"restrictions?|safeguards?|"
            r"protections?|controls?|"
            r"guardrails"
            r")\b"
            r".{0,50}\b("
            r"lifted|removed|disabled|inactive"
            r")\b",
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
