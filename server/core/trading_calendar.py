"""交易日历模块 — 封装 exchange_calendars，判断指定日期是否为交易日。

保守策略：任何异常（库不可用、数据缺失、参数类型不兼容）均返回 False，
即默认按非交易日处理，避免在非交易日给出错误判断。
"""

import datetime as dt

from loguru import logger


def is_trading_day(date: dt.date | None = None) -> bool:
    """判断指定日期是否为上交所（XSHG）交易日。

    Args:
        date: 待判断的日期，None 表示当天。

    Returns:
        True 表示交易日，False 表示非交易日或无法判断。
    """
    if date is None:
        date = dt.date.today()

    try:
        import exchange_calendars as ec

        cal = ec.get_calendar("XSHG")
        # is_session 接受 str "YYYY-MM-DD" 或 pd.Timestamp
        return bool(cal.is_session(str(date)))
    except Exception:
        logger.warning(
            "交易日历判断失败，默认按非交易日处理 (date={})",
            date.isoformat(),
        )
        return False
