<template>
  <el-container style="height:100vh">
    <el-aside width="200px" style="background:#001529">
      <div style="height:64px;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:600;font-size:15px;">
        系统管理
      </div>
      <el-menu background-color="#001529" text-color="#ffffffa6" active-text-color="#fff" :router="true" :default-active="$route.path">
        <el-menu-item index="/admin/users"><el-icon><User /></el-icon>用户管理</el-menu-item>
        <el-menu-item index="/admin/system"><el-icon><Setting /></el-icon>系统配置</el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header style="background:#fff;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #dee2e6;padding:0 24px;">
        <span style="font-size:16px;font-weight:600;">AI教师Agent - 管理控制台</span>
        <el-button text @click="authStore.logout()">退出</el-button>
      </el-header>
      <el-main style="background:#f8f9fa;">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>
<script setup>
import { useAuthStore } from '@/stores/auth'
const authStore = useAuthStore()
</script>
