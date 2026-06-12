<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import type { ChatMessage } from '@/types/api'
import MessageBubble from './MessageBubble.vue'
import { Bot } from 'lucide-vue'

const props = defineProps<{ messages: ChatMessage[] }>()
const containerRef = ref<HTMLDivElement>()

function scrollToBottom() {
  nextTick(() => {
    if (containerRef.value) containerRef.value.scrollTop = containerRef.value.scrollHeight
  })
}
watch(() => props.messages.length, scrollToBottom)
</script>

<template>
  <div ref="containerRef" class="flex-1 overflow-y-auto px-4 py-4 flex flex-col gap-4 bg-white">
    <div v-if="messages.length === 0" class="flex flex-col items-center justify-center h-full text-gray-400 gap-3">
      <div class="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center">
        <Bot :size="24" class="text-gray-400" />
      </div>
      <p class="text-sm">你的 AI Python 导师已就绪</p>
    </div>
    <MessageBubble v-for="msg in messages" :key="msg.id" :message="msg" />
  </div>
</template>
