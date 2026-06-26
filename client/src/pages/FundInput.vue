<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useFundStore } from '@/stores/fund';
import { LABELS } from '@/locales/zh-CN';
import SearchBar from '@/components/SearchBar.vue';
import FundPreview from '@/components/FundPreview.vue';
import ErrorAlert from '@/components/ErrorAlert.vue';
import DisclaimerBar from '@/components/DisclaimerBar.vue';

const router = useRouter();
const store = useFundStore();

/** 记录最后一次搜索的基金代码，供重试使用。 */
const lastCode = ref<string | null>(null);

/**
 * 处理基金代码搜索。
 *
 * 调用 Store 查询基金信息。
 * Store 内部已处理三种错误码（40001/40002/40003）的文案映射。
 *
 * @param code 6 位基金代码。
 */
async function onSearch(code: string): Promise<void> {
  lastCode.value = code;
  await store.fetchFundInfo(code);
}

/**
 * 重试：清空错误后使用上次输入的代码重新查询。
 *
 * 仅在 lastCode 存在时执行重试，防止跨页面错误残留导致的空重试。
 */
function onRetry(): void {
  if (lastCode.value) {
    store.clearError();
    store.fetchFundInfo(lastCode.value);
  }
}

/**
 * 处理用户确认查看基金详情。
 *
 * 跳转到 FundResult 页面，携带基金代码路由参数。
 *
 * @param code 6 位基金代码。
 */
function onConfirm(code: string): void {
  router.push({ name: 'FundResult', params: { code } });
}
</script>

<template>
  <div class="max-w-2xl mx-auto px-4 py-8 pb-20">
    <!-- 页面标题 -->
    <h1 class="text-2xl font-bold text-center mb-2 text-gray-900">
      {{ LABELS.PAGE_TITLE }}
    </h1>
    <p class="text-gray-500 text-center mb-6">
      {{ LABELS.PAGE_SUBTITLE }}
    </p>

    <!-- 搜索栏 -->
    <SearchBar :loading="store.loading" @search="onSearch" />

    <!-- 全局错误提示（API 返回的业务错误） -->
    <ErrorAlert
      v-if="store.error"
      :message="store.error"
      @retry="onRetry"
    />

    <!-- 基金预览卡片（查询成功后展示） -->
    <FundPreview :fund-info="store.fundInfo" @confirm="onConfirm" />

    <!-- 免责声明 -->
    <DisclaimerBar />
  </div>
</template>
