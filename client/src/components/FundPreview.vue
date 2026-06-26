<script setup lang="ts">
import type { FundInfo } from '@/types/api';
import { useFundStore } from '@/stores/fund';
import { formatDecimal, formatPercent } from '@/utils/format';
import { LABELS, ERROR_MESSAGES } from '@/locales/zh-CN';

/**
 * Props 定义。
 *
 * - fundInfo: 基金信息，null 时组件不渲染任何 DOM。
 */
defineProps<{
  fundInfo: FundInfo | null;
}>();

/**
 * Emits 定义。
 *
 * - confirm: 用户确认查看该基金详情。
 */
const emit = defineEmits<{
  (e: 'confirm', code: string): void;
}>();

const store = useFundStore();

/** 点击确认按钮。 */
function onConfirm(code: string): void {
  emit('confirm', code);
}
</script>

<template>
  <div
    v-if="fundInfo"
    :class="[
      'rounded-xl shadow-sm p-6 mt-4 transition-colors duration-150',
      !store.isBondFund
        ? 'bg-amber-50 border border-amber-400'
        : 'bg-white border border-gray-200',
    ]"
  >
    <!-- 基金基本信息 -->
    <section class="space-y-2">
      <h2 class="text-lg font-semibold text-gray-900">
        {{ fundInfo.name }}
      </h2>

      <p class="text-sm text-gray-500">
        {{ fundInfo.fund_code }}
      </p>

      <!-- 基金类型标签 -->
      <span
        :class="[
          'inline-block text-xs font-medium rounded-full px-2.5 py-0.5',
          !store.isBondFund
            ? 'bg-amber-200 text-amber-800'
            : 'bg-green-100 text-green-700',
        ]"
      >
        {{ fundInfo.fund_type }}
      </span>

      <!-- 净值与七日年化 -->
      <div class="grid grid-cols-2 gap-3 pt-2">
        <div>
          <span class="text-xs text-gray-400">{{ LABELS.NAV }}</span>
          <p class="text-base font-medium text-gray-800">
            {{ formatDecimal(fundInfo.nav) }}
            <span v-if="fundInfo.nav !== null" class="text-xs text-gray-400">{{ LABELS.YUAN }}</span>
          </p>
        </div>
        <div>
          <span class="text-xs text-gray-400">{{ LABELS.SEVEN_DAY_YIELD }}</span>
          <p class="text-base font-medium text-gray-800">
            {{ fundInfo.seven_day_annual_yield !== null ? formatPercent(fundInfo.seven_day_annual_yield) : LABELS.NO_DATA }}
          </p>
        </div>
      </div>
    </section>

    <!-- 非债券型警告 -->
    <div
      v-if="!store.isBondFund"
      role="alert"
      class="mt-4 bg-amber-50 border border-amber-400 text-amber-800 rounded-lg p-3 text-sm flex items-start gap-2"
    >
      <span aria-hidden="true">⚠️</span>
      <span>{{ ERROR_MESSAGES.TYPE_MISMATCH }}</span>
    </div>

    <!-- 确认按钮（仅债券型可用） -->
    <button
      v-if="store.isBondFund"
      type="button"
      class="mt-5 w-full bg-blue-600 hover:bg-blue-700 active:bg-blue-800
             text-white text-sm font-medium rounded-lg py-2.5
             transition-colors duration-150"
      @click="onConfirm(fundInfo.fund_code)"
    >
      {{ LABELS.CONFIRM_BUTTON }} →
    </button>

    <!-- 非债券型不可确认 -->
    <div
      v-else
      class="mt-5 w-full text-center text-sm text-gray-400 py-2.5
             bg-gray-100 rounded-lg cursor-not-allowed"
    >
      {{ LABELS.BOND_FUND_ONLY }}
    </div>
  </div>
</template>
