"""缓存模块 — 基于 cachetools.TTLCache 的内存缓存。

按 key 前缀区分 TTL：
- "fund:"   → 基金信息 30min
- "calc:"   → 计算结果 5min
- "market:" → 市场利率 2min
"""

from typing import Any, Callable

from cachetools import TTLCache

from core.config import settings

# 按前缀维护的缓存实例字典
_caches: dict[str, TTLCache] = {}

# 默认 maxsize（单用户场景足够）
_DEFAULT_MAXSIZE = 256


def _get_ttl_for_prefix(prefix: str) -> int:
    """根据 key 前缀返回对应的 TTL（秒）。"""
    if prefix.startswith("fund:"):
        return settings.CACHE_TTL_FUND
    elif prefix.startswith("calc:"):
        return settings.CACHE_TTL_CALC
    elif prefix.startswith("market:"):
        return settings.CACHE_TTL_MARKET
    else:
        # 未匹配的前缀默认 300s
        return 300


def get_cache(prefix: str) -> TTLCache:
    """按前缀获取或创建 TTLCache 实例。

    Args:
        prefix: 缓存 key 前缀（如 "fund:"、"calc:"、"market:"）

    Returns:
        对应 TTL 的 TTLCache 实例
    """
    if prefix not in _caches:
        ttl = _get_ttl_for_prefix(prefix)
        _caches[prefix] = TTLCache(maxsize=_DEFAULT_MAXSIZE, ttl=ttl)
    return _caches[prefix]


def get_or_set(cache: TTLCache, key: str, factory: Callable[[], Any]) -> Any:
    """从缓存取值，未命中则调用 factory 生成值并写入缓存。

    Args:
        cache: TTLCache 实例
        key: 缓存键，不能为空字符串
        factory: 生成缓存值的无参可调用对象

    Returns:
        缓存值或 factory 生成的新值

    Raises:
        ValueError: 当 key 为空字符串时
    """
    if not key:
        raise ValueError("Cache key must not be empty")

    if key in cache:
        return cache[key]

    value = factory()
    cache[key] = value
    return value
