"""日志配置模块 — 基于 loguru 配置控制台 + 文件双输出。"""

import sys
from pathlib import Path

from loguru import logger

from core.config import settings


def setup_logging() -> None:
    """配置 loguru：移除默认 handler，添加控制台彩色输出 + 文件归档。

    调用一次即全局生效，在 api/main.py 启动时调用。
    """
    # 移除默认 handler
    logger.remove()

    # 控制台彩色输出（级别由 LOG_LEVEL 环境变量控制）
    console_level = settings.LOG_LEVEL.upper()
    logger.add(
        sys.stdout,
        colorize=True,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        level=console_level,
    )

    # 确保 logs 目录存在
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # 文件输出（10MB 轮转，保留最近 5 个归档）
    logger.add(
        logs_dir / "bond_tool.log",
        rotation="10 MB",
        retention=5,
        encoding="utf-8",
        format=(
            "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
            "{name}:{function}:{line} - {message}"
        ),
        level="INFO",
    )

    logger.info("Logging configured — level: {}", console_level)
