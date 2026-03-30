"""
教学目标数据对象 (DO-004)

用于存储和管理教学目标
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class ObjectiveLevel(str, Enum):
    """目标层次"""
    KNOWLEDGE = "knowledge"      # 知识目标
    SKILL = "skill"              # 技能目标
    PROCESS = "process"          # 过程目标
    EMOTION = "emotion"          # 情感目标
    COMPETENCY = "competency"    # 素养目标


class ObjectiveStatus(str, Enum):
    """目标状态"""
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    ACHIEVED = "achieved"


@dataclass
class TeachingObjectives:
    """
    教学目标数据对象
    
    存储课程的教学目标，支持多维度目标管理
    """
    # 基本信息
    objectives_id: str
    plan_id: Optional[str] = None  # 关联的教案ID
    
    # 目标内容（按层次分类）
    knowledge_objectives: List[str] = field(default_factory=list)      # 知识目标
    skill_objectives: List[str] = field(default_factory=list)          # 技能目标
    process_objectives: List[str] = field(default_factory=list)        # 过程目标
    emotion_objectives: List[str] = field(default_factory=list)        # 情感目标
    competency_objectives: List[str] = field(default_factory=list)     # 素养目标
    
    # 元信息
    status: ObjectiveStatus = ObjectiveStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "objectives_id": self.objectives_id,
            "plan_id": self.plan_id,
            "knowledge_objectives": self.knowledge_objectives,
            "skill_objectives": self.skill_objectives,
            "process_objectives": self.process_objectives,
            "emotion_objectives": self.emotion_objectives,
            "competency_objectives": self.competency_objectives,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TeachingObjectives":
        """从字典创建"""
        return cls(
            objectives_id=data["objectives_id"],
            plan_id=data.get("plan_id"),
            knowledge_objectives=data.get("knowledge_objectives", []),
            skill_objectives=data.get("skill_objectives", []),
            process_objectives=data.get("process_objectives", []),
            emotion_objectives=data.get("emotion_objectives", []),
            competency_objectives=data.get("competency_objectives", []),
            status=ObjectiveStatus(data.get("status", "draft")),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else datetime.now(),
            created_by=data.get("created_by", "system")
        )
    
    def add_objective(self, level: ObjectiveLevel, objective: str) -> None:
        """添加目标"""
        if level == ObjectiveLevel.KNOWLEDGE:
            self.knowledge_objectives.append(objective)
        elif level == ObjectiveLevel.SKILL:
            self.skill_objectives.append(objective)
        elif level == ObjectiveLevel.PROCESS:
            self.process_objectives.append(objective)
        elif level == ObjectiveLevel.EMOTION:
            self.emotion_objectives.append(objective)
        elif level == ObjectiveLevel.COMPETENCY:
            self.competency_objectives.append(objective)
        self.updated_at = datetime.now()
    
    def get_all_objectives(self) -> List[str]:
        """获取所有目标"""
        return (
            self.knowledge_objectives +
            self.skill_objectives +
            self.process_objectives +
            self.emotion_objectives +
            self.competency_objectives
        )
    
    def confirm(self) -> None:
        """确认目标"""
        self.status = ObjectiveStatus.CONFIRMED
        self.updated_at = datetime.now()
    
    def __str__(self) -> str:
        return f"TeachingObjectives({self.objectives_id}: {len(self.get_all_objectives())} objectives)"
