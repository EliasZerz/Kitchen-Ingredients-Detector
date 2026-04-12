"""FastAPI app: health check and image upload → detections + kcal per 100g."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from ultralytics import YOLO

from kitchen_detector.inference import decode_image_bgr, default_weights_path, predict_image
from kitchen_detector.schemas import PredictResponse

_model: YOLO | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _model
    path = default_weights_path()
    if path.is_file():
        _model = YOLO(str(path))
    else:
        _model = None
    yield
    _model = None


app = FastAPI(title="Kitchen Ingredients Detector", lifespan=lifespan)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": _model is not None,
        "weights_path": str(default_weights_path()),
    }


@app.post("/predict", response_model=PredictResponse)
async def predict(
    file: Annotated[UploadFile, File(description="Image (JPEG/PNG)")],
    conf: Annotated[float, Query(ge=0.0, le=1.0)] = 0.25,
):
    if _model is None:
        raise HTTPException(
            status_code=503,
            detail=f"No weights at {default_weights_path()}. Train and copy best.pt or set MODEL_PATH.",
        )
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file.")
    img = decode_image_bgr(data)
    if img is None:
        raise HTTPException(status_code=400, detail="Could not decode image. Use JPEG or PNG.")

    return predict_image(_model, img, conf=conf)
