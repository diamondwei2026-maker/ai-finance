<script setup lang="ts">
import { LABELS } from '@/locales/zh-CN';
import { formatDate } from '@/utils/format';

/**
 * ResultHeader — 结果头部组件。
 *
 * 展示基金名称、代码、数据日期及非交易日提示。
 */

interface Props {
  fundName?: string | null;
  fundCode?: string;
  dataDate?: string | null;
  isTradingDay?: boolean;
}

const props = defineProps<Props>();
</script>

<template>
  <div class="bg-white rounded-lg p-5 mb-4">
    <!-- 基金名称 + 代码 -->
    <div class="flex items-baseline gap-2 mb-3">
      <h2 class="text-xl font-bold text-gray-900">
        {{ props.fundName ?? 'N/A' }}
      </h2>
      <span class="text-sm text-gray-500">
        {{ props.fundCode ?? 'N/A' }}
      </span>
    </div>

    <!-- 数据日期 -->
    <div class="flex items-center gap-2 text-sm text-gray-600">
      <span>{{ LABELS.DATA_DATE }}：</span>
      <time
        v-if="props.dataDate"
        :datetime="props.dataDate"
        class="font-medium text-gray-800"
      >
        {{ formatDate(props.dataDate) }}
      </time>
      <span v-else class="font-medium text-gray-800">N/A</span>
      <span class="text-gray-400">（昨日净值）</span>
    </div>

    <!-- 非交易日标注 -->
    <p
      v-if="props.isTradingDay === false"
      class="text-amber-600 text-xs mt-2"
    >
      非交易日，数据可能有延迟
    </p>
  </div>
</template>
