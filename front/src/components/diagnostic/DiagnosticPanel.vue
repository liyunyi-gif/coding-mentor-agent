<script setup lang="ts">
import { ref } from 'vue'
import { useSessionStore } from '@/stores/session'
import { getNextDiagnostic, submitDiagnosticAnswer } from '@/api/diagnostics'
import { Stethoscope } from 'lucide-vue'
import type { DiagnosticQuestion } from '@/types/api'
import QuestionCard from './QuestionCard.vue'

const store = useSessionStore()

const currentQuestion = ref<DiagnosticQuestion | null>(null)
const isCompleted = ref(false)
const totalAnswered = ref(0)
const selectedIndex = ref<number | null>(null)
const isCorrect = ref<boolean | null>(null)
const feedbackMessage = ref('')
const feedbackType = ref<'success' | 'fail' | ''>('')
const isLoading = ref(false)

async function loadQuestion() {
  const sid = store.sessionId || (await store.initSession())
  isLoading.value = true
  try {
    const data = await getNextDiagnostic(sid)
    if ('completed' in data && data.completed) {
      isCompleted.value = true
      totalAnswered.value = data.total_answered
      currentQuestion.value = null
    } else {
      currentQuestion.value = data as DiagnosticQuestion
      isCompleted.value = false
      resetSelection()
    }
  } finally {
    isLoading.value = false
  }
}

function resetSelection() {
  selectedIndex.value = null
  isCorrect.value = null
  feedbackMessage.value = ''
  feedbackType.value = ''
}

async function handleSelect(index: number) {
  if (!currentQuestion.value || selectedIndex.value !== null) return
  selectedIndex.value = index

  try {
    const data = await submitDiagnosticAnswer(currentQuestion.value.diagnostic_id, {
      answer_index: index,
      concept_id: currentQuestion.value.concept_id,
      question: currentQuestion.value.question,
      difficulty: currentQuestion.value.difficulty,
    })
    isCorrect.value = data.correct
    feedbackMessage.value = data.message
    feedbackType.value = data.correct ? 'success' : 'fail'
  } catch (err) {
    feedbackMessage.value = `提交失败: ${err instanceof Error ? err.message : '未知错误'}`
    feedbackType.value = 'fail'
  }
}

loadQuestion()
</script>

<template>
  <div class="flex-1 overflow-y-auto p-5">
    <h2 class="text-brand-blue text-lg mb-1">诊断测评</h2>
    <p class="text-gray-500 text-sm mb-4">完成诊断题，系统将评估你的 Python 水平并推荐学习起点。</p>

    <div v-if="isCompleted" class="bg-green-900/20 border border-green-800 rounded-lg p-5 text-green-400">
      <p class="font-semibold">诊断测评已完成！</p>
      <p class="text-sm mt-1">共回答了 {{ totalAnswered }} 题。你现在可以开始练习了。</p>
    </div>

    <QuestionCard
      v-else-if="currentQuestion"
      :question="currentQuestion"
      :selected-index="selectedIndex"
      :is-correct="isCorrect"
      :disabled="selectedIndex !== null"
      @select="handleSelect"
    />

    <div
      v-if="feedbackMessage"
      :class="[
        'p-3 rounded text-sm mt-2',
        feedbackType === 'success' ? 'bg-green-900/20 text-green-400' : 'bg-red-900/20 text-red-400',
      ]"
    >
      {{ feedbackMessage }}
    </div>

    <div class="flex gap-3 mt-4">
      <button
        v-if="!isCompleted"
        @click="loadQuestion"
        :disabled="isLoading"
        class="px-5 py-2.5 bg-brand-dark text-brand-blue border border-brand-blue rounded text-sm hover:bg-brand-blue/20 transition-colors disabled:opacity-50"
      >
        {{ isLoading ? '加载中...' : currentQuestion ? '下一题' : '开始诊断' }}
      </button>
    </div>

    <div v-if="!currentQuestion && !isCompleted && !isLoading" class="flex items-center justify-center h-40 text-gray-500">
      <Stethoscope :size="40" class="opacity-50" />
    </div>
  </div>
</template>
