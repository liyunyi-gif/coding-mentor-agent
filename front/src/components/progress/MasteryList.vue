<script setup lang="ts">
import type { MasteryItem } from '@/types/api'
import MasteryBar from './MasteryBar.vue'

defineProps<{ items: MasteryItem[] }>()
</script>

<template>
  <div v-if="items.length === 0" class="text-gray-500 text-sm">暂无掌握度数据</div>
  <div v-else class="space-y-1.5">
    <div
      v-for="item in items"
      :key="item.concept_id"
      class="flex items-center justify-between py-1.5 border-b border-brand-border/50"
    >
      <span class="text-sm w-24 shrink-0">{{ item.name || item.concept_id }}</span>
      <MasteryBar :level="item.mastery_level" />
      <span class="text-xs text-gray-500 w-12 text-right">{{ item.mastery_level }}%</span>
    </div>
  </div>
</template>
