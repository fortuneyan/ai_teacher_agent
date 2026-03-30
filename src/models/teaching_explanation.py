"""
教学讲解数据对象 (DO-013)

用于存储和管理智能讲解内容
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class ExplanationType(str, Enum):
    """讲解类型"""
    CONCEPT = "concept"         # 概念讲解
    EXAMPLE = "example"         # 例题讲解
    EXERCISE = "exercise"       # 习题讲解
    SUMMARY = "summary"         # 知识总结
    Q_AND_A = "q_and_a"         # 问答讲解
    COMPARISON = "comparison"   # 对比讲解
    ERROR_ANALYSIS = "error_analysis"  # 错误分析


class ExplanationLevel(str, Enum):
    """讲解深度"""
    BASIC = "basic"             # 基础
    INTERMEDIATE = "intermediate"  # 中等
    ADVANCED = "advanced"       # 深入


@dataclass
class ExplanationStep:
    """
    讲解步骤
    
    一个完整的讲解由多个步骤组成
    """
    step_number: int
    step_title: str
    content: str                    # 讲解内容
    key_points: List[str] = field(default_factory=list)  # 要点
    visual_aids: List[str] = field(default_factory=list)  # 辅助材料建议
    expected_duration: int = 3      # 预计时长（分钟）
    interaction_prompt: Optional[str] = None  # 互动提示
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_number": self.step_number,
            "step_title": self.step_title,
            "content": self.content,
            "key_points": self.key_points,
            "visual_aids": self.visual_aids,
            "expected_duration": self.expected_duration,
            "interaction_prompt": self.interaction_prompt
        }


@dataclass
class CommonMisconception:
    """
    常见误区
    
    记录学生容易犯的错误和误解
    """
    misconception_id: str
    description: str                # 误区描述
    why_wrong: str                  # 错误原因
    how_to_correct: str             # 纠正方法
    example: Optional[str] = None   # 示例
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "misconception_id": self.misconception_id,
            "description": self.description,
            "why_wrong": self.why_wrong,
            "how_to_correct": self.how_to_correct,
            "example": self.example
        }


@dataclass
class TeachingExplanation:
    """
    教学讲解数据对象
    
    存储完整的讲解内容
    """
    # 基本信息
    explanation_id: str
    explanation_type: ExplanationType
    title: str
    
    # 关联信息
    topic: str                      # 讲解主题
    subject: Optional[str] = None
    education_level: Optional[str] = None
    
    # 讲解内容
    introduction: str = ""          # 引入
    steps: List[ExplanationStep] = field(default_factory=list)  # 讲解步骤
    conclusion: str = ""            # 总结
    
    # 深度和难度
    level: ExplanationLevel = ExplanationLevel.INTERMEDIATE
    prerequisites: List[str] = field(default_factory=list)  # 前置知识
    
    # 常见误区
    common_misconceptions: List[CommonMisconception] = field(default_factory=list)
    
    # 拓展内容
    extension_questions: List[str] = field(default_factory=list)  # 拓展问题
    related_topics: List[str] = field(default_factory=list)       # 相关主题
    
    # 元信息
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    version: int = 1
    
    def add_step(self, step: ExplanationStep) -> None:
        """添加讲解步骤"""
        self.steps.append(step)
        self.updated_at = datetime.now()
    
    def add_misconception(self, misconception: CommonMisconception) -> None:
        """添加常见误区"""
        self.common_misconceptions.append(misconception)
        self.updated_at = datetime.now()
    
    def get_total_duration(self) -> int:
        """获取总讲解时长"""
        return sum(s.expected_duration for s in self.steps)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "explanation_id": self.explanation_id,
            "explanation_type": self.explanation_type.value,
            "title": self.title,
            "topic": self.topic,
            "subject": self.subject,
            "education_level": self.education_level,
            "introduction": self.introduction,
            "steps": [s.to_dict() for s in self.steps],
            "conclusion": self.conclusion,
            "level": self.level.value,
            "prerequisites": self.prerequisites,
            "common_misconceptions": [m.to_dict() for m in self.common_misconceptions],
            "extension_questions": self.extension_questions,
            "related_topics": self.related_topics,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by,
            "version": self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TeachingExplanation":
        """从字典创建"""
        explanation = cls(
            explanation_id=data["explanation_id"],
            explanation_type=ExplanationType(data.get("explanation_type", "concept")),
            title=data["title"],
            topic=data["topic"],
            subject=data.get("subject"),
            education_level=data.get("education_level"),
            introduction=data.get("introduction", ""),
            conclusion=data.get("conclusion", ""),
            level=ExplanationLevel(data.get("level", "intermediate")),
            prerequisites=data.get("prerequisites", []),
            extension_questions=data.get("extension_questions", []),
            related_topics=data.get("related_topics", []),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else datetime.now(),
            created_by=data.get("created_by", "system"),
            version=data.get("version", 1)
        )
        
        # 解析步骤
        for step_data in data.get("steps", []):
            explanation.steps.append(ExplanationStep(
                step_number=step_data["step_number"],
                step_title=step_data["step_title"],
                content=step_data["content"],
                key_points=step_data.get("key_points", []),
                visual_aids=step_data.get("visual_aids", []),
                expected_duration=step_data.get("expected_duration", 3),
                interaction_prompt=step_data.get("interaction_prompt")
            ))
        
        # 解析误区
        for misc_data in data.get("common_misconceptions", []):
            explanation.common_misconceptions.append(CommonMisconception(
                misconception_id=misc_data["misconception_id"],
                description=misc_data["description"],
                why_wrong=misc_data["why_wrong"],
                how_to_correct=misc_data["how_to_correct"],
                example=misc_data.get("example")
            ))
        
        return explanation
    
    def __str__(self) -> str:
        return f"TeachingExplanation({self.explanation_id}: {self.title})"


@dataclass
class StudentQuestion:
    """
    学生问题数据对象
    
    记录学生提出的问题
    """
    question_id: str
    student_id: str
    question_text: str              # 问题内容
    related_topic: Optional[str] = None  # 相关主题
    difficulty_level: ExplanationLevel = ExplanationLevel.INTERMEDIATE
    
    # 回答信息
    answer: Optional[str] = None
    answered_by: Optional[str] = None  # 回答者（AI或教师）
    answered_at: Optional[datetime] = None
    
    # 元信息
    created_at: datetime = field(default_factory=datetime.now)
    is_resolved: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "question_id": self.question_id,
            "student_id": self.student_id,
            "question_text": self.question_text,
            "related_topic": self.related_topic,
            "difficulty_level": self.difficulty_level.value,
            "answer": self.answer,
            "answered_by": self.answered_by,
            "answered_at": self.answered_at.isoformat() if self.answered_at else None,
            "created_at": self.created_at.isoformat(),
            "is_resolved": self.is_resolved
        }
