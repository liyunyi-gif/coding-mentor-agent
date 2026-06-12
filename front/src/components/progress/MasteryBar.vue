<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ level: number }>()

const color = computed(() => {
  if (props.level >= 80) return 'bg-green-500'
  if (props.level >= 50) return 'bg-orange-500'
  return 'bg-red-500'
})
</script>

<template>
  <div class="w-28 h-2 bg-brand-border rounded-full overflow-hidden">
    <div :class="[color, 'h-full rounded-full transition-all']" :style="{ width: `${level}%` }"></div>
  </div>
</template>
