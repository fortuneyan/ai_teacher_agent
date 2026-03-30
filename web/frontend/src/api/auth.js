import request from './request'
import { mockLogin } from './mock'

// 强制使用真实后端API（与lessonPlan.js保持一致）
const USE_MOCK = false

export const authAPI = {
  async login(credentials) {
    if (USE_MOCK) return mockLogin(credentials)
    const form = new URLSearchParams()
    form.append('username', credentials.username)
    form.append('password', credentials.password)
    return request.post('/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
  },

  getMe() {
    if (USE_MOCK) {
      const user = JSON.parse(localStorage.getItem('user') || 'null')
      return Promise.resolve(user)
    }
    return request.get('/auth/me')
  },

  register(data) {
    return request.post('/auth/register', data)
  },

  changePassword(data) {
    return request.post('/auth/change-password', data)
  },
}
