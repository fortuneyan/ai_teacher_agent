"""
智能备课助手演示脚本

演示完整的备课流程：
1. 输入课程名称
2. 自动搜索资源并生成教案
3. 展示教案供用户审核
4. 处理用户反馈并更新
"""

import asyncio
import sys
import os

# 添加项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from ai_teacher_agent.skills.lesson_preparation import (
    LessonPreparationAssistant,
    LessonPlan,
    UserFeedback,
    prepare_lesson,
    process_user_feedback
)


async def demo_basic_preparation():
    """演示基础备课流程"""
    print("\n" + "="*70)
    print("演示1: 基础备课流程")
    print("="*70)
    
    # 创建助手
    assistant = LessonPreparationAssistant()
    
    # 输入课程信息
    course_name = "高中数学"
    topic = "函数的概念"
    
    # 执行备课
    result = await assistant.prepare_lesson(course_name, topic)
    
    # 展示生成的教案
    lesson_plan_data = result["lesson_plan"]
    lesson_plan = LessonPlan(**lesson_plan_data)
    
    print("\n" + "="*70)
    print("生成的教案预览")
    print("="*70)
    print(assistant.format_lesson_plan_for_display(lesson_plan))
    
    return lesson_plan


async def demo_feedback_processing(lesson_plan: LessonPlan):
    """演示用户反馈处理"""
    print("\n" + "="*70)
    print("演示2: 用户反馈处理")
    print("="*70)
    
    assistant = LessonPreparationAssistant()
    
    # 模拟用户反馈场景
    feedback_scenarios = [
        {
            "name": "有效反馈 - 增加实际应用",
            "feedback": UserFeedback(
                feedback_type="modify",
                target_section="教学目标",
                content="需要增加实际应用的目标",
                suggested_change="能够运用函数概念解决实际问题，如分析手机话费套餐、气温变化等"
            )
        },
        {
            "name": "模糊反馈 - 需要澄清",
            "feedback": UserFeedback(
                feedback_type="modify",
                target_section="教学过程",
                content="我觉得不太好",
                suggested_change=None
            )
        },
        {
            "name": "无效反馈 - 不相关",
            "feedback": UserFeedback(
                feedback_type="modify",
                target_section="教学目标",
                content="这个课程可以打折销售吗？",
                suggested_change=None
            )
        },
        {
            "name": "复杂反馈 - 需要大量修改",
            "feedback": UserFeedback(
                feedback_type="modify",
                target_section="教学过程",
                content="希望重新设计整个教学过程，采用项目式学习",
                suggested_change="完全重构教学流程，以真实项目为载体，学生分组完成函数建模任务..."
            )
        }
    ]
    
    for scenario in feedback_scenarios:
        print(f"\n{'-'*70}")
        print(f"场景: {scenario['name']}")
        print(f"{'-'*70}")
        
        feedback = scenario["feedback"]
        print(f"用户反馈:")
        print(f"  类型: {feedback.feedback_type}")
        print(f"  目标: {feedback.target_section}")
        print(f"  内容: {feedback.content}")
        if feedback.suggested_change:
            print(f"  建议: {feedback.suggested_change[:50]}...")
        
        # 处理反馈
        result = await assistant.process_feedback(lesson_plan, feedback)
        
        print(f"\n处理结果:")
        print(f"  状态: {result['status']}")
        print(f"  消息: {result['message']}")
        
        if result['status'] == 'accepted':
            updated_plan = LessonPlan(**result['updated_plan'])
            print(f"  新版本: {updated_plan.version}")
            print(f"\n更新后的教学目标:")
            for obj in updated_plan.knowledge_objectives[-2:]:  # 显示最后两个（包含新增的）
                print(f"    - {obj}")


async def demo_interactive_mode():
    """交互式演示模式"""
    print("\n" + "="*70)
    print("交互式备课助手")
    print("="*70)
    
    assistant = LessonPreparationAssistant()
    
    # 获取用户输入
    print("\n请输入课程信息:")
    course_name = input("课程名称 (如: 高中数学): ").strip() or "高中数学"
    topic = input("课时主题 (如: 函数的概念): ").strip() or "函数的概念"
    
    # 执行备课
    result = await assistant.prepare_lesson(course_name, topic)
    
    lesson_plan = LessonPlan(**result["lesson_plan"])
    
    # 展示教案
    print("\n" + "="*70)
    print("教案预览")
    print("="*70)
    print(assistant.format_lesson_plan_for_display(lesson_plan))
    
    # 交互式反馈循环
    while True:
        print("\n" + "="*70)
        print("审核选项:")
        print("  1. 批准 (教案可用)")
        print("  2. 提出修改意见")
        print("  3. 查看完整教案")
        print("  4. 退出")
        print("="*70)
        
        choice = input("\n请选择 (1-4): ").strip()
        
        if choice == "1":
            print("\n✓ 教案已批准！")
            break
            
        elif choice == "2":
            print("\n请输入修改意见:")
            target = input("  目标部分 (如: 教学目标/教学重难点/教学过程): ").strip()
            content = input("  反馈内容: ").strip()
            suggestion = input("  具体修改建议 (可选): ").strip() or None
            
            feedback = UserFeedback(
                feedback_type="modify",
                target_section=target,
                content=content,
                suggested_change=suggestion
            )
            
            result = await assistant.process_feedback(lesson_plan, feedback)
            
            print(f"\n处理结果: {result['message']}")
            
            if result['status'] == 'accepted':
                lesson_plan = LessonPlan(**result['updated_plan'])
                print("\n教案已更新！")
                
        elif choice == "3":
            print("\n" + "="*70)
            print("完整教案")
            print("="*70)
            print(assistant.format_lesson_plan_for_display(lesson_plan))
            
        elif choice == "4":
            print("\n退出备课助手")
            break
        
        else:
            print("\n无效选择，请重试")


async def main():
    """主函数"""
    print("\n" + "="*70)
    print("AI教师Agent - 智能备课助手演示")
    print("="*70)
    print("\n本演示展示:")
    print("  1. 基于课程标准的智能备课")
    print("  2. 网络资源整合")
    print("  3. 用户审核与反馈处理")
    print("  4. 智能过滤不合理意见")
    
    print("\n请选择演示模式:")
    print("  1. 自动演示 (展示完整流程)")
    print("  2. 交互模式 (您可以参与审核)")
    print("  3. 仅展示反馈处理")
    
    mode = input("\n请选择 (1-3): ").strip() or "1"
    
    if mode == "1":
        # 自动演示
        lesson_plan = await demo_basic_preparation()
        await demo_feedback_processing(lesson_plan)
        
    elif mode == "2":
        # 交互模式
        await demo_interactive_mode()
        
    elif mode == "3":
        # 仅反馈处理
        # 先创建一个示例教案
        assistant = LessonPreparationAssistant()
        result = await assistant.prepare_lesson("高中数学", "函数的概念")
        lesson_plan = LessonPlan(**result["lesson_plan"])
        await demo_feedback_processing(lesson_plan)
    
    print("\n" + "="*70)
    print("演示结束")
    print("="*70)


if __name__ == "__main__":
    # 运行演示
    asyncio.run(main())
