"""
skills._base - 双层 Skill 架构核心框架

提供 Native Skill 和 Soft Skill 的统一管理能力。

Native Skill: Python 类实现，高性能硬编码
Soft Skill: SKILL.md 文档，LLM 理解后执行

使用方式:
```python
from skills._base import (
    BaseSkill,
    SkillMetadata,
    SkillCategory,
    SkillType,
    SkillRegistry,
    SkillExecutor,
)

# 定义 Native Skill
class MySkill(BaseSkill):
    metadata = SkillMetadata(
        name="my_skill",
        display_name="我的技能",
        version="1.0.0",
        description="示例技能",
        category=SkillCategory.UTILITY,
    )
    
    async def execute(self, context):
        return {"status": "success", "data": {}}

# 注册
SkillRegistry.register_native(MySkill)

# 执行
executor = SkillExecutor(llm_service=my_llm)
result = await executor.execute("my_skill", {})
```
"""

from .base import BaseSkill
from .metadata import SkillMetadata, SkillCategory, SkillType
from .registry import SkillRegistry, skill_registry
from .executor import SkillExecutor, AsyncSkillExecutor
from .soft_loader import SoftSkillLoader, ParsedSkill
from .soft_executor import SoftSkillExecutor, SoftSkillTemplate

__all__ = [
    # 核心类
    "BaseSkill",
    "SkillMetadata",
    "SkillCategory",
    "SkillType",
    "SkillRegistry",
    "skill_registry",
    # 执行器
    "SkillExecutor",
    "AsyncSkillExecutor",
    # Soft Skill 相关
    "SoftSkillLoader",
    "SoftSkillExecutor",
    "SoftSkillTemplate",
    "ParsedSkill",
]
