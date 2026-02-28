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

# 确保目录存在
DATA_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)

# 颜色映射文件
COLOR_MAPPING_FILE = DATA_DIR / "colorMapping.json"

# CORS 配置
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

# 服务器配置
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# 模板配置：DaMaUS 和 EPUS 只有图片 URL 格式不同
TEMPLATES = {
    "DaMaUS": {
        "image_variant": "PL",  # 使用 -PL1.jpg, -PL2.jpg 等
        "template_file": "EP-ES0128BDG02-补码-Tammy-2.25模版.xlsm"  # 固定的模板文件
    },
    "EPUS": {
        "image_variant": "L",   # 使用 -L1.jpg, -L2.jpg 等
        "template_file": "EP-ES0128BDG02-补码-Tammy-2.25模版.xlsm"  # 固定的模板文件
    },
    "PZUS": {
        "image_variant": "PL",  # 使用 -PL1.jpg, -PL2.jpg 等
        "template_file": "EP-ES0128BDG02-补码-Tammy-2.25模版.xlsm"  # 固定的模板文件
    }
}
