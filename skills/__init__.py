"""
AI Teacher Agent - 双层 Skill 架构

统一导出所有技能模块，支持 Native Skill 和 Soft Skill 两种类型。

Native Skill: Python 类实现，高性能硬编码
Soft Skill: SKILL.md 文档，LLM 理解后执行

使用示例:

    # 方式1: 使用统一执行器
    from skills import init_skills, execute_skill

    init_skills(soft_skills_dir="./skills/soft/skills")
    result = await execute_skill("lesson_preparation", {
        "education_level": "高中",
        "subject": "数学",
        "topic": "函数的概念"
    })

    # 方式2: 直接使用 Native Skill
    from skills import LessonPreparationSkill

    skill = LessonPreparationSkill(llm_service=my_llm)
    result = await skill.execute(context)

    # 方式3: 列出所有可用技能
    from skills import list_skills

    for name, info in list_skills().items():
        print(f"[{info['skill_type']}] {name}: {info['display_name']}")
"""

import logging
from typing import Dict, Any, Optional

# ==================== 核心框架 ====================

from skills._base import (
    BaseSkill,
    SkillMetadata,
    SkillCategory,
    SkillType,
    SkillRegistry,
    SkillExecutor,
    AsyncSkillExecutor,
    SoftSkillLoader,
    SoftSkillExecutor,
    SoftSkillTemplate,
)

# ==================== Native Skills ====================

from skills.native import (
    # 备课技能
    LessonPreparationAssistant,
    complete_lesson_preparation,
    FeedbackEvaluator,
    LessonPlan,
    UserFeedback,
    generate_detailed_objectives,
    design_detailed_teaching_process,
    
    # 评估技能
    ExerciseGenerator,
    TestPaperGenerator,
    TeachingExplainer,
    AnswerEvaluator,
    QuestionType,
    Difficulty,
    PaperType,
    PaperConfig,
)

# ==================== 原始模块导入（向后兼容） ====================

# 保留从 native 子目录导入的能力
from skills.native import lesson_preparation
from skills.native import teaching_assessment

# ==================== 初始化和管理函数 ====================

_soft_skills_loaded = False


def init_skills(soft_skills_dir: str = None) -> None:
    """
    初始化所有技能
    
    调用此函数将:
    1. 注册所有 Native Skills（如果尚未注册）
    2. 加载指定目录中的 Soft Skills
    
    Args:
        soft_skills_dir: Soft Skills 目录路径，默认 "skills/soft/skills"
    """
    global _soft_skills_loaded
    
    # 加载 Soft Skills
    if soft_skills_dir:
        loader = SoftSkillLoader()
        soft_skills = loader.load_directory(soft_skills_dir)
        for name, skill_data in soft_skills.items():
            SkillRegistry.register_soft(skill_data)
    
    _soft_skills_loaded = True
    logging.info(f"Skills initialized. Native: {len(SkillRegistry.list_natives())}, Soft: {len(SkillRegistry.list_softs())}")


def list_skills() -> Dict[str, Dict[str, Any]]:
    """
    列出所有已注册的技能
    
    Returns:
        {name: skill_info} 格式的字典
    """
    return SkillRegistry.list_all()


def get_skill(name: str) -> Optional[Any]:
    """
    获取指定名称的技能
    
    Args:
        name: 技能名称
        
    Returns:
        Native Skill 类或 Soft Skill 字典，不存在返回 None
    """
    return SkillRegistry.get(name)


def execute_skill(name: str, context: Dict[str, Any], llm_service=None) -> Dict[str, Any]:
    """
    统一执行技能（同步版本）
    
    自动选择 Native 或 Soft Skill 并执行。
    
    Args:
        name: 技能名称
        context: 执行上下文
        llm_service: LLM 服务实例（Soft Skill 必须）
        
    Returns:
        执行结果字典
    """
    import asyncio
    
    async def _execute():
        executor = SkillExecutor(llm_service=llm_service)
        return await executor.execute(name, context)
    
    return asyncio.get_event_loop().run_until_complete(_execute())


async def execute_skill_async(name: str, context: Dict[str, Any], llm_service=None) -> Dict[str, Any]:
    """
    统一执行技能（异步版本）
    
    Args:
        name: 技能名称
        context: 执行上下文
        llm_service: LLM 服务实例（Soft Skill 必须）
        
    Returns:
        执行结果字典
    """
    executor = SkillExecutor(llm_service=llm_service)
    return await executor.execute(name, context)


def create_soft_skill(
    name: str,
    display_name: str,
    description: str,
    parameters: list = None,
    triggers: list = None,
    content: str = None
) -> str:
    """
    创建 Soft Skill 的 SKILL.md 内容
    
    Args:
        name: 技能名称 (kebab-case)
        display_name: 显示名称
        description: 简短描述
        parameters: 参数列表
        triggers: 触发词列表
        content: Markdown 正文
        
    Returns:
        SKILL.md 格式的字符串
    """
    return SoftSkillTemplate.generate(
        name=name,
        display_name=display_name,
        description=description,
        parameters=parameters,
        triggers=triggers,
        content=content
    )


# ==================== __all__ ====================

__all__ = [
    # 核心框架
    "BaseSkill",
    "SkillMetadata",
    "SkillCategory",
    "SkillType",
    "SkillRegistry",
    "SkillExecutor",
    "AsyncSkillExecutor",
    "SoftSkillLoader",
    "SoftSkillExecutor",
    "SoftSkillTemplate",
    
    # Native Skills - 备课
    "LessonPreparationAssistant",
    "complete_lesson_preparation",
    "FeedbackEvaluator",
    "LessonPlan",
    "UserFeedback",
    "generate_detailed_objectives",
    "design_detailed_teaching_process",
    
    # Native Skills - 评估
    "ExerciseGenerator",
    "TestPaperGenerator",
    "TeachingExplainer",
    "AnswerEvaluator",
    "QuestionType",
    "Difficulty",
    "PaperType",
    "PaperConfig",
    
    # 模块（向后兼容）
    "lesson_preparation",
    "teaching_assessment",
    
    # 管理函数
    "init_skills",
    "list_skills",
    "get_skill",
    "execute_skill",
    "execute_skill_async",
    "create_soft_skill",
]
