"""
颜色映射 API 路由
"""
from fastapi import APIRouter, HTTPException
from typing import Dict

from app.core.color_mapper import color_mapper
from app.models.mapping import (
    ColorMapping,
    ColorMappingBatch,
    ColorMappingResponse,
    ColorMappingSearchResponse
)

router = APIRouter(prefix="/api/mapping", tags=["颜色映射"])


@router.get("", response_model=ColorMappingResponse)
async def get_all_mappings():
    """获取所有颜色映射"""
    try:
        mappings = color_mapper.get_all_mappings()
        return ColorMappingResponse(
            success=True,
            data=mappings
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=ColorMappingSearchResponse)
async def search_mappings(keyword: str):
    """搜索颜色映射"""
    try:
        mappings = color_mapper.search_mappings(keyword)
        return ColorMappingSearchResponse(
            success=True,
            data=mappings,
            count=len(mappings)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=ColorMappingResponse)
async def add_mapping(data: ColorMapping | ColorMappingBatch | Dict[str, str]):
    """添加或更新颜色映射（支持单个或批量）"""
    try:
        if isinstance(data, ColorMapping):
            # 单个映射
            color_mapper.add_mapping(data.code, data.name)
        elif isinstance(data, ColorMappingBatch):
            # 批量映射（使用 Pydantic 模型）
            mappings_dict = {m.code: m.name for m in data.mappings}
            color_mapper.add_mappings_batch(mappings_dict)
        elif isinstance(data, dict):
            # 批量映射（直接传字典）
            color_mapper.add_mappings_batch(data)
        else:
            raise HTTPException(status_code=400, detail="无效的请求格式")

        return ColorMappingResponse(
            success=True,
            message="颜色映射已保存"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{code}", response_model=ColorMappingResponse)
async def delete_mapping(code: str):
    """删除颜色映射"""
    try:
        success = color_mapper.delete_mapping(code)
        if success:
            return ColorMappingResponse(
                success=True,
                message=f"颜色映射 {code} 已删除"
            )
        else:
            raise HTTPException(status_code=404, detail=f"颜色代码 {code} 不存在")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
