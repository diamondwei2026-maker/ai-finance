"""配置管理模块 — 从 .env 文件和环境变量读取所有配置项。"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置，自动从 .env 文件加载。"""

    # MongoDB
    MONGODB_URL: str  # 必填，无默认值，缺失时启动报错

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    # Cache TTL (seconds)
    CACHE_TTL_FUND: int = 1800       # 基金信息 30min
    CACHE_TTL_CALC: int = 300        # 计算结果 5min
    CACHE_TTL_MARKET: int = 120      # 市场利率 2min

    # App
    APP_NAME: str = "债券收益计算工具"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# 模块级单例，其他模块通过 `from core.config import settings` 引用
settings = Settings()
