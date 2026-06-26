<script setup lang="ts">
import { ref, onUnmounted } from 'vue';
import { LABELS } from '@/locales/zh-CN';

/**
 * Props 定义。
 *
 * - loading: 是否处于查询加载状态，控制按钮禁用和 spinner 显示。
 */
const props = withDefaults(defineProps<{
  loading?: boolean;
}>(), {
  loading: false,
});

/**
 * Emits 定义。
 *
 * - search: 用户输入有效 6 位代码时触发。
 */
const emit = defineEmits<{
  (e: 'search', code: string): void;
}>();

// ── 状态 ──────────────────────────────────────────────────────────────

/** 输入框当前值。 */
const inputValue = ref<string>('');

/** 本地校验错误信息，null 表示无错误。 */
const localError = ref<string | null>(null);

/** 防抖定时器句柄。 */
let debounceTimer: ReturnType<typeof setTimeout> | null = null;

// ── 校验 ──────────────────────────────────────────────────────────────

/**
 * 校验基金代码格式：必须为 6 位数字。
 *
 * @param code 输入的基金代码字符串。
 * @returns true 表示格式有效。
 */
function isValidCode(code: string): boolean {
  return code.length === 6 && /^\d{6}$/.test(code);
}

// ── 核心操作 ──────────────────────────────────────────────────────────

/**
 * 校验当前输入并通过则 emit search 事件。
 *
 * 校验失败时设置 localError，不 emit。
 * loading 状态下不执行任何操作。
 */
function tryEmitSearch(): void {
  if (props.loading) {
    return;
  }

  if (!isValidCode(inputValue.value)) {
    localError.value = LABELS.FUND_CODE_INPUT_ERROR;
    return;
  }

  localError.value = null;
  emit('search', inputValue.value);
}

/**
 * 执行搜索：清除防抖定时器，立即调用 tryEmitSearch。
 * 由按钮点击、Enter 键触发，跳过防抖立即执行。
 */
function performSearch(): void {
  // 清除防抖定时器，避免重复触发
  if (debounceTimer !== null) {
    clearTimeout(debounceTimer);
    debounceTimer = null;
  }

  tryEmitSearch();
}

/**
 * 防抖校验与搜索：input 事件 300ms 后自动触发。
 */
function scheduleDebouncedSearch(): void {
  if (debounceTimer !== null) {
    clearTimeout(debounceTimer);
  }

  debounceTimer = setTimeout(() => {
    debounceTimer = null;
    tryEmitSearch();
  }, 300);
}

// ── 事件处理 ──────────────────────────────────────────────────────────

/**
 * 处理 input 事件：过滤非数字字符，清除旧错误，启动防抖。
 */
function onInput(e: Event): void {
  const target = e.target as HTMLInputElement;
  const raw = target.value;

  // 过滤非数字字符
  const filtered = raw.replace(/\D/g, '');
  if (filtered !== raw) {
    target.value = filtered;
  }

  inputValue.value = filtered;
  localError.value = null;

  scheduleDebouncedSearch();
}

/**
 * 处理按钮点击事件。
 */
function onClick(): void {
  performSearch();
}

/**
 * 处理 Enter 键事件。
 */
function onKeyup(e: KeyboardEvent): void {
  if (e.key === 'Enter') {
    performSearch();
  }
}

// ── 生命周期 ──────────────────────────────────────────────────────────

onUnmounted(() => {
  if (debounceTimer !== null) {
    clearTimeout(debounceTimer);
    debounceTimer = null;
  }
});
</script>

<template>
  <div class="w-full">
    <label for="fund-code-input" class="sr-only">{{ LABELS.INPUT_ARIA_LABEL }}</label>

    <div class="flex gap-2">
      <input
        id="fund-code-input"
        type="text"
        inputmode="numeric"
        maxlength="6"
        :placeholder="LABELS.FUND_CODE_PLACEHOLDER"
        :disabled="loading"
        class="flex-1 px-4 py-2.5 text-base border border-gray-300 rounded-lg
               focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
               disabled:bg-gray-100 disabled:cursor-not-allowed
               transition-colors duration-150"
        @input="onInput"
        @keyup="onKeyup"
      />

      <button
        type="button"
        :disabled="loading"
        class="inline-flex items-center justify-center gap-2
               px-6 py-2.5 text-sm font-medium text-white
               bg-blue-600 hover:bg-blue-700 active:bg-blue-800
               rounded-lg transition-colors duration-150
               disabled:bg-blue-400 disabled:cursor-not-allowed
               min-w-[80px]"
        @click="onClick"
      >
        <!-- Spinner -->
        <svg
          v-if="loading"
          class="animate-spin h-4 w-4 text-white/80"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
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
        <span v-if="!loading">{{ LABELS.QUERY_BUTTON }}</span>
      </button>
    </div>

    <!-- 本地校验错误 -->
    <span
      v-if="localError"
      role="alert"
      class="block mt-2 text-sm text-red-600"
    >
      {{ localError }}
    </span>
  </div>
</template>
