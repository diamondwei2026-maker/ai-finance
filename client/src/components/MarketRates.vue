<script setup lang="ts">
import { LABELS } from "@/locales/zh-CN";
import { formatPercent } from "@/utils/format";

/**
 * MarketRates — 市场利率卡片组件。
 *
 * 展示 10 年期国债收益率（%）和 AA+ 信用利差（bp），横排布局。
 */

interface Props {
  tenYearTreasury?: number | null;
  creditSpreadAaPlus?: number | null;
}

const props = defineProps<Props>();
</script>

<template>
  <div class="bg-blue-50 rounded-lg p-4 mb-4">
    <!-- 标题行 -->
    <p class="text-sm font-medium text-gray-700 mb-3">当前市场</p>

    <!-- 指标横排 -->
    <div class="flex gap-4">
      <!-- 10年期国债 -->
      <div class="flex-1 text-center">
        <p class="text-xs text-gray-500 mb-1">{{ LABELS.TEN_YEAR_TREASURY }}</p>
        <p class="text-lg font-semibold text-gray-900">
          {{
            props.tenYearTreasury != null
              ? formatPercent(props.tenYearTreasury)
              : "N/A"
          }}
        </p>
      </div>

      <!-- 信用利差 -->
      <div class="flex-1 text-center">
        <p class="text-xs text-gray-500 mb-1">{{ LABELS.CREDIT_SPREAD }}</p>
        <p class="text-lg font-semibold text-gray-900">
          {{
            props.creditSpreadAaPlus != null
              ? `${props.creditSpreadAaPlus}bp`
              : "N/A"
          }}
        </p>
      </div>
    </div>
  </div>
</template>
