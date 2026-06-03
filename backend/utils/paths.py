from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_DIR.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"

DATA_DIR = BACKEND_DIR / "data"
GESTURES_DIR = DATA_DIR / "gestures"
DATASETS_DIR = DATA_DIR / "datasets"
DATABASE_DIR = DATA_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "gesture_db.db"

MODELS_DIR = BACKEND_DIR / "models"
MODEL_PATH = MODELS_DIR / "cnn_model_keras2.h5"

ARTIFACTS_DIR = BACKEND_DIR / "artifacts"
HISTOGRAM_PATH = ARTIFACTS_DIR / "hist"


def ensure_directories():
    for directory in (
        GESTURES_DIR,
        DATASETS_DIR,
        DATABASE_DIR,
        MODELS_DIR,
        ARTIFACTS_DIR,
    ):
        directory.mkdir(parents=True, exist_ok=True)
