"""
配置管理模块
"""
import os
import shutil
from pathlib import Path

# 项目根目录（backend/app/config.py -> backend/）
BASE_DIR = Path(__file__).resolve().parent.parent


def _resolve_dir_path(env_name: str, default_path: Path) -> Path:
    raw_value = str(os.getenv(env_name, "")).strip()
    if not raw_value:
        return default_path
    path = Path(raw_value).expanduser()
    if not path.is_absolute():
        path = BASE_DIR / path
    return path


# 数据目录
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = _resolve_dir_path("UPLOADS_DIR", BASE_DIR / "uploads")
RESULTS_DIR = _resolve_dir_path("RESULTS_DIR", BASE_DIR / "results")
SEED_UPLOADS_DIR = BASE_DIR / "seed_uploads"

# 确保目录存在
DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# 颜色映射文件
COLOR_MAPPING_FILE = DATA_DIR / "colorMapping.json"

# CORS 配置
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

# 服务器配置
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

TEMPLATES = {
    "DaMaUS": {
        "image_variant": "PL",
        "template_file": "DAMA输出模板.xlsm",
        "follow_sell_template_file": "DAMA跟卖模板.xlsm",
    },
    "PZUS": {
        "image_variant": "PL",
        "template_file": "PZ输出模板.xlsm",
    },
}

STORE_CONFIGS = {
    "DaMaUS": {
        "prefix": "DA",
        "source_files": ["DA-0.xlsm"],
        "listing_report": "DM-All+Listings+Report.txt",
    },
    "PZUS": {
        "prefix": "PZ",
        "source_files": ["PZ-0.xlsm", "PZ-1.xlsm"],
        "listing_report": "PZ-All+Listings+Report.txt",
    },
}

DEFAULT_TEMPLATE_TYPE = "DaMaUS"
ALLOWED_TEMPLATE_TYPES = ("DaMaUS", "PZUS")
ALLOWED_STORE_PREFIXES = ("DM", "PZ")
TEMPLATE_TO_STORE_PREFIX = {"DaMaUS": "DM", "PZUS": "PZ"}
HISTORY_DB_PATH = UPLOADS_DIR / "export_history.db"


def ensure_seed_uploads() -> list[str]:
    if not SEED_UPLOADS_DIR.exists():
        return []

    copied_files: list[str] = []
    for seed_path in SEED_UPLOADS_DIR.iterdir():
        if not seed_path.is_file():
            continue
        target_path = UPLOADS_DIR / seed_path.name
        if target_path.exists():
            continue
        shutil.copy2(seed_path, target_path)
        copied_files.append(seed_path.name)
    return copied_files
