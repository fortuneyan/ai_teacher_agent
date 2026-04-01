"""
习题生成器 - 支持多种题型

功能：
1. 选择题生成
2. 填空题生成
3. 判断题生成
4. 简答题生成
5. 计算题生成
6. 应用题生成
7. 探究题生成
8. 实践题生成
9. 开放题生成
"""

import uuid
import random
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum


class QuestionType(Enum):
    """题型枚举"""
    SINGLE_CHOICE = "单选题"
    MULTIPLE_CHOICE = "多选题"
    FILL_BLANK = "填空题"
    TRUE_FALSE = "判断题"
    SHORT_ANSWER = "简答题"
    CALCULATION = "计算题"
    APPLICATION = "应用题"
    INQUIRY = "探究题"
    PRACTICAL = "实践题"
    OPEN_ENDED = "开放题"


class Difficulty(Enum):
    """难度等级"""
    EASY = "基础"
    MEDIUM = "中等"
    HARD = "困难"


@dataclass
class Question:
    """习题对象"""
    question_id: str
    question_type: str
    difficulty: str
    content: str
    answer: str
    options: Optional[List[str]] = None  # 选择题选项
    analysis: str = ""  # 解析
    score: int = 10  # 分值
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


class ExerciseGenerator:
    """
    习题生成器
    
    使用示例：
        generator = ExerciseGenerator()
        
        # 生成单选题
        question = generator.generate_single_choice(
            topic="函数",
            knowledge_point="函数概念",
            difficulty=Difficulty.MEDIUM
        )
        
        # 批量生成
        questions = generator.generate_batch(
            topic="函数",
            num_each_type=5
        )
    """
    
    def __init__(self, llm_service=None):
        self.llm_service = llm_service
        self.generated_count = 0
    
    # ==================== 选择题生成 ====================
    
    def generate_single_choice(
        self,
        topic: str,
        knowledge_point: str,
        difficulty: Difficulty = Difficulty.MEDIUM
    ) -> Question:
        """
        生成单选题
        
        Args:
            topic: 教学主题
            knowledge_point: 知识点
            difficulty: 难度等级
            
        Returns:
            Question对象
        """
        # 生成题干
        content = f"关于{knowledge_point}的说法，正确的是："
        
        # 生成选项（简化版本）
        options = [
            f"A. {knowledge_point}的定义是...",
            f"B. {knowledge_point}具有以下性质...",
            f"C. {knowledge_point}的应用范围...",
            f"D. {knowledge_point}的图形特征是..."
        ]
        
        # 正确答案（随机）
        correct_idx = random.randint(0, 3)
        answer = chr(65 + correct_idx)  # A, B, C, D
        
        self.generated_count += 1
        
        return Question(
            question_id=f"EX-{uuid.uuid4().hex[:8].upper()}",
            question_type=QuestionType.SINGLE_CHOICE.value,
            difficulty=difficulty.value,
            content=content,
            options=options,
            answer=answer,
            analysis=f"根据{knowledge_point}的定义和性质，可以判断正确答案为{answer}。",
            score=self._get_score(difficulty),
            tags=[topic, knowledge_point]
        )
    
    def generate_multiple_choice(
        self,
        topic: str,
        knowledge_point: str,
        difficulty: Difficulty = Difficulty.MEDIUM
    ) -> Question:
        """生成多选题"""
        content = f"下列关于{knowledge_point}的说法，正确的有："
        
        options = [
            f"A. {knowledge_point}的定义包含几个要点",
            f"B. {knowledge_point}的主要性质",
            f"C. {knowledge_point}的应用场景",
            f"D. {knowledge_point}的图形特征"
        ]
        
        # 多选题答案可能是多个
        answer = "AB"
        
        self.generated_count += 1
        
        return Question(
            question_id=f"EX-{uuid.uuid4().hex[:8].upper()}",
            question_type=QuestionType.MULTIPLE_CHOICE.value,
            difficulty=difficulty.value,
            content=content,
            options=options,
            answer=answer,
            analysis="需要逐项分析每个选项的正确性。",
            score=self._get_score(difficulty) * 2,
            tags=[topic, knowledge_point]
        )
    
    # ==================== 填空题生成 ====================
    
    def generate_fill_blank(
        self,
        topic: str,
        knowledge_point: str,
        difficulty: Difficulty = Difficulty.MEDIUM
    ) -> Question:
        """生成填空题"""
        content = f"1. {knowledge_point}的定义为：______"
        
        answer = f"{knowledge_point}是指..."
        
        self.generated_count += 1
        
        return Question(
            question_id=f"EX-{uuid.uuid4().hex[:8].upper()}",
            question_type=QuestionType.FILL_BLANK.value,
            difficulty=difficulty.value,
            content=content,
            answer=answer,
            analysis=f"本题考察对{knowledge_point}定义的掌握程度。",
            score=self._get_score(difficulty),
            tags=[topic, knowledge_point]
        )
    
    # ==================== 判断题生成 ====================
    
    def generate_true_false(
        self,
        topic: str,
        knowledge_point: str,
        difficulty: Difficulty = Difficulty.EASY
    ) -> Question:
        """生成判断题"""
        statements = [
            f"{knowledge_point}是本节的重点内容。",
            f"所有{knowledge_point}都具有相同的性质。",
            f"{knowledge_point}在实际生活中有广泛应用。"
        ]
        
        content = f"判断下列说法的正误（正确打O，错误打X）：\n" + "\n".join(
            f"{i+1}. {s}" for i, s in enumerate(statements)
        )
        
        answer = "O,X,O"
        
        self.generated_count += 1
        
        return Question(
            question_id=f"EX-{uuid.uuid4().hex[:8].upper()}",
            question_type=QuestionType.TRUE_FALSE.value,
            difficulty=difficulty.value,
            content=content,
            answer=answer,
            analysis="理解概念的关键在于把握本质特征。",
            score=self._get_score(difficulty),
            tags=[topic, knowledge_point]
        )
    
    # ==================== 简答题生成 ====================
    
    def generate_short_answer(
        self,
        topic: str,
        knowledge_point: str,
        difficulty: Difficulty = Difficulty.MEDIUM
    ) -> Question:
        """生成简答题"""
        content = f"请简要回答：{knowledge_point}的主要特点有哪些？"
        
        answer = f"""1. 特点一：...
2. 特点二：...
3. 特点三：..."""
        
        self.generated_count += 1
        
        return Question(
            question_id=f"EX-{uuid.uuid4().hex[:8].upper()}",
            question_type=QuestionType.SHORT_ANSWER.value,
            difficulty=difficulty.value,
            content=content,
            answer=answer,
            analysis=f"简答题需要条理清晰，要点完整。",
            score=self._get_score(difficulty) * 2,
            tags=[topic, knowledge_point]
        )
    
    # ==================== 计算题生成 ====================
    
    def generate_calculation(
        self,
        topic: str,
        knowledge_point: str,
        difficulty: Difficulty = Difficulty.MEDIUM
    ) -> Question:
        """生成计算题"""
        content = f"""已知：...
求：{knowledge_point}的计算结果

解："""
        
        answer = """解题步骤：
1. 分析已知条件
2. 选择合适的方法
3. 进行计算
4. 验证结果"""
        
        self.generated_count += 1
        
        return Question(
            question_id=f"EX-{uuid.uuid4().hex[:8].upper()}",
            question_type=QuestionType.CALCULATION.value,
            difficulty=difficulty.value,
            content=content,
            answer=answer,
            analysis="计算题需要注意解题步骤的完整性。",
            score=self._get_score(difficulty) * 3,
            tags=[topic, knowledge_point]
        )
    
    # ==================== 应用题生成 ====================
    
    def generate_application(
        self,
        topic: str,
        knowledge_point: str,
        difficulty: Difficulty = Difficulty.MEDIUM
    ) -> Question:
        """生成应用题"""
        content = f"""某商场销售一种商品，成本价为100元，售价为150元。
请运用{knowledge_point}的知识解决以下问题：
1. 该商品的利润是多少？
2. 利润率是多少？
3. 如果要获得20%的利润率，售价应定为多少？"""
        
        answer = """1. 利润 = 售价 - 成本 = 150 - 100 = 50元
2. 利润率 = 利润 / 成本 = 50 / 100 = 50%
3. 售价 = 成本 × (1 + 利润率) = 100 × 1.2 = 120元"""
        
        self.generated_count += 1
        
        return Question(
            question_id=f"EX-{uuid.uuid4().hex[:8].upper()}",
            question_type=QuestionType.APPLICATION.value,
            difficulty=difficulty.value,
            content=content,
            answer=answer,
            analysis="应用题需要将理论知识与实际问题相结合。",
            score=self._get_score(difficulty) * 3,
            tags=[topic, knowledge_point, "实际应用"]
        )
    
    # ==================== 探究题生成 ====================
    
    def generate_inquiry(
        self,
        topic: str,
        knowledge_point: str,
        difficulty: Difficulty = Difficulty.HARD
    ) -> Question:
        """生成探究题"""
        content = f"""{knowledge_point}在不同的条件下会有什么不同的表现？
请设计一个实验方案来探究这个问题。

提示：
1. 明确实验目的
2. 设计实验步骤
3. 预期实验结果
4. 得出结论"""
        
        answer = """实验设计方案：
1. 实验目的：探究...的条件对...的影响
2. 实验变量：自变量、因变量、控制变量
3. 实验步骤：...
4. 预期结果：...
5. 结论：..."""
        
        self.generated_count += 1
        
        return Question(
            question_id=f"EX-{uuid.uuid4().hex[:8].upper()}",
            question_type=QuestionType.INQUIRY.value,
            difficulty=difficulty.value,
            content=content,
            answer=answer,
            analysis="探究题培养学生的科学探究能力和创新思维。",
            score=self._get_score(difficulty) * 4,
            tags=[topic, knowledge_point, "探究能力"]
        )
    
    # ==================== 实践题生成 ====================
    
    def generate_practical(
        self,
        topic: str,
        knowledge_point: str,
        difficulty: Difficulty = Difficulty.MEDIUM
    ) -> Question:
        """生成实践题"""
        content = f"""请运用{knowledge_point}的知识，完成以下任务：

任务背景：...
任务要求：
1. 实地调查或测量...
2. 收集数据并整理分析
3. 撰写实践报告
4. 提出改进建议"""
        
        answer = """实践报告框架：
1. 实践目的
2. 实践过程
3. 数据分析
4. 结论与建议"""
        
        self.generated_count += 1
        
        return Question(
            question_id=f"EX-{uuid.uuid4().hex[:8].upper()}",
            question_type=QuestionType.PRACTICAL.value,
            difficulty=difficulty.value,
            content=content,
            answer=answer,
            analysis="实践题强调知识在实际中的应用。",
            score=self._get_score(difficulty) * 3,
            tags=[topic, knowledge_point, "实践能力"]
        )
    
    # ==================== 开放题生成 ====================
    
    def generate_open_ended(
        self,
        topic: str,
        knowledge_point: str,
        difficulty: Difficulty = Difficulty.HARD
    ) -> Question:
        """生成开放题"""
        content = f"""{knowledge_point}在现实生活中有哪些应用？
请举例说明，并分析其优缺点。

要求：
1. 至少举出3个实例
2. 分析每个实例的特点
3. 总结{knowledge_point}的一般应用规律"""
        
        answer = """开放性答案示例：
实例1：...（分析优缺点）
实例2：...（分析优缺点）
实例3：...（分析优缺点）
规律总结：..."""
        
        self.generated_count += 1
        
        return Question(
            question_id=f"EX-{uuid.uuid4().hex[:8].upper()}",
            question_type=QuestionType.OPEN_ENDED.value,
            difficulty=difficulty.value,
            content=content,
            answer=answer,
            analysis="开放题没有标准答案，鼓励学生独立思考和创新。",
            score=self._get_score(difficulty) * 4,
            tags=[topic, knowledge_point, "开放思维"]
        )
    
    # ==================== 批量生成 ====================
    
    def generate_batch(
        self,
        topic: str,
        num_each_type: int = 2,
        knowledge_point: Optional[str] = None
    ) -> List[Question]:
        """
        批量生成习题
        
        Args:
            topic: 教学主题
            num_each_type: 每种题型的数量
            knowledge_point: 具体知识点
            
        Returns:
            习题列表
        """
        if knowledge_point is None:
            knowledge_point = topic
        
        questions = []
        generators = [
            (self.generate_single_choice, Difficulty.MEDIUM),
            (self.generate_multiple_choice, Difficulty.MEDIUM),
            (self.generate_fill_blank, Difficulty.EASY),
            (self.generate_true_false, Difficulty.EASY),
            (self.generate_short_answer, Difficulty.MEDIUM),
            (self.generate_calculation, Difficulty.MEDIUM),
            (self.generate_application, Difficulty.HARD),
            (self.generate_inquiry, Difficulty.HARD),
            (self.generate_practical, Difficulty.MEDIUM),
            (self.generate_open_ended, Difficulty.HARD),
        ]
        
        for gen_func, difficulty in generators:
            for _ in range(num_each_type):
                q = gen_func(topic, knowledge_point, difficulty)
                questions.append(q)
        
        return questions
    
    def generate_by_difficulty(
        self,
        topic: str,
        knowledge_point: str,
        easy: int = 3,
        medium: int = 5,
        hard: int = 2
    ) -> Dict[str, List[Question]]:
        """
        按难度生成习题
        
        Args:
            topic: 教学主题
            knowledge_point: 知识点
            easy: 基础题数量
            medium: 中等题数量
            hard: 困难题数量
            
        Returns:
            按难度分类的习题字典
        """
        result = {
            "easy": [],
            "medium": [],
            "hard": []
        }
        
        # 基础题
        for _ in range(easy):
            result["easy"].append(self.generate_true_false(topic, knowledge_point, Difficulty.EASY))
            result["easy"].append(self.generate_fill_blank(topic, knowledge_point, Difficulty.EASY))
        
        # 中等题
        for _ in range(medium):
            result["medium"].append(self.generate_single_choice(topic, knowledge_point, Difficulty.MEDIUM))
            result["medium"].append(self.generate_short_answer(topic, knowledge_point, Difficulty.MEDIUM))
        
        # 困难题
        for _ in range(hard):
            result["hard"].append(self.generate_application(topic, knowledge_point, Difficulty.HARD))
            result["hard"].append(self.generate_inquiry(topic, knowledge_point, Difficulty.HARD))
        
        return result
    
    # ==================== 辅助方法 ====================
    
    def _get_score(self, difficulty: Difficulty) -> int:
        """根据难度获取分值"""
        scores = {
            Difficulty.EASY: 5,
            Difficulty.MEDIUM: 10,
            Difficulty.HARD: 15
        }
        return scores.get(difficulty, 10)
    
    def export_to_dict(self, questions: List[Question]) -> List[Dict[str, Any]]:
        """导出习题为字典列表"""
        return [asdict(q) for q in questions]
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取生成统计"""
        return {
            "total_generated": self.generated_count,
            "question_types": [qt.value for qt in QuestionType]
        }
