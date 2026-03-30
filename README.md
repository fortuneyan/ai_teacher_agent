# AI教师Agent - 智能备课助手

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Status](https://img.shields.io/badge/Status-Completed-success.svg)]()
[![Version](https://img.shields.io/badge/Version-1.0-orange.svg)]()

一个基于AI的智能备课助手，帮助教师快速生成符合课程标准的教案，支持用户反馈和自动优化。

## 功能特性

### 核心备课功能
- **智能备课**: 根据课程信息自动生成完整教案
- **课标搜索**: 自动搜索相关课程标准
- **资源推荐**: 推荐PPT、视频、练习题等教学资源
- **反馈优化**: 智能处理用户反馈并自动优化教案
- **完整闭环**: 从输入到优化的完整备课流程

### 测试/讲解模块 (新增)
- **智能出题**: 自动生成9种题型的习题（单选、多选、填空、判断、简答、计算、证明、应用、综合）
- **智能组卷**: 支持7种试卷类型（练习、测验、单元测试、期中、期末、模拟、入学）
- **智能讲解**: 提供概念讲解、例题讲解、习题讲解、错误分析
- **智能评估**: 自动评分、知识点分析、能力维度评估、个性化学习建议

## 快速开始

### 安装

```bash
git clone <repository-url>
cd ai_teacher_agent
pip install -r requirements.txt
```

### 使用

#### 方式1: 运行演示

```bash
# MVP演示
python mvp_demo.py

# 扩展功能演示
python extended_demo.py

# 完整功能演示
python full_demo.py

# 测试/讲解模块演示 (新增)
python assessment_demo.py
```

#### 方式2: Web界面

```bash
# 启动后端
cd web/backend
uvicorn app.main:app --reload --port 8100

# 启动前端 (新终端)
cd web/frontend
npm install
npm run dev
```

访问 http://localhost:5173 使用以下账号登录：

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 教师 | teacher01 | demo123 |
| 学生 | student01 | demo123 |
| 管理员 | admin | admin123 |

#### 方式3: CLI交互

```bash
# 主CLI（包含备课和测试/讲解模块）
python cli.py

# 测试/讲解模块独立CLI
python cli_assessment.py
```

#### 方式3: 代码调用

```python
from models import CourseBasicInfo
from skills import LessonPreparationSkill

# 初始化
skill = LessonPreparationSkill()

# 输入课程信息
course = CourseBasicInfo(
    education_level="高中",
    subject="数学",
    topic="函数的概念"
)

# 搜索课标
_, standards = skill.search_curriculum_standards(course)

# 生成教案
plan = skill.generate_lesson_plan(course, standards)

# 处理反馈
modified_plan, evaluation, update = skill.process_feedback_loop(
    lesson_plan=plan,
    feedback_content="增加更多实际应用的例子"
)
```

## 项目结构

```
ai_teacher_agent/
├── src/
│   ├── models/           # 数据对象层 (16个对象)
│   ├── mocks/            # Mock服务层
│   └── skills/           # 技能层
│       ├── lesson_preparation/   # 备课技能
│       └── teaching_assessment/  # 测试/讲解技能 (新增)
├── tests/                # 测试代码
├── docs/                 # 设计文档
├── mvp_demo.py           # MVP演示
├── extended_demo.py      # 扩展演示
├── full_demo.py          # 完整功能演示
├── assessment_demo.py    # 测试/讲解模块演示 (新增)
├── cli.py                # CLI交互界面
└── cli_assessment.py     # 测试/讲解模块CLI (新增)
```

## 核心功能

### 备课模块

| 功能 | 描述 | 状态 |
|-----|------|------|
| 搜索课标 | 根据学科/年级搜索课程标准 | ✅ |
| 生成教案 | 基于课标自动生成教案 | ✅ |
| 资源搜索 | 推荐教学资源 | ✅ |
| 反馈评估 | 智能评估用户反馈 | ✅ |
| 自动修改 | 根据反馈优化教案 | ✅ |

### 测试/讲解模块 (新增)

| 功能 | 描述 | 状态 |
|-----|------|------|
| 智能出题 | 自动生成9种题型的习题 | ✅ |
| 智能组卷 | 支持7种试卷类型的智能组卷 | ✅ |
| 概念讲解 | 从具体到抽象的多步骤概念讲解 | ✅ |
| 习题讲解 | 针对具体题目的详细讲解 | ✅ |
| 错误分析 | 针对性纠错讲解 | ✅ |
| 智能评估 | 自动评分和多维度分析 | ✅ |
| 学习建议 | 个性化提升方案 | ✅ |

## 数据对象

### 备课模块

- `CourseBasicInfo` - 课程基本信息
- `CurriculumStandard` - 课程标准
- `TeachingResource` - 教学资源
- `TeachingObjectives` - 教学目标
- `LessonPlan` - 教案
- `UserFeedback` - 用户反馈
- `FeedbackEvaluation` - 反馈评估
- `CoursewareOutline` - 课件大纲

### 测试/讲解模块 (新增)

- `Exercise` - 习题
- `ExerciseSet` - 习题集
- `TestPaper` - 试卷
- `TestPaperSection` - 试卷章节
- `TestPaperConfig` - 试卷配置
- `StudentAnswer` - 学生答案
- `TestResult` - 测试结果
- `TeachingExplanation` - 教学讲解
- `ExplanationStep` - 讲解步骤
- `CommonMisconception` - 常见误区
- `StudentQuestion` - 学生提问

## 文档

- [开发准则](docs/DEVELOPMENT_GUIDELINES.md)
- [数据字典](docs/data_dictionary.md)
- [MVP完成报告](docs/MVP_COMPLETION_REPORT.md)
- [最终完成报告](docs/FINAL_COMPLETION_REPORT.md)

## 技术栈

- Python 3.8+
- Dataclasses
- pytest (测试)

## 待办事项

- [ ] 接入真实搜索API
- [ ] 接入真实LLM服务
- [ ] 添加Web界面
- [ ] 添加数据持久化
- [ ] 接入题库API
- [ ] 添加学生管理功能
- [ ] 添加班级成绩分析
- [ ] 添加知识点图谱

## 许可证

MIT License

## 作者

AI教师Agent开发团队
