"""
试卷生成器 - 自动生成标准化试卷

功能：
1. 选择题试卷
2. 综合试卷
3. 单元测试卷
4. 期中/期末试卷
"""

import uuid
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime

from .exercise_generator import ExerciseGenerator, Question, Difficulty


class PaperType(Enum):
    """试卷类型"""
    CHOICE_ONLY = "选择题试卷"
    COMPREHENSIVE = "综合试卷"
    UNIT_TEST = "单元测试"
    MIDTERM = "期中考试"
    FINAL = "期末考试"


class PaperConfig:
    """试卷配置"""
    
    def __init__(
        self,
        paper_type: PaperType = PaperType.COMPREHENSIVE,
        total_score: int = 100,
        duration: int = 90,
        include_choice: bool = True,
        include_fill_blank: bool = True,
        include_calculation: bool = True,
        include_application: bool = True,
        include_inquiry: bool = False
    ):
        self.paper_type = paper_type
        self.total_score = total_score
        self.duration = duration
        self.include_choice = include_choice
        self.include_fill_blank = include_fill_blank
        self.include_calculation = include_calculation
        self.include_application = include_application
        self.include_inquiry = include_inquiry


@dataclass
class TestPaper:
    """试卷对象"""
    paper_id: str
    title: str
    paper_type: str
    subject: str
    grade: str
    
    # 试卷结构
    sections: List[Dict[str, Any]]  # 各部分题目
    total_score: int
    duration: int  # 分钟
    
    # 元数据
    created_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # 题库引用
    questions: List[Dict[str, Any]] = field(default_factory=list)
    
    @property
    def total_questions(self) -> int:
        """总题数"""
        return len(self.questions)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class TestPaperGenerator:
    """
    试卷生成器
    
    使用示例：
        generator = TestPaperGenerator()
        
        config = PaperConfig(
            paper_type=PaperType.COMPREHENSIVE,
            total_score=100,
            duration=90
        )
        
        paper = generator.generate_paper(
            subject="高中数学",
            grade="高一",
            topic="函数的概念",
            config=config
        )
    """
    
    def __init__(self, llm_service=None):
        self.llm_service = llm_service
        self.exercise_generator = ExerciseGenerator(llm_service)
    
    def generate_paper(
        self,
        subject: str,
        grade: str,
        topic: str,
        knowledge_points: Optional[List[str]] = None,
        config: Optional[PaperConfig] = None
    ) -> TestPaper:
        """
        生成试卷
        
        Args:
            subject: 科目
            grade: 年级
            topic: 主题
            knowledge_points: 知识点列表
            config: 试卷配置
            
        Returns:
            TestPaper对象
        """
        if config is None:
            config = PaperConfig()
        
        if knowledge_points is None:
            knowledge_points = [topic]
        
        questions = []
        sections = []
        current_score = 0
        question_num = 1
        
        # 选择题部分
        if config.include_choice:
            choice_section = self._generate_choice_section(
                subject, grade, topic, knowledge_points, question_num
            )
            sections.append(choice_section)
            questions.extend(choice_section["questions"])
            current_score += choice_section["score"]
            question_num += len(choice_section["questions"])
        
        # 填空题部分
        if config.include_fill_blank:
            fill_section = self._generate_fill_blank_section(
                subject, grade, topic, knowledge_points, question_num
            )
            sections.append(fill_section)
            questions.extend(fill_section["questions"])
            current_score += fill_section["score"]
            question_num += len(fill_section["questions"])
        
        # 计算题部分
        if config.include_calculation:
            calc_section = self._generate_calculation_section(
                subject, grade, topic, knowledge_points, question_num
            )
            sections.append(calc_section)
            questions.extend(calc_section["questions"])
            current_score += calc_section["score"]
            question_num += len(calc_section["questions"])
        
        # 应用题部分
        if config.include_application:
            app_section = self._generate_application_section(
                subject, grade, topic, knowledge_points, question_num
            )
            sections.append(app_section)
            questions.extend(app_section["questions"])
            current_score += app_section["score"]
            question_num += len(app_section["questions"])
        
        # 探究题部分
        if config.include_inquiry:
            inquiry_section = self._generate_inquiry_section(
                subject, grade, topic, knowledge_points, question_num
            )
            sections.append(inquiry_section)
            questions.extend(inquiry_section["questions"])
            current_score += inquiry_section["score"]
        
        # 构建试卷标题
        title = self._generate_title(subject, grade, topic, config.paper_type)
        
        paper = TestPaper(
            paper_id=f"TP-{uuid.uuid4().hex[:8].upper()}",
            title=title,
            paper_type=config.paper_type.value,
            subject=subject,
            grade=grade,
            sections=sections,
            total_score=config.total_score,
            duration=config.duration,
            created_at=datetime.now().isoformat(),
            questions=[q.to_dict() if isinstance(q, Question) else q for q in questions]
        )
        
        return paper
    
    def _generate_choice_section(
        self,
        subject: str,
        grade: str,
        topic: str,
        knowledge_points: List[str],
        start_num: int
    ) -> Dict[str, Any]:
        """生成选择题部分"""
        questions = []
        
        for i, kp in enumerate(knowledge_points):
            q = self.exercise_generator.generate_single_choice(
                topic=topic,
                knowledge_point=kp,
                difficulty=Difficulty.EASY if i % 2 == 0 else Difficulty.MEDIUM
            )
            questions.append(q.to_dict())
        
        return {
            "section_name": "一、选择题",
            "instruction": f"本大题共{len(questions)}小题，每小题5分，共{len(questions) * 5}分",
            "questions": questions,
            "score": len(questions) * 5,
            "type": "选择题"
        }
    
    def _generate_fill_blank_section(
        self,
        subject: str,
        grade: str,
        topic: str,
        knowledge_points: List[str],
        start_num: int
    ) -> Dict[str, Any]:
        """生成填空题部分"""
        questions = []
        
        for kp in knowledge_points[:3]:
            q = self.exercise_generator.generate_fill_blank(
                topic=topic,
                knowledge_point=kp,
                difficulty=Difficulty.MEDIUM
            )
            questions.append(q.to_dict())
        
        return {
            "section_name": "二、填空题",
            "instruction": f"本大题共{len(questions)}小题，每小题5分，共{len(questions) * 5}分",
            "questions": questions,
            "score": len(questions) * 5,
            "type": "填空题"
        }
    
    def _generate_calculation_section(
        self,
        subject: str,
        grade: str,
        topic: str,
        knowledge_points: List[str],
        start_num: int
    ) -> Dict[str, Any]:
        """生成计算题部分"""
        questions = []
        
        for kp in knowledge_points[:2]:
            q = self.exercise_generator.generate_calculation(
                topic=topic,
                knowledge_point=kp,
                difficulty=Difficulty.MEDIUM
            )
            questions.append(q.to_dict())
        
        return {
            "section_name": "三、计算题",
            "instruction": f"本大题共{len(questions)}小题，共{len(questions) * 15}分",
            "questions": questions,
            "score": len(questions) * 15,
            "type": "计算题"
        }
    
    def _generate_application_section(
        self,
        subject: str,
        grade: str,
        topic: str,
        knowledge_points: List[str],
        start_num: int
    ) -> Dict[str, Any]:
        """生成应用题部分"""
        questions = []
        
        q = self.exercise_generator.generate_application(
            topic=topic,
            knowledge_point=knowledge_points[0] if knowledge_points else topic,
            difficulty=Difficulty.HARD
        )
        questions.append(q.to_dict())
        
        return {
            "section_name": "四、应用题",
            "instruction": f"本大题共{len(questions)}小题，共{len(questions) * 15}分",
            "questions": questions,
            "score": len(questions) * 15,
            "type": "应用题"
        }
    
    def _generate_inquiry_section(
        self,
        subject: str,
        grade: str,
        topic: str,
        knowledge_points: List[str],
        start_num: int
    ) -> Dict[str, Any]:
        """生成探究题部分"""
        questions = []
        
        q = self.exercise_generator.generate_inquiry(
            topic=topic,
            knowledge_point=knowledge_points[0] if knowledge_points else topic,
            difficulty=Difficulty.HARD
        )
        questions.append(q.to_dict())
        
        return {
            "section_name": "五、探究题",
            "instruction": f"本大题共{len(questions)}小题，共{len(questions) * 10}分",
            "questions": questions,
            "score": len(questions) * 10,
            "type": "探究题"
        }
    
    def _generate_title(
        self,
        subject: str,
        grade: str,
        topic: str,
        paper_type: PaperType
    ) -> str:
        """生成试卷标题"""
        type_names = {
            PaperType.CHOICE_ONLY: "选择题专项练习",
            PaperType.COMPREHENSIVE: "综合测试",
            PaperType.UNIT_TEST: "单元测试",
            PaperType.MIDTERM: "期中考试",
            PaperType.FINAL: "期末考试"
        }
        
        return f"{grade}{subject}《{topic}》{type_names.get(paper_type, '测试')}"
    
    def generate_answer_key(self, paper: TestPaper) -> Dict[str, Any]:
        """生成答案"""
        answers = {}
        
        for section in paper.sections:
            section_name = section["section_name"]
            section_answers = []
            
            for q in section["questions"]:
                if isinstance(q, Question):
                    section_answers.append({
                        "question_id": q.question_id,
                        "answer": q.answer,
                        "analysis": q.analysis
                    })
                else:
                    section_answers.append({
                        "question_id": q.get("question_id", ""),
                        "answer": q.get("answer", ""),
                        "analysis": q.get("analysis", "")
                    })
            
            answers[section_name] = section_answers
        
        return {
            "paper_id": paper.paper_id,
            "title": paper.title,
            "answers": answers,
            "total_score": paper.total_score
        }
