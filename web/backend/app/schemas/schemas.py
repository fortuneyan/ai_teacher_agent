"""
AI教师Agent Web后端 - Pydantic 数据模式
"""
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============================================================
# 枚举类型
# ============================================================

class UserRole(str, Enum):
    TEACHER = "teacher"
    STUDENT = "student"
    ADMIN = "admin"
    PARENT = "parent"


class LessonPlanStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"


class ChannelStatus(str, Enum):
    WAITING = "waiting"
    TEACHING = "teaching"
    ENDED = "ended"


class ExerciseType(str, Enum):
    SINGLE = "single"      # 单选题
    MULTIPLE = "multiple"  # 多选题
    FILL = "fill"          # 填空题
    JUDGE = "judge"        # 判断题
    SHORT = "short"        # 简答题
    CALC = "calc"          # 计算题
    PROOF = "proof"        # 证明题
    APPLY = "apply"        # 应用题
    COMPREHENSIVE = "comprehensive"  # 综合题


class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    CHALLENGE = "challenge"


# ============================================================
# 用户相关模式
# ============================================================

class UserBase(BaseModel):
    username: str
    full_name: Optional[str] = None
    role: UserRole
    subject: Optional[str] = None
    grade: Optional[str] = None


class UserCreate(UserBase):
    password: str
    email: Optional[EmailStr] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: int
    uuid: str
    email: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ============================================================
# 教案相关模式
# ============================================================

class LessonPlanCreate(BaseModel):
    """创建教案请求（触发AI生成）"""
    subject: str
    grade: str
    topic: str
    version: Optional[str] = None
    duration: Optional[int] = 45
    custom_objectives: Optional[List[str]] = None


class LessonPlanUpdate(BaseModel):
    """更新教案"""
    title: Optional[str] = None
    content: Optional[str] = None
    key_points: Optional[str] = None
    teaching_flow: Optional[List[Dict[str, Any]]] = None
    resources: Optional[List[Dict[str, Any]]] = None


class LessonPlanResponse(BaseModel):
    id: int
    uuid: str
    title: str
    subject: Optional[str]
    grade: Optional[str]
    topic: Optional[str]
    status: LessonPlanStatus
    content: Optional[str]
    teaching_flow: Optional[List[Dict[str, Any]]]
    ai_generated: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LessonPlanListItem(BaseModel):
    """教案列表项（不含完整内容）"""
    id: int
    uuid: str
    title: str
    subject: Optional[str]
    grade: Optional[str]
    topic: Optional[str]
    status: LessonPlanStatus
    ai_generated: bool
    created_at: datetime


# ============================================================
# 习题相关模式
# ============================================================

class ExerciseGenerateRequest(BaseModel):
    """生成习题请求"""
    subject: str
    grade: str
    topic: str
    type: ExerciseType
    difficulty: DifficultyLevel
    count: int = 1


class ExerciseResponse(BaseModel):
    id: int
    uuid: str
    subject: Optional[str]
    grade: Optional[str]
    topic: Optional[str]
    type: ExerciseType
    difficulty: DifficultyLevel
    content: str
    options: Optional[List[Dict[str, str]]]
    answer: Optional[str]
    explanation: Optional[str]
    knowledge_points: Optional[List[str]]

    class Config:
        from_attributes = True


# ============================================================
# 频道相关模式
# ============================================================

class ChannelCreate(BaseModel):
    """创建频道"""
    lesson_plan_id: Optional[int] = None
    name: str


class ChannelJoin(BaseModel):
    """加入频道"""
    channel_code: str


class ChannelResponse(BaseModel):
    id: int
    channel_code: str
    name: str
    status: ChannelStatus
    current_page: int
    student_count: int
    teacher_name: Optional[str]
    lesson_title: Optional[str]
    created_at: datetime


class QuizStart(BaseModel):
    """发起随堂测试"""
    exercise_id: int


class QuizAnswerSubmit(BaseModel):
    """提交答案"""
    channel_id: int
    exercise_id: int
    answer: str


class QuizStatsResponse(BaseModel):
    """测试统计"""
    total_students: int
    submitted_count: int
    correct_count: int
    correct_rate: float
    option_counts: Dict[str, int]


# ============================================================
# WebSocket消息模式
# ============================================================

class WSMessage(BaseModel):
    """WebSocket消息格式"""
    type: str
    channel_id: Optional[int] = None
    from_user: Optional[str] = None
    data: Dict[str, Any] = {}
    timestamp: Optional[str] = None


# ============================================================
# 学情相关模式
# ============================================================

class ClassAnalyticsResponse(BaseModel):
    """班级学情统计"""
    class_name: str
    student_count: int
    avg_score: float
    homework_completion_rate: float
    knowledge_mastery: Dict[str, float]   # 知识点掌握度
    score_distribution: Dict[str, int]    # 成绩分布
    weak_points: List[str]                # 薄弱知识点


class StudentProgressResponse(BaseModel):
    """学生学习进度"""
    student_name: str
    subject: str
    exercises_done: int
    avg_score: float
    knowledge_mastery: Dict[str, float]
    recent_activities: List[Dict[str, Any]]
