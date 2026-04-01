---
name: student-feedback
version: "1.0.0"
display_name: 学生反馈分析
description: 分析学生对课程内容的反馈，提取关键信息和改进建议
category: utility
author: custom
tags:
  - 学生
  - 反馈
  - 分析
triggers:
  - "学生反馈"
  - "分析反馈"
  - "课堂反馈"
parameters:
  - name: feedback_text
    type: string
    required: true
    description: 学生反馈的原始文本
  - name: include_suggestions
    type: boolean
    required: false
    default: true
    description: 是否包含改进建议
---

# 学生反馈分析助手

## 能力描述

分析学生对课程内容的反馈，识别：
- 理解较好的知识点
- 存在困难的知识点
- 学生的具体问题
- 改进教学的建议

## 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| feedback_text | string | 是 | 学生反馈的原始文本 |
| include_suggestions | boolean | 否 | 是否包含改进建议，默认是 |

## 返回格式

返回 JSON 格式的分析结果：

```json
{
  "summary": "学生对本次课程的总体反馈摘要",
  "positive_points": [
    "学生认为掌握较好的知识点"
  ],
  "difficult_points": [
    "学生反映存在困难的知识点"
  ],
  "questions": [
    "学生提出的具体问题"
  ],
  "suggestions": [
    "针对教学的改进建议"
  ]
}
```

## 示例

**输入：**
```
feedback_text: "老师讲的函数概念很清楚，但是在做题的时候还是不太会应用。概念部分的例题很好懂，但是变式题就不知道从哪里下手了。希望老师能多讲一些解题技巧。"
```

**输出：**
```json
{
  "summary": "学生基本理解函数概念，但在应用和解题方面存在困难，需要更多解题技巧指导。",
  "positive_points": [
    "函数基本概念理解较好",
    "课堂例题讲解清晰易懂"
  ],
  "difficult_points": [
    "函数的实际应用",
    "变式题的解题思路"
  ],
  "questions": [
    "变式题不知道从哪里下手"
  ],
  "suggestions": [
    "增加解题技巧和方法的教学",
    "提供更多同类型题目的练习",
    "增加从基础到提高的过渡性例题"
  ]
}
```

## 使用场景

- 分析单个学生的反馈
- 批量分析多个学生的反馈
- 为教师调整教学提供依据
