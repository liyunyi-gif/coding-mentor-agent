<script setup lang="ts">
import type { DiagnosticQuestion } from '@/types/api'
import OptionButton from './OptionButton.vue'

defineProps<{
  question: DiagnosticQuestion
  selectedIndex: number | null
  isCorrect: boolean | null
  disabled: boolean
}>()

const emit = defineEmits<{ select: [index: number] }>()
</script>

<template>
  <div class="bg-brand-card p-5 rounded-lg mb-4">
    <h3 class="text-brand-blue mb-3 text-sm">
      第 {{ question.total_answered + 1 }} 题 — {{ question.concept_name }}
    </h3>
    <p class="mb-3 text-[15px]">{{ question.question }}</p>
    <OptionButton
      v-for="(opt, idx) in question.options"
      :key="idx"
      :label="opt"
      :index="idx"
      :disabled="disabled"
      :state="
        selectedIndex === idx
          ? isCorrect === true
            ? 'correct'
            : isCorrect === false
              ? 'wrong'
              : undefined
          : undefined
      "
      @select="emit('select', $event)"
    />
  </div>
</template>
