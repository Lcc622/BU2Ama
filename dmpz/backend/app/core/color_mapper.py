"""
颜色映射管理模块
"""
import json
from typing import Dict, Optional
from pathlib import Path
from app.config import COLOR_MAPPING_FILE


class ColorMapper:
    """颜色映射管理器"""

    def __init__(self):
        self.mappings: Dict[str, str] = {}
        self.load_mappings()

    def load_mappings(self) -> None:
        """从 JSON 文件加载颜色映射"""
        if COLOR_MAPPING_FILE.exists():
            try:
                with open(COLOR_MAPPING_FILE, 'r', encoding='utf-8') as f:
                    self.mappings = json.load(f)
            except Exception as e:
                print(f"加载颜色映射失败: {e}")
                self.mappings = {}
        else:
            self.mappings = {}
            self.save_mappings()

    def save_mappings(self) -> None:
        """保存颜色映射到 JSON 文件"""
        try:
            with open(COLOR_MAPPING_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.mappings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存颜色映射失败: {e}")
            raise

    def get_all_mappings(self) -> Dict[str, str]:
        """获取所有颜色映射"""
        return self.mappings.copy()

    def search_mappings(self, keyword: str) -> Dict[str, str]:
        """搜索颜色映射"""
        keyword = keyword.upper()
        return {
            code: name
            for code, name in self.mappings.items()
            if keyword in code.upper() or keyword in name.upper()
        }

    def add_mapping(self, code: str, name: str) -> None:
        """添加或更新颜色映射"""
        code = code.upper()
        self.mappings[code] = name
        self.save_mappings()

    def add_mappings_batch(self, mappings: Dict[str, str]) -> None:
        """批量添加或更新颜色映射"""
        for code, name in mappings.items():
            self.mappings[code.upper()] = name
        self.save_mappings()

    def delete_mapping(self, code: str) -> bool:
        """删除颜色映射"""
        code = code.upper()
        if code in self.mappings:
            del self.mappings[code]
            self.save_mappings()
            return True
        return False

    def get_color_name(self, code: str) -> Optional[str]:
        """根据颜色代码获取颜色名称"""
        return self.mappings.get(code.upper())


# 全局单例
color_mapper = ColorMapper()
