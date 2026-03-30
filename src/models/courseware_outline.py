"""
课件大纲数据对象

用于存储课件结构和每页内容
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class SlideType(str, Enum):
    """幻灯片类型"""
    TITLE = "title"           # 标题页
    CONTENT = "content"       # 内容页
    IMAGE = "image"           # 图片页
    CHART = "chart"           # 图表页
    VIDEO = "video"           # 视频页
    EXERCISE = "exercise"     # 练习页
    SUMMARY = "summary"       # 总结页
    TRANSITION = "transition" # 过渡页


@dataclass
class SlideOutline:
    """单页幻灯片大纲"""
    slide_number: int
    slide_type: SlideType
    title: str
    content_points: List[str] = field(default_factory=list)
    layout_suggestion: str = ""
    materials_needed: List[str] = field(default_factory=list)
    speaker_notes: str = ""
    duration_minutes: int = 2
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "slide_number": self.slide_number,
            "slide_type": self.slide_type.value,
            "title": self.title,
            "content_points": self.content_points,
            "layout_suggestion": self.layout_suggestion,
            "materials_needed": self.materials_needed,
            "speaker_notes": self.speaker_notes,
            "duration_minutes": self.duration_minutes
        }


@dataclass
class CoursewareOutline:
    """
    课件大纲数据对象
    
    存储完整课件的结构信息
    """
    # 基本信息
    outline_id: str
    plan_id: Optional[str] = None
    title: str = ""
    
    # 幻灯片列表
    slides: List[SlideOutline] = field(default_factory=list)
    
    # 设计信息
    design_theme: str = "简洁教育风格"
    color_scheme: str = "蓝色系"
    font_suggestion: str = "微软雅黑"
    
    # 元信息
    total_slides: int = 0
    estimated_duration: int = 0  # 总时长（分钟）
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """初始化后计算总页数和时长"""
        self.total_slides = len(self.slides)
        self.estimated_duration = sum(s.duration_minutes for s in self.slides)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "outline_id": self.outline_id,
            "plan_id": self.plan_id,
            "title": self.title,
            "slides": [s.to_dict() for s in self.slides],
            "design_theme": self.design_theme,
            "color_scheme": self.color_scheme,
            "font_suggestion": self.font_suggestion,
            "total_slides": self.total_slides,
            "estimated_duration": self.estimated_duration,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    def add_slide(self, slide: SlideOutline) -> None:
        """添加幻灯片"""
        self.slides.append(slide)
        self.total_slides = len(self.slides)
        self.estimated_duration = sum(s.duration_minutes for s in self.slides)
        self.updated_at = datetime.now()
    
    def get_slide(self, number: int) -> Optional[SlideOutline]:
        """获取指定页码的幻灯片"""
        for slide in self.slides:
            if slide.slide_number == number:
                return slide
        return None
    
    def __str__(self) -> str:
        return f"CoursewareOutline({self.outline_id}: {self.total_slides} slides)"
