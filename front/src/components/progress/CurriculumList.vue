<script setup lang="ts">
import type { CurriculumUnit } from '@/types/api'

defineProps<{ units: CurriculumUnit[] }>()

function statusBadge(status: string) {
  switch (status) {
    case 'completed':
      return { label: '已完成', cls: 'bg-green-900/30 text-green-400' }
    case 'current':
      return { label: '进行中', cls: 'bg-blue-900/30 text-blue-400' }
    default:
      return { label: '待学', cls: 'bg-gray-800 text-gray-400' }
  }
}
</script>

<template>
  <div v-if="units.length === 0" class="text-gray-500 text-sm">暂无课程数据</div>
  <div v-else class="space-y-1.5">
    <div
      v-for="unit in units"
      :key="unit.id"
      class="flex items-center justify-between py-1.5 border-b border-brand-border/50"
    >
      <span class="text-sm">{{ unit.title }}</span>
      <span :class="['text-xs px-2 py-0.5 rounded-full', statusBadge(unit.status).cls]">
        {{ statusBadge(unit.status).label }}
      </span>
    </div>
  </div>
</template>
