"""
AI Teacher Agent - 命令行交互界面

提供完整的交互式备课助手，支持：
1. 交互式备课流程
2. 习题生成与练习
3. 试卷生成
4. 教学讲解
5. 答案评估
"""

import sys
import uuid
from typing import Optional, Dict, Any

# 异步支持
import asyncio

# 导入核心模块
from skills.native.lesson_preparation import (
    LessonPreparationAssistant,
    complete_lesson_preparation,
    FeedbackEvaluator,
    generate_detailed_objectives,
    design_detailed_teaching_process
)

from skills.native.teaching_assessment import (
    ExerciseGenerator,
    TestPaperGenerator,
    TeachingExplainer,
    AnswerEvaluator,
    PaperConfig,
    PaperType
)


class LessonPreparationCLI:
    """备课助手CLI - 交互式界面"""
    
    def __init__(self):
        self.assistant = LessonPreparationAssistant()
        self.current_result: Optional[Dict[str, Any]] = None
        self.current_lesson_plan = None
        self.exercise_gen = ExerciseGenerator()
        self.paper_gen = TestPaperGenerator()
        self.explainer = TeachingExplainer()
        self.evaluator = AnswerEvaluator()
    
    def print_header(self, title: str):
        """打印标题"""
        print("\n" + "=" * 60)
        print(f"  {title}")
        print("=" * 60)
    
    def print_menu(self):
        """打印主菜单"""
        self.print_header("AI Teacher Agent - 智能备课助手")
        print("")
        print("  [1] 新建备课")
        print("  [2] 继续完善教案")
        print("  [3] 生成习题")
        print("  [4] 生成试卷")
        print("  [5] 教学讲解")
        print("  [6] 答案评估")
        print("  [7] 查看当前教案")
        print("  [8] 演示模式")
        print("  [0] 退出")
        print("")
        print("-" * 60)
    
    def get_input(self, prompt: str, default: Optional[str] = None) -> str:
        """获取用户输入"""
        if default:
            full_prompt = f"  {prompt} (默认: {default}): "
        else:
            full_prompt = f"  {prompt}: "
        
        value = input(full_prompt).strip()
        return value if value else (default or "")
    
    def print_result_summary(self, result: Dict[str, Any]):
        """打印结果摘要"""
        print("\n  [摘要]")
        print(f"    课程: {result.get('course_name', 'N/A')}")
        print(f"    主题: {result.get('topic', 'N/A')}")
        print(f"    年级: {result.get('education_level', 'N/A')}")
        
        if 'lesson_plan' in result:
            lp = result['lesson_plan']
            print(f"    教案版本: v{lp.get('version', '1.0')}")
            print(f"    教学目标: {len(lp.get('knowledge_objectives', []))} 个")
            print(f"    教学环节: {len(lp.get('teaching_process', []))} 个")
        
        if 'courseware' in result:
            cw = result['courseware']
            print(f"    课件页数: {len(cw.get('slides', []))} 页")
        
        if 'resources' in result:
            total_res = sum(len(v) for v in result['resources'].values())
            print(f"    教学资源: {total_res} 个")
    
    # ==================== 功能1: 新建备课 ====================
    
    async def create_lesson(self):
        """创建新教案"""
        self.print_header("新建备课")
        
        course_name = self.get_input("课程名称", "高中数学")
        topic = self.get_input("课时主题", "函数的概念")
        education_level = self.get_input("教育阶段", "高中")
        suggested_hours = int(self.get_input("建议课时数", "2"))
        
        print(f"\n  正在为《{topic}》备课，请稍候...\n")
        
        # 使用完整备课流程
        self.current_result = await complete_lesson_preparation(
            course_name=course_name,
            topic=topic,
            education_level=education_level,
            suggested_hours=suggested_hours
        )
        
        if self.current_result:
            self.current_lesson_plan = self.current_result.get('lesson_plan')
            print("\n  [OK] 备课完成!")
            self.print_result_summary(self.current_result)
        else:
            print("\n  [ERROR] 备课失败")
    
    # ==================== 功能2: 完善教案 ====================
    
    async def improve_lesson(self):
        """完善教案"""
        if not self.current_result:
            print("\n  当前没有教案，请先新建备课")
            return
        
        self.print_header("完善教案")
        
        print("\n  请输入您的修改意见：")
        print("  (例如：增加例题、添加小组讨论环节、修改教学目标等)")
        print("  (输入 'q' 返回菜单)")
        
        feedback_text = input("\n  > ").strip()
        if feedback_text.lower() == 'q':
            return
        
        # 模拟反馈评估
        from skills.native.lesson_preparation import UserFeedback
        
        feedback = UserFeedback(
            feedback_type="modify",
            target_section="教案",
            content=feedback_text
        )
        
        # 评估反馈
        evaluator = FeedbackEvaluator()
        evaluation = evaluator.evaluate_feedback(feedback, self.current_lesson_plan)
        
        print("\n  反馈评估：")
        print(f"    决策: {evaluation['decision']}")
        print(f"    置信度: {evaluation['confidence']:.2f}")
        print(f"    推理: {evaluation['reasoning']}")
        
        # 应用修改
        if evaluation['decision'] == 'accepted':
            updated_plan, update_record = evaluator.modify_lesson_plan(
                self.current_lesson_plan, feedback, evaluation
            )
            self.current_lesson_plan = updated_plan
            self.current_result['lesson_plan'] = self.current_lesson_plan
            self.current_result['lesson_plan']['version'] = updated_plan.version
            print(f"\n  [OK] 教案已更新至版本 {updated_plan.version}")
        else:
            print("\n  反馈未被采纳，教案保持不变")
    
    # ==================== 功能3: 生成习题 ====================
    
    def generate_exercises(self):
        """生成习题"""
        self.print_header("生成习题")
        
        topic = self.get_input("主题", self.current_result.get('topic', '函数') if self.current_result else '函数')
        
        print("\n  题型选择：")
        print("  [1] 单选题")
        print("  [2] 多选题")
        print("  [3] 填空题")
        print("  [4] 判断题")
        print("  [5] 简答题")
        print("  [6] 计算题")
        print("  [7] 应用题")
        print("  [8] 全部题型")
        
        choice = self.get_input("选择", "8")
        
        print("\n  正在生成习题...\n")
        
        if choice == "1":
            questions = [self.exercise_gen.generate_single_choice(topic, topic)]
        elif choice == "2":
            questions = [self.exercise_gen.generate_multiple_choice(topic, topic)]
        elif choice == "3":
            questions = [self.exercise_gen.generate_fill_blank(topic, topic)]
        elif choice == "4":
            questions = [self.exercise_gen.generate_true_false(topic, topic)]
        elif choice == "5":
            questions = [self.exercise_gen.generate_short_answer(topic, topic)]
        elif choice == "6":
            questions = [self.exercise_gen.generate_calculation(topic, topic)]
        elif choice == "7":
            questions = [self.exercise_gen.generate_application(topic, topic)]
        else:
            questions = self.exercise_gen.generate_batch(topic, num_each_type=2)
        
        print(f"  生成 {len(questions)} 道习题：\n")
        
        for i, q in enumerate(questions, 1):
            print(f"  【{i}】{q.question_type} ({q.difficulty}) [{q.score}分]")
            print(f"      {q.content}")
            if q.options:
                for opt in q.options:
                    print(f"        {opt}")
            print(f"      答案: {q.answer}")
            if q.analysis:
                print(f"      解析: {q.analysis}")
            print("")
    
    # ==================== 功能4: 生成试卷 ====================
    
    def generate_test_paper(self):
        """生成试卷"""
        self.print_header("生成试卷")
        
        subject = self.get_input("科目", self.current_result.get('course_name', '高中数学') if self.current_result else '高中数学')
        grade = self.get_input("年级", self.current_result.get('education_level', '高一') if self.current_result else '高一')
        topic = self.get_input("主题", self.current_result.get('topic', '函数') if self.current_result else '函数')
        
        print("\n  试卷类型：")
        print("  [1] 选择题专项")
        print("  [2] 综合试卷")
        print("  [3] 单元测试")
        print("  [4] 期中考试")
        print("  [5] 期末考试")
        
        type_choice = self.get_input("选择", "2")
        
        paper_types = {
            "1": PaperType.CHOICE_ONLY,
            "2": PaperType.COMPREHENSIVE,
            "3": PaperType.UNIT_TEST,
            "4": PaperType.MIDTERM,
            "5": PaperType.FINAL
        }
        
        config = PaperConfig(paper_type=paper_types.get(type_choice, PaperType.COMPREHENSIVE))
        
        print("\n  正在生成试卷...\n")
        
        paper = self.paper_gen.generate_paper(
            subject=subject,
            grade=grade,
            topic=topic,
            config=config
        )
        
        print(f"  试卷标题: {paper.title}")
        print(f"  试卷ID: {paper.paper_id}")
        print(f"  总分: {paper.total_score} 分")
        print(f"  时长: {paper.duration} 分钟")
        print(f"  总题数: {paper.total_questions} 道\n")
        
        # 显示试卷结构
        print("  试卷结构：")
        for section in paper.sections:
            print(f"    {section['section_name']}: {section['instruction']}")
        
        # 生成答案
        answer_key = self.paper_gen.generate_answer_key(paper)
        print("\n  [OK] 试卷生成完成！")
        print(f"  答案已准备就绪。")
    
    # ==================== 功能5: 教学讲解 ====================
    
    def show_teaching_explanation(self):
        """教学讲解"""
        self.print_header("教学讲解")
        
        topic = self.get_input("主题", self.current_result.get('topic', '函数') if self.current_result else '函数')
        
        print("\n  讲解类型：")
        print("  [1] 概念讲解")
        print("  [2] 例题讲解")
        print("  [3] 方法讲解")
        print("  [4] 拓展讲解")
        
        choice = self.get_input("选择", "1")
        
        print("\n  正在生成讲解...\n")
        
        if choice == "1":
            exp = self.explainer.explain_concept(topic, topic)
        elif choice == "2":
            exp = self.explainer.explain_example(
                topic, 
                f"关于{topic}的例题",
                "解答步骤：..."
            )
        elif choice == "3":
            exp = self.explainer.explain_method(topic, f"{topic}的解题方法")
        else:
            exp = self.explainer.explain_extension(topic, f"{topic}拓展")
        
        print(f"  【{exp.explanation_type}】{exp.title}")
        print(f"  时长: 约{exp.duration_minutes}分钟\n")
        print("-" * 40)
        print(exp.content)
        print("-" * 40)
        
        if exp.common_mistakes:
            print("\n  常见错误：")
            for mistake in exp.common_mistakes:
                print(f"    - {mistake}")
        
        if exp.tips:
            print("\n  学习技巧：")
            for tip in exp.tips:
                print(f"    - {tip}")
    
    # ==================== 功能6: 答案评估 ====================
    
    def evaluate_answers(self):
        """答案评估"""
        self.print_header("答案评估")
        
        print("\n  请选择评估类型：")
        print("  [1] 评估客观题")
        print("  [2] 评估主观题")
        print("  [3] 演示评估")
        
        choice = self.get_input("选择", "3")
        
        if choice == "1":
            self._evaluate_objective_demo()
        elif choice == "2":
            self._evaluate_subjective_demo()
        else:
            self._evaluate_demo()
    
    def _evaluate_objective_demo(self):
        """评估客观题演示"""
        print("\n  【客观题评估演示】")
        print("  题目: 关于函数概念的说法，正确的是：")
        print("    A. 函数是一种特殊的关系")
        print("    B. 每个x对应唯一的y")
        print("    C. 函数是数集到数集的映射")
        print("    D. 以上都对")
        
        student_answer = self.get_input("您的答案", "D")
        correct_answer = "D"
        
        result = self.evaluator.evaluate_objective(
            question_id="DEMO-001",
            question_type="单选题",
            student_answer=student_answer,
            correct_answer=correct_answer,
            max_score=5
        )
        
        print(f"\n  评估结果: {result.feedback}")
        print(f"  得分: {result.score}/{result.max_score} ({result.score_level})")
        
        if result.suggestions:
            print("\n  建议：")
            for s in result.suggestions:
                print(f"    - {s}")
    
    def _evaluate_subjective_demo(self):
        """评估主观题演示"""
        print("\n  【主观题评估演示】")
        print("  题目: 请简述函数的基本性质。")
        print("  参考答案: 1. 定义域 2. 值域 3. 单调性 4. 奇偶性 5. 周期性")
        
        student_answer = self.get_input("您的答案", "函数的基本性质包括定义域、值域和单调性。")
        reference_answer = "1. 定义域 2. 值域 3. 单调性 4. 奇偶性 5. 周期性"
        
        result = self.evaluator.evaluate_subjective(
            question_id="DEMO-002",
            question_type="简答题",
            student_answer=student_answer,
            reference_answer=reference_answer,
            max_score=10
        )
        
        print(f"\n  评估结果: {result.feedback}")
        print(f"  得分: {result.score:.1f}/{result.max_score} ({result.score_level})")
        
        if result.suggestions:
            print("\n  改进建议：")
            for s in result.suggestions:
                print(f"    - {s}")
    
    def _evaluate_demo(self):
        """综合评估演示"""
        print("\n  【综合评估演示】")
        
        # 批量评估
        items = [
            {
                "question_id": "Q1",
                "question_type": "单选题",
                "student_answer": "A",
                "correct_answer": "A",
                "max_score": 5
            },
            {
                "question_id": "Q2",
                "question_type": "填空题",
                "student_answer": "定义域",
                "correct_answer": "定义域",
                "max_score": 5
            },
            {
                "question_id": "Q3",
                "question_type": "简答题",
                "student_answer": "函数性质包括定义域和值域",
                "reference_answer": "1. 定义域 2. 值域 3. 单调性 4. 奇偶性 5. 周期性",
                "max_score": 10
            }
        ]
        
        results = self.evaluator.evaluate_batch(items)
        summary = self.evaluator.generate_summary(results)
        
        print(f"\n  评估统计：")
        print(f"    总题数: {summary['total_questions']}")
        print(f"    正确数: {summary['correct_count']}")
        print(f"    正确率: {summary['accuracy_rate']:.1%}")
        print(f"    总得分: {summary['total_score']:.1f}/{summary['total_max_score']}")
        print(f"    等级: {summary['score_level']}")
    
    # ==================== 功能7: 查看教案 ====================
    
    def show_lesson_plan(self):
        """查看当前教案"""
        if not self.current_result:
            print("\n  当前没有教案，请先新建备课")
            return
        
        self.print_header("当前教案")
        
        # 显示教案详情
        lp = self.current_result.get('lesson_plan', {})
        
        print(f"\n  课程: {self.current_result.get('course_name', 'N/A')}")
        print(f"  主题: {self.current_result.get('topic', 'N/A')}")
        print(f"  版本: v{lp.get('version', '1.0')}")
        
        print("\n  [教学目标]")
        for obj in lp.get('knowledge_objectives', [])[:5]:
            print(f"    - {obj}")
        
        print("\n  [教学重难点]")
        print(f"    重点: {', '.join(lp.get('key_points', ['N/A'])[:3])}")
        print(f"    难点: {', '.join(lp.get('difficult_points', ['N/A'])[:3])}")
        
        print("\n  [教学过程]")
        for step in lp.get('teaching_process', [])[:5]:
            phase = step.get('phase', step.get('stage', 'N/A'))
            duration = step.get('duration', 'N/A')
            print(f"    【{phase}】{duration}")
        
        print("\n  [课件]")
        cw = self.current_result.get('courseware', {})
        print(f"    共 {len(cw.get('slides', []))} 页")
        print(f"    风格: {cw.get('design_style', 'N/A')}")
    
    # ==================== 功能8: 演示模式 ====================
    
    async def run_demo(self):
        """运行演示"""
        self.print_header("功能演示")
        
        print("\n  正在运行完整功能演示...\n")
        
        # 演示1: 完整备课流程
        print("  [演示1] 完整备课流程")
        result = await complete_lesson_preparation(
            course_name="高中数学",
            topic="函数的概念",
            education_level="高中",
            suggested_hours=2
        )
        self.current_result = result
        print(f"  完成! 教案版本: v{result['lesson_plan']['version']}\n")
        
        # 演示2: 习题生成
        print("  [演示2] 习题生成")
        questions = self.exercise_gen.generate_batch("函数的概念", num_each_type=1)
        print(f"  生成 {len(questions)} 道习题\n")
        
        # 演示3: 试卷生成
        print("  [演示3] 试卷生成")
        paper = self.paper_gen.generate_paper(
            subject="高中数学",
            grade="高一",
            topic="函数的概念"
        )
        print(f"  生成试卷: {paper.title}")
        print(f"  总分: {paper.total_score}分, 题数: {paper.total_questions}道\n")
        
        # 演示4: 教学讲解
        print("  [演示4] 教学讲解")
        exp = self.explainer.explain_concept("函数", "函数的概念")
        print(f"  生成讲解: {exp.title}, 时长: {exp.duration_minutes}分钟\n")
        
        # 演示5: 答案评估
        print("  [演示5] 答案评估")
        result = self.evaluator.evaluate_objective(
            question_id="DEMO",
            question_type="单选题",
            student_answer="A",
            correct_answer="A",
            max_score=5
        )
        print(f"  评估结果: {result.score}/{result.max_score}\n")
        
        print("  [OK] 演示完成!")
    
    # ==================== 主循环 ====================
    
    def run(self):
        """运行CLI"""
        while True:
            self.print_menu()
            choice = input("  请选择: ").strip()
            
            if choice == "1":
                asyncio.run(self.create_lesson())
            elif choice == "2":
                asyncio.run(self.improve_lesson())
            elif choice == "3":
                self.generate_exercises()
            elif choice == "4":
                self.generate_test_paper()
            elif choice == "5":
                self.show_teaching_explanation()
            elif choice == "6":
                self.evaluate_answers()
            elif choice == "7":
                self.show_lesson_plan()
            elif choice == "8":
                asyncio.run(self.run_demo())
            elif choice == "0":
                print("\n  感谢使用 AI Teacher Agent，再见!")
                break
            else:
                print("\n  无效选择，请重试")
            
            input("\n  按回车继续...")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("  欢迎使用 AI Teacher Agent - 智能备课助手")
    print("  版本: 2.0 (整合版)")
    print("=" * 60)
    
    cli = LessonPreparationCLI()
    cli.run()


if __name__ == "__main__":
    main()
