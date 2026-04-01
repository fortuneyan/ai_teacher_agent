"""
制定进度计划技能
对应第5章 - AgentSkills
自动生成课程进度计划
"""

from typing import Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class SkillMetadata:
    name: str = "schedule_plan"
    display_name: str = "制定进度计划"
    version: str = "1.0.0"
    description: str = "根据课程大纲制定详细的教学进度计划"
    category: str = "进度规划"
    tags: List[str] = field(default_factory=lambda: ["进度", "计划", "排课"])


class SchedulePlanSkill:
    """制定进度计划技能"""

    def __init__(self, llm_service=None):
        self.metadata = SkillMetadata()
        self.llm_service = llm_service

    def get_metadata(self) -> SkillMetadata:
        return self.metadata

    def execute(self, state: Any, course_info: Dict[str, Any]) -> Dict[str, Any]:
        """执行技能 - 制定进度计划"""
        course_name = course_info.get("course_name", "")
        teaching_hours = course_info.get("teaching_hours", 16)
        weeks = course_info.get("weeks", 8)

        # 检查是否有LLM服务
        if self.llm_service:
            schedule = self._generate_schedule_with_llm(course_info)
        else:
            # 使用本地生成
            schedule = self._generate_schedule(course_name, teaching_hours, weeks)

        # 保存进度计划（JSON格式）
        self._save_schedule(course_name, schedule, teaching_hours, course_info)

        result = {
            "status": "success",
            "course_name": course_name,
            "schedule": schedule,
            "total_weeks": weeks,
            "filename": f"{course_name}_进度计划.json",
        }

        return result

    def _generate_schedule_with_llm(
        self, course_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """使用LLM生成进度计划"""
        course_name = course_info.get("course_name", "")
        teaching_hours = course_info.get("teaching_hours", 16)
        weeks = course_info.get("weeks", 8)

        system_prompt = """你是一名专业的教学规划专家，擅长制定课程进度计划。
请根据课程信息，设计一份详细的周进度计划。
请用中文回复。"""

        prompt = f"""请为课程「{course_name}」制定一份{weeks}周的教学进度计划：

- 总课时：{teaching_hours}课时
- 周数：{weeks}周

请为每一周制定计划，每一周包含：
- week: 周次
- topic: 主题
- hours: 课时数
- content: 教学内容
- objectives: 学习目标（数组）
- activities: 教学活动（数组）
- homework: 作业（数组）
- assessment: 考核方式

请以JSON数组格式返回。"""

        result = self.llm_service.generate_json(prompt, system_prompt)

        if "error" in result:
            print(f"LLM生成失败，使用本地生成: {result.get('error')}")
            return self._generate_schedule(course_name, teaching_hours, weeks)

        # 确保返回的是列表
        if isinstance(result, list):
            return result
        elif isinstance(result, dict) and "schedule" in result:
            return result["schedule"]
        else:
            return self._generate_schedule(course_name, teaching_hours, weeks)

    def _generate_schedule(
        self, course_name: str, teaching_hours: int, weeks: int
    ) -> List[Dict[str, Any]]:
        """生成课程进度计划"""
        hours_per_week = teaching_hours // weeks
        schedule = []

        for week in range(1, weeks + 1):
            week_plan = {
                "week": week,
                "topic": self._get_week_topic(week, weeks),
                "hours": hours_per_week,
                "content": self._get_week_content(week, weeks),
                "objectives": self._get_week_objectives(week, weeks),
                "activities": ["理论讲授", "案例分析", "课堂讨论", "实践练习"],
                "homework": ["复习本周内容", "完成课后练习", "预习下周内容"],
                "assessment": "平时表现" if week % 2 == 0 else "无",
            }
            schedule.append(week_plan)

        return schedule

    def _get_week_topic(self, week: int, total_weeks: int) -> str:
        """获取周主题"""
        if week == 1:
            return "课程导论"
        elif week == total_weeks:
            return "课程总结"
        elif week <= total_weeks * 0.3:
            return f"基础理论{week - 1}"
        elif week <= total_weeks * 0.7:
            return f"核心知识{week - int(total_weeks * 0.3)}"
        else:
            return f"实践应用{week - int(total_weeks * 0.7)}"

    def _get_week_content(self, week: int, total_weeks: int) -> str:
        """获取周教学内容"""
        if week == 1:
            return "课程介绍、学习目标、考核方式、课程框架"
        elif week == total_weeks:
            return "知识回顾、综合练习、期末答疑"
        else:
            return f"第{week}周相关知识点的讲解和练习"

    def _get_week_objectives(self, week: int, total_weeks: int) -> List[str]:
        """获取周学习目标"""
        if week == 1:
            return ["了解课程整体框架", "明确学习目标"]
        elif week == total_weeks:
            return ["巩固所学知识", "提升综合能力"]
        else:
            return ["掌握本周知识点", "能够进行简单应用"]

    def _save_schedule(
        self,
        course_name: str,
        schedule: List[Dict[str, Any]],
        teaching_hours: int,
        course_info: Dict[str, Any] = None,
    ) -> None:
        """保存进度计划（JSON格式）"""
        from tools.file_tools import JsonGenerator, FileTool

        generator = JsonGenerator()
        textbook_name = course_info.get("textbook_name", "") if course_info else ""
        file_tool = FileTool(course_name=course_name, textbook_name=textbook_name)

        json_data = generator.generate_schedule(course_name, teaching_hours, schedule)

        filename = f"{course_name}_进度计划.json"
        file_tool.save_json(json_data, filename, subdir="schedules")


def schedule_plan_skill(
    context: Dict[str, Any], previous_results: Dict[str, Any]
) -> Dict[str, Any]:
    """Pipeline调用的执行函数"""
    skill = SchedulePlanSkill()
    return skill.execute(None, context)
