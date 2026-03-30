"""
测试/讲解模块演示脚本

演示AI教师Agent的出题、测试、讲解功能
"""
import sys
sys.path.insert(0, 'src')

from models import (
    CourseBasicInfo, TeachingObjectives,
    QuestionType, DifficultyLevel, TestPaperType
)
from skills.teaching_assessment import (
    ExerciseGenerator, TestPaperGenerator,
    TeachingExplainer, AnswerEvaluator
)


def print_separator(title: str):
    """打印分隔线"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def demo_exercise_generator():
    """演示习题生成"""
    print_separator("1. 习题生成器演示")
    
    # 初始化生成器
    generator = ExerciseGenerator()
    
    # 课程信息
    course_info = CourseBasicInfo(
        education_level="高中",
        subject="数学",
        topic="函数的概念",
        grade="高一"
    )
    
    # 教学目标
    objectives = TeachingObjectives(
        objectives_id="obj_001",
        knowledge_objectives=["理解函数的概念", "掌握函数的表示方法"],
        skill_objectives=["能够判断函数关系", "能够求函数值"],
        process_objectives=["经历从具体到抽象的过程"],
        emotion_objectives=["体会数学的抽象美"],
        competency_objectives=["发展数学抽象素养"]
    )
    
    print("\n【生成单选题】")
    exercise1 = generator.generate_exercise(
        topic="函数的概念",
        question_type=QuestionType.SINGLE_CHOICE,
        difficulty=DifficultyLevel.MEDIUM,
        key_points=["函数的定义"],
        course_info=course_info,
        objectives=objectives
    )
    print(f"题目: {exercise1.question_text}")
    print(f"选项:")
    for option in exercise1.answer_options:
        for key, value in option.items():
            print(f"  {key}. {value}")
    print(f"正确答案: {exercise1.correct_answer}")
    print(f"解析: {exercise1.explanation}")
    
    print("\n【生成填空题】")
    exercise2 = generator.generate_exercise(
        topic="函数的概念",
        question_type=QuestionType.FILL_BLANK,
        difficulty=DifficultyLevel.EASY,
        key_points=["函数的三要素"],
        course_info=course_info,
        objectives=objectives
    )
    print(f"题目: {exercise2.question_text}")
    print(f"答案: {exercise2.correct_answer}")
    
    print("\n【生成习题集】")
    exercise_set = generator.generate_exercise_set(
        topic="函数的概念",
        course_info=course_info,
        objectives=objectives,
        total_count=10
    )
    print(f"习题集名称: {exercise_set.set_name}")
    print(f"题目数量: {len(exercise_set.exercises)}")
    print(f"总分: {exercise_set.total_score}")
    print(f"预计用时: {exercise_set.total_time}分钟")
    
    return generator, course_info, objectives


def demo_test_paper_generator(course_info, objectives):
    """演示试卷生成"""
    print_separator("2. 试卷生成器演示")
    
    generator = TestPaperGenerator()
    
    print("\n【生成单元测试卷】")
    paper = generator.generate_test_paper(
        paper_name="高一数学-函数的概念-单元测试",
        paper_type=TestPaperType.UNIT_TEST,
        course_info=course_info,
        objectives=objectives
    )
    
    print(f"试卷名称: {paper.paper_name}")
    print(f"试卷类型: {paper.paper_type.value}")
    print(f"总分: {paper.total_score}")
    print(f"时长: {paper.duration}分钟")
    print(f"章节数: {len(paper.sections)}")
    print(f"总题数: {paper.get_exercise_count()}")
    
    print("\n试卷结构:")
    for section in paper.sections:
        print(f"\n  【{section.section_name}】")
        print(f"  题目数: {section.exercise_count}")
        print(f"  分值: {section.total_score}")
        print(f"  说明: {section.instructions}")
    
    print("\n【生成专项练习卷】")
    practice_paper = generator.generate_practice_paper(
        course_info=course_info,
        objectives=objectives,
        exercise_count=15
    )
    print(f"练习卷名称: {practice_paper.paper_name}")
    print(f"题目数: {practice_paper.get_exercise_count()}")
    
    # 统计信息
    stats = generator.get_paper_statistics(paper)
    print("\n试卷统计:")
    print(f"  难度分布: {stats['difficulty_distribution']}")
    print(f"  题型分布: {stats['type_distribution']}")
    
    return generator, paper


def demo_teaching_explainer(course_info):
    """演示智能讲解"""
    print_separator("3. 智能讲解引擎演示")
    
    explainer = TeachingExplainer()
    
    print("\n【概念讲解】")
    explanation = explainer.explain_concept(
        concept="函数",
        course_info=course_info,
        level="intermediate"
    )
    
    print(f"讲解主题: {explanation.title}")
    print(f"讲解类型: {explanation.explanation_type}")
    print(f"难度级别: {explanation.level}")
    print(f"\n引入: {explanation.introduction}")
    
    print("\n讲解步骤:")
    for step in explanation.steps:
        print(f"\n  步骤 {step.step_number}: {step.step_title}")
        print(f"  内容: {step.content[:80]}...")
        print(f"  要点: {', '.join(step.key_points)}")
        print(f"  预计时长: {step.expected_duration}分钟")
    
    print(f"\n总结: {explanation.conclusion}")
    
    print("\n常见误区:")
    for misc in explanation.common_misconceptions:
        print(f"  - {misc.description}")
        print(f"    原因: {misc.why_wrong}")
        print(f"    纠正: {misc.how_to_correct}")
    
    print("\n【例题讲解】")
    example_explanation = explainer.explain_example(
        example_title="函数概念理解例题",
        problem="已知f(x) = 2x + 1，求f(3)的值。",
        solution="将x=3代入f(x)=2x+1，得f(3)=2×3+1=7。",
        course_info=course_info,
        key_points=["函数值的计算", "代入法"]
    )
    print(f"例题: {example_explanation.title}")
    print(f"步骤数: {len(example_explanation.steps)}")
    
    print("\n【问答功能】")
    qa_result = explainer.answer_question(
        question="函数和映射有什么区别？",
        course_info=course_info
    )
    print(f"问题: {qa_result['question']}")
    print(f"类型: {qa_result['question_type']}")
    print(f"难度: {qa_result['difficulty']}")
    print(f"回答: {qa_result['answer'][:100]}...")
    
    return explainer


def demo_answer_evaluator(paper):
    """演示答题评估"""
    print_separator("4. 答题评估器演示")
    
    evaluator = AnswerEvaluator()
    
    # 模拟学生答案
    answers = {}
    exercise_map = {}
    
    for section in paper.sections:
        for exercise in section.exercises:
            exercise_map[exercise.exercise_id] = exercise
            # 模拟不同正确率的答案
            import random
            if random.random() > 0.4:  # 60%正确率
                answers[exercise.exercise_id] = exercise.correct_answer
            else:
                answers[exercise.exercise_id] = "错误答案"
    
    print("\n【评估试卷】")
    from datetime import datetime, timedelta
    start_time = datetime.now() - timedelta(minutes=45)
    end_time = datetime.now()
    
    result = evaluator.evaluate_test_paper(
        paper=paper,
        answers=answers,
        student_id="student_001",
        start_time=start_time,
        end_time=end_time
    )
    
    print(f"学生ID: {result.student_id}")
    print(f"总分: {result.total_score}/{result.max_score}")
    print(f"正确题数: {result.correct_count}")
    print(f"错误题数: {result.wrong_count}")
    print(f"用时: {result.total_time}秒")
    
    print("\n【生成分析报告】")
    report = evaluator.generate_analysis_report(result, paper)
    
    print(f"\n成绩等级: {report['score_level']}")
    print(f"正确率: {report['basic_info']['accuracy_rate']}%")
    
    print("\n知识点掌握情况:")
    for item in report['knowledge_analysis'][:5]:
        print(f"  - {item['knowledge']}: {item['mastery']}% ({item['level']})")
    
    print("\n能力维度分析:")
    for item in report['ability_analysis']:
        print(f"  - {item['ability']}: {item['score']}% ({item['level']})")
    
    print("\n学习建议:")
    for suggestion in report['suggestions']:
        print(f"  * {suggestion}")
    
    print("\n提升计划:")
    for plan in report['improvement_plan'][:3]:
        print(f"  优先级{plan['priority']}: {plan['knowledge']}")
        print(f"    当前掌握度: {plan['current_mastery']}% → 目标: {plan['target_mastery']}%")
        print(f"    建议用时: {plan['estimated_time']}")
    
    print("\n【错题讲解】")
    explanations = evaluator.get_wrong_question_explanations(result, paper)
    print(f"错题数量: {len(explanations)}")
    for i, exp in enumerate(explanations[:2], 1):
        print(f"\n  错题{i}: {exp.title[:40]}...")
        print(f"  讲解步骤: {len(exp.steps)}步")
    
    return evaluator, result


def demo_complete_workflow():
    """演示完整工作流程"""
    print_separator("5. 完整工作流程演示")
    
    # 初始化所有组件
    exercise_gen = ExerciseGenerator()
    paper_gen = TestPaperGenerator()
    explainer = TeachingExplainer()
    evaluator = AnswerEvaluator()
    
    # 课程信息
    course_info = CourseBasicInfo(
        education_level="高中",
        subject="数学",
        topic="三角函数",
        grade="高一",
        suggested_hours=6
    )
    
    objectives = TeachingObjectives(
        objectives_id="obj_002",
        knowledge_objectives=["理解三角函数的定义", "掌握三角函数的图像和性质"],
        skill_objectives=["能够绘制三角函数图像", "能够解决三角函数应用问题"],
        process_objectives=["经历从特殊到一般的探究过程"],
        emotion_objectives=["感受数学与生活的联系"],
        competency_objectives=["发展直观想象素养"]
    )
    
    print("\n【步骤1: 生成专项练习】")
    exercise_set = exercise_gen.generate_exercise_set(
        topic="三角函数",
        course_info=course_info,
        objectives=objectives,
        total_count=5
    )
    print(f"生成习题集: {exercise_set.set_name}")
    
    print("\n【步骤2: 生成测试卷】")
    paper = paper_gen.generate_test_paper(
        paper_name="三角函数单元测试",
        paper_type=TestPaperType.UNIT_TEST,
        course_info=course_info,
        objectives=objectives
    )
    print(f"生成试卷: {paper.paper_name} ({paper.get_exercise_count()}题)")
    
    print("\n【步骤3: 学生答题】")
    # 模拟学生答题
    answers = {}
    import random
    for section in paper.sections:
        for exercise in section.exercises:
            # 模拟答题（70%正确率）
            if random.random() > 0.3:
                answers[exercise.exercise_id] = exercise.correct_answer
            else:
                answers[exercise.exercise_id] = "学生错误答案"
    print(f"学生完成答题: {len(answers)}题")
    
    print("\n【步骤4: 自动评分】")
    from datetime import datetime, timedelta
    result = evaluator.evaluate_test_paper(
        paper=paper,
        answers=answers,
        start_time=datetime.now() - timedelta(minutes=50),
        end_time=datetime.now()
    )
    print(f"评分完成: {result.total_score}/{result.max_score}分")
    
    print("\n【步骤5: 生成讲解】")
    # 为错题生成讲解
    wrong_explanations = evaluator.get_wrong_question_explanations(result, paper)
    print(f"为{len(wrong_explanations)}道错题生成讲解")
    
    print("\n【步骤6: 输出分析报告】")
    report = evaluator.generate_analysis_report(result, paper)
    print(f"成绩: {report['basic_info']['accuracy_rate']}% ({report['score_level']})")
    print(f"建议: {report['suggestions'][0]}")
    
    print("\n[OK] 完整工作流程演示完成！")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("  AI教师Agent - 测试/讲解模块演示")
    print("=" * 60)
    print("\n本演示展示以下功能：")
    print("  1. 习题生成器 - 自动生成各类题型")
    print("  2. 试卷生成器 - 智能组卷")
    print("  3. 智能讲解引擎 - 概念、例题、习题讲解")
    print("  4. 答题评估器 - 自动评分和分析")
    print("  5. 完整工作流程 - 从出题到讲解的闭环")
    
    # 运行各模块演示
    generator, course_info, objectives = demo_exercise_generator()
    paper_gen, paper = demo_test_paper_generator(course_info, objectives)
    explainer = demo_teaching_explainer(course_info)
    evaluator, result = demo_answer_evaluator(paper)
    demo_complete_workflow()
    
    # 总结
    print_separator("演示总结")
    print("\n已实现功能:")
    print("  [OK] 习题生成器 (ExerciseGenerator)")
    print("      - 支持9种题型: 单选、多选、填空、判断、简答、计算、证明、应用、综合")
    print("      - 支持4级难度: 容易、中等、较难、挑战")
    print("      - 自动生成解析和解题步骤")
    print("      - 习题集管理")
    
    print("\n  [OK] 试卷生成器 (TestPaperGenerator)")
    print("      - 支持7种试卷类型: 练习、测验、单元测试、期中、期末、模拟、入学")
    print("      - 智能难度分布")
    print("      - 试卷结构自定义")
    print("      - 导出功能")
    
    print("\n  [OK] 智能讲解引擎 (TeachingExplainer)")
    print("      - 概念讲解: 从具体到抽象的多步骤讲解")
    print("      - 例题讲解: 完整的解题思路分析")
    print("      - 习题讲解: 针对具体题目的讲解")
    print("      - 错误分析: 针对性纠错讲解")
    print("      - 智能问答: 回答学生提问")
    
    print("\n  [OK] 答题评估器 (AnswerEvaluator)")
    print("      - 自动评分: 支持多种题型的智能评分")
    print("      - 知识分析: 知识点掌握度分析")
    print("      - 能力分析: 多维度能力评估")
    print("      - 错题讲解: 自动生成错题讲解")
    print("      - 学习建议: 个性化提升方案")
    
    print("\n" + "=" * 60)
    print("  测试/讲解模块演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
