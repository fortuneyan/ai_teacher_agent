"""
skills._base.registry - Skill 注册中心

统一管理 Native Skills 和 Soft Skills 的注册与发现。
"""

from typing import Dict, List, Optional, Type, Any
import logging
import importlib
import pkgutil
from pathlib import Path

from .metadata import SkillMetadata, SkillType
from .base import BaseSkill

logger = logging.getLogger(__name__)


class SkillRegistry:
    """
    Skill 注册中心
    
    支持两种类型的技能:
    - Native Skill: Python 类实现，硬编码高性能
    - Soft Skill: SKILL.md 文档，LLM 理解后执行
    
    使用方式:
    ```python
    from skills._base import SkillRegistry, SkillType
    
    # 注册 Native Skill
    SkillRegistry.register_native(MySkillClass)
    
    # 注册 Soft Skill
    SkillRegistry.register_soft(skill_data)
    
    # 获取技能
    skill = SkillRegistry.get("my_skill")
    
    # 列出所有
    all_skills = SkillRegistry.list_all()
    ```
    """
    
    # 存储 Native Skills: name -> Class
    _native_skills: Dict[str, Type[BaseSkill]] = {}
    
    # 存储 Soft Skills: name -> dict (SKILL.md 解析结果)
    _soft_skills: Dict[str, Dict[str, Any]] = {}
    
    # 已初始化的标志
    _initialized: bool = False
    
    @classmethod
    def register_native(cls, skill_class: Type[BaseSkill]) -> Type[BaseSkill]:
        """
        注册 Native Skill
        
        Args:
            skill_class: 继承自 BaseSkill 的类
            
        Returns:
            被注册的类（用于装饰器）
        """
        if not issubclass(skill_class, BaseSkill):
            raise ValueError(f"{skill_class.__name__} must inherit from BaseSkill")
        
        metadata = skill_class.metadata
        if metadata is None:
            raise ValueError(f"{skill_class.__name__} must define metadata")
        
        name = metadata.name
        if name in cls._native_skills:
            logger.warning(f"Overwriting existing native skill: {name}")
        
        cls._native_skills[name] = skill_class
        logger.debug(f"Registered native skill: {name}")
        
        return skill_class
    
    @classmethod
    def register_soft(cls, skill_data: Dict[str, Any]) -> None:
        """
        注册 Soft Skill
        
        Args:
            skill_data: SKILL.md 解析后的字典，必须包含:
                - name: 技能名称
                - display_name: 显示名称
                - description: 描述
                - content: Markdown 正文
        """
        name = skill_data.get("name")
        if not name:
            raise ValueError("Soft skill must have 'name' field")
        
        # 补充默认值
        skill_data.setdefault("skill_type", SkillType.SOFT.value)
        skill_data.setdefault("display_name", name.replace("-", " ").title())
        skill_data.setdefault("version", "1.0.0")
        skill_data.setdefault("author", "custom")
        
        if name in cls._soft_skills:
            logger.warning(f"Overwriting existing soft skill: {name}")
        
        cls._soft_skills[name] = skill_data
        logger.debug(f"Registered soft skill: {name}")
    
    @classmethod
    def get(cls, name: str) -> Optional[Type[BaseSkill] | Dict[str, Any]]:
        """
        获取技能
        
        优先返回 Native Skill，如果不存在则返回 Soft Skill。
        
        Args:
            name: 技能名称
            
        Returns:
            Native Skill 类或 Soft Skill 字典，如果不存在则返回 None
        """
        # 优先查找 Native
        if name in cls._native_skills:
            return cls._native_skills[name]
        
        # 其次查找 Soft
        if name in cls._soft_skills:
            return cls._soft_skills[name]
        
        return None
    
    @classmethod
    def get_native(cls, name: str) -> Optional[Type[BaseSkill]]:
        """获取 Native Skill"""
        return cls._native_skills.get(name)
    
    @classmethod
    def get_soft(cls, name: str) -> Optional[Dict[str, Any]]:
        """获取 Soft Skill"""
        return cls._soft_skills.get(name)
    
    @classmethod
    def list_all(cls) -> Dict[str, Dict[str, Any]]:
        """
        列出所有已注册的技能
        
        Returns:
            {name: {metadata_dict, type}} 格式的字典
        """
        result = {}
        
        # 添加 Native Skills
        for name, skill_class in cls._native_skills.items():
            metadata = skill_class.metadata
            result[name] = {
                **metadata.to_dict(),
                "skill_type": SkillType.NATIVE.value,
            }
        
        # 添加 Soft Skills
        for name, skill_data in cls._soft_skills.items():
            result[name] = {
                "name": name,
                "display_name": skill_data.get("display_name", name),
                "version": skill_data.get("version", "1.0.0"),
                "description": skill_data.get("description", ""),
                "author": skill_data.get("author", "custom"),
                "skill_type": SkillType.SOFT.value,
                "category": skill_data.get("category", "custom"),
                "triggers": skill_data.get("triggers", []),
                "content": skill_data.get("content", ""),
            }
        
        return result
    
    @classmethod
    def list_by_type(cls, skill_type: SkillType) -> Dict[str, Dict[str, Any]]:
        """按类型列出技能"""
        all_skills = cls.list_all()
        return {
            name: data 
            for name, data in all_skills.items() 
            if data.get("skill_type") == skill_type.value
        }
    
    @classmethod
    def list_natives(cls) -> Dict[str, Type[BaseSkill]]:
        """列出所有 Native Skills"""
        return cls._native_skills.copy()
    
    @classmethod
    def list_softs(cls) -> Dict[str, Dict[str, Any]]:
        """列出所有 Soft Skills"""
        return cls._soft_skills.copy()
    
    @classmethod
    def unregister(cls, name: str) -> bool:
        """取消注册技能"""
        if name in cls._native_skills:
            del cls._native_skills[name]
            logger.debug(f"Unregistered native skill: {name}")
            return True
        
        if name in cls._soft_skills:
            del cls._soft_skills[name]
            logger.debug(f"Unregistered soft skill: {name}")
            return True
        
        return False
    
    @classmethod
    def clear(cls) -> None:
        """清空所有注册"""
        cls._native_skills.clear()
        cls._soft_skills.clear()
        cls._initialized = False
        logger.debug("Cleared all skills")
    
    @classmethod
    def is_initialized(cls) -> bool:
        """检查是否已初始化"""
        return cls._initialized
    
    @classmethod
    def set_initialized(cls, value: bool = True) -> None:
        """设置初始化状态"""
        cls._initialized = value


# 便捷访问
skill_registry = SkillRegistry
