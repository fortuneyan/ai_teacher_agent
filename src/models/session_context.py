"""
会话上下文数据对象 (DO-006)

用于存储和管理会话状态
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class SessionStatus(str, Enum):
    """会话状态"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class SessionContext:
    """
    会话上下文数据对象
    
    存储会话的完整状态和交互历史
    """
    # 基本信息
    session_id: str
    user_id: Optional[str] = None
    
    # 当前状态
    current_stage: str = "init"  # init, input, search, analysis, generation, review
    status: SessionStatus = SessionStatus.ACTIVE
    
    # 关联数据
    course_info: Optional[Dict[str, Any]] = None
    plan_id: Optional[str] = None
    
    # 交互历史
    interaction_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # 元信息
    created_at: datetime = field(default_factory=datetime.now)
    last_active_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "current_stage": self.current_stage,
            "status": self.status.value,
            "course_info": self.course_info,
            "plan_id": self.plan_id,
            "interaction_history": self.interaction_history,
            "created_at": self.created_at.isoformat(),
            "last_active_at": self.last_active_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionContext":
        """从字典创建"""
        return cls(
            session_id=data["session_id"],
            user_id=data.get("user_id"),
            current_stage=data.get("current_stage", "init"),
            status=SessionStatus(data.get("status", "active")),
            course_info=data.get("course_info"),
            plan_id=data.get("plan_id"),
            interaction_history=data.get("interaction_history", []),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            last_active_at=datetime.fromisoformat(data["last_active_at"]) if "last_active_at" in data else datetime.now()
        )
    
    def update_stage(self, stage: str) -> None:
        """更新当前阶段"""
        self.current_stage = stage
        self.last_active_at = datetime.now()
        self._record_action("stage_change", {"new_stage": stage})
    
    def add_interaction(self, action: str, data: Dict[str, Any]) -> None:
        """添加交互记录"""
        self.interaction_history.append({
            "action": action,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
        self.last_active_at = datetime.now()
    
    def _record_action(self, action: str, data: Dict[str, Any]) -> None:
        """记录操作"""
        self.interaction_history.append({
            "action": action,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
    
    def complete(self) -> None:
        """完成会话"""
        self.status = SessionStatus.COMPLETED
        self.last_active_at = datetime.now()
    
    def __str__(self) -> str:
        return f"SessionContext({self.session_id}: {self.current_stage})"
