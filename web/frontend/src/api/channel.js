import request from './request'

const USE_MOCK = import.meta.env.DEV

// Mock 频道数据
const mockChannel = {
  channel_id: 'mock-channel-001',
  title: '演示课堂',
  invite_code: 'DEMO01',
  status: 'active',
  created_at: new Date().toISOString(),
}

export const channelAPI = {
  async create(data) {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 600))
      return { ...mockChannel, title: data.title || '演示课堂' }
    }
    return request.post('/channels', data)
  },

  get(id) {
    return request.get(`/channels/${id}`)
  },

  async join(id, inviteCode) {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 400))
      return { ...mockChannel, channel_id: id }
    }
    return request.post(`/channels/${id}/join`, { invite_code: inviteCode })
  },

  end(id) {
    return request.post(`/channels/${id}/end`)
  },

  getMembers(id) {
    return request.get(`/channels/${id}/members`)
  },

  getMessages(id, params = {}) {
    return request.get(`/channels/${id}/messages`, { params })
  },

  syncPage(id, page) {
    return request.post(`/channels/${id}/sync-page`, { page })
  },
}

export const exerciseAPI = {
  list(params = {}) {
    return request.get('/exercises', { params })
  },

  get(id) {
    return request.get(`/exercises/${id}`)
  },

  generate(data) {
    return request.post('/exercises/generate', data)
  },

  create(data) {
    return request.post('/exercises', data)
  },

  update(id, data) {
    return request.put(`/exercises/${id}`, data)
  },

  delete(id) {
    return request.delete(`/exercises/${id}`)
  },

  submitAnswer(exerciseId, data) {
    return request.post(`/exercises/${exerciseId}/submit`, data)
  },
}

export const analyticsAPI = {
  getClassSummary(params = {}) {
    return request.get('/analytics/class-summary', { params })
  },

  getStudentProgress(studentId) {
    return request.get(`/analytics/student/${studentId}`)
  },

  getChannelStats(channelId) {
    return request.get(`/analytics/channel/${channelId}`)
  },

  getKnowledgeMap(params = {}) {
    return request.get('/analytics/knowledge-map', { params })
  },
}
