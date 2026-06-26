<script setup lang="ts">
import { onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useFundStore } from '@/stores/fund';
import DisclaimerBar from '@/components/DisclaimerBar.vue';
import ErrorAlert from '@/components/ErrorAlert.vue';
import ResultHeader from '@/components/ResultHeader.vue';
import NavGrid from '@/components/NavGrid.vue';
import YieldMetrics from '@/components/YieldMetrics.vue';
import MarketRates from '@/components/MarketRates.vue';
import RefreshButton from '@/components/RefreshButton.vue';

/**
 * FundResult — 计算结果展示页。
 *
 * 从路由参数获取基金代码，自动触发收益计算。
 * 支持三种状态渲染：骨架屏（加载中）、错误提示（失败）、完整结果（成功）。
 */

const route = useRoute();
const store = useFundStore();

/** 当前基金代码（来自路由参数）。 */
const code = route.params.code as string;

onMounted(() => {
  // query ?refresh=1 时无条件重新计算
  if (route.query.refresh === '1') {
    store.refreshCalculation(code);
    return;
  }

  // 没有已有计算结果时自动触发
  if (store.calculation === null) {
    store.refreshCalculation(code);
  }
});

/** 重试：清空错误后重新触发计算。 */
function onRetry(): void {
  store.clearError();
  store.refreshCalculation(code);
}
</script>

<template>
  <div class="max-w-lg mx-auto px-4 py-6 pb-20">
    <h1 class="text-2xl font-bold text-center mb-6 text-gray-900">
      计算结果
    </h1>

    <!-- ═══ 加载态：骨架屏 ═══ -->
    <div v-if="store.loading && store.calculation === null" class="space-y-4">
      <!-- 模拟 ResultHeader -->
      <div class="bg-white rounded-lg p-5 space-y-3">
        <div class="h-6 w-3/4 bg-gray-200 rounded animate-pulse" />
        <div class="h-4 w-1/2 bg-gray-200 rounded animate-pulse" />
      </div>

      <!-- 模拟 NavGrid + YieldMetrics -->
      <div class="bg-gray-50 rounded-lg p-4">
        <div class="h-32 w-full bg-gray-200 rounded animate-pulse" />
      </div>

      <!-- 模拟 MarketRates -->
      <div class="bg-gray-50 rounded-lg p-4">
        <div class="h-20 w-full bg-gray-200 rounded animate-pulse" />
      </div>
    </div>

    <!-- ═══ 错误态 ═══ -->
    <ErrorAlert
      v-else-if="store.error"
      :message="store.error"
      @retry="onRetry"
    />

    <!-- ═══ 结果态 ═══ -->
    <template v-else-if="store.calculation?.status === 'completed'">
      <!-- 基金名称 + 日期 -->
      <ResultHeader
        :fund-name="store.calculation.fund_name ?? store.fundInfo?.name"
        :fund-code="store.calculation.fund_code ?? store.fundInfo?.fund_code"
        :data-date="store.calculation.data_date"
        :is-trading-day="store.calculation.is_trading_day"
      />

      <!-- 净值 + 日涨跌 -->
      <NavGrid
        :nav="store.calculation.nav"
        :daily-change-pct="store.calculation.daily_change_pct"
      />

      <!-- 收益指标 -->
      <YieldMetrics
        :seven-day-yield="store.calculation.seven_day_annual_yield"
        :wanfen-income="store.calculation.wanfen_income"
        :one-month-return="store.calculation.one_month_return"
        :three-month-max-drawdown="store.calculation.three_month_max_drawdown"
      />

      <!-- 市场利率 -->
      <MarketRates
        :ten-year-treasury="store.calculation.ten_year_treasury"
        :credit-spread-aa-plus="store.calculation.credit_spread_aa_plus"
      />

      <!-- 刷新计算按钮 -->
      <RefreshButton
        :loading="store.loading"
        @refresh="store.refreshCalculation(code)"
      />
    </template>

    <!-- 免责声明 -->
    <DisclaimerBar />
  </div>
</template>
