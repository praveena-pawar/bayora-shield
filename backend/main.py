from fastapi import FastAPI

app = FastAPI(
    title="Bayora Shield",
    description=(
        "An isolated AI security testing platform "
        "for adversarial evaluation and audit integrity."
    ),
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Report the API service health."""
    return {
        "status": "healthy",
        "service": "Bayora Shield",
    }