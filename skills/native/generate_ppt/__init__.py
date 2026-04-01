"""
生成PPT课件技能
对应第5章 - AgentSkills
自动生成PPT课件大纲（可转换为PPT）
"""

from typing import Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class SkillMetadata:
    name: str = "generate_ppt"
    display_name: str = "生成PPT课件"
    version: str = "1.0.0"
    description: str = "根据教学大纲生成PPT课件内容"
    category: str = "课件制作"
    tags: List[str] = field(default_factory=lambda: ["PPT", "课件", "演示"])


class GeneratePPTSkill:
    """生成PPT课件技能"""

    def __init__(self, llm_service=None):
        self.metadata = SkillMetadata()
        self.llm_service = llm_service

    def get_metadata(self) -> SkillMetadata:
        return self.metadata

    def execute(self, state: Any, course_info: Dict[str, Any]) -> Dict[str, Any]:
        """执行技能 - 生成PPT课件"""
        course_name = course_info.get("course_name", "")

        # 检查是否有LLM服务
        if self.llm_service:
            slides = self._generate_slides_with_llm(course_info)
        else:
            # 使用本地生成
            slides = self._generate_slides(course_name)

        # 保存PPT大纲
        self._save_ppt(course_name, slides, course_info)

        result = {
            "status": "success",
            "course_name": course_name,
            "slides": slides,
            "total_slides": len(slides),
            "filename": f"{course_name}_课件.md",
        }

        return result

    def _generate_slides_with_llm(
        self, course_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """使用LLM生成PPT内容"""
        course_name = course_info.get("course_name", "")

        system_prompt = """你是一名专业的PPT制作专家，擅长设计教学课件。
请根据课程信息，设计一份完整的PPT大纲。
请用中文回复。"""

        prompt = f"""请为课程「{course_name}」设计一份PPT课件大纲。

请设计8-10页幻灯片，每页包含：
- type: 幻灯片类型 (title/toc/content/summary/ending)
- title: 标题
- content: 主要内容
- notes: 演讲备注

请以JSON数组格式返回。"""

        result = self.llm_service.generate_json(prompt, system_prompt)

        if "error" in result:
            print(f"LLM生成失败，使用本地生成: {result.get('error')}")
            return self._generate_slides(course_name)

        # 确保返回的是列表
        if isinstance(result, list):
            return result
        else:
            return self._generate_slides(course_name)

    def _generate_slides(self, course_name: str) -> List[Dict[str, Any]]:
        """生成PPT幻灯片内容"""
        slides = []

        # 封面
        slides.append(
            {
                "type": "title",
                "title": course_name,
                "content": "教学课件",
                "notes": "课程名称和授课信息",
            }
        )

        # 目录
        slides.append(
            {
                "type": "toc",
                "title": "课程目录",
                "content": "\n".join(
                    [
                        "第一章: 课程概述",
                        "第二章: 基础理论",
                        "第三章: 核心方法",
                        "第四章: 实践应用",
                        "第五章: 总结与展望",
                    ]
                ),
                "notes": "展示本课程的主要内容框架",
            }
        )

        # 课程概述
        slides.append(
            {
                "type": "content",
                "title": "第一章: 课程概述",
                "content": f"""{course_name}简介
• {course_name}的定义
• {course_name}的发展历程
• {course_name}的研究意义
• 课程学习目标""",
                "notes": "帮助学生建立整体认知",
            }
        )

        # 基础理论
        slides.append(
            {
                "type": "content",
                "title": "第二章: 基础理论",
                "content": f"""{course_name}基本概念
• 核心概念解析
• 基本原理
• 理论框架
• 经典案例分析""",
                "notes": "夯实理论基础",
            }
        )

        # 核心方法
        slides.append(
            {
                "type": "content",
                "title": "第三章: 核心方法",
                "content": f"""主要方法与技术
• 方法论概述
• 关键技术介绍
• 工具与平台
• 方法对比分析""",
                "notes": "掌握核心技术",
            }
        )

        # 实践应用
        slides.append(
            {
                "type": "content",
                "title": "第四章: 实践应用",
                "content": f"""{course_name}应用场景
• 行业应用案例
• 项目实践演示
• 常见问题与解决
• 实战技巧分享""",
                "notes": "提升实践能力",
            }
        )

        # 总结
        slides.append(
            {
                "type": "summary",
                "title": "第五章: 总结与展望",
                "content": f"""课程总结
• 核心知识点回顾
• 学习收获
• 拓展方向
• 思考与练习""",
                "notes": "巩固学习成果",
            }
        )

        # 结束页
        slides.append(
            {
                "type": "ending",
                "title": "谢谢！",
                "content": "欢迎提问与交流",
                "notes": "结束页面",
            }
        )

        return slides

    def _save_ppt(
        self,
        course_name: str,
        slides: List[Dict[str, Any]],
        course_info: Dict[str, Any] = None,
    ) -> None:
        """保存PPT大纲"""
        from tools.file_tools import MarkdownGenerator, FileTool

        generator = MarkdownGenerator()
        textbook_name = course_info.get("textbook_name", "") if course_info else ""
        file_tool = FileTool(course_name=course_name, textbook_name=textbook_name)

        md_content = generator.generate_ppt_content(course_name, slides)

        filename = f"{course_name}_课件.md"
        file_tool.save_markdown(md_content, filename, subdir="ppt")


def generate_ppt_skill(
    context: Dict[str, Any], previous_results: Dict[str, Any]
) -> Dict[str, Any]:
    """Pipeline调用的执行函数"""
    skill = GeneratePPTSkill()
    return skill.execute(None, context)
