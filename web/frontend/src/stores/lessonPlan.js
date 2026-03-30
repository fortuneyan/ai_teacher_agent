import { defineStore } from 'pinia'
import { ref } from 'vue'
import { lessonPlanAPI } from '@/api/lessonPlan'

export const useLessonPlanStore = defineStore('lessonPlan', () => {
  const plans = ref([])
  const currentPlan = ref(null)
  const loading = ref(false)
  const generating = ref(false)
  const total = ref(0)

  async function fetchPlans(params = {}) {
    loading.value = true
    try {
      const data = await lessonPlanAPI.list(params)
      // 兼容后端返回数组或 {items, total} 格式
      if (Array.isArray(data)) {
        plans.value = data
        total.value = data.length
      } else {
        plans.value = data.items || []
        total.value = data.total || 0
      }
    } finally {
      loading.value = false
    }
  }

  async function fetchPlan(id) {
    loading.value = true
    try {
      currentPlan.value = await lessonPlanAPI.get(id)
    } finally {
      loading.value = false
    }
  }

  async function generatePlan(params) {
    generating.value = true
    try {
      const plan = await lessonPlanAPI.generate(params)
      // 确保 plans 是数组
      if (!plans.value) plans.value = []
      plans.value.unshift(plan)
      currentPlan.value = plan
      return plan
    } finally {
      generating.value = false
    }
  }

  async function savePlan(id, data) {
    const updated = await lessonPlanAPI.update(id, data)
    const index = plans.value.findIndex(p => p.id === id)
    if (index !== -1) plans.value[index] = updated
    if (currentPlan.value?.id === id) currentPlan.value = updated
    return updated
  }

  async function deletePlan(id) {
    await lessonPlanAPI.delete(id)
    plans.value = plans.value.filter(p => p.id !== id)
  }

  return {
    plans,
    currentPlan,
    loading,
    generating,
    total,
    fetchPlans,
    fetchPlan,
    generatePlan,
    savePlan,
    deletePlan,
  }
})
