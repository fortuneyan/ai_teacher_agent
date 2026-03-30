"""
智能讲解引擎

提供概念讲解、例题讲解、习题讲解等功能
"""
import uuid
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# 添加src到路径
src_path = Path(__file__).parent.parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from models import (
    TeachingExplanation, ExplanationStep, ExplanationType,
    ExplanationLevel, CommonMisconception,
    Exercise, CourseBasicInfo, TeachingObjectives
)
from mocks import MockLLMService


class TeachingExplainer:
    """
    智能讲解引擎
    
    根据教学内容生成结构化的讲解内容
    """
    
    def __init__(self):
        """初始化讲解引擎"""
        self.llm_service = MockLLMService()
        self.explanation_history: List[TeachingExplanation] = []
    
    def explain_concept(
        self,
        concept: str,
        course_info: CourseBasicInfo,
        level: ExplanationLevel = ExplanationLevel.INTERMEDIATE,
        prerequisites: List[str] = None
    ) -> TeachingExplanation:
        """
        概念讲解
        
        Args:
            concept: 概念名称
            course_info: 课程信息
            level: 讲解深度
            prerequisites: 前置知识
            
        Returns:
            TeachingExplanation: 讲解内容
        """
        explanation_id = f"exp_{uuid.uuid4().hex[:8]}"
        
        explanation = TeachingExplanation(
            explanation_id=explanation_id,
            explanation_type=ExplanationType.CONCEPT,
            title=f"{concept}的概念",
            topic=concept,
            subject=course_info.subject,
            education_level=course_info.education_level,
            level=level,
            prerequisites=prerequisites or []
        )
        
        # 生成引入
        explanation.introduction = self._generate_concept_introduction(concept, course_info)
        
        # 生成讲解步骤
        steps = self._generate_concept_steps(concept, level, course_info)
        for step in steps:
            explanation.add_step(step)
        
        # 生成总结
        explanation.conclusion = self._generate_concept_conclusion(concept)
        
        # 添加常见误区
        misconceptions = self._generate_common_misconceptions(concept)
        for misc in misconceptions:
            explanation.add_misconception(misc)
        
        # 添加拓展内容
        explanation.extension_questions = self._generate_extension_questions(concept)
        explanation.related_topics = self._generate_related_topics(concept, course_info.subject)
        
        self.explanation_history.append(explanation)
        return explanation
    
    def explain_example(
        self,
        example_title: str,
        problem: str,
        solution: str,
        course_info: CourseBasicInfo,
        key_points: List[str] = None
    ) -> TeachingExplanation:
        """
        例题讲解
        
        Args:
            example_title: 例题标题
            problem: 题目内容
            solution: 解答过程
            course_info: 课程信息
            key_points: 考查要点
            
        Returns:
            TeachingExplanation: 讲解内容
        """
        explanation_id = f"exp_{uuid.uuid4().hex[:8]}"
        
        explanation = TeachingExplanation(
            explanation_id=explanation_id,
            explanation_type=ExplanationType.EXAMPLE,
            title=example_title,
            topic=example_title,
            subject=course_info.subject,
            education_level=course_info.education_level,
            level=ExplanationLevel.INTERMEDIATE
        )
        
        # 生成引入
        explanation.introduction = f"本例题主要考查{', '.join(key_points) if key_points else '相关知识点'}。"
        
        # 生成讲解步骤
        steps = [
            ExplanationStep(
                step_number=1,
                step_title="审题分析",
                content=f"首先仔细阅读题目：{problem[:50]}...",
                key_points=["理解题意", "提取已知条件"],
                expected_duration=2
            ),
            ExplanationStep(
                step_number=2,
                step_title="思路分析",
                content=f"这道题需要运用{key_points[0] if key_points else '相关知识'}来解决。解题的关键是...",
                key_points=["确定解题方法", "明确解题步骤"],
                expected_duration=3
            ),
            ExplanationStep(
                step_number=3,
                step_title="详细解答",
                content=f"下面我们详细解答：{solution[:100]}...",
                key_points=["规范书写", "逻辑清晰"],
                expected_duration=5
            ),
            ExplanationStep(
                step_number=4,
                step_title="方法总结",
                content="通过这道例题，我们可以总结出以下解题方法...",
                key_points=["总结规律", "举一反三"],
                expected_duration=2
            )
        ]
        
        for step in steps:
            explanation.add_step(step)
        
        explanation.conclusion = "掌握这类题目的解题方法，需要在理解概念的基础上多加练习。"
        
        self.explanation_history.append(explanation)
        return explanation
    
    def explain_exercise(
        self,
        exercise: Exercise,
        course_info: CourseBasicInfo,
        student_wrong_answer: Optional[str] = None
    ) -> TeachingExplanation:
        """
        习题讲解
        
        Args:
            exercise: 习题对象
            course_info: 课程信息
            student_wrong_answer: 学生错误答案（可选，用于针对性讲解）
            
        Returns:
            TeachingExplanation: 讲解内容
        """
        explanation_id = f"exp_{uuid.uuid4().hex[:8]}"
        
        explanation = TeachingExplanation(
            explanation_id=explanation_id,
            explanation_type=ExplanationType.EXERCISE,
            title=f"习题讲解：{exercise.question_text[:30]}...",
            topic=exercise.topic or (course_info.topic if course_info else ""),
            subject=course_info.subject if course_info else exercise.subject,
            education_level=course_info.education_level if course_info else exercise.education_level,
            level=ExplanationLevel.INTERMEDIATE
        )
        
        # 生成引入
        explanation.introduction = f"本题考查{', '.join(exercise.key_points) if exercise.key_points else '相关知识点'}，难度为{exercise.difficulty.value}。"
        
        # 如果有学生错误答案，添加错误分析
        if student_wrong_answer:
            explanation.introduction += f"\n学生答案：{student_wrong_answer}"
        
        # 生成讲解步骤
        steps = []
        
        # 步骤1：题目分析
        steps.append(ExplanationStep(
            step_number=1,
            step_title="题目分析",
            content=f"题目：{exercise.question_text}\n\n这道题属于{exercise.question_type.value}，主要考查{exercise.key_points[0] if exercise.key_points else '基础知识'}。",
            key_points=["理解题意", "明确考点"],
            expected_duration=2
        ))
        
        # 步骤2：思路点拨
        if exercise.solution_steps:
            steps.append(ExplanationStep(
                step_number=2,
                step_title="解题思路",
                content=f"解题步骤：\n" + "\n".join(f"{i+1}. {step}" for i, step in enumerate(exercise.solution_steps)),
                key_points=exercise.solution_steps[:2],
                expected_duration=3
            ))
        
        # 步骤3：详细解答
        steps.append(ExplanationStep(
            step_number=3,
            step_title="详细解答",
            content=f"正确答案：{exercise.correct_answer}\n\n解析：{exercise.explanation}",
            key_points=["掌握解法", "理解原理"],
            expected_duration=4
        ))
        
        # 步骤4：方法总结
        steps.append(ExplanationStep(
            step_number=4,
            step_title="方法总结",
            content=f"这类{exercise.question_type.value}的解题关键是：\n1. 仔细审题\n2. 运用{exercise.key_points[0] if exercise.key_points else '相关知识'}\n3. 规范作答",
            key_points=["总结方法", "迁移应用"],
            expected_duration=2
        ))
        
        for step in steps:
            explanation.add_step(step)
        
        explanation.conclusion = f"通过这道{exercise.difficulty.value}难度的题目，我们巩固了{exercise.key_points[0] if exercise.key_points else '相关知识'}的应用。"
        
        self.explanation_history.append(explanation)
        return explanation
    
    def explain_mistake(
        self,
        concept: str,
        wrong_answer: str,
        correct_answer: str,
        course_info: CourseBasicInfo
    ) -> TeachingExplanation:
        """
        错误分析讲解
        
        Args:
            concept: 相关概念
            wrong_answer: 错误答案
            correct_answer: 正确答案
            course_info: 课程信息
            
        Returns:
            TeachingExplanation: 讲解内容
        """
        explanation_id = f"exp_{uuid.uuid4().hex[:8]}"
        
        explanation = TeachingExplanation(
            explanation_id=explanation_id,
            explanation_type=ExplanationType.ERROR_ANALYSIS,
            title=f"错误分析：{concept}",
            topic=concept,
            subject=course_info.subject,
            education_level=course_info.education_level,
            level=ExplanationLevel.INTERMEDIATE
        )
        
        explanation.introduction = f"很多同学在学习{concept}时容易犯这样的错误。下面我们详细分析错误原因。"
        
        steps = [
            ExplanationStep(
                step_number=1,
                step_title="错误呈现",
                content=f"错误答案：{wrong_answer}\n正确答案：{correct_answer}",
                key_points=["识别错误"],
                expected_duration=1
            ),
            ExplanationStep(
                step_number=2,
                step_title="错误原因分析",
                content=f"出现这个错误的主要原因是：\n1. 对{concept}的理解不够深入\n2. 混淆了相关概念\n3. 解题方法掌握不牢固",
                key_points=["分析原因", "找出根源"],
                expected_duration=3
            ),
            ExplanationStep(
                step_number=3,
                step_title="正确理解",
                content=f"正确的理解应该是：{correct_answer}。这涉及到{concept}的核心要点...",
                key_points=["纠正理解", "建立正确认知"],
                expected_duration=4
            ),
            ExplanationStep(
                step_number=4,
                step_title="避免再错",
                content="为了避免类似错误，建议：\n1. 加强概念理解\n2. 多做对比练习\n3. 建立错题本",
                key_points=["预防措施", "巩固提高"],
                expected_duration=2
            )
        ]
        
        for step in steps:
            explanation.add_step(step)
        
        explanation.conclusion = f"理解错误是学习的重要环节，通过分析错误可以加深对{concept}的理解。"
        
        self.explanation_history.append(explanation)
        return explanation
    
    def answer_question(
        self,
        question: str,
        course_info: CourseBasicInfo,
        context: str = None
    ) -> Dict[str, str]:
        """
        回答学生提问
        
        Args:
            question: 学生问题
            course_info: 课程信息
            context: 上下文信息（可选）
            
        Returns:
            Dict: 包含回答和相关内容
        """
        # 分析问题的类型和难度
        question_type = self._analyze_question_type(question)
        difficulty = self._estimate_difficulty(question)
        
        # 生成回答
        answer = self._generate_answer(question, course_info, question_type)
        
        # 生成相关知识点
        related_points = self._extract_related_points(question, course_info.subject)
        
        # 生成拓展问题
        extension = self._generate_extension(question, question_type)
        
        return {
            "question": question,
            "answer": answer,
            "question_type": question_type,
            "difficulty": difficulty,
            "related_points": related_points,
            "extension": extension
        }
    
    def _generate_concept_introduction(self, concept: str, course_info: CourseBasicInfo) -> str:
        """生成概念引入"""
        introductions = {
            "函数": f"在{course_info.education_level}数学中，函数是一个核心概念。它描述了变量之间的对应关系，是研究数量关系的重要工具。",
            "方程": f"方程是{course_info.education_level}数学的重要内容，它帮助我们解决实际问题中的未知量。",
            "几何": f"几何是研究空间形式的数学分支，在{course_info.education_level}阶段我们将学习更深入的{concept}知识。"
        }
        
        for key, value in introductions.items():
            if key in concept:
                return value
        
        return f"今天我们来学习{course_info.education_level}{course_info.subject}中的重要概念——{concept}。"
    
    def _generate_concept_steps(self, concept: str, level: ExplanationLevel, course_info: CourseBasicInfo) -> List[ExplanationStep]:
        """生成概念讲解步骤"""
        steps = []
        
        # 步骤1：直观感知
        steps.append(ExplanationStep(
            step_number=1,
            step_title="直观感知",
            content=f"首先，让我们通过具体例子来感受{concept}。例如：[具体例子]。从这些例子中，我们可以发现...",
            key_points=["从具体到抽象", "建立直观认识"],
            visual_aids=["示例图片", "具体数据"],
            expected_duration=3,
            interaction_prompt="你能举出生活中的例子吗？"
        ))
        
        # 步骤2：定义讲解
        if level == ExplanationLevel.BASIC:
            definition = f"{concept}的定义是：[基础定义]。简单来说，就是..."
        elif level == ExplanationLevel.INTERMEDIATE:
            definition = f"{concept}的严格定义是：[标准定义]。理解这个定义需要注意三个要点：..."
        else:
            definition = f"{concept}的完整定义是：[深入定义]。从数学角度看，这个定义包含了深刻的内涵..."
        
        steps.append(ExplanationStep(
            step_number=2,
            step_title="定义讲解",
            content=definition,
            key_points=["准确理解定义", "把握关键要素"],
            visual_aids=["定义板书", "关键词标注"],
            expected_duration=5,
            interaction_prompt="定义中的关键词是什么？"
        ))
        
        # 步骤3：深入理解
        steps.append(ExplanationStep(
            step_number=3,
            step_title="深入理解",
            content=f"理解了定义后，我们来深入分析{concept}的性质和特点。首先...其次...",
            key_points=["理解性质", "掌握特点"],
            visual_aids=["性质图表", "对比表格"],
            expected_duration=4,
            interaction_prompt="你能总结出几个主要特点吗？"
        ))
        
        # 步骤4：应用举例
        steps.append(ExplanationStep(
            step_number=4,
            step_title="应用举例",
            content=f"下面我们通过例题来巩固对{concept}的理解。[例题讲解]",
            key_points=["学会应用", "解决问题"],
            visual_aids=["例题板书", "解题步骤"],
            expected_duration=5,
            interaction_prompt="请尝试解答这道例题。"
        ))
        
        return steps
    
    def _generate_concept_conclusion(self, concept: str) -> str:
        """生成概念总结"""
        return f"今天我们学习了{concept}的概念。要点回顾：\n1. 定义：[核心定义]\n2. 性质：[主要性质]\n3. 应用：[应用场景]\n\n希望大家在课后继续巩固，多做练习。"
    
    def _generate_common_misconceptions(self, concept: str) -> List[CommonMisconception]:
        """生成常见误区"""
        misconceptions = [
            CommonMisconception(
                misconception_id=f"misc_{uuid.uuid4().hex[:6]}",
                description=f"认为{concept}只适用于特定情况",
                why_wrong=f"这种理解过于局限，{concept}有更广泛的应用范围。",
                how_to_correct=f"通过更多例子理解{concept}的普遍性。"
            ),
            CommonMisconception(
                misconception_id=f"misc_{uuid.uuid4().hex[:6]}",
                description=f"混淆{concept}与相关概念",
                why_wrong=f"虽然相关，但两者有本质区别。",
                how_to_correct=f"通过对比学习，明确概念边界。"
            )
        ]
        return misconceptions
    
    def _generate_extension_questions(self, concept: str) -> List[str]:
        """生成拓展问题"""
        return [
            f"{concept}在实际生活中有哪些应用？",
            f"如果条件改变，{concept}会有什么变化？",
            f"{concept}与之前学过的知识有什么联系？",
            f"你能用{concept}解决一个实际问题吗？"
        ]
    
    def _generate_related_topics(self, concept: str, subject: str) -> List[str]:
        """生成相关主题"""
        if subject == "数学":
            return ["代数", "几何", "函数", "方程", "不等式"]
        elif subject == "物理":
            return ["力学", "电磁学", "光学", "热学"]
        elif subject == "化学":
            return ["无机化学", "有机化学", "物理化学", "分析化学"]
        else:
            return ["基础知识", "进阶内容", "综合应用"]
    
    def _analyze_question_type(self, question: str) -> str:
        """分析问题类型"""
        if any(word in question for word in ["为什么", "原因", "原理"]):
            return "原理性问题"
        elif any(word in question for word in ["怎么", "如何", "方法"]):
            return "方法性问题"
        elif any(word in question for word in ["是什么", "什么叫", "定义"]):
            return "概念性问题"
        elif any(word in question for word in ["例子", "举例"]):
            return "应用性问题"
        else:
            return "一般性问题"
    
    def _estimate_difficulty(self, question: str) -> str:
        """估计问题难度"""
        if any(word in question for word in ["深入", "本质", "原理", "证明"]):
            return "较难"
        elif any(word in question for word in ["为什么", "联系", "区别"]):
            return "中等"
        else:
            return "基础"
    
    def _generate_answer(self, question: str, course_info: CourseBasicInfo, question_type: str) -> str:
        """生成回答"""
        return f"关于您的问题'{question}'，这是一个{question_type}。\n\n[详细回答内容...]\n\n希望这个解释对您有帮助！"
    
    def _extract_related_points(self, question: str, subject: str) -> List[str]:
        """提取相关知识点"""
        return ["相关知识点1", "相关知识点2", "相关知识点3"]
    
    def _generate_extension(self, question: str, question_type: str) -> str:
        """生成拓展内容"""
        return f"基于您的{question_type}，您可以进一步思考：\n1. 拓展问题1\n2. 拓展问题2"
    
    def get_explanation_history(self) -> List[TeachingExplanation]:
        """获取讲解历史"""
        return self.explanation_history
    
    def clear_history(self) -> None:
        """清空历史"""
        self.explanation_history = []
