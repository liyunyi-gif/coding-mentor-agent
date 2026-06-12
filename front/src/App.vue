<script setup lang="ts">
import { onMounted } from 'vue'
import { useSessionStore } from '@/stores/session'
import AppHeader from '@/components/layout/AppHeader.vue'

const store = useSessionStore()

onMounted(() => {
  store.initSession().catch((err) => {
    console.error('Failed to initialize session:', err)
  })
})
</script>

<template>
  <AppHeader />
  <main class="flex-1 overflow-hidden">
    <router-view />
  </main>
</template>
