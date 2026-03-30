"""
AI_Teacher Agent 技能模块
对应第5章 - AgentSkills定义和组织
"""

from ai_teacher_agent.skills.collect_materials import CollectMaterialsSkill
from ai_teacher_agent.skills.design_lesson import DesignLessonSkill
from ai_teacher_agent.skills.outline_summary import OutlineSummarySkill
from ai_teacher_agent.skills.generate_ppt import GeneratePPTSkill
from ai_teacher_agent.skills.schedule_plan import SchedulePlanSkill

__all__ = [
    "CollectMaterialsSkill",
    "DesignLessonSkill",
    "OutlineSummarySkill",
    "GeneratePPTSkill",
    "SchedulePlanSkill",
]
