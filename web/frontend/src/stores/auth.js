import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '@/api/auth'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  // 从 localStorage 初始化，确保不为 undefined
  const storedUser = localStorage.getItem('user')
  const user = ref(storedUser ? JSON.parse(storedUser) : null)
  const token = ref(localStorage.getItem('token') || '')

  const isLoggedIn = computed(() => !!token.value && !!user.value)
  const isTeacher = computed(() => user.value?.role === 'teacher')
  const isStudent = computed(() => user.value?.role === 'student')
  const isAdmin = computed(() => user.value?.role === 'admin')

  async function login(credentials) {
    const data = await authAPI.login(credentials)
    console.log('API response:', data)
    const accessToken = data.access_token
    token.value = accessToken
    const userObj = {
      ...data.user,
      name: data.user.name || data.user.full_name || data.user.username,
    }
    user.value = userObj
    // 先设置 localStorage
    localStorage.setItem('token', accessToken)
    localStorage.setItem('user', JSON.stringify(userObj))
    // 验证
    console.log('Token saved:', localStorage.getItem('token'))
    return data
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    router.push('/login')
  }

  async function refreshUser() {
    try {
      const data = await authAPI.getMe()
      user.value = data
      localStorage.setItem('user', JSON.stringify(data))
    } catch (e) {
      console.error('refreshUser error:', e)
      logout()
    }
  }

  return {
    user,
    token,
    isLoggedIn,
    isTeacher,
    isStudent,
    isAdmin,
    login,
    logout,
    refreshUser,
  }
})
