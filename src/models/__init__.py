"""
数据对象模块

包含所有AI教师Agent使用的数据模型
"""

from .course_basic_info import CourseBasicInfo, ValidationResult
from .curriculum_standard import CurriculumStandard
from .user_feedback import UserFeedback
from .feedback_evaluation import FeedbackEvaluation
from .lesson_plan import LessonPlan, LessonPlanStatus
from .search_result import SearchResult
from .teaching_resource import TeachingResource, ResourceType, ResourceStatus
from .teaching_objectives import TeachingObjectives, ObjectiveLevel, ObjectiveStatus
from .session_context import SessionContext, SessionStatus
from .resource_search_params import ResourceSearchParams
from .resource_search_result import ResourceSearchResult
from .lesson_plan_update import LessonPlanUpdate, UpdateType, UpdateStatus
from .courseware_outline import CoursewareOutline, SlideOutline, SlideType

# 测试/讲解模块数据对象
from .exercise import (
    Exercise, ExerciseSet, QuestionType, 
    DifficultyLevel, ExerciseStatus
)
from .test_paper import (
    TestPaper, TestPaperSection, TestPaperConfig,
    TestPaperType, TestPaperStatus, StudentAnswer, TestResult
)
from .teaching_explanation import (
    TeachingExplanation, ExplanationStep, ExplanationType,
    ExplanationLevel, CommonMisconception, StudentQuestion
)

__all__ = [
    'CourseBasicInfo',
    'ValidationResult',
    'CurriculumStandard',
    'UserFeedback',
    'FeedbackEvaluation',
    'LessonPlan',
    'LessonPlanStatus',
    'SearchResult',
    'TeachingResource',
    'ResourceType',
    'ResourceStatus',
    'TeachingObjectives',
    'ObjectiveLevel',
    'ObjectiveStatus',
    'SessionContext',
    'SessionStatus',
    'ResourceSearchParams',
    'ResourceSearchResult',
    'LessonPlanUpdate',
    'UpdateType',
    'UpdateStatus',
    'CoursewareOutline',
    'SlideOutline',
    'SlideType',
    # 测试/讲解模块
    'Exercise',
    'ExerciseSet',
    'QuestionType',
    'DifficultyLevel',
    'ExerciseStatus',
    'TestPaper',
    'TestPaperSection',
    'TestPaperConfig',
    'TestPaperType',
    'TestPaperStatus',
    'StudentAnswer',
    'TestResult',
    'TeachingExplanation',
    'ExplanationStep',
    'ExplanationType',
    'ExplanationLevel',
    'CommonMisconception',
    'StudentQuestion',
]
