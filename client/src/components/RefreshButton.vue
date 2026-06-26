<script setup lang="ts">
import { LABELS } from '@/locales/zh-CN';

/**
 * RefreshButton — 刷新计算按钮组件。
 *
 * 支持正常态和 loading 态（disabled + spinner + "计算中…"）。
 */

interface Props {
  loading?: boolean;
}

defineProps<Props>();

defineEmits<{
  refresh: [];
}>();
</script>

<template>
  <button
    :disabled="loading"
    class="w-full px-6 py-3 rounded-lg font-medium transition-colors
           bg-blue-600 text-white hover:bg-blue-700
           disabled:opacity-50 disabled:cursor-not-allowed"
    @click="$emit('refresh')"
  >
    <!-- Loading Spinner -->
    <svg
      v-if="loading"
      class="animate-spin h-5 w-5 mr-2 inline align-middle"
      viewBox="0 0 24 24"
      fill="none"
    >
      <circle
        class="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        stroke-width="4"
      />
      <path
        class="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
      />
    </svg>

    {{ loading ? '计算中…' : LABELS.REFRESH_BUTTON }}
  </button>
</template>
