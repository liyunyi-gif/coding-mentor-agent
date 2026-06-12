<script setup lang="ts">
import type { DiagnosticQuestion } from '@/types/api'
import OptionButton from './OptionButton.vue'

defineProps<{ question: DiagnosticQuestion; selectedIndex: number | null; isCorrect: boolean | null; disabled: boolean }>()
const emit = defineEmits<{ select: [index: number] }>()
</script>

<template>
  <div class="bg-white border border-gray-200 p-5 rounded-xl mb-4">
    <span class="inline-block px-2 py-0.5 text-xs rounded-full bg-blue-50 text-blue-600 mb-2">{{ question.concept_name }}</span>
    <h3 class="text-sm font-medium text-gray-500 mb-3">第 {{ question.total_answered + 1 }} 题</h3>
    <p class="mb-3 text-gray-800">{{ question.question }}</p>
    <OptionButton
      v-for="(opt, idx) in question.options" :key="idx" :label="opt" :index="idx" :disabled="disabled"
      :state="selectedIndex === idx ? (isCorrect === true ? 'correct' : isCorrect === false ? 'wrong' : undefined) : undefined"
      @select="emit('select', $event)"
    />
  </div>
</template>
