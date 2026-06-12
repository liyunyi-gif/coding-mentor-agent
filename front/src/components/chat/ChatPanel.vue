<script setup lang="ts">
import { ref, onUnmounted } from 'vue'
import { useSessionStore } from '@/stores/session'
import CodeEditor from './CodeEditor.vue'
import MessageList from './MessageList.vue'
import { ArrowUp, Code2, MessageCircle } from 'lucide-vue'
import { sendMessage } from '@/api/messages'

const store = useSessionStore()
const input = ref('')
const code = ref('')
const showCode = ref(false)
const editorRef = ref<InstanceType<typeof CodeEditor>>()
let sseSource: EventSource | null = null

onUnmounted(() => { sseSource?.close() })

async function handleSend() {
  const text = input.value.trim()
  if (!text && !code.value) return

  const sid = store.sessionId!
  store.isLoading = true

  // Display user message
  const displayText = code.value ? `${text || '请看这段代码'}\n\n\`\`\`python\n${code.value}\n\`\`\`` : text
  store.addMessage('user', displayText)
  input.value = ''

  // Add streaming placeholder
  store.addMessage('assistant', '')
  const streamMsg = store.messages[store.messages.length - 1]

  // Connect SSE before sending
  const turnId: string | null = null
  sseSource = new EventSource(`/api/sessions/${sid}/events`)

  sseSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      if (data.type === 'message_delta' && streamMsg.role === 'assistant') {
        streamMsg.text = data.delta
      } else if (data.type === 'done') {
        sseSource?.close()
        sseSource = null
      }
    } catch { /* ignore parse errors */ }
  }

  sseSource.onerror = () => {
    // Fallback: SSE error, close and wait for POST response
    sseSource?.close()
    sseSource = null
  }

  // Send message (this triggers SSE events)
  try {
    const body: { message: string; code?: string } = { message: text || '请看这段代码' }
    if (code.value) body.code = code.value
    const data = await sendMessage(sid, body)
    // Update streaming message with final text if SSE didn't do it
    if (streamMsg.role === 'assistant' && !streamMsg.text) {
      streamMsg.text = data.assistant_message
    }
  } catch (err) {
    if (streamMsg.role === 'assistant' && !streamMsg.text) {
      streamMsg.role = 'error'
      streamMsg.text = `错误: ${err instanceof Error ? err.message : '未知错误'}`
    }
  } finally {
    store.isLoading = false
    code.value = ''
    editorRef.value?.clear()
    sseSource?.close()
    sseSource = null
  }
}
</script>

<template>
  <div class="flex flex-col flex-1 min-h-0 bg-white">
    <MessageList :messages="store.messages" />
    <div class="px-4 py-3 border-t border-gray-100 bg-white">
      <div v-if="showCode" class="mb-2">
        <CodeEditor ref="editorRef" v-model="code" />
      </div>
      <div class="flex items-center gap-2">
        <button
          @click="showCode = !showCode"
          :class="[
            'flex items-center gap-1.5 px-3 py-2 rounded-lg border transition-colors shrink-0 text-xs font-medium',
            showCode ? 'bg-gray-100 border-gray-300 text-gray-700' : 'bg-white border-gray-200 text-gray-500 hover:bg-gray-50',
          ]"
          :title="showCode ? '切换到消息输入' : '切换到代码输入'"
        >
          <component :is="showCode ? MessageCircle : Code2" :size="16" />
          <span v-if="showCode">点击切换聊天框</span>
          <span v-else>点击切换代码框</span>
        </button>
        <input
          v-model="input" :disabled="store.isLoading"
          :placeholder="showCode ? '描述你的代码意图 (Enter 发送)' : '输入消息，询问 Python 问题 (Enter 发送)'"
          class="flex-1 px-3 py-2.5 bg-white border border-gray-200 rounded-xl text-sm text-gray-800 placeholder-gray-400 outline-none focus:border-blue-400 transition-colors disabled:opacity-50"
          @keydown.enter.exact.prevent="handleSend"
        />
        <button
          :disabled="store.isLoading || (!input.trim() && !code)"
          @click="handleSend"
          class="p-2 rounded-lg bg-blue-500 text-white hover:bg-blue-600 disabled:opacity-40 transition-colors shrink-0"
        >
          <ArrowUp :size="16" />
        </button>
      </div>
    </div>
  </div>
</template>
