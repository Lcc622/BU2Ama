"""
配置管理模块
"""
import os
from pathlib import Path

# 项目根目录（backend/app/config.py -> backend/）
BASE_DIR = Path(__file__).resolve().parent.parent

# 数据目录
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = BASE_DIR / "uploads"
RESULTS_DIR = BASE_DIR / "results"

# 确保目录存在
DATA_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

# 颜色映射文件
COLOR_MAPPING_FILE = DATA_DIR / "colorMapping.json"

# CORS 配置
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

# 服务器配置
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# 模板配置：每个店铺使用各自的输出模板
TEMPLATES = {
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
STORE_CONFIGS = {
    "DaMaUS": {
        "prefix": "DA",
        "source_files": ["DA-0.xlsm", "DA-1.xlsm", "DA-2.xlsm"],
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
