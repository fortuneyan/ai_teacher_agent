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
    // 根据学段获取正确的年级映射
    const levelGradeMap = {
      primary: {
        'grade1': '一年级', 'grade2': '二年级', 'grade3': '三年级',
        'grade4': '四年级', 'grade5': '五年级', 'grade6': '六年级',
      },
      middle: {
        'grade1': '初一', 'grade2': '初二', 'grade3': '初三',
      },
      high: {
        'grade1': '高一', 'grade2': '高二', 'grade3': '高三',
      },
      university: {
        'grade1': '大一', 'grade2': '大二', 'grade3': '大三', 'grade4': '大四',
      },
    }
    
    // 根据学段获取默认年级
    const defaultGrades = {
      primary: '一年级',
      middle: '初一',
      high: '高一',
      university: '大一',
    }
    
    const gradeMapForLevel = levelGradeMap[data.level] || {}
    let grade = gradeMapForLevel[data.grade]
    
    // 如果映射失败，使用该学段的默认年级
    if (!grade) {
      grade = defaultGrades[data.level] || '高一'
      console.warn(`Grade mapping failed for level=${data.level}, grade=${data.grade}, using default: ${grade}`)
    }
    
    const payload = {
      subject: data.subject,
      grade: grade,
      topic: data.topic,
      version: '人教版',
      duration: parseInt(data.duration) || 1,
      custom_objectives: data.objectives ? [data.objectives] : null,
    }
    console.log('Generating lesson plan with payload:', payload)
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
