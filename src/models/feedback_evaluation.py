"""
数据对象: FeedbackEvaluation (DO-011)
反馈评估结果
"""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field, asdict


@dataclass
class FeedbackEvaluation:
    """
    对用户反馈的智能评估结果
    """
    
    # 必填字段
    evaluation_id: str
    feedback_id: str
    decision: str
    confidence: float
    relevance_score: float
    feasibility_score: float
    reasoning: str
    evaluated_at: datetime
    evaluated_by: str
    
    # 可选字段
    alternative_suggestion: Optional[str] = None
    clarification_question: Optional[str] = None
    
    # 常量
    VALID_DECISIONS = ["accepted", "rejected", "needs_clarification", "partial_accepted", "pending_review"]
    
    # 评估阈值
    RELEVANCE_THRESHOLD = 0.5
    FEASIBILITY_THRESHOLD = 0.3
    CONFIDENCE_THRESHOLD = 0.7
    AUTO_ACCEPT_THRESHOLD = 0.8
    AUTO_REJECT_THRESHOLD = 0.2
    
    def __post_init__(self):
        """初始化后验证"""
        self._validate()
    
    def _validate(self):
        """验证数据"""
        if self.decision not in self.VALID_DECISIONS:
            raise ValueError(f"decision必须是{self.VALID_DECISIONS}之一")
        
        for score_name, score in [
            ("confidence", self.confidence),
            ("relevance_score", self.relevance_score),
            ("feasibility_score", self.feasibility_score)
        ]:
            if not (0.0 <= score <= 1.0):
                raise ValueError(f"{score_name}必须在0.0-1.0之间")
        
        if isinstance(self.evaluated_at, str):
            self.evaluated_at = datetime.fromisoformat(self.evaluated_at)
    
    def is_accepted(self) -> bool:
        """是否被接受"""
        return self.decision == "accepted"
    
    def is_rejected(self) -> bool:
        """是否被拒绝"""
        return self.decision == "rejected"
    
    def needs_clarification(self) -> bool:
        """是否需要澄清"""
        return self.decision == "needs_clarification"
    
    def to_dict(self) -> dict:
        """转换为字典"""
        data = asdict(self)
        data['evaluated_at'] = self.evaluated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'FeedbackEvaluation':
        """从字典创建"""
        if 'evaluated_at' in data and isinstance(data['evaluated_at'], str):
            data['evaluated_at'] = datetime.fromisoformat(data['evaluated_at'])
        return cls(**data)
