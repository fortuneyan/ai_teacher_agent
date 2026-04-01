"""
答案评估器 - 智能评估学生答案

功能：
1. 客观题自动评分
2. 主观题辅助评分
3. 详细反馈生成
4. 错题分析
"""

import uuid
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime


class EvaluationType(Enum):
    """评估类型"""
    OBJECTIVE = "客观题评估"
    SUBJECTIVE = "主观题评估"
    COMPREHENSIVE = "综合评估"


class ScoreLevel(Enum):
    """得分等级"""
    EXCELLENT = "优秀"      # 90-100
    GOOD = "良好"         # 80-89
    PASS = "及格"         # 60-79
    FAIL = "不及格"       # 0-59


@dataclass
class EvaluationResult:
    """评估结果"""
    evaluation_id: str
    question_id: str
    question_type: str
    
    # 评分
    score: float
    max_score: float
    score_level: str
    
    # 详细评估
    is_correct: bool
    correct_answer: str
    student_answer: str
    
    # 反馈
    feedback: str  # 总体反馈
    suggestions: List[str] = field(default_factory=list)  # 改进建议
    key_points_review: List[str] = field(default_factory=list)  # 需要复习的关键点
    
    # 元数据
    evaluated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AnswerEvaluator:
    """
    答案评估器
    
    使用示例：
        evaluator = AnswerEvaluator()
        
        # 评估选择题
        result = evaluator.evaluate_objective(
            question_id="EX-001",
            question_type="单选题",
            student_answer="A",
            correct_answer="A",
            max_score=5
        )
        
        # 评估主观题
        result = evaluator.evaluate_subjective(
            question_id="EX-002",
            question_type="简答题",
            student_answer="学生的答案...",
            reference_answer="参考答案...",
            max_score=10
        )
        
        # 综合评估
        results = evaluator.evaluate_batch(questions_and_answers)
    """
    
    def __init__(self, llm_service=None):
        self.llm_service = llm_service
        self.evaluation_count = 0
    
    # ==================== 客观题评估 ====================
    
    def evaluate_objective(
        self,
        question_id: str,
        question_type: str,
        student_answer: str,
        correct_answer: str,
        max_score: float = 10
    ) -> EvaluationResult:
        """
        评估客观题
        
        Args:
            question_id: 题目ID
            question_type: 题型
            student_answer: 学生答案
            correct_answer: 正确答案
            max_score: 满分
            
        Returns:
            EvaluationResult对象
        """
        # 标准化答案
        student = self._normalize_answer(student_answer)
        correct = self._normalize_answer(correct_answer)
        
        # 判断是否正确
        is_correct = student == correct
        
        # 计算得分
        if is_correct:
            score = max_score
        else:
            # 部分得分的题型
            if question_type in ["多选题", "填空题"]:
                # 计算部分得分
                score = self._calculate_partial_score(student, correct, max_score)
            else:
                score = 0
        
        # 获取得分等级
        score_level = self._get_score_level(score, max_score)
        
        # 生成反馈
        if is_correct:
            feedback = "回答正确！"
        else:
            feedback = f"回答错误，正确答案是 {correct_answer}"
        
        # 建议
        suggestions = []
        if not is_correct:
            suggestions.append("建议复习相关知识点")
            suggestions.append("注意审题，避免粗心错误")
        
        self.evaluation_count += 1
        
        return EvaluationResult(
            evaluation_id=f"EV-{uuid.uuid4().hex[:8].upper()}",
            question_id=question_id,
            question_type=question_type,
            score=score,
            max_score=max_score,
            score_level=score_level.value,
            is_correct=is_correct,
            correct_answer=correct_answer,
            student_answer=student_answer,
            feedback=feedback,
            suggestions=suggestions
        )
    
    def _normalize_answer(self, answer: str) -> str:
        """标准化答案"""
        # 去除空格和特殊字符
        answer = answer.strip().upper()
        answer = re.sub(r'[\s\.\,\;]', '', answer)
        return answer
    
    def _calculate_partial_score(
        self,
        student: str,
        correct: str,
        max_score: float
    ) -> float:
        """计算部分得分"""
        if not student:
            return 0
        
        correct_chars = set(correct)
        student_chars = set(student)
        
        # 计算重合度
        if correct_chars == student_chars:
            return max_score
        elif student_chars.issubset(correct_chars):
            # 学生答案包含在正确答案中
            ratio = len(student_chars) / len(correct_chars)
            return max_score * ratio * 0.8
        else:
            # 有重合但不完全匹配
            common = student_chars & correct_chars
            ratio = len(common) / len(correct_chars)
            return max_score * ratio * 0.5
    
    # ==================== 主观题评估 ====================
    
    def evaluate_subjective(
        self,
        question_id: str,
        question_type: str,
        student_answer: str,
        reference_answer: str,
        max_score: float = 10,
        scoring_rubric: Optional[Dict[str, Any]] = None
    ) -> EvaluationResult:
        """
        评估主观题
        
        Args:
            question_id: 题目ID
            question_type: 题型
            student_answer: 学生答案
            reference_answer:参考答案
            max_score: 满分
            scoring_rubric: 评分标准
            
        Returns:
            EvaluationResult对象
        """
        # 使用评分标准或默认评分
        if scoring_rubric is None:
            scoring_rubric = self._default_rubric(question_type)
        
        # 计算得分
        score = self._calculate_subjective_score(
            student_answer, reference_answer, max_score, scoring_rubric
        )
        
        # 获取得分等级
        score_level = self._get_score_level(score, max_score)
        
        # 判断是否正确（60%以上为正确）
        is_correct = (score / max_score) >= 0.6
        
        # 生成详细反馈
        feedback = self._generate_feedback(score, max_score, question_type)
        
        # 建议
        suggestions = self._generate_suggestions(score, max_score, question_type)
        
        # 需要复习的关键点
        key_points = self._extract_key_points(reference_answer)
        
        self.evaluation_count += 1
        
        return EvaluationResult(
            evaluation_id=f"EV-{uuid.uuid4().hex[:8].upper()}",
            question_id=question_id,
            question_type=question_type,
            score=score,
            max_score=max_score,
            score_level=score_level.value,
            is_correct=is_correct,
            correct_answer=reference_answer,
            student_answer=student_answer,
            feedback=feedback,
            suggestions=suggestions,
            key_points_review=key_points
        )
    
    def _default_rubric(self, question_type: str) -> Dict[str, Any]:
        """默认评分标准"""
        rubrics = {
            "简答题": {
                "completeness": 0.4,  # 完整性
                "accuracy": 0.4,      # 准确性
                "clarity": 0.2        # 清晰度
            },
            "计算题": {
                "method": 0.3,        # 方法
                "calculation": 0.5,    # 计算
                "result": 0.2          # 结果
            },
            "应用题": {
                "understanding": 0.3, # 理解
                "analysis": 0.3,      # 分析
                "solution": 0.3,       # 解答
                "expression": 0.1      # 表达
            },
            "探究题": {
                "hypothesis": 0.2,     # 假设
                "design": 0.3,         # 设计
                "conclusion": 0.3,     # 结论
                "expression": 0.2      # 表达
            }
        }
        return rubrics.get(question_type, {
            "content": 0.5,
            "expression": 0.5
        })
    
    def _calculate_subjective_score(
        self,
        student: str,
        reference: str,
        max_score: float,
        rubric: Dict[str, float]
    ) -> float:
        """计算主观题得分"""
        if not student or not reference:
            return 0
        
        # 计算内容匹配度
        student_words = set(self._extract_keywords(student))
        reference_words = set(self._extract_keywords(reference))
        
        if not reference_words:
            return max_score
        
        # 关键词匹配度
        match_ratio = len(student_words & reference_words) / len(reference_words)
        
        # 应用评分标准
        score = max_score * match_ratio
        
        return min(score, max_score)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单实现：去除标点和停用词
        stop_words = {"的", "了", "在", "是", "我", "有", "和", "就", "不", "人"}
        words = re.findall(r'[\u4e00-\u9fa5a-zA-Z0-9]+', text)
        return [w for w in words if w not in stop_words and len(w) > 1]
    
    def _generate_feedback(
        self,
        score: float,
        max_score: float,
        question_type: str
    ) -> str:
        """生成反馈"""
        ratio = score / max_score
        
        if ratio >= 0.9:
            return f"回答非常出色！要点全面，表达清晰。"
        elif ratio >= 0.7:
            return f"回答较好，基本掌握了{question_type}的要点。"
        elif ratio >= 0.5:
            return f"回答一般，部分要点遗漏或表述不准确。"
        elif ratio >= 0.3:
            return f"回答不完整，需要加强相关知识点的学习。"
        else:
            return f"回答偏离主题，建议重新复习相关知识。"
    
    def _generate_suggestions(
        self,
        score: float,
        max_score: float,
        question_type: str
    ) -> List[str]:
        """生成建议"""
        ratio = score / max_score
        suggestions = []
        
        if ratio < 0.7:
            suggestions.append(f"建议加强对{question_type}的基础训练")
        
        if ratio < 0.5:
            suggestions.append("注意分析题目的要求，明确答题方向")
            suggestions.append("可以参考正确答案，分析自己的不足")
        
        if ratio >= 0.5:
            suggestions.append("可以尝试更高难度的题目")
        
        return suggestions[:3]
    
    def _extract_key_points(self, reference: str) -> List[str]:
        """提取关键点"""
        # 简单实现：提取每段的第一个要点
        points = []
        for line in reference.split("\n"):
            line = line.strip()
            if line and not line.startswith("#"):
                # 去除序号
                line = re.sub(r'^\d+[\.\、]\s*', '', line)
                if line:
                    points.append(line[:50])  # 截取前50字符
        return points[:5]
    
    # ==================== 辅助方法 ====================
    
    def _get_score_level(self, score: float, max_score: float) -> ScoreLevel:
        """获取得分等级"""
        ratio = score / max_score if max_score > 0 else 0
        
        if ratio >= 0.9:
            return ScoreLevel.EXCELLENT
        elif ratio >= 0.8:
            return ScoreLevel.GOOD
        elif ratio >= 0.6:
            return ScoreLevel.PASS
        else:
            return ScoreLevel.FAIL
    
    def evaluate_batch(
        self,
        items: List[Dict[str, Any]]
    ) -> List[EvaluationResult]:
        """
        批量评估
        
        Args:
            items: 评估项列表，每项包含：
                - question_id
                - question_type
                - student_answer
                - correct_answer (客观题) / reference_answer (主观题)
                - max_score
                
        Returns:
            评估结果列表
        """
        results = []
        
        for item in items:
            question_type = item.get("question_type", "")
            
            if question_type in ["单选题", "多选题", "判断题", "填空题"]:
                result = self.evaluate_objective(
                    question_id=item["question_id"],
                    question_type=question_type,
                    student_answer=item["student_answer"],
                    correct_answer=item["correct_answer"],
                    max_score=item.get("max_score", 10)
                )
            else:
                result = self.evaluate_subjective(
                    question_id=item["question_id"],
                    question_type=question_type,
                    student_answer=item["student_answer"],
                    reference_answer=item.get("reference_answer", ""),
                    max_score=item.get("max_score", 10),
                    scoring_rubric=item.get("scoring_rubric")
                )
            
            results.append(result)
        
        return results
    
    def generate_summary(
        self,
        results: List[EvaluationResult]
    ) -> Dict[str, Any]:
        """
        生成评估汇总
        
        Args:
            results: 评估结果列表
            
        Returns:
            汇总报告
        """
        total_score = sum(r.score for r in results)
        total_max = sum(r.max_score for r in results)
        correct_count = sum(1 for r in results if r.is_correct)
        
        return {
            "total_questions": len(results),
            "correct_count": correct_count,
            "accuracy_rate": correct_count / len(results) if results else 0,
            "total_score": total_score,
            "total_max_score": total_max,
            "average_score": total_score / len(results) if results else 0,
            "score_level": self._get_score_level(
                total_score, total_max
            ).value if total_max > 0 else "N/A",
            "question_results": [r.to_dict() for r in results]
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取评估统计"""
        return {
            "total_evaluated": self.evaluation_count,
            "supported_types": [
                "单选题", "多选题", "判断题", "填空题",
                "简答题", "计算题", "应用题", "探究题"
            ]
        }
