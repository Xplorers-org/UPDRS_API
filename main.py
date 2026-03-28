from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from routers import analyze_router
from ml.model_predictor import _download_and_cache

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once when the Space starts — downloads + caches all 3 models
    print("Startup: downloading models from HF Hub...")
    _download_and_cache()
    print("Startup complete. API is ready.")
    yield
    # Shutdown cleanup (optional)
    print("Shutting down.")

app = FastAPI(
    title="Parkinson's disease prediction API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router.router)

@app.get("/")
def read_root():
    return {"message": "Parkinson's disease prediction API"}

@app.get("/health")
def health():
    from ml.model_predictor import _cache
    return {
        "status": "ok",
        "models_loaded": bool(_cache)
    }