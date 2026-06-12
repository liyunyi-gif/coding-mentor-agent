<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useSessionStore } from '@/stores/session'
import { requestPractice } from '@/api/practice'
import { getProgress } from '@/api/progress'
import { marked } from 'marked'
import type { Exercise } from '@/types/api'
import { Dumbbell, Lock } from 'lucide-vue'

const store = useSessionStore()
const exercise = ref<Exercise | null>(null)
const isLocked = ref(false)
const lockMessage = ref('')
const statusMessage = ref('')
const isLoading = ref(false)
const btnLabel = ref('请求练习')

async function checkAvailability() {
  try {
    const data = await getProgress()
    if (data.practice_state === 'available_after_explicit_request') {
      isLocked.value = false
      statusMessage.value = '诊断已完成，可以开始练习！'
    } else if (data.diagnostic_state === 'active') {
      isLocked.value = true
      lockMessage.value = '诊断进行中，完成诊断后可解锁练习。'
      statusMessage.value = ''
    } else {
      isLocked.value = true
      lockMessage.value = '请先完成诊断测评。'
      statusMessage.value = ''
    }
  } catch (err) {
    console.error('Practice check failed:', err)
  }
}

async function handleRequestPractice() {
  const sid = store.sessionId || (await store.initSession())
  isLoading.value = true
  try {
    const data = await requestPractice(sid)
    if (data.kind === 'practice_locked') {
      isLocked.value = true
      lockMessage.value = data.message
      exercise.value = null
    } else {
      isLocked.value = false
      exercise.value = data.exercise
      statusMessage.value = `${data.message} 切换到聊天面板，在代码编辑器中编写代码，然后发送消息提交。`
      btnLabel.value = '换一题'
    }
  } catch (err) {
    lockMessage.value = `请求练习失败: ${err instanceof Error ? err.message : '未知错误'}`
  } finally {
    isLoading.value = false
  }
}

function renderMarkdown(text: string): string {
  return marked.parse(text) as string
}

onMounted(checkAvailability)
</script>

<template>
  <div class="flex-1 overflow-y-auto p-5">
    <h2 class="text-brand-blue text-lg mb-1">练习</h2>
    <p class="text-gray-500 text-sm mb-4">完成诊断后可解锁练习。</p>

    <!-- Locked state -->
    <div v-if="isLocked" class="bg-brand-card p-4 rounded-lg mb-3 flex items-center gap-3">
      <Lock :size="18" class="text-red-400 shrink-0" />
      <p class="text-red-400 text-sm">{{ lockMessage }}</p>
    </div>

    <!-- Unlocked state -->
    <div v-if="statusMessage && !isLocked" class="bg-green-900/20 p-4 rounded-lg mb-3">
      <p class="text-green-400 text-sm">{{ statusMessage }}</p>
    </div>

    <!-- Exercise card -->
    <div v-if="exercise" class="bg-brand-card p-5 rounded-lg mb-3">
      <h3 class="text-brand-blue font-semibold mb-3">{{ exercise.title }}</h3>
      <div class="markdown-body text-sm text-gray-300 mb-4" v-html="renderMarkdown(exercise.prompt_md)"></div>
      <div v-if="exercise.acceptance_checklist?.length" class="border-t border-brand-border pt-3">
        <h4 class="text-sm text-gray-400 mb-2">验收标准</h4>
        <ul class="list-disc list-inside text-sm text-gray-400 space-y-1">
          <li v-for="item in exercise.acceptance_checklist" :key="item">{{ item }}</li>
        </ul>
      </div>
    </div>

    <!-- Request button -->
    <button
      v-if="!isLocked"
      @click="handleRequestPractice"
      :disabled="isLoading"
      class="px-5 py-2.5 bg-brand-dark text-brand-blue border border-brand-blue rounded text-sm hover:bg-brand-blue/20 transition-colors disabled:opacity-50"
    >
      {{ isLoading ? '加载中...' : btnLabel }}
    </button>

    <!-- Empty -->
    <div v-if="!exercise && isLocked" class="flex items-center justify-center h-40 text-gray-500">
      <Dumbbell :size="40" class="opacity-50" />
    </div>
  </div>
</template>
