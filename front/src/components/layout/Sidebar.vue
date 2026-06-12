<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus, MessageSquare, X } from 'lucide-vue'
import { exportData } from '@/api/data'
import { deleteSession } from '@/api/sessions'
import { useSessionStore } from '@/stores/session'

interface SessionInfo { id: string; status: string; started_at: string }

const props = defineProps<{ collapsed: boolean }>()
const emit = defineEmits<{ 'update:collapsed': [v: boolean]; 'selectSession': [id: string] }>()

const store = useSessionStore()
const sessions = ref<SessionInfo[]>([])

async function loadSessions() {
  try {
    const data = await exportData()
    sessions.value = (data.sessions || []).slice(-30).reverse()
  } catch { /* ignore */ }
}

function formatDate(iso: string) {
  const d = new Date(iso)
  return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

async function handleNewChat() {
  await store.newChat()
  await loadSessions()
  emit('selectSession', store.sessionId!)
}

function handleSelect(id: string) {
  store.loadSession(id).then(() => {
    emit('selectSession', id)
  })
}

async function handleDelete(e: Event, id: string) {
  e.stopPropagation()
  if (!confirm('确认删除此对话？所有消息将被永久删除。')) return
  try {
    await deleteSession(id)
    store.removeSessionName(id)
    // If deleting current session, clear
    if (store.sessionId === id) {
      store.clearMessages()
      store.sessionId = null
    }
    await loadSessions()
  } catch { /* ignore */ }
}

onMounted(loadSessions)

defineExpose({ loadSessions })
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
        @click="handleNewChat"
        class="flex items-center gap-2 w-full px-3 py-2 text-sm text-gray-700 bg-white border border-gray-200 rounded-lg hover:bg-gray-100 transition-colors"
      >
        <Plus :size="16" />新对话
      </button>
    </div>

    <div class="flex-1 overflow-y-auto px-2 pb-2">
      <p class="px-2 py-1 text-xs text-gray-400 font-medium">历史对话</p>
      <div v-if="sessions.length === 0" class="px-2 py-3 text-xs text-gray-400">暂无</div>
      <div
        v-for="s in sessions" :key="s.id"
        @click="handleSelect(s.id)"
        :class="[
          'group flex items-center gap-2 w-full px-3 py-2 text-left text-sm rounded-lg transition-colors cursor-pointer',
          store.sessionId === s.id
            ? 'bg-gray-200 text-gray-900 font-medium'
            : 'text-gray-600 hover:bg-gray-200/70',
        ]"
      >
        <MessageSquare :size="14" class="shrink-0 text-gray-400" />
        <span class="truncate flex-1">{{ store.getSessionName(s.id) }}</span>
        <span class="text-xs text-gray-400 shrink-0">{{ formatDate(s.started_at) }}</span>
        <button
          @click="(e) => handleDelete(e, s.id)"
          class="shrink-0 p-1 rounded-full bg-gray-200 text-gray-400 hover:bg-gray-300 hover:text-gray-600 transition-colors ml-1"
          title="删除"
        >
          <X :size="12" />
        </button>
      </div>
    </div>
  </aside>
</template>
