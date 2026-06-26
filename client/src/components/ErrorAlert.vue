<script setup lang="ts">
/**
 * ErrorAlert — 可复用的错误提示 + 重试组件。
 *
 * 在 FundInput 和 FundResult 页面中统一使用，
 * 提供红色提示区域和重试按钮。
 */

interface Props {
  /** 错误消息文本。 */
  message: string;
  /** 重试按钮文字，默认 "重试"。 */
  retryLabel?: string;
}

const props = withDefaults(defineProps<Props>(), {
  retryLabel: '重试',
});

const emit = defineEmits<{
  /** 用户点击重试时触发。 */
  (e: 'retry'): void;
}>();
</script>

<template>
  <div
    role="alert"
    class="bg-red-50 border border-red-300 text-red-700 rounded-lg p-4 mt-4 text-sm"
  >
    <p class="mb-3">{{ props.message }}</p>
    <button
      type="button"
      class="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium
             hover:bg-red-700 active:bg-red-800 transition-colors"
      @click="emit('retry')"
    >
      {{ props.retryLabel }}
    </button>
  </div>
</template>
