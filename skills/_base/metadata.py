"""
skills._base.metadata - 标准化 Skill 元数据定义

定义所有 Skill 的元数据结构，支持 Native 和 Soft 两种类型。
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional


class SkillCategory(Enum):
    """技能分类"""
    CORE = "core"              # 核心能力（备课、评估等）
    WORKFLOW = "workflow"       # 工作流（收集素材、设计教案等）
    UTILITY = "utility"        # 工具类（文件处理等）
    CUSTOM = "custom"          # 自定义（用户添加）


class SkillType(Enum):
    """技能类型"""
    NATIVE = "native"          # 原生技能 - Python 硬编码
    SOFT = "soft"             # 软技能 - SKILL.md 文档


@dataclass
class SkillMetadata:
    """标准化的技能元数据"""
    
    # === 必填字段 ===
    name: str                              # 唯一标识，如 "lesson_preparation"
    display_name: str                      # 显示名称，如 "智能备课"
    version: str                           # 版本号，如 "1.0.0"
    description: str                       # 简短描述
    
    # === 类型标识 ===
    skill_type: SkillType = SkillType.NATIVE  # 技能类型
    category: SkillCategory = SkillCategory.WORKFLOW
    
    # === 可选字段 ===
    author: str = "AI Teacher Team"
    tags: List[str] = field(default_factory=list)
    
    # === 触发词（用于 LLM 识别）===
    triggers: List[str] = field(default_factory=list)
    
    # === 输入输出模式 ===
    input_schema: Optional[Dict[str, Any]] = None   # JSON Schema
    output_schema: Optional[Dict[str, Any]] = None
    
    # === 依赖关系 ===
    requires: List[str] = field(default_factory=list)   # 依赖的 skill
    provides: List[str] = field(default_factory=list)    # 提供的输出
    
    # === 配置选项 ===
    default_config: Dict[str, Any] = field(default_factory=dict)
    supported_llm_models: List[str] = field(default_factory=list)
    
    # === Soft Skill 特有 ===
    parameters: List[Dict[str, Any]] = field(default_factory=list)  # SKILL.md 参数定义
    runtime: Optional[str] = None              # 执行环境
    timeout: int = 60                          # 超时时间（秒）
    
    # === 软技能内容（SKILL.md 正文）===
    content: Optional[str] = None              # Markdown 正文
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "name": self.name,
            "display_name": self.display_name,
            "version": self.version,
            "description": self.description,
            "skill_type": self.skill_type.value,
            "category": self.category.value if self.category else None,
            "author": self.author,
            "tags": self.tags,
            "triggers": self.triggers,
        }
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SkillMetadata":
        """从字典创建"""
        # 处理枚举类型
        if "skill_type" in data:
            data["skill_type"] = SkillType(data["skill_type"])
        if "category" in data and isinstance(data["category"], str):
            data["category"] = SkillCategory(data["category"])
        
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
    
    def to_openclaw_format(self) -> str:
        """转换为 OpenClaw SKILL.md 格式"""
        frontmatter = [
            "---",
            f'name: "{self.name}"',
            f'version: "{self.version}"',
            f'display_name: "{self.display_name}"',
            f'description: "{self.description}"',
            f'category: "{self.category.value}"',
            f'author: "{self.author}"',
        ]
        
        if self.tags:
            frontmatter.append(f'tags: [{", ".join(self.tags)}]')
        
        if self.triggers:
            frontmatter.append(f"triggers:")
            for trigger in self.triggers:
                frontmatter.append(f'  - "{trigger}"')
        
        if self.parameters:
            frontmatter.append("parameters:")
            for param in self.parameters:
                required = param.get("required", False)
                default = param.get("default")
                frontmatter.append(f'  - name: {param["name"]}')
                frontmatter.append(f'    type: {param["type"]}')
                frontmatter.append(f'    required: {str(required).lower()}')
                if default is not None:
                    frontmatter.append(f'    default: {default}')
        
        if self.timeout and self.skill_type == SkillType.SOFT:
            frontmatter.append(f"timeout: {self.timeout}")
        
        frontmatter.append("---")
        
        content = "\n".join(frontmatter)
        if self.content:
            content += f"\n\n{self.content}"
        
        return content
