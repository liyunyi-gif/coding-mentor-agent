<script setup lang="ts">
import type { ProgressResponse } from '@/types/api'

defineProps<{ data: ProgressResponse }>()

function statusLabel(state: string) {
  const labels: Record<string, string> = {
    not_started: '未开始',
    active: '进行中',
    completed: '已完成',
  }
  return labels[state] || state
}

function practiceLabel(state: string) {
  const labels: Record<string, string> = {
    locked_by_diagnostic: '需先完成诊断',
    available_after_explicit_request: '可请求练习',
  }
  return labels[state] || state
}
</script>

<template>
  <div class="grid grid-cols-2 gap-3 text-sm">
    <div>
      <span class="text-gray-500">当前水平</span>
      <strong class="block text-gray-200">{{ data.current_level }}</strong>
    </div>
    <div>
      <span class="text-gray-500">整体进度</span>
      <strong class="block text-gray-200">{{ data.course_progress_percent }}%</strong>
    </div>
    <div>
      <span class="text-gray-500">诊断状态</span>
      <strong class="block text-gray-200">{{ statusLabel(data.diagnostic_state) }}</strong>
    </div>
    <div>
      <span class="text-gray-500">练习状态</span>
      <strong class="block text-gray-200">{{ practiceLabel(data.practice_state) }}</strong>
    </div>
  </div>
</template>
