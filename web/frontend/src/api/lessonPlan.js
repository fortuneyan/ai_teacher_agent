import request from './request'
import { mockGeneratePlan, mockGetPlans, mockGetPlan, mockUpdatePlan, mockDeletePlan } from './mock'

// 强制使用真实后端API（禁用mock）
// 如需使用mock，设置为 import.meta.env.DEV
const USE_MOCK = false

export const lessonPlanAPI = {
  list(params = {}) {
    if (USE_MOCK) return mockGetPlans(params)
    return request.get('/lesson-plans/', { params })
  },

  get(id) {
    if (USE_MOCK) return mockGetPlan(id)
    return request.get(`/lesson-plans/${id}`)
  },

  generate(data) {
    if (USE_MOCK) return mockGeneratePlan(data)
    const gradeMap = {
      'grade1': '高一', 'grade2': '高二', 'grade3': '高三',
      'grade4': '大一', 'grade5': '大二', 'grade6': '大三', 'grade7': '大四',
      'grade8': '初一', 'grade9': '初二', 'grade10': '初三',
      'grade11': '一年级', 'grade12': '二年级', 'grade13': '三年级',
      'grade14': '四年级', 'grade15': '五年级', 'grade16': '六年级',
    }
    const payload = {
      subject: data.subject,
      grade: gradeMap[data.grade] || data.grade,
      topic: data.topic,
      version: '人教版',
      duration: parseInt(data.duration) || 1,
      custom_objectives: data.objectives ? [data.objectives] : null,
    }
    console.trace('Generating lesson plan with payload:', payload)
    return request.post('/lesson-plans/', payload)
  },

  update(id, data) {
    if (USE_MOCK) return mockUpdatePlan(id, data)
    return request.put(`/lesson-plans/${id}`, data)
  },

  delete(id) {
    if (USE_MOCK) return mockDeletePlan(id)
    return request.delete(`/lesson-plans/${id}`)
  },

  export(id) {
    return request.get(`/lesson-plans/${id}/export`)
  },
}
