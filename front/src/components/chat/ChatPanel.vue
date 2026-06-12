<script setup lang="ts">
import { ref } from 'vue'
import { useSessionStore } from '@/stores/session'
import CodeEditor from './CodeEditor.vue'
import MessageList from './MessageList.vue'
import ChatInput from './ChatInput.vue'

const store = useSessionStore()
const code = ref('')
const editorRef = ref<InstanceType<typeof CodeEditor>>()

async function handleSend(message: string) {
  const codeValue = code.value
  await store.sendMessage(message, codeValue || undefined)
  code.value = ''
  editorRef.value?.clear()
}
</script>

<template>
  <div class="flex flex-col h-full">
    <MessageList :messages="store.messages" />
    <div class="px-4 py-3 bg-brand-panel border-t border-brand-border space-y-2">
      <CodeEditor ref="editorRef" v-model="code" />
      <ChatInput :disabled="store.isLoading" @send="handleSend" />
    </div>
  </div>
</template>
