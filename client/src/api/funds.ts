/** 基金查询 API。 */

import { baseFetch } from './index';
import type { FundInfo } from '@/types/api';

/**
 * 查询基金基本信息。
 *
 * @param code 6 位基金代码（如 "020741"）。
 * @returns 基金信息。
 */
export async function fetchFund(code: string): Promise<FundInfo> {
  return baseFetch<FundInfo>(`/api/v1/funds/${encodeURIComponent(code)}`);
}
