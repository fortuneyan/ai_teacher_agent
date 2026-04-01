"""
教学评估模块

包含：
1. 习题生成器 (ExerciseGenerator)
2. 试卷生成器 (TestPaperGenerator)
3. 教学讲解器 (TeachingExplainer)
4. 答案评估器 (AnswerEvaluator)

使用示例：
    from skills.teaching_assessment import ExerciseGenerator, TestPaperGenerator
    
    # 生成习题
    exercise_gen = ExerciseGenerator()
    questions = exercise_gen.generate_batch(topic="函数", num_each_type=3)
    
    # 生成试卷
    paper_gen = TestPaperGenerator()
    paper = paper_gen.generate_paper(
        subject="高中数学",
        grade="高一",
        topic="函数的概念"
    )
"""

from .exercise_generator import (
    ExerciseGenerator,
    Question,
    QuestionType,
    Difficulty
)

from .test_paper_generator import (
    TestPaperGenerator,
    TestPaper,
    PaperType,
    PaperConfig
)

from .teaching_explainer import (
    TeachingExplainer,
    Explanation,
    ExplanationType
)

from .answer_evaluator import (
    AnswerEvaluator,
    EvaluationResult,
    EvaluationType,
    ScoreLevel
)

__all__ = [
    # 习题生成
    "ExerciseGenerator",
    "Question",
    "QuestionType",
    "Difficulty",
    
    # 试卷生成
    "TestPaperGenerator",
    "TestPaper",
    "PaperType",
    "PaperConfig",
    
    # 教学讲解
    "TeachingExplainer",
    "Explanation",
    "ExplanationType",
    
    # 答案评估
    "AnswerEvaluator",
    "EvaluationResult",
    "EvaluationType",
    "ScoreLevel",
]
