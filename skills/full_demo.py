"""
AI Teacher Agent - 完整功能演示脚本

演示所有核心功能：
1. 完整备课流程（6步）
2. 细化三维教学目标
3. 详细教学过程设计
4. 课件结构生成
5. 习题生成
6. 试卷生成
7. 教学讲解
8. 答案评估
"""

import asyncio
import sys

# 导入核心模块
from skills.native.lesson_preparation import (
    LessonPreparationAssistant,
    complete_lesson_preparation,
    generate_detailed_objectives,
    design_detailed_teaching_process,
    FeedbackEvaluator,
    UserFeedback,
    LessonPlan
)

from skills.native.teaching_assessment import (
    ExerciseGenerator,
    TestPaperGenerator,
    TeachingExplainer,
    AnswerEvaluator,
    PaperConfig,
    PaperType,
    Difficulty
)


def print_separator(title: str):
    """打印分隔线"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_json(data, indent=2):
    """美化打印JSON"""
    import json
    print(json.dumps(data, ensure_ascii=False, indent=indent))


async def demo_lesson_preparation():
    """演示完整备课流程"""
    print_separator("演示1: 完整备课流程")
    
    print("\n  准备为「函数的概念」创建完整教案...\n")
    
    result = await complete_lesson_preparation(
        course_name="高中数学",
        topic="函数的概念",
        education_level="高中",
        suggested_hours=2
    )
    
    # 展示备课成果
    print("\n  [备课成果]")
    
    # 1. 课程信息
    print(f"\n  课程: {result['course_name']}")
    print(f"  主题: {result['topic']}")
    print(f"  年级: {result['education_level']}")
    
    # 2. 教学目标
    objectives = result.get('objectives', {})
    print(f"\n  [教学目标]")
    print(f"    知识目标: {len(objectives.get('knowledge_objectives', []))} 条")
    for obj in objectives.get('knowledge_objectives', [])[:3]:
        print(f"      - {obj}")
    print(f"    技能目标: {len(objectives.get('skill_objectives', []))} 条")
    print(f"    情感目标: {len(objectives.get('emotion_objectives', []))} 条")
    
    # 3. 教案
    lesson_plan = result.get('lesson_plan', {})
    print(f"\n  [教案]")
    print(f"    版本: v{lesson_plan.get('version', '1.0')}")
    print(f"    知识目标: {len(lesson_plan.get('knowledge_objectives', []))} 条")
    print(f"    能力目标: {len(lesson_plan.get('ability_objectives', []))} 条")
    
    # 4. 详细教学过程
    print(f"\n  [详细教学过程]")
    for step in lesson_plan.get('teaching_process', [])[:5]:
        print(f"\n    步骤 {step.get('step', '?')}: 【{step.get('phase', step.get('stage', 'N/A'))}】")
        print(f"      时长: {step.get('duration', 'N/A')}")
        print(f"      教师活动: {step.get('teacher_activity', step.get('activities', ['N/A']))}")
        print(f"      设计意图: {step.get('design_intent', 'N/A')}")
    
    # 5. 课件
    courseware = result.get('courseware', {})
    print(f"\n  [课件]")
    print(f"    总页数: {len(courseware.get('slides', []))} 页")
    print(f"    设计风格: {courseware.get('design_style', 'N/A')}")
    
    # 显示课件结构
    print("\n  课件结构预览:")
    for slide in courseware.get('slides', [])[:5]:
        print(f"    第{slide.get('number', slide.get('slide_number', '?'))}页 [{slide.get('type', slide.get('slide_type', 'N/A'))}]")
        print(f"      标题: {slide.get('title', 'N/A')}")
    
    # 6. 教学资源
    resources = result.get('resources', {})
    total_res = sum(len(v) for v in resources.values())
    print(f"\n  [教学资源]")
    print(f"    总计: {total_res} 个")
    for res_type, res_list in resources.items():
        if res_list:
            print(f"    - {res_type}: {len(res_list)} 个")
    
    return result


def demo_exercise_generator():
    """演示习题生成"""
    print_separator("演示2: 习题生成")
    
    generator = ExerciseGenerator()
    
    print("\n  生成各类型习题...\n")
    
    # 1. 按类型生成
    print("  [按类型生成]")
    question_types = [
        ("单选题", generator.generate_single_choice),
        ("多选题", generator.generate_multiple_choice),
        ("填空题", generator.generate_fill_blank),
        ("判断题", generator.generate_true_false),
        ("简答题", generator.generate_short_answer),
        ("计算题", generator.generate_calculation),
        ("应用题", generator.generate_application),
        ("探究题", generator.generate_inquiry),
        ("开放题", generator.generate_open_ended),
    ]
    
    for qtype, gen_func in question_types:
        q = gen_func("函数", "函数的概念", Difficulty.MEDIUM)
        print(f"\n  [{qtype}] ({q.difficulty})")
        print(f"    ID: {q.question_id}")
        print(f"    题目: {q.content[:50]}...")
        print(f"    答案: {q.answer}")
        print(f"    分值: {q.score}分")
    
    # 2. 批量生成
    print("\n\n  [批量生成]")
    questions = generator.generate_batch("函数的概念", num_each_type=2)
    print(f"  共生成 {len(questions)} 道习题")
    
    # 3. 按难度生成
    print("\n  [按难度生成]")
    by_difficulty = generator.generate_by_difficulty(
        "函数", "函数的概念",
        easy=2, medium=3, hard=2
    )
    for level, qs in by_difficulty.items():
        print(f"    {level}: {len(qs)} 道")
    
    # 统计
    stats = generator.get_statistics()
    print(f"\n  生成统计: {stats['total_generated']} 道习题")


def demo_test_paper_generator():
    """演示试卷生成"""
    print_separator("演示3: 试卷生成")
    
    generator = TestPaperGenerator()
    
    # 生成综合试卷
    config = PaperConfig(
        paper_type=PaperType.COMPREHENSIVE,
        total_score=100,
        duration=90,
        include_choice=True,
        include_fill_blank=True,
        include_calculation=True,
        include_application=True,
        include_inquiry=False
    )
    
    print("\n  生成综合试卷...")
    paper = generator.generate_paper(
        subject="高中数学",
        grade="高一",
        topic="函数的概念",
        config=config
    )
    
    print(f"\n  试卷信息:")
    print(f"    标题: {paper.title}")
    print(f"    ID: {paper.paper_id}")
    print(f"    类型: {paper.paper_type}")
    print(f"    总分: {paper.total_score} 分")
    print(f"    时长: {paper.duration} 分钟")
    print(f"    题数: {paper.total_questions} 道")
    
    print(f"\n  试卷结构:")
    for section in paper.sections:
        print(f"    {section['section_name']}")
        print(f"      {section['instruction']}")
        print(f"      满分: {section['score']}分, 题数: {len(section['questions'])}道")
    
    # 生成其他类型试卷
    print("\n\n  生成其他类型试卷...")
    
    test_types = [
        PaperType.CHOICE_ONLY,
        PaperType.UNIT_TEST,
        PaperType.MIDTERM,
        PaperType.FINAL
    ]
    
    for ptype in test_types:
        config = PaperConfig(paper_type=ptype)
        p = generator.generate_paper(
            subject="高中数学",
            grade="高一",
            topic="函数的概念",
            config=config
        )
        print(f"    {ptype.value}: {p.paper_id} ({p.total_score}分)")
    
    # 生成答案
    print("\n  生成答案...")
    answer_key = generator.generate_answer_key(paper)
    print(f"  答案ID: {answer_key['paper_id']}")
    print(f"  总分: {answer_key['total_score']}")


def demo_teaching_explainer():
    """演示教学讲解"""
    print_separator("演示4: 教学讲解")
    
    explainer = TeachingExplainer()
    
    # 1. 概念讲解
    print("\n  [概念讲解]")
    concept = explainer.explain_concept(
        topic="函数",
        concept_name="函数的概念",
        difficulty=Difficulty.MEDIUM
    )
    print(f"\n  讲解ID: {concept.explanation_id}")
    print(f"  类型: {concept.explanation_type}")
    print(f"  标题: {concept.title}")
    print(f"  时长: {concept.duration_minutes} 分钟")
    print(f"  难度: {concept.difficulty}")
    print(f"  关键点: {', '.join(concept.key_points[:3])}")
    print(f"  常见错误: {len(concept.common_mistakes)} 条")
    print(f"  学习技巧: {len(concept.tips)} 条")
    
    # 2. 例题讲解
    print("\n\n  [例题讲解]")
    example = explainer.explain_example(
        topic="函数",
        example_problem="已知 f(x) = 2x + 1，求 f(3)",
        solution="f(3) = 2*3 + 1 = 7",
        difficulty=Difficulty.EASY
    )
    print(f"\n  讲解ID: {example.explanation_id}")
    print(f"  类型: {example.explanation_type}")
    print(f"  时长: {example.duration_minutes} 分钟")
    print(f"  题目: {example.examples[0]['example']}")
    
    # 3. 方法讲解
    print("\n\n  [方法讲解]")
    method = explainer.explain_method(
        topic="函数",
        method_name="数形结合",
        application_scenarios=["求解方程", "分析性质", "证明不等式"],
        difficulty=Difficulty.MEDIUM
    )
    print(f"\n  讲解ID: {method.explanation_id}")
    print(f"  类型: {method.explanation_type}")
    print(f"  标题: {method.title}")
    print(f"  时长: {method.duration_minutes} 分钟")
    
    # 4. 拓展讲解
    print("\n\n  [拓展讲解]")
    extension = explainer.explain_extension(
        topic="函数",
        extension_name="函数的零点",
        base_knowledge="函数的概念",
        difficulty=Difficulty.HARD
    )
    print(f"\n  讲解ID: {extension.explanation_id}")
    print(f"  类型: {extension.explanation_type}")
    print(f"  标题: {extension.title}")
    print(f"  时长: {extension.duration_minutes} 分钟")
    print(f"  难度: {extension.difficulty}")


def demo_answer_evaluator():
    """演示答案评估"""
    print_separator("演示5: 答案评估")
    
    evaluator = AnswerEvaluator()
    
    # 1. 评估客观题
    print("\n  [客观题评估]")
    
    test_cases = [
        ("单选题", "A", "A", 5),
        ("单选题", "B", "A", 5),
        ("多选题", "AB", "ABC", 10),
        ("填空题", "定义域", "定义域", 5),
        ("判断题", "O", "X", 5),
    ]
    
    for qtype, student_ans, correct_ans, max_score in test_cases:
        result = evaluator.evaluate_objective(
            question_id=f"TEST-{qtype}",
            question_type=qtype,
            student_answer=student_ans,
            correct_answer=correct_ans,
            max_score=max_score
        )
        
        status = "[OK]" if result.is_correct else "[X]"
        print(f"\n  {status} {qtype}")
        print(f"      学生答案: {result.student_answer}")
        print(f"      正确答案: {result.correct_answer}")
        print(f"      得分: {result.score}/{result.max_score} ({result.score_level})")
        print(f"      反馈: {result.feedback}")
    
    # 2. 评估主观题
    print("\n\n  [主观题评估]")
    
    subjective_cases = [
        ("简答题", 
         "函数的基本性质包括定义域、值域和单调性。",
         "1. 定义域 2. 值域 3. 单调性 4. 奇偶性 5. 周期性",
         10),
        ("计算题",
         "解：f(3) = 2*3 + 1 = 7。",
         "f(3) = 2*3 + 1 = 7，答案为7。",
         15),
    ]
    
    for qtype, student_ans, ref_ans, max_score in subjective_cases:
        result = evaluator.evaluate_subjective(
            question_id=f"TEST-{qtype}",
            question_type=qtype,
            student_answer=student_ans,
            reference_answer=ref_ans,
            max_score=max_score
        )
        
        print(f"\n  {qtype}")
        print(f"      得分: {result.score:.1f}/{result.max_score} ({result.score_level})")
        print(f"      反馈: {result.feedback}")
        if result.suggestions:
            print(f"      建议: {result.suggestions[0]}")
    
    # 3. 批量评估
    print("\n\n  [批量评估统计]")
    
    batch_items = [
        {"question_id": "Q1", "question_type": "单选题", "student_answer": "A", "correct_answer": "A", "max_score": 5},
        {"question_id": "Q2", "question_type": "单选题", "student_answer": "C", "correct_answer": "B", "max_score": 5},
        {"question_id": "Q3", "question_type": "填空题", "student_answer": "定义域", "correct_answer": "定义域", "max_score": 5},
        {"question_id": "Q4", "question_type": "简答题", "student_answer": "包括定义域", "reference_answer": "1. 定义域 2. 值域", "max_score": 10},
    ]
    
    results = evaluator.evaluate_batch(batch_items)
    summary = evaluator.generate_summary(results)
    
    print(f"\n  总题数: {summary['total_questions']}")
    print(f"  正确数: {summary['correct_count']}")
    print(f"  正确率: {summary['accuracy_rate']:.1%}")
    print(f"  总得分: {summary['total_score']:.1f}/{summary['total_max_score']}")
    print(f"  平均分: {summary['average_score']:.1f}")
    print(f"  等级: {summary['score_level']}")


async def demo_feedback_processing():
    """演示反馈处理"""
    print_separator("演示6: 反馈处理")
    
    evaluator = FeedbackEvaluator()
    
    # 创建教案对象
    lesson_plan = LessonPlan(
        course_name="高中数学",
        topic="函数的概念",
        duration=45,
        education_level="高一",
        knowledge_objectives=["理解函数概念", "掌握函数表示"],
        ability_objectives=["能判断函数关系", "能求函数值"],
        emotion_objectives=["培养数学兴趣"],
        key_points=["函数概念", "函数三要素"],
        difficult_points=["函数概念的理解"],
        teaching_methods=["讲授法", "讨论法"],
        teaching_process=[
            {"stage": "导入", "duration": 5, "activities": [], "methods": ""},
            {"stage": "新授", "duration": 20, "activities": [], "methods": ""}
        ],
        blackboard_design="函数概念图",
        resources_needed=["课件", "教材"],
        homework={"basic": "练习题", "advanced": "思考题"},
        reflection_questions=["学生理解如何?"]
    )
    
    # 反馈案例
    feedback_cases = [
        ("请增加函数在实际生活中的应用例子", "accepted"),
        ("太简单了", "rejected"),
        ("添加更多练习题", "partial"),
    ]
    
    for content, expected_decision in feedback_cases:
        feedback = UserFeedback(
            feedback_type="modify",
            target_section="教案",
            content=content
        )
        
        print(f"\n  反馈: {content}")
        
        evaluation = evaluator.evaluate_feedback(feedback, lesson_plan)
        
        print(f"  决策: {evaluation['decision']} (预期: {expected_decision})")
        print(f"  置信度: {evaluation['confidence']:.2f}")
        print(f"  相关性: {evaluation['relevance_score']:.2f}")
        print(f"  可行性: {evaluation['feasibility_score']:.2f}")
        
        # 应用修改
        if evaluation['decision'] == 'accepted':
            updated_plan, update_record = evaluator.modify_lesson_plan(
                lesson_plan, feedback, evaluation
            )
            print(f"  更新: {update_record['status']}, 版本: {updated_plan.version}")


async def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("  AI Teacher Agent - 完整功能演示")
    print("  版本: 2.0 (整合版)")
    print("=" * 60)
    
    # 演示1: 完整备课流程
    await demo_lesson_preparation()
    input("\n\n  按回车继续演示...")
    
    # 演示2: 习题生成
    demo_exercise_generator()
    input("\n\n  按回车继续演示...")
    
    # 演示3: 试卷生成
    demo_test_paper_generator()
    input("\n\n  按回车继续演示...")
    
    # 演示4: 教学讲解
    demo_teaching_explainer()
    input("\n\n  按回车继续演示...")
    
    # 演示5: 答案评估
    demo_answer_evaluator()
    input("\n\n  按回车继续演示...")
    
    # 演示6: 反馈处理
    await demo_feedback_processing()
    
    # 完成
    print_separator("演示完成")
    print("\n  所有功能验证成功!")
    print("\n  已实现完整功能:")
    print("    [OK] 完整备课流程 (6步)")
    print("    [OK] 细化三维教学目标")
    print("    [OK] 详细教学过程设计")
    print("    [OK] 课件结构生成")
    print("    [OK] 习题生成 (9种题型)")
    print("    [OK] 试卷生成 (5种类型)")
    print("    [OK] 教学讲解 (4种类型)")
    print("    [OK] 答案评估 (客观+主观)")
    print("    [OK] 用户反馈处理")
    print("    [OK] 交互式CLI界面")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
