"""
习题数据对象 (DO-011)

用于存储和管理习题信息
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class QuestionType(str, Enum):
    """题目类型"""
    SINGLE_CHOICE = "single_choice"      # 单选题
    MULTIPLE_CHOICE = "multiple_choice"  # 多选题
    FILL_BLANK = "fill_blank"            # 填空题
    TRUE_FALSE = "true_false"            # 判断题
    SHORT_ANSWER = "short_answer"        # 简答题
    CALCULATION = "calculation"          # 计算题
    PROOF = "proof"                      # 证明题
    APPLICATION = "application"          # 应用题
    COMPREHENSIVE = "comprehensive"      # 综合题


class DifficultyLevel(str, Enum):
    """难度等级"""
    EASY = "easy"           # 容易
    MEDIUM = "medium"       # 中等
    HARD = "hard"           # 较难
    CHALLENGING = "challenging"  # 挑战


class ExerciseStatus(str, Enum):
    """习题状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


@dataclass
class Exercise:
    """
    习题数据对象
    
    存储习题的完整信息，包括题目、答案、解析等
    """
    # 基本信息
    exercise_id: str
    question_text: str                  # 题目内容
    question_type: QuestionType         # 题目类型
    
    # 答案信息
    correct_answer: str                 # 正确答案
    answer_options: Optional[List[Dict[str, str]]] = None  # 选项（选择题）
    
    # 解析信息
    explanation: str = ""               # 详细解析
    key_points: List[str] = field(default_factory=list)  # 考查知识点
    solution_steps: List[str] = field(default_factory=list)  # 解题步骤
    
    # 分类信息
    subject: Optional[str] = None
    education_level: Optional[str] = None
    topic: Optional[str] = None
    chapter: Optional[str] = None
    
    # 难度和分值
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    score: float = 5.0                  # 分值
    estimated_time: int = 5             # 预计答题时间（分钟）
    
    # 能力维度
    knowledge_dimension: List[str] = field(default_factory=list)  # 知识维度
    ability_dimension: List[str] = field(default_factory=list)    # 能力维度
    
    # 元信息
    status: ExerciseStatus = ExerciseStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    usage_count: int = 0
    accuracy_rate: Optional[float] = None  # 正确率统计
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "exercise_id": self.exercise_id,
            "question_text": self.question_text,
            "question_type": self.question_type.value,
            "correct_answer": self.correct_answer,
            "answer_options": self.answer_options,
            "explanation": self.explanation,
            "key_points": self.key_points,
            "solution_steps": self.solution_steps,
            "subject": self.subject,
            "education_level": self.education_level,
            "topic": self.topic,
            "chapter": self.chapter,
            "difficulty": self.difficulty.value,
            "score": self.score,
            "estimated_time": self.estimated_time,
            "knowledge_dimension": self.knowledge_dimension,
            "ability_dimension": self.ability_dimension,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by,
            "usage_count": self.usage_count,
            "accuracy_rate": self.accuracy_rate
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Exercise":
        """从字典创建"""
        return cls(
            exercise_id=data["exercise_id"],
            question_text=data["question_text"],
            question_type=QuestionType(data.get("question_type", "short_answer")),
            correct_answer=data["correct_answer"],
            answer_options=data.get("answer_options"),
            explanation=data.get("explanation", ""),
            key_points=data.get("key_points", []),
            solution_steps=data.get("solution_steps", []),
            subject=data.get("subject"),
            education_level=data.get("education_level"),
            topic=data.get("topic"),
            chapter=data.get("chapter"),
            difficulty=DifficultyLevel(data.get("difficulty", "medium")),
            score=data.get("score", 5.0),
            estimated_time=data.get("estimated_time", 5),
            knowledge_dimension=data.get("knowledge_dimension", []),
            ability_dimension=data.get("ability_dimension", []),
            status=ExerciseStatus(data.get("status", "active")),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else datetime.now(),
            created_by=data.get("created_by", "system"),
            usage_count=data.get("usage_count", 0),
            accuracy_rate=data.get("accuracy_rate")
        )
    
    def update_usage(self) -> None:
        """更新使用次数"""
        self.usage_count += 1
        self.updated_at = datetime.now()
    
    def add_key_point(self, point: str) -> None:
        """添加考查知识点"""
        if point not in self.key_points:
            self.key_points.append(point)
            self.updated_at = datetime.now()
    
    def __str__(self) -> str:
        return f"Exercise({self.exercise_id}: {self.question_type.value})"


@dataclass
class ExerciseSet:
    """
    习题集数据对象
    
    用于组织一组相关习题
    """
    set_id: str
    set_name: str
    description: str = ""
    exercises: List[Exercise] = field(default_factory=list)
    
    # 分类信息
    subject: Optional[str] = None
    education_level: Optional[str] = None
    topic: Optional[str] = None
    
    # 统计信息
    total_score: float = 0.0
    total_time: int = 0
    
    # 元信息
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    
    def add_exercise(self, exercise: Exercise) -> None:
        """添加习题"""
        self.exercises.append(exercise)
        self.total_score += exercise.score
        self.total_time += exercise.estimated_time
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "set_id": self.set_id,
            "set_name": self.set_name,
            "description": self.description,
            "exercises": [e.to_dict() for e in self.exercises],
            "subject": self.subject,
            "education_level": self.education_level,
            "topic": self.topic,
            "total_score": self.total_score,
            "total_time": self.total_time,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by
        }
