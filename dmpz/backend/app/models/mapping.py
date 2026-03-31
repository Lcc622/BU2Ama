"""
Pydantic 数据模型 - 颜色映射
"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ColorMapping(BaseModel):
    """颜色映射模型"""
    code: str = Field(..., description="颜色代码（2个大写字母）", min_length=2, max_length=2)
    name: str = Field(..., description="颜色名称")


class ColorMappingBatch(BaseModel):
    """批量颜色映射模型"""
    mappings: List[ColorMapping]


class ColorMappingResponse(BaseModel):
    """颜色映射响应模型"""
    success: bool
    data: Optional[Dict[str, str]] = None
    message: Optional[str] = None


class ColorMappingSearchResponse(BaseModel):
    """颜色映射搜索响应模型"""
    success: bool
    data: Optional[Dict[str, str]] = None
    count: int = 0
