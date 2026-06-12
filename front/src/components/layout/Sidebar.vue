<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus, MessageSquare, PanelLeftClose, PanelLeftOpen } from 'lucide-vue'
import { exportData } from '@/api/data'

interface SessionInfo {
  id: string
  status: string
  started_at: string
}

const props = defineProps<{ collapsed: boolean }>()
const emit = defineEmits<{ 'update:collapsed': [v: boolean]; 'newChat': []; 'selectSession': [id: string] }>()

const sessions = ref<SessionInfo[]>([])

async function loadSessions() {
  try {
    const data = await exportData()
    sessions.value = (data.sessions || []).slice(-20).reverse()
  } catch { /* ignore */ }
}

function formatDate(iso: string) {
  const d = new Date(iso)
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2, '0')}`
}

onMounted(loadSessions)
</script>

<template>
  <aside
    :class="[
      'flex flex-col border-r border-gray-200 bg-gray-50 transition-all duration-200 shrink-0',
      collapsed ? 'w-0 overflow-hidden border-0' : 'w-64',
    ]"
  >
    <div class="p-3">
      <button
        @click="emit('newChat')"
        class="flex items-center gap-2 w-full px-3 py-2 text-sm text-gray-700 bg-white border border-gray-200 rounded-lg hover:bg-gray-100 transition-colors"
      >
        <Plus :size="16" />新对话
      </button>
    </div>

    <div class="flex-1 overflow-y-auto px-2 pb-2">
      <p class="px-2 py-1 text-xs text-gray-400 font-medium">历史对话</p>
      <div v-if="sessions.length === 0" class="px-2 py-3 text-xs text-gray-400">暂无</div>
      <button
        v-for="s in sessions"
        :key="s.id"
        @click="emit('selectSession', s.id)"
        class="flex items-center gap-2 w-full px-3 py-2 text-left text-sm text-gray-600 rounded-lg hover:bg-gray-200/70 transition-colors truncate"
      >
        <MessageSquare :size="14" class="shrink-0 text-gray-400" />
        <span class="truncate">{{ s.id.slice(0, 14) }}...</span>
        <span class="text-xs text-gray-400 ml-auto shrink-0">{{ formatDate(s.started_at) }}</span>
      </button>
    </div>
  </aside>

  <button
    @click="emit('update:collapsed', !collapsed)"
    class="absolute left-0 top-1/2 -translate-y-1/2 z-10 p-1 bg-white border border-gray-200 rounded-r-md shadow-sm hover:bg-gray-50 transition-colors"
    :style="{ left: collapsed ? '0' : '256px' }"
  >
    <PanelLeftOpen v-if="collapsed" :size="16" class="text-gray-500" />
    <PanelLeftClose v-else :size="16" class="text-gray-500" />
  </button>
</template>
