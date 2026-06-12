<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionStore } from '@/stores/session'
import Sidebar from '@/components/layout/Sidebar.vue'
import AppHeader from '@/components/layout/AppHeader.vue'
import { PanelLeftOpen, PanelLeftClose } from 'lucide-vue'

const store = useSessionStore()
const router = useRouter()
const sidebarCollapsed = ref(false)

onMounted(() => {
  store.initSession().catch((err) => console.error('Session init failed:', err))
})

function handleSelectSession(id: string) {
  router.push('/chat')
}
</script>

<template>
  <div class="flex h-screen relative">
    <Sidebar
      v-model:collapsed="sidebarCollapsed"
      @select-session="handleSelectSession"
    />
    <!-- Collapse toggle button - outside sidebar so it stays visible -->
    <button
      @click="sidebarCollapsed = !sidebarCollapsed"
      class="absolute left-0 top-1/2 -translate-y-1/2 z-10 p-1.5 bg-white border border-gray-200 rounded-r-md shadow-sm hover:bg-gray-50 transition-colors"
      :style="{ left: sidebarCollapsed ? '0' : '256px' }"
    >
      <PanelLeftOpen v-if="sidebarCollapsed" :size="16" class="text-gray-500" />
      <PanelLeftClose v-else :size="16" class="text-gray-500" />
    </button>
    <div class="flex flex-col flex-1 min-w-0">
      <AppHeader
        :sidebar-collapsed="sidebarCollapsed"
        @toggle-sidebar="sidebarCollapsed = !sidebarCollapsed"
      />
      <main class="flex-1 overflow-hidden bg-white">
        <router-view />
      </main>
    </div>
  </div>
</template>
