/** 数值格式化工具函数。 */

/**
 * 将数值格式化为百分比字符串。
 *
 * @param value 百分比数值（如 0.31 表示 0.31%）。
 * @returns 格式化后的字符串，null/undefined 返回 "N/A"。
 */
export function formatPercent(value: number | null | undefined): string {
  if (value === null || value === undefined) {
    return 'N/A';
  }
  return `${value}%`;
}

/**
 * 将任意值转为展示字符串，null/undefined 显示为 "N/A"。
 *
 * @param value 待展示的值。
 * @returns 字符串形式的值，或 "N/A"。
 */
export function formatNA(value: unknown): string {
  if (value === null || value === undefined) {
    return 'N/A';
  }
  return String(value);
}

/**
 * 将日期字符串格式化为中文展示形式。
 *
 * @param date 日期字符串（如 "2025-06-24"）或 null/undefined。
 * @returns 中文日期（如 "2025年6月24日"）或 "N/A"。
 */
export function formatDate(date: string | null | undefined): string {
  if (date === null || date === undefined) {
    return 'N/A';
  }

  const d = new Date(date);

  // 无效日期
  if (isNaN(d.getTime())) {
    return 'N/A';
  }

  const year = d.getFullYear();
  const month = d.getMonth() + 1;
  const day = d.getDate();

  return `${year}年${month}月${day}日`;
}
