"""
MVP版本演示脚本

演示智能备课助手的核心功能：
1. 搜索课程标准
2. 生成教案
"""
import sys
sys.path.insert(0, 'src')

from models import CourseBasicInfo, LessonPlanStatus
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
    print("  AI教师Agent - 智能备课助手 (MVP版本)")
    print("=" * 60)
    
    # 初始化技能
    skill = LessonPreparationSkill()
    
    # ==================== 步骤1: 输入课程信息 ====================
    print_separator("步骤1: 输入课程信息")
    
    course_info = CourseBasicInfo(
        education_level="高中",
        subject="数学",
        topic="函数的概念",
        grade="高一",
        textbook_version="人教版",
        suggested_hours=4
    )
    
    print("课程基本信息:")
    print_json(course_info.to_dict())
    
    # ==================== 步骤2: 搜索课程标准 ====================
    print_separator("步骤2: 搜索课程标准")
    
    search_result, standards = skill.search_curriculum_standards(course_info)
    
    print(f"搜索查询: {search_result.query}")
    print(f"找到 {search_result.total_count} 条相关课标")
    print(f"搜索耗时: {search_result.search_time_ms}ms")
    
    if standards:
        print("\n课标详情:")
        for i, std in enumerate(standards, 1):
            print(f"\n  [{i}] {std.standard_name}")
            print(f"      主题: {std.topic}")
            print(f"      建议课时: {std.suggested_hours}")
            print(f"      相关性: {std.relevance_score:.2f}")
            print(f"      内容要求:")
            for req in std.content_requirements[:2]:
                print(f"        - {req}")
    else:
        print("未找到相关课标")
        return
    
    # ==================== 步骤3: 分析课标 ====================
    print_separator("步骤3: 分析课标要求")
    
    analysis = skill.analyze_standards(standards)
    print("分析结果:")
    print_json(analysis)
    
    # ==================== 步骤4: 生成教案 ====================
    print_separator("步骤4: 生成教案")
    
    lesson_plan = skill.generate_lesson_plan(
        course_info=course_info,
        standards=standards,
        requirements=["注重实际应用", "增加互动环节"]
    )
    
    print(f"教案ID: {lesson_plan.plan_id}")
    print(f"标题: {lesson_plan.title}")
    print(f"状态: {lesson_plan.status.value}")
    print(f"版本: v{lesson_plan.version}")
    
    print("\n教学目标:")
    for i, obj in enumerate(lesson_plan.teaching_objectives, 1):
        print(f"  {i}. {obj}")
    
    print("\n教学流程:")
    for step in lesson_plan.teaching_procedure:
        print(f"\n  【{step['phase']}】{step['duration']}")
        print(f"    活动: {step['activity']}")
        print(f"    方法: {step['method']}")
        print(f"    目的: {step['purpose']}")
    
    # ==================== 步骤5: 会话摘要 ====================
    print_separator("步骤5: 会话摘要")
    
    summary = skill.get_session_summary()
    print("执行的操作:")
    for action in summary["actions"]:
        print(f"  - {action['action']} at {action['timestamp']}")
    
    print("\n服务调用统计:")
    print(f"  搜索API调用: {summary['search_api_stats']['call_count']} 次")
    print(f"  LLM服务调用: {summary['llm_service_stats']['call_count']} 次")
    
    # ==================== 完成 ====================
    print_separator("MVP演示完成")
    print("核心功能验证成功！")
    print("\n已实现功能:")
    print("  [OK] 课程基本信息管理")
    print("  [OK] 课程标准搜索")
    print("  [OK] 课标分析")
    print("  [OK] 教案自动生成")
    print("  [OK] 会话历史记录")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
