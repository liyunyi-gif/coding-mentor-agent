<script setup lang="ts">
import type { WeakConcept, MasteryItem } from '@/types/api'

defineProps<{ items: WeakConcept[]; hasMastery: boolean }>()
</script>

<template>
  <div v-if="items.length === 0">
    <p v-if="hasMastery" class="text-green-400 text-sm">所有概念掌握良好 ✓</p>
    <p v-else class="text-gray-500 text-sm">请先完成诊断</p>
  </div>
  <div v-else class="space-y-1.5">
    <div
      v-for="item in items"
      :key="item.concept_id"
      class="flex items-center justify-between py-1.5 border-b border-brand-border/50"
    >
      <span class="text-sm">{{ item.name }}</span>
      <span class="text-xs px-2 py-0.5 rounded-full bg-red-900/30 text-red-400">{{ item.reason }}</span>
    </div>
  </div>
</template>
