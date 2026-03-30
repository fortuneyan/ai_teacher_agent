"""
试卷数据对象 (DO-012)

用于存储和管理试卷信息
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

from .exercise import Exercise, DifficultyLevel


class TestPaperType(str, Enum):
    """试卷类型"""
    PRACTICE = "practice"       # 练习题
    QUIZ = "quiz"               # 小测验
    UNIT_TEST = "unit_test"     # 单元测试
    MIDTERM = "midterm"         # 期中考试
    FINAL = "final"             # 期末考试
    MOCK_EXAM = "mock_exam"     # 模拟考试
    ENTRANCE = "entrance"       # 入学测试


class TestPaperStatus(str, Enum):
    """试卷状态"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


@dataclass
class TestPaperSection:
    """
    试卷章节数据对象
    
    试卷的一个部分（如选择题、填空题等）
    """
    section_id: str
    section_name: str           # 章节名称
    section_type: str           # 章节类型
    instructions: str = ""      # 答题说明
    exercises: List[Exercise] = field(default_factory=list)
    
    # 统计
    total_score: float = 0.0
    exercise_count: int = 0
    
    def add_exercise(self, exercise: Exercise) -> None:
        """添加习题"""
        self.exercises.append(exercise)
        self.total_score += exercise.score
        self.exercise_count += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "section_id": self.section_id,
            "section_name": self.section_name,
            "section_type": self.section_type,
            "instructions": self.instructions,
            "exercises": [e.to_dict() for e in self.exercises],
            "total_score": self.total_score,
            "exercise_count": self.exercise_count
        }


@dataclass
class TestPaperConfig:
    """
    试卷配置数据对象
    
    用于生成试卷的配置参数
    """
    # 基本信息
    paper_type: TestPaperType = TestPaperType.UNIT_TEST
    total_score: float = 100.0
    duration: int = 90                    # 考试时长（分钟）
    
    # 难度分布
    difficulty_distribution: Dict[DifficultyLevel, int] = field(default_factory=lambda: {
        DifficultyLevel.EASY: 30,
        DifficultyLevel.MEDIUM: 50,
        DifficultyLevel.HARD: 20
    })
    
    # 题型分布
    question_type_distribution: Dict[str, int] = field(default_factory=dict)
    
    # 知识点覆盖
    required_key_points: List[str] = field(default_factory=list)
    
    # 其他配置
    allow_random_order: bool = True       # 是否允许打乱顺序
    show_answer_immediately: bool = False  # 是否立即显示答案


@dataclass
class TestPaper:
    """
    试卷数据对象
    
    存储试卷的完整信息
    """
    # 基本信息
    paper_id: str
    paper_name: str
    paper_type: TestPaperType
    
    # 分类信息
    subject: Optional[str] = None
    education_level: Optional[str] = None
    topic: Optional[str] = None
    
    # 试卷结构
    sections: List[TestPaperSection] = field(default_factory=list)
    instructions: str = ""                # 总体答题说明
    
    # 考试信息
    total_score: float = 100.0
    duration: int = 90                    # 考试时长（分钟）
    pass_score: float = 60.0              # 及格分数
    
    # 状态
    status: TestPaperStatus = TestPaperStatus.DRAFT
    
    # 元信息
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    version: int = 1
    
    def add_section(self, section: TestPaperSection) -> None:
        """添加章节"""
        self.sections.append(section)
        self.total_score = sum(s.total_score for s in self.sections)
        self.updated_at = datetime.now()
    
    def get_all_exercises(self) -> List[Exercise]:
        """获取所有习题"""
        exercises = []
        for section in self.sections:
            exercises.extend(section.exercises)
        return exercises
    
    def get_exercise_count(self) -> int:
        """获取习题总数"""
        return sum(s.exercise_count for s in self.sections)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "paper_id": self.paper_id,
            "paper_name": self.paper_name,
            "paper_type": self.paper_type.value,
            "subject": self.subject,
            "education_level": self.education_level,
            "topic": self.topic,
            "sections": [s.to_dict() for s in self.sections],
            "instructions": self.instructions,
            "total_score": self.total_score,
            "duration": self.duration,
            "pass_score": self.pass_score,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by,
            "version": self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TestPaper":
        """从字典创建"""
        paper = cls(
            paper_id=data["paper_id"],
            paper_name=data["paper_name"],
            paper_type=TestPaperType(data.get("paper_type", "unit_test")),
            subject=data.get("subject"),
            education_level=data.get("education_level"),
            topic=data.get("topic"),
            instructions=data.get("instructions", ""),
            total_score=data.get("total_score", 100.0),
            duration=data.get("duration", 90),
            pass_score=data.get("pass_score", 60.0),
            status=TestPaperStatus(data.get("status", "draft")),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else datetime.now(),
            created_by=data.get("created_by", "system"),
            version=data.get("version", 1)
        )
        
        # 解析章节
        for section_data in data.get("sections", []):
            section = TestPaperSection(
                section_id=section_data["section_id"],
                section_name=section_data["section_name"],
                section_type=section_data["section_type"],
                instructions=section_data.get("instructions", ""),
                total_score=section_data.get("total_score", 0.0),
                exercise_count=section_data.get("exercise_count", 0)
            )
            # 解析习题
            from .exercise import Exercise
            for exercise_data in section_data.get("exercises", []):
                section.exercises.append(Exercise.from_dict(exercise_data))
            paper.sections.append(section)
        
        return paper
    
    def __str__(self) -> str:
        return f"TestPaper({self.paper_id}: {self.paper_name})"


@dataclass
class StudentAnswer:
    """
    学生答题记录
    """
    answer_id: str
    exercise_id: str
    student_id: str
    answer_text: str                    # 学生答案
    is_correct: Optional[bool] = None   # 是否正确
    score: float = 0.0                  # 得分
    time_spent: int = 0                 # 答题用时（秒）
    submitted_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "answer_id": self.answer_id,
            "exercise_id": self.exercise_id,
            "student_id": self.student_id,
            "answer_text": self.answer_text,
            "is_correct": self.is_correct,
            "score": self.score,
            "time_spent": self.time_spent,
            "submitted_at": self.submitted_at.isoformat()
        }


@dataclass
class TestResult:
    """
    测试结果数据对象
    """
    result_id: str
    paper_id: str
    student_id: str
    
    # 答题记录
    answers: List[StudentAnswer] = field(default_factory=list)
    
    # 成绩统计
    total_score: float = 0.0
    max_score: float = 0.0
    correct_count: int = 0
    wrong_count: int = 0
    unanswered_count: int = 0
    
    # 能力分析
    knowledge_mastery: Dict[str, float] = field(default_factory=dict)  # 知识点掌握度
    ability_analysis: Dict[str, float] = field(default_factory=dict)   # 能力维度分析
    
    # 用时
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_time: int = 0                   # 总用时（秒）
    
    # 元信息
    created_at: datetime = field(default_factory=datetime.now)
    
    def calculate_score(self) -> None:
        """计算总分"""
        self.total_score = sum(a.score for a in self.answers)
        self.correct_count = sum(1 for a in self.answers if a.is_correct)
        self.wrong_count = sum(1 for a in self.answers if a.is_correct is False)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "result_id": self.result_id,
            "paper_id": self.paper_id,
            "student_id": self.student_id,
            "answers": [a.to_dict() for a in self.answers],
            "total_score": self.total_score,
            "max_score": self.max_score,
            "correct_count": self.correct_count,
            "wrong_count": self.wrong_count,
            "unanswered_count": self.unanswered_count,
            "knowledge_mastery": self.knowledge_mastery,
            "ability_analysis": self.ability_analysis,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "total_time": self.total_time,
            "created_at": self.created_at.isoformat()
        }
