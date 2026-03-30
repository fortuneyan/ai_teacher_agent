import { defineStore } from 'pinia'
import { ref } from 'vue'
import { channelAPI } from '@/api/channel'

export const useChannelStore = defineStore('channel', () => {
  const channel = ref(null)
  const members = ref([])
  const messages = ref([])
  const currentPage = ref(0)
  const isConnected = ref(false)
  const ws = ref(null)

  function setChannel(data) {
    channel.value = data
  }

  function setConnected(val) {
    isConnected.value = val
  }

  function addMember(member) {
    const exists = members.value.find(m => m.user_id === member.user_id)
    if (!exists) members.value.push(member)
  }

  function removeMember(userId) {
    members.value = members.value.filter(m => m.user_id !== userId)
  }

  function addMessage(msg) {
    messages.value.push(msg)
    if (messages.value.length > 500) {
      messages.value.shift()
    }
  }

  function setCurrentPage(page) {
    currentPage.value = page
  }

  async function createChannel(data) {
    const result = await channelAPI.create(data)
    channel.value = result
    return result
  }

  async function joinChannel(inviteCode) {
    // 学生通过邀请码加入：先找频道，再加入
    const result = await channelAPI.join('by-invite', inviteCode)
    channel.value = result
    return result
  }

  function reset() {
    channel.value = null
    members.value = []
    messages.value = []
    currentPage.value = 0
    isConnected.value = false
    if (ws.value) {
      ws.value.close()
      ws.value = null
    }
  }

  return {
    channel,
    members,
    messages,
    currentPage,
    isConnected,
    ws,
    setChannel,
    setConnected,
    addMember,
    removeMember,
    addMessage,
    setCurrentPage,
    createChannel,
    joinChannel,
    reset,
  }
})
