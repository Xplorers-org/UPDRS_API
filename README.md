---
title: UPDRS API
emoji: 🧠
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# Parkinson's Disease Motor UPDRS Prediction API

A production-style FastAPI service that predicts **motor UPDRS score** from a voice sample and patient metadata.

The service:

- accepts audio uploads (`wav`, `mp3`, `ogg`, `webm`),
- converts them to WAV when needed,
- extracts clinical voice biomarkers using Praat,
- loads a trained ensemble model from Hugging Face,
- returns a numeric UPDRS motor prediction.

---

## 1) What this API does

Given:

- `age`
- `sex` (`male` or `female`)
- `test_time`
- `audio_file`

The API returns:

- `prediction` (float): estimated motor UPDRS score.

---

## 2) Project structure

```text
UPDRS_API/
├── main.py
├── requirements.txt
├── Dockerfile
├── README.md
├── routers/
│   └── analyze_router.py
├── services/
│   └── voice_analyze_service.py
├── ml/
│   └── model_predictor.py
├── utils/
│   ├── file_handler.py
│   └── voice_data_extraction.py
└── schema/
    └── patient_inputs.py
```

### Responsibilities

- **main.py**: app startup, CORS, lifespan hook, route registration.
- **routers/analyze_router.py**: request validation and endpoint definitions.
- **services/voice_analyze_service.py**: end-to-end orchestration.
- **utils/file_handler.py**: upload persistence + ffmpeg conversion.
- **utils/voice_data_extraction.py**: Praat/parselmouth feature extraction.
- **ml/model_predictor.py**: model download/cache and inference.

---

## 3) API endpoints

| Method | Path             | Purpose                                      |
| ------ | ---------------- | -------------------------------------------- |
| GET    | `/`              | Basic welcome/status message                 |
| GET    | `/health`        | Health + model cache state                   |
| POST   | `/analyze/test`  | Echo/debug endpoint for multipart form input |
| POST   | `/analyze/voice` | Main prediction endpoint                     |

### `GET /health` response

```json
{
  "status": "ok",
  "models_loaded": true
}
```

---

## 4) Main prediction endpoint

### `POST /analyze/voice`

Content type: `multipart/form-data`

| Field        | Type   | Validation         |
| ------------ | ------ | ------------------ |
| `age`        | int    | `10 < age < 120`   |
| `sex`        | string | `male` or `female` |
| `test_time`  | float  | `> 0`              |
| `audio_file` | file   | required           |

### Example response

```json
{
  "prediction": 18.42
}
```

---

## 5) How prediction works (pipeline)

1. Request arrives at `POST /analyze/voice`.
2. Audio file is written to a temp file.
3. Non-WAV formats are converted to WAV via `ffmpeg`.
4. Praat/parselmouth extracts acoustic and nonlinear features.
5. `sex` is encoded (`male=1`, `female=0`).
6. Features are combined with `age` and `test_time`.
7. Features are ordered/scaled according to `feature_names.pkl` and `scaler.pkl`.
8. Ensemble model predicts UPDRS.
9. Temp file is always cleaned up.

---

## 6) Extracted voice features

The service extracts these features:

- **Jitter**
  - `Jitter(%)`
  - `Jitter(Abs)`
  - `Jitter:RAP`
  - `Jitter:PPQ5`
  - `Jitter:DDP`

- **Shimmer**
  - `Shimmer`
  - `Shimmer(dB)`
  - `Shimmer:APQ3`
  - `Shimmer:APQ5`
  - `Shimmer:APQ11`
  - `Shimmer:DDA`

- **Noise/Harmonics**
  - `NHR`
  - `HNR`

- **Nonlinear dynamics**
  - `RPDE`
  - `DFA`
  - `PPE`

---

## 7) Model details

- Model repo: https://huggingface.co/xplorers/parkinsons-updrs-model
- Artifacts downloaded on startup:
  - `ensemble_model.pkl`
  - `feature_names.pkl`
  - `scaler.pkl`
- Models are cached in-memory (`_cache`) after first load.

---

## 8) Environment variables

Create a `.env` file in the project root (optional but recommended):

```env
HF_TOKEN=your_huggingface_access_token
```

`main.py` calls `load_dotenv()`, so `.env` is loaded automatically.

---

## 9) Local development setup

### Prerequisites

- Python 3.11+ (recommended for this codebase)
- `ffmpeg` installed and available in PATH

### Install

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Open:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

---

## 10) Docker usage

Build image:

```bash
docker build -t updrs-api .
```

Run container:

```bash
docker run --rm -p 7860:7860 --env HF_TOKEN=$HF_TOKEN updrs-api
```

Container entrypoint uses:

```bash
uvicorn main:app --host 0.0.0.0 --port 7860
```

---

## 11) cURL examples

### Health check

```bash
curl http://127.0.0.1:8000/health
```

### Voice prediction

```bash
curl -X POST "http://127.0.0.1:8000/analyze/voice" \
  -F "age=63" \
  -F "sex=male" \
  -F "test_time=12.5" \
  -F "audio_file=@./sample.wav"
```

---

## 12) Error handling and troubleshooting

### 401 Unauthorized from Hugging Face

Cause: gated/private model repository.

Fix:

1. Ensure your account has access to the model page.
2. Set `HF_TOKEN` in environment or `.env`.
3. Restart the API.

### `ffmpeg` conversion failure

Cause: `ffmpeg` missing or unsupported input file.

Fix:

- Install `ffmpeg` (system package).
- Test source file manually with `ffmpeg -i <file>`.

### Models not loaded

`predict_parkinson()` raises runtime error if startup download failed.

Fix:

- Check server startup logs.
- Verify internet access and token permissions.

---

## 13) License

This project includes a `LICENSE` file at the repository root. Review it before distribution or production use.
