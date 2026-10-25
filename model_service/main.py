from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(
    title="Bayora Model Service",
    description="Isolated inference service for Bayora Shield.",
    version="0.1.0",
)


class InferenceRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=10_000)


class InferenceResponse(BaseModel):
    response: str


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "Bayora Model Service",
    }


@app.post("/infer", response_model=InferenceResponse)
def infer(request: InferenceRequest) -> InferenceResponse:
    """Execute mock inference inside the isolated model service."""

    return InferenceResponse(
        response=f"Mock model response received for {len(request.prompt)} characters."
    )