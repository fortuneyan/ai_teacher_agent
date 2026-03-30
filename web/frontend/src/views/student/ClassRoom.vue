<template>
  <div class="classroom-page">
    <div class="page-header">
      <h2>课堂学习</h2>
      <p class="text-muted">加入教师的授课频道，参与实时课堂</p>
    </div>

    <template v-if="!channelStore.channel">
      <el-card style="max-width: 480px; margin: 0 auto; margin-top: 40px;">
        <template #header>
          <span style="font-weight:600;">加入课堂</span>
        </template>
        <el-form label-width="80px">
          <el-form-item label="邀请码">
            <el-input v-model="inviteCode" placeholder="请输入教师提供的邀请码" size="large" clearable />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" size="large" style="width:100%" :loading="joining" @click="handleJoin">
              加入课堂
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </template>

    <template v-else>
      <div class="room-container">
        <div class="room-header">
          <el-tag type="danger" effect="dark">
            <span class="live-dot"></span> 课堂进行中
          </el-tag>
          <span class="room-title">{{ channelStore.channel.title }}</span>
          <el-button size="small" @click="handleLeave">离开课堂</el-button>
        </div>

        <el-row :gutter="16">
          <el-col :span="16">
            <el-card class="slide-card">
              <div class="slide-area">
                <el-icon size="64" color="#dee2e6"><Picture /></el-icon>
                <p class="text-muted">第 {{ channelStore.currentPage + 1 }} 页</p>
                <p class="text-muted" style="font-size:12px;">等待教师同步课件...</p>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card class="chat-card">
              <template #header><span>课堂消息</span></template>
              <el-scrollbar height="300px">
                <div v-for="(msg, i) in channelStore.messages" :key="i" class="msg-item">
                  <span class="msg-sender">{{ msg.sender_name }}：</span>
                  <span>{{ msg.content }}</span>
                </div>
              </el-scrollbar>
              <div class="mt-sm">
                <el-input v-model="chatInput" placeholder="发送消息" size="small" @keyup.enter="sendChat">
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
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useChannelStore } from '@/stores/channel'
import { useChannelWS } from '@/composables/useChannelWS'

const channelStore = useChannelStore()
const inviteCode = ref('')
const joining = ref(false)
const chatInput = ref('')
let ws = null

async function handleJoin() {
  if (!inviteCode.value.trim()) {
    ElMessage.warning('请输入邀请码')
    return
  }
  joining.value = true
  try {
    const channel = await channelStore.joinChannel(inviteCode.value.trim())
    ws = useChannelWS(channel.channel_id)
    ws.connect()
    ElMessage.success('已加入课堂！')
  } catch {
    //
  } finally {
    joining.value = false
  }
}

function handleLeave() {
  ws?.disconnect()
  channelStore.reset()
}

function sendChat() {
  if (!chatInput.value.trim()) return
  ws?.sendChat(chatInput.value.trim())
  chatInput.value = ''
}
</script>

<style scoped>
.classroom-page {}
.page-header { margin-bottom: 24px; }
.page-header h2 { font-size: 20px; font-weight: 600; margin-bottom: 4px; }
.room-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
  padding: 12px 16px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.room-title { flex: 1; font-size: 16px; font-weight: 600; }
.slide-card { height: 400px; }
.slide-area {
  height: 320px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  border-radius: 8px;
  gap: 8px;
}
.live-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  background: #fff;
  border-radius: 50%;
  margin-right: 4px;
  animation: pulse 1.5s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
.msg-item { padding: 4px 8px; font-size: 13px; }
.msg-sender { color: #1971C2; font-weight: 500; }
</style>
