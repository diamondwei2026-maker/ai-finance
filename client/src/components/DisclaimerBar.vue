<script setup lang="ts">
import { DISCLAIMER } from '@/locales/zh-CN';

/**
 * DisclaimerBar — 全局复用免责声明横幅。
 *
 * 固定在视口底部，半透明毛玻璃效果。
 * 使用该组件的页面需确保主体有足够的 padding-bottom（推荐 pb-16 ~ pb-20），
 * 避免底部内容被遮挡。
 */
</script>

<template>
  <footer
    class="fixed bottom-0 left-0 right-0 z-10
           bg-gray-100/90 backdrop-blur-sm
           border-t border-gray-200
           px-4 py-3 text-center"
  >
    <p class="text-xs text-gray-500 leading-relaxed max-w-2xl mx-auto">
      {{ DISCLAIMER.TEXT }}
    </p>
  </footer>
</template>
