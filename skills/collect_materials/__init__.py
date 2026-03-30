"""
收集教材技能
对应第5章 - AgentSkills
负责收集指定课程的教材内容
"""

from typing import Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class SkillMetadata:
    """技能元数据 - 对应5.3.1"""

    name: str = "collect_materials"
    display_name: str = "收集教材内容"
    version: str = "1.0.0"
    description: str = "根据课程名称收集相关的教材内容、教学大纲和课程标准"
    category: str = "教学内容收集"
    tags: List[str] = field(default_factory=lambda: ["教学", "教材", "收集"])


class CollectMaterialsSkill:
    """
    收集教材技能
    使用搜索工具收集课程相关教材内容
    """

    def __init__(self, search_tool=None):
        self.metadata = SkillMetadata()
        self.search_tool = search_tool

    def get_metadata(self) -> SkillMetadata:
        """获取技能元数据"""
        return self.metadata

    def execute(self, state: Any, course_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行技能 - 收集教材内容

        Args:
            state: Agent状态
            course_info: 课程信息

        Returns:
            收集到的教材内容
        """
        course_name = course_info.get("course_name", "")
        course_type = course_info.get("course_type", "")

        # 使用搜索工具收集教材
        if self.search_tool:
            from ai_teacher_agent.tools.search_tools import TextbookCollector
            from ai_teacher_agent.tools.search_tools import CurriculumStandardFetcher

            # 收集教材
            collector = TextbookCollector(self.search_tool)
            materials = collector.collect(course_name, course_type)

            # 收集课程标准
            fetcher = CurriculumStandardFetcher(self.search_tool)
            standards = fetcher.fetch(
                course_name, course_info.get("education_level", "高中")
            )
        else:
            # 模拟数据
            materials = self._mock_materials(course_name)
            standards = self._mock_standards(course_name)

        # 保存到知识库
        self._save_to_knowledge_base(course_info, materials, standards)

        result = {
            "status": "success",
            "course_name": course_name,
            "materials_count": len(materials.get("materials", [])),
            "standards_count": len(standards.get("standards", [])),
            "materials": materials,
            "standards": standards,
        }

        return result

    def _mock_materials(self, course_name: str) -> Dict[str, Any]:
        """生成模拟教材数据"""
        return {
            "course_name": course_name,
            "materials": [
                {
                    "title": f"{course_name}基础教程",
                    "source": "https://example.com/textbook",
                    "content": f"{course_name}是研究...",
                    "type": "textbook",
                },
                {
                    "title": f"{course_name}高级教程",
                    "source": "https://example.com/advanced",
                    "content": f"深入学习{course_name}...",
                    "type": "textbook",
                },
            ],
            "source_count": 2,
        }

    def _mock_standards(self, course_name: str) -> Dict[str, Any]:
        """生成模拟课程标准数据"""
        return {
            "course_name": course_name,
            "standards": [
                {
                    "title": f"{course_name}课程标准",
                    "source": "https://example.com/standard",
                    "content": f"{course_name}教学目标...",
                }
            ],
        }

    def _save_to_knowledge_base(
        self, course_info: Dict[str, Any], materials: Dict, standards: Dict
    ) -> None:
        """保存到知识库"""
        from ai_teacher_agent.tools.file_tools import FileTool

        course_name = course_info.get("course_name", "")
        textbook_name = course_info.get("textbook_name", "")

        file_tool = FileTool(course_name=course_name, textbook_name=textbook_name)

        # 保存教材
        for material in materials.get("materials", []):
            content = f"""# {material.get("title")}

来源: {material.get("source")}

类型: {material.get("type")}

内容:
{material.get("content")}
"""
            filename = f"{course_name}_{material.get('type')}.md"
            file_tool.save_markdown(content, filename, subdir="textbooks")

        # 保存课程标准
        for standard in standards.get("standards", []):
            content = f"""# {standard.get("title")}

来源: {standard.get("source")}

内容:
{standard.get("content")}
"""
            filename = f"{course_name}_standard.md"
            file_tool.save_markdown(content, filename, subdir="curriculum_standards")


# Pipeline中使用的执行函数
def collect_materials_skill(
    context: Dict[str, Any], previous_results: Dict[str, Any]
) -> Dict[str, Any]:
    """Pipeline调用的执行函数"""
    skill = CollectMaterialsSkill()
    return skill.execute(None, context)
