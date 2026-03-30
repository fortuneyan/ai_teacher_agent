"""
答题评估器

评估学生答题情况，提供详细分析和建议
"""
import uuid
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from difflib import SequenceMatcher

# 添加src到路径
src_path = Path(__file__).parent.parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from models import (
    Exercise, QuestionType, StudentAnswer, TestResult, TestPaper,
    TeachingExplanation, ExplanationType
)
from .teaching_explainer import TeachingExplainer


class AnswerEvaluator:
    """
    答题评估器
    
    评估学生答题情况，生成详细分析报告
    """
    
    def __init__(self):
        """初始化评估器"""
        self.explainer = TeachingExplainer()
        self.evaluation_history: List[TestResult] = []
    
    def evaluate_answer(
        self,
        exercise: Exercise,
        student_answer: str,
        student_id: str = "student_001"
    ) -> StudentAnswer:
        """
        评估单个答案
        
        Args:
            exercise: 习题对象
            student_answer: 学生答案
            student_id: 学生ID
            
        Returns:
            StudentAnswer: 评估结果
        """
        answer_id = f"ans_{uuid.uuid4().hex[:8]}"
        
        # 判断答案正确性
        is_correct, score = self._check_answer(exercise, student_answer)
        
        answer_record = StudentAnswer(
            answer_id=answer_id,
            exercise_id=exercise.exercise_id,
            student_id=student_id,
            answer_text=student_answer,
            is_correct=is_correct,
            score=score,
            submitted_at=datetime.now()
        )
        
        return answer_record
    
    def evaluate_test_paper(
        self,
        paper: TestPaper,
        answers: Dict[str, str],  # {exercise_id: student_answer}
        student_id: str = "student_001",
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> TestResult:
        """
        评估整张试卷
        
        Args:
            paper: 试卷对象
            answers: 学生答案字典
            student_id: 学生ID
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            TestResult: 测试结果
        """
        result_id = f"result_{uuid.uuid4().hex[:8]}"
        
        result = TestResult(
            result_id=result_id,
            paper_id=paper.paper_id,
            student_id=student_id,
            start_time=start_time,
            end_time=end_time,
            max_score=paper.total_score
        )
        
        # 评估每道题
        for section in paper.sections:
            for exercise in section.exercises:
                student_answer = answers.get(exercise.exercise_id, "")
                answer_record = self.evaluate_answer(exercise, student_answer, student_id)
                result.answers.append(answer_record)
        
        # 计算总分
        result.calculate_score()
        
        # 计算用时
        if start_time and end_time:
            result.total_time = int((end_time - start_time).total_seconds())
        
        # 分析知识点掌握情况
        result.knowledge_mastery = self._analyze_knowledge_mastery(paper, result.answers)
        
        # 分析能力维度
        result.ability_analysis = self._analyze_ability_dimensions(paper, result.answers)
        
        self.evaluation_history.append(result)
        return result
    
    def generate_analysis_report(self, result: TestResult, paper: TestPaper) -> Dict[str, Any]:
        """
        生成详细分析报告
        
        Args:
            result: 测试结果
            paper: 试卷对象
            
        Returns:
            Dict: 分析报告
        """
        report = {
            "basic_info": {
                "student_id": result.student_id,
                "paper_id": result.paper_id,
                "total_score": result.total_score,
                "max_score": result.max_score,
                "accuracy_rate": round(result.total_score / result.max_score * 100, 2) if result.max_score > 0 else 0,
                "correct_count": result.correct_count,
                "wrong_count": result.wrong_count,
                "total_time": result.total_time,
                "average_time_per_question": round(result.total_time / len(result.answers), 2) if result.answers else 0
            },
            "score_level": self._get_score_level(result.total_score, result.max_score),
            "knowledge_analysis": self._generate_knowledge_analysis(result.knowledge_mastery),
            "ability_analysis": self._generate_ability_analysis(result.ability_analysis),
            "wrong_questions": self._analyze_wrong_questions(result, paper),
            "suggestions": self._generate_suggestions(result, paper),
            "improvement_plan": self._generate_improvement_plan(result.knowledge_mastery)
        }
        
        return report
    
    def get_wrong_question_explanations(
        self,
        result: TestResult,
        paper: TestPaper
    ) -> List[TeachingExplanation]:
        """
        获取错题讲解
        
        Args:
            result: 测试结果
            paper: 试卷对象
            
        Returns:
            List[TeachingExplanation]: 错题讲解列表
        """
        explanations = []
        
        # 获取所有习题
        exercise_map = {}
        for section in paper.sections:
            for exercise in section.exercises:
                exercise_map[exercise.exercise_id] = exercise
        
        # 为每道错题生成讲解
        for answer in result.answers:
            if not answer.is_correct:
                exercise = exercise_map.get(answer.exercise_id)
                if exercise:
                    explanation = self.explainer.explain_exercise(
                        exercise=exercise,
                        course_info=None,  # 可以从paper中获取
                        student_wrong_answer=answer.answer_text
                    )
                    explanations.append(explanation)
        
        return explanations
    
    def compare_with_class(
        self,
        result: TestResult,
        class_results: List[TestResult]
    ) -> Dict[str, Any]:
        """
        与班级平均水平对比
        
        Args:
            result: 单个学生结果
            class_results: 全班结果列表
            
        Returns:
            Dict: 对比分析
        """
        if not class_results:
            return {"error": "没有班级数据"}
        
        # 计算班级平均分
        class_avg_score = sum(r.total_score for r in class_results) / len(class_results)
        class_avg_accuracy = sum(r.correct_count for r in class_results) / sum(len(r.answers) for r in class_results) * 100
        
        # 计算排名
        sorted_scores = sorted([r.total_score for r in class_results], reverse=True)
        rank = sorted_scores.index(result.total_score) + 1 if result.total_score in sorted_scores else len(sorted_scores)
        
        # 计算百分位
        percentile = (1 - rank / len(class_results)) * 100
        
        return {
            "student_score": result.total_score,
            "class_average": round(class_avg_score, 2),
            "difference": round(result.total_score - class_avg_score, 2),
            "rank": rank,
            "total_students": len(class_results),
            "percentile": round(percentile, 2),
            "comparison": "above_average" if result.total_score > class_avg_score else "below_average",
            "class_avg_accuracy": round(class_avg_accuracy, 2)
        }
    
    def _check_answer(self, exercise: Exercise, student_answer: str) -> Tuple[bool, float]:
        """检查答案正确性并评分"""
        if not student_answer or not student_answer.strip():
            return False, 0.0
        
        correct_answer = exercise.correct_answer.strip()
        student_answer = student_answer.strip()
        
        # 根据题型判断
        if exercise.question_type == QuestionType.SINGLE_CHOICE:
            is_correct = student_answer.upper() == correct_answer.upper()
            score = exercise.score if is_correct else 0.0
            
        elif exercise.question_type == QuestionType.MULTIPLE_CHOICE:
            # 多选题：全对得满分，部分对得一半，有错得0分
            student_set = set(student_answer.upper())
            correct_set = set(correct_answer.upper())
            
            if student_set == correct_set:
                is_correct = True
                score = exercise.score
            elif student_set.issubset(correct_set) and len(student_set) > 0:
                is_correct = False
                score = exercise.score * 0.5
            else:
                is_correct = False
                score = 0.0
                
        elif exercise.question_type == QuestionType.TRUE_FALSE:
            # 判断题
            student_bool = self._parse_boolean(student_answer)
            correct_bool = self._parse_boolean(correct_answer)
            is_correct = student_bool == correct_bool
            score = exercise.score if is_correct else 0.0
            
        elif exercise.question_type in [QuestionType.FILL_BLANK, QuestionType.SHORT_ANSWER]:
            # 填空题和简答题：使用相似度匹配
            similarity = SequenceMatcher(None, student_answer, correct_answer).ratio()
            is_correct = similarity > 0.8
            score = exercise.score * similarity if similarity > 0.5 else 0.0
            
        else:
            # 计算题、应用题、综合题：关键词匹配
            keywords = self._extract_keywords(correct_answer)
            matched_keywords = sum(1 for kw in keywords if kw in student_answer)
            accuracy = matched_keywords / len(keywords) if keywords else 0.0
            
            is_correct = accuracy > 0.7
            score = exercise.score * accuracy
        
        return is_correct, round(score, 2)
    
    def _parse_boolean(self, answer: str) -> Optional[bool]:
        """解析布尔值"""
        true_values = ["正确", "对", "√", "是", "true", "yes", "1", "t"]
        false_values = ["错误", "错", "×", "否", "false", "no", "0", "f", "x"]
        
        answer_lower = answer.lower().strip()
        if any(tv in answer_lower for tv in true_values):
            return True
        elif any(fv in answer_lower for fv in false_values):
            return False
        return None
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单实现：提取长度大于2的词
        words = text.replace("。", "").replace("，", "").replace("、", "").split()
        return [w for w in words if len(w) >= 2]
    
    def _analyze_knowledge_mastery(
        self,
        paper: TestPaper,
        answers: List[StudentAnswer]
    ) -> Dict[str, float]:
        """分析知识点掌握情况"""
        knowledge_scores = {}
        knowledge_counts = {}
        
        # 获取所有习题
        exercise_map = {}
        for section in paper.sections:
            for exercise in section.exercises:
                exercise_map[exercise.exercise_id] = exercise
        
        # 统计各知识点的得分情况
        for answer in answers:
            exercise = exercise_map.get(answer.exercise_id)
            if exercise:
                for key_point in exercise.key_points:
                    if key_point not in knowledge_scores:
                        knowledge_scores[key_point] = 0.0
                        knowledge_counts[key_point] = 0
                    knowledge_scores[key_point] += answer.score
                    knowledge_counts[key_point] += exercise.score
        
        # 计算掌握度（百分比）
        mastery = {}
        for key_point in knowledge_scores:
            if knowledge_counts[key_point] > 0:
                mastery[key_point] = round(knowledge_scores[key_point] / knowledge_counts[key_point] * 100, 2)
            else:
                mastery[key_point] = 0.0
        
        return mastery
    
    def _analyze_ability_dimensions(
        self,
        paper: TestPaper,
        answers: List[StudentAnswer]
    ) -> Dict[str, float]:
        """分析能力维度"""
        # 按题型映射到能力维度
        ability_map = {
            "single_choice": "识记理解",
            "multiple_choice": "综合分析",
            "fill_blank": "识记理解",
            "true_false": "识记理解",
            "short_answer": "表达应用",
            "calculation": "运算求解",
            "proof": "推理论证",
            "application": "实际应用",
            "comprehensive": "综合分析"
        }
        
        ability_scores = {}
        ability_counts = {}
        
        exercise_map = {}
        for section in paper.sections:
            for exercise in section.exercises:
                exercise_map[exercise.exercise_id] = exercise
        
        for answer in answers:
            exercise = exercise_map.get(answer.exercise_id)
            if exercise:
                ability = ability_map.get(exercise.question_type.value, "综合能力")
                if ability not in ability_scores:
                    ability_scores[ability] = 0.0
                    ability_counts[ability] = 0
                ability_scores[ability] += answer.score
                ability_counts[ability] += exercise.score
        
        # 计算能力得分率
        analysis = {}
        for ability in ability_scores:
            if ability_counts[ability] > 0:
                analysis[ability] = round(ability_scores[ability] / ability_counts[ability] * 100, 2)
            else:
                analysis[ability] = 0.0
        
        return analysis
    
    def _get_score_level(self, score: float, max_score: float) -> str:
        """获取成绩等级"""
        if max_score == 0:
            return "无数据"
        
        percentage = score / max_score * 100
        if percentage >= 90:
            return "优秀"
        elif percentage >= 80:
            return "良好"
        elif percentage >= 70:
            return "中等"
        elif percentage >= 60:
            return "及格"
        else:
            return "待提高"
    
    def _generate_knowledge_analysis(self, knowledge_mastery: Dict[str, float]) -> List[Dict[str, Any]]:
        """生成知识点分析"""
        analysis = []
        for knowledge, mastery in knowledge_mastery.items():
            level = "掌握" if mastery >= 80 else "基本掌握" if mastery >= 60 else "需加强"
            analysis.append({
                "knowledge": knowledge,
                "mastery": mastery,
                "level": level,
                "suggestion": self._get_knowledge_suggestion(mastery)
            })
        
        # 按掌握度排序
        analysis.sort(key=lambda x: x["mastery"])
        return analysis
    
    def _generate_ability_analysis(self, ability_analysis: Dict[str, float]) -> List[Dict[str, Any]]:
        """生成能力维度分析"""
        analysis = []
        for ability, score in ability_analysis.items():
            level = "强" if score >= 80 else "中等" if score >= 60 else "需提升"
            analysis.append({
                "ability": ability,
                "score": score,
                "level": level
            })
        
        # 按得分排序
        analysis.sort(key=lambda x: x["score"], reverse=True)
        return analysis
    
    def _analyze_wrong_questions(self, result: TestResult, paper: TestPaper) -> List[Dict[str, Any]]:
        """分析错题"""
        wrong_questions = []
        
        exercise_map = {}
        for section in paper.sections:
            for exercise in section.exercises:
                exercise_map[exercise.exercise_id] = exercise
        
        for answer in result.answers:
            if not answer.is_correct:
                exercise = exercise_map.get(answer.exercise_id)
                if exercise:
                    wrong_questions.append({
                        "exercise_id": exercise.exercise_id,
                        "question_type": exercise.question_type.value,
                        "difficulty": exercise.difficulty.value,
                        "key_points": exercise.key_points,
                        "student_answer": answer.answer_text,
                        "correct_answer": exercise.correct_answer,
                        "score": answer.score,
                        "full_score": exercise.score,
                        "explanation": exercise.explanation
                    })
        
        return wrong_questions
    
    def _generate_suggestions(self, result: TestResult, paper: TestPaper) -> List[str]:
        """生成学习建议"""
        suggestions = []
        
        accuracy = result.total_score / result.max_score if result.max_score > 0 else 0
        
        if accuracy >= 0.9:
            suggestions.append("整体表现优秀，建议挑战更高难度的题目。")
        elif accuracy >= 0.8:
            suggestions.append("整体表现良好，注意细节可以更进一步。")
        elif accuracy >= 0.6:
            suggestions.append("基础知识掌握尚可，需要加强重点知识的学习。")
        else:
            suggestions.append("需要系统复习基础知识，建议重新学习相关章节。")
        
        # 根据错题类型给出建议
        wrong_types = set()
        exercise_map = {}
        for section in paper.sections:
            for exercise in section.exercises:
                exercise_map[exercise.exercise_id] = exercise
        
        for answer in result.answers:
            if not answer.is_correct:
                exercise = exercise_map.get(answer.exercise_id)
                if exercise:
                    wrong_types.add(exercise.question_type.value)
        
        if "calculation" in wrong_types:
            suggestions.append("计算题失分较多，建议加强运算能力的训练。")
        if "application" in wrong_types:
            suggestions.append("应用题理解有困难，建议多练习将实际问题转化为数学问题。")
        if "comprehensive" in wrong_types:
            suggestions.append("综合题得分不理想，需要加强知识整合能力。")
        
        return suggestions
    
    def _generate_improvement_plan(self, knowledge_mastery: Dict[str, float]) -> List[Dict[str, Any]]:
        """生成提升计划"""
        plan = []
        
        # 找出掌握度低于60%的知识点
        weak_points = [(k, v) for k, v in knowledge_mastery.items() if v < 60]
        weak_points.sort(key=lambda x: x[1])  # 按掌握度从低到高排序
        
        for i, (knowledge, mastery) in enumerate(weak_points[:5], 1):  # 最多取前5个
            plan.append({
                "priority": i,
                "knowledge": knowledge,
                "current_mastery": mastery,
                "target_mastery": 80,
                "suggested_actions": [
                    f"重新学习{knowledge}的基础概念",
                    f"完成{knowledge}相关的基础练习题",
                    f"总结{knowledge}的常见题型和解题方法"
                ],
                "estimated_time": "2-3小时"
            })
        
        return plan
    
    def _get_knowledge_suggestion(self, mastery: float) -> str:
        """根据掌握度给出建议"""
        if mastery >= 90:
            return "掌握得很好，可以尝试更高难度的题目"
        elif mastery >= 80:
            return "掌握良好，注意细节即可"
        elif mastery >= 60:
            return "基本掌握，建议多做练习巩固"
        elif mastery >= 40:
            return "掌握不够扎实，需要重点复习"
        else:
            return "掌握较差，建议重新学习相关内容"
    
    def get_evaluation_history(self) -> List[TestResult]:
        """获取评估历史"""
        return self.evaluation_history
    
    def clear_history(self) -> None:
        """清空历史"""
        self.evaluation_history = []
