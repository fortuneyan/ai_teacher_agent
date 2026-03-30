<template>
  <div class="login-page">
    <div class="login-container">
      <!-- 左侧介绍 -->
      <div class="login-left">
        <div class="brand">
          <el-icon size="48" color="#1971C2"><School /></el-icon>
          <h1>AI教师Agent</h1>
          <p>智能备课 · 实时授课 · 精准学情</p>
        </div>
        <ul class="feature-list">
          <li><el-icon color="#2F9E44"><Check /></el-icon> AI智能生成教案、课件、习题</li>
          <li><el-icon color="#2F9E44"><Check /></el-icon> 多教师多学生实时在线授课</li>
          <li><el-icon color="#2F9E44"><Check /></el-icon> 学情数据可视化分析</li>
          <li><el-icon color="#2F9E44"><Check /></el-icon> 符合课程标准，开箱即用</li>
        </ul>
      </div>

      <!-- 右侧登录表单 -->
      <div class="login-right">
        <div class="login-card">
          <h2>登录</h2>
          <p class="login-subtitle">欢迎使用AI教师Agent</p>

          <el-form
            ref="formRef"
            :model="form"
            :rules="rules"
            label-position="top"
            @submit.prevent="handleLogin"
          >
            <el-form-item label="用户名" prop="username">
              <el-input
                v-model="form.username"
                placeholder="请输入用户名"
                size="large"
                prefix-icon="User"
                @keyup.enter="handleLogin"
              />
            </el-form-item>

            <el-form-item label="密码" prop="password">
              <el-input
                v-model="form.password"
                type="password"
                placeholder="请输入密码"
                size="large"
                prefix-icon="Lock"
                show-password
                @keyup.enter="handleLogin"
              />
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                size="large"
                :loading="loading"
                style="width: 100%"
                @click="handleLogin"
              >
                {{ loading ? '登录中...' : '登 录' }}
              </el-button>
            </el-form-item>
          </el-form>

          <!-- 演示账号 -->
          <el-divider>演示账号</el-divider>
          <div class="demo-accounts">
            <el-tag
              v-for="demo in demoAccounts"
              :key="demo.username"
              class="demo-tag"
              @click="fillDemo(demo)"
            >
              {{ demo.label }}
            </el-tag>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const formRef = ref()
const loading = ref(false)

const form = ref({
  username: '',
  password: '',
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const demoAccounts = [
  { label: '教师账号', username: 'teacher01', password: 'demo123' },
  { label: '学生账号', username: 'student01', password: 'demo123' },
  { label: '管理员', username: 'admin', password: 'admin123' },
]

function fillDemo(demo) {
  form.value.username = demo.username
  form.value.password = demo.password
}

async function handleLogin() {
  if (!form.value.username || !form.value.password) {
    ElMessage.error('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    await authStore.login(form.value)
    const redirect = route.query.redirect
    const role = authStore.user?.role
    if (redirect) {
      router.push(redirect)
    } else if (role === 'teacher') {
      router.push('/teacher/dashboard')
    } else if (role === 'student') {
      router.push('/student/classroom')
    } else if (role === 'admin') {
      router.push('/admin/users')
    }
    ElMessage.success(`欢迎回来，${authStore.user?.name}`)
  } catch (e) {
    console.error('Login error:', e)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #1971C2 0%, #0c4a8a 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.login-container {
  display: flex;
  width: 100%;
  max-width: 900px;
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}

.login-left {
  flex: 1;
  background: linear-gradient(160deg, #1971C2 0%, #0c4a8a 100%);
  padding: 48px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  color: #fff;
}

.brand {
  margin-bottom: 40px;
}
.brand h1 {
  font-size: 28px;
  font-weight: 700;
  margin: 16px 0 8px;
}
.brand p {
  font-size: 15px;
  opacity: 0.85;
}

.feature-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.feature-list li {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  opacity: 0.9;
}

.login-right {
  flex: 1;
  padding: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-card {
  width: 100%;
  max-width: 360px;
}

.login-card h2 {
  font-size: 24px;
  font-weight: 700;
  color: #343a40;
  margin-bottom: 4px;
}

.login-subtitle {
  color: #6c757d;
  font-size: 14px;
  margin-bottom: 32px;
}

.demo-accounts {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 8px;
}

.demo-tag {
  cursor: pointer;
}
.demo-tag:hover {
  opacity: 0.8;
}

@media (max-width: 640px) {
  .login-left {
    display: none;
  }
  .login-right {
    padding: 32px 24px;
  }
}
</style>
