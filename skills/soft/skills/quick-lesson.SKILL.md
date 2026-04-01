---
name: quick-lesson
version: "1.0.0"
display_name: 快速备课
description: 根据主题快速生成一节课的简要教案，包含教学目标、重点难点和教学流程
category: workflow
author: custom
tags:
  - 备课
  - 教案
  - 快速
triggers:
  - "快速备课"
  - "简单教案"
  - "简要教案"
parameters:
  - name: topic
    type: string
    required: true
    description: 课程主题
  - name: subject
    type: string
    required: false
    description: 学科名称
  - name: duration
    type: number
    required: false
    default: 45
    description: 课时长（分钟）
---

# 快速备课助手

## 能力描述

根据用户提供的主题，快速生成一节课的简要教案。适合时间紧迫或初步备课场景。

## 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| topic | string | 是 | 课程主题 |
| subject | string | 否 | 学科名称（如未提供将根据主题推断） |
| duration | number | 否 | 课时长（分钟），默认45 |

## 返回格式

返回 Markdown 格式的简要教案，包含以下部分：

- 教学目标
- 教学重点
- 教学难点
- 教学流程（时间分配）
- 课堂小结

## 示例

**输入：**
```
topic: 光的折射
subject: 物理
duration: 40
```

**输出：**
```markdown
# 《光的折射》教案

## 教学目标
1. 理解光的折射现象
2. 掌握折射定律
3. 能够解释生活中的折射现象

## 教学重点
- 折射定律的理解与应用

## 教学难点
- 折射角与入射角的关系

## 教学流程（40分钟）
| 时间 | 环节 | 内容 |
|------|------|------|
| 5min | 导入 | 展示筷子在水中弯折的现象 |
| 10min | 新课 | 讲解折射定律 |
| 15min | 练习 | 典型例题分析 |
| 10min | 小结 | 梳理知识点 |

## 课堂小结
1. 折射现象定义
2. 折射定律要点
3. 生活中折射实例
```

## 注意事项

- 教案应简洁明了，适合快速参考
- 突出重点和难点
- 时间分配要合理
