"""
教案更新数据对象 (DO-012)

用于记录教案的修改历史
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class UpdateType(str, Enum):
    """更新类型"""
    CREATE = "create"
    MODIFY = "modify"
    DELETE = "delete"
    PUBLISH = "publish"
    ARCHIVE = "archive"


class UpdateStatus(str, Enum):
    """更新状态"""
    PENDING = "pending"
    APPLIED = "applied"
    REJECTED = "rejected"
    ROLLED_BACK = "rolled_back"


@dataclass
class LessonPlanUpdate:
    """
    教案更新数据对象
    
    记录教案的每次修改
    """
    # 基本信息
    update_id: str
    plan_id: str
    
    # 更新内容
    update_type: UpdateType
    field_name: Optional[str] = None  # 修改的字段
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    description: str = ""
    
    # 更新来源
    source: str = "system"  # system, user, feedback
    triggered_by: Optional[str] = None  # 触发者ID
    
    # 状态
    status: UpdateStatus = UpdateStatus.PENDING
    applied_at: Optional[datetime] = None
    
    # 元信息
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "update_id": self.update_id,
            "plan_id": self.plan_id,
            "update_type": self.update_type.value,
            "field_name": self.field_name,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "description": self.description,
            "source": self.source,
            "triggered_by": self.triggered_by,
            "status": self.status.value,
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LessonPlanUpdate":
        """从字典创建"""
        return cls(
            update_id=data["update_id"],
            plan_id=data["plan_id"],
            update_type=UpdateType(data.get("update_type", "modify")),
            field_name=data.get("field_name"),
            old_value=data.get("old_value"),
            new_value=data.get("new_value"),
            description=data.get("description", ""),
            source=data.get("source", "system"),
            triggered_by=data.get("triggered_by"),
            status=UpdateStatus(data.get("status", "pending")),
            applied_at=datetime.fromisoformat(data["applied_at"]) if data.get("applied_at") else None,
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now()
        )
    
    def apply(self) -> None:
        """应用更新"""
        self.status = UpdateStatus.APPLIED
        self.applied_at = datetime.now()
    
    def reject(self) -> None:
        """拒绝更新"""
        self.status = UpdateStatus.REJECTED
    
    def rollback(self) -> None:
        """回滚更新"""
        self.status = UpdateStatus.ROLLED_BACK
    
    def __str__(self) -> str:
        return f"LessonPlanUpdate({self.update_id}: {self.update_type.value} {self.field_name})"
