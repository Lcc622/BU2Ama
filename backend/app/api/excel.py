"""
Excel 处理 API 路由
"""
import os
import re
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from fastapi.responses import FileResponse, JSONResponse

from app.config import DEFAULT_TEMPLATE_TYPE, RESULTS_DIR, STORE_CONFIGS, STORE_GROUP, TEMPLATES, UPLOADS_DIR
from app.core.excel_processor import excel_processor
from app.core.export_history import export_history
from app.core.follow_sell_processor import follow_sell_processor
from app.core.output_validator import validate_output
from app.models.excel import (
    AnalysisResult,
    ProcessRequest,
    ProcessResponse,
    ProcessAsyncStartResponse,
    ProcessJobStatusResponse,
    TemplateInfo,
    FileInfo,
    SKCQueryRequest,
    SKCQueryResponse,
    SKCProcessRequest,
    SKCProcessResponse,
    SKCBatchProcessRequest,
    SKCBatchProcessResponse,
    ExportHistoryResponse,
)

router = APIRouter(prefix="/api", tags=["Excel 处理"])

_process_executor = ThreadPoolExecutor(max_workers=max(2, int(os.getenv("PROCESS_WORKERS", "4"))))
_process_jobs: Dict[str, Dict] = {}
_jobs_lock = threading.Lock()


def _run_process_job(job_id: str, request: ProcessRequest) -> None:
    started_at = datetime.now().timestamp()
    with _jobs_lock:
        job = _process_jobs.get(job_id)
        if job is not None:
            queued_seconds = max(0.0, started_at - job.get("created_at", started_at))
            job.update({
                "status": "running",
                "message": f"处理中（排队 {queued_seconds:.1f}s 后开始）",
                "started_at": started_at,
                "queued_seconds": queued_seconds,
                "last_progress_at": started_at,
            })

    def progress_update(message: str) -> None:
        with _jobs_lock:
            job = _process_jobs.get(job_id)
            if job is None:
                return
            if job.get("status") == "running":
                job["message"] = message
                job["last_progress_at"] = datetime.now().timestamp()

    try:
        output_filename, processed_count = excel_processor.process_excel(
            template_type=request.template_type,
            filenames=request.filenames,
            selected_prefixes=request.selected_prefixes,
            generated_skus=request.generated_skus,
            target_color=request.target_color,
            target_size=request.target_size,
            processing_mode=request.mode,
            progress_callback=progress_update,
        )
        _record_export_history(
            module=_normalize_export_module(request.mode),
            template_type=request.template_type,
            input_data=_build_add_mode_input_data(request),
            filename=output_filename,
            processed_count=processed_count,
        )
        with _jobs_lock:
            finished_at = datetime.now().timestamp()
            _process_jobs[job_id].update({
                "status": "completed",
                "output_filename": output_filename,
                "processed_count": processed_count,
                "message": "处理完成",
                "error": None,
                "completed_at": finished_at,
                "run_seconds": max(0.0, finished_at - _process_jobs[job_id].get("started_at", finished_at)),
            })
    except Exception as e:
        with _jobs_lock:
            failed_at = datetime.now().timestamp()
            _process_jobs[job_id].update({
                "status": "failed",
                "error": str(e),
                "message": "处理失败",
                "failed_at": failed_at,
                "run_seconds": max(0.0, failed_at - _process_jobs[job_id].get("started_at", failed_at)),
            })


def _resolve_store_config(template_type: Optional[str]) -> Dict:
    normalized = str(template_type or "").strip()
    resolved_template_type = normalized if normalized in STORE_CONFIGS else DEFAULT_TEMPLATE_TYPE
    return STORE_CONFIGS[resolved_template_type]


def _resolve_follow_sell_source_files(template_type: Optional[str] = None) -> List[str]:
    store_config = _resolve_store_config(template_type)
    source_files = [name for name in store_config["source_files"] if (UPLOADS_DIR / name).exists()]
    listing_report = str(store_config["listing_report"])
    if (UPLOADS_DIR / listing_report).exists():
        source_files.append(listing_report)
    return source_files


def _build_follow_sell_filename(skc_tag: str) -> str:
    normalized_skc = re.sub(r"[^A-Z0-9]", "", str(skc_tag or "").strip().upper()) or "UNKNOWN"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"followsell_{normalized_skc}_{timestamp}.xlsx"
    output_path = RESULTS_DIR / filename
    suffix = 1
    while output_path.exists():
        filename = f"followsell_{normalized_skc}_{timestamp}_{suffix}.xlsx"
        output_path = RESULTS_DIR / filename
        suffix += 1
    return filename


def _rename_follow_sell_export(original_filename: str, skc_tag: str) -> tuple[str, int]:
    source_path = RESULTS_DIR / original_filename
    if not source_path.exists():
        source_path = UPLOADS_DIR / original_filename
    if not source_path.exists():
        raise FileNotFoundError(f"导出文件不存在: {original_filename}")

    target_filename = _build_follow_sell_filename(skc_tag)
    target_path = RESULTS_DIR / target_filename
    source_path.rename(target_path)
    return target_filename, int(target_path.stat().st_size)


def _normalize_export_module(mode: Optional[str]) -> str:
    normalized = str(mode or "").strip().lower()
    return "add-code" if normalized == "add-code" else "add-color"


def _build_add_mode_input_data(request: ProcessRequest) -> Dict:
    generated_skus = [str(sku).strip().upper() for sku in (request.generated_skus or []) if str(sku).strip()]
    colors = sorted({sku[7:9] for sku in generated_skus if len(sku) >= 9})
    sizes = sorted({sku[9:11] for sku in generated_skus if len(sku) >= 11})
    return {
        "prefixes": [str(p).strip().upper() for p in request.selected_prefixes if str(p).strip()],
        "colors": colors,
        "sizes": sizes,
        "mode": _normalize_export_module(request.mode),
    }

def _is_allowed_data_filename(filename: str) -> bool:
    normalized = str(filename or "").strip()
    if not normalized:
        return False
    allowed_xlsm = {
        source_file
        for config in STORE_CONFIGS.values()
        for source_file in config.get("source_files", [])
    }
    if normalized in allowed_xlsm:
        return True
    allowed_reports = {
        str(config.get("listing_report", "")).lower()
        for config in STORE_CONFIGS.values()
        if config.get("listing_report")
    }
    return normalized.lower() in allowed_reports


def _validate_selection_constraints(generated_skus: Optional[List[str]]) -> None:
    skus = [str(sku).strip().upper() for sku in (generated_skus or []) if str(sku).strip()]
    if not skus:
        raise HTTPException(status_code=400, detail="缺少目标 SKU，无法处理")

    colors = {sku[7:9] for sku in skus if len(sku) >= 9}
    sizes = {sku[9:11] for sku in skus if len(sku) >= 11}
    if not colors or not sizes:
        raise HTTPException(status_code=400, detail="目标 SKU 格式不正确，无法识别颜色或尺码")


def _build_data_source_warning(new_style: Optional[str], old_style: Optional[str]) -> Optional[str]:
    normalized_new = str(new_style or "").strip().upper()
    normalized_old = str(old_style or "").strip().upper()
    if normalized_new and normalized_old and normalized_new != normalized_old:
        return f"数据来自老款号 {normalized_old}，请确认新老款对应关系正确"
    return None


def _build_per_skc_summary(
    success_results: List[Dict],
    generated_skus: List[str],
    *,
    start_row: int = 4,
) -> List[Dict]:
    row_by_sku = {
        str(sku).strip().upper(): start_row + index
        for index, sku in enumerate(generated_skus)
        if str(sku).strip()
    }
    summaries: List[Dict] = []

    for result in success_results:
        rows: List[int] = []
        seen = set()
        for item in result.get("sizes", []):
            sku = str(item.get("sku", "")).strip().upper()
            if len(sku) < 11 or sku in seen:
                continue
            seen.add(sku)
            row_number = row_by_sku.get(sku)
            if row_number is not None:
                rows.append(row_number)

        if not rows:
            continue

        summaries.append({
            "skc": str(result.get("skc", "")).strip().upper(),
            "new_style": str(result.get("new_style", "")).strip().upper(),
            "old_style": str(result.get("old_style", "")).strip().upper(),
            "row_count": len(rows),
            "start_row": rows[0],
            "end_row": rows[-1],
        })

    return summaries


def _record_export_history(
    *,
    module: str,
    template_type: str,
    input_data: Dict,
    filename: str,
    processed_count: int,
) -> None:
    try:
        file_path = RESULTS_DIR / filename
        if not file_path.exists():
            file_path = UPLOADS_DIR / filename
        file_size = int(file_path.stat().st_size) if file_path.exists() else 0
        export_history.add_record(
            module=module,
            template_type=template_type,
            input_data=input_data,
            filename=filename,
            file_size=file_size,
            processed_count=processed_count,
            status="success",
        )
        export_history.cleanup(retention_days=90, max_records=1000)
    except Exception as exc:
        print(f"[export-history] 记录失败: {exc}")


def _resolve_generated_file_path(filename: str) -> Path:
    result_path = RESULTS_DIR / filename
    if result_path.exists():
        return result_path
    return UPLOADS_DIR / filename


def _safe_validate_generated_output(filename: str, template_type: str) -> Optional[Dict]:
    try:
        file_path = _resolve_generated_file_path(filename)
        if not file_path.exists():
            return None
        return validate_output(str(file_path), template_type)
    except Exception:
        return None


@router.get("/templates", response_model=List[TemplateInfo])
async def get_templates():
    """获取可用的模板列表"""
    templates = []
    for name, config in TEMPLATES.items():
        templates.append(TemplateInfo(
            name=name,
            file="",  # 不再显示文件名
            exists=True  # 模板配置存在即可
        ))
    return templates


@router.post("/analyze", response_model=AnalysisResult)
async def analyze_file(file: UploadFile = File(...)):
    """分析上传的 Excel 文件"""
    try:
        if not _is_allowed_data_filename(file.filename):
            raise HTTPException(
                status_code=400,
                detail="仅支持上传 DA/EP/PZ 店铺的 -0/-1/-2.xlsm 和 All+Listings+Report.txt 数据文件"
            )
        # 保存上传的文件
        file_path = UPLOADS_DIR / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # .txt 价格报告只需要上传保存，不做 Excel 分析
        if str(file.filename).lower().endswith('.txt'):
            return AnalysisResult(
                success=True,
                filename=file.filename,
                total_skus=0,
                unique_colors=0,
                color_distribution=[],
                unknown_colors=[],
                prefixes=[],
                suffixes=[],
            )

        # 分析文件
        result = excel_processor.analyze_excel_file(file.filename)
        return result

    except HTTPException:
        raise
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析文件失败: {str(e)}")


@router.post("/analyze-existing", response_model=AnalysisResult)
async def analyze_existing_file(filename: str):
    """分析服务器上已存在的文件"""
    try:
        # 检查文件是否存在
        file_path = UPLOADS_DIR / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"文件不存在: {filename}")

        # 分析文件
        result = excel_processor.analyze_excel_file(filename)
        return result

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析文件失败: {str(e)}")


@router.post("/process", response_model=ProcessResponse)
async def process_excel(request: ProcessRequest):
    """处理 Excel 文件并生成新文件"""
    try:
        _validate_selection_constraints(request.generated_skus)
        output_filename, processed_count = excel_processor.process_excel(
            template_type=request.template_type,
            filenames=request.filenames,
            selected_prefixes=request.selected_prefixes,
            generated_skus=request.generated_skus,
            target_color=request.target_color,
            target_size=request.target_size,
            processing_mode=request.mode,
        )
        _record_export_history(
            module=_normalize_export_module(request.mode),
            template_type=request.template_type,
            input_data=_build_add_mode_input_data(request),
            filename=output_filename,
            processed_count=processed_count,
        )

        return ProcessResponse(
            success=True,
            output_filename=output_filename,
            message="处理完成",
            processed_count=processed_count
        )

    except HTTPException:
        raise
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理文件失败: {str(e)}")


@router.post("/process-async", response_model=ProcessAsyncStartResponse)
async def process_excel_async(request: ProcessRequest):
    """异步处理 Excel 文件并返回任务 ID"""
    _validate_selection_constraints(request.generated_skus)

    job_id = uuid.uuid4().hex
    with _jobs_lock:
        _process_jobs[job_id] = {
            "status": "queued",
            "output_filename": None,
            "processed_count": 0,
            "message": "任务排队中",
            "error": None,
            "created_at": datetime.now().timestamp(),
        }
    _process_executor.submit(_run_process_job, job_id, request)

    return ProcessAsyncStartResponse(
        success=True,
        job_id=job_id,
        message="任务已提交"
    )


@router.get("/process-status/{job_id}", response_model=ProcessJobStatusResponse)
async def get_process_status(job_id: str):
    """查询异步处理任务状态"""
    with _jobs_lock:
        job = _process_jobs.get(job_id)
        queue_position = 0
        if job and job.get("status") == "queued":
            created_at = float(job.get("created_at", 0))
            queue_position = sum(
                1
                for other_id, other in _process_jobs.items()
                if other_id != job_id
                and other.get("status") == "queued"
                and float(other.get("created_at", 0)) < created_at
            )

    if not job:
        raise HTTPException(status_code=404, detail=f"任务不存在: {job_id}")

    message = job.get("message")
    if job.get("status") == "queued":
        if queue_position > 0:
            message = f"任务排队中，前方 {queue_position} 个任务"
        else:
            message = "任务排队中，即将开始"
    elif job.get("status") == "completed":
        run_seconds = job.get("run_seconds")
        queued_seconds = job.get("queued_seconds")
        if run_seconds is not None and queued_seconds is not None:
            message = f"处理完成（排队 {queued_seconds:.1f}s，执行 {run_seconds:.1f}s）"
    elif job.get("status") == "failed":
        run_seconds = job.get("run_seconds")
        if run_seconds is not None:
            message = f"处理失败（执行 {run_seconds:.1f}s）"
    elif job.get("status") == "running":
        last_progress_at = job.get("last_progress_at")
        if last_progress_at is not None:
            idle_seconds = max(0.0, datetime.now().timestamp() - float(last_progress_at))
            if idle_seconds >= 5:
                message = f"{message}（当前步骤已运行 {idle_seconds:.1f}s）"

    return ProcessJobStatusResponse(
        success=True,
        job_id=job_id,
        status=job["status"],
        output_filename=job.get("output_filename"),
        processed_count=job.get("processed_count", 0),
        message=message,
        error=job.get("error"),
    )


@router.get("/export-history", response_model=ExportHistoryResponse)
async def get_export_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    module: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
):
    """获取通用导出历史记录（分页/模块过滤/搜索）"""
    records, total = export_history.list_records(
        page=page,
        page_size=page_size,
        module=module,
        search=search,
    )
    return ExportHistoryResponse(
        success=True,
        data=records,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/export-history/{history_id}/download")
async def download_export_history_file(history_id: int):
    """下载历史记录文件，若文件缺失则更新状态为 file_missing。"""
    record = export_history.get_record(history_id)
    if not record:
        raise HTTPException(status_code=404, detail="历史记录不存在")

    filename = record["filename"]
    file_path = _resolve_generated_file_path(filename)
    if not file_path.exists():
        export_history.update_status(history_id, "file_missing")
        return JSONResponse(
            content={"success": False, "message": "文件不存在，已标记为 file_missing"},
            status_code=200,
        )

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@router.delete("/export-history/{history_id}")
async def delete_export_history(history_id: int):
    """删除历史记录，并尝试删除对应文件。"""
    record = export_history.delete_record(history_id)
    if not record:
        raise HTTPException(status_code=404, detail="历史记录不存在")

    deleted_file = False
    filename = record.get("filename", "")
    if filename:
        file_path = _resolve_generated_file_path(filename)
        if file_path.exists():
            try:
                os.remove(file_path)
                deleted_file = True
            except OSError:
                deleted_file = False

    return {
        "success": True,
        "deleted": True,
        "deleted_file": deleted_file,
        "message": "历史记录已删除",
    }


@router.get("/download/{filename}")
async def download_file(filename: str):
    """下载生成的文件"""
    file_path = _resolve_generated_file_path(filename)

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@router.get("/store-info")
async def get_store_info():
    """返回当前实例的店铺信息"""
    _display = {"EP": "EP 店铺", "DM_PZ": "DM/PZ 店铺"}
    return {
        "store_group": STORE_GROUP or "ALL",
        "display_name": _display.get(STORE_GROUP or "", "全部店铺"),
    }


@router.get("/files", response_model=List[FileInfo])
async def list_files():
    """列出已上传的文件（按当前实例的店铺过滤）"""
    # 从 source_files 和 listing_report 的实际文件名提取前缀（取第一个 "-" 前的部分）
    if STORE_GROUP:
        _prefixes = set()
        for cfg in STORE_CONFIGS.values():
            for fname in cfg.get("source_files", []):
                _prefixes.add(fname.split("-")[0].upper() + "-")
            report = cfg.get("listing_report", "")
            if report:
                _prefixes.add(report.split("-")[0].upper() + "-")
        allowed_prefixes = tuple(_prefixes)
    else:
        allowed_prefixes = None

    files = []
    for file_path in UPLOADS_DIR.glob("*"):
        if not file_path.is_file():
            continue
        if allowed_prefixes and not file_path.name.upper().startswith(allowed_prefixes):
            continue
        stat = file_path.stat()
        files.append(FileInfo(
            filename=file_path.name,
            size=stat.st_size,
            upload_time=datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        ))

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


@router.post("/follow-sell/query-skc", response_model=SKCQueryResponse)
async def query_skc(request: SKCQueryRequest):
    """查询 SKC 对应的所有尺码信息

    根据输入的 SKC（7位款号+2位颜色），通过新老款映射表查找老款号，
    然后在对应店铺的 -0/-1/-2 聚合表中查找所有尺码信息
    """
    try:
        result = follow_sell_processor.find_sizes_for_skc(
            skc=request.skc,
            template_type=request.template_type,
        )
        result["data_source_warning"] = _build_data_source_warning(
            result.get("new_style"),
            result.get("old_style"),
        )
        return SKCQueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询 SKC 失败: {str(e)}")


@router.post("/follow-sell/process-skc", response_model=SKCProcessResponse)
async def process_skc(request: SKCProcessRequest):
    """根据 SKC 自动匹配老款尺码并导出模板 Excel"""
    try:
        query_result = follow_sell_processor.find_sizes_for_skc(
            skc=request.skc,
            template_type=request.template_type,
        )
        if not query_result.get("success"):
            raise HTTPException(status_code=400, detail=query_result.get("message", "SKC 查询失败"))

        generated_skus = [str(item.get("sku", "")).strip().upper() for item in query_result.get("sizes", []) if item.get("sku")]
        generated_skus = [sku for sku in generated_skus if len(sku) >= 11]
        if not generated_skus:
            raise HTTPException(status_code=400, detail="未生成有效 SKU，无法导出")

        source_files = _resolve_follow_sell_source_files(request.template_type)

        store_config = _resolve_store_config(request.template_type)
        required_xlsm = store_config["source_files"]
        found_xlsm = [f for f in source_files if not f.endswith('.txt')]
        missing_xlsm = [f for f in required_xlsm if f not in found_xlsm]
        if missing_xlsm:
            raise HTTPException(status_code=400, detail=f"缺少数据文件: {', '.join(missing_xlsm)}，无法导出")

        output_filename, _processed_count = excel_processor.process_excel(
            template_type=request.template_type,
            filenames=source_files,
            selected_prefixes=[query_result["new_style"]],
            generated_skus=generated_skus,
            target_color=None,
            target_size=None,
            source_style_map={query_result["new_style"]: query_result["old_style"]},
            clear_image_urls=True,
            follow_sell_mode=True,
        )
        history_filename, _file_size = _rename_follow_sell_export(output_filename, query_result["skc"])
        validation = _safe_validate_generated_output(history_filename, request.template_type)
        _record_export_history(
            module="follow-sell",
            template_type=request.template_type,
            input_data={
                "skc": query_result["skc"],
                "new_style": query_result["new_style"],
                "old_style": query_result["old_style"],
            },
            filename=history_filename,
            processed_count=len(generated_skus),
        )

        return SKCProcessResponse(
            success=True,
            skc=query_result["skc"],
            new_style=query_result["new_style"],
            old_style=query_result["old_style"],
            total_skus=len(generated_skus),
            output_filename=history_filename,
            message=f"导出成功，共生成 {len(generated_skus)} 个 SKU",
            validation=validation,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理 SKC 失败: {str(e)}")


@router.post("/follow-sell/process-skc-batch", response_model=SKCBatchProcessResponse)
async def process_skc_batch(request: SKCBatchProcessRequest):
    """根据多条 SKC 批量匹配并合并导出一个模板 Excel"""
    try:
        normalized_skcs: List[str] = []
        seen_skcs = set()
        for item in request.skcs:
            normalized = str(item).strip().upper()
            if not normalized or normalized in seen_skcs:
                continue
            seen_skcs.add(normalized)
            normalized_skcs.append(normalized)
        if not normalized_skcs:
            raise HTTPException(status_code=400, detail="请至少提供一条有效 SKC")

        success_results = []
        failed_count = 0
        for skc in normalized_skcs:
            result = follow_sell_processor.find_sizes_for_skc(
                skc=skc,
                template_type=request.template_type,
            )
            if result.get("success"):
                success_results.append(result)
            else:
                failed_count += 1

        if not success_results:
            raise HTTPException(status_code=400, detail="所有 SKC 均匹配失败，无法导出")

        generated_skus: List[str] = []
        selected_prefixes: List[str] = []
        seen = set()
        for result in success_results:
            style = result.get("new_style", "")
            if style and style not in selected_prefixes:
                selected_prefixes.append(style)
            for item in result.get("sizes", []):
                sku = str(item.get("sku", "")).strip().upper()
                if len(sku) >= 11 and sku not in seen:
                    seen.add(sku)
                    generated_skus.append(sku)

        if not generated_skus:
            raise HTTPException(status_code=400, detail="未生成有效 SKU，无法导出")

        per_skc_summary = _build_per_skc_summary(success_results, generated_skus)

        source_files = _resolve_follow_sell_source_files(request.template_type)
        store_config = _resolve_store_config(request.template_type)
        required_xlsm = store_config["source_files"]
        found_xlsm = [f for f in source_files if not f.endswith('.txt')]
        missing_xlsm = [f for f in required_xlsm if f not in found_xlsm]
        if missing_xlsm:
            raise HTTPException(status_code=400, detail=f"缺少数据文件: {', '.join(missing_xlsm)}，无法导出")

        output_filename, _processed_count = excel_processor.process_excel(
            template_type=request.template_type,
            filenames=source_files,
            selected_prefixes=selected_prefixes,
            generated_skus=generated_skus,
            target_color=None,
            target_size=None,
            source_style_map={
                str(result.get("new_style", "")).strip().upper(): str(result.get("old_style", "")).strip().upper()
                for result in success_results
                if result.get("new_style") and result.get("old_style")
            },
            clear_image_urls=True,
            follow_sell_mode=True,
        )
        batch_skc = ",".join(normalized_skcs)
        history_filename, _file_size = _rename_follow_sell_export(output_filename, "batch")
        validation = _safe_validate_generated_output(history_filename, request.template_type)
        new_styles = sorted({
            str(item.get("new_style", "")).strip().upper()
            for item in success_results
            if item.get("new_style")
        })
        old_styles = sorted({
            str(item.get("old_style", "")).strip().upper()
            for item in success_results
            if item.get("old_style")
        })
        _record_export_history(
            module="follow-sell",
            template_type=request.template_type,
            input_data={
                "skc": batch_skc,
                "new_style": ",".join(new_styles),
                "old_style": ",".join(old_styles),
            },
            filename=history_filename,
            processed_count=len(generated_skus),
        )

        return SKCBatchProcessResponse(
            success=True,
            total_input_skcs=len(normalized_skcs),
            success_skcs=len(success_results),
            failed_skcs=failed_count,
            total_skus=len(generated_skus),
            per_skc_summary=per_skc_summary,
            output_filename=history_filename,
            message=f"批量导出成功：SKC 成功 {len(success_results)}，失败 {failed_count}，SKU 共 {len(generated_skus)}",
            validation=validation,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量处理 SKC 失败: {str(e)}")
