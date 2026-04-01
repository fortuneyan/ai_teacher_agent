"""
skills.native.teaching_assessment - 教学评估 Native Skill

这是原生 Python 实现的教学评估技能，包括：
- 习题生成
- 试卷生成
- 教学讲解
- 答案评估
"""

import logging
from typing import Dict, Any, List, Optional

import sys
from pathlib import Path

_current_dir = Path(__file__).parent
_parent_dir = _current_dir.parent.parent
if str(_parent_dir) not in sys.path:
    sys.path.insert(0, str(_parent_dir))

# 从原始位置导入
from skills.teaching_assessment import (
    ExerciseGenerator as _OriginalExerciseGenerator,
    TestPaperGenerator as _OriginalTestPaperGenerator,
    TeachingExplainer as _OriginalTeachingExplainer,
    AnswerEvaluator as _OriginalAnswerEvaluator,
    Question,
    QuestionType,
    Difficulty,
    TestPaper,
    PaperType,
    PaperConfig,
    Explanation,
    ExplanationType,
    EvaluationResult,
    EvaluationType,
    ScoreLevel,
)

from skills._base import (
    BaseSkill,
    SkillMetadata,
    SkillCategory,
    SkillType,
    SkillRegistry,
)

logger = logging.getLogger(__name__)

# ==================== Native Skill 元数据 ====================

EXERCISE_GENERATOR_METADATA = SkillMetadata(
    name="exercise_generator",
    display_name="习题生成",
    version="1.0.0",
    description="根据知识点生成多种题型的练习题，包括选择题、填空题、解答题等",
    skill_type=SkillType.NATIVE,
    category=SkillCategory.CORE,
    author="AI Teacher Team",
    tags=["习题", "练习题", "题目生成"],
    triggers=["生成习题", "出题", "练习题"],
    parameters=[
        {"name": "topic", "type": "string", "required": True, "description": "知识点或主题"},
        {"name": "num_each_type", "type": "number", "required": False, "default": 2, "description": "每种题型生成的数量"},
        {"name": "difficulty", "type": "string", "required": False, "default": "medium", "description": "难度：easy/medium/hard"},
    ],
)

TEST_PAPER_GENERATOR_METADATA = SkillMetadata(
    name="test_paper_generator",
    display_name="试卷生成",
    version="1.0.0",
    description="根据配置生成完整的试卷，支持章节测试、期中期末考试等",
    skill_type=SkillType.NATIVE,
    category=SkillCategory.CORE,
    author="AI Teacher Team",
    tags=["试卷", "考试", "测验"],
    triggers=["生成试卷", "出卷", "组卷"],
)

TEACHING_EXPLAINER_METADATA = SkillMetadata(
    name="teaching_explainer",
    display_name="教学讲解",
    version="1.0.0",
    description="提供多种形式的知识点讲解，包括概念解析、案例讲解等",
    skill_type=SkillType.NATIVE,
    category=SkillCategory.CORE,
    author="AI Teacher Team",
    tags=["讲解", "教学", "知识点"],
    triggers=["讲解", "知识点讲解", "教学讲解"],
)

ANSWER_EVALUATOR_METADATA = SkillMetadata(
    name="answer_evaluator",
    display_name="答案评估",
    version="1.0.0",
    description="评估学生的答题结果，提供详细的反馈和建议",
    skill_type=SkillType.NATIVE,
    category=SkillCategory.CORE,
    author="AI Teacher Team",
    tags=["评估", "批改", "评分"],
    triggers=["评估答案", "批改", "评分"],
)


# ==================== Native Skill 类 ====================

@SkillRegistry.register_native
class ExerciseGeneratorSkill(BaseSkill):
    """
    习题生成 Native Skill
    
    使用方式:
    ```python
    from skills._base import SkillExecutor
    
    executor = SkillExecutor(llm_service=my_llm)
    result = await executor.execute("exercise_generator", {
        "topic": "函数的概念",
        "num_each_type": 3,
        "difficulty": "medium"
    })
    ```
    """
    
    metadata = EXERCISE_GENERATOR_METADATA
    
    def __init__(self, llm_service=None, **kwargs):
        super().__init__(llm_service, **kwargs)
        self._generator = _OriginalExerciseGenerator(llm_service=llm_service)
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行习题生成"""
        try:
            topic = context.get("topic")
            num_each_type = context.get("num_each_type", 2)
            difficulty_str = context.get("difficulty", "medium")
            
            # 转换难度
            difficulty_map = {
                "easy": Difficulty.EASY,
                "medium": Difficulty.MEDIUM,
                "hard": Difficulty.HARD,
            }
            difficulty = difficulty_map.get(difficulty_str, Difficulty.MEDIUM)
            
            # 生成习题
            questions = self._generator.generate_batch(
                topic=topic,
                num_each_type=num_each_type,
                difficulty=difficulty
            )
            
            return {
                "status": "success",
                "data": {
                    "topic": topic,
                    "questions": [q.to_dict() for q in questions],
                    "total_count": len(questions),
                },
                "metadata": {
                    "skill": self.metadata.name,
                    "version": self.metadata.version,
                    "type": SkillType.NATIVE.value,
                }
            }
            
        except Exception as e:
            logger.exception("Error in ExerciseGeneratorSkill.execute()")
            return {
                "status": "error",
                "message": str(e),
                "code": "EXERCISE_GEN_ERROR"
            }


@SkillRegistry.register_native
class TestPaperGeneratorSkill(BaseSkill):
    """
    试卷生成 Native Skill
    """
    
    metadata = TEST_PAPER_GENERATOR_METADATA
    
    def __init__(self, llm_service=None, **kwargs):
        super().__init__(llm_service, **kwargs)
        self._generator = _OriginalTestPaperGenerator(llm_service=llm_service)
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行试卷生成"""
        try:
            # 提取参数
            subject = context.get("subject")
            grade = context.get("grade")
            paper_type = context.get("paper_type", "chapter_test")
            config = context.get("config", {})
            topics = context.get("topics", [])
            
            # 生成试卷
            paper = self._generator.generate(
                subject=subject,
                grade=grade,
                paper_type=paper_type,
                config=PaperConfig(**config) if config else None,
                topics=topics
            )
            
            return {
                "status": "success",
                "data": paper.to_dict() if hasattr(paper, 'to_dict') else paper,
                "metadata": {
                    "skill": self.metadata.name,
                    "version": self.metadata.version,
                    "type": SkillType.NATIVE.value,
                }
            }
            
        except Exception as e:
            logger.exception("Error in TestPaperGeneratorSkill.execute()")
            return {
                "status": "error",
                "message": str(e),
                "code": "PAPER_GEN_ERROR"
            }


@SkillRegistry.register_native
class TeachingExplainerSkill(BaseSkill):
    """
    教学讲解 Native Skill
    """
    
    metadata = TEACHING_EXPLAINER_METADATA
    
    def __init__(self, llm_service=None, **kwargs):
        super().__init__(llm_service, **kwargs)
        self._explainer = _OriginalTeachingExplainer(llm_service=llm_service)
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行教学讲解"""
        try:
            topic = context.get("topic")
            explanation_type = context.get("type", "concept")
            student_level = context.get("student_level")
            
            # 生成讲解
            explanation = self._explainer.explain(
                topic=topic,
                explanation_type=explanation_type,
                student_level=student_level
            )
            
            return {
                "status": "success",
                "data": explanation.to_dict() if hasattr(explanation, 'to_dict') else explanation,
                "metadata": {
                    "skill": self.metadata.name,
                    "version": self.metadata.version,
                    "type": SkillType.NATIVE.value,
                }
            }
            
        except Exception as e:
            logger.exception("Error in TeachingExplainerSkill.execute()")
            return {
                "status": "error",
                "message": str(e),
                "code": "EXPLAIN_ERROR"
            }


@SkillRegistry.register_native
class AnswerEvaluatorSkill(BaseSkill):
    """
    答案评估 Native Skill
    """
    
    metadata = ANSWER_EVALUATOR_METADATA
    
    def __init__(self, llm_service=None, **kwargs):
        super().__init__(llm_service, **kwargs)
        self._evaluator = _OriginalAnswerEvaluator(llm_service=llm_service)
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行答案评估"""
        try:
            question = context.get("question")
            answer = context.get("answer")
            evaluation_type = context.get("type", "detailed")
            
            # 评估答案
            result = self._evaluator.evaluate(
                question=question,
                answer=answer,
                evaluation_type=evaluation_type
            )
            
            return {
                "status": "success",
                "data": result.to_dict() if hasattr(result, 'to_dict') else result,
                "metadata": {
                    "skill": self.metadata.name,
                    "version": self.metadata.version,
                    "type": SkillType.NATIVE.value,
                }
            }
            
        except Exception as e:
            logger.exception("Error in AnswerEvaluatorSkill.execute()")
            return {
                "status": "error",
                "message": str(e),
                "code": "EVALUATE_ERROR"
            }


# ==================== 便捷函数 ====================

def native_exercise_generator(
    topic: str,
    llm_service=None,
    num_each_type: int = 2,
    difficulty: str = "medium"
) -> List[Question]:
    """便捷函数：生成习题"""
    generator = ExerciseGeneratorSkill(llm_service=llm_service)
    return generator._generator.generate_batch(
        topic=topic,
        num_each_type=num_each_type,
        difficulty=Difficulty(difficulty)
    )


# ==================== 导出 ====================

__all__ = [
    # Skill 类
    "ExerciseGeneratorSkill",
    "TestPaperGeneratorSkill",
    "TeachingExplainerSkill",
    "AnswerEvaluatorSkill",
    # 元数据
    "EXERCISE_GENERATOR_METADATA",
    "TEST_PAPER_GENERATOR_METADATA",
    "TEACHING_EXPLAINER_METADATA",
    "ANSWER_EVALUATOR_METADATA",
    # 原始类（从 skills 导入）
    "_OriginalExerciseGenerator",
    "_OriginalTestPaperGenerator",
    "_OriginalTeachingExplainer",
    "_OriginalAnswerEvaluator",
    "Question",
    "QuestionType",
    "Difficulty",
    "TestPaper",
    "PaperType",
    "PaperConfig",
    "Explanation",
    "ExplanationType",
    "EvaluationResult",
    "EvaluationType",
    "ScoreLevel",
    # 便捷函数
    "native_exercise_generator",
]
