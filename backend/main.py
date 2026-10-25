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



import httpx
from fastapi import HTTPException


from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel, Field

from evaluator.evaluation_engine import EvaluationCase, evaluate_cases
from evaluator.security_validator import run_validation
from security.audit_logger import AuditLogger
from security.prompt_detector import (
    DetectionResult,
    SecurityDecision,
    inspect_prompt,
)


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



def inspect_with_blue_team(prompt: str) -> DetectionResult:
    """Send a prompt to the separate Blue Team service."""

    blue_team_url = "http://blue-team:8003/defend"

    try:
        response = httpx.post(
            blue_team_url,
            json={"prompt": prompt},
            timeout=5.0,
        )
        response.raise_for_status()
        data = response.json()

    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=504,
            detail="Blue Team service timed out.",
        ) from exc

    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not communicate with the Blue Team service.",
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=502,
            detail="Blue Team service returned invalid JSON.",
        ) from exc

    try:
        decision = SecurityDecision(data["decision"])
        reason = data["reason"]

        if not isinstance(reason, str):
            raise ValueError("Invalid reason")

    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail="Blue Team service returned an invalid response.",
        ) from exc

    return DetectionResult(
        decision=decision,
        reason=reason,
    )

class ModelInferenceResponse(BaseModel):
    response: str


def request_model_inference(prompt: str) -> ModelInferenceResponse:
    """Send an approved prompt to the Model Gateway."""

    gateway_url = "http://model-gateway:8005/infer"

    try:
        response = httpx.post(
            gateway_url,
            json={"prompt": prompt},
            timeout=15.0,
        )
        response.raise_for_status()

    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=504,
            detail="Model Gateway timed out.",
        ) from exc

    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail="Model Gateway returned an unsuccessful response.",
        ) from exc

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail="Could not communicate with the Model Gateway.",
        ) from exc

    try:
        return ModelInferenceResponse.model_validate(response.json())
    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=502,
            detail="Model Gateway returned an invalid response.",
        ) from exc





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


class InferenceResponse(BaseModel):
    decision: str
    reason: str
    response: str | None = None


class AuditEventResponse(BaseModel):
    sequence: int
    event_id: str
    timestamp: str
    decision: str
    reason: str
    previous_hash: str
    event_hash: str


class AuditEventsResponse(BaseModel):
    total: int
    events: list[AuditEventResponse]


class AuditVerificationResponse(BaseModel):
    valid: bool
    total_events: int




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


# Read-only audit endpoints

@app.get("/audit/events", response_model=AuditEventsResponse)
def get_audit_events(
    limit: int = 50,
) -> AuditEventsResponse:
    """Return the most recent audit events."""

    if not 1 <= limit <= 500:
        raise HTTPException(
            status_code=422,
            detail="Limit must be between 1 and 500.",
        )

    rows = audit_logger._connection.execute(
        """
        SELECT sequence, event_json
        FROM audit_events
        ORDER BY sequence DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()

    events = [
        AuditEventResponse(
            sequence=sequence,
            **__import__("json").loads(event_json),
        )
        for sequence, event_json in rows
    ]

    return AuditEventsResponse(
        total=len(events),
        events=events,
    )


@app.get(
    "/audit/verify",
    response_model=AuditVerificationResponse,
)
def verify_audit_chain() -> AuditVerificationResponse:
    """Verify the integrity of the complete audit chain."""

    return AuditVerificationResponse(
        valid=audit_logger.verify_chain(),
        total_events=len(audit_logger.events),
    )




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


# Secure model inference endpoint

@app.post("/inference", response_model=InferenceResponse)
def secure_inference(
    request: PromptRequest,
) -> InferenceResponse:
    """Inspect a prompt before allowing access to model inference."""

    # Step 1: Ask the Blue Team to inspect the prompt.
    result = inspect_with_blue_team(request.prompt)

    # Step 2: Record the security decision.
    audit_logger.record_event(
        decision=result.decision.value,
        reason=result.reason,
    )

    # Step 3: Block inference unless the decision is ALLOW.
    if result.decision != SecurityDecision.ALLOW:
        return InferenceResponse(
            decision=result.decision.value,
            reason=result.reason,
            response=None,
        )

    # Step 4: Only approved prompts reach the Model Gateway.
    model_result = request_model_inference(request.prompt)

    return InferenceResponse(
        decision=result.decision.value,
        reason=result.reason,
        response=model_result.response,
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



@app.post("/evaluation/run-red-team-suite")
def run_red_team_suite() -> dict:
    """Fetch the Red Team suite and evaluate it through the existing engine."""
    red_team_url = "http://red-team:8002/test-suite"

    try:
        response = httpx.get(red_team_url, timeout=5.0)
        response.raise_for_status()
        data = response.json()
    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=504,
            detail="Red Team service timed out.",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not retrieve the Red Team test suite.",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=502,
            detail="Red Team service returned invalid JSON.",
        ) from exc

    raw_payloads = data.get("payloads")
    if not isinstance(raw_payloads, list) or not raw_payloads:
        raise HTTPException(
            status_code=502,
            detail="Red Team service returned an invalid or empty test suite.",
        )

    try:
        payloads = [
            create_test_payload(
                payload_id=item["payload_id"],
                content=item["content"],
                category=AttackCategory(item["category"]),
                expected_decision=ExpectedDecision(item["expected_decision"]),
            )
            for item in raw_payloads
        ]
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        raise HTTPException(
            status_code=502,
            detail="Red Team service returned an invalid payload.",
        ) from exc

    cases = create_evaluation_cases(payloads)
    return evaluate_cases(cases, audit_logger)




@app.post("/evaluation/run-blue-team-suite")
def run_blue_team_suite() -> dict:
    """Evaluate the Red Team test suite against the Blue Team service."""

    red_team_url = "http://red-team:8002/test-suite"

    try:
        response = httpx.get(red_team_url, timeout=5.0)
        response.raise_for_status()
        data = response.json()

    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=504,
            detail="Red Team service timed out.",
        ) from exc

    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not retrieve the Red Team test suite.",
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=502,
            detail="Red Team service returned invalid JSON.",
        ) from exc

    raw_payloads = data.get("payloads")

    if not isinstance(raw_payloads, list) or not raw_payloads:
        raise HTTPException(
            status_code=502,
            detail="Red Team service returned an invalid or empty test suite.",
        )

    try:
        payloads = [
            create_test_payload(
                payload_id=item["payload_id"],
                content=item["content"],
                category=AttackCategory(item["category"]),
                expected_decision=ExpectedDecision(
                    item["expected_decision"]
                ),
            )
            for item in raw_payloads
        ]

    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        raise HTTPException(
            status_code=502,
            detail="Red Team service returned an invalid payload.",
        ) from exc

    cases = create_evaluation_cases(payloads)

    return evaluate_cases(
        cases,
        audit_logger,
        detector=inspect_with_blue_team,
    )
