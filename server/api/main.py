"""FastAPI 应用入口 — 包含 lifespan 事件、CORS 中间件、健康检查路由。"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
        await init_beanie(
            database=client.get_default_database(),
            document_models=[Fund, Calculation, MarketData],
        )
        logger.info("MongoDB connected, Beanie initialized")
    except Exception as e:
        logger.error("MongoDB connection failed: {}", e)
        logger.warning("Application running in degraded mode — database unavailable")
        # 不崩溃，让应用以降级模式运行

    yield

    # ===== shutdown =====
    logger.info("Application shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── 路由注册 ──────────────────────────────────────────────────────

from api.routes import funds

app.include_router(funds.router, prefix="/api/v1")


@app.get("/")
async def health_check() -> dict[str, str]:
    """根路径健康检查。"""
    return {"status": "ok"}
