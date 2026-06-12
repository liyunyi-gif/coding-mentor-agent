<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useSessionStore } from '@/stores/session'
import Sidebar from '@/components/layout/Sidebar.vue'
import AppHeader from '@/components/layout/AppHeader.vue'

const store = useSessionStore()
const sidebarCollapsed = ref(false)

onMounted(() => {
  store.initSession().catch((err) => console.error('Session init failed:', err))
})

function handleNewChat() {
  store.clearMessages()
  store.initSession()
}
</script>

<template>
  <div class="flex h-screen relative">
    <Sidebar v-model:collapsed="sidebarCollapsed" @new-chat="handleNewChat" />
    <div class="flex flex-col flex-1 min-w-0">
      <AppHeader :sidebar-collapsed="sidebarCollapsed" @toggle-sidebar="sidebarCollapsed = !sidebarCollapsed" />
      <main class="flex-1 overflow-hidden bg-white">
        <router-view />
      </main>
    </div>
  </div>
</template>
