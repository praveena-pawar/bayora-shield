from dataclasses import asdict, dataclass

from evaluator.evaluation_metrics import calculate_metrics
from security.audit_logger import AuditLogger
from security.prompt_detector import inspect_prompt
from security.red_team import RedTeamPayload


@dataclass(frozen=True)
class EvaluationCase:
    case_id: str
    prompt: str
    expected_decision: str


def create_evaluation_cases(
    payloads: list[RedTeamPayload],
) -> list[EvaluationCase]:
    """Convert structured Red Team payloads into evaluation cases."""

    return [
        EvaluationCase(
            case_id=payload.payload_id,
            prompt=payload.content,
            expected_decision=payload.expected_decision.value,
        )
        for payload in payloads
    ]


@dataclass(frozen=True)
class EvaluationResult:
    case_id: str
    expected_decision: str
    actual_decision: str
    passed: bool
    reason: str


def evaluate_cases(
    cases: list[EvaluationCase],
    audit_logger: AuditLogger,
    detector=inspect_prompt,
) -> dict:
    """Evaluate prompts and record each result in the audit log."""

    results = []

    for case in cases:
        detection = detector(case.prompt)
        actual_decision = detection.decision.value
        passed = actual_decision == case.expected_decision

        audit_logger.record_event(
            decision=actual_decision,
            reason=(
                f"Evaluation case {case.case_id}: "
                f"expected={case.expected_decision}, "
                f"actual={actual_decision}, passed={passed}"
            ),
        )

        result = EvaluationResult(
            case_id=case.case_id,
            expected_decision=case.expected_decision,
            actual_decision=actual_decision,
            passed=passed,
            reason=detection.reason,
        )

        results.append(asdict(result))

    total = len(results)
    passed_count = sum(result["passed"] for result in results)


    metrics = calculate_metrics(results)

    return {
        "total_cases": total,
        "passed": passed_count,
        "failed": total - passed_count,
        "pass_rate": round(passed_count / total * 100, 2) if total else 0.0,
        "results": results,
        "metrics": metrics,
        "audit_chain_valid": audit_logger.verify_chain(),
    }
