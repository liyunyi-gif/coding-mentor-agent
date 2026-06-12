<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useSessionStore } from '@/stores/session'
import { Code, Stethoscope, Dumbbell, ChartBar, PanelLeft } from 'lucide-vue'

defineProps<{ sidebarCollapsed: boolean }>()
const emit = defineEmits<{ 'toggleSidebar': [] }>()

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
  const p = route.path
  for (const t of tabs) if (p.startsWith('/' + t.name)) return t.name
  return 'chat'
})
</script>

<template>
  <header class="w-full flex items-center gap-3 px-4 py-2.5 bg-white border-b border-gray-200 shrink-0">
    <button @click="emit('toggleSidebar')" class="p-1.5 rounded-md hover:bg-gray-100 text-gray-500 transition-colors" title="侧栏">
      <PanelLeft :size="18" />
    </button>
    <h1 class="text-base font-semibold text-gray-800 whitespace-nowrap">Python 学伴</h1>
    <nav class="flex gap-0.5 ml-2">
      <button
        v-for="t in tabs" :key="t.name" @click="router.push(t.route)"
        :class="[
          'flex items-center gap-1 px-3 py-1.5 rounded-md text-sm transition-colors',
          activeTab === t.name ? 'bg-gray-100 text-gray-900 font-medium' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50',
        ]"
      >
        <component :is="t.icon" :size="14" />
        {{ t.label }}
      </button>
    </nav>
    <span class="ml-auto text-xs text-gray-400">{{ store.sessionDisplay }}</span>
  </header>
</template>
