from fastapi import FastAPI

app = FastAPI(
    title="Landa Backend API",
    description="Setup scaffold only. Business logic pending.",
    version="0.1.0",
)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
