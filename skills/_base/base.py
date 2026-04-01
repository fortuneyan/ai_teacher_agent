"""
skills._base.base - BaseSkill 抽象基类

所有 Native Skill 必须继承此类并实现 execute() 方法。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type
import logging

from .metadata import SkillMetadata, SkillCategory, SkillType

logger = logging.getLogger(__name__)


class BaseSkill(ABC):
    """
    所有 Native Skill 的抽象基类
    
    使用方式:
    ```python
    from skills._base import BaseSkill, SkillMetadata, SkillCategory
    
    class MySkill(BaseSkill):
        metadata = SkillMetadata(
            name="my_skill",
            display_name="我的技能",
            version="1.0.0",
            description="这是一个示例技能",
            category=SkillCategory.UTILITY,
        )
        
        async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
            # 实现逻辑
            return {"status": "success", "data": {...}}
    ```
    """
    
    # 类级别的元数据（子类必须设置）
    metadata: SkillMetadata = None
    
    def __init__(self, llm_service=None, **kwargs):
        """
        初始化技能
        
        Args:
            llm_service: LLM 服务实例（可选）
            **kwargs: 其他配置参数
        """
        self.llm_service = llm_service
        self._config = kwargs
        self._validate_metadata()
    
    def _validate_metadata(self):
        """验证元数据是否正确设置"""
        if self.metadata is None:
            raise ValueError(
                f"{self.__class__.__name__} must define class-level 'metadata'"
            )
        
        if not isinstance(self.metadata, SkillMetadata):
            raise ValueError(
                f"{self.__class__.__name__}.metadata must be SkillMetadata instance"
            )
        
        # 确保类型为 NATIVE
        if self.metadata.skill_type != SkillType.NATIVE:
            self.metadata.skill_type = SkillType.NATIVE
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行技能的核心逻辑
        
        Args:
            context: 执行上下文，包含输入参数
                - 必需参数由 input_schema 定义
                
        Returns:
            执行结果字典，必须包含:
                - status: "success" | "error"
                - data: 实际结果数据
                - metadata: 执行元信息（skill 名、版本等）
        """
        pass
    
    def validate_input(self, context: Dict[str, Any]) -> bool:
        """
        验证输入参数
        
        Args:
            context: 输入上下文
            
        Returns:
            验证是否通过
        """
        if self.metadata.input_schema is None:
            return True
        
        # 简单实现：检查必需字段
        required = self.metadata.input_schema.get("required", [])
        for field in required:
            if field not in context:
                logger.warning(f"Missing required field: {field}")
                return False
        
        return True
    
    def get_metadata(self) -> SkillMetadata:
        """获取技能元数据"""
        return self.metadata
    
    def get_name(self) -> str:
        """获取技能名称"""
        return self.metadata.name
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.metadata.name})>"
