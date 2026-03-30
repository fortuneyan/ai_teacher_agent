"""
资源搜索结果数据对象 (DO-009)

用于封装资源搜索的结果
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class ResourceSearchResult:
    """
    资源搜索结果数据对象
    
    封装资源搜索的结果和元信息
    """
    # 搜索参数
    params: Dict[str, Any] = field(default_factory=dict)
    
    # 结果列表
    resources: List[Dict[str, Any]] = field(default_factory=list)
    
    # 分页信息
    total_count: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0
    
    # 搜索元信息
    search_time_ms: int = 0
    searched_at: datetime = field(default_factory=datetime.now)
    source: str = "mock"
    
    def __post_init__(self):
        """初始化后计算总页数"""
        if self.page_size > 0:
            self.total_pages = (self.total_count + self.page_size - 1) // self.page_size
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "params": self.params,
            "resources": self.resources,
            "total_count": self.total_count,
            "page": self.page,
            "page_size": self.page_size,
            "total_pages": self.total_pages,
            "search_time_ms": self.search_time_ms,
            "searched_at": self.searched_at.isoformat(),
            "source": self.source
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResourceSearchResult":
        """从字典创建"""
        return cls(
            params=data.get("params", {}),
            resources=data.get("resources", []),
            total_count=data.get("total_count", 0),
            page=data.get("page", 1),
            page_size=data.get("page_size", 20),
            search_time_ms=data.get("search_time_ms", 0),
            searched_at=datetime.fromisoformat(data["searched_at"]) if "searched_at" in data else datetime.now(),
            source=data.get("source", "mock")
        )
    
    def has_next_page(self) -> bool:
        """是否有下一页"""
        return self.page < self.total_pages
    
    def has_prev_page(self) -> bool:
        """是否有上一页"""
        return self.page > 1
    
    def get_page_range(self) -> tuple:
        """获取当前页的记录范围"""
        start = (self.page - 1) * self.page_size + 1
        end = min(self.page * self.page_size, self.total_count)
        return (start, end)
    
    def __str__(self) -> str:
        return f"ResourceSearchResult({self.total_count} resources, page {self.page}/{self.total_pages})"
