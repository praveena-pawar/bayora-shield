import os

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

MODEL_SERVICE_URL = os.getenv(
    "MODEL_SERVICE_URL",
    "http://127.0.0.1:8004",
)

app = FastAPI(
    title="Bayora Model Gateway",
    description="Controlled access to the isolated model service.",
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
        "service": "Bayora Model Gateway",
    }


@app.post("/infer", response_model=InferenceResponse)
def infer(request: InferenceRequest) -> InferenceResponse:
    """Forward inference requests to the isolated model service."""

    try:
        response = httpx.post(
            f"{MODEL_SERVICE_URL.rstrip('/')}/infer",
            json={"prompt": request.prompt},
            timeout=10.0,
        )
        response.raise_for_status()

    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=504,
            detail="Model service timed out.",
        ) from exc

    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail="Model service returned an unsuccessful response.",
        ) from exc

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail="Model service is unavailable.",
        ) from exc

    try:
        result = InferenceResponse.model_validate(response.json())
    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=502,
            detail="Model service returned an invalid response.",
        ) from exc

    return result