<template>
  <div class="teaching-room">
    <!-- 未开始状态 -->
    <template v-if="!channelStore.channel">
      <div class="page-header">
        <div>
          <h2>授课教室</h2>
          <p class="text-muted">创建频道，开始实时授课</p>
        </div>
      </div>

      <el-row :gutter="24">
        <el-col :xs="24" :lg="12">
          <el-card>
            <template #header>
              <span class="card-title">创建授课频道</span>
            </template>
            <el-form :model="createForm" label-width="80px">
              <el-form-item label="课程名称">
                <el-input v-model="createForm.title" placeholder="例如：高一数学-函数概念" />
              </el-form-item>
              <el-form-item label="选择教案">
                <el-select v-model="createForm.lessonPlanId" placeholder="选择本次课使用的教案" style="width:100%">
                  <el-option
                    v-for="plan in planStore.plans"
                    :key="plan.id"
                    :label="plan.title"
                    :value="plan.id"
                  />
                </el-select>
              </el-form-item>
              <el-form-item label="最大人数">
                <el-input-number v-model="createForm.maxStudents" :min="1" :max="100" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" size="large" icon="VideoCamera" :loading="creating" @click="handleCreate" style="width:100%">
                  开始授课
                </el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>

        <el-col :xs="24" :lg="12">
          <el-card>
            <template #header>
              <span class="card-title">最近课堂记录</span>
            </template>
            <el-empty description="暂无记录" :image-size="80" />
          </el-card>
        </el-col>
      </el-row>
    </template>

    <!-- 授课中状态 -->
    <template v-else>
      <div class="room-container">
        <!-- 顶部工具栏 -->
        <div class="room-toolbar">
          <div class="room-info">
            <el-tag type="danger" effect="dark" class="live-badge">
              <span class="live-dot"></span> 直播中
            </el-tag>
            <span class="room-title">{{ channelStore.channel.title }}</span>
            <el-tag type="info" size="small">
              邀请码：{{ channelStore.channel.invite_code }}
            </el-tag>
          </div>
          <div class="room-actions">
            <el-tooltip content="同步页面到所有学生">
              <el-button icon="Refresh" size="small" @click="syncCurrentPage">同步页面</el-button>
            </el-tooltip>
            <el-button icon="Collection" size="small" @click="showQuizPanel = !showQuizPanel">
              随堂测试
            </el-button>
            <el-button type="danger" icon="SwitchButton" size="small" @click="handleEndClass">
              结束授课
            </el-button>
          </div>
        </div>

        <el-row :gutter="16" class="room-body">
          <!-- 课件区域 -->
          <el-col :span="16">
            <el-card class="courseware-card">
              <template #header>
                <div class="flex-between">
                  <span>课件展示</span>
                  <div class="page-controls">
                    <el-button icon="ArrowLeft" :disabled="currentPage <= 0" size="small" @click="prevPage" />
                    <span class="page-num">{{ currentPage + 1 }} / {{ totalPages }}</span>
                    <el-button icon="ArrowRight" :disabled="currentPage >= totalPages - 1" size="small" @click="nextPage" />
                  </div>
                </div>
              </template>
              <div class="courseware-content">
                <div class="slide-placeholder">
                  <el-icon size="64" color="#dee2e6"><Picture /></el-icon>
                  <p class="text-muted">第 {{ currentPage + 1 }} 页</p>
                </div>
              </div>
            </el-card>
          </el-col>

          <!-- 右侧面板 -->
          <el-col :span="8">
            <!-- 学生列表 -->
            <el-card class="students-card">
              <template #header>
                <div class="flex-between">
                  <span>在线学生 ({{ channelStore.members.length }})</span>
                  <el-badge :value="channelStore.members.length" type="success" />
                </div>
              </template>
              <el-scrollbar height="200px">
                <div v-if="channelStore.members.length === 0" class="text-muted" style="text-align:center;padding:16px;">
                  等待学生加入...
                </div>
                <div v-for="member in channelStore.members" :key="member.user_id" class="student-item">
                  <el-avatar size="small">{{ member.name?.[0] }}</el-avatar>
                  <span class="student-name">{{ member.name }}</span>
                  <el-tag size="small" type="success">在线</el-tag>
                </div>
              </el-scrollbar>
            </el-card>

            <!-- 聊天/互动 -->
            <el-card class="chat-card mt-md">
              <template #header>
                <span>课堂互动</span>
              </template>
              <el-scrollbar ref="chatScrollRef" height="200px" class="chat-messages">
                <div v-for="(msg, i) in channelStore.messages" :key="i" class="message-item">
                  <span class="msg-sender">{{ msg.sender_name }}：</span>
                  <span class="msg-content">{{ msg.content }}</span>
                </div>
                <div v-if="channelStore.messages.length === 0" class="text-muted" style="text-align:center;padding:16px;">
                  暂无消息
                </div>
              </el-scrollbar>
              <div class="chat-input mt-sm">
                <el-input
                  v-model="chatInput"
                  placeholder="发送消息..."
                  size="small"
                  @keyup.enter="sendChat"
                >
                  <template #append>
                    <el-button icon="Promotion" @click="sendChat" />
                  </template>
                </el-input>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useChannelStore } from '@/stores/channel'
import { useLessonPlanStore } from '@/stores/lessonPlan'
import { useChannelWS } from '@/composables/useChannelWS'

const channelStore = useChannelStore()
const planStore = useLessonPlanStore()

const creating = ref(false)
const showQuizPanel = ref(false)
const chatInput = ref('')
const chatScrollRef = ref()
const currentPage = ref(0)
const totalPages = ref(10)

const createForm = ref({
  title: '',
  lessonPlanId: null,
  maxStudents: 50,
})

let ws = null

async function handleCreate() {
  if (!createForm.value.title) {
    ElMessage.warning('请输入课程名称')
    return
  }
  creating.value = true
  try {
    const channel = await channelStore.createChannel(createForm.value)
    // 连接 WebSocket
    ws = useChannelWS(channel.channel_id)
    ws.connect()
    ElMessage.success(`频道创建成功！邀请码：${channel.invite_code}`)
  } catch {
    //
  } finally {
    creating.value = false
  }
}

function prevPage() {
  if (currentPage.value > 0) {
    currentPage.value--
    ws?.sendPageSync(currentPage.value)
  }
}

function nextPage() {
  if (currentPage.value < totalPages.value - 1) {
    currentPage.value++
    ws?.sendPageSync(currentPage.value)
  }
}

function syncCurrentPage() {
  ws?.sendPageSync(currentPage.value)
  ElMessage.success('页面已同步到所有学生')
}

function sendChat() {
  if (!chatInput.value.trim()) return
  ws?.sendChat(chatInput.value.trim())
  chatInput.value = ''
}

async function handleEndClass() {
  await ElMessageBox.confirm('确定结束本次授课吗？', '结束授课', {
    confirmButtonText: '确定结束',
    cancelButtonText: '取消',
    type: 'warning',
  })
  ws?.disconnect()
  channelStore.reset()
  ElMessage.success('授课已结束')
}

// 自动滚动聊天
watch(() => channelStore.messages.length, () => {
  nextTick(() => {
    chatScrollRef.value?.setScrollTop(99999)
  })
})

onMounted(() => {
  planStore.fetchPlans({ page: 1, page_size: 50 })
})
</script>

<style scoped>
.teaching-room {
  height: 100%;
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

.card-title {
  font-size: 15px;
  font-weight: 600;
}

/* 授课中布局 */
.room-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: #fff;
  border-radius: 8px;
  margin-bottom: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.room-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.room-title {
  font-size: 16px;
  font-weight: 600;
  color: #343a40;
}

.room-actions {
  display: flex;
  gap: 8px;
}

.live-badge {
  display: flex;
  align-items: center;
  gap: 6px;
}

.live-dot {
  width: 8px;
  height: 8px;
  background: #fff;
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.courseware-card {
  height: calc(100vh - 240px);
}

.courseware-content {
  display: flex;
  align-items: center;
  justify-content: center;
  height: calc(100vh - 340px);
  background: #f8f9fa;
  border-radius: 8px;
}

.slide-placeholder {
  text-align: center;
}

.page-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-num {
  font-size: 13px;
  color: #6c757d;
  min-width: 60px;
  text-align: center;
}

.student-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border-radius: 4px;
}
.student-item:hover {
  background: #f8f9fa;
}

.student-name {
  flex: 1;
  font-size: 13px;
}

.chat-messages {
  padding: 4px 0;
}

.message-item {
  padding: 4px 8px;
  font-size: 13px;
  line-height: 1.6;
}

.msg-sender {
  color: #1971C2;
  font-weight: 500;
}

.msg-content {
  color: #343a40;
}
</style>
