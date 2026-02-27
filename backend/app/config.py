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
TEMPLATES_DIR = BASE_DIR / "templates"

# 确保目录存在
DATA_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)

# 颜色映射文件
COLOR_MAPPING_FILE = DATA_DIR / "colorMapping.json"

# CORS 配置
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

# 服务器配置
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# 模板配置
TEMPLATES = {
    "DaMaUS": {
        "file": "加色模板.xlsm",
        "sheet": "Template",
        "columns": {
            "sku": 0,
            "product_name": 1,
            "key_features": 2,
            "generic_keyword": 3,
            "color": 4,
            "color_map": 5,
            "size": 6,
            "main_image": 7,
            "other_images": list(range(8, 15)),
            "launch_date": 15
        },
        "image_variant": "PL"
    },
    "EPUS": {
        "file": "EP-ES01840FL-加色-Coco-2.4新表.xlsm",
        "sheet": "Template",
        "columns": {
            # 基础信息 (0-based index)
            "product_type": 0,           # feed_product_type
            "seller_sku": 1,             # item_sku
            "brand_name": 2,             # brand_name
            "update_delete": 3,          # update_delete
            "product_name": 4,           # item_name
            "product_description": 7,    # product_description
            "item_type": 8,              # item_type
            "style_number": 9,           # model
            "closure_type": 10,          # closure_type
            "part_number": 12,           # part_number
            "care_instructions": 14,     # care_instructions
            "price": 15,                 # standard_price
            "quantity": 16,              # quantity
            "outer_material": 17,        # outer_material_type1
            "target_gender": 25,         # target_gender
            "age_range": 26,             # age_range_description

            # 尺码系统
            "size_system": 27,           # apparel_size_system
            "size_class": 28,            # apparel_size_class
            "size_value": 29,            # apparel_size
            "body_type": 31,             # apparel_body_type
            "height_type": 32,           # apparel_height_type

            # 图片
            "main_image": 72,            # main_image_url
            "other_image_1": 73,         # other_image_url1
            "other_image_2": 74,         # other_image_url2
            "other_image_3": 75,         # other_image_url3
            "other_image_4": 76,         # other_image_url4
            "other_image_5": 77,         # other_image_url5
            "size_chart": 78,            # other_image_url6 (尺码图)
            "swatch_image": 81,          # swatch_image_url

            # 变体关系
            "parentage": 82,             # parent_child
            "parent_sku": 83,            # parent_sku
            "relationship_type": 84,     # relationship_type
            "variation_theme": 85,       # variation_theme

            # 产品特性
            "bullet_point_1": 89,        # bullet_point1
            "bullet_point_2": 90,        # bullet_point2
            "bullet_point_3": 91,        # bullet_point3
            "bullet_point_4": 92,        # bullet_point4
            "bullet_point_5": 93,        # bullet_point5
            "generic_keyword": 94,       # generic_keyword

            # 颜色相关
            "color_map": 111,            # color_map
            "color": 135,                # color

            # 产品属性
            "occasion_type": 107,        # occasion_type
            "material_type": 117,        # material_type
            "occasion_lifestyle": 127,   # occasion_lifestyle
            "size": 152,                 # size
            "pattern": 154,              # pattern
            "neck_style": 158,           # neck_style
            "seasons": 159,              # seasons
            "apparel_silhouette": 160,   # apparel_silhouette
            "pattern_style": 161,        # pattern_style
            "embellishment_feature": 241,# embellishment_feature
            "sleeve_type": 258,          # sleeve_type
            "size_map": 298,             # size_map
            "item_length_description": 301, # item_length_description
            "waist_style": 294,          # waist_style
            "back_style": 242,           # back_style

            # 包装信息
            "package_length_unit": 368,  # package_length_unit_of_measure
            "package_weight": 369,       # package_weight

            # 材质和合规
            "fabric_type": 383,          # fabric_type
            "import_designation": 384,   # import_designation
            "dangerous_goods": 414,      # dangerous_goods_regulations

            # 价格相关
            "list_price": 512,           # list_price
            "business_price": 536,       # business_price
            "quantity_price": 539,       # quantity_price_1
            "quantity_price_2": 541,     # quantity_price_2
            "quantity_price_3": 543,     # quantity_price_3

            # Launch Date
            "launch_date": 531           # product_site_launch_date
        },
        "image_variant": "L"
    }
}
