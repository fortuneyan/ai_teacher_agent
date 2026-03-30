import { ref, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useChannelStore } from '@/stores/channel'
import { ElMessage } from 'element-plus'

/**
 * WebSocket频道连接 composable
 * 管理实时授课频道的 WebSocket 连接
 */
export function useChannelWS(channelId) {
  const authStore = useAuthStore()
  const channelStore = useChannelStore()

  const socket = ref(null)
  const reconnectTimer = ref(null)
  const reconnectCount = ref(0)
  const MAX_RECONNECT = 5

  function connect() {
    if (socket.value?.readyState === WebSocket.OPEN) return

    const wsUrl = `${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/ws/channel/${channelId}?token=${authStore.token}`
    socket.value = new WebSocket(wsUrl)

    socket.value.onopen = () => {
      channelStore.setConnected(true)
      reconnectCount.value = 0
      console.log(`[WS] 已连接到频道 ${channelId}`)
    }

    socket.value.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data)
        handleMessage(msg)
      } catch (e) {
        console.error('[WS] 消息解析失败', e)
      }
    }

    socket.value.onclose = (event) => {
      channelStore.setConnected(false)
      if (!event.wasClean && reconnectCount.value < MAX_RECONNECT) {
        const delay = Math.min(1000 * 2 ** reconnectCount.value, 30000)
        reconnectCount.value++
        console.log(`[WS] 连接断开，${delay / 1000}s 后重连 (${reconnectCount.value}/${MAX_RECONNECT})`)
        reconnectTimer.value = setTimeout(connect, delay)
      } else if (reconnectCount.value >= MAX_RECONNECT) {
        ElMessage.error('网络连接失败，请刷新页面重试')
      }
    }

    socket.value.onerror = (err) => {
      console.error('[WS] 连接错误', err)
    }
  }

  function handleMessage(msg) {
    switch (msg.type) {
      case 'member_join':
        channelStore.addMember(msg.data)
        break
      case 'member_leave':
        channelStore.removeMember(msg.data.user_id)
        break
      case 'page_sync':
        channelStore.setCurrentPage(msg.data.page)
        break
      case 'chat':
        channelStore.addMessage(msg.data)
        break
      case 'quiz_start':
        channelStore.addMessage({ type: 'quiz', ...msg.data })
        break
      case 'quiz_stats':
        channelStore.addMessage({ type: 'quiz_stats', ...msg.data })
        break
      case 'channel_end':
        ElMessage.info('课堂已结束')
        channelStore.reset()
        break
      default:
        channelStore.addMessage(msg)
    }
  }

  function send(type, data = {}) {
    if (socket.value?.readyState === WebSocket.OPEN) {
      socket.value.send(JSON.stringify({ type, data }))
    } else {
      console.warn('[WS] 未连接，无法发送消息')
    }
  }

  function sendPageSync(page) {
    send('page_sync', { page })
  }

  function sendChat(content) {
    send('chat', { content })
  }

  function sendQuizStart(exerciseId) {
    send('quiz_start', { exercise_id: exerciseId })
  }

  function disconnect() {
    clearTimeout(reconnectTimer.value)
    if (socket.value) {
      socket.value.onclose = null // 防止触发重连
      socket.value.close()
      socket.value = null
    }
    channelStore.setConnected(false)
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    connect,
    disconnect,
    send,
    sendPageSync,
    sendChat,
    sendQuizStart,
  }
}
