<template>
  <div class="dashboard">
    <!-- 页面标题 -->
    <div class="page-header">
      <div>
        <h2>备课工作台</h2>
        <p class="text-muted">AI辅助生成教案、课件和习题</p>
      </div>
      <el-button type="primary" icon="Plus" @click="router.push('/teacher/lesson-plans')">
        我的教案
      </el-button>
    </div>

    <el-row :gutter="24">
      <!-- 左侧：AI备课表单 -->
      <el-col :xs="24" :lg="14">
        <el-card class="form-card">
          <template #header>
            <div class="flex-between">
              <span class="card-title">快速备课</span>
              <el-tag type="success" size="small">AI驱动</el-tag>
            </div>
          </template>

          <el-form
            ref="formRef"
            :model="form"
            :rules="rules"
            label-width="80px"
            label-position="left"
          >
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="学段" prop="level">
                  <el-select v-model="form.level" placeholder="选择学段" style="width:100%" @change="handleLevelChange">
                    <el-option label="小学" value="primary" />
                    <el-option label="初中" value="middle" />
                    <el-option label="高中" value="high" />
                    <el-option label="大学" value="university" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="学科" prop="subject">
                  <el-select v-model="form.subject" placeholder="选择学科" style="width:100%">
                    <el-option label="数学" value="math" />
                    <el-option label="语文" value="chinese" />
                    <el-option label="英语" value="english" />
                    <el-option label="物理" value="physics" />
                    <el-option label="化学" value="chemistry" />
                    <el-option label="生物" value="biology" />
                    <el-option label="历史" value="history" />
                    <el-option label="地理" value="geography" />
                    <el-option label="政治" value="politics" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="年级" prop="grade">
                  <el-select v-model="form.grade" placeholder="选择年级" style="width:100%">
                    <el-option v-for="g in gradeOptions" :key="g.value" :label="g.label" :value="g.value" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="课时" prop="duration">
                  <el-select v-model="form.duration" style="width:100%">
                    <el-option label="1课时（45分钟）" value="1" />
                    <el-option label="2课时（90分钟）" value="2" />
                    <el-option label="3课时（135分钟）" value="3" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="课题" prop="topic">
              <el-input
                v-model="form.topic"
                placeholder="例如：一元二次方程、细胞的结构与功能..."
                clearable
              />
            </el-form-item>

            <el-form-item label="教学目标">
              <el-input
                v-model="form.objectives"
                type="textarea"
                :rows="2"
                placeholder="可选：描述本节课的教学目标（留空则AI自动生成）"
              />
            </el-form-item>

            <el-form-item label="特殊要求">
              <el-input
                v-model="form.requirements"
                type="textarea"
                :rows="2"
                placeholder="可选：特殊教学要求、班级特点等"
              />
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                size="large"
                :loading="planStore.generating"
                icon="MagicStick"
                style="width: 100%"
                @click="handleGenerate"
              >
                {{ planStore.generating ? 'AI正在生成教案...' : 'AI生成教案' }}
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 右侧：最近教案 + 统计 -->
      <el-col :xs="24" :lg="10">
        <!-- 快速统计 -->
        <el-row :gutter="12" class="mb-md">
          <el-col :span="8" v-for="stat in stats" :key="stat.label">
            <el-card class="stat-card">
              <div class="stat-value" :style="{ color: stat.color }">{{ stat.value }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 最近教案 -->
        <el-card>
          <template #header>
            <div class="flex-between">
              <span class="card-title">最近教案</span>
              <el-button text size="small" @click="router.push('/teacher/lesson-plans')">
                查看全部 →
              </el-button>
            </div>
          </template>

          <div v-if="planStore.loading" class="loading-placeholder">
            <el-skeleton :rows="4" animated />
          </div>
          <div v-else-if="planStore.plans.length === 0" class="empty-state">
            <el-empty description="还没有教案，快去生成一个吧" :image-size="80" />
          </div>
          <div v-else class="plan-list">
            <div
              v-for="plan in planStore.plans.slice(0, 5)"
              :key="plan.id"
              class="plan-item"
              @click="router.push(`/teacher/lesson-plans/${plan.id}/edit`)"
            >
              <div class="plan-info">
                <div class="plan-title">{{ plan.title }}</div>
                <div class="plan-meta text-muted">
                  {{ plan.subject }} · {{ plan.grade }} · {{ formatDate(plan.created_at) }}
                </div>
              </div>
              <el-tag :type="statusType(plan.status)" size="small">
                {{ statusLabel(plan.status) }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 生成结果预览 -->
    <el-dialog
      v-model="showPreview"
      title="教案生成成功"
      width="70%"
      :close-on-click-modal="false"
    >
      <div v-if="generatedPlan" class="plan-preview">
        <div class="plan-preview-header">
          <h3>{{ generatedPlan.title }}</h3>
          <div class="text-muted">{{ generatedPlan.subject }} · {{ generatedPlan.grade }}</div>
        </div>
        <el-scrollbar height="400px">
          <div class="plan-content" v-html="generatedPlan.content_html || generatedPlan.content"></div>
        </el-scrollbar>
      </div>
      <template #footer>
        <el-button @click="showPreview = false">关闭</el-button>
        <el-button type="primary" icon="Edit" @click="openEditor">
          编辑教案
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useLessonPlanStore } from '@/stores/lessonPlan'
import dayjs from 'dayjs'

const router = useRouter()
const planStore = useLessonPlanStore()

const formRef = ref()
const showPreview = ref(false)
const generatedPlan = ref(null)

const form = ref({
  level: 'high',
  subject: 'math',
  grade: 'grade1',  // 默认高中一年级
  duration: '1',
  topic: '',
  objectives: '',
  requirements: '',
})

const rules = {
  level: [{ required: true, message: '请选择学段' }],
  subject: [{ required: true, message: '请选择学科' }],
  grade: [{ required: true, message: '请选择年级' }],
  topic: [{ required: true, message: '请输入课题', trigger: 'blur' }],
}

// 根据学段获取年级列表
const gradeListMap = {
  primary: ['一年级', '二年级', '三年级', '四年级', '五年级', '六年级'],
  middle: ['初一', '初二', '初三'],
  high: ['高一', '高二', '高三'],
  university: ['大一', '大二', '大三', '大四'],
}

const gradeOptions = computed(() => {
  const list = gradeListMap[form.value.level] || []
  return list.map((label, i) => ({
    label,
    value: `grade${i + 1}`,
  }))
})

// 切换学段时重置年级为该学段第一个年级
function handleLevelChange() {
  if (gradeOptions.value.length > 0) {
    form.value.grade = gradeOptions.value[0].value
  }
}

const stats = ref([
  { label: '本月教案', value: 0, color: '#1971C2' },
  { label: '习题数量', value: 0, color: '#2F9E44' },
  { label: '上课次数', value: 0, color: '#F08C00' },
])

function formatDate(dateStr) {
  if (!dateStr) return ''
  return dayjs(dateStr).format('MM/DD')
}

function statusType(status) {
  const map = { draft: 'info', completed: 'success', archived: '' }
  return map[status] || 'info'
}

function statusLabel(status) {
  const map = { draft: '草稿', completed: '完成', archived: '归档' }
  return map[status] || status
}

async function handleGenerate() {
  await formRef.value?.validate()
  try {
    const plan = await planStore.generatePlan(form.value)
    console.log('Generated plan:', plan)
    generatedPlan.value = plan
    showPreview.value = true
    ElMessage.success('教案生成成功！')
  } catch (e) {
    console.error('Generate error:', e)
    ElMessage.error('教案生成失败')
  }
}

function openEditor() {
  showPreview.value = false
  if (generatedPlan.value?.id) {
    router.push(`/teacher/lesson-plans/${generatedPlan.value.id}/edit`)
  }
}

onMounted(() => {
  planStore.fetchPlans({ page: 1, page_size: 10 })
})
</script>

<style scoped>
.dashboard {
  max-width: 1400px;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 24px;
}
.page-header h2 {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 4px;
}

.form-card {
  height: fit-content;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
}

.stat-card {
  text-align: center;
  padding: 4px 0;
}
:deep(.stat-card .el-card__body) {
  padding: 16px 8px;
}
.stat-value {
  font-size: 28px;
  font-weight: 700;
  line-height: 1;
}
.stat-label {
  font-size: 12px;
  color: #6c757d;
  margin-top: 6px;
}

.plan-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.plan-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s;
}
.plan-item:hover {
  background: #f8f9fa;
}

.plan-title {
  font-size: 14px;
  font-weight: 500;
  color: #343a40;
  margin-bottom: 2px;
}
.plan-meta {
  font-size: 12px;
}

.loading-placeholder {
  padding: 16px 0;
}

.plan-preview-header {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #dee2e6;
}
.plan-preview-header h3 {
  font-size: 18px;
  margin-bottom: 4px;
}

.plan-content {
  padding: 0 4px;
  line-height: 1.8;
}
</style>
