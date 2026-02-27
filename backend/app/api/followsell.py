"""
跟卖上新 API 路由
"""

import logging
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse

from app.core.followsell_processor import FollowSellProcessor
from app.models.followsell import FollowSellResponse
from app.config import UPLOADS_DIR

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/followsell", tags=["followsell"])


@router.post("/process", response_model=FollowSellResponse)
async def process_followsell(
    file: UploadFile = File(..., description="老版本 Excel 文件"),
    new_product_code: str = Form(..., description="新产品代码，如 ES01846")
):
    """
    处理跟卖上新

    上传老版本 Excel 文件，输入新产品代码，生成新版本 Excel 文件。

    Args:
        file: 老版本 Excel 文件（.xlsm 或 .xlsx）
        new_product_code: 新产品代码（7-8位字符）

    Returns:
        处理结果，包含生成的文件信息
    """
    logger.info(f"收到跟卖处理请求: filename={file.filename}, new_code={new_product_code}")

    # 验证文件格式
    if not file.filename.endswith(('.xlsx', '.xlsm', '.xls')):
        raise HTTPException(
            status_code=400,
            detail="不支持的文件格式，请上传 .xlsx、.xlsm 或 .xls 文件"
        )

    # 验证产品代码格式
    if len(new_product_code) < 7 or len(new_product_code) > 8:
        raise HTTPException(
            status_code=400,
            detail="产品代码长度必须为 7-8 位字符"
        )

    try:
        # 保存上传的文件
        upload_path = UPLOADS_DIR / file.filename
        with open(upload_path, "wb") as f:
            content = await file.read()
            f.write(content)

        logger.info(f"文件已保存: {upload_path}")

        # 处理跟卖
        processor = FollowSellProcessor()
        result = processor.process(str(upload_path), new_product_code)

        # 返回成功响应
        return FollowSellResponse(
            success=True,
            message="处理成功",
            data=result
        )

    except FileNotFoundError as e:
        logger.error(f"文件不存在: {e}")
        raise HTTPException(status_code=404, detail=str(e))

    except ValueError as e:
        logger.error(f"数据验证错误: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"处理失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")


@router.get("/download/{filename}")
async def download_file(filename: str):
    """
    下载生成的文件

    Args:
        filename: 文件名

    Returns:
        文件下载响应
    """
    file_path = UPLOADS_DIR / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
