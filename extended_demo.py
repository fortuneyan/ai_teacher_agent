"""
扩展功能演示脚本

演示AI教师Agent的完整功能：
1. 搜索课程标准
2. 生成教案
3. 搜索教学资源
4. 用户反馈处理
5. 教案修改
"""
import sys
sys.path.insert(0, 'src')

from models import CourseBasicInfo, ResourceSearchParams
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
    print("  AI教师Agent - 智能备课助手 (扩展版本)")
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
    
    if standards:
        print("\n课标详情:")
        for i, std in enumerate(standards, 1):
            print(f"\n  [{i}] {std.standard_name}")
            print(f"      主题: {std.topic}")
            print(f"      建议课时: {std.suggested_hours}")
    
    # ==================== 步骤3: 生成教案 ====================
    print_separator("步骤3: 生成教案")
    
    lesson_plan = skill.generate_lesson_plan(
        course_info=course_info,
        standards=standards,
        requirements=["注重实际应用"]
    )
    
    print(f"教案ID: {lesson_plan.plan_id}")
    print(f"标题: {lesson_plan.title}")
    print(f"版本: v{lesson_plan.version}")
    
    print("\n教学目标:")
    for i, obj in enumerate(lesson_plan.teaching_objectives, 1):
        print(f"  {i}. {obj}")
    
    print("\n教学流程:")
    for step in lesson_plan.teaching_procedure:
        print(f"  【{step['phase']}】{step['duration']} - {step['activity']}")
    
    # ==================== 步骤4: 搜索教学资源 ====================
    print_separator("步骤4: 搜索教学资源")
    
    resource_params = ResourceSearchParams(
        keywords="函数",
        subject="数学",
        education_level="高中",
        page=1,
        page_size=10
    )
    
    resource_result = skill.search_teaching_resources(resource_params)
    
    print(f"搜索关键词: {resource_params.keywords}")
    print(f"找到 {resource_result.total_count} 个资源")
    print(f"第 {resource_result.page}/{resource_result.total_pages} 页")
    
    print("\n资源列表:")
    for i, res in enumerate(resource_result.resources, 1):
        print(f"\n  [{i}] {res['resource_name']}")
        print(f"      类型: {res['resource_type']}")
        print(f"      评分: {res['rating']}/5.0")
        print(f"      使用次数: {res['usage_count']}")
    
    # ==================== 步骤5: 用户反馈处理 ====================
    print_separator("步骤5: 用户反馈处理")
    
    feedback_content = "请增加更多实际应用的例子，并添加一些课堂互动环节"
    
    print(f"用户反馈: {feedback_content}")
    
    modified_plan, evaluation, update = skill.process_feedback_loop(
        lesson_plan=lesson_plan,
        feedback_content=feedback_content,
        submitted_by="张老师"
    )
    
    print(f"\n反馈评估结果:")
    print(f"  决策: {evaluation.decision}")
    print(f"  置信度: {evaluation.confidence:.2f}")
    print(f"  相关性: {evaluation.relevance_score:.2f}")
    print(f"  可行性: {evaluation.feasibility_score:.2f}")
    print(f"  推理: {evaluation.reasoning}")
    
    print(f"\n教案更新:")
    print(f"  更新ID: {update.update_id}")
    print(f"  状态: {update.status.value}")
    print(f"  描述: {update.description}")
    
    # ==================== 步骤6: 修改后的教案 ====================
    print_separator("步骤6: 修改后的教案")
    
    print(f"教案ID: {modified_plan.plan_id}")
    print(f"版本: v{modified_plan.version}")
    
    print("\n更新后的教学目标:")
    for i, obj in enumerate(modified_plan.teaching_objectives, 1):
        print(f"  {i}. {obj}")
    
    print("\n更新后的教学流程:")
    for step in modified_plan.teaching_procedure:
        print(f"  【{step['phase']}】{step['duration']}")
        print(f"    活动: {step['activity']}")
    
    # ==================== 步骤7: 会话摘要 ====================
    print_separator("步骤7: 会话摘要")
    
    summary = skill.get_session_summary()
    print("执行的操作:")
    for action in summary["actions"]:
        print(f"  - {action['action']} at {action['timestamp']}")
    
    print("\n服务调用统计:")
    print(f"  搜索API调用: {summary['search_api_stats']['call_count']} 次")
    print(f"  LLM服务调用: {summary['llm_service_stats']['call_count']} 次")
    
    # ==================== 完成 ====================
    print_separator("扩展功能演示完成")
    print("所有功能验证成功！")
    print("\n已实现功能:")
    print("  [OK] 课程基本信息管理")
    print("  [OK] 课程标准搜索")
    print("  [OK] 教案自动生成")
    print("  [OK] 教学资源搜索")
    print("  [OK] 用户反馈处理")
    print("  [OK] 教案自动修改")
    print("  [OK] 完整反馈循环")
    print("  [OK] 会话历史记录")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
