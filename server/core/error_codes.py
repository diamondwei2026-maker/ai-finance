"""错误码模块 — 统一错误码常量与中文消息模板。

错误码分段：
- 4xxxx: 业务错误（正常 HTTP 状态码下返回）
- 5xxxx: 系统错误（HTTP 5xx）

消息模板：面向用户的中文提示，含 {code} {fund_type} 等占位符。
"""

# ═══════════════════════════════════════════════════════════════════════
# 错误码常量
# ═══════════════════════════════════════════════════════════════════════

FUND_NOT_FOUND: int = 40001
"""基金代码不存在（数据源查无此基金）。"""

FUND_TYPE_MISMATCH: int = 40002
"""基金类型不匹配——非债券型基金。"""

INVALID_CODE_FORMAT: int = 40003
"""基金代码格式错误——非6位纯数字。"""

DATA_SOURCE_FAILED: int = 40004
"""单个数据源获取失败（可恢复，对应指标标 N/A）。"""

ALL_SOURCES_FAILED: int = 50001
"""所有数据源不可用（致命错误，返回 503）。"""

CALCULATION_FAILED: int = 50002
"""计算过程失败。"""


# ═══════════════════════════════════════════════════════════════════════
# 中文消息模板
# ═══════════════════════════════════════════════════════════════════════


class ErrorMessages:
    """错误码对应的中文提示消息模板。

    使用 format() 类方法将占位符替换为具体值。

    Example:
        >>> ErrorMessages.format(ErrorMessages.FUND_NOT_FOUND, code="999999")
        "基金不存在（代码：999999），请检查后重新输入"
    """

    FUND_NOT_FOUND: str = "基金不存在（代码：{code}），请检查后重新输入"
    FUND_TYPE_MISMATCH: str = "仅支持债券型基金，当前类型：{fund_type}"
    INVALID_CODE_FORMAT: str = "基金代码格式错误，请输入6位数字代码"
    DATA_SOURCE_FAILED: str = "部分数据暂时不可用（{indicator}），请稍后重试"
    ALL_SOURCES_FAILED: str = "服务暂时不可用，请稍后重试"
    CALCULATION_FAILED: str = "计算失败，请稍后重试"

    @classmethod
    def format(cls, template: str, **kwargs: object) -> str:
        """用关键字参数替换消息模板中的占位符。

        Args:
            template: 含 {placeholder} 的模板字符串
            **kwargs: 占位符 → 值的映射

        Returns:
            格式化后的中文字符串
        """
        return template.format(**kwargs)
