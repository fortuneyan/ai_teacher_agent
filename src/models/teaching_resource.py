"""
教学资源数据对象 (DO-003)

用于存储和管理教学资源信息
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class ResourceType(str, Enum):
    """资源类型"""
    PPT = "ppt"
    VIDEO = "video"
    DOCUMENT = "document"
    IMAGE = "image"
    AUDIO = "audio"
    INTERACTIVE = "interactive"
    EXERCISE = "exercise"
    OTHER = "other"


class ResourceStatus(str, Enum):
    """资源状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


@dataclass
class TeachingResource:
    """
    教学资源数据对象
    
    存储教学资源的元数据和内容
    """
    # 基本信息
    resource_id: str
    resource_name: str
    resource_type: ResourceType
    
    # 内容信息
    content: str  # 资源内容或描述
    file_url: Optional[str] = None
    file_size: Optional[int] = None  # 字节
    
    # 分类信息
    subject: Optional[str] = None
    education_level: Optional[str] = None
    topic: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    # 元信息
    status: ResourceStatus = ResourceStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    usage_count: int = 0
    rating: float = 0.0  # 0-5分
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "resource_id": self.resource_id,
            "resource_name": self.resource_name,
            "resource_type": self.resource_type.value,
            "content": self.content,
            "file_url": self.file_url,
            "file_size": self.file_size,
            "subject": self.subject,
            "education_level": self.education_level,
            "topic": self.topic,
            "tags": self.tags,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by,
            "usage_count": self.usage_count,
            "rating": self.rating
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TeachingResource":
        """从字典创建"""
        return cls(
            resource_id=data["resource_id"],
            resource_name=data["resource_name"],
            resource_type=ResourceType(data.get("resource_type", "other")),
            content=data.get("content", ""),
            file_url=data.get("file_url"),
            file_size=data.get("file_size"),
            subject=data.get("subject"),
            education_level=data.get("education_level"),
            topic=data.get("topic"),
            tags=data.get("tags", []),
            status=ResourceStatus(data.get("status", "active")),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else datetime.now(),
            created_by=data.get("created_by", "system"),
            usage_count=data.get("usage_count", 0),
            rating=data.get("rating", 0.0)
        )
    
    def update_usage(self) -> None:
        """更新使用次数"""
        self.usage_count += 1
        self.updated_at = datetime.now()
    
    def add_tag(self, tag: str) -> None:
        """添加标签"""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now()
    
    def __str__(self) -> str:
        return f"TeachingResource({self.resource_id}: {self.resource_name})"
