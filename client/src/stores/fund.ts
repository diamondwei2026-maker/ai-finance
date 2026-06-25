/** 基金信息与计算结果 Pinia Store。
 *
 * 管理基金查询和收益计算的全局状态，供 FundInput / FundResult 页面共享。
 */

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { FundInfo, Calculation } from '@/types/api';
import { fetchFund } from '@/api/funds';
import { triggerCalculation, getCalculation } from '@/api/calculations';
import { ApiError } from '@/api/index';
import { ERROR_MESSAGES } from '@/locales/zh-CN';

/** 轮询间隔（毫秒）。 */
const POLL_INTERVAL = 2000;

/** 轮询最大时长（毫秒）。 */
const POLL_TIMEOUT = 120_000;

export const useFundStore = defineStore('fund', () => {
  // ── 状态 ──────────────────────────────────────────────────────────

  /** 基金基本信息。 */
  const fundInfo = ref<FundInfo | null>(null);

  /** 最新计算结果。 */
  const calculation = ref<Calculation | null>(null);

  /** 是否有请求进行中。 */
  const loading = ref(false);

  /** 最近一次错误信息。 */
  const error = ref<string | null>(null);

  // ── 计算属性 ──────────────────────────────────────────────────────

  /** 当前查询的基金是否为债券型。 */
  const isBondFund = computed<boolean>(() => {
    return fundInfo.value?.fund_type?.includes('债') ?? false;
  });

  /** 是否已有计算结果。 */
  const hasCalculation = computed<boolean>(() => calculation.value !== null);

  // ── 操作 ──────────────────────────────────────────────────────────

  /**
   * 查询基金基本信息。
   *
   * @param code 6 位基金代码。
   */
  async function fetchFundInfo(code: string): Promise<void> {
    loading.value = true;
    error.value = null;

    try {
      fundInfo.value = await fetchFund(code);
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        error.value = err.message;
      } else {
        error.value = ERROR_MESSAGES.UNKNOWN_ERROR;
      }
    } finally {
      loading.value = false;
    }
  }

  /**
   * 触发收益计算并轮询等待结果。
   *
   * 流程：POST 触发计算 → 获取 calculation_id →
   * 轮询 GET 结果（最多 120 秒）→ 更新 calculation。
   *
   * @param code 6 位基金代码。
   */
  async function refreshCalculation(code: string): Promise<void> {
    loading.value = true;
    error.value = null;

    try {
      // 1. 触发计算
      const triggerResult = await triggerCalculation(code);

      // 2. 如果已完成，直接获取结果
      if (triggerResult.status === 'completed') {
        const result = await getCalculation(triggerResult.calculation_id);
        if (result.status === 'completed') {
          calculation.value = result;
        }
        return;
      }

      // 3. 轮询等待结果
      const startTime = Date.now();

      while (Date.now() - startTime < POLL_TIMEOUT) {
        await sleep(POLL_INTERVAL);

        const result = await getCalculation(triggerResult.calculation_id);

        if (result.status === 'completed') {
          calculation.value = result;
          return;
        }

        if (result.status === 'failed') {
          error.value = result.error_message ?? ERROR_MESSAGES.CALCULATION_FAILED;
          return;
        }

        // status === 'processing' → 继续轮询
      }

      // 4. 超时
      error.value = ERROR_MESSAGES.POLLING_TIMEOUT;
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        error.value = err.message;
      } else {
        error.value = ERROR_MESSAGES.UNKNOWN_ERROR;
      }
    } finally {
      loading.value = false;
    }
  }

  /** 清空错误信息。 */
  function clearError(): void {
    error.value = null;
  }

  // ── 内部工具 ──────────────────────────────────────────────────────

  /** Promise-based 延迟。 */
  function sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  // ── 导出 ──────────────────────────────────────────────────────────

  return {
    // 状态
    fundInfo,
    calculation,
    loading,
    error,
    // 计算属性
    isBondFund,
    hasCalculation,
    // 操作
    fetchFundInfo,
    refreshCalculation,
    clearError,
  };
});
