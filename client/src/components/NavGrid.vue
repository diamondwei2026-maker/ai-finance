<script setup lang="ts">
import { computed } from 'vue';
import { LABELS } from '@/locales/zh-CN';
import { formatDecimal, formatPercent } from '@/utils/format';

/**
 * NavGrid — 净值网格组件。
 *
 * 展示最新净值（保留 2 位小数）和日涨跌幅（带正负号颜色）。
 * 颜色遵循 A 股/中债市场惯例：红涨绿跌（BR-05）。
 */

interface Props {
  nav?: number | null;
  dailyChangePct?: number | null;
}

const props = defineProps<Props>();

/** 格式化后的净值：保留 2 位小数或 "N/A"。 */
const navDisplay = computed<string>(() => {
  return formatDecimal(props.nav);
});

/** 格式化后的日涨跌幅文本（含正负号 + %）。 */
const dailyChangeDisplay = computed<string>(() => {
  if (props.dailyChangePct === null || props.dailyChangePct === undefined) return 'N/A';
  const pctStr = formatPercent(props.dailyChangePct);
  if (props.dailyChangePct > 0) return `+${pctStr}`;
  return pctStr;
});

/** 日涨跌幅颜色 class — 红涨绿跌。 */
const dailyChangeColor = computed<string>(() => {
  if (props.dailyChangePct === null || props.dailyChangePct === undefined) return 'text-gray-400';
  if (props.dailyChangePct > 0) return 'text-red-600';
  if (props.dailyChangePct < 0) return 'text-green-600';
  return 'text-gray-600';
});
</script>

<template>
  <div class="grid grid-cols-2 gap-4 mb-4">
    <!-- 最新净值 -->
    <div class="bg-gray-50 rounded-lg p-4 text-center">
      <p class="text-xs text-gray-500 mb-1">{{ LABELS.NAV }}</p>
      <p class="text-xl sm:text-2xl font-semibold text-gray-900">{{ navDisplay }}</p>
    </div>

    <!-- 日涨跌幅 -->
    <div class="bg-gray-50 rounded-lg p-4 text-center">
      <p class="text-xs text-gray-500 mb-1">{{ LABELS.DAILY_CHANGE }}</p>
      <p class="text-xl sm:text-2xl font-semibold" :class="dailyChangeColor">
        {{ dailyChangeDisplay }}
      </p>
    </div>
  </div>
</template>
