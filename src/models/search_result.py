"""
搜索结果数据对象 (DO-007)
MVP版本简化实现
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class SearchResult:
    """
    搜索结果数据对象
    
    用于封装课程标准搜索的结果
    """
    # 搜索元信息
    query: str
    results: List[Dict[str, Any]] = field(default_factory=list)
    total_count: int = 0
    
    # 搜索参数
    filters: Dict[str, Any] = field(default_factory=dict)
    
    # 元信息
    search_time_ms: int = 0
    searched_at: datetime = field(default_factory=datetime.now)
    source: str = "mock"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "query": self.query,
            "results": self.results,
            "total_count": self.total_count,
            "filters": self.filters,
            "search_time_ms": self.search_time_ms,
            "searched_at": self.searched_at.isoformat(),
            "source": self.source
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SearchResult":
        """从字典创建"""
        return cls(
            query=data["query"],
            results=data.get("results", []),
            total_count=data.get("total_count", 0),
            filters=data.get("filters", {}),
            search_time_ms=data.get("search_time_ms", 0),
            searched_at=datetime.fromisoformat(data["searched_at"]) if "searched_at" in data else datetime.now(),
            source=data.get("source", "mock")
        )
    
    def add_result(self, result: Dict[str, Any]) -> None:
        """添加搜索结果"""
        self.results.append(result)
        self.total_count = len(self.results)
    
    def get_top_results(self, n: int = 5) -> List[Dict[str, Any]]:
        """获取前N个结果"""
        return self.results[:n]
    
    def __str__(self) -> str:
        return f"SearchResult({self.query}: {self.total_count} results)"
