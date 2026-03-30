"""
完整功能演示脚本

演示AI教师Agent的所有功能：
1. 完整备课流程
2. 细化教学目标
3. 详细教学过程
4. 课件结构生成
5. 用户反馈处理
"""
import sys
sys.path.insert(0, 'src')

from models import CourseBasicInfo
from skills import LessonPreparationSkill


def print_separator(title: str):
    """打印分隔线"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_json(data, indent=2):
    """美化打印JSON"""
    import json
    print(json.dumps(data, ensure_ascii=False, indent=indent))


def main():
    print("\n" + "=" * 60)
    print("  AI教师Agent - 智能备课助手 (完整版)")
    print("=" * 60)
    
    # 初始化技能
    skill = LessonPreparationSkill()
    
    # ==================== 完整备课流程 ====================
    print_separator("完整备课流程")
    
    course_info = CourseBasicInfo(
        education_level="高中",
        subject="数学",
        topic="函数的概念",
        grade="高一",
        textbook_version="人教版",
        suggested_hours=4
    )
    
    # 执行完整备课
    result = skill.complete_lesson_preparation(course_info)
    
    # 展示备课成果
    print_separator("备课成果展示")
    
    # 1. 教学目标
    print("\n【教学目标】")
    objectives = result['objectives']
    print(f"  知识目标: {len(objectives['knowledge_objectives'])} 条")
    for obj in objectives['knowledge_objectives']:
        print(f"    - {obj}")
    print(f"  技能目标: {len(objectives['skill_objectives'])} 条")
    print(f"  过程目标: {len(objectives['process_objectives'])} 条")
    print(f"  情感目标: {len(objectives['emotion_objectives'])} 条")
    print(f"  素养目标: {len(objectives['competency_objectives'])} 条")
    
    # 2. 教案
    print("\n【教案】")
    lesson_plan = result['lesson_plan']
    print(f"  标题: {lesson_plan['title']}")
    print(f"  版本: v{lesson_plan['version']}")
    
    # 3. 详细教学过程
    print("\n【详细教学过程】")
    for step in lesson_plan['teaching_procedure']:
        print(f"\n  步骤 {step['step']}: 【{step['phase']}】{step['duration']}")
        print(f"    教师活动: {step['teacher_activity']}")
        print(f"    学生活动: {step['student_activity']}")
        print(f"    设计意图: {step['design_intent']}")
        if step.get('key_points'):
            print(f"    关键点: {', '.join(step['key_points'])}")
    
    # 4. 课件大纲
    print("\n【课件大纲】")
    courseware = result['courseware']
    print(f"  课件ID: {courseware['outline_id']}")
    print(f"  总页数: {courseware['total_slides']} 页")
    print(f"  预计时长: {courseware['estimated_duration']} 分钟")
    print(f"  设计风格: {courseware['design_theme']}")
    print(f"  配色方案: {courseware['color_scheme']}")
    
    print("\n  课件结构:")
    for slide in courseware['slides']:
        print(f"\n    第{slide['slide_number']}页 [{slide['slide_type']}]")
        print(f"      标题: {slide['title']}")
        print(f"      内容要点: {len(slide['content_points'])} 条")
        print(f"      布局建议: {slide['layout_suggestion']}")
        if slide['materials_needed']:
            print(f"      所需素材: {', '.join(slide['materials_needed'])}")
        print(f"      时长: {slide['duration_minutes']} 分钟")
    
    # 5. 教学资源
    print("\n【推荐教学资源】")
    resources = result['resources']
    print(f"  找到 {resources['total_count']} 个资源")
    for i, res in enumerate(resources['resources'], 1):
        print(f"\n  [{i}] {res['resource_name']}")
        print(f"      类型: {res['resource_type']}")
        print(f"      评分: {res['rating']}/5.0")
        print(f"      使用次数: {res['usage_count']}")
    
    # ==================== 用户反馈处理 ====================
    print_separator("用户反馈处理")
    
    from models import LessonPlan, LessonPlanStatus
    from datetime import datetime
    
    # 重建LessonPlan对象
    plan = LessonPlan(
        plan_id=lesson_plan['plan_id'],
        title=lesson_plan['title'],
        subject=lesson_plan['subject'],
        education_level=lesson_plan['education_level'],
        topic=lesson_plan['topic'],
        teaching_objectives=lesson_plan['teaching_objectives'],
        teaching_procedure=lesson_plan['teaching_procedure'],
        status=LessonPlanStatus(lesson_plan['status']),
        created_at=datetime.fromisoformat(lesson_plan['created_at']),
        updated_at=datetime.fromisoformat(lesson_plan['updated_at']),
        created_by=lesson_plan['created_by'],
        version=lesson_plan['version']
    )
    
    # 提交反馈
    feedback_content = "请增加函数在经济中的应用例子，并添加一个小组讨论环节"
    print(f"用户反馈: {feedback_content}")
    
    modified_plan, evaluation, update = skill.process_feedback_loop(
        lesson_plan=plan,
        feedback_content=feedback_content,
        submitted_by="张老师"
    )
    
    print(f"\n反馈评估:")
    print(f"  决策: {evaluation.decision}")
    print(f"  置信度: {evaluation.confidence:.2f}")
    print(f"  相关性: {evaluation.relevance_score:.2f}")
    print(f"  可行性: {evaluation.feasibility_score:.2f}")
    print(f"  推理: {evaluation.reasoning}")
    
    print(f"\n教案更新:")
    print(f"  更新ID: {update.update_id}")
    print(f"  状态: {update.status.value}")
    print(f"  描述: {update.description}")
    
    if evaluation.decision == "accepted":
        print("\n更新后的教学目标:")
        for i, obj in enumerate(modified_plan.teaching_objectives, 1):
            print(f"  {i}. {obj}")
    
    # ==================== 会话摘要 ====================
    print_separator("会话摘要")
    
    summary = skill.get_session_summary()
    print(f"共执行 {summary['total_actions']} 次操作:")
    for i, action in enumerate(summary['actions'], 1):
        print(f"  {i}. {action['action']} - {action['timestamp']}")
    
    print(f"\n服务调用统计:")
    print(f"  搜索API: {summary['search_api_stats']['call_count']} 次")
    print(f"  LLM服务: {summary['llm_service_stats']['call_count']} 次")
    
    # ==================== 完成 ====================
    print_separator("完整功能演示完成")
    print("所有功能验证成功！")
    print("\n已实现完整功能:")
    print("  [OK] 完整备课流程")
    print("  [OK] 细化三维教学目标")
    print("  [OK] 详细教学过程设计")
    print("  [OK] 课件结构生成")
    print("  [OK] 教学资源搜索")
    print("  [OK] 用户反馈处理")
    print("  [OK] 教案自动修改")
    print("  [OK] 会话历史记录")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
