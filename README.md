---
title: UPDRS API
emoji: 🧠
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# Parkinson's Disease UPDRS Prediction API

A FastAPI-based REST API that predicts a patient's **motor UPDRS score** (Unified Parkinson's Disease Rating Scale) from a voice recording.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Root welcome message |
| `GET` | `/health` | Health check — confirms models are loaded |
| `POST` | `/analyze/voice` | Main prediction endpoint |
| `POST` | `/analyze/test` | Debug echo endpoint |

## Usage — `/analyze/voice`

Submit a `multipart/form-data` POST request with:

| Field | Type | Description |
|-------|------|-------------|
| `age` | int | Age (11–119) |
| `sex` | string | `male` or `female` |
| `test_time` | float | Time since recruitment (days) |
| `audio_file` | file | Voice recording (WAV, MP3, OGG, WebM) |

### Response

```json
{
  "prediction": 18.42
}
```

`prediction` is the estimated motor UPDRS score (float).

## Voice Features Extracted

The API uses **Praat** (via `parselmouth`) to extract 16 acoustic biomarkers:
- **Jitter**: `Jitter(%)`, `Jitter(Abs)`, `Jitter:RAP`, `Jitter:PPQ5`, `Jitter:DDP`
- **Shimmer**: `Shimmer`, `Shimmer(dB)`, `Shimmer:APQ3`, `Shimmer:APQ5`, `Shimmer:APQ11`, `Shimmer:DDA`
- **Noise**: `NHR`, `HNR`
- **Nonlinear**: `RPDE`, `DFA`, `PPE`

## Model

- Hosted on HuggingFace: [`xplorers/parkinsons-updrs-model`](https://huggingface.co/xplorers/parkinsons-updrs-model)
- Ensemble model (RandomForest + XGBoost + LightGBM via VotingRegressor)
- Downloaded and cached in memory at startup
