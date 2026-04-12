"""
Train the YOLO model on your fruit images.

How to run:
  1. Open a terminal in this project folder (Kitchen-Ingredients-Detector).
  2. Activate your venv if you use one.
  3. Run:  python train.py

The first time, it will download yolov8n.pt. When it finishes, your trained
weights are in:  models/best.pt
"""

from pathlib import Path

import shutil
from ultralytics import YOLO

# How many passes over the data (bigger = longer, often a bit better)
EPOCHS = 25

here = Path(__file__).parent
data_file = here / "fruit-detection-24" / "data.yaml"

model = YOLO("yolov8n.pt")
model.train(
    data=str(data_file),
    epochs=EPOCHS,
    imgsz=640,
    project=str(here / "runs" / "detect"),
    name="fruit",
)

# Copy best weights into models/ (that folder is already in the repo)
best_weights = here / "runs" / "detect" / "fruit" / "weights" / "best.pt"
shutil.copy2(best_weights, here / "models" / "best.pt")
print("Finished. Use models/best.pt for predictions.")
