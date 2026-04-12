"""Run YOLO on a BGR image and build API response models."""

from __future__ import annotations

import os
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO

from kitchen_detector.nutrition import KCAL_PER_100G
from kitchen_detector.schemas import BBox, Detection, PredictResponse


def repo_root() -> Path:
    """Project root (folder containing models/, train.py)."""
    return Path(__file__).resolve().parents[2]


def default_weights_path() -> Path:
    raw = os.environ.get("MODEL_PATH")
    if raw:
        p = Path(raw).expanduser()
        return p if p.is_absolute() else repo_root() / p
    return repo_root() / "models" / "best.pt"


def decode_image_bgr(data: bytes) -> np.ndarray | None:
    arr = np.frombuffer(data, dtype=np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_COLOR)


def predict_image(model: YOLO, image_bgr: np.ndarray, conf: float = 0.25) -> PredictResponse:
    results = model.predict(image_bgr, conf=conf, verbose=False)
    if not results:
        return PredictResponse(detections=[])

    r = results[0]
    detections: list[Detection] = []
    if r.boxes is None or len(r.boxes) == 0:
        return PredictResponse(detections=[])

    names = r.names
    for box in r.boxes:
        xyxy = box.xyxy[0].tolist()
        x1, y1, x2, y2 = (float(xyxy[0]), float(xyxy[1]), float(xyxy[2]), float(xyxy[3]))
        c = float(box.conf[0].item())
        cid = int(box.cls[0].item())
        label = names[cid]
        kcal = KCAL_PER_100G.get(label)
        detections.append(
            Detection(
                label=label,
                confidence=c,
                bbox=BBox(x1=x1, y1=y1, x2=x2, y2=y2),
                calories_kcal_per_100g=kcal,
            )
        )

    return PredictResponse(detections=detections)
