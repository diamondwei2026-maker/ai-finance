"""FastAPI 应用入口 — 包含 lifespan 事件、CORS 中间件、健康检查路由。"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from models.fund import Fund
from models.calculation import Calculation
from models.market_data import MarketData
from core.config import settings
from core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理：startup 初始化日志/数据库，shutdown 清理资源。"""
    # ===== startup =====
    setup_logging()
    logger.info("Starting {} v{}", settings.APP_NAME, settings.APP_VERSION)

    # MongoDB 连接 + Beanie 初始化
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client.get_default_database()

        # 确保数据库存在 — MongoDB 在首次写入时才真正创建 DB，
        # 这里通过创建 collections 来触发（已存在则跳过）
        existing_cols = await db.list_collection_names()
        for coll_name in ("funds", "calculations", "market_data"):
            if coll_name not in existing_cols:
                await db.create_collection(coll_name)
                logger.info("已创建 MongoDB 集合: {}", coll_name)

        await init_beanie(
            database=db,
            document_models=[Fund, Calculation, MarketData],
        )
        logger.info("MongoDB 数据库 {} 已就绪，Beanie 已初始化", db.name)
    except Exception as e:
        logger.error("MongoDB 初始化失败: {}", e)
        logger.warning("应用以降级模式运行 — 数据库不可用")
        # 不崩溃，让应用以降级模式运行

    yield

    # ===== shutdown =====
    logger.info("Application shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)


# ── 全局异常处理器 ──────────────────────────────────────────────────


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """捕获所有未处理的异常，返回统一 ApiResponse 格式。

    避免 FastAPI 默认的原始 500 响应，确保前端始终收到结构化错误。
    """
    logger.exception("未处理的异常: {} — {}", request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={
            "code": 50000,
            "message": "服务器内部错误，请稍后重试",
            "data": None,
        },
    )


# CORS 中间件 — 仅允许前端需要的 HTTP 方法和请求头
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


# ── 路由注册 ──────────────────────────────────────────────────────

from api.routes import funds, calculations

app.include_router(funds.router, prefix="/api/v1")
app.include_router(calculations.router, prefix="/api/v1")


@app.get("/")
async def health_check() -> dict[str, str]:
    """根路径健康检查。"""
    return {"status": "ok"}
