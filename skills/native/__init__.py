"""
skills.native - Native Skills 模块

内置的原生 Python 技能，高性能、可控性强。

使用方式:
```python
from skills.native import (
    LessonPreparationSkill,
    ExerciseGeneratorSkill,
    TestPaperGeneratorSkill,
)

# 直接使用
skill = LessonPreparationSkill(llm_service=my_llm)
result = await skill.execute({
    "education_level": "高中",
    "subject": "数学",
    "topic": "函数的概念"
})

# 通过注册中心使用
from skills._base import SkillRegistry, SkillExecutor

SkillRegistry.register_native(LessonPreparationSkill)
executor = SkillExecutor(llm_service=my_llm)
result = await executor.execute("lesson_preparation", context)
```
"""

# ==================== 核心技能 ====================

from .lesson_preparation import (
    # Native Skill 类
    LessonPreparationSkill,
    FeedbackProcessingSkill,
    # 元数据
    LESSON_PREPARATION_METADATA,
    FEEDBACK_PROCESSING_METADATA,
    # 便捷函数
    native_complete_lesson_preparation,
)

from .teaching_assessment import (
    # Native Skill 类
    ExerciseGeneratorSkill,
    TestPaperGeneratorSkill,
    TeachingExplainerSkill,
    AnswerEvaluatorSkill,
    # 元数据
    EXERCISE_GENERATOR_METADATA,
    TEST_PAPER_GENERATOR_METADATA,
    TEACHING_EXPLAINER_METADATA,
    ANSWER_EVALUATOR_METADATA,
    # 便捷函数
    native_exercise_generator,
)

__all__ = [
    # 备课技能
    "LessonPreparationSkill",
    "FeedbackProcessingSkill",
    "LESSON_PREPARATION_METADATA",
    "FEEDBACK_PROCESSING_METADATA",
    "native_complete_lesson_preparation",
    
    # 评估技能
    "ExerciseGeneratorSkill",
    "TestPaperGeneratorSkill",
    "TeachingExplainerSkill",
    "AnswerEvaluatorSkill",
    "EXERCISE_GENERATOR_METADATA",
    "TEST_PAPER_GENERATOR_METADATA",
    "TEACHING_EXPLAINER_METADATA",
    "ANSWER_EVALUATOR_METADATA",
    "native_exercise_generator",
]
