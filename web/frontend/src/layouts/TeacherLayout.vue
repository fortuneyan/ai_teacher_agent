<template>
  <el-container class="teacher-layout">
    <!-- 侧边栏 -->
    <el-aside :width="sidebarCollapsed ? '64px' : '220px'" class="sidebar">
      <div class="sidebar-logo">
        <el-icon size="24" color="#1971C2"><School /></el-icon>
        <span v-if="!sidebarCollapsed" class="logo-text">AI教师Agent</span>
      </div>

      <el-menu
        :default-active="activeMenu"
        :collapse="sidebarCollapsed"
        :router="true"
        background-color="#001529"
        text-color="#ffffffa6"
        active-text-color="#ffffff"
        class="sidebar-menu"
      >
        <el-menu-item index="/teacher/dashboard">
          <el-icon><EditPen /></el-icon>
          <template #title>备课工作台</template>
        </el-menu-item>
        <el-menu-item index="/teacher/lesson-plans">
          <el-icon><Document /></el-icon>
          <template #title>我的教案</template>
        </el-menu-item>
        <el-menu-item index="/teacher/exercises">
          <el-icon><Collection /></el-icon>
          <template #title>习题管理</template>
        </el-menu-item>
        <el-menu-item index="/teacher/teaching-room">
          <el-icon><VideoCamera /></el-icon>
          <template #title>授课教室</template>
        </el-menu-item>
        <el-menu-item index="/teacher/analytics">
          <el-icon><TrendCharts /></el-icon>
          <template #title>学情分析</template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container class="main-container">
      <!-- 顶部导航 -->
      <el-header class="header">
        <div class="header-left">
          <el-button
            :icon="sidebarCollapsed ? 'Expand' : 'Fold'"
            text
            @click="sidebarCollapsed = !sidebarCollapsed"
          />
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/teacher/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentTitle">{{ currentTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <!-- 在线状态 -->
          <el-badge :value="onlineCount" class="online-badge" type="success">
            <el-icon><User /></el-icon>
          </el-badge>
          <!-- 用户信息 -->
          <el-dropdown @command="handleUserCommand">
            <div class="user-info">
              <el-avatar size="small" :src="authStore.user?.avatar">
                {{ authStore.user?.name?.[0] || 'T' }}
              </el-avatar>
              <span class="user-name">{{ authStore.user?.name || '教师' }}</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                <el-dropdown-item command="settings">设置</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 主内容区 -->
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const route = useRoute()
const sidebarCollapsed = ref(false)
const onlineCount = ref(0)

const activeMenu = computed(() => route.path)
const currentTitle = computed(() => route.meta?.title)

function handleUserCommand(command) {
  if (command === 'logout') {
    authStore.logout()
  }
}
</script>

<style scoped>
.teacher-layout {
  height: 100vh;
  overflow: hidden;
}

.sidebar {
  background: #001529;
  transition: width 0.3s;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.sidebar-logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 0 16px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  overflow: hidden;
}

.logo-text {
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  white-space: nowrap;
}

.sidebar-menu {
  border-right: none;
  flex: 1;
}

.main-container {
  overflow: hidden;
}

.header {
  height: 64px;
  background: #fff;
  border-bottom: 1px solid #dee2e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.online-badge {
  cursor: default;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.2s;
}
.user-info:hover {
  background: #f5f5f5;
}

.user-name {
  font-size: 14px;
  color: #343a40;
}

.main-content {
  background: #f8f9fa;
  overflow-y: auto;
  padding: 24px;
}
</style>
