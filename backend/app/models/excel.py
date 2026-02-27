"""
Pydantic 数据模型 - Excel 处理
"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class SKUInfo(BaseModel):
    """SKU 信息模型"""
    sku: str
    product_code: str
    color_code: str
    size: str
    suffix: str


class ColorDistribution(BaseModel):
    """颜色分布模型"""
    color_code: str
    color_name: Optional[str] = None
    count: int


class AnalysisResult(BaseModel):
    """Excel 分析结果模型"""
    success: bool
    filename: str
    total_skus: int
    unique_colors: int
    color_distribution: List[ColorDistribution]
    unknown_colors: List[str]
    prefixes: List[str]
    suffixes: List[str]


class ProcessRequest(BaseModel):
    """Excel 处理请求模型"""
    template_type: str = Field(..., description="模板类型：DaMaUS 或 EPUS")
    filenames: List[str] = Field(..., description="要处理的文件名列表")
    selected_prefixes: List[str] = Field(..., description="选中的 SKU 前缀列表")
    target_color: Optional[str] = Field(None, description="目标颜色代码（用于换色）")
    target_size: Optional[str] = Field(None, description="目标尺码（用于加码）")


class ProcessResponse(BaseModel):
    """Excel 处理响应模型"""
    success: bool
    output_filename: Optional[str] = None
    message: Optional[str] = None
    processed_count: int = 0


class TemplateInfo(BaseModel):
    """模板信息模型"""
    name: str
    file: str
    exists: bool


class FileInfo(BaseModel):
    """文件信息模型"""
    filename: str
    size: int
    upload_time: str
