<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useSessionStore } from '@/stores/session'
import { requestPractice } from '@/api/practice'
import { getProgress } from '@/api/progress'
import { marked } from 'marked'
import type { Exercise } from '@/types/api'
import { Lock, Code2 } from 'lucide-vue'

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
      isLocked.value = false; statusMessage.value = '诊断已完成，可以开始练习！'
    } else if (data.diagnostic_state === 'active') {
      isLocked.value = true; lockMessage.value = '诊断进行中，完成诊断后可解锁练习。'
    } else {
      isLocked.value = true; lockMessage.value = '请先完成诊断测评。'
    }
  } catch { /* ignore */ }
}

async function handleRequest() {
  const sid = store.sessionId || (await store.initSession())
  isLoading.value = true
  try {
    const data = await requestPractice(sid)
    if (data.kind === 'practice_locked') { isLocked.value = true; lockMessage.value = data.message; exercise.value = null }
    else { isLocked.value = false; exercise.value = data.exercise; statusMessage.value = data.next_step; btnLabel.value = '换一题' }
  } catch { lockMessage.value = '请求失败' } finally { isLoading.value = false }
}

onMounted(checkAvailability)
</script>

<template>
  <div class="flex-1 overflow-y-auto p-6 bg-gray-50">
    <div class="w-full">
      <h2 class="text-lg font-semibold text-gray-800 mb-1">练习</h2>
      <p class="text-sm text-gray-500 mb-4">完成诊断后可解锁编程练习。</p>

      <!-- Locked -->
      <div v-if="isLocked" class="bg-white border border-gray-200 p-4 rounded-xl mb-3 flex items-center gap-3">
        <Lock :size="18" class="text-red-400 shrink-0" />
        <p class="text-red-500 text-sm">{{ lockMessage }}</p>
      </div>

      <!-- Status -->
      <div v-if="statusMessage && !isLocked" class="bg-blue-50 border border-blue-200 p-4 rounded-xl mb-3">
        <p class="text-blue-700 text-sm">{{ statusMessage }}</p>
      </div>

      <!-- Exercise -->
      <div v-if="exercise" class="bg-white border border-gray-200 p-5 rounded-xl mb-3">
        <h3 class="text-gray-800 font-semibold mb-3">{{ exercise.title }}</h3>
        <div class="markdown-body text-sm text-gray-700 mb-4" v-html="marked.parse(exercise.prompt_md)"></div>
        <div v-if="exercise.acceptance_checklist?.length" class="border-t border-gray-100 pt-3">
          <h4 class="text-sm font-medium text-gray-600 mb-2">验收标准</h4>
          <ul class="list-disc list-inside text-sm text-gray-500 space-y-1">
            <li v-for="item in exercise.acceptance_checklist" :key="item">{{ item }}</li>
          </ul>
        </div>
      </div>

      <button v-if="!isLocked" @click="handleRequest" :disabled="isLoading"
        class="flex items-center gap-2 px-5 py-2.5 bg-blue-500 text-white rounded-lg text-sm font-medium hover:bg-blue-600 disabled:opacity-50 transition-colors">
        <Code2 :size="14" /> {{ isLoading ? '加载中...' : btnLabel }}
      </button>
    </div>
  </div>
</template>
