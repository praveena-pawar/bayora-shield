from evaluator.evaluation_engine import (
    EvaluationCase,
    create_evaluation_cases,
    evaluate_cases,
)
from security.red_team import (
    AttackCategory,
    ExpectedDecision,
    create_test_payload,
)


from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel, Field

from evaluator.evaluation_engine import EvaluationCase, evaluate_cases
from evaluator.security_validator import run_validation
from security.audit_logger import AuditLogger
from security.prompt_detector import inspect_prompt


app = FastAPI(
    title="Bayora Shield",
    description=(
        "An isolated AI security testing platform "
        "for adversarial evaluation and audit integrity."
    ),
    version="0.3.0",
)



PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "data" / "audit.db"

audit_logger = AuditLogger(db_path=str(DATABASE_PATH))


# Request and response schemas

class PromptRequest(BaseModel):
    prompt: str = Field(
        min_length=1,
        max_length=10_000,
        description="The prompt to inspect.",
    )


class PromptInspectionResponse(BaseModel):
    decision: str
    reason: str


class EvaluationCaseRequest(BaseModel):
    case_id: str = Field(min_length=1, max_length=100)
    prompt: str = Field(min_length=1, max_length=10_000)
    expected_decision: str = Field(
        pattern=r"^(ALLOW|BLOCK|FLAG)$",
        description="Expected security decision.",
    )


class EvaluationRequest(BaseModel):
    cases: list[EvaluationCaseRequest] = Field(
        min_length=1,
        max_length=100,
        description="Controlled test cases for evaluation.",
    )

class RedTeamPayloadRequest(BaseModel):
    payload_id: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1, max_length=10_000)
    category: AttackCategory
    expected_decision: ExpectedDecision


class RedTeamEvaluationRequest(BaseModel):
    payloads: list[RedTeamPayloadRequest] = Field(
        min_length=1,
        max_length=100,
    )



# Health endpoint

@app.get("/health")
def health_check() -> dict[str, str]:
    """Report the API service health."""
    return {
        "status": "healthy",
        "service": "Bayora Shield",
    }


# Security inspection endpoint

@app.post(
    "/security/inspect",
    response_model=PromptInspectionResponse,
)
def inspect_prompt_endpoint(
    request: PromptRequest,
) -> PromptInspectionResponse:
    """Inspect a prompt and record the security decision."""

    result = inspect_prompt(request.prompt)

    audit_logger.record_event(
        decision=result.decision.value,
        reason=result.reason,
    )

    return PromptInspectionResponse(
        decision=result.decision.value,
        reason=result.reason,
    )


# Security validation endpoint

@app.post("/security/validate")
def validate_security() -> dict:
    """Run the configured security validation checks."""
    return run_validation()



@app.post("/evaluation/run")
def run_evaluation(request: EvaluationRequest) -> dict:
    """Run controlled security test cases and return an evaluation report."""

    cases = [
        EvaluationCase(
            case_id=case.case_id,
            prompt=case.prompt,
            expected_decision=case.expected_decision,
        )
        for case in request.cases
    ]

    return evaluate_cases(cases, audit_logger)



@app.post("/evaluation/run-red-team")
def run_red_team_evaluation(
    request: RedTeamEvaluationRequest,
) -> dict:
    """Evaluate categorized Red Team payloads."""

    payloads = [
        create_test_payload(
            payload_id=payload.payload_id,
            content=payload.content,
            category=payload.category,
            expected_decision=payload.expected_decision,
        )
        for payload in request.payloads
    ]

    cases = create_evaluation_cases(payloads)

    return evaluate_cases(cases, audit_logger)