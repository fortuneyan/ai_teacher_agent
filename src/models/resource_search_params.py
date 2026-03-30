"""
资源搜索参数数据对象 (DO-008)

用于封装资源搜索的请求参数
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class ResourceSearchParams:
    """
    资源搜索参数数据对象
    
    封装资源搜索的所有参数
    """
    # 关键词
    keywords: Optional[str] = None
    
    # 筛选条件
    subject: Optional[str] = None
    education_level: Optional[str] = None
    topic: Optional[str] = None
    resource_type: Optional[str] = None
    
    # 标签筛选
    tags: List[str] = field(default_factory=list)
    
    # 分页
    page: int = 1
    page_size: int = 20
    
    # 排序
    sort_by: str = "relevance"  # relevance, rating, created_at
    sort_order: str = "desc"    # asc, desc
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "keywords": self.keywords,
            "subject": self.subject,
            "education_level": self.education_level,
            "topic": self.topic,
            "resource_type": self.resource_type,
            "tags": self.tags,
            "page": self.page,
            "page_size": self.page_size,
            "sort_by": self.sort_by,
            "sort_order": self.sort_order
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResourceSearchParams":
        """从字典创建"""
        return cls(
            keywords=data.get("keywords"),
            subject=data.get("subject"),
            education_level=data.get("education_level"),
            topic=data.get("topic"),
            resource_type=data.get("resource_type"),
            tags=data.get("tags", []),
            page=data.get("page", 1),
            page_size=data.get("page_size", 20),
            sort_by=data.get("sort_by", "relevance"),
            sort_order=data.get("sort_order", "desc")
        )
    
    def add_tag(self, tag: str) -> None:
        """添加标签筛选"""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def next_page(self) -> None:
        """下一页"""
        self.page += 1
    
    def prev_page(self) -> None:
        """上一页"""
        if self.page > 1:
            self.page -= 1
    
    def __str__(self) -> str:
        return f"ResourceSearchParams({self.keywords}, page={self.page})"
