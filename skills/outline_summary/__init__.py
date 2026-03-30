"""
归纳教学大纲技能
对应第5章 - AgentSkills
归纳总结课程的教学大纲
"""

from typing import Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class SkillMetadata:
    name: str = "outline_summary"
    display_name: str = "归纳教学大纲"
    version: str = "1.0.0"
    description: str = "根据教案和教材内容归纳总结教学大纲"
    category: str = "教学内容规划"
    tags: List[str] = field(default_factory=lambda: ["大纲", "课程结构", "章节"])


class OutlineSummarySkill:
    """归纳教学大纲技能"""

    def __init__(self, llm_service=None):
        self.metadata = SkillMetadata()
        self.llm_service = llm_service

    def get_metadata(self) -> SkillMetadata:
        return self.metadata

    def execute(self, state: Any, course_info: Dict[str, Any]) -> Dict[str, Any]:
        """执行技能 - 归纳教学大纲"""
        course_name = course_info.get("course_name", "")
        teaching_hours = course_info.get("teaching_hours", 16)

        # 检查是否有LLM服务
        if self.llm_service:
            chapters = self._generate_chapters_with_llm(course_info)
        else:
            # 使用本地生成
            chapters = self._generate_chapters(course_name, teaching_hours)

        # 保存教学大纲
        self._save_syllabus(course_name, chapters, course_info)

        result = {
            "status": "success",
            "course_name": course_name,
            "chapters": chapters,
            "total_chapters": len(chapters),
            "filename": f"{course_name}_教学大纲.md",
        }

        return result

    def _generate_chapters_with_llm(
        self, course_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """使用LLM生成教学大纲"""
        course_name = course_info.get("course_name", "")
        teaching_hours = course_info.get("teaching_hours", 16)
        education_level = course_info.get("education_level", "大学")

        system_prompt = """你是一名专业的课程设计专家，擅长制定教学大纲。
请根据课程信息，设计一份合理的教学大纲，包含章节安排、课时分配等。
请用中文回复。"""

        # 根据课时数确定章节数
        if teaching_hours <= 8:
            num_chapters = 3
        elif teaching_hours <= 16:
            num_chapters = 5
        else:
            num_chapters = 8

        prompt = f"""请为课程「{course_name}」设计一份教学大纲：

- 总课时：{teaching_hours}课时
- 教育阶段：{education_level}
- 章节数：{num_chapters}章

请设计{num_chapters}章节目录，每章包含：
- title: 章节标题
- hours: 课时数
- content: 主要内容
- objectives: 学习目标

请以JSON数组格式返回。"""

        result = self.llm_service.generate_json(prompt, system_prompt)

        if "error" in result:
            print(f"LLM生成失败，使用本地生成: {result.get('error')}")
            return self._generate_chapters(course_name, teaching_hours)

        # 确保返回的是列表
        if isinstance(result, list):
            return result
        elif isinstance(result, dict) and "chapters" in result:
            return result["chapters"]
        else:
            return self._generate_chapters(course_name, teaching_hours)

    def _generate_chapters(
        self, course_name: str, teaching_hours: int
    ) -> List[Dict[str, Any]]:
        """生成课程章节"""
        # 根据课时数确定章节数
        if teaching_hours <= 8:
            num_chapters = 3
        elif teaching_hours <= 16:
            num_chapters = 5
        else:
            num_chapters = 8

        chapters = []

        # 绪论章
        chapters.append(
            {
                "title": "绪论",
                "hours": 2,
                "content": f"{course_name}概述、发展历史、研究意义",
                "objectives": "了解课程整体框架，明确学习目标",
            }
        )

        # 中间章节
        for i in range(1, num_chapters - 1):
            chapters.append(
                {
                    "title": f"第{i}章 核心内容{i}",
                    "hours": teaching_hours // num_chapters,
                    "content": f"{course_name}的核心概念、原理和方法",
                    "objectives": f"掌握{course_name}的核心知识点",
                }
            )

        # 总结章
        chapters.append(
            {
                "title": "总结与实践",
                "hours": 2,
                "content": "课程总结、综合实践、拓展应用",
                "objectives": "整合知识，提升实践能力",
            }
        )

        return chapters

    def _save_syllabus(
        self,
        course_name: str,
        chapters: List[Dict[str, Any]],
        course_info: Dict[str, Any],
    ) -> None:
        """保存教学大纲"""
        from ai_teacher_agent.tools.file_tools import MarkdownGenerator, FileTool

        generator = MarkdownGenerator()
        textbook_name = course_info.get("textbook_name", "")
        file_tool = FileTool(course_name=course_name, textbook_name=textbook_name)

        md_content = generator.generate_syllabus(course_name, course_info, chapters)

        filename = f"{course_name}_教学大纲.md"
        file_tool.save_markdown(md_content, filename, subdir="syllabus")


def outline_summary_skill(
    context: Dict[str, Any], previous_results: Dict[str, Any]
) -> Dict[str, Any]:
    """Pipeline调用的执行函数"""
    skill = OutlineSummarySkill()
    return skill.execute(None, context)
