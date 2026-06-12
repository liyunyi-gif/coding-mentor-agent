<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import type { ChatMessage } from '@/types/api'
import MessageBubble from './MessageBubble.vue'
import { Bot } from 'lucide-vue'

const props = defineProps<{ messages: ChatMessage[] }>()

const containerRef = ref<HTMLDivElement>()

function scrollToBottom() {
  nextTick(() => {
    if (containerRef.value) {
      containerRef.value.scrollTop = containerRef.value.scrollHeight
    }
  })
}

watch(() => props.messages.length, scrollToBottom)
</script>

<template>
  <div ref="containerRef" class="flex-1 overflow-y-auto px-4 py-3 flex flex-col gap-3">
    <div v-if="messages.length === 0" class="flex flex-col items-center justify-center h-full text-gray-500 gap-3">
      <Bot :size="40" class="opacity-50" />
      <p class="text-sm">你的 AI Python 导师已就绪，开始提问吧！</p>
    </div>
    <MessageBubble v-for="msg in messages" :key="msg.id" :message="msg" />
  </div>
</template>
