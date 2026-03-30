"""
AI教师Agent - 测试/讲解模块CLI

提供交互式的出题、测试、讲解功能
"""
import sys
import uuid
sys.path.insert(0, 'src')

from models import (
    CourseBasicInfo, TeachingObjectives,
    QuestionType, DifficultyLevel, TestPaperType
)
from skills.teaching_assessment import (
    ExerciseGenerator, TestPaperGenerator,
    TeachingExplainer, AnswerEvaluator
)


class AssessmentCLI:
    """测试/讲解模块CLI"""
    
    def __init__(self):
        self.exercise_gen = ExerciseGenerator()
        self.paper_gen = TestPaperGenerator()
        self.explainer = TeachingExplainer()
        self.evaluator = AnswerEvaluator()
        
        self.current_course = None
        self.current_objectives = None
        self.current_paper = None
        self.current_result = None
    
    def print_header(self, title):
        """打印标题"""
        print("\n" + "=" * 50)
        print(f"  {title}")
        print("=" * 50)
    
    def print_menu(self):
        """打印主菜单"""
        self.print_header("AI教师Agent - 测试/讲解模块")
        print("\n  [1] 设置课程信息")
        print("  [2] 生成单个习题")
        print("  [3] 生成习题集")
        print("  [4] 生成试卷")
        print("  [5] 概念讲解")
        print("  [6] 习题讲解")
        print("  [7] 模拟答题")
        print("  [8] 查看分析报告")
        print("  [9] 智能问答")
        print("  [0] 返回上级菜单")
        print("\n" + "-" * 50)
    
    def get_input(self, prompt, default=None):
        """获取用户输入"""
        if default:
            full_prompt = f"{prompt} (默认: {default}): "
        else:
            full_prompt = f"{prompt}: "
        
        value = input(full_prompt).strip()
        return value if value else default
    
    def setup_course(self):
        """设置课程信息"""
        self.print_header("设置课程信息")
        
        education_level = self.get_input("学段", "高中")
        subject = self.get_input("学科", "数学")
        topic = self.get_input("主题", "函数的概念")
        grade = self.get_input("年级", "高一")
        
        self.current_course = CourseBasicInfo(
            education_level=education_level,
            subject=subject,
            topic=topic,
            grade=grade
        )
        
        # 设置教学目标
        print("\n请输入教学目标（用逗号分隔）:")
        knowledge = self.get_input("知识目标", "理解概念,掌握方法").split(",")
        skills = self.get_input("技能目标", "能够应用,能够计算").split(",")
        
        self.current_objectives = TeachingObjectives(
            objectives_id=f"obj_{uuid.uuid4().hex[:8]}",
            knowledge_objectives=[k.strip() for k in knowledge],
            skill_objectives=[s.strip() for s in skills],
            process_objectives=["经历探究过程"],
            emotion_objectives=["培养学习兴趣"],
            competency_objectives=["发展核心素养"]
        )
        
        print(f"\n课程信息设置完成: {education_level}{subject} - {topic}")
    
    def generate_exercise(self):
        """生成单个习题"""
        self.print_header("生成单个习题")
        
        if not self.current_course:
            print("  请先设置课程信息（选项1）")
            return
        
        # 选择题型
        print("\n  题型选项:")
        print("    1. 单选题")
        print("    2. 多选题")
        print("    3. 填空题")
        print("    4. 判断题")
        print("    5. 简答题")
        print("    6. 计算题")
        print("    7. 应用题")
        
        type_choice = self.get_input("请选择题型", "1")
        type_map = {
            "1": QuestionType.SINGLE_CHOICE,
            "2": QuestionType.MULTIPLE_CHOICE,
            "3": QuestionType.FILL_BLANK,
            "4": QuestionType.TRUE_FALSE,
            "5": QuestionType.SHORT_ANSWER,
            "6": QuestionType.CALCULATION,
            "7": QuestionType.APPLICATION
        }
        question_type = type_map.get(type_choice, QuestionType.SINGLE_CHOICE)
        
        # 选择难度
        print("\n  难度选项:")
        print("    1. 容易")
        print("    2. 中等")
        print("    3. 较难")
        
        diff_choice = self.get_input("请选择难度", "2")
        diff_map = {
            "1": DifficultyLevel.EASY,
            "2": DifficultyLevel.MEDIUM,
            "3": DifficultyLevel.HARD
        }
        difficulty = diff_map.get(diff_choice, DifficultyLevel.MEDIUM)
        
        # 输入知识点
        key_point = self.get_input("考查知识点", self.current_course.topic)
        
        print(f"\n正在生成{difficulty.value}难度的{question_type.value}...")
        
        exercise = self.exercise_gen.generate_exercise(
            topic=self.current_course.topic,
            question_type=question_type,
            difficulty=difficulty,
            key_points=[key_point],
            course_info=self.current_course,
            objectives=self.current_objectives
        )
        
        print(f"\n【题目】")
        print(f"{exercise.question_text}")
        
        if exercise.answer_options:
            print("\n选项:")
            for option in exercise.answer_options:
                for key, value in option.items():
                    print(f"  {key}. {value}")
        
        print(f"\n【答案】 {exercise.correct_answer}")
        print(f"【解析】 {exercise.explanation}")
        print(f"【分值】 {exercise.score}分")
        print(f"【预计用时】 {exercise.estimated_time}分钟")
    
    def generate_exercise_set(self):
        """生成习题集"""
        self.print_header("生成习题集")
        
        if not self.current_course:
            print("  请先设置课程信息（选项1）")
            return
        
        count = int(self.get_input("题目数量", "10"))
        
        print(f"\n正在生成{count}题的习题集...")
        
        exercise_set = self.exercise_gen.generate_exercise_set(
            topic=self.current_course.topic,
            course_info=self.current_course,
            objectives=self.current_objectives,
            total_count=count
        )
        
        print(f"\n习题集名称: {exercise_set.set_name}")
        print(f"题目数量: {len(exercise_set.exercises)}")
        print(f"总分: {exercise_set.total_score}分")
        print(f"预计用时: {exercise_set.total_time}分钟")
        
        print("\n题目列表:")
        for i, ex in enumerate(exercise_set.exercises[:5], 1):
            print(f"  {i}. [{ex.question_type.value}] {ex.question_text[:30]}... ({ex.score}分)")
        
        if len(exercise_set.exercises) > 5:
            print(f"  ... 还有 {len(exercise_set.exercises) - 5} 题")
    
    def generate_test_paper(self):
        """生成试卷"""
        self.print_header("生成试卷")
        
        if not self.current_course:
            print("  请先设置课程信息（选项1）")
            return
        
        # 选择试卷类型
        print("\n  试卷类型:")
        print("    1. 单元测试")
        print("    2. 期中考试")
        print("    3. 期末考试")
        print("    4. 专项练习")
        
        type_choice = self.get_input("请选择类型", "1")
        type_map = {
            "1": TestPaperType.UNIT_TEST,
            "2": TestPaperType.MIDTERM,
            "3": TestPaperType.FINAL,
            "4": TestPaperType.PRACTICE
        }
        paper_type = type_map.get(type_choice, TestPaperType.UNIT_TEST)
        
        paper_name = self.get_input("试卷名称", f"{self.current_course.topic}测试")
        
        print(f"\n正在生成试卷...")
        
        if paper_type == TestPaperType.PRACTICE:
            self.current_paper = self.paper_gen.generate_practice_paper(
                course_info=self.current_course,
                objectives=self.current_objectives
            )
        else:
            self.current_paper = self.paper_gen.generate_test_paper(
                paper_name=paper_name,
                paper_type=paper_type,
                course_info=self.current_course,
                objectives=self.current_objectives
            )
        
        print(f"\n试卷名称: {self.current_paper.paper_name}")
        print(f"试卷类型: {self.current_paper.paper_type.value}")
        print(f"总分: {self.current_paper.total_score}分")
        print(f"时长: {self.current_paper.duration}分钟")
        print(f"题目数: {self.current_paper.get_exercise_count()}")
        
        print("\n试卷结构:")
        for section in self.current_paper.sections:
            print(f"  【{section.section_name}】{section.exercise_count}题，共{section.total_score}分")
    
    def explain_concept(self):
        """概念讲解"""
        self.print_header("概念讲解")
        
        if not self.current_course:
            print("  请先设置课程信息（选项1）")
            return
        
        concept = self.get_input("请输入要讲解的概念", self.current_course.topic)
        
        print("\n  讲解深度:")
        print("    1. 基础")
        print("    2. 中等")
        print("    3. 深入")
        
        level_choice = self.get_input("请选择深度", "2")
        level_map = {
            "1": ExplanationLevel.BASIC,
            "2": ExplanationLevel.INTERMEDIATE,
            "3": ExplanationLevel.ADVANCED
        }
        level = level_map.get(level_choice, ExplanationLevel.INTERMEDIATE)
        
        print(f"\n正在生成{concept}的讲解...")
        
        explanation = self.explainer.explain_concept(
            concept=concept,
            course_info=self.current_course,
            level=level
        )
        
        print(f"\n【{explanation.title}】")
        print(f"\n引入: {explanation.introduction}")
        
        print("\n讲解内容:")
        for step in explanation.steps:
            print(f"\n  步骤 {step.step_number}: {step.step_title}")
            print(f"  {step.content[:100]}...")
            if step.interaction_prompt:
                print(f"  [互动] {step.interaction_prompt}")
        
        print(f"\n总结: {explanation.conclusion}")
        
        if explanation.common_misconceptions:
            print("\n常见误区:")
            for misc in explanation.common_misconceptions:
                print(f"  • {misc.description}")
    
    def explain_exercise(self):
        """习题讲解"""
        self.print_header("习题讲解")
        
        if not self.current_paper:
            print("  请先生成试卷（选项4）")
            return
        
        # 显示题目列表
        print("\n  试卷题目:")
        all_exercises = self.current_paper.get_all_exercises()
        for i, ex in enumerate(all_exercises[:10], 1):
            print(f"    {i}. [{ex.question_type.value}] {ex.question_text[:30]}...")
        
        choice = int(self.get_input("请选择要讲解的题目编号", "1"))
        if 1 <= choice <= len(all_exercises):
            exercise = all_exercises[choice - 1]
            
            print(f"\n正在生成讲解...")
            
            explanation = self.explainer.explain_exercise(
                exercise=exercise,
                course_info=self.current_course
            )
            
            print(f"\n【题目】")
            print(exercise.question_text)
            
            print(f"\n【讲解】")
            for step in explanation.steps:
                print(f"\n{step.step_number}. {step.step_title}")
                print(f"   {step.content}")
            
            print(f"\n【正确答案】 {exercise.correct_answer}")
    
    def simulate_exam(self):
        """模拟答题"""
        self.print_header("模拟答题")
        
        if not self.current_paper:
            print("  请先生成试卷（选项4）")
            return
        
        print(f"\n开始模拟答题: {self.current_paper.paper_name}")
        print(f"共{self.current_paper.get_exercise_count()}题，满分{self.current_paper.total_score}分")
        
        answers = {}
        all_exercises = self.current_paper.get_all_exercises()
        
        # 模拟答题（随机正确率）
        import random
        for exercise in all_exercises:
            if random.random() > 0.3:  # 70%正确率
                answers[exercise.exercise_id] = exercise.correct_answer
            else:
                answers[exercise.exercise_id] = "模拟错误答案"
        
        print("\n答题完成，正在评分...")
        
        from datetime import datetime, timedelta
        self.current_result = self.evaluator.evaluate_test_paper(
            paper=self.current_paper,
            answers=answers,
            start_time=datetime.now() - timedelta(minutes=45),
            end_time=datetime.now()
        )
        
        print(f"\n评分结果:")
        print(f"  得分: {self.current_result.total_score}/{self.current_result.max_score}")
        print(f"  正确: {self.current_result.correct_count}题")
        print(f"  错误: {self.current_result.wrong_count}题")
        print(f"  用时: {self.current_result.total_time}秒")
    
    def view_analysis_report(self):
        """查看分析报告"""
        self.print_header("查看分析报告")
        
        if not self.current_result:
            print("  请先进行模拟答题（选项7）")
            return
        
        report = self.evaluator.generate_analysis_report(self.current_result, self.current_paper)
        
        print(f"\n【基本信息】")
        print(f"  总分: {report['basic_info']['total_score']}/{report['basic_info']['max_score']}")
        print(f"  正确率: {report['basic_info']['accuracy_rate']}%")
        print(f"  等级: {report['score_level']}")
        
        print(f"\n【知识点掌握情况】")
        for item in report['knowledge_analysis'][:5]:
            print(f"  • {item['knowledge']}: {item['mastery']}% - {item['level']}")
        
        print(f"\n【能力维度分析】")
        for item in report['ability_analysis']:
            print(f"  • {item['ability']}: {item['score']}% - {item['level']}")
        
        print(f"\n【学习建议】")
        for suggestion in report['suggestions']:
            print(f"  • {suggestion}")
        
        if report['improvement_plan']:
            print(f"\n【提升计划】")
            for plan in report['improvement_plan'][:3]:
                print(f"  优先级{plan['priority']}: {plan['knowledge']}")
                print(f"    建议: {plan['suggested_actions'][0]}")
    
    def q_and_a(self):
        """智能问答"""
        self.print_header("智能问答")
        
        if not self.current_course:
            print("  请先设置课程信息（选项1）")
            return
        
        question = self.get_input("请输入您的问题")
        
        if not question:
            print("  问题不能为空")
            return
        
        print("\n正在思考...")
        
        result = self.explainer.answer_question(
            question=question,
            course_info=self.current_course
        )
        
        print(f"\n问题: {result['question']}")
        print(f"类型: {result['question_type']}")
        print(f"难度: {result['difficulty']}")
        print(f"\n回答:\n{result['answer']}")
        
        if result['related_points']:
            print(f"\n相关知识点: {', '.join(result['related_points'])}")
    
    def run(self):
        """运行CLI"""
        while True:
            self.print_menu()
            choice = input("  请选择: ").strip()
            
            if choice == "1":
                self.setup_course()
            elif choice == "2":
                self.generate_exercise()
            elif choice == "3":
                self.generate_exercise_set()
            elif choice == "4":
                self.generate_test_paper()
            elif choice == "5":
                self.explain_concept()
            elif choice == "6":
                self.explain_exercise()
            elif choice == "7":
                self.simulate_exam()
            elif choice == "8":
                self.view_analysis_report()
            elif choice == "9":
                self.q_and_a()
            elif choice == "0":
                print("\n  返回上级菜单")
                break
            else:
                print("\n  无效选择，请重试")
            
            input("\n  按回车继续...")


def main():
    """主函数"""
    print("\n" + "=" * 50)
    print("  欢迎使用AI教师Agent - 测试/讲解模块")
    print("=" * 50)
    
    cli = AssessmentCLI()
    cli.run()


if __name__ == "__main__":
    main()
