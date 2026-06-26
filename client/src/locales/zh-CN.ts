/** 中文界面文案常量。
 *
 * 所有面向用户的文案集中管理，便于后续 i18n 扩展。
 */

// ═══════════════════════════════════════════════════════════════════════
// 错误提示
// ═══════════════════════════════════════════════════════════════════════

export const ERROR_MESSAGES = {
  NETWORK_ERROR: '网络异常，请检查网络连接',
  TIMEOUT: '请求超时，请稍后重试',
  FUND_NOT_FOUND: '基金代码不存在，请检查后重试',
  TYPE_MISMATCH: '该基金不是债券型基金，请输入债券基金代码',
  INVALID_CODE_FORMAT: '基金代码格式错误，请输入6位数字',
  CALCULATION_FAILED: '计算失败，请稍后重试',
  UNKNOWN_ERROR: '未知错误，请稍后重试',
  POLLING_TIMEOUT: '计算超时，请稍后重试',
} as const;

// ═══════════════════════════════════════════════════════════════════════
// 标签文案
// ═══════════════════════════════════════════════════════════════════════

export const LABELS = {
  PAGE_TITLE: '债券收益计算',
  FUND_CODE_PLACEHOLDER: '请输入6位基金代码',
  QUERY_BUTTON: '查询',
  REFRESH_BUTTON: '刷新计算',
  LOADING: '加载中...',
  CALCULATING: '计算中，请稍候...',
  NAV: '最新净值',
  DAILY_CHANGE: '日涨跌',
  SEVEN_DAY_YIELD: '七日年化',
  WANFEN_INCOME: '万份收益',
  ONE_MONTH_RETURN: '近1月收益',
  MAX_DRAWDOWN: '近3月最大回撤',
  TEN_YEAR_TREASURY: '10年期国债',
  CREDIT_SPREAD: '信用利差',
  DATA_DATE: '数据日期',
  NOT_TRADING_DAY: '非交易日',
  BOND_FUND: '债券型',
  NON_BOND_FUND: '非债券型',
  YUAN: '元',
  FUND_INFO: '基金信息',
  CALCULATION_RESULT: '计算结果',
  FUND_CODE_INPUT_ERROR: '请输入 6 位基金代码',
  CONFIRM_BUTTON: '确认并查看详情',
  PAGE_SUBTITLE: '输入基金代码，一键获取收益数据',
  NO_DATA: '暂无数据',
  INPUT_ARIA_LABEL: '基金代码',
} as const;

// ═══════════════════════════════════════════════════════════════════════
// 免责声明
// ═══════════════════════════════════════════════════════════════════════

export const DISCLAIMER = {
  TITLE: '免责声明',
  TEXT: '本工具计算结果仅供参考，不构成任何投资建议。基金过往业绩不代表未来表现，投资有风险，选择需谨慎。数据来源：天天基金、东方财富、中债信息网。',
} as const;
