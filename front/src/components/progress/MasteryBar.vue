<script setup lang="ts">
import { computed } from 'vue'
const props = defineProps<{ level: number }>()
const color = computed(() => props.level >= 80 ? 'bg-green-500' : props.level >= 50 ? 'bg-orange-400' : 'bg-red-500')
</script>
<template>
  <div class="w-28 h-2 bg-gray-100 rounded-full overflow-hidden">
    <div :class="[color, 'h-full rounded-full transition-all']" :style="{ width: `${level}%` }"></div>
  </div>
</template>
