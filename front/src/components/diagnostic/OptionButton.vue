<script setup lang="ts">
defineProps<{ label: string; index: number; state?: 'normal' | 'correct' | 'wrong'; disabled?: boolean }>()
const emit = defineEmits<{ select: [index: number] }>()
</script>

<template>
  <button
    :disabled="disabled"
    @click="emit('select', index)"
    :class="[
      'block w-full text-left px-4 py-2.5 my-1 rounded-lg border text-sm transition-colors',
      state === 'correct' ? 'bg-green-50 border-green-300 text-green-700' :
      state === 'wrong' ? 'bg-red-50 border-red-300 text-red-600' :
      'bg-white border-gray-200 text-gray-700 hover:border-blue-300 hover:bg-blue-50',
      disabled ? 'cursor-not-allowed' : 'cursor-pointer',
    ]"
  >
    {{ String.fromCharCode(65 + index) }}. {{ label }}
  </button>
</template>
