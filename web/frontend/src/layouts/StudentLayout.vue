<template>
  <el-container class="student-layout">
    <el-header class="header">
      <div class="header-left">
        <el-icon size="22" color="#1971C2"><School /></el-icon>
        <span class="brand-name">AI学习助手</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        mode="horizontal"
        :router="true"
        class="nav-menu"
      >
        <el-menu-item index="/student/classroom">课堂学习</el-menu-item>
        <el-menu-item index="/student/exercises">习题练习</el-menu-item>
        <el-menu-item index="/student/progress">学习进度</el-menu-item>
      </el-menu>
      <el-dropdown @command="handleCommand">
        <div class="user-info">
          <el-avatar size="small">{{ authStore.user?.name?.[0] || 'S' }}</el-avatar>
          <span>{{ authStore.user?.name || '学生' }}</span>
          <el-icon><ArrowDown /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="logout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </el-header>
    <el-main class="main-content">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const route = useRoute()
const activeMenu = computed(() => route.path)

function handleCommand(cmd) {
  if (cmd === 'logout') authStore.logout()
}
</script>

<style scoped>
.student-layout { height: 100vh; overflow: hidden; }
.header {
  height: 60px;
  background: #fff;
  border-bottom: 1px solid #dee2e6;
  display: flex;
  align-items: center;
  padding: 0 24px;
  gap: 24px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}
.header-left { display: flex; align-items: center; gap: 8px; }
.brand-name { font-size: 16px; font-weight: 600; color: #343a40; }
.nav-menu { flex: 1; border-bottom: none; }
.user-info { display: flex; align-items: center; gap: 8px; cursor: pointer; font-size: 14px; }
.main-content { background: #f8f9fa; overflow-y: auto; padding: 24px; }
</style>
