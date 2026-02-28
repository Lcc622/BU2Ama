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
    generated_skus: Optional[List[str]] = Field(None, description="前端拼接生成的目标 SKU 列表")
    target_color: Optional[str] = Field(None, description="目标颜色代码（用于换色）")
    target_size: Optional[str] = Field(None, description="目标尺码（用于加码）")


class ProcessResponse(BaseModel):
    """Excel 处理响应模型"""
    success: bool
    output_filename: Optional[str] = None
    message: Optional[str] = None
    processed_count: int = 0


class ProcessAsyncStartResponse(BaseModel):
    """异步任务创建响应"""
    success: bool
    job_id: str
    message: str


class ProcessJobStatusResponse(BaseModel):
    """异步任务状态响应"""
    success: bool
    job_id: str
    status: str
    output_filename: Optional[str] = None
    processed_count: int = 0
    message: Optional[str] = None
    error: Optional[str] = None


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


class SKCQueryRequest(BaseModel):
    """SKC 查询请求模型"""
    skc: str = Field(..., description="SKC 字符串，格式为 7位style + 2位color，如 ES0128BDG")


class SKCSize(BaseModel):
    """SKC 尺码信息"""
    size: str
    suffix: str
    sku: str


class SKCQueryResponse(BaseModel):
    """SKC 查询响应模型"""
    success: bool
    skc: str
    new_style: str
    old_style: str
    color_code: str
    sizes: List[SKCSize]
    message: str


class SKCProcessRequest(BaseModel):
    """SKC 处理并导出请求模型"""
    skc: str = Field(..., description="SKC 字符串，格式为 7位style + 2位color，如 ES0128BDG")
    template_type: str = Field("EPUS", description="模板类型：DaMaUS / EPUS / PZUS")


class SKCProcessResponse(BaseModel):
    """SKC 处理并导出响应模型"""
    success: bool
    skc: str
    new_style: str
    old_style: str
    total_skus: int
    output_filename: Optional[str] = None
    message: str


class SKCBatchProcessRequest(BaseModel):
    """SKC 批量处理并导出请求模型"""
    skcs: List[str] = Field(..., description="SKC 列表")
    template_type: str = Field("EPUS", description="模板类型：DaMaUS / EPUS / PZUS")


class SKCBatchProcessResponse(BaseModel):
    """SKC 批量处理并导出响应模型"""
    success: bool
    total_input_skcs: int
    success_skcs: int
    failed_skcs: int
    total_skus: int
    output_filename: Optional[str] = None
    message: str
