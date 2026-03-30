"""
数据对象: UserFeedback (DO-010)
用户反馈
"""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field, asdict


@dataclass
class UserFeedback:
    """
    用户对教案或课件的反馈
    """
    
    # 必填字段
    feedback_id: str
    session_id: str
    lesson_plan_id: str
    feedback_type: str
    content: str
    submitted_at: datetime
    submitted_by: str
    
    # 可选字段
    target_section: Optional[str] = None
    suggested_change: Optional[str] = None
    priority: str = "normal"
    
    # 常量
    VALID_FEEDBACK_TYPES = ["modify", "add", "delete", "comment", "approve", "reject"]
    VALID_PRIORITIES = ["low", "normal", "high", "urgent"]
    
    def __post_init__(self):
        """初始化后验证"""
        self._validate()
    
    def _validate(self):
        """验证数据"""
        if self.feedback_type not in self.VALID_FEEDBACK_TYPES:
            raise ValueError(f"feedback_type必须是{self.VALID_FEEDBACK_TYPES}之一")
        
        if self.priority not in self.VALID_PRIORITIES:
            raise ValueError(f"priority必须是{self.VALID_PRIORITIES}之一")
        
        if len(self.content) < 5:
            raise ValueError("content长度不能少于5个字符")
        
        if isinstance(self.submitted_at, str):
            self.submitted_at = datetime.fromisoformat(self.submitted_at)
    
    def to_dict(self) -> dict:
        """转换为字典"""
        data = asdict(self)
        data['submitted_at'] = self.submitted_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'UserFeedback':
        """从字典创建"""
        if 'submitted_at' in data and isinstance(data['submitted_at'], str):
            data['submitted_at'] = datetime.fromisoformat(data['submitted_at'])
        return cls(**data)
