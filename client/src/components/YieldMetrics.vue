<script setup lang="ts">
import { computed } from 'vue';
import { LABELS } from '@/locales/zh-CN';
import { formatDecimal, formatPercent } from '@/utils/format';

/**
 * YieldMetrics — 收益指标卡片组件。
 *
 * 展示 4 项收益指标（七日年化、万份收益、近1月收益、近3月最大回撤），
 * 2×2 网格布局，每项含 emoji + 标签 + 数值。
 * 颜色遵循 A 股/中债市场惯例：红涨绿跌（BR-05）。
 */

interface Props {
  sevenDayYield?: number | null;
  wanfenIncome?: number | null;
  oneMonthReturn?: number | null;
  threeMonthMaxDrawdown?: number | null;
}

const props = defineProps<Props>();

/** 指标项定义。 */
interface MetricItem {
  emoji: string;
  label: string;
  value: number | null | undefined;
  display: string;
  /** 颜色 class — 红涨绿跌，0 或 null 用灰色。 */
  colorClass: string;
}

/** 根据数值正负返回颜色 class（红涨绿跌）。 */
function getColorClass(value: number | null | undefined): string {
  if (value === null || value === undefined) return 'text-gray-400';
  if (value > 0) return 'text-red-600';
  if (value < 0) return 'text-green-600';
  return 'text-gray-600';
}

/** 构建 4 项指标展示数据。 */
function buildMetrics(): MetricItem[] {
  return [
    {
      emoji: '\u{1F4C8}', // 📈
      label: LABELS.SEVEN_DAY_YIELD,
      value: props.sevenDayYield,
      display:
        props.sevenDayYield != null
          ? formatPercent(props.sevenDayYield)
          : 'N/A',
      colorClass: getColorClass(props.sevenDayYield),
    },
    {
      emoji: '\u{1F4B5}', // 💵
      label: LABELS.WANFEN_INCOME,
      value: props.wanfenIncome,
      display:
        props.wanfenIncome != null
          ? `${formatDecimal(props.wanfenIncome)} ${LABELS.YUAN}`
          : 'N/A',
      colorClass: 'text-gray-900',
    },
    {
      emoji: '\u{1F4C9}', // 📉
      label: LABELS.ONE_MONTH_RETURN,
      value: props.oneMonthReturn,
      display:
        props.oneMonthReturn != null
          ? formatPercent(props.oneMonthReturn)
          : 'N/A',
      colorClass: getColorClass(props.oneMonthReturn),
    },
    {
      emoji: '⚠️', // ⚠️
      label: LABELS.MAX_DRAWDOWN,
      value: props.threeMonthMaxDrawdown,
      display:
        props.threeMonthMaxDrawdown != null
          ? formatPercent(props.threeMonthMaxDrawdown)
          : 'N/A',
      colorClass: 'text-gray-900',
    },
  ];
}
</script>

<template>
  <div class="grid grid-cols-2 gap-3 mb-4">
    <div
      v-for="(item, idx) in buildMetrics()"
      :key="idx"
      class="bg-gray-50 rounded-lg p-4 flex flex-col items-center text-center"
    >
      <span class="text-xl sm:text-2xl mb-1">{{ item.emoji }}</span>
      <span class="text-xs text-gray-500">{{ item.label }}</span>
      <span class="text-lg sm:text-xl font-semibold mt-1" :class="item.colorClass">{{ item.display }}</span>
    </div>
  </div>
</template>
