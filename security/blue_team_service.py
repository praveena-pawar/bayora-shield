
from fastapi import FastAPI
from pydantic import BaseModel, Field

from security.prompt_detector import inspect_prompt


app = FastAPI(
    title="Bayora Blue Team Service",
    description="Defensive prompt inspection service for controlled security evaluation.",
    version="0.1.0",
)


class DefenseRequest(BaseModel):
    prompt: str = Field(max_length=10_000)


class DefenseResponse(BaseModel):
    decision: str
    reason: str


@app.get("/health")
def health_check() -> dict[str, str]:
    """Report Blue Team service health."""
    return {
        "status": "healthy",
        "service": "Bayora Blue Team",
    }


@app.post("/defend", response_model=DefenseResponse)
def defend_prompt(request: DefenseRequest) -> DefenseResponse:
    """Inspect a prompt using the configured defensive rules."""
    result = inspect_prompt(request.prompt)

    return DefenseResponse(
        decision=result.decision.value,
        reason=result.reason,
    )
