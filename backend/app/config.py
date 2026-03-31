"""
配置管理模块
"""
import os
from pathlib import Path
from typing import Dict, Tuple

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

# 确保目录存在
DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# 颜色映射文件
COLOR_MAPPING_FILE = DATA_DIR / "colorMapping.json"

ADD_COLOR_TEMPLATE_FILE = "加色模板.xlsx"

# CORS 配置
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

# 服务器配置
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# 模板配置：每个店铺使用各自的输出模板
_ALL_TEMPLATES = {
    "DaMaUS": {
        "image_variant": "PL",  # 使用 -PL1.jpg, -PL2.jpg 等
        "template_file": "DAMA输出模板.xlsm"  # DAMA 店铺专用模板
    },
    "EPUS": {
        "image_variant": "L",   # 使用 -L1.jpg, -L2.jpg 等
        "template_file": "EP输出模板.xlsm"  # EP 店铺专用模板
    },
    "PZUS": {
        "image_variant": "PL",  # 使用 -PL1.jpg, -PL2.jpg 等
        "template_file": "PZ输出模板.xlsm"  # PZ 店铺专用模板
    }
}

# 店铺数据文件配置（跟卖按模板类型路由到对应店铺源数据）
_ALL_STORE_CONFIGS = {
    "DaMaUS": {
        "prefix": "DA",
        "source_files": ["DA-0.xlsm"],
        "listing_report": "DM-All+Listings+Report.txt",
    },
    "EPUS": {
        "prefix": "EP",
        "source_files": ["EP-0.xlsm", "EP-1.xlsm", "EP-2.xlsm"],
        "listing_report": "EP-All+Listings+Report.txt",
    },
    "PZUS": {
        "prefix": "PZ",
        "source_files": ["PZ-0.xlsm", "PZ-1.xlsm", "PZ-2.xlsm"],
        "listing_report": "PZ-All+Listings+Report.txt",
    },
}

STORE_GROUP = str(os.getenv("STORE_GROUP", "")).strip().upper() or None
STORE_GROUP_TEMPLATES: Dict[str, Tuple[str, ...]] = {
    "EP": ("EPUS",),
    "DM_PZ": ("DaMaUS", "PZUS"),
}

if STORE_GROUP and STORE_GROUP not in STORE_GROUP_TEMPLATES:
    allowed_groups = ", ".join(sorted(STORE_GROUP_TEMPLATES))
    raise ValueError(f"无效的 STORE_GROUP={STORE_GROUP}，允许值: {allowed_groups}")

_ALLOWED_TEMPLATE_TYPES = STORE_GROUP_TEMPLATES.get(STORE_GROUP, tuple(_ALL_STORE_CONFIGS.keys()))

TEMPLATES = {
    name: _ALL_TEMPLATES[name]
    for name in _ALLOWED_TEMPLATE_TYPES
}

STORE_CONFIGS = {
    name: _ALL_STORE_CONFIGS[name]
    for name in _ALLOWED_TEMPLATE_TYPES
}

TEMPLATE_TO_STORE_PREFIX = {
    "DaMaUS": "DM",
    "EPUS": "EP",
    "PZUS": "PZ",
}
ALLOWED_TEMPLATE_TYPES = tuple(STORE_CONFIGS.keys())
ALLOWED_STORE_PREFIXES = tuple(TEMPLATE_TO_STORE_PREFIX[name] for name in ALLOWED_TEMPLATE_TYPES)
DEFAULT_TEMPLATE_TYPE = "EPUS" if "EPUS" in STORE_CONFIGS else (ALLOWED_TEMPLATE_TYPES[0] if ALLOWED_TEMPLATE_TYPES else "EPUS")

# 历史记录 DB 路径：按店铺隔离，避免 EP 和 DM/PZ 记录混在一起
HISTORY_DB_PATH = UPLOADS_DIR / f"export_history_{STORE_GROUP or 'ALL'}.db"
