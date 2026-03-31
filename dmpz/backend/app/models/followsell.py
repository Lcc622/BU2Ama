"""
跟卖上新数据模型
"""

from pydantic import BaseModel, Field


class FollowSellRequest(BaseModel):
    """跟卖处理请求"""
    new_product_code: str = Field(
        ...,
        min_length=7,
        max_length=8,
        description="新产品代码，如 ES01846"
    )


class FollowSellResponse(BaseModel):
    """跟卖处理响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    data: dict | None = Field(None, description="处理结果数据")


class FollowSellResult(BaseModel):
    """跟卖处理结果"""
    total_skus: int = Field(..., description="处理的 SKU 总数")
    old_product_code: str = Field(..., description="识别的老产品代码")
    new_product_code: str = Field(..., description="新产品代码")
    output_filename: str = Field(..., description="生成的文件名")
    output_path: str = Field(..., description="生成的文件路径")
    price_adjustment: float = Field(..., description="价格调整")
    date_used: str = Field(..., description="使用的日期")
