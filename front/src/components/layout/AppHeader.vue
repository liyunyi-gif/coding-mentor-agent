<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import { computed } from 'vue'
import { useSessionStore } from '@/stores/session'
import { Code, Stethoscope, Dumbbell, ChartBar } from 'lucide-vue'

const router = useRouter()
const route = useRoute()
const store = useSessionStore()

const tabs = [
  { name: 'chat', label: '聊天', icon: Code, route: '/chat' },
  { name: 'diagnostic', label: '诊断', icon: Stethoscope, route: '/diagnostic' },
  { name: 'practice', label: '练习', icon: Dumbbell, route: '/practice' },
  { name: 'progress', label: '进度', icon: ChartBar, route: '/progress' },
]

const activeTab = computed(() => {
  const path = route.path
  for (const tab of tabs) {
    if (path.startsWith('/' + tab.name)) return tab.name
  }
  return 'chat'
})

function goTab(tab: typeof tabs[0]) {
  router.push(tab.route)
}
</script>

<template>
  <header class="flex items-center gap-4 px-5 py-3 bg-brand-panel border-b border-brand-border">
    <h1 class="text-lg font-semibold text-brand-blue whitespace-nowrap">Python 课程学伴</h1>
    <nav class="flex gap-1">
      <button
        v-for="tab in tabs"
        :key="tab.name"
        @click="goTab(tab)"
        :class="[
          'flex items-center gap-1.5 px-3 py-1.5 rounded text-sm border transition-colors',
          activeTab === tab.name
            ? 'bg-brand-dark text-brand-blue border-brand-blue'
            : 'bg-transparent text-gray-500 border-brand-border hover:bg-brand-dark hover:text-gray-300',
        ]"
      >
        <component :is="tab.icon" :size="14" />
        {{ tab.label }}
      </button>
    </nav>
    <span class="ml-auto text-xs text-gray-600">{{ store.sessionDisplay }}</span>
  </header>
</template>
