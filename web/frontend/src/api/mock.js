/**
 * Mock 数据服务
 * 在后端未启动时提供演示数据
 * 使用 localStorage 实现数据持久化
 */

const MOCK_DELAY = 800  // 模拟网络延迟
const STORAGE_KEY = 'ai_teacher_plans'

export const mockDelay = (ms = MOCK_DELAY) => new Promise(r => setTimeout(r, ms))

// 从 localStorage 加载数据
function loadPlansFromStorage() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      return JSON.parse(stored)
    }
  } catch (e) {
    console.warn('Failed to load plans from localStorage:', e)
  }
  return null
}

// 保存数据到 localStorage
function savePlansToStorage(plans) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(plans))
  } catch (e) {
    console.warn('Failed to save plans to localStorage:', e)
  }
}

// 初始化 mock 数据（仅在首次使用时）
const defaultPlans = [
  {
    id: 1,
    title: '函数的概念与表示',
    subject: 'math',
    grade: '高一',
    level: 'high',
    topic: '函数的概念与表示',
    duration: 1,
    objectives: '理解函数的概念，掌握函数的三种表示方法',
    status: 'completed',
    ai_generated: true,
    created_at: new Date(Date.now() - 86400000 * 2).toISOString(),
  },
  {
    id: 2,
    title: '一元二次方程的解法',
    subject: 'math',
    grade: '初三',
    level: 'middle',
    topic: '一元二次方程',
    duration: 2,
    objectives: '掌握配方法、公式法、分解因式法解一元二次方程',
    status: 'draft',
    ai_generated: true,
    created_at: new Date(Date.now() - 86400000).toISOString(),
  },
  {
    id: 3,
    title: '细胞的结构与功能',
    subject: 'biology',
    grade: '高二',
    level: 'high',
    topic: '细胞的结构与功能',
    duration: 1,
    objectives: '了解细胞各部分结构及其功能',
    status: 'completed',
    ai_generated: false,
    created_at: new Date().toISOString(),
  },
]

// 使用持久化的数据或默认数据
let mockPlans = loadPlansFromStorage() || [...defaultPlans]
let nextPlanId = Math.max(4, ...mockPlans.map(p => p.id)) + 1

// 保存到 localStorage
function persistPlans() {
  savePlansToStorage(mockPlans)
}

// Mock 生成教案
export const mockGeneratePlan = async (params) => {
  await mockDelay(1500)
  const plan = {
    id: nextPlanId++,
    title: `${params.topic || '新课题'} - 教案`,
    subject: params.subject || 'math',
    grade: params.grade || '高一',
    level: params.level || 'high',
    topic: params.topic,
    duration: parseInt(params.duration) || 1,
    objectives: params.objectives || `通过本节课学习，学生将能够：
1. 理解${params.topic}的基本概念
2. 掌握相关的核心知识点
3. 能够运用所学知识解决实际问题`,
    content: `# ${params.topic} 教案

## 一、教学目标

**知识与技能目标**
- 理解${params.topic}的基本概念和性质
- 掌握相关定理和公式的推导过程
- 能够运用所学知识解决实际问题

**过程与方法目标**
- 通过探究活动，培养学生的逻辑推理能力
- 通过小组讨论，提高学生的合作交流能力

**情感态度目标**
- 激发学生学习数学的兴趣
- 培养严谨求实的科学态度

## 二、教学重难点

**教学重点**：${params.topic}的概念理解和基本应用

**教学难点**：抽象概念的具体化理解

## 三、教学过程

### 1. 导入新课（5分钟）
通过生活实例引入本节课的主题，激发学生的学习兴趣。

### 2. 新课讲授（25分钟）
**（1）概念引入**
结合具体例子，引导学生理解${params.topic}的基本概念。

**（2）性质探究**
通过例题分析，总结${params.topic}的重要性质。

**（3）例题讲解**
- 例题1：基础应用题
- 例题2：综合提高题

### 3. 练习巩固（10分钟）
布置课堂练习，检验学生的掌握情况。

### 4. 总结提升（5分钟）
师生共同总结本节课的重点内容，布置课后作业。

## 四、板书设计

${params.topic}
├── 概念定义
├── 基本性质
└── 典型例题

## 五、作业布置
课后习题第1-5题`,
    content_html: `<h1>${params.topic} 教案</h1><p>（AI生成内容）</p>`,
    status: 'draft',
    ai_generated: true,
    created_at: new Date().toISOString(),
  }
  mockPlans.unshift(plan)
  persistPlans()
  return plan
}

// Mock 教案列表
export const mockGetPlans = async (params = {}) => {
  await mockDelay(400)
  return {
    items: mockPlans.slice(0, params.page_size || 20),
    total: mockPlans.length,
    page: params.page || 1,
  }
}

// Mock 单个教案
export const mockGetPlan = async (id) => {
  await mockDelay(300)
  const plan = mockPlans.find(p => p.id == id)
  if (!plan) throw new Error('教案不存在')
  return plan
}

// Mock 更新教案
export const mockUpdatePlan = async (id, data) => {
  await mockDelay(300)
  const index = mockPlans.findIndex(p => p.id == id)
  if (index === -1) throw new Error('教案不存在')
  mockPlans[index] = { ...mockPlans[index], ...data }
  persistPlans()
  return mockPlans[index]
}

// Mock 删除教案
export const mockDeletePlan = async (id) => {
  await mockDelay(300)
  const index = mockPlans.findIndex(p => p.id == id)
  if (index === -1) throw new Error('教案不存在')
  mockPlans.splice(index, 1)
  persistPlans()
  return { success: true }
}

// Mock 用户登录
export const mockLogin = async (credentials) => {
  await mockDelay(600)
  const accounts = {
    teacher01: { id: 1, username: 'teacher01', name: '张老师', role: 'teacher' },
    student01: { id: 2, username: 'student01', name: '王小明', role: 'student' },
    admin: { id: 3, username: 'admin', name: '管理员', role: 'admin' },
  }
  const user = accounts[credentials.username]
  if (!user || credentials.password !== 'demo123' && credentials.password !== 'admin123') {
    throw new Error('用户名或密码错误')
  }
  return {
    access_token: `mock_token_${user.role}_${Date.now()}`,
    token_type: 'bearer',
    user: { ...user, is_active: true, created_at: new Date().toISOString() },
  }
}
