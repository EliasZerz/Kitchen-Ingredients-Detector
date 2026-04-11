"""FastAPI application entrypoint (inference wiring added later)."""

from fastapi import FastAPI

app = FastAPI(title="Kitchen Ingredients Detector")


@app.get("/health")
def health():
    return {"status": "ok"}
