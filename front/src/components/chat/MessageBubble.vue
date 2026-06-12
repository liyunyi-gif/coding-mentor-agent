<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'
import type { ChatMessage } from '@/types/api'

const props = defineProps<{ message: ChatMessage }>()

const isMarkdown = computed(() => props.message.role === 'assistant')
const renderedHtml = computed(() => (isMarkdown.value ? marked.parse(props.message.text) as string : ''))

const bubbleClass = computed(() => {
  const base = 'px-4 py-3 rounded-lg max-w-[85%] leading-relaxed text-sm'
  switch (props.message.role) {
    case 'user':
      return `${base} bg-brand-dark text-gray-200 self-end`
    case 'assistant':
      return `${base} bg-brand-card text-gray-300 self-start`
    case 'error':
      return `${base} bg-red-900/40 text-red-400 self-center`
  }
})
</script>

<template>
  <div :class="bubbleClass">
    <div v-if="message.role === 'assistant'" class="markdown-body" v-html="renderedHtml"></div>
    <div v-else class="whitespace-pre-wrap">{{ message.text }}</div>
  </div>
</template>
