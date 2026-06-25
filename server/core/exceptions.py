"""异常处理模块 — 定义业务异常体系。

异常分级：
- RecoverableError：单个数据源失败 → 该指标标 N/A，其余指标正常返回
- FatalError：全部数据源不可用 → 返回 503，提示用户稍后重试
"""


class AppException(Exception):
    """业务异常基类。

    Attributes:
        message: 错误描述信息
        code: 业务错误码
        status_code: HTTP 状态码
    """

    def __init__(self, message: str, code: int = 50000, status_code: int = 500) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)


class RecoverableError(AppException):
    """可恢复错误 — 单个数据源失败，对应指标标 N/A。

    默认 HTTP 状态码 200（不中断响应，仅部分数据缺失）。
    """

    def __init__(
        self,
        message: str = "部分数据不可用",
        code: int = 40001,
        status_code: int = 200,
    ) -> None:
        super().__init__(message=message, code=code, status_code=status_code)


class FatalError(AppException):
    """致命错误 — 所有数据源均不可用。

    默认 HTTP 状态码 503（服务不可用，提示用户稍后重试）。
    """

    def __init__(
        self,
        message: str = "服务暂时不可用，请稍后重试",
        code: int = 50001,
        status_code: int = 503,
    ) -> None:
        super().__init__(message=message, code=code, status_code=status_code)


class ErrorCode:
    """业务错误码常量。

    注意：错误码 40003 分配给 INVALID_CODE_FORMAT（基金代码格式错误），
    原 DATA_SOURCE_FAILED 移位至 40004。
    """

    FUND_NOT_FOUND: int = 40001       # 基金不存在
    TYPE_MISMATCH: int = 40002        # 基金类型不匹配（非债券型）
    INVALID_CODE_FORMAT: int = 40003  # 基金代码格式错误
    DATA_SOURCE_FAILED: int = 40004   # 数据源获取失败（可恢复）
    ALL_SOURCES_FAILED: int = 50001   # 所有数据源不可用（致命）
    CALCULATION_FAILED: int = 50002   # 计算失败
