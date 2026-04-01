"""
skills._base.executor - 统一 Skill 执行器

自动选择 Native 或 Soft Skill 并执行。
"""

from typing import Dict, Any, Optional, Type
import logging

from .metadata import SkillMetadata, SkillType
from .base import BaseSkill
from .registry import SkillRegistry

logger = logging.getLogger(__name__)


class SkillExecutor:
    """
    统一 Skill 执行器
    
    自动根据技能类型选择合适的执行方式:
    - Native Skill: 直接调用 Python 类方法
    - Soft Skill: 调用 LLM 理解 SKILL.md 后执行
    
    使用方式:
    ```python
    executor = SkillExecutor(llm_service=my_llm)
    
    # 执行 Native Skill
    result = await executor.execute("lesson_preparation", {
        "education_level": "高中",
        "subject": "数学",
        "topic": "函数的概念"
    })
    
    # 执行 Soft Skill
    result = await executor.execute("quick-lesson", {
        "topic": "光的折射"
    })
    ```
    """
    
    def __init__(self, llm_service=None):
        """
        初始化执行器
        
        Args:
            llm_service: LLM 服务实例（Soft Skill 必须）
        """
        self.llm_service = llm_service
        self._soft_executor = None
        
        # 延迟导入避免循环依赖
        if llm_service is not None:
            from .soft_executor import SoftSkillExecutor
            self._soft_executor = SoftSkillExecutor(llm_service)
    
    async def execute(self, skill_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行技能
        
        Args:
            skill_name: 技能名称
            context: 执行上下文/参数
            
        Returns:
            执行结果字典
        """
        skill = SkillRegistry.get(skill_name)
        
        if skill is None:
            return {
                "status": "error",
                "message": f"Skill '{skill_name}' not found",
                "code": "SKILL_NOT_FOUND"
            }
        
        # 判断技能类型
        if isinstance(skill, type) and issubclass(skill, BaseSkill):
            # Native Skill
            return await self._execute_native(skill, context)
        elif isinstance(skill, dict):
            # Soft Skill 或已注册的数据
            skill_type = skill.get("skill_type")
            if skill_type == SkillType.SOFT.value:
                return await self._execute_soft(skill_name, context)
            elif skill_type == SkillType.NATIVE.value:
                # 元数据字典，需要获取实际类
                skill_class = SkillRegistry.get_native(skill_name)
                if skill_class:
                    return await self._execute_native(skill_class, context)
        
        return {
            "status": "error",
            "message": f"Unknown skill type for '{skill_name}'",
            "code": "UNKNOWN_SKILL_TYPE"
        }
    
    async def _execute_native(self, skill_class: Type[BaseSkill], context: Dict[str, Any]) -> Dict[str, Any]:
        """执行 Native Skill"""
        try:
            # 创建实例
            instance = skill_class(llm_service=self.llm_service)
            
            # 验证输入
            if not instance.validate_input(context):
                return {
                    "status": "error",
                    "message": "Invalid input parameters",
                    "code": "INVALID_INPUT"
                }
            
            # 执行
            logger.info(f"Executing native skill: {instance.get_name()}")
            result = await instance.execute(context)
            
            # 补充元数据
            if isinstance(result, dict) and "metadata" not in result:
                result["metadata"] = {
                    "skill": instance.get_name(),
                    "version": instance.metadata.version,
                    "type": SkillType.NATIVE.value
                }
            
            return result
            
        except Exception as e:
            logger.exception(f"Error executing native skill: {skill_class.__name__}")
            return {
                "status": "error",
                "message": str(e),
                "code": "EXECUTION_ERROR"
            }
    
    async def _execute_soft(self, skill_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行 Soft Skill"""
        if self._soft_executor is None:
            return {
                "status": "error",
                "message": "Soft Skill requires LLM service",
                "code": "LLM_REQUIRED"
            }
        
        try:
            logger.info(f"Executing soft skill: {skill_name}")
            result = await self._soft_executor.execute(skill_name, context)
            
            # 补充元数据
            if isinstance(result, dict) and "metadata" not in result:
                skill_data = SkillRegistry.get_soft(skill_name)
                result["metadata"] = {
                    "skill": skill_name,
                    "version": skill_data.get("version", "1.0.0") if skill_data else "1.0.0",
                    "type": SkillType.SOFT.value
                }
            
            return result
            
        except Exception as e:
            logger.exception(f"Error executing soft skill: {skill_name}")
            return {
                "status": "error",
                "message": str(e),
                "code": "EXECUTION_ERROR"
            }


class AsyncSkillExecutor(SkillExecutor):
    """
    异步 Skill 执行器
    
    提供更简洁的异步上下文管理。
    """
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
