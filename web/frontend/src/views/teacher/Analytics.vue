<template>
  <div class="analytics-page">
    <div class="page-header">
      <div>
        <h2>学情分析</h2>
        <p class="text-muted">班级学习数据可视化</p>
      </div>
    </div>

    <!-- 概览统计 -->
    <el-row :gutter="16" class="mb-lg">
      <el-col :xs="12" :sm="6" v-for="card in overviewCards" :key="card.label">
        <el-card class="overview-card">
          <div class="overview-icon" :style="{ background: card.bg }">
            <el-icon :size="24" :color="card.color">
              <component :is="card.icon" />
            </el-icon>
          </div>
          <div class="overview-info">
            <div class="overview-value">{{ card.value }}</div>
            <div class="overview-label">{{ card.label }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="24">
      <!-- 分数分布图 -->
      <el-col :xs="24" :lg="12">
        <el-card>
          <template #header>
            <span class="card-title">成绩分布</span>
          </template>
          <v-chart :option="scoreDistChartOption" style="height: 280px" autoresize />
        </el-card>
      </el-col>

      <!-- 知识点掌握度 -->
      <el-col :xs="24" :lg="12">
        <el-card>
          <template #header>
            <span class="card-title">知识点掌握度</span>
          </template>
          <v-chart :option="knowledgeChartOption" style="height: 280px" autoresize />
        </el-card>
      </el-col>
    </el-row>

    <!-- 学生详情表 -->
    <el-card class="mt-lg">
      <template #header>
        <span class="card-title">学生详情</span>
      </template>
      <el-table :data="studentData" border>
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="score" label="平均分" width="80">
          <template #default="{ row }">
            <span :class="scoreClass(row.score)">{{ row.score }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="exercises" label="完成题数" width="100" />
        <el-table-column prop="accuracy" label="正确率" width="100">
          <template #default="{ row }">
            <el-progress :percentage="row.accuracy" :color="progressColor(row.accuracy)" />
          </template>
        </el-table-column>
        <el-table-column prop="trend" label="趋势" width="80">
          <template #default="{ row }">
            <el-tag :type="row.trend > 0 ? 'success' : row.trend < 0 ? 'danger' : 'info'" size="small">
              {{ row.trend > 0 ? '↑ 上升' : row.trend < 0 ? '↓ 下降' : '— 持平' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastActivity" label="最近活动" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, RadarChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent, RadarComponent } from 'echarts/components'

use([CanvasRenderer, BarChart, RadarChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent, RadarComponent])

const overviewCards = ref([
  { label: '班级人数', value: 42, icon: 'User', color: '#1971C2', bg: '#e8f0fe' },
  { label: '本月平均分', value: '78.5', icon: 'TrendCharts', color: '#2F9E44', bg: '#e6f4ea' },
  { label: '完成习题', value: 256, icon: 'EditPen', color: '#F08C00', bg: '#fef3e2' },
  { label: '需关注学生', value: 5, icon: 'Warning', color: '#E03131', bg: '#fce8e6' },
])

const scoreDistChartOption = ref({
  tooltip: { trigger: 'axis' },
  xAxis: {
    type: 'category',
    data: ['<60', '60-69', '70-79', '80-89', '90-100'],
  },
  yAxis: { type: 'value', name: '人数' },
  series: [{
    type: 'bar',
    data: [3, 5, 14, 15, 5],
    itemStyle: {
      color: (params) => {
        const colors = ['#E03131', '#F08C00', '#1971C2', '#1971C2', '#2F9E44']
        return colors[params.dataIndex]
      },
    },
    label: { show: true, position: 'top' },
  }],
})

const knowledgeChartOption = ref({
  tooltip: {},
  radar: {
    indicator: [
      { name: '函数概念', max: 100 },
      { name: '方程与不等式', max: 100 },
      { name: '数列', max: 100 },
      { name: '三角函数', max: 100 },
      { name: '向量', max: 100 },
      { name: '概率统计', max: 100 },
    ],
  },
  series: [{
    type: 'radar',
    data: [{
      value: [85, 72, 68, 91, 76, 63],
      name: '班级平均',
      areaStyle: { color: 'rgba(25, 113, 194, 0.2)' },
      lineStyle: { color: '#1971C2' },
    }],
  }],
})

const studentData = ref([
  { name: '张小明', score: 92, exercises: 38, accuracy: 88, trend: 1, lastActivity: '2小时前' },
  { name: '李小华', score: 85, exercises: 35, accuracy: 82, trend: 0, lastActivity: '1天前' },
  { name: '王小红', score: 76, exercises: 30, accuracy: 75, trend: -1, lastActivity: '3小时前' },
  { name: '赵小强', score: 61, exercises: 22, accuracy: 58, trend: -1, lastActivity: '2天前' },
  { name: '陈小丽', score: 95, exercises: 42, accuracy: 93, trend: 1, lastActivity: '30分钟前' },
])

function scoreClass(score) {
  if (score >= 90) return 'text-success'
  if (score >= 70) return 'text-primary'
  if (score >= 60) return 'text-warning'
  return 'text-danger'
}

function progressColor(val) {
  if (val >= 80) return '#2F9E44'
  if (val >= 60) return '#1971C2'
  if (val >= 40) return '#F08C00'
  return '#E03131'
}
</script>

<style scoped>
.analytics-page {}
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 24px;
}
.page-header h2 { font-size: 20px; font-weight: 600; margin-bottom: 4px; }

.card-title { font-size: 15px; font-weight: 600; }

.overview-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
}

.overview-icon {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.overview-value {
  font-size: 26px;
  font-weight: 700;
  color: #343a40;
  line-height: 1;
}
.overview-label {
  font-size: 13px;
  color: #6c757d;
  margin-top: 4px;
}
</style>
