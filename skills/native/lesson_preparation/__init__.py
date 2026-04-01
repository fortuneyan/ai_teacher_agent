"""
skills.native.lesson_preparation - 智能备课 Native Skill

这是原生 Python 实现的备课技能，性能高、可控性强。
"""

import logging
from typing import Dict, Any, Optional

# 导入原实现（从 skills 目录）
import sys
from pathlib import Path

# 添加父目录到路径以便导入
_current_dir = Path(__file__).parent
_parent_dir = _current_dir.parent.parent
if str(_parent_dir) not in sys.path:
    sys.path.insert(0, str(_parent_dir))

# 从原始位置导入
from skills.lesson_preparation import (
    LessonPreparationAssistant as _OriginalAssistant,
    CurriculumStandardFetcher,
    ResourceSearcher,
    ContentGenerator,
    FeedbackProcessor,
    FeedbackEvaluator,
    ResourceType,
    ContentQuality,
    CurriculumStandard,
    TeachingResource,
    LessonPlan,
    Courseware,
    UserFeedback,
    FeedbackEvaluation,
    prepare_lesson,
    process_user_feedback,
    complete_lesson_preparation,
    generate_detailed_objectives,
    design_detailed_teaching_process,
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

LESSON_PREPARATION_METADATA = SkillMetadata(
    name="lesson_preparation",
    display_name="智能备课",
    version="1.0.0",
    description="根据课程标准和学生情况，生成完整的教学设计方案、教案和课件",
    skill_type=SkillType.NATIVE,
    category=SkillCategory.CORE,
    author="AI Teacher Team",
    tags=["备课", "教案", "课件", "教学设计"],
    triggers=["备课", "教案", "课程设计", "教学设计", "制作课件"],
    input_schema={
        "type": "object",
        "properties": {
            "education_level": {
                "type": "string",
                "description": "教育阶段，如 高中、初中、小学"
            },
            "subject": {
                "type": "string",
                "description": "学科名称"
            },
            "topic": {
                "type": "string",
                "description": "课程主题"
            },
            "teaching_hours": {
                "type": "number",
                "description": "课时数"
            },
        },
        "required": ["education_level", "subject", "topic"]
    },
    provides=["lesson_plan", "courseware", "teaching_resources"],
)

FEEDBACK_PROCESSING_METADATA = SkillMetadata(
    name="feedback_processing",
    display_name="反馈处理",
    version="1.0.0",
    description="处理用户对教案的反馈，评估反馈质量并修改教案",
    skill_type=SkillType.NATIVE,
    category=SkillCategory.CORE,
    author="AI Teacher Team",
    tags=["反馈", "教案修改"],
    triggers=["反馈", "修改教案", "调整教案"],
)

# ==================== Native Skill 类 ====================

@SkillRegistry.register_native
class LessonPreparationSkill(BaseSkill):
    """
    智能备课 Native Skill
    
    封装完整的备课流程，包括：
    - 获取课程标准
    - 搜索教学资源
    - 生成教案
    - 生成课件
    
    使用方式:
    ```python
    from skills._base import SkillExecutor
    
    executor = SkillExecutor(llm_service=my_llm)
    result = await executor.execute("lesson_preparation", {
        "education_level": "高中",
        "subject": "数学",
        "topic": "函数的概念"
    })
    ```
    """
    
    metadata = LESSON_PREPARATION_METADATA
    
    def __init__(self, llm_service=None, **kwargs):
        super().__init__(llm_service, **kwargs)
        # 使用原始实现
        self._assistant = _OriginalAssistant(llm_service=llm_service)
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行备课"""
        try:
            # 提取参数
            course_name = context.get("course_name") or f"{context.get('education_level', '')} {context.get('subject', '')}"
            topic = context.get("topic")
            teaching_hours = context.get("teaching_hours", 1)
            
            # 调用原始实现
            result = await self._assistant.prepare_lesson(
                course_name=course_name,
                topic=topic,
                teaching_hours=teaching_hours,
            )
            
            return {
                "status": "success",
                "data": result,
                "metadata": {
                    "skill": self.metadata.name,
                    "version": self.metadata.version,
                    "type": SkillType.NATIVE.value,
                }
            }
            
        except Exception as e:
            logger.exception("Error in LessonPreparationSkill.execute()")
            return {
                "status": "error",
                "message": str(e),
                "code": "LESSON_PREP_ERROR"
            }
    
    async def _process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """内部处理逻辑（保留用于扩展）"""
        return await self.execute(context)


@SkillRegistry.register_native
class FeedbackProcessingSkill(BaseSkill):
    """
    反馈处理 Native Skill
    
    处理用户对教案的反馈，评估质量并修改教案。
    """
    
    metadata = FEEDBACK_PROCESSING_METADATA
    
    def __init__(self, llm_service=None, **kwargs):
        super().__init__(llm_service, **kwargs)
        self._feedback_evaluator = FeedbackEvaluator(llm_service=llm_service)
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行反馈处理"""
        try:
            feedback_text = context.get("feedback")
            lesson_plan = context.get("lesson_plan")
            
            if not feedback_text:
                return {
                    "status": "error",
                    "message": "feedback is required"
                }
            
            # 评估反馈
            evaluation = await self._feedback_evaluator.evaluate(feedback_text)
            
            # 如果反馈有效且需要修改教案
            modified_plan = None
            if lesson_plan and evaluation.get("needs_modification"):
                modified_plan = await self._feedback_evaluator.modify(
                    lesson_plan=lesson_plan,
                    feedback=feedback_text
                )
            
            return {
                "status": "success",
                "data": {
                    "evaluation": evaluation,
                    "modified_plan": modified_plan,
                },
                "metadata": {
                    "skill": self.metadata.name,
                    "version": self.metadata.version,
                    "type": SkillType.NATIVE.value,
                }
            }
            
        except Exception as e:
            logger.exception("Error in FeedbackProcessingSkill.execute()")
            return {
                "status": "error",
                "message": str(e),
                "code": "FEEDBACK_ERROR"
            }


# ==================== 便捷函数 ====================

async def native_complete_lesson_preparation(
    education_level: str,
    subject: str,
    topic: str,
    llm_service=None,
    **kwargs
) -> Dict[str, Any]:
    """
    便捷函数：完整备课流程（使用 Native Skill）
    
    这是 complete_lesson_preparation 的 Native 版本。
    """
    skill = LessonPreparationSkill(llm_service=llm_service)
    return await skill.execute({
        "education_level": education_level,
        "subject": subject,
        "topic": topic,
        **kwargs
    })


# ==================== 导出 ====================

__all__ = [
    # Skill 类
    "LessonPreparationSkill",
    "FeedbackProcessingSkill",
    # 元数据
    "LESSON_PREPARATION_METADATA",
    "FEEDBACK_PROCESSING_METADATA",
    # 原始类和函数（从 skills 导入）
    "_OriginalAssistant",
    "CurriculumStandardFetcher",
    "ResourceSearcher",
    "ContentGenerator",
    "FeedbackProcessor",
    "FeedbackEvaluator",
    "ResourceType",
    "ContentQuality",
    "CurriculumStandard",
    "TeachingResource",
    "LessonPlan",
    "Courseware",
    "UserFeedback",
    "FeedbackEvaluation",
    "prepare_lesson",
    "process_user_feedback",
    "complete_lesson_preparation",
    "generate_detailed_objectives",
    "design_detailed_teaching_process",
    # 便捷函数
    "native_complete_lesson_preparation",
]
