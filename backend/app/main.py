"""
FastAPI 主应用
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.config import CORS_ORIGINS
from app.api import mapping, excel, followsell
from app.core.excel_processor import excel_processor

# 创建 FastAPI 应用
app = FastAPI(
    title="BU2Ama Excel 颜色加色系统",
    description="Excel SKU 颜色映射和处理系统",
    version="2.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(mapping.router)
app.include_router(excel.router)
app.include_router(followsell.router)

logger = logging.getLogger(__name__)


@app.on_event("startup")
async def prewarm_caches():
    template_warmup = excel_processor.prewarm_template_cache()
    logger.info(f"Template cache prewarm: {template_warmup}")


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": str(exc)
        }
    )


# 健康检查
@app.get("/")
async def root():
    return {
        "name": "BU2Ama Excel 颜色加色系统",
        "version": "2.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    from app.config import HOST, PORT

    uvicorn.run(
        "app.main:app",
        host=HOST,
        port=PORT,
        reload=True
    )
