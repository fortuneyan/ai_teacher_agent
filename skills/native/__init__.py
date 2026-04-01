"""
skills.native - Native Skills 模块

内置的原生 Python 技能，高性能、可控性强。

使用方式:
```python
from skills.native.lesson_preparation import LessonPreparationAssistant

assistant = LessonPreparationAssistant()
result = await assistant.prepare_lesson(
    course_name="高中数学",
    topic="函数的概念",
    education_level="高中"
)
```
"""

# ==================== 备课技能 ====================

from .lesson_preparation import (
    # 核心类
    LessonPreparationAssistant,
    CurriculumStandardFetcher,
    ResourceSearcher,
    ContentGenerator,
    FeedbackProcessor,
    FeedbackEvaluator,
    # 数据类
    LessonPlan,
    Courseware,
    TeachingResource,
    CurriculumStandard,
    UserFeedback,
    FeedbackEvaluation,
    ResourceType,
    ContentQuality,
    # 便捷函数
    prepare_lesson,
    process_user_feedback,
    complete_lesson_preparation,
    generate_detailed_objectives,
    design_detailed_teaching_process,
)

# ==================== 评估技能 ====================

from .teaching_assessment import (
    # 核心类
    ExerciseGenerator,
    TestPaperGenerator,
    TeachingExplainer,
    AnswerEvaluator,
    # 数据类
    Question,
    TestPaper,
    Explanation,
    EvaluationResult,
    # 枚举和配置
    QuestionType,
    Difficulty,
    PaperType,
    PaperConfig,
    ExplanationType,
    EvaluationType,
    ScoreLevel,
)

__all__ = [
    # 备课技能
    "LessonPreparationAssistant",
    "CurriculumStandardFetcher",
    "ResourceSearcher",
    "ContentGenerator",
    "FeedbackProcessor",
    "FeedbackEvaluator",
    "LessonPlan",
    "Courseware",
    "TeachingResource",
    "CurriculumStandard",
    "UserFeedback",
    "FeedbackEvaluation",
    "ResourceType",
    "ContentQuality",
    "prepare_lesson",
    "process_user_feedback",
    "complete_lesson_preparation",
    "generate_detailed_objectives",
    "design_detailed_teaching_process",
    
    # 评估技能
    "ExerciseGenerator",
    "TestPaperGenerator",
    "TeachingExplainer",
    "AnswerEvaluator",
    "Question",
    "TestPaper",
    "Explanation",
    "EvaluationResult",
    "QuestionType",
    "Difficulty",
    "PaperType",
    "PaperConfig",
    "ExplanationType",
    "EvaluationType",
    "ScoreLevel",
]
