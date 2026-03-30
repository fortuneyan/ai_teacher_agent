"""
数据对象: CurriculumStandard (DO-002)
课程标准
"""

import json
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class CurriculumStandard:
    """
    课程标准
    
    从国家或地方课程标准中提取的教学要求
    """
    
    # 必填字段
    standard_id: str
    standard_name: str
    standard_type: str  # 国家/地方/校本
    education_level: str
    subject: str
    topic: str
    content_requirements: List[str]
    competency_requirements: List[str]
    achievement_standards: List[str]
    suggested_hours: int
    extracted_at: datetime
    relevance_score: float
    
    # 可选字段
    source_url: Optional[str] = None
    
    # 常量
    VALID_STANDARD_TYPES = ["国家", "地方", "校本"]
    
    def __post_init__(self):
        """初始化后验证"""
        self._validate()
    
    def _validate(self):
        """验证数据"""
        if self.standard_type not in self.VALID_STANDARD_TYPES:
            raise ValueError(f"standard_type必须是{self.VALID_STANDARD_TYPES}之一")
        
        if not self.content_requirements:
            raise ValueError("content_requirements不能为空")
        
        if not self.achievement_standards:
            raise ValueError("achievement_standards不能为空")
        
        if not (0.0 <= self.relevance_score <= 1.0):
            raise ValueError("relevance_score必须在0.0-1.0之间")
        
        if isinstance(self.extracted_at, str):
            self.extracted_at = datetime.fromisoformat(self.extracted_at)
    
    def to_dict(self) -> dict:
        """转换为字典"""
        data = asdict(self)
        data['extracted_at'] = self.extracted_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CurriculumStandard':
        """从字典创建"""
        if 'extracted_at' in data and isinstance(data['extracted_at'], str):
            data['extracted_at'] = datetime.fromisoformat(data['extracted_at'])
        return cls(**data)
