"""
习题生成器

根据教学内容自动生成各类习题
"""
import uuid
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

# 添加src到路径
src_path = Path(__file__).parent.parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from models import (
    Exercise, ExerciseSet, QuestionType,
    DifficultyLevel, ExerciseStatus,
    CourseBasicInfo, TeachingObjectives
)
from mocks import MockLLMService


class ExerciseGenerator:
    """
    习题生成器
    
    根据教学目标和知识点自动生成各类习题
    """
    
    def __init__(self):
        """初始化生成器"""
        self.llm_service = MockLLMService()
        self.generated_exercises: List[Exercise] = []
    
    def generate_exercise(
        self,
        topic: str,
        question_type: QuestionType,
        difficulty: DifficultyLevel,
        key_points: List[str],
        course_info: Optional[CourseBasicInfo] = None,
        objectives: Optional[TeachingObjectives] = None
    ) -> Exercise:
        """
        生成单个习题
        
        Args:
            topic: 题目主题
            question_type: 题目类型
            difficulty: 难度等级
            key_points: 考查知识点
            course_info: 课程信息（可选）
            objectives: 教学目标（可选）
            
        Returns:
            Exercise: 生成的习题对象
        """
        exercise_id = f"ex_{uuid.uuid4().hex[:8]}"
        
        # 根据题型生成题目
        if question_type == QuestionType.SINGLE_CHOICE:
            exercise = self._generate_single_choice(topic, difficulty, key_points)
        elif question_type == QuestionType.MULTIPLE_CHOICE:
            exercise = self._generate_multiple_choice(topic, difficulty, key_points)
        elif question_type == QuestionType.FILL_BLANK:
            exercise = self._generate_fill_blank(topic, difficulty, key_points)
        elif question_type == QuestionType.TRUE_FALSE:
            exercise = self._generate_true_false(topic, difficulty, key_points)
        elif question_type == QuestionType.SHORT_ANSWER:
            exercise = self._generate_short_answer(topic, difficulty, key_points)
        elif question_type == QuestionType.CALCULATION:
            exercise = self._generate_calculation(topic, difficulty, key_points)
        elif question_type == QuestionType.APPLICATION:
            exercise = self._generate_application(topic, difficulty, key_points)
        else:
            exercise = self._generate_comprehensive(topic, difficulty, key_points)
        
        # 设置基本信息
        exercise.exercise_id = exercise_id
        exercise.subject = course_info.subject if course_info else None
        exercise.education_level = course_info.education_level if course_info else None
        exercise.topic = topic
        exercise.difficulty = difficulty
        exercise.key_points = key_points
        
        # 设置分值和用时
        exercise.score = self._get_score_by_type(question_type, difficulty)
        exercise.estimated_time = self._get_time_by_difficulty(difficulty)
        
        self.generated_exercises.append(exercise)
        return exercise
    
    def generate_exercise_set(
        self,
        topic: str,
        course_info: CourseBasicInfo,
        objectives: TeachingObjectives,
        question_types: List[QuestionType] = None,
        difficulty_distribution: Dict[DifficultyLevel, int] = None,
        total_count: int = 10
    ) -> ExerciseSet:
        """
        生成习题集
        
        Args:
            topic: 主题
            course_info: 课程信息
            objectives: 教学目标
            question_types: 题型列表（默认多种题型）
            difficulty_distribution: 难度分布（默认中等为主）
            total_count: 题目总数
            
        Returns:
            ExerciseSet: 习题集
        """
        set_id = f"set_{uuid.uuid4().hex[:8]}"
        
        # 默认题型分布
        if question_types is None:
            question_types = [
                QuestionType.SINGLE_CHOICE,
                QuestionType.FILL_BLANK,
                QuestionType.SHORT_ANSWER,
                QuestionType.CALCULATION
            ]
        
        # 默认难度分布
        if difficulty_distribution is None:
            difficulty_distribution = {
                DifficultyLevel.EASY: 30,
                DifficultyLevel.MEDIUM: 50,
                DifficultyLevel.HARD: 20
            }
        
        # 提取知识点
        key_points = self._extract_key_points(objectives)
        
        # 创建习题集
        exercise_set = ExerciseSet(
            set_id=set_id,
            set_name=f"{topic}练习题",
            description=f"{course_info.education_level}{course_info.subject} - {topic}专项练习",
            subject=course_info.subject,
            education_level=course_info.education_level,
            topic=topic
        )
        
        # 按难度分布生成题目
        type_index = 0
        for difficulty, percentage in difficulty_distribution.items():
            count = int(total_count * percentage / 100)
            for i in range(count):
                question_type = question_types[type_index % len(question_types)]
                key_point = key_points[i % len(key_points)] if key_points else topic
                
                exercise = self.generate_exercise(
                    topic=topic,
                    question_type=question_type,
                    difficulty=difficulty,
                    key_points=[key_point],
                    course_info=course_info,
                    objectives=objectives
                )
                exercise_set.add_exercise(exercise)
                type_index += 1
        
        return exercise_set
    
    def _generate_single_choice(self, topic: str, difficulty: DifficultyLevel, key_points: List[str]) -> Exercise:
        """生成单选题"""
        key_point = key_points[0] if key_points else topic
        
        # 根据难度设置干扰项复杂度
        if difficulty == DifficultyLevel.EASY:
            question_text = f"下列关于{topic}的说法，正确的是（ ）"
            options = [
                {"A": f"{topic}是初中数学的基础概念"},
                {"B": f"{topic}在实际生活中没有应用"},
                {"C": f"{topic}与{key_point}无关"},
                {"D": f"{topic}只能用于特定场景"}
            ]
            correct = "A"
            explanation = f"{topic}确实是数学学习的基础概念，选项B、C、D的说法都是错误的。"
        elif difficulty == DifficultyLevel.MEDIUM:
            question_text = f"关于{topic}的{key_point}，以下说法正确的是（ ）"
            options = [
                {"A": f"{key_point}的定义包含三个要素"},
                {"B": f"{key_point}只适用于特定条件"},
                {"C": f"{key_point}与{topic}没有直接关系"},
                {"D": f"{key_point}不能用于解决实际问题"}
            ]
            correct = "A"
            explanation = f"{key_point}的定义确实包含三个核心要素，这是理解{topic}的关键。"
        else:
            question_text = f"在{topic}中，关于{key_point}的深入理解，正确的是（ ）"
            options = [
                {"A": f"{key_point}在任何情况下都成立"},
                {"B": f"{key_point}的逆命题也成立"},
                {"C": f"{key_point}需要满足特定条件才能应用"},
                {"D": f"{key_point}与其他概念没有联系"}
            ]
            correct = "C"
            explanation = f"{key_point}的应用确实需要满足特定条件，这是深入理解{topic}的重要方面。"
        
        return Exercise(
            exercise_id="",
            question_text=question_text,
            question_type=QuestionType.SINGLE_CHOICE,
            correct_answer=correct,
            answer_options=options,
            explanation=explanation,
            solution_steps=[
                f"理解{topic}的基本概念",
                f"分析{key_point}的具体含义",
                "逐一判断各选项的正确性",
                "选择最符合题意的答案"
            ]
        )
    
    def _generate_multiple_choice(self, topic: str, difficulty: DifficultyLevel, key_points: List[str]) -> Exercise:
        """生成多选题"""
        key_point = key_points[0] if key_points else topic
        
        question_text = f"关于{topic}的{key_point}，以下说法正确的有（ ）"
        options = [
            {"A": f"{key_point}是{topic}的核心内容"},
            {"B": f"{key_point}在实际中有广泛应用"},
            {"C": f"{key_point}的理解需要基础知识"},
            {"D": f"{key_point}与其他知识没有关联"}
        ]
        correct = "ABC"
        explanation = f"选项A、B、C都是关于{key_point}的正确描述，D选项错误，因为{key_point}与其他知识有密切联系。"
        
        return Exercise(
            exercise_id="",
            question_text=question_text,
            question_type=QuestionType.MULTIPLE_CHOICE,
            correct_answer=correct,
            answer_options=options,
            explanation=explanation,
            solution_steps=[
                f"回顾{topic}中关于{key_point}的内容",
                "逐一分析每个选项",
                "判断各选项的正确性",
                "选出所有正确的选项"
            ]
        )
    
    def _generate_fill_blank(self, topic: str, difficulty: DifficultyLevel, key_points: List[str]) -> Exercise:
        """生成填空题"""
        key_point = key_points[0] if key_points else topic
        
        if difficulty == DifficultyLevel.EASY:
            question_text = f"{topic}是研究_____的数学分支。"
            correct = "数量关系和空间形式"
            explanation = f"{topic}主要研究数量关系和空间形式，这是数学的基本研究对象。"
        elif difficulty == DifficultyLevel.MEDIUM:
            question_text = f"在{topic}中，{key_point}的定义包含_____、_____、_____三个要素。"
            correct = "定义域；对应关系；值域"
            explanation = f"{key_point}的完整定义需要包含定义域、对应关系和值域三个要素。"
        else:
            question_text = f"应用{topic}解决实际问题时，首先需要_____，然后_____，最后_____。"
            correct = "建立数学模型；求解模型；验证结果"
            explanation = f"应用{topic}解决实际问题的一般步骤是：建立数学模型、求解模型、验证结果。"
        
        return Exercise(
            exercise_id="",
            question_text=question_text,
            question_type=QuestionType.FILL_BLANK,
            correct_answer=correct,
            explanation=explanation,
            solution_steps=[
                f"回忆{topic}的基本概念",
                f"理解{key_point}的具体内容",
                "根据题意填写正确答案"
            ]
        )
    
    def _generate_true_false(self, topic: str, difficulty: DifficultyLevel, key_points: List[str]) -> Exercise:
        """生成判断题"""
        key_point = key_points[0] if key_points else topic
        
        question_text = f"{topic}中的{key_point}只适用于特定场景，不能推广到一般情况。（ ）"
        correct = "错误"
        explanation = f"这个说法是错误的。{key_point}在{topic}中具有普遍适用性，可以推广到多种场景。"
        
        return Exercise(
            exercise_id="",
            question_text=question_text,
            question_type=QuestionType.TRUE_FALSE,
            correct_answer=correct,
            explanation=explanation,
            solution_steps=[
                f"理解{key_point}的定义和适用范围",
                "判断题目说法的正确性"
            ]
        )
    
    def _generate_short_answer(self, topic: str, difficulty: DifficultyLevel, key_points: List[str]) -> Exercise:
        """生成简答题"""
        key_point = key_points[0] if key_points else topic
        
        question_text = f"简述{topic}中{key_point}的定义，并举例说明其在实际生活中的应用。"
        correct = f"{key_point}的定义：[具体定义]。应用示例：[生活实例]。"
        explanation = f"简答题需要准确阐述{key_point}的定义，并给出恰当的实际应用例子。"
        
        return Exercise(
            exercise_id="",
            question_text=question_text,
            question_type=QuestionType.SHORT_ANSWER,
            correct_answer=correct,
            explanation=explanation,
            solution_steps=[
                f"准确回忆{key_point}的定义",
                "用自己的语言组织答案",
                "举出恰当的实际例子",
                "检查答案的完整性"
            ]
        )
    
    def _generate_calculation(self, topic: str, difficulty: DifficultyLevel, key_points: List[str]) -> Exercise:
        """生成计算题"""
        key_point = key_points[0] if key_points else topic
        
        if difficulty == DifficultyLevel.EASY:
            question_text = f"已知[具体条件]，求{topic}相关的[目标量]。"
            correct = "[计算结果]"
            explanation = f"通过直接应用{topic}的基本公式即可求解。"
        elif difficulty == DifficultyLevel.MEDIUM:
            question_text = f"在{topic}中，已知{key_point}的[条件]，求[目标量]。（需要两步计算）"
            correct = "[计算结果]"
            explanation = f"需要先利用{key_point}的性质，再结合{topic}的相关公式求解。"
        else:
            question_text = f"综合应用{topic}和{key_point}的知识，解决以下问题：[复杂情境]。"
            correct = "[计算结果]"
            explanation = f"本题需要综合运用{topic}和{key_point}的知识，分多步求解。"
        
        return Exercise(
            exercise_id="",
            question_text=question_text,
            question_type=QuestionType.CALCULATION,
            correct_answer=correct,
            explanation=explanation,
            solution_steps=[
                "分析题目条件",
                f"确定需要使用的{topic}知识",
                "列出相关公式",
                "逐步计算求解",
                "检验结果合理性"
            ]
        )
    
    def _generate_application(self, topic: str, difficulty: DifficultyLevel, key_points: List[str]) -> Exercise:
        """生成应用题"""
        key_point = key_points[0] if key_points else topic
        
        scenarios = [
            f"某工厂生产{topic}相关产品",
            f"学校组织{topic}相关活动",
            f"商场进行{topic}相关促销",
            f"城市规划中的{topic}应用"
        ]
        scenario = scenarios[hash(topic) % len(scenarios)]
        
        question_text = f"{scenario}，[具体情境描述]。请运用{topic}的知识解决以下问题：[问题描述]。"
        correct = "[完整解答过程]"
        explanation = f"本题考查{topic}在实际问题中的应用，关键是将实际问题转化为数学问题。"
        
        return Exercise(
            exercise_id="",
            question_text=question_text,
            question_type=QuestionType.APPLICATION,
            correct_answer=correct,
            explanation=explanation,
            solution_steps=[
                "理解实际问题的背景",
                "提取关键数学信息",
                f"建立{topic}相关的数学模型",
                "求解数学问题",
                "将结果解释回实际问题"
            ]
        )
    
    def _generate_comprehensive(self, topic: str, difficulty: DifficultyLevel, key_points: List[str]) -> Exercise:
        """生成综合题"""
        key_points_str = "、".join(key_points[:3]) if key_points else topic
        
        question_text = f"综合题：结合{topic}中的{key_points_str}等知识，解决以下问题：[复杂综合问题描述]。"
        correct = "[完整解答]"
        explanation = f"本题综合考查{topic}的多个知识点，需要灵活运用所学知识。"
        
        return Exercise(
            exercise_id="",
            question_text=question_text,
            question_type=QuestionType.COMPREHENSIVE,
            correct_answer=correct,
            explanation=explanation,
            solution_steps=[
                "通读题目，理解整体要求",
                "分析涉及的知识点",
                "确定解题思路",
                "分步求解",
                "综合整理答案"
            ]
        )
    
    def _get_score_by_type(self, question_type: QuestionType, difficulty: DifficultyLevel) -> float:
        """根据题型和难度获取分值"""
        base_scores = {
            QuestionType.SINGLE_CHOICE: 3.0,
            QuestionType.MULTIPLE_CHOICE: 4.0,
            QuestionType.FILL_BLANK: 3.0,
            QuestionType.TRUE_FALSE: 2.0,
            QuestionType.SHORT_ANSWER: 5.0,
            QuestionType.CALCULATION: 8.0,
            QuestionType.PROOF: 10.0,
            QuestionType.APPLICATION: 10.0,
            QuestionType.COMPREHENSIVE: 12.0
        }
        
        difficulty_multiplier = {
            DifficultyLevel.EASY: 0.8,
            DifficultyLevel.MEDIUM: 1.0,
            DifficultyLevel.HARD: 1.2,
            DifficultyLevel.CHALLENGING: 1.5
        }
        
        return base_scores.get(question_type, 5.0) * difficulty_multiplier.get(difficulty, 1.0)
    
    def _get_time_by_difficulty(self, difficulty: DifficultyLevel) -> int:
        """根据难度获取预计用时"""
        time_map = {
            DifficultyLevel.EASY: 3,
            DifficultyLevel.MEDIUM: 5,
            DifficultyLevel.HARD: 8,
            DifficultyLevel.CHALLENGING: 12
        }
        return time_map.get(difficulty, 5)
    
    def _extract_key_points(self, objectives: TeachingObjectives) -> List[str]:
        """从教学目标中提取知识点"""
        key_points = []
        
        # 从知识目标中提取
        if hasattr(objectives, 'knowledge_objectives'):
            for obj in objectives.knowledge_objectives:
                # 简单提取关键词
                key_points.append(obj.replace("理解", "").replace("掌握", "").replace("运用", ""))
        
        # 从技能目标中提取
        if hasattr(objectives, 'skill_objectives'):
            for obj in objectives.skill_objectives:
                key_points.append(obj.replace("能够", "").replace("学会", ""))
        
        return key_points if key_points else ["基础知识"]
    
    def get_generated_count(self) -> int:
        """获取已生成习题数量"""
        return len(self.generated_exercises)
    
    def clear_history(self) -> None:
        """清空生成历史"""
        self.generated_exercises = []
