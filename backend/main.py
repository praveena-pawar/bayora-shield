import secrets
import threading
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from evaluator.evaluation_engine import (
    EvaluationCase,
    create_evaluation_cases,
    evaluate_cases,
)
from evaluator.security_validator import run_validation
from security.audit_logger import AuditLogger
from security.commit_reveal import (
    create_commitment,
    verify_commitment,
)
from security.prompt_detector import (
    DetectionResult,
    SecurityDecision,
    inspect_prompt,
)
from security.red_team import (
    AttackCategory,
    ExpectedDecision,
    create_test_payload,
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
            raise TypeError("Invalid reason")

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

class CommitRequest(BaseModel):
    payload: str = Field(min_length=1, max_length=10_000)


class CommitResponse(BaseModel):
    commitment_id: str
    commitment_hash: str
    status: str


class RevealRequest(BaseModel):
    commitment_id: str = Field(min_length=1)
    payload: str = Field(min_length=1, max_length=10_000)
    nonce: str = Field(min_length=1)


class RevealResponse(BaseModel):
    commitment_id: str
    valid: bool
    status: str

class BlindEvaluationResponse(BaseModel):
    commitment_id: str
    commitment_hash: str
    decision: str
    reason: str
    commitment_valid: bool
    evaluation_passed: bool



commit_reveal_lock = threading.Lock()
pending_commitments: dict[str, dict] = {}



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



@app.post(
    "/commit-reveal/commit",
    response_model=CommitResponse,
)
def commit_payload(request: CommitRequest) -> CommitResponse:
    """Commit to a payload without revealing its contents."""

    commitment = create_commitment(request.payload)
    commitment_id = secrets.token_urlsafe(16)

    with commit_reveal_lock:
        pending_commitments[commitment_id] = {
            "commitment_hash": commitment.commitment_hash,
            "nonce": commitment.nonce,
            "payload": request.payload,
        }

    audit_logger.record_event(
        decision="COMMIT",
        reason=f"Commitment created: {commitment_id}",
    )

    return CommitResponse(
        commitment_id=commitment_id,
        commitment_hash=commitment.commitment_hash,
        status="committed",
    )


@app.post(
    "/commit-reveal/verify",
    response_model=RevealResponse,
)
def reveal_payload(request: RevealRequest) -> RevealResponse:
    """Verify a revealed payload against its stored commitment."""

    with commit_reveal_lock:
        stored = pending_commitments.get(request.commitment_id)

        if stored is None:
            raise HTTPException(
                status_code=404,
                detail="Commitment not found or already revealed.",
            )

        valid = (
            request.payload == stored["payload"]
            and verify_commitment(
                request.payload,
                request.nonce,
                stored["commitment_hash"],
            )
            and request.nonce == stored["nonce"]
        )

        del pending_commitments[request.commitment_id]

    audit_logger.record_event(
        decision="REVEAL_VALID" if valid else "REVEAL_INVALID",
        reason=f"Commitment verification: {request.commitment_id}",
    )

    return RevealResponse(
        commitment_id=request.commitment_id,
        valid=valid,
        status="verified" if valid else "verification_failed",
    )





@app.post("/commit-reveal/run-evaluation")
def run_commit_reveal_evaluation(
    commitment_id: str,
) -> dict:
    """Evaluate a committed payload before it is revealed."""

    with commit_reveal_lock:
        stored = pending_commitments.get(commitment_id)

        if stored is None:
            raise HTTPException(
                status_code=404,
                detail="Commitment not found or already revealed.",
            )

        if stored.get("evaluation_in_progress", False):
            raise HTTPException(
                status_code=409,
                detail="Cannot reveal while evaluation is in progress.",
            )

        if (
            stored.get("evaluation") is not None
            or stored.get("evaluation_in_progress", False)
        ):
            raise HTTPException(
                status_code=409,
                detail="This commitment has already been evaluated or is being evaluated.",
            )

        # Reserve this commitment to prevent concurrent evaluations.
        stored["evaluation_in_progress"] = True
        payload = stored["payload"]

    try:
        # Do not hold the lock during the network request.
        result = inspect_with_blue_team(payload)

    except Exception:
        # Allow a retry if the evaluation fails.
        with commit_reveal_lock:
            stored = pending_commitments.get(commitment_id)
            if stored is not None:
                stored["evaluation_in_progress"] = False
        raise

    with commit_reveal_lock:
        stored = pending_commitments.get(commitment_id)

        if stored is None:
            raise HTTPException(
                status_code=409,
                detail="Commitment state changed during evaluation.",
            )

        stored["evaluation"] = {
            "decision": result.decision.value,
            "reason": result.reason,
        }
        stored["evaluation_in_progress"] = False

    audit_logger.record_event(
        decision="BLIND_EVALUATION",
        reason=(
            f"Commitment {commitment_id} evaluated; "
            f"decision={result.decision.value}"
        ),
    )

    return {
        "commitment_id": commitment_id,
        "status": "evaluated",
        "decision": result.decision.value,
    }



@app.post(
    "/commit-reveal/evaluate",
    response_model=BlindEvaluationResponse,
)
def evaluate_committed_payload(
    request: RevealRequest,
) -> BlindEvaluationResponse:
    """Verify a reveal and return the previously stored evaluation."""

    with commit_reveal_lock:
        stored = pending_commitments.get(request.commitment_id)

        if stored is None:
            raise HTTPException(
                status_code=404,
                detail="Commitment not found or already revealed.",
            )

        if stored.get("evaluation") is None:
            raise HTTPException(
                status_code=409,
                detail="Commitment must be evaluated before reveal.",
            )

        if (
            request.payload != stored["payload"]
            or request.nonce != stored["nonce"]
        ):
            raise HTTPException(
                status_code=400,
                detail="Reveal does not match the committed payload.",
            )

        commitment_valid = verify_commitment(
            request.payload,
            request.nonce,
            stored["commitment_hash"],
        )

        if not commitment_valid:
            raise HTTPException(
                status_code=400,
                detail="Commitment verification failed.",
            )

        evaluation = stored["evaluation"]
        commitment_hash = stored["commitment_hash"]

        # Consume the commitment only after successful verification.
        del pending_commitments[request.commitment_id]

    audit_logger.record_event(
        decision="REVEAL_VALID",
        reason=f"Commitment {request.commitment_id} verified after evaluation",
    )

    return BlindEvaluationResponse(
        commitment_id=request.commitment_id,
        commitment_hash=commitment_hash,
        decision=evaluation["decision"],
        reason=evaluation["reason"],
        commitment_valid=True,
        evaluation_passed=True,
    )
