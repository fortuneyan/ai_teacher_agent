"""
搜索API Mock服务

模拟课程标准搜索服务
"""
import time
import random
from typing import List, Dict, Any, Optional
from datetime import datetime


class MockSearchAPI:
    """
    模拟搜索API
    
    提供课程标准的模拟搜索功能
    """
    
    # 模拟课标数据库
    MOCK_STANDARDS = [
        {
            "standard_id": "GB-2020-MATH-001",
            "standard_name": "普通高中数学课程标准",
            "standard_type": "国家",
            "education_level": "高中",
            "subject": "数学",
            "topic": "函数的概念",
            "content_requirements": [
                "理解函数的概念，了解构成函数的要素",
                "会求一些简单函数的定义域和值域",
                "了解映射的概念"
            ],
            "competency_requirements": [
                "数学抽象：从具体实例中抽象出函数概念",
                "逻辑推理：理解函数定义的逻辑结构"
            ],
            "achievement_standards": [
                "能用集合与对应的语言刻画函数",
                "能判断两个函数是否为同一函数"
            ],
            "suggested_hours": 4
        },
        {
            "standard_id": "GB-2020-MATH-002",
            "standard_name": "普通高中数学课程标准",
            "standard_type": "国家",
            "education_level": "高中",
            "subject": "数学",
            "topic": "函数的单调性",
            "content_requirements": [
                "理解函数的单调性及其几何意义",
                "会用定义判断简单函数的单调性"
            ],
            "competency_requirements": [
                "数学抽象：理解单调性的代数表达",
                "直观想象：通过图像理解单调性"
            ],
            "achievement_standards": [
                "能用定义证明简单函数的单调性",
                "能根据图像判断函数的单调性"
            ],
            "suggested_hours": 3
        },
        {
            "standard_id": "GB-2020-PHYSICS-001",
            "standard_name": "普通高中物理课程标准",
            "standard_type": "国家",
            "education_level": "高中",
            "subject": "物理",
            "topic": "牛顿运动定律",
            "content_requirements": [
                "理解牛顿第一定律",
                "掌握牛顿第二定律",
                "理解牛顿第三定律"
            ],
            "competency_requirements": [
                "物理观念：建立力和运动的关系",
                "科学思维：运用牛顿定律分析实际问题"
            ],
            "achievement_standards": [
                "能用牛顿定律解决简单的动力学问题",
                "能分析实际情境中的受力情况"
            ],
            "suggested_hours": 6
        }
    ]
    
    def __init__(self):
        self.call_count = 0
        self.last_call_time = None
    
    def search(
        self,
        query: str,
        education_level: Optional[str] = None,
        subject: Optional[str] = None,
        topic: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        模拟搜索课程标准
        
        Args:
            query: 搜索关键词
            education_level: 学段筛选
            subject: 学科筛选
            topic: 主题筛选
            limit: 返回结果数量限制
            
        Returns:
            搜索结果字典
        """
        start_time = time.time()
        
        # 模拟网络延迟
        time.sleep(random.uniform(0.1, 0.3))
        
        # 过滤结果
        results = []
        for std in self.MOCK_STANDARDS:
            # 关键词匹配
            if query and query.lower() not in std["topic"].lower():
                continue
            
            # 学段筛选
            if education_level and std["education_level"] != education_level:
                continue
            
            # 学科筛选
            if subject and std["subject"] != subject:
                continue
            
            # 主题筛选
            if topic and std["topic"] != topic:
                continue
            
            # 添加相关性分数
            std_copy = std.copy()
            std_copy["relevance_score"] = random.uniform(0.7, 0.99)
            std_copy["extracted_at"] = datetime.now().isoformat()
            results.append(std_copy)
        
        # 限制结果数量
        results = results[:limit]
        
        search_time_ms = int((time.time() - start_time) * 1000)
        
        self.call_count += 1
        self.last_call_time = datetime.now()
        
        return {
            "query": query,
            "results": results,
            "total_count": len(results),
            "filters": {
                "education_level": education_level,
                "subject": subject,
                "topic": topic
            },
            "search_time_ms": search_time_ms,
            "searched_at": datetime.now().isoformat(),
            "source": "mock_search_api"
        }
    
    def get_by_id(self, standard_id: str) -> Optional[Dict[str, Any]]:
        """
        根据ID获取课标
        
        Args:
            standard_id: 课标ID
            
        Returns:
            课标数据或None
        """
        for std in self.MOCK_STANDARDS:
            if std["standard_id"] == standard_id:
                result = std.copy()
                result["relevance_score"] = 1.0
                result["extracted_at"] = datetime.now().isoformat()
                return result
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """获取Mock服务统计信息"""
        return {
            "call_count": self.call_count,
            "last_call_time": self.last_call_time.isoformat() if self.last_call_time else None,
            "available_standards": len(self.MOCK_STANDARDS)
        }
