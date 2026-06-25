import { createRouter, createWebHashHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'FundInput',
    component: () => import('@/pages/FundInput.vue'),
  },
  {
    path: '/fund/:code',
    name: 'FundResult',
    component: () => import('@/pages/FundResult.vue'),
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

export default router
