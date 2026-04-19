# Kitchen Ingredients Detector

A full-stack computer vision app that detects fruits in kitchen photos using **YOLOv8**, annotates bounding boxes, and shows **calorie estimates** per 100 g. A **FastAPI** backend serves predictions; a **React + Vite** frontend lets users upload images and view results instantly.

---

## Features

- Detects **6 fruit classes**: apple, banana, kiwi, lemon, orange, strawberry
- Returns bounding boxes, confidence scores, and kcal/100 g per detection
- FastAPI REST API with auto-generated `/docs` (Swagger UI)
- React frontend with live bounding-box overlay
- Custom model training on a Roboflow dataset (YOLOv8n base)

---

## Project Structure

```
Kitchen-Ingredients-Detector/
├── train.py                        # Train YOLOv8 on the dataset
├── serve.py                        # Start the FastAPI server
├── requirements.txt                # Python dependencies
├── pyproject.toml                  # Package metadata (src layout)
├── models/                         # Place best.pt here (gitignored)
├── fruit-detection-24/             # Downloaded dataset (gitignored)
│   └── data.yaml
├── src/
│   └── kitchen_detector/
│       ├── app/
│       │   └── main.py             # FastAPI app (health + predict endpoints)
│       ├── inference.py            # YOLO inference logic
│       ├── schemas.py              # Pydantic models (BBox, Detection, PredictResponse)
│       ├── nutrition.py            # Static kcal/100g lookup table
│       └── download_dataset.py     # Roboflow dataset downloader
└── frontend/
    ├── src/
    │   ├── App.jsx                 # Main UI — upload, overlay, results
    │   └── main.jsx
    ├── vite.config.js
    └── package.json
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Model | PyTorch, Ultralytics YOLOv8 |
| Computer Vision | OpenCV, NumPy |
| API | FastAPI, Uvicorn, Pydantic v2 |
| Dataset | Roboflow (`fruit-detection-aubry` v24) |
| Frontend | React 18, Vite 5 |
| Packaging | setuptools (`src/` layout) |

---

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher

### 1. Clone and set up Python environment

```bash
git clone <your-repo-url>
cd Kitchen-Ingredients-Detector

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
pip install -e .
```

### 2. Download the dataset (for training only)

Get a free API key from [Roboflow](https://roboflow.com), then:

```bash
# Windows PowerShell
$env:ROBOFLOW_API_KEY="your_api_key_here"
# macOS/Linux
export ROBOFLOW_API_KEY="your_api_key_here"

python -m kitchen_detector.download_dataset
```

This creates `fruit-detection-24/` with `train/`, `valid/`, and `test/` image folders.

### 3. Train the model

```bash
python train.py
```

Training runs for 25 epochs on the downloaded dataset and automatically copies the best weights to `models/best.pt`. You can adjust `EPOCHS` in `train.py`.

> You can skip steps 2–3 by placing a pre-trained `best.pt` directly in `models/`.

### 4. Start the API

```bash
python serve.py
```

The API runs at [http://127.0.0.1:8000](http://127.0.0.1:8000).

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Check server status and whether model is loaded |
| `/predict` | POST | Upload an image and get detections |
| `/docs` | GET | Interactive Swagger UI |

You can override the model path with an environment variable:

```bash
# Windows PowerShell
$env:MODEL_PATH="path/to/custom.pt"
# macOS/Linux
export MODEL_PATH="path/to/custom.pt"
```

### 5. Start the frontend

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

The UI runs at [http://127.0.0.1:5173](http://127.0.0.1:5173) and talks to the API via the `VITE_API_URL` variable set in `frontend/.env.development`.

---

## API Usage

### `POST /predict`

Upload a JPEG or PNG image. Optionally pass a `conf` query parameter (default `0.25`) to adjust the confidence threshold.

**Request**

```bash
curl -X POST "http://127.0.0.1:8000/predict?conf=0.3" \
  -F "file=@photo.jpg"
```

**Response**

```json
{
  "detections": [
    {
      "label": "apple",
      "confidence": 0.87,
      "bbox": { "x1": 120.0, "y1": 45.0, "x2": 310.0, "y2": 260.0 },
      "calories_kcal_per_100g": 52.0
    },
    {
      "label": "banana",
      "confidence": 0.93,
      "bbox": { "x1": 400.0, "y1": 80.0, "x2": 620.0, "y2": 310.0 },
      "calories_kcal_per_100g": 89.0
    }
  ]
}
```

### `GET /health`

```json
{
  "status": "ok",
  "model_loaded": true,
  "weights_path": "C:/Users/.../models/best.pt"
}
```

---

## Calorie Reference

| Fruit | kcal / 100 g |
|---|---|
| Apple | 52 |
| Banana | 89 |
| Kiwi | 61 |
| Lemon | 29 |
| Orange | 47 |
| Strawberry | 32 |

Values are stored in `src/kitchen_detector/nutrition.py` and can be extended to match additional YOLO class names.

---

## Dataset

This project uses the [fruit-detection-aubry v24](https://universe.roboflow.com/school-qmdcx/fruit-detection-aubry/dataset/24) dataset from Roboflow, licensed under **CC BY 4.0**.

---

## Notes

- Model weights (`*.pt`) and dataset folders (`fruit-detection-*/`) are gitignored. A fresh clone requires either running the training pipeline or supplying `models/best.pt` manually.
- CORS is configured to allow requests from `localhost:5173` and `localhost:5174` (Vite dev server defaults).
