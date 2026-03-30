<template>
  <div class="exercises-page">
    <div class="page-header">
      <div>
        <h2>习题管理</h2>
        <p class="text-muted">AI生成并管理习题库</p>
      </div>
      <el-button type="primary" icon="MagicStick" @click="showGenDialog = true">
        AI生成习题
      </el-button>
    </div>

    <el-card>
      <el-table :data="exercises" v-loading="loading">
        <el-table-column prop="title" label="题目" min-width="240" />
        <el-table-column prop="type" label="题型" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ typeLabel(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="difficulty" label="难度" width="80">
          <template #default="{ row }">
            <el-rate v-model="row.difficulty" :max="4" disabled size="small" />
          </template>
        </el-table-column>
        <el-table-column prop="subject" label="学科" width="80" />
        <el-table-column label="操作" width="120">
          <template #default>
            <el-button text size="small" icon="View">查看</el-button>
            <el-button text size="small" icon="Delete" type="danger">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 生成习题对话框 -->
    <el-dialog v-model="showGenDialog" title="AI生成习题" width="500px">
      <el-form :model="genForm" label-width="80px">
        <el-form-item label="学科">
          <el-select v-model="genForm.subject" style="width:100%">
            <el-option label="数学" value="math" />
            <el-option label="语文" value="chinese" />
            <el-option label="英语" value="english" />
          </el-select>
        </el-form-item>
        <el-form-item label="知识点">
          <el-input v-model="genForm.knowledge" placeholder="例如：一元二次方程" />
        </el-form-item>
        <el-form-item label="题型">
          <el-checkbox-group v-model="genForm.types">
            <el-checkbox label="single_choice">单选</el-checkbox>
            <el-checkbox label="fill_blank">填空</el-checkbox>
            <el-checkbox label="short_answer">简答</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="题目数量">
          <el-input-number v-model="genForm.count" :min="1" :max="20" />
        </el-form-item>
        <el-form-item label="难度">
          <el-radio-group v-model="genForm.difficulty">
            <el-radio-button label="easy">简单</el-radio-button>
            <el-radio-button label="medium">中等</el-radio-button>
            <el-radio-button label="hard">较难</el-radio-button>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showGenDialog = false">取消</el-button>
        <el-button type="primary" :loading="generating" @click="handleGenerate">
          生成习题
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const generating = ref(false)
const showGenDialog = ref(false)

const genForm = ref({
  subject: 'math',
  knowledge: '',
  types: ['single_choice'],
  count: 5,
  difficulty: 'medium',
})

const exercises = ref([
  { id: 1, title: '解方程：x² - 5x + 6 = 0', type: 'calculation', difficulty: 2, subject: '数学' },
  { id: 2, title: '下列哪个函数是奇函数？', type: 'single_choice', difficulty: 1, subject: '数学' },
  { id: 3, title: '已知等差数列 {an}，a₁=2，公差d=3，求a₁₀', type: 'short_answer', difficulty: 2, subject: '数学' },
])

function typeLabel(type) {
  const m = {
    single_choice: '单选',
    multi_choice: '多选',
    fill_blank: '填空',
    judge: '判断',
    short_answer: '简答',
    calculation: '计算',
  }
  return m[type] || type
}

async function handleGenerate() {
  if (!genForm.value.knowledge) {
    ElMessage.warning('请输入知识点')
    return
  }
  generating.value = true
  try {
    await new Promise(r => setTimeout(r, 1500))
    ElMessage.success('习题生成成功！')
    showGenDialog.value = false
  } finally {
    generating.value = false
  }
}
</script>

<style scoped>
.exercises-page {}
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 24px;
}
.page-header h2 { font-size: 20px; font-weight: 600; margin-bottom: 4px; }
</style>
