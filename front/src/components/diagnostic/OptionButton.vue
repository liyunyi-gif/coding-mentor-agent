<script setup lang="ts">
defineProps<{
  label: string
  index: number
  state?: 'normal' | 'correct' | 'wrong'
  disabled?: boolean
}>()

const emit = defineEmits<{ select: [index: number] }>()
</script>

<template>
  <button
    :disabled="disabled"
    @click="emit('select', index)"
    :class="[
      'block w-full text-left px-4 py-2.5 my-1.5 rounded border text-sm transition-colors',
      state === 'correct'
        ? 'bg-green-900/30 border-green-600 text-green-400'
        : state === 'wrong'
          ? 'bg-red-900/30 border-red-600 text-red-400'
          : 'bg-[#2a2a3a] border-brand-border text-gray-200 hover:bg-brand-dark hover:border-brand-blue',
      disabled ? 'cursor-not-allowed' : 'cursor-pointer',
    ]"
  >
    {{ String.fromCharCode(65 + index) }}. {{ label }}
  </button>
</template>
