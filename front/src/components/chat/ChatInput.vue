<script setup lang="ts">
import { ref } from 'vue'
import { Send } from 'lucide-vue'

const emit = defineEmits<{ send: [message: string] }>()
const props = defineProps<{ disabled?: boolean }>()

const input = ref('')

function handleSend() {
  const text = input.value.trim()
  if (!text || props.disabled) return
  emit('send', text)
  input.value = ''
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}
</script>

<template>
  <div class="flex gap-2">
    <input
      v-model="input"
      type="text"
      :disabled="disabled"
      placeholder="输入消息，询问 Python 问题..."
      class="flex-1 px-3 py-2.5 bg-brand-darker border border-brand-border rounded text-gray-200 text-sm outline-none focus:border-brand-blue transition-colors disabled:opacity-50"
      @keydown="handleKeydown"
    />
    <button
      :disabled="disabled || !input.trim()"
      @click="handleSend"
      class="flex items-center gap-1 px-4 py-2.5 bg-brand-dark text-brand-blue border border-brand-blue rounded text-sm hover:bg-brand-blue/20 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
    >
      <Send :size="14" />
      发送
    </button>
  </div>
</template>
