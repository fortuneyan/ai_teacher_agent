<template>
  <div class="lesson-plans">
    <div class="page-header">
      <div>
        <h2>我的教案</h2>
        <p class="text-muted">管理和编辑您的所有教案</p>
      </div>
      <el-button type="primary" icon="Plus" @click="router.push('/teacher/dashboard')">
        生成新教案
      </el-button>
    </div>

    <!-- 筛选栏 -->
    <el-card class="filter-card mb-md">
      <el-row :gutter="16" align="middle">
        <el-col :span="6">
          <el-input v-model="filters.keyword" placeholder="搜索教案标题..." prefix-icon="Search" clearable @change="fetchData" />
        </el-col>
        <el-col :span="4">
          <el-select v-model="filters.subject" placeholder="学科" clearable @change="fetchData" style="width:100%">
            <el-option label="数学" value="math" />
            <el-option label="语文" value="chinese" />
            <el-option label="英语" value="english" />
            <el-option label="物理" value="physics" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filters.status" placeholder="状态" clearable @change="fetchData" style="width:100%">
            <el-option label="草稿" value="draft" />
            <el-option label="已完成" value="completed" />
            <el-option label="已归档" value="archived" />
          </el-select>
        </el-col>
      </el-row>
    </el-card>

    <!-- 教案列表 -->
    <el-card>
      <el-table
        :data="planStore.plans"
        v-loading="planStore.loading"
        row-class-name="table-row"
        @row-click="openPlan"
        style="cursor:pointer"
      >
        <el-table-column prop="title" label="教案标题" min-width="200">
          <template #default="{ row }">
            <div class="plan-title">{{ row.title }}</div>
            <div class="text-muted" style="font-size:12px;">{{ row.topic }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="subject" label="学科" width="80">
          <template #default="{ row }">
            <el-tag size="small" type="info">{{ subjectLabel(row.subject) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="grade" label="年级" width="80" />
        <el-table-column prop="duration" label="课时" width="80">
          <template #default="{ row }">{{ row.duration }}课时</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="120">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button text size="small" icon="Edit" @click.stop="router.push(`/teacher/lesson-plans/${row.id}/edit`)">编辑</el-button>
            <el-button text size="small" icon="Delete" type="danger" @click.stop="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination mt-md">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="planStore.total"
          layout="total, prev, pager, next"
          @change="fetchData"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useLessonPlanStore } from '@/stores/lessonPlan'
import dayjs from 'dayjs'

const router = useRouter()
const planStore = useLessonPlanStore()

const page = ref(1)
const pageSize = ref(20)
const filters = ref({ keyword: '', subject: '', status: '' })

function fetchData() {
  planStore.fetchPlans({ page: page.value, page_size: pageSize.value, ...filters.value })
}

function openPlan(row) {
  router.push(`/teacher/lesson-plans/${row.id}/edit`)
}

function subjectLabel(s) {
  const m = { math: '数学', chinese: '语文', english: '英语', physics: '物理', chemistry: '化学' }
  return m[s] || s
}

function statusType(s) {
  return { draft: 'info', completed: 'success', archived: '' }[s] || 'info'
}

function statusLabel(s) {
  return { draft: '草稿', completed: '完成', archived: '归档' }[s] || s
}

function formatDate(d) {
  return d ? dayjs(d).format('YYYY/MM/DD') : ''
}

async function handleDelete(row) {
  await ElMessageBox.confirm(`确定删除教案"${row.title}"吗？`, '删除确认', {
    type: 'warning',
    confirmButtonText: '删除',
    confirmButtonClass: 'el-button--danger',
  })
  await planStore.deletePlan(row.id)
  ElMessage.success('已删除')
}

onMounted(fetchData)
</script>

<style scoped>
.lesson-plans {}
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 24px;
}
.page-header h2 { font-size: 20px; font-weight: 600; margin-bottom: 4px; }
.filter-card {}
.plan-title { font-size: 14px; font-weight: 500; }
.pagination { display: flex; justify-content: flex-end; }
</style>
