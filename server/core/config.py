"""配置管理模块 — 从 .env 文件和环境变量读取所有配置项。"""

from typing import Annotated, ClassVar

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置，自动从 .env 文件加载。"""

    # MongoDB
    MONGODB_URL: str  # 必填，无默认值，缺失时启动报错

    # CORS
    CORS_ORIGINS: Annotated[list[str], NoDecode] = ["http://localhost:5173"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """将逗号分隔的环境变量字符串解析为列表。

        Render 环境变量只能传字符串，此方法确保
        "https://a.com,https://b.com" → ["https://a.com", "https://b.com"]
        空字符串回退到默认值，避免无源列表阻止所有跨域请求。
        """
        if isinstance(v, str):
            if not v.strip():
                return ["http://localhost:5173"]
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    VALID_LOG_LEVELS: ClassVar[set[str]] = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

    @field_validator("LOG_LEVEL", mode="before")
    @classmethod
    def validate_log_level(cls, v):
        """验证并规范化 LOG_LEVEL 值。"""
        if not isinstance(v, str) or not v.strip():
            return "DEBUG"
        upper = v.strip().upper()
        if upper not in cls.VALID_LOG_LEVELS:
            raise ValueError(
                f"LOG_LEVEL '{v}' 无效，有效值: {', '.join(sorted(cls.VALID_LOG_LEVELS))}"
            )
        return upper

    # Environment
    ENVIRONMENT: str = "development"  # development | production
    LOG_LEVEL: str = "DEBUG"          # DEBUG | INFO | WARNING | ERROR | CRITICAL

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
