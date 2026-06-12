<script setup lang="ts">
import { ref } from 'vue'
import { useSessionStore } from '@/stores/session'
import { getNextDiagnostic, submitDiagnosticAnswer } from '@/api/diagnostics'
import type { DiagnosticQuestion } from '@/types/api'
import QuestionCard from './QuestionCard.vue'
import { SkipForward } from 'lucide-vue'

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
  selectedIndex.value = null; isCorrect.value = null; feedbackMessage.value = ''; feedbackType.value = ''
}

async function handleSelect(index: number) {
  if (!currentQuestion.value || selectedIndex.value !== null) return
  selectedIndex.value = index
  try {
    const data = await submitDiagnosticAnswer(currentQuestion.value.diagnostic_id, {
      answer_index: index, concept_id: currentQuestion.value.concept_id,
      question: currentQuestion.value.question, difficulty: currentQuestion.value.difficulty,
    })
    isCorrect.value = data.correct; feedbackMessage.value = data.message; feedbackType.value = data.correct ? 'success' : 'fail'
  } catch (err) {
    feedbackMessage.value = `提交失败: ${err instanceof Error ? err.message : '未知错误'}`; feedbackType.value = 'fail'
  }
}

function skip() { loadQuestion() }

loadQuestion()
</script>

<template>
  <div class="flex-1 min-h-0 overflow-y-auto p-6 bg-gray-50">
    <div class="w-full">
      <h2 class="text-lg font-semibold text-gray-800 mb-1">诊断测评</h2>
      <p class="text-sm text-gray-500 mb-4">完成诊断题，系统将评估你的 Python 水平。</p>

      <div v-if="isCompleted" class="bg-green-50 border border-green-200 rounded-xl p-6 text-green-700">
        <p class="font-semibold text-lg">诊断测评已完成！</p>
        <p class="text-sm mt-1">共回答了 {{ totalAnswered }} 题，你现在可以开始练习了。</p>
      </div>

      <QuestionCard
        v-else-if="currentQuestion" :question="currentQuestion"
        :selected-index="selectedIndex" :is-correct="isCorrect"
        :disabled="selectedIndex !== null" @select="handleSelect"
      />

      <!-- Feedback -->
      <div v-if="feedbackMessage" :class="[
        'p-3 rounded-lg text-sm mb-3',
        feedbackType === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-600',
      ]">{{ feedbackMessage }}</div>

      <!-- Buttons -->
      <div class="flex gap-3" v-if="!isCompleted">
        <button @click="loadQuestion" :disabled="isLoading"
          class="px-5 py-2.5 bg-blue-500 text-white rounded-lg text-sm font-medium hover:bg-blue-600 disabled:opacity-50 transition-colors">
          {{ isLoading ? '加载中...' : currentQuestion ? '下一题' : '开始诊断' }}
        </button>
        <button v-if="currentQuestion && selectedIndex === null" @click="skip"
          class="flex items-center gap-1 px-4 py-2.5 text-sm text-gray-500 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
          <SkipForward :size="14" /> 跳过
        </button>
      </div>
    </div>
  </div>
</template>
