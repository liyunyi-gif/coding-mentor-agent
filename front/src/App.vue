<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionStore } from '@/stores/session'
import Sidebar from '@/components/layout/Sidebar.vue'
import AppHeader from '@/components/layout/AppHeader.vue'

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
    <!-- Collapse toggle -->
    <button
      @click="sidebarCollapsed = !sidebarCollapsed"
      :title="sidebarCollapsed ? '点击展开对话栏' : '点击收回对话栏'"
      class="absolute top-1/2 -translate-y-1/2 z-10 w-7 h-16 bg-white border border-gray-200 rounded-r-md shadow-sm hover:bg-gray-50 transition-colors flex items-center justify-center"
      :style="{ left: sidebarCollapsed ? '0' : '256px' }"
    >
      <span class="text-gray-400 text-sm font-bold select-none">{{ sidebarCollapsed ? '>' : '<' }}</span>
    </button>
    <div class="flex flex-col flex-1 min-w-0">
      <AppHeader
        :sidebar-collapsed="sidebarCollapsed"
        @toggle-sidebar="sidebarCollapsed = !sidebarCollapsed"
      />
      <main class="flex-1 overflow-hidden bg-gray-50">
        <router-view />
      </main>
    </div>
  </div>
</template>
