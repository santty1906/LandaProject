from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
DB_PATH = DATA_DIR / "landa.db"
TEMPLATE_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

SECRET_KEY = os.getenv("LANDA_SECRET_KEY", "dev-secret-change-me")
MAX_CONTENT_LENGTH = int(os.getenv("LANDA_MAX_CONTENT_LENGTH", str(5 * 1024 * 1024)))
MIN_PASSWORD_LENGTH = int(os.getenv("LANDA_MIN_PASSWORD_LENGTH", "8"))
FACE_IMAGE_SIZE = int(os.getenv("LANDA_FACE_IMAGE_SIZE", "200"))
MIN_FACE_AREA = int(os.getenv("LANDA_MIN_FACE_AREA", "8000"))
MIN_SHARPNESS = float(os.getenv("LANDA_MIN_SHARPNESS", "40.0"))
MIN_BRIGHTNESS = float(os.getenv("LANDA_MIN_BRIGHTNESS", "45.0"))
MAX_BRIGHTNESS = float(os.getenv("LANDA_MAX_BRIGHTNESS", "235.0"))
MATCH_THRESHOLD = float(os.getenv("LANDA_MATCH_THRESHOLD", "58.0"))
FACE_POSES = ("frontal", "izquierda", "derecha")
