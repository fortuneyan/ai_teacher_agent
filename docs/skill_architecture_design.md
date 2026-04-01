# 双层 Skill 架构设计

> AI Teacher Agent - Native Skill + Soft Skill 双层架构

## 一、架构概览

```
ai_teacher_agent/
├── skills/
│   │
│   ├── _base/                        # 🔧 核心框架
│   │   ├── __init__.py
│   │   ├── base.py                   # BaseSkill 抽象基类
│   │   ├── metadata.py               # SkillMetadata 标准定义
│   │   ├── registry.py               # SkillRegistry 注册中心
│   │   ├── native_loader.py          # Native Skill 加载器
│   │   └── soft_loader.py            # Soft Skill (SKILL.md) 加载器
│   │
│   ├── native/                       # 📦 Native Skills（内置硬编码）
│   │   ├── __init__.py              # 统一导出所有 native skills
│   │   ├── lesson_preparation/       # 智能备课
│   │   ├── teaching_assessment/      # 教学评估
│   │   ├── collect_materials/        # 收集素材
│   │   ├── design_lesson/           # 设计教案
│   │   ├── generate_ppt/             # 生成 PPT
│   │   ├── outline_summary/          # 归纳大纲
│   │   └── schedule_plan/            # 进度计划
│   │
│   └── soft/                         # 📝 Soft Skills（SKILL.md）
│       ├── README.md                # Soft Skill 使用指南
│       └── skills/                   # 用户自定义 SKILL.md
│           ├── quick-lesson.SKILL.md
│           ├── student-feedback.SKILL.md
│           └── ...
│
└── skill_templates/                  # 📋 Skill 模板目录
    ├── native_skill_template.py      # Native Skill 模板
    └── soft_skill_template.md        # Soft Skill 模板
```

## 二、核心概念

### 2.1 Native Skill（原生技能）

| 特性 | 说明 |
|------|------|
| **实现方式** | Python 类继承 `BaseSkill` |
| **性能** | 高，直接执行无二次解析 |
| **可控性** | 完全可控，可调试 |
| **适用场景** | 核心业务逻辑、复杂处理 |

```python
# skills/native/lesson_preparation/__init__.py

from skills._base import BaseSkill, SkillMetadata, SkillCategory

class LessonPreparationSkill(BaseSkill):
    """智能备课 - Native Skill"""
    
    metadata = SkillMetadata(
        name="lesson_preparation",
        display_name="智能备课",
        category=SkillCategory.CORE,
        # ... 完整元数据
    )
    
    async def execute(self, context: dict) -> dict:
        # 直接执行复杂逻辑
        pass
```

### 2.2 Soft Skill（软技能）

| 特性 | 说明 |
|------|------|
| **实现方式** | SKILL.md 文档 + LLM 理解 |
| **性能** | 中等，需 LLM 解析 |
| **可控性** | 依赖 LLM，可定制提示 |
| **适用场景** | 简单任务、用户自定义能力 |
| **热插拔** | ✅ 新增/删除文件即可 |

```markdown
<!-- skills/soft/skills/quick-lesson.SKILL.md -->

---
name: quick-lesson
description: 快速生成一节课的简要教案
version: 1.0.0
author: custom
category: workflow
triggers:
  - "快速备课"
  - "简单教案"
parameters:
  - name: topic
    type: string
    required: true
  - name: duration
    type: number
    required: false
    default: 45
---

# 快速备课助手

## 能力描述

根据主题快速生成一节课的简要教案，包含教学目标、重点难点和教学流程。

## 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| topic | string | 是 | 课程主题 |
| duration | number | 否 | 课时长（分钟），默认45 |

## 返回格式

返回 Markdown 格式的简要教案。

## 示例

输入：「快速备课：光的折射」
→ 返回简明教案
```

## 三、核心组件设计

### 3.1 SkillLoader 统一加载器

```python
# skills/_base/registry.py

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Type
from enum import Enum

class SkillType(Enum):
    NATIVE = "native"    # 原生技能
    SOFT = "soft"        # 软技能

class SkillRegistry:
    """统一 Skill 注册中心"""
    
    _native_skills: Dict[str, Type[BaseSkill]] = {}
    _soft_skills: Dict[str, dict] = {}  # SKILL.md 解析结果
    
    @classmethod
    def register_native(cls, skill_class: Type[BaseSkill]):
        """注册 Native Skill"""
        metadata = skill_class.metadata
        cls._native_skills[metadata.name] = skill_class
        
    @classmethod
    def register_soft(cls, skill_data: dict):
        """注册 Soft Skill"""
        cls._soft_skills[skill_data["name"]] = skill_data
        
    @classmethod
    def load_all(cls, soft_skills_dir: str = None):
        """加载所有技能"""
        # 1. 加载 Native Skills（自动扫描）
        cls._discover_native_skills()
        
        # 2. 加载 Soft Skills（从目录）
        if soft_skills_dir:
            cls._load_soft_skills(soft_skills_dir)
    
    @classmethod
    def get(cls, name: str) -> Optional[Type[BaseSkill] | dict]:
        """获取技能（优先 native）"""
        if name in cls._native_skills:
            return cls._native_skills[name]
        return cls._soft_skills.get(name)
    
    @classmethod
    def list_all(cls) -> Dict[str, dict]:
        """列出所有技能"""
        result = {}
        for name, skill_class in cls._native_skills.items():
            result[name] = {
                **skill_class.metadata.to_dict(),
                "type": SkillType.NATIVE.value
            }
        for name, skill_data in cls._soft_skills.items():
            result[name] = {
                **skill_data,
                "type": SkillType.SOFT.value
            }
        return result
```

### 3.2 Soft Skill 执行器

```python
# skills/_base/soft_executor.py

from typing import Dict, Any
from skills._base import skill_registry

class SoftSkillExecutor:
    """Soft Skill 执行器 - 将 SKILL.md 转换为 LLM 可执行的提示"""
    
    def __init__(self, llm_service):
        self.llm_service = llm_service
    
    async def execute(self, skill_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行 Soft Skill"""
        skill_data = skill_registry.get(skill_name)
        if not skill_data:
            raise ValueError(f"Skill '{skill_name}' not found")
        
        if skill_data.get("type") != SkillType.SOFT.value:
            raise ValueError(f"'{skill_name}' is not a Soft Skill")
        
        # 1. 构建执行提示
        prompt = self._build_execution_prompt(skill_data, context)
        
        # 2. 调用 LLM
        result = await self.llm_service.generate(prompt)
        
        # 3. 解析结果
        return self._parse_result(result)
    
    def _build_execution_prompt(self, skill_data: dict, context: dict) -> str:
        """构建执行提示"""
        # 将 SKILL.md 内容转换为 LLM 可执行的提示
        template = f"""
## 任务：执行 {skill_data['display_name']}

### 技能描述
{skill_data.get('description', '')}

### 输入参数
{json.dumps(context, ensure_ascii=False, indent=2)}

### 执行指南
{skill_data.get('content', '')}

### 请按照技能定义执行任务，返回结果。
"""
        return template
```

### 3.3 统一执行接口

```python
# skills/_base/executor.py

from typing import Dict, Any, Optional

class SkillExecutor:
    """统一执行器 - 自动选择 Native 或 Soft Skill"""
    
    def __init__(self, llm_service=None):
        self.llm_service = llm_service
        self._soft_executor = SoftSkillExecutor(llm_service) if llm_service else None
    
    async def execute(self, skill_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行技能（自动选择类型）"""
        skill = skill_registry.get(skill_name)
        
        if skill is None:
            raise ValueError(f"Skill '{skill_name}' not found")
        
        # Native Skill
        if isinstance(skill, type) and issubclass(skill, BaseSkill):
            instance = skill(llm_service=self.llm_service)
            return await instance.execute(context)
        
        # Soft Skill
        if isinstance(skill, dict) and skill.get("type") == SkillType.SOFT.value:
            if not self._soft_executor:
                raise ValueError("Soft Skill requires LLM service")
            return await self._soft_executor.execute(skill_name, context)
        
        raise ValueError(f"Unknown skill type: {skill_name}")
```

## 四、统一导出接口

```python
# skills/__init__.py

"""
AI Teacher Agent - 双层 Skill 架构

支持两种技能类型：
- Native Skill：内置 Python 技能，高性能硬编码
- Soft Skill：OpenClaw SKILL.md 格式，可热插拔
"""

from skills._base import (
    BaseSkill,
    SkillMetadata,
    SkillCategory,
    SkillRegistry,
    SkillType,
    SkillExecutor,
)

# === 导出 Native Skills ===
from skills.native.lesson_preparation import LessonPreparationSkill
from skills.native.teaching_assessment import ExerciseGenerator, TestPaperGenerator

# === 导出快捷方法 ===

def get_skill(name: str):
    """获取技能类"""
    return SkillRegistry.get(name)

def list_skills() -> Dict[str, dict]:
    """列出所有可用技能"""
    return SkillRegistry.list_all()

def execute_skill(name: str, context: dict, llm_service=None) -> dict:
    """统一执行技能"""
    executor = SkillExecutor(llm_service)
    return executor.execute(name, context)

# === 初始化 ===
def init_skills(soft_skills_dir: str = None):
    """初始化所有技能"""
    SkillRegistry.load_all(soft_skills_dir)

__all__ = [
    # 框架
    "BaseSkill",
    "SkillMetadata", 
    "SkillCategory",
    "SkillRegistry",
    "SkillExecutor",
    "SkillType",
    # Native Skills
    "LessonPreparationSkill",
    "ExerciseGenerator",
    "TestPaperGenerator",
    # 快捷方法
    "get_skill",
    "list_skills",
    "execute_skill",
    "init_skills",
]
```

## 五、使用示例

### 5.1 基本使用

```python
from skills import init_skills, execute_skill

# 初始化（扫描所有 skills）
init_skills(soft_skills_dir="./skills/soft/skills")

# 列出所有技能
for name, info in list_skills().items():
    skill_type = info["type"]
    print(f"[{skill_type}] {name}: {info['display_name']}")

# 执行 Native Skill
result = await execute_skill("lesson_preparation", {
    "education_level": "高中",
    "subject": "数学", 
    "topic": "函数的概念"
})

# 执行 Soft Skill
result = await execute_skill("quick-lesson", {
    "topic": "光的折射",
    "duration": 40
})
```

### 5.2 创建 Soft Skill

用户只需创建 SKILL.md 文件即可添加新技能：

```markdown
<!-- skills/soft/skills/my-custom-skill.SKILL.md -->

---
name: my-custom-skill
display_name: 我的自定义技能
description: 用户自定义的简单任务技能
version: 1.0.0
author: user
category: utility
triggers:
  - "自定义"
  - "我的技能"
---

# 我的自定义技能

## 能力描述
这是一个用户自定义的技能，用于...

## 参数说明
...

## 执行逻辑
...
```

## 六、文件结构

```
skills/
├── __init__.py                     # 统一导出
├── _base/                         # 核心框架
│   ├── __init__.py
│   ├── base.py                    # BaseSkill 基类
│   ├── metadata.py                # 元数据定义
│   ├── registry.py                # 注册中心
│   ├── executor.py                # 统一执行器
│   ├── soft_executor.py           # Soft Skill 执行器
│   └── soft_loader.py             # SKILL.md 加载器
├── native/                        # Native Skills
│   ├── __init__.py               # 导出所有 native skills
│   ├── lesson_preparation/        # 原备课技能
│   ├── teaching_assessment/       # 原评估技能
│   └── ...                        # 其他迁移的技能
└── soft/                          # Soft Skills
    ├── README.md                 # 使用指南
    └── skills/                   # SKILL.md 文件目录
        ├── quick-lesson.SKILL.md
        └── student-feedback.SKILL.md
```

## 七、实施计划

| 阶段 | 内容 | 工作量 |
|------|------|--------|
| **Phase 1** | 创建 `_base/` 核心框架 | 0.5天 |
| **Phase 2** | 迁移现有 skills 到 `native/` | 0.5天 |
| **Phase 3** | 实现 Soft Skill 加载器和执行器 | 0.5天 |
| **Phase 4** | 创建示例 Soft Skill | 0.25天 |
| **Phase 5** | 更新统一导出 `__init__.py` | 0.25天 |
| **Phase 6** | 测试验证 | 0.5天 |
| **总计** | | **2.5天** |
