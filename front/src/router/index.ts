import { createRouter, createWebHashHistory } from 'vue-router'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', redirect: '/chat' },
    {
      path: '/chat',
      name: 'chat',
      component: () => import('@/components/chat/ChatPanel.vue'),
    },
    {
      path: '/diagnostic',
      name: 'diagnostic',
      component: () => import('@/components/diagnostic/DiagnosticPanel.vue'),
    },
    {
      path: '/practice',
      name: 'practice',
      component: () => import('@/components/practice/PracticePanel.vue'),
    },
    {
      path: '/progress',
      name: 'progress',
      component: () => import('@/components/progress/ProgressPanel.vue'),
    },
  ],
})

export default router
