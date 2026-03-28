import joblib
import os
import numpy as np
import pandas as pd
from huggingface_hub import hf_hub_download

MODEL_REPO = "xplorers/parkinsons-updrs-model"
MODEL_DIR  = "/tmp/models"

# In-memory cache — models are loaded once at startup, reused for every request
_cache = {}

def _download_and_cache():
    """Download models from HF Hub and cache in memory. Runs once at startup."""
    if _cache:
        return  # already loaded

    os.makedirs(MODEL_DIR, exist_ok=True)

    filenames = ["ensemble_model.pkl", "feature_names.pkl", "scaler.pkl"]
    for filename in filenames:
        hf_hub_download(
            repo_id=MODEL_REPO,
            filename=filename,
            repo_type="model",
            local_dir=MODEL_DIR,
            token=os.getenv("HF_TOKEN"),  # needed if your HF model repo is private
        )

    _cache["model"]         = joblib.load(os.path.join(MODEL_DIR, "ensemble_model.pkl"))
    _cache["feature_names"] = joblib.load(os.path.join(MODEL_DIR, "feature_names.pkl"))
    _cache["scaler"]        = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))
    print("Models loaded into memory from HF Hub.")


def predict_parkinson(features: dict) -> float:
    """
    Predict Parkinson's motor UPDRS score from patient features.
    Uses cached models — no disk read on each request.
    """
    try:
        model         = _cache["model"]
        feature_names = _cache["feature_names"]
        scaler        = _cache["scaler"]

        print(f"Expected features: {feature_names}")
        print(f"Received features: {list(features.keys())}")

        missing_features = [name for name in feature_names if name not in features]
        if missing_features:
            raise ValueError(f"Missing required features: {missing_features}")

        for name in feature_names:
            value = features[name]
            if pd.isna(value) or np.isinf(value):
                print(f"Warning: Feature '{name}' has invalid value: {value}, replacing with 0.0")
                features[name] = 0.0

        input_values = [features[name] for name in feature_names]
        input_df     = pd.DataFrame([input_values], columns=feature_names)

        scaled_features  = scaler.transform(input_df)
        updrs_prediction = model.predict(scaled_features)[0]

        return float(updrs_prediction)

    except KeyError:
        raise RuntimeError("Models not loaded. Ensure startup lifespan ran successfully.")
    except Exception as e:
        raise Exception(f"Prediction error: {e}")


def get_required_features():
    try:
        return list(_cache["feature_names"])
    except KeyError:
        return [
            'age', 'sex', 'test_time', 'Jitter(%)', 'Jitter(Abs)', 'Jitter:RAP',
            'Jitter:PPQ5', 'Jitter:DDP', 'Shimmer', 'Shimmer(dB)', 'Shimmer:APQ3',
            'Shimmer:APQ5', 'Shimmer:APQ11', 'Shimmer:DDA', 'NHR', 'HNR',
            'RPDE', 'DFA', 'PPE'
        ]