/** API 相关 TypeScript 类型定义。 */

// ═══════════════════════════════════════════════════════════════════════
// 泛型响应包装
// ═══════════════════════════════════════════════════════════════════════

/** 统一 API 响应包装。 */
export interface ApiResponse<T> {
  /** 业务状态码，0 = 成功，非 0 = 错误码。 */
  code: number;
  /** 提示信息。 */
  message: string;
  /** 响应数据，错误时为 null。 */
  data: T | null;
}

// ═══════════════════════════════════════════════════════════════════════
// 错误码常量
// ═══════════════════════════════════════════════════════════════════════

/**
 * 业务错误码常量。
 *
 * 使用 const 对象 + as const 而非 enum，
 * 以兼容 tsconfig 中 erasableSyntaxOnly: true。
 */
export const ErrorCode = {
  /** 前端：请求超时 */
  TIMEOUT: 0,
  /** 前端：网络异常 */
  NETWORK_ERROR: -1,
  /** 后端：基金不存在 */
  FUND_NOT_FOUND: 40001,
  /** 后端：基金类型不匹配（非债券型） */
  TYPE_MISMATCH: 40002,
  /** 后端：基金代码格式错误 */
  INVALID_CODE_FORMAT: 40003,
  /** 后端：数据源获取失败（可恢复） */
  DATA_SOURCE_FAILED: 40004,
  /** 后端：所有数据源不可用（致命） */
  ALL_SOURCES_FAILED: 50001,
  /** 后端：计算失败 */
  CALCULATION_FAILED: 50002,
} as const;

export type ErrorCodeValue = (typeof ErrorCode)[keyof typeof ErrorCode];

// ═══════════════════════════════════════════════════════════════════════
// 基金查询
// ═══════════════════════════════════════════════════════════════════════

/** GET /api/v1/funds/{code} 响应 data 字段。 */
export interface FundInfo {
  /** 6 位基金代码。 */
  fund_code: string;
  /** 基金名称。 */
  name: string;
  /** 基金类型（如"债券型"、"混合偏债"）。 */
  fund_type: string;
  /** 最新单位净值。 */
  nav: number | null;
  /** 七日年化收益率（%），非货币基金可能为 null。 */
  seven_day_annual_yield: number | null;
  /** 数据更新时间（ISO 格式字符串）。 */
  updated_at: string;
  /** 免责声明固定文本。 */
  disclaimer: string;
}

// ═══════════════════════════════════════════════════════════════════════
// 收益计算
// ═══════════════════════════════════════════════════════════════════════

/** GET /api/v1/calculations/{id} 响应 data 字段。
 *
 * 支持三种状态：
 * - processing：计算进行中
 * - completed：计算完成，含 8 项指标
 * - failed：计算失败，含 error_message
 */
export interface Calculation {
  /** 计算状态。 */
  status: 'processing' | 'completed' | 'failed';

  /** 基金代码（completed 时）。 */
  fund_code?: string;
  /** 基金名称（completed 时）。 */
  fund_name?: string;

  // ── 8 项收益指标（completed 时，允许 null 表示数据缺失） ──────

  /** 最新单位净值。 */
  nav?: number | null;
  /** 日涨跌幅（%）。 */
  daily_change_pct?: number | null;
  /** 七日年化收益率（%）。 */
  seven_day_annual_yield?: number | null;
  /** 万份收益（元）。 */
  wanfen_income?: number | null;
  /** 近1月收益率（%）。 */
  one_month_return?: number | null;
  /** 近3月最大回撤（%）。 */
  three_month_max_drawdown?: number | null;
  /** 10年期国债收益率（%）。 */
  ten_year_treasury?: number | null;
  /** 信用利差 AA+（bp）。 */
  credit_spread_aa_plus?: number | null;

  // ── 元数据 ──────────────────────────────────────────────────

  /** 数据日期 "YYYY-MM-DD"。 */
  data_date?: string;
  /** 是否为交易日。 */
  is_trading_day?: boolean;
  /** 免责声明固定文本。 */
  disclaimer?: string;

  // ── 失败状态 ──────────────────────────────────────────────

  /** 错误信息（failed 状态时）。 */
  error_message?: string;
}

/** POST /api/v1/calculations 响应 data 字段。 */
export interface TriggerResult {
  calculation_id: string;
  status: string;
}
