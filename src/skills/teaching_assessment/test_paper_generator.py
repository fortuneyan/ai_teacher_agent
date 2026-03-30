"""
试卷生成器

根据配置自动生成完整试卷
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
    TestPaper, TestPaperSection, TestPaperConfig,
    TestPaperType, TestPaperStatus,
    Exercise, QuestionType, DifficultyLevel,
    CourseBasicInfo, TeachingObjectives
)
from .exercise_generator import ExerciseGenerator


class TestPaperGenerator:
    """
    试卷生成器
    
    根据配置自动生成符合要求的完整试卷
    """
    
    # 默认题型配置
    DEFAULT_SECTIONS = {
        TestPaperType.UNIT_TEST: [
            ("选择题", QuestionType.SINGLE_CHOICE, 30),
            ("填空题", QuestionType.FILL_BLANK, 20),
            ("解答题", QuestionType.SHORT_ANSWER, 30),
            ("应用题", QuestionType.APPLICATION, 20)
        ],
        TestPaperType.QUIZ: [
            ("选择题", QuestionType.SINGLE_CHOICE, 40),
            ("填空题", QuestionType.FILL_BLANK, 30),
            ("简答题", QuestionType.SHORT_ANSWER, 30)
        ],
        TestPaperType.MIDTERM: [
            ("选择题", QuestionType.SINGLE_CHOICE, 24),
            ("填空题", QuestionType.FILL_BLANK, 16),
            ("计算题", QuestionType.CALCULATION, 30),
            ("解答题", QuestionType.SHORT_ANSWER, 20),
            ("综合题", QuestionType.COMPREHENSIVE, 10)
        ],
        TestPaperType.FINAL: [
            ("选择题", QuestionType.SINGLE_CHOICE, 20),
            ("填空题", QuestionType.FILL_BLANK, 15),
            ("判断题", QuestionType.TRUE_FALSE, 10),
            ("计算题", QuestionType.CALCULATION, 25),
            ("应用题", QuestionType.APPLICATION, 20),
            ("综合题", QuestionType.COMPREHENSIVE, 10)
        ]
    }
    
    def __init__(self):
        """初始化生成器"""
        self.exercise_generator = ExerciseGenerator()
        self.generated_papers: List[TestPaper] = []
    
    def generate_test_paper(
        self,
        paper_name: str,
        paper_type: TestPaperType,
        course_info: CourseBasicInfo,
        objectives: TeachingObjectives,
        config: Optional[TestPaperConfig] = None
    ) -> TestPaper:
        """
        生成试卷
        
        Args:
            paper_name: 试卷名称
            paper_type: 试卷类型
            course_info: 课程信息
            objectives: 教学目标
            config: 试卷配置（可选，使用默认配置）
            
        Returns:
            TestPaper: 生成的试卷
        """
        paper_id = f"paper_{uuid.uuid4().hex[:8]}"
        
        # 使用默认配置
        if config is None:
            config = TestPaperConfig(paper_type=paper_type)
        
        # 创建试卷
        paper = TestPaper(
            paper_id=paper_id,
            paper_name=paper_name,
            paper_type=paper_type,
            subject=course_info.subject,
            education_level=course_info.education_level,
            topic=course_info.topic,
            total_score=config.total_score,
            duration=config.duration,
            instructions=self._generate_instructions(paper_type, config.duration)
        )
        
        # 提取知识点
        key_points = self._extract_key_points(objectives)
        
        # 获取章节配置
        sections_config = self.DEFAULT_SECTIONS.get(paper_type, self.DEFAULT_SECTIONS[TestPaperType.UNIT_TEST])
        
        # 生成各章节
        for section_name, question_type, score_percentage in sections_config:
            section_score = config.total_score * score_percentage / 100
            section = self._generate_section(
                section_name=section_name,
                question_type=question_type,
                target_score=section_score,
                topic=course_info.topic,
                key_points=key_points,
                difficulty_distribution=config.difficulty_distribution,
                course_info=course_info,
                objectives=objectives
            )
            paper.add_section(section)
        
        self.generated_papers.append(paper)
        return paper
    
    def generate_practice_paper(
        self,
        course_info: CourseBasicInfo,
        objectives: TeachingObjectives,
        focus_key_points: List[str] = None,
        exercise_count: int = 20
    ) -> TestPaper:
        """
        生成专项练习卷
        
        Args:
            course_info: 课程信息
            objectives: 教学目标
            focus_key_points: 重点知识点（可选）
            exercise_count: 题目数量
            
        Returns:
            TestPaper: 练习卷
        """
        paper_id = f"practice_{uuid.uuid4().hex[:8]}"
        
        # 提取知识点
        key_points = focus_key_points or self._extract_key_points(objectives)
        
        paper = TestPaper(
            paper_id=paper_id,
            paper_name=f"{course_info.topic}专项练习",
            paper_type=TestPaperType.PRACTICE,
            subject=course_info.subject,
            education_level=course_info.education_level,
            topic=course_info.topic,
            total_score=100.0,
            duration=60,
            instructions="本练习针对重点知识进行专项训练，请认真作答。"
        )
        
        # 生成混合题型章节
        section = TestPaperSection(
            section_id=f"sec_{uuid.uuid4().hex[:6]}",
            section_name="综合练习",
            section_type="mixed",
            instructions="根据题目要求选择适当的方法作答。"
        )
        
        # 生成各种题型的题目
        question_types = [
            QuestionType.SINGLE_CHOICE,
            QuestionType.FILL_BLANK,
            QuestionType.SHORT_ANSWER,
            QuestionType.CALCULATION
        ]
        
        for i in range(exercise_count):
            question_type = question_types[i % len(question_types)]
            key_point = key_points[i % len(key_points)]
            difficulty = self._get_difficulty_by_index(i, exercise_count)
            
            exercise = self.exercise_generator.generate_exercise(
                topic=course_info.topic,
                question_type=question_type,
                difficulty=difficulty,
                key_points=[key_point],
                course_info=course_info,
                objectives=objectives
            )
            section.add_exercise(exercise)
        
        paper.add_section(section)
        self.generated_papers.append(paper)
        return paper
    
    def _generate_section(
        self,
        section_name: str,
        question_type: QuestionType,
        target_score: float,
        topic: str,
        key_points: List[str],
        difficulty_distribution: Dict[DifficultyLevel, int],
        course_info: CourseBasicInfo,
        objectives: TeachingObjectives
    ) -> TestPaperSection:
        """生成试卷章节"""
        section_id = f"sec_{uuid.uuid4().hex[:6]}"
        
        section = TestPaperSection(
            section_id=section_id,
            section_name=section_name,
            section_type=question_type.value,
            instructions=self._get_section_instructions(question_type)
        )
        
        # 计算题目数量
        avg_score = self._get_avg_score(question_type)
        question_count = max(1, int(target_score / avg_score))
        
        # 按难度分布生成题目
        current_score = 0.0
        question_index = 0
        
        for difficulty, percentage in difficulty_distribution.items():
            count = max(1, int(question_count * percentage / 100))
            
            for i in range(count):
                if current_score >= target_score:
                    break
                
                key_point = key_points[question_index % len(key_points)]
                
                exercise = self.exercise_generator.generate_exercise(
                    topic=topic,
                    question_type=question_type,
                    difficulty=difficulty,
                    key_points=[key_point],
                    course_info=course_info,
                    objectives=objectives
                )
                
                section.add_exercise(exercise)
                current_score += exercise.score
                question_index += 1
        
        return section
    
    def _generate_instructions(self, paper_type: TestPaperType, duration: int) -> str:
        """生成试卷说明"""
        instructions_map = {
            TestPaperType.UNIT_TEST: f"本试卷为单元测试卷，满分100分，考试时间{duration}分钟。请认真审题，规范作答。",
            TestPaperType.QUIZ: f"本测验用于检测课堂学习效果，考试时间{duration}分钟。请独立完成。",
            TestPaperType.MIDTERM: f"期中考试试卷，满分100分，考试时间{duration}分钟。请仔细审题，注意答题规范。",
            TestPaperType.FINAL: f"期末考试试卷，满分100分，考试时间{duration}分钟。请合理分配时间，认真检查。",
            TestPaperType.PRACTICE: f"专项练习卷，用于巩固所学知识，建议用时{duration}分钟。",
            TestPaperType.MOCK_EXAM: f"模拟考试试卷，满分100分，考试时间{duration}分钟。请模拟真实考试环境作答。",
            TestPaperType.ENTRANCE: f"入学测试卷，满分100分，考试时间{duration}分钟。请如实作答，以便了解学情。"
        }
        return instructions_map.get(paper_type, f"考试时间{duration}分钟，请认真作答。")
    
    def _get_section_instructions(self, question_type: QuestionType) -> str:
        """获取章节答题说明"""
        instructions_map = {
            QuestionType.SINGLE_CHOICE: "每小题只有一个正确答案，请将正确答案的序号填入括号内。",
            QuestionType.MULTIPLE_CHOICE: "每小题有两个或两个以上正确答案，请将正确答案的序号填入括号内。",
            QuestionType.FILL_BLANK: "请将正确答案填写在横线上。",
            QuestionType.TRUE_FALSE: "正确的打'√'，错误的打'×'。",
            QuestionType.SHORT_ANSWER: "请简要回答问题，注意条理清晰。",
            QuestionType.CALCULATION: "请写出必要的计算步骤，只写结果不得分。",
            QuestionType.PROOF: "请写出完整的证明过程，逻辑清晰，步骤完整。",
            QuestionType.APPLICATION: "请仔细阅读题目，建立数学模型并求解。",
            QuestionType.COMPREHENSIVE: "本题综合考查多个知识点，请灵活运用所学知识作答。"
        }
        return instructions_map.get(question_type, "请按题目要求作答。")
    
    def _get_avg_score(self, question_type: QuestionType) -> float:
        """获取题型平均分值"""
        avg_scores = {
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
        return avg_scores.get(question_type, 5.0)
    
    def _get_difficulty_by_index(self, index: int, total: int) -> DifficultyLevel:
        """根据索引获取难度（前30%容易，中间50%中等，后20%较难）"""
        if index < total * 0.3:
            return DifficultyLevel.EASY
        elif index < total * 0.8:
            return DifficultyLevel.MEDIUM
        else:
            return DifficultyLevel.HARD
    
    def _extract_key_points(self, objectives: TeachingObjectives) -> List[str]:
        """从教学目标中提取知识点"""
        key_points = []
        
        if hasattr(objectives, 'knowledge_objectives'):
            for obj in objectives.knowledge_objectives:
                key_points.append(obj.replace("理解", "").replace("掌握", "").replace("运用", ""))
        
        if hasattr(objectives, 'skill_objectives'):
            for obj in objectives.skill_objectives:
                key_points.append(obj.replace("能够", "").replace("学会", ""))
        
        return key_points if key_points else ["基础知识"]
    
    def get_paper_statistics(self, paper: TestPaper) -> Dict[str, Any]:
        """获取试卷统计信息"""
        stats = {
            "total_exercises": paper.get_exercise_count(),
            "total_score": paper.total_score,
            "duration": paper.duration,
            "section_count": len(paper.sections),
            "difficulty_distribution": {},
            "type_distribution": {}
        }
        
        # 统计难度分布
        for section in paper.sections:
            for exercise in section.exercises:
                difficulty = exercise.difficulty.value
                stats["difficulty_distribution"][difficulty] = stats["difficulty_distribution"].get(difficulty, 0) + 1
                
                q_type = exercise.question_type.value
                stats["type_distribution"][q_type] = stats["type_distribution"].get(q_type, 0) + 1
        
        return stats
    
    def export_paper(self, paper: TestPaper, format: str = "dict") -> Any:
        """
        导出试卷
        
        Args:
            paper: 试卷对象
            format: 导出格式 (dict/json/text)
            
        Returns:
            导出结果
        """
        if format == "dict":
            return paper.to_dict()
        elif format == "json":
            import json
            return json.dumps(paper.to_dict(), ensure_ascii=False, indent=2)
        elif format == "text":
            return self._export_as_text(paper)
        else:
            return paper.to_dict()
    
    def _export_as_text(self, paper: TestPaper) -> str:
        """导出为文本格式"""
        lines = []
        lines.append("=" * 60)
        lines.append(f"  {paper.paper_name}")
        lines.append("=" * 60)
        lines.append(f"\n考试时间：{paper.duration}分钟  满分：{paper.total_score}分")
        lines.append(f"\n{paper.instructions}\n")
        
        for section in paper.sections:
            lines.append(f"\n{section.section_name}（共{section.exercise_count}题，共{section.total_score}分）")
            lines.append(f"{section.instructions}\n")
            
            for i, exercise in enumerate(section.exercises, 1):
                lines.append(f"{i}. {exercise.question_text} ({exercise.score}分)")
                if exercise.answer_options:
                    for option in exercise.answer_options:
                        for key, value in option.items():
                            lines.append(f"   {key}. {value}")
                lines.append("")
        
        lines.append("\n" + "=" * 60)
        lines.append("  参考答案")
        lines.append("=" * 60)
        
        for section in paper.sections:
            lines.append(f"\n{section.section_name}")
            for i, exercise in enumerate(section.exercises, 1):
                lines.append(f"{i}. {exercise.correct_answer}")
        
        return "\n".join(lines)
    
    def get_generated_count(self) -> int:
        """获取已生成试卷数量"""
        return len(self.generated_papers)
