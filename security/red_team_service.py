from fastapi import FastAPI
from pydantic import BaseModel, Field

from security.red_team import create_test_payload

app = FastAPI(
    title="Bayora Red Team Service",
    description="Creates controlled security-testing payloads.",
    version="0.1.0",
)


class PayloadRequest(BaseModel):
    payload_id: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1, max_length=10_000)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "Bayora Red Team",
    }


@app.post("/payloads")
def create_payload(request: PayloadRequest) -> dict[str, str]:
    payload = create_test_payload(
        payload_id=request.payload_id,
        content=request.content,
    )

    return {
        "payload_id": payload.payload_id,
        "content": payload.content,
    }