/** 收益计算 API。 */

import { baseFetch } from './index';
import type { Calculation, TriggerResult } from '@/types/api';

/**
 * 触发基金收益计算。
 *
 * @param code 6 位基金代码（如 "020741"）。
 * @returns calculation_id 和状态。
 */
export async function triggerCalculation(code: string): Promise<TriggerResult> {
  return baseFetch<TriggerResult>('/api/v1/calculations', {
    method: 'POST',
    body: JSON.stringify({ fund_code: code }),
  });
}

/**
 * 获取计算结果。
 *
 * @param id calculation_id（MongoDB ObjectId 字符串）。
 * @returns 计算结果（支持 processing/completed/failed 三种状态）。
 */
export async function getCalculation(id: string): Promise<Calculation> {
  return baseFetch<Calculation>(
    `/api/v1/calculations/${encodeURIComponent(id)}`,
  );
}
