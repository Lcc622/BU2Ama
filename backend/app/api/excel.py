"""
Excel 处理 API 路由
"""
import os
from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse

from app.config import UPLOADS_DIR, TEMPLATES_DIR, TEMPLATES
from app.core.excel_processor import excel_processor
from app.models.excel import (
    AnalysisResult,
    ProcessRequest,
    ProcessResponse,
    TemplateInfo,
    FileInfo
)

router = APIRouter(prefix="/api", tags=["Excel 处理"])


@router.get("/templates", response_model=List[TemplateInfo])
async def get_templates():
    """获取可用的模板列表"""
    templates = []
    for name, config in TEMPLATES.items():
        template_path = TEMPLATES_DIR / config["file"]
        templates.append(TemplateInfo(
            name=name,
            file=config["file"],
            exists=template_path.exists()
        ))
    return templates


@router.post("/analyze", response_model=AnalysisResult)
async def analyze_file(file: UploadFile = File(...)):
    """分析上传的 Excel 文件"""
    try:
        # 保存上传的文件
        file_path = UPLOADS_DIR / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # 分析文件
        result = excel_processor.analyze_excel_file(file.filename)
        return result

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析文件失败: {str(e)}")


@router.post("/process", response_model=ProcessResponse)
async def process_excel(request: ProcessRequest):
    """处理 Excel 文件并生成新文件"""
    try:
        output_filename, processed_count = excel_processor.process_excel(
            template_type=request.template_type,
            filenames=request.filenames,
            selected_prefixes=request.selected_prefixes,
            target_color=request.target_color,
            target_size=request.target_size
        )

        return ProcessResponse(
            success=True,
            output_filename=output_filename,
            message="处理完成",
            processed_count=processed_count
        )

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理文件失败: {str(e)}")


@router.get("/download/{filename}")
async def download_file(filename: str):
    """下载生成的文件"""
    file_path = UPLOADS_DIR / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@router.get("/files", response_model=List[FileInfo])
async def list_files():
    """列出所有已上传的文件"""
    files = []
    for file_path in UPLOADS_DIR.glob("*"):
        if file_path.is_file():
            stat = file_path.stat()
            files.append(FileInfo(
                filename=file_path.name,
                size=stat.st_size,
                upload_time=datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            ))

    # 按上传时间倒序排列
    files.sort(key=lambda x: x.upload_time, reverse=True)
    return files


@router.delete("/files/{filename}")
async def delete_file(filename: str):
    """删除已上传的文件"""
    file_path = UPLOADS_DIR / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")

    try:
        os.remove(file_path)
        return {"success": True, "message": f"文件 {filename} 已删除"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除文件失败: {str(e)}")
