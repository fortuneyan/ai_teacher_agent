import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    redirect: '/login',
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { requiresAuth: false },
  },
  // 教师端
  {
    path: '/teacher',
    component: () => import('@/layouts/TeacherLayout.vue'),
    meta: { requiresAuth: true, role: 'teacher' },
    redirect: '/teacher/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'TeacherDashboard',
        component: () => import('@/views/teacher/Dashboard.vue'),
        meta: { title: '备课工作台', icon: 'EditPen' },
      },
      {
        path: 'lesson-plans',
        name: 'LessonPlans',
        component: () => import('@/views/teacher/LessonPlans.vue'),
        meta: { title: '我的教案', icon: 'Document' },
      },
      {
        path: 'lesson-plans/:id/edit',
        name: 'LessonPlanEditor',
        component: () => import('@/views/teacher/LessonPlanEditor.vue'),
        meta: { title: '编辑教案', hidden: true },
      },
      {
        path: 'exercises',
        name: 'TeacherExercises',
        component: () => import('@/views/teacher/Exercises.vue'),
        meta: { title: '习题管理', icon: 'Collection' },
      },
      {
        path: 'teaching-room',
        name: 'TeachingRoom',
        component: () => import('@/views/teacher/TeachingRoom.vue'),
        meta: { title: '授课教室', icon: 'VideoCamera' },
      },
      {
        path: 'analytics',
        name: 'Analytics',
        component: () => import('@/views/teacher/Analytics.vue'),
        meta: { title: '学情分析', icon: 'TrendCharts' },
      },
    ],
  },
  // 学生端
  {
    path: '/student',
    component: () => import('@/layouts/StudentLayout.vue'),
    meta: { requiresAuth: true, role: 'student' },
    redirect: '/student/classroom',
    children: [
      {
        path: 'classroom',
        name: 'StudentClassroom',
        component: () => import('@/views/student/ClassRoom.vue'),
        meta: { title: '课堂学习', icon: 'School' },
      },
      {
        path: 'exercises',
        name: 'StudentExercises',
        component: () => import('@/views/student/Exercises.vue'),
        meta: { title: '习题练习', icon: 'EditPen' },
      },
      {
        path: 'progress',
        name: 'MyProgress',
        component: () => import('@/views/student/MyProgress.vue'),
        meta: { title: '学习进度', icon: 'TrendCharts' },
      },
    ],
  },
  // 管理端
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAuth: true, role: 'admin' },
    redirect: '/admin/users',
    children: [
      {
        path: 'users',
        name: 'UserManage',
        component: () => import('@/views/admin/UserManage.vue'),
        meta: { title: '用户管理', icon: 'User' },
      },
      {
        path: 'system',
        name: 'SystemConfig',
        component: () => import('@/views/admin/SystemConfig.vue'),
        meta: { title: '系统配置', icon: 'Setting' },
      },
    ],
  },
  // 404
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }
  
  if (to.name === 'Login' && authStore.isLoggedIn) {
    const role = authStore.user?.role
    if (role === 'teacher') next('/teacher/dashboard')
    else if (role === 'student') next('/student/classroom')
    else if (role === 'admin') next('/admin/users')
    else next()
    return
  }
  
  next()
})

export default router
