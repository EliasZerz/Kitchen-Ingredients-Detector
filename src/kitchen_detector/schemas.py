from pydantic import BaseModel, Field


class BBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


class Detection(BaseModel):
    label: str
    confidence: float = Field(ge=0.0, le=1.0)
    bbox: BBox
    calories_kcal_per_100g: float | None = None


class PredictResponse(BaseModel):
    detections: list[Detection]
