<template>
  <div class="editor-page">
    <div class="editor-header">
      <el-button icon="ArrowLeft" text @click="router.back()">返回</el-button>
      <div class="editor-title">
        <el-input v-model="plan.title" placeholder="教案标题" class="title-input" />
      </div>
      <div class="editor-actions">
        <el-tag :type="statusType(plan.status)" class="mr-sm">{{ statusLabel(plan.status) }}</el-tag>
        <el-button icon="Download" @click="handleExport">导出</el-button>
        <el-button type="primary" icon="Check" :loading="saving" @click="handleSave">保存</el-button>
      </div>
    </div>

    <div class="editor-body">
      <!-- 教案元信息 -->
      <el-card class="meta-card">
        <el-row :gutter="16">
          <el-col :span="4">
            <el-form-item label="学科">
              <el-select v-model="plan.subject" size="small">
                <el-option label="数学" value="math" />
                <el-option label="语文" value="chinese" />
                <el-option label="英语" value="english" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="年级">
              <el-input v-model="plan.grade" size="small" />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="课时">
              <el-input-number v-model="plan.duration" :min="1" :max="5" size="small" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="教学目标">
              <el-input v-model="plan.objectives" size="small" placeholder="本节课的核心教学目标" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-card>

      <!-- 富文本编辑器 -->
      <el-card class="content-card">
        <template #header>
          <div class="flex-between">
            <span class="card-title">教案内容</span>
            <el-button text size="small" icon="MagicStick" @click="aiRewrite">AI优化</el-button>
          </div>
        </template>
        <div class="editor-toolbar">
          <el-button-group>
            <el-button size="small" icon="Bold" @click="editor?.chain().focus().toggleBold().run()" />
            <el-button size="small" icon="Italic" @click="editor?.chain().focus().toggleItalic().run()" />
          </el-button-group>
          <el-button-group class="ml-sm">
            <el-button size="small" @click="editor?.chain().focus().toggleHeading({ level: 2 }).run()">H2</el-button>
            <el-button size="small" @click="editor?.chain().focus().toggleHeading({ level: 3 }).run()">H3</el-button>
          </el-button-group>
          <el-button-group class="ml-sm">
            <el-button size="small" icon="List" @click="editor?.chain().focus().toggleBulletList().run()" />
          </el-button-group>
        </div>
        <div ref="editorEl" class="editor-content"></div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Editor } from '@tiptap/core'
import StarterKit from '@tiptap/starter-kit'
import { useLessonPlanStore } from '@/stores/lessonPlan'

const route = useRoute()
const router = useRouter()
const planStore = useLessonPlanStore()

const saving = ref(false)
const editorEl = ref()
let editor = null

const plan = ref({
  id: route.params.id,
  title: '加载中...',
  subject: 'math',
  grade: '高一',
  duration: 1,
  objectives: '',
  status: 'draft',
  content: '',
})

function statusType(s) {
  return { draft: 'info', completed: 'success', archived: '' }[s] || 'info'
}
function statusLabel(s) {
  return { draft: '草稿', completed: '完成', archived: '归档' }[s] || s
}

async function handleSave() {
  saving.value = true
  try {
    plan.value.content = editor?.getHTML() || ''
    await planStore.savePlan(plan.value.id, plan.value)
    ElMessage.success('保存成功')
  } finally {
    saving.value = false
  }
}

function handleExport() {
  ElMessage.info('导出功能开发中...')
}

function aiRewrite() {
  ElMessage.info('AI优化功能开发中...')
}

onMounted(async () => {
  // 初始化 TipTap 编辑器
  editor = new Editor({
    element: editorEl.value,
    extensions: [StarterKit],
    content: plan.value.content || '<h2>教学目标</h2><p>本节课学生将能够...</p><h2>教学重难点</h2><h2>教学过程</h2><h3>导入环节</h3><h3>新课讲授</h3><h3>练习巩固</h3><h3>总结提升</h3>',
    editorProps: {
      attributes: {
        class: 'tiptap-editor',
      },
    },
  })

  // 加载教案数据
  if (route.params.id && route.params.id !== 'new') {
    try {
      await planStore.fetchPlan(route.params.id)
      if (planStore.currentPlan) {
        Object.assign(plan.value, planStore.currentPlan)
        editor.commands.setContent(plan.value.content || '')
      }
    } catch {
      // 使用默认内容
    }
  }
})

onBeforeUnmount(() => {
  editor?.destroy()
})
</script>

<style scoped>
.editor-page {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 64px - 48px);
}

.editor-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 0;
  margin-bottom: 16px;
  background: #fff;
  border-radius: 8px;
  padding: 12px 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.editor-title {
  flex: 1;
}

.title-input :deep(.el-input__wrapper) {
  box-shadow: none;
  font-size: 18px;
  font-weight: 600;
}

.editor-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.editor-body {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.meta-card :deep(.el-card__body) {
  padding: 16px;
}

.content-card {
  flex: 1;
}

.editor-toolbar {
  padding: 8px 0;
  border-bottom: 1px solid #dee2e6;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
}

.ml-sm { margin-left: 8px; }
.mr-sm { margin-right: 8px; }
.card-title { font-size: 15px; font-weight: 600; }

:deep(.tiptap-editor) {
  min-height: 400px;
  outline: none;
  line-height: 1.8;
  font-size: 14px;
}

:deep(.tiptap-editor h2) {
  font-size: 18px;
  font-weight: 600;
  margin: 20px 0 10px;
  color: #1971C2;
}

:deep(.tiptap-editor h3) {
  font-size: 15px;
  font-weight: 600;
  margin: 14px 0 8px;
}

:deep(.tiptap-editor p) {
  margin: 6px 0;
  color: #343a40;
}

:deep(.tiptap-editor ul, .tiptap-editor ol) {
  padding-left: 20px;
}
</style>
