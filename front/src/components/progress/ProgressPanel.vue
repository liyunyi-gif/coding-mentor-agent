<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getProgress } from '@/api/progress'
import type { ProgressResponse } from '@/types/api'
import ProfileCard from './ProfileCard.vue'
import MasteryList from './MasteryList.vue'
import WeakList from './WeakList.vue'
import CurriculumList from './CurriculumList.vue'
import { ChartBar } from 'lucide-vue'

const data = ref<ProgressResponse | null>(null)
const error = ref('')

async function load() {
  try {
    data.value = await getProgress()
  } catch (err) {
    error.value = `加载进度失败: ${err instanceof Error ? err.message : '未知错误'}`
  }
}

onMounted(load)
</script>

<template>
  <div class="flex-1 overflow-y-auto p-5">
    <h2 class="text-brand-blue text-lg mb-1">学习进度</h2>
    <p v-if="error" class="text-red-400 text-sm mb-4">{{ error }}</p>

    <div v-if="data" class="space-y-3">
      <section class="bg-brand-card p-4 rounded-lg">
        <h3 class="text-brand-blue text-sm font-semibold mb-2">基本概况</h3>
        <ProfileCard :data="data" />
      </section>

      <section class="bg-brand-card p-4 rounded-lg">
        <h3 class="text-brand-blue text-sm font-semibold mb-2">概念掌握</h3>
        <MasteryList :items="data.mastery" />
      </section>

      <section class="bg-brand-card p-4 rounded-lg">
        <h3 class="text-brand-blue text-sm font-semibold mb-2">薄弱环节</h3>
        <WeakList :items="data.weak_concepts" :has-mastery="data.mastery.length > 0" />
      </section>

      <section class="bg-brand-card p-4 rounded-lg">
        <h3 class="text-brand-blue text-sm font-semibold mb-2">课程进度</h3>
        <CurriculumList :units="data.curriculum" />
      </section>
    </div>

    <div v-else-if="!error" class="flex items-center justify-center h-40 text-gray-500">
      <ChartBar :size="40" class="opacity-50" />
    </div>
  </div>
</template>
