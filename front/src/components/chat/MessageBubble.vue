<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'
import type { ChatMessage } from '@/types/api'
import { Bot, User } from 'lucide-vue'

const props = defineProps<{ message: ChatMessage }>()
const isMarkdown = computed(() => props.message.role === 'assistant')
const html = computed(() => isMarkdown.value ? (marked.parse(props.message.text) as string) : '')
</script>

<template>
  <!-- Error -->
  <div v-if="message.role === 'error'" class="flex justify-center py-2">
    <span class="px-4 py-1.5 bg-red-50 text-red-600 rounded-lg text-xs">{{ message.text }}</span>
  </div>

  <!-- Assistant (left, white bubble) -->
  <div v-else-if="message.role === 'assistant'" class="flex gap-3 max-w-[85%] self-start">
    <div class="w-7 h-7 rounded-full bg-gray-100 flex items-center justify-center shrink-0 mt-0.5">
      <Bot :size="14" class="text-gray-500" />
    </div>
    <div class="markdown-body text-sm leading-relaxed text-gray-700" v-html="html"></div>
  </div>

  <!-- User (right, blue bubble) -->
  <div v-else class="max-w-[75%] self-end px-4 py-2.5 bg-blue-50 text-gray-800 rounded-2xl rounded-br-md text-sm leading-relaxed whitespace-pre-wrap break-words">
    <div>{{ message.text }}</div>
  </div>
</template>
