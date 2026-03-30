<template>
  <div>
    <h2 style="margin-bottom:24px;">用户管理</h2>
    <el-card>
      <el-table :data="users" border>
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="name" label="姓名" />
        <el-table-column prop="role" label="角色">
          <template #default="{ row }">
            <el-tag :type="row.role==='teacher'?'primary':row.role==='admin'?'danger':'success'">
              {{ { teacher:'教师', student:'学生', admin:'管理员' }[row.role] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="row.status==='active'?'success':'info'">{{ row.status==='active'?'正常':'停用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作">
          <template #default>
            <el-button text size="small">编辑</el-button>
            <el-button text size="small" type="danger">停用</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>
<script setup>
import { ref } from 'vue'
const users = ref([
  { username: 'teacher01', name: '张老师', role: 'teacher', status: 'active' },
  { username: 'teacher02', name: '李老师', role: 'teacher', status: 'active' },
  { username: 'student01', name: '王小明', role: 'student', status: 'active' },
  { username: 'admin', name: '系统管理员', role: 'admin', status: 'active' },
])
</script>
