<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getProgress } from '@/api/progress'
import type { ProgressResponse } from '@/types/api'
import MasteryBar from './MasteryBar.vue'

const data = ref<ProgressResponse | null>(null)
const error = ref('')

function statusLabel(s: string) { const m: Record<string,string>={not_started:'未开始',active:'进行中',completed:'已完成'}; return m[s]||s }
function practiceLabel(s: string) { const m: Record<string,string>={locked_by_diagnostic:'需先完成诊断',available_after_explicit_request:'可请求练习'}; return m[s]||s }
function unitBadge(s: string) {
  if (s==='completed') return 'bg-green-50 text-green-600'
  if (s==='current') return 'bg-blue-50 text-blue-600'
  return 'bg-gray-100 text-gray-500'
}
function unitLabel(s: string) { const m: Record<string,string>={completed:'已完成',current:'进行中',upcoming:'待学'}; return m[s]||s }

onMounted(async () => { try { data.value = await getProgress() } catch (e) { error.value = `加载失败: ${e}` } })
</script>

<template>
  <div class="flex-1 min-h-0 overflow-y-auto p-6 bg-gray-50">
    <div class="w-full">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">学习进度</h2>
      <p v-if="error" class="text-red-500 text-sm mb-4">{{ error }}</p>

      <div v-if="data" class="space-y-3">
        <!-- Profile -->
        <section class="bg-white border border-gray-200 p-4 rounded-xl">
          <h3 class="text-sm font-semibold text-gray-700 mb-2">基本概况</h3>
          <div class="grid grid-cols-2 gap-3 text-sm">
            <div><span class="text-gray-400">当前水平</span><strong class="block text-gray-800">{{ data.current_level }}</strong></div>
            <div><span class="text-gray-400">整体进度</span><strong class="block text-gray-800">{{ data.course_progress_percent }}%</strong></div>
            <div><span class="text-gray-400">诊断状态</span><strong class="block text-gray-800">{{ statusLabel(data.diagnostic_state) }}</strong></div>
            <div><span class="text-gray-400">练习状态</span><strong class="block text-gray-800">{{ practiceLabel(data.practice_state) }}</strong></div>
          </div>
        </section>

        <!-- Mastery -->
        <section class="bg-white border border-gray-200 p-4 rounded-xl">
          <h3 class="text-sm font-semibold text-gray-700 mb-2">概念掌握</h3>
          <div v-if="data.mastery.length===0" class="text-gray-400 text-sm">暂无数据</div>
          <div v-else class="space-y-1.5">
            <div v-for="m in data.mastery" :key="m.concept_id" class="flex items-center gap-3 py-1.5 border-b border-gray-50">
              <span class="text-sm w-24 shrink-0 text-gray-700">{{ m.name || m.concept_id }}</span>
              <MasteryBar :level="m.mastery_level" />
              <span class="text-xs text-gray-400 w-10 text-right">{{ m.mastery_level }}%</span>
            </div>
          </div>
        </section>

        <!-- Weak -->
        <section class="bg-white border border-gray-200 p-4 rounded-xl">
          <h3 class="text-sm font-semibold text-gray-700 mb-2">薄弱环节</h3>
          <div v-if="data.weak_concepts.length===0">
            <p v-if="data.mastery.length>0" class="text-green-600 text-sm">所有概念掌握良好 ✓</p>
            <p v-else class="text-gray-400 text-sm">请先完成诊断</p>
          </div>
          <div v-else class="space-y-1.5">
            <div v-for="w in data.weak_concepts" :key="w.concept_id" class="flex items-center justify-between py-1.5 border-b border-gray-50">
              <span class="text-sm text-gray-700">{{ w.name }}</span>
              <span class="text-xs px-2 py-0.5 rounded-full bg-red-50 text-red-500">{{ w.reason }}</span>
            </div>
          </div>
        </section>

        <!-- Curriculum -->
        <section class="bg-white border border-gray-200 p-4 rounded-xl">
          <h3 class="text-sm font-semibold text-gray-700 mb-2">课程大纲</h3>
          <div v-if="data.curriculum.length===0" class="text-gray-400 text-sm">暂无</div>
          <div v-else class="space-y-1.5">
            <div v-for="u in data.curriculum" :key="u.id" class="flex items-center justify-between py-1.5 border-b border-gray-50">
              <span class="text-sm text-gray-700">{{ u.title }}</span>
              <span :class="['text-xs px-2 py-0.5 rounded-full', unitBadge(u.status)]">{{ unitLabel(u.status) }}</span>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>
