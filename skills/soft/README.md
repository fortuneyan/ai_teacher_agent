# Soft Skills - 可热插拔的技能目录

> Soft Skill 是 OpenClaw 风格的技能，使用 SKILL.md 文档定义，通过 LLM 理解后执行。

## 目录结构

```
soft/
├── README.md              # 本文件
├── skills/               # SKILL.md 文件目录
│   ├── quick-lesson.SKILL.md
│   ├── student-feedback.SKILL.md
│   └── ...
└── templates/           # 模板目录
    └── soft_skill_template.md
```

## 什么是 Soft Skill？

Soft Skill 使用 OpenClaw 的 SKILL.md 格式定义技能：

```markdown
---
name: my-skill
display_name: 我的技能
description: 简短描述
version: 1.0.0
author: custom
triggers:
  - "触发词1"
  - "触发词2"
parameters:
  - name: param1
    type: string
    required: true
---

# 技能名称

## 能力描述

这里是技能的详细说明...
```

## 如何添加新技能？

### 方式一：手动创建

1. 在 `soft/skills/` 目录创建 `.SKILL.md` 文件
2. 遵循上述格式编写内容
3. 重启应用或调用 `init_skills()` 重新加载

### 方式二：使用模板生成器

```python
from skills._base import SoftSkillTemplate

content = SoftSkillTemplate.generate(
    name="my-custom-skill",
    display_name="我的自定义技能",
    description="这是一个示例技能",
    parameters=[
        {"name": "input", "type": "string", "required": True}
    ],
    triggers=["自定义", "我的技能"]
)

# 保存到文件
with open("skills/soft/skills/my-custom-skill.SKILL.md", "w") as f:
    f.write(content)
```

## 示例 Soft Skills

### quick-lesson.SKILL.md

快速生成简要教案的技能。

### student-feedback.SKILL.md

处理学生反馈的技能。

## 触发词

Soft Skill 支持触发词，当用户输入包含触发词时，LLM 会自动识别并建议使用对应的技能。

## 注意事项

1. Soft Skill 依赖 LLM 理解，执行结果可能不稳定
2. 复杂逻辑建议使用 Native Skill
3. Soft Skill 支持热插拔，但需要重启或重新加载
