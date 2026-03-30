"""
教案数据对象 (DO-005)
MVP版本简化实现
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class LessonPlanStatus(str, Enum):
    """教案状态"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


@dataclass
class LessonPlan:
    """
    教案数据对象
    
    MVP版本包含核心字段：
    - 基本信息：ID、标题、学科、年级
    - 教学目标
    - 教学流程
    - 状态
    """
    # 基本信息
    plan_id: str
    title: str
    subject: str
    education_level: str
    topic: str
    
    # 教学目标 (MVP: 简化为字符串列表)
    teaching_objectives: List[str] = field(default_factory=list)
    
    # 教学流程 (MVP: 简化为步骤列表)
    teaching_procedure: List[Dict[str, Any]] = field(default_factory=list)
    
    # 元信息
    status: LessonPlanStatus = LessonPlanStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    version: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "plan_id": self.plan_id,
            "title": self.title,
            "subject": self.subject,
            "education_level": self.education_level,
            "topic": self.topic,
            "teaching_objectives": self.teaching_objectives,
            "teaching_procedure": self.teaching_procedure,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by,
            "version": self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LessonPlan":
        """从字典创建"""
        return cls(
            plan_id=data["plan_id"],
            title=data["title"],
            subject=data["subject"],
            education_level=data["education_level"],
            topic=data["topic"],
            teaching_objectives=data.get("teaching_objectives", []),
            teaching_procedure=data.get("teaching_procedure", []),
            status=LessonPlanStatus(data.get("status", "draft")),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else datetime.now(),
            created_by=data.get("created_by", "system"),
            version=data.get("version", 1)
        )
    
    def update(self, **kwargs) -> None:
        """更新教案"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()
        self.version += 1
    
    def add_objective(self, objective: str) -> None:
        """添加教学目标"""
        if objective not in self.teaching_objectives:
            self.teaching_objectives.append(objective)
            self.updated_at = datetime.now()
    
    def add_procedure_step(self, step: Dict[str, Any]) -> None:
        """添加教学步骤"""
        self.teaching_procedure.append(step)
        self.updated_at = datetime.now()
    
    def publish(self) -> None:
        """发布教案"""
        self.status = LessonPlanStatus.PUBLISHED
        self.updated_at = datetime.now()
    
    def __str__(self) -> str:
        return f"LessonPlan({self.plan_id}: {self.title})"
