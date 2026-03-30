"""
数据对象: CourseBasicInfo (DO-001)
课程基本信息
"""

import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import uuid4
from dataclasses import dataclass, field, asdict


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    
    def add_error(self, error: str):
        """添加错误信息"""
        self.errors.append(error)
        self.is_valid = False


@dataclass
class CourseBasicInfo:
    """
    课程基本信息
    
    属性:
        education_level: 学段（小学/初中/高中）
        subject: 学科名称
        topic: 教学主题
        grade: 年级（可选）
        textbook_version: 教材版本（可选）
        suggested_hours: 建议课时数（默认1）
        input_timestamp: 输入时间戳
        session_id: 会话标识
    """
    
    # 必填字段
    education_level: str
    subject: str
    topic: str
    
    # 可选字段
    grade: Optional[str] = None
    textbook_version: Optional[str] = None
    suggested_hours: int = 1
    
    # 自动生成的字段
    input_timestamp: datetime = field(default_factory=datetime.now)
    session_id: str = field(default_factory=lambda: str(uuid4()))
    
    # 常量定义
    VALID_EDUCATION_LEVELS = ["小学", "初中", "高中"]
    MAX_SUBJECT_LENGTH = 20
    MIN_TOPIC_LENGTH = 2
    MAX_TOPIC_LENGTH = 100
    MIN_HOURS = 1
    MAX_HOURS = 10
    
    def __post_init__(self):
        """初始化后验证"""
        self._validate_and_normalize()
    
    def _validate_and_normalize(self):
        """验证并规范化数据"""
        # 确保input_timestamp是datetime对象
        if isinstance(self.input_timestamp, str):
            self.input_timestamp = datetime.fromisoformat(self.input_timestamp)
        
        # 验证education_level
        if self.education_level not in self.VALID_EDUCATION_LEVELS:
            raise ValueError(
                f"education_level必须是{self.VALID_EDUCATION_LEVELS}之一，"
                f"当前值：{self.education_level}"
            )
        
        # 验证subject
        if not self.subject or len(self.subject) == 0:
            raise ValueError("subject不能为空")
        if len(self.subject) > self.MAX_SUBJECT_LENGTH:
            raise ValueError(
                f"subject长度不能超过{self.MAX_SUBJECT_LENGTH}字符，"
                f"当前长度：{len(self.subject)}"
            )
        
        # 验证topic
        if not self.topic:
            raise ValueError("topic不能为空")
        if len(self.topic) < self.MIN_TOPIC_LENGTH:
            raise ValueError(
                f"topic长度不能少于{self.MIN_TOPIC_LENGTH}字符，"
                f"当前长度：{len(self.topic)}"
            )
        if len(self.topic) > self.MAX_TOPIC_LENGTH:
            raise ValueError(
                f"topic长度不能超过{self.MAX_TOPIC_LENGTH}字符，"
                f"当前长度：{len(self.topic)}"
            )
        
        # 验证suggested_hours
        if not isinstance(self.suggested_hours, int):
            raise ValueError(f"suggested_hours必须是整数，当前类型：{type(self.suggested_hours)}")
        if self.suggested_hours < self.MIN_HOURS or self.suggested_hours > self.MAX_HOURS:
            raise ValueError(
                f"suggested_hours必须在{self.MIN_HOURS}-{self.MAX_HOURS}之间，"
                f"当前值：{self.suggested_hours}"
            )
    
    @classmethod
    def validate(cls, data: Dict[str, Any]) -> ValidationResult:
        """
        验证数据字典
        
        Args:
            data: 要验证的数据字典
            
        Returns:
            ValidationResult: 验证结果
        """
        result = ValidationResult(is_valid=True)
        
        # 检查必填字段
        required_fields = ["education_level", "subject", "topic"]
        for field_name in required_fields:
            if field_name not in data or not data[field_name]:
                result.add_error(f"缺少必填字段：{field_name}")
        
        if not result.is_valid:
            return result
        
        # 验证education_level
        if data.get("education_level") not in cls.VALID_EDUCATION_LEVELS:
            result.add_error(
                f"education_level必须是{cls.VALID_EDUCATION_LEVELS}之一"
            )
        
        # 验证subject长度
        subject = data.get("subject", "")
        if len(subject) > cls.MAX_SUBJECT_LENGTH:
            result.add_error(
                f"subject长度不能超过{cls.MAX_SUBJECT_LENGTH}字符"
            )
        
        # 验证topic长度
        topic = data.get("topic", "")
        if len(topic) < cls.MIN_TOPIC_LENGTH:
            result.add_error(
                f"topic长度不能少于{cls.MIN_TOPIC_LENGTH}字符"
            )
        if len(topic) > cls.MAX_TOPIC_LENGTH:
            result.add_error(
                f"topic长度不能超过{cls.MAX_TOPIC_LENGTH}字符"
            )
        
        # 验证suggested_hours
        hours = data.get("suggested_hours", 1)
        if not isinstance(hours, int):
            result.add_error("suggested_hours必须是整数")
        elif hours < cls.MIN_HOURS or hours > cls.MAX_HOURS:
            result.add_error(
                f"suggested_hours必须在{cls.MIN_HOURS}-{cls.MAX_HOURS}之间"
            )
        
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            Dict: 包含所有字段的字典
        """
        data = asdict(self)
        # 将datetime转换为ISO格式字符串
        data['input_timestamp'] = self.input_timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CourseBasicInfo':
        """
        从字典创建对象
        
        Args:
            data: 数据字典
            
        Returns:
            CourseBasicInfo: 创建的对象
        """
        # 处理时间戳
        if 'input_timestamp' in data and isinstance(data['input_timestamp'], str):
            data['input_timestamp'] = datetime.fromisoformat(data['input_timestamp'])
        
        return cls(**data)
    
    def to_json(self) -> str:
        """
        转换为JSON字符串
        
        Returns:
            str: JSON字符串
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'CourseBasicInfo':
        """
        从JSON字符串创建对象
        
        Args:
            json_str: JSON字符串
            
        Returns:
            CourseBasicInfo: 创建的对象
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"{self.education_level}{self.grade or ''}{self.subject} - {self.topic}"
    
    def __repr__(self) -> str:
        """正式字符串表示"""
        return (
            f"CourseBasicInfo("
            f"education_level='{self.education_level}', "
            f"subject='{self.subject}', "
            f"topic='{self.topic}', "
            f"session_id='{self.session_id}')"
        )
    
    def get_cache_key(self) -> str:
        """
        获取缓存键
        
        Returns:
            str: 用于缓存的键
        """
        return f"course:{self.education_level}:{self.subject}:{self.topic}"
