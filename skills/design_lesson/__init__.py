"""
设计教案技能
对应第5章 - AgentSkills
根据收集的教材内容设计详细教案
"""

from typing import Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class SkillMetadata:
    """技能元数据"""

    name: str = "design_lesson"
    display_name: str = "设计教案"
    version: str = "1.0.0"
    description: str = "根据教材内容和课程标准设计详细的教学方案"
    category: str = "教学内容设计"
    tags: List[str] = field(default_factory=lambda: ["教案", "教学设计", "方案"])


class DesignLessonSkill:
    """设计教案技能"""

    def __init__(self, llm_service=None):
        self.metadata = SkillMetadata()
        self.llm_service = llm_service

    def get_metadata(self) -> SkillMetadata:
        return self.metadata

    def execute(self, state: Any, course_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行技能 - 设计教案

        Args:
            state: Agent状态
            course_info: 课程信息

        Returns:
            教案内容
        """
        course_name = course_info.get("course_name", "")
        teaching_hours = course_info.get("teaching_hours", 16)
        target_audience = course_info.get("target_audience", "学生")

        # 检查是否有LLM服务
        if self.llm_service:
            # 使用LLM生成教案
            lesson_plan = self._generate_lesson_plan_with_llm(course_info)
        else:
            # 使用本地生成
            lesson_plan = self._generate_lesson_plan(
                course_name, teaching_hours, target_audience
            )

        # 保存教案到知识库
        self._save_lesson_plan(course_name, lesson_plan, course_info)

        result = {
            "status": "success",
            "course_name": course_name,
            "lesson_plan": lesson_plan,
            "filename": f"{course_name}_教案.md",
        }

        return result

    def _generate_lesson_plan_with_llm(
        self, course_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """使用LLM生成教案"""
        course_name = course_info.get("course_name", "")
        course_type = course_info.get("course_type", "")
        target_audience = course_info.get("target_audience", "学生")
        teaching_hours = course_info.get("teaching_hours", 16)
        education_level = course_info.get("education_level", "大学")
        textbook_name = course_info.get("textbook_name", "")

        system_prompt = """你是一名专业的教学设计专家，擅长编写高质量的教案。
请根据提供的信息，设计一份详细的教案。
教案应该包含：教学目标（知识目标、能力目标、情感目标）、教学重难点、教学方法、教学过程、课后反思等部分。
请用中文回复。"""

        prompt = f"""请为以下课程设计一份详细的教案：

- 课程名称：{course_name}
- 课程类型：{course_type}
- 目标受众：{target_audience}
- 总课时：{teaching_hours}课时
- 教育阶段：{education_level}
- 教材版本：{textbook_name}

请以JSON格式返回，包含以下字段：
- knowledge_objectives: 知识目标
- ability_objectives: 能力目标  
- emotion_objectives: 情感目标
- key_points: 教学重点
- difficult_points: 教学难点
- teaching_methods: 教学方法
- teaching_process: 教学过程
- evaluation: 教学评价
- reflection: 课后反思

请确保内容专业、详细、实用。"""

        result = self.llm_service.generate_json(prompt, system_prompt)

        # 如果LLM调用失败，使用本地生成
        if "error" in result:
            print(f"LLM生成失败，使用本地生成: {result.get('error')}")
            return self._generate_lesson_plan(
                course_name, teaching_hours, target_audience
            )

        return result

    def _generate_lesson_plan(
        self, course_name: str, teaching_hours: int, target_audience: str
    ) -> Dict[str, Any]:
        """生成教案内容"""

        # 教学目标
        knowledge_objectives = f"""1. 掌握{course_name}的基本概念和核心原理
2. 理解{course_name}的理论体系和应用场景
3. 了解{course_name}的最新发展趋势"""

        ability_objectives = f"""1. 能够运用{course_name}的知识解决实际问题
2. 能够独立完成{course_name}相关的项目实践
3. 具备{course_name}的创新思维和分析能力"""

        emotion_objectives = f"""1. 培养对{course_name}的学习兴趣
2. 树立严谨求实的科学态度
3. 增强团队协作和自主学习的意识"""

        # 教学重难点
        key_points = f"""1. {course_name}的核心概念和基本原理
2. {course_name}的理论框架和方法论
3. {course_name}的实际应用技能"""

        difficult_points = f"""1. {course_name}复杂理论的深入理解
2. {course_name}在实际场景中的应用
3. {course_name}的创新实践"""

        # 教学方法
        teaching_methods = """1. 讲授法：系统讲解基本概念和理论
2. 案例分析法：通过实际案例加深理解
3. 讨论法：组织学生进行小组讨论
4. 实践法：安排实验和项目实践
5. 翻转课堂：课前预习与课内讨论结合"""

        # 教学过程
        teaching_process = """## 第一课时：导入与基础概念

### (一) 导入环节 (5分钟)
- 复习上节课内容
- 引入新课主题

### (二) 新课讲授 (30分钟)
- 讲解基本概念
- 分析核心原理
- 展示案例

### (三) 课堂练习 (10分钟)
- 随堂练习
- 师生互动

### (四) 小结与作业 (5分钟)
- 总结本节重点
- 布置课后作业

## 后续课时安排...
"""

        # 教学评价
        evaluation = """1. 平时成绩(40%): 课堂表现、作业完成情况、期中测试
2. 实践成绩(30%): 实验报告、项目作品
3. 期末成绩(30%): 闭卷考试"""

        # 课后反思
        reflection = """1. 本节课教学目标的达成情况
2. 教学方法和手段的有效性
3. 学生反馈和存在的问题
4. 改进措施和下一步计划"""

        return {
            "knowledge_objectives": knowledge_objectives,
            "ability_objectives": ability_objectives,
            "emotion_objectives": emotion_objectives,
            "key_points": key_points,
            "difficult_points": difficult_points,
            "teaching_methods": teaching_methods,
            "teaching_process": teaching_process,
            "evaluation": evaluation,
            "reflection": reflection,
        }

    def _save_lesson_plan(
        self, course_name: str, lesson_plan: Dict[str, Any], course_info: Dict[str, Any]
    ) -> None:
        """保存教案到知识库"""
        from tools.file_tools import MarkdownGenerator, FileTool

        generator = MarkdownGenerator()
        textbook_name = course_info.get("textbook_name", "")
        file_tool = FileTool(course_name=course_name, textbook_name=textbook_name)

        md_content = generator.generate_lesson_plan(
            course_name, course_info, lesson_plan
        )

        filename = f"{course_name}_教案.md"
        file_tool.save_markdown(md_content, filename, subdir="lesson_plans")


def design_lesson_skill(
    context: Dict[str, Any], previous_results: Dict[str, Any]
) -> Dict[str, Any]:
    """Pipeline调用的执行函数"""
    skill = DesignLessonSkill()
    return skill.execute(None, context)
