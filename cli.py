"""
AI教师Agent - 命令行交互界面

提供简单的交互式备课助手
"""
import sys
import uuid
sys.path.insert(0, 'src')

from models import CourseBasicInfo, ResourceSearchParams
from skills import LessonPreparationSkill


class LessonPreparationCLI:
    """备课助手CLI"""
    
    def __init__(self):
        self.skill = LessonPreparationSkill()
        self.current_plan = None
        self.course_info = None
    
    def print_header(self, title):
        """打印标题"""
        print("\n" + "=" * 50)
        print(f"  {title}")
        print("=" * 50)
    
    def print_menu(self):
        """打印主菜单"""
        self.print_header("AI教师Agent - 智能备课助手")
        print("\n  [1] 新建备课")
        print("  [2] 查看当前教案")
        print("  [3] 搜索教学资源")
        print("  [4] 提交反馈")
        print("  [5] 查看会话历史")
        print("  [6] 测试/讲解模块")
        print("  [0] 退出")
        print("\n" + "-" * 50)
    
    def get_input(self, prompt, default=None):
        """获取用户输入"""
        if default:
            full_prompt = f"{prompt} (默认: {default}): "
        else:
            full_prompt = f"{prompt}: "
        
        value = input(full_prompt).strip()
        return value if value else default
    
    def create_lesson(self):
        """创建新教案"""
        self.print_header("新建备课")
        
        # 获取课程信息
        education_level = self.get_input("学段", "高中")
        subject = self.get_input("学科", "数学")
        topic = self.get_input("主题", "函数的概念")
        grade = self.get_input("年级", "高一")
        hours = int(self.get_input("建议课时", "4"))
        
        # 创建课程信息
        self.course_info = CourseBasicInfo(
            education_level=education_level,
            subject=subject,
            topic=topic,
            grade=grade,
            suggested_hours=hours
        )
        
        print(f"\n正在为您准备《{topic}》的教案...")
        
        # 搜索课标
        print("  正在搜索课程标准...")
        search_result, standards = self.skill.search_curriculum_standards(self.course_info)
        print(f"  找到 {len(standards)} 条相关课标")
        
        # 生成教案
        print("  正在生成教案...")
        self.current_plan = self.skill.generate_lesson_plan(
            course_info=self.course_info,
            standards=standards
        )
        
        print(f"\n教案生成完成!")
        print(f"  教案ID: {self.current_plan.plan_id}")
        print(f"  标题: {self.current_plan.title}")
        self.show_plan_summary()
    
    def show_plan_summary(self):
        """显示教案摘要"""
        if not self.current_plan:
            print("\n  当前没有教案，请先新建备课")
            return
        
        print("\n  教学目标:")
        for i, obj in enumerate(self.current_plan.teaching_objectives, 1):
            print(f"    {i}. {obj}")
        
        print("\n  教学流程:")
        for step in self.current_plan.teaching_procedure:
            print(f"    【{step['phase']}】{step['duration']}")
    
    def search_resources(self):
        """搜索教学资源"""
        self.print_header("搜索教学资源")
        
        if not self.course_info:
            print("  请先新建备课")
            return
        
        keywords = self.get_input("关键词", self.course_info.topic)
        
        params = ResourceSearchParams(
            keywords=keywords,
            subject=self.course_info.subject,
            education_level=self.course_info.education_level
        )
        
        print(f"\n正在搜索资源...")
        result = self.skill.search_teaching_resources(params)
        
        print(f"\n找到 {result.total_count} 个资源:")
        for i, res in enumerate(result.resources, 1):
            print(f"\n  [{i}] {res['resource_name']}")
            print(f"      类型: {res['resource_type']}")
            print(f"      评分: {res['rating']}/5.0")
    
    def submit_feedback(self):
        """提交反馈"""
        self.print_header("提交反馈")
        
        if not self.current_plan:
            print("  当前没有教案，请先新建备课")
            return
        
        print("\n  当前教案:")
        self.show_plan_summary()
        
        print("\n  请输入您的修改意见:")
        feedback = input("  > ").strip()
        
        if not feedback:
            print("  反馈内容不能为空")
            return
        
        print(f"\n  正在处理反馈...")
        modified_plan, evaluation, update = self.skill.process_feedback_loop(
            lesson_plan=self.current_plan,
            feedback_content=feedback,
            submitted_by="用户"
        )
        
        print(f"\n  反馈评估: {evaluation.decision}")
        print(f"  置信度: {evaluation.confidence:.2f}")
        
        if evaluation.decision == "accepted":
            self.current_plan = modified_plan
            print("\n  教案已更新!")
            self.show_plan_summary()
        else:
            print("\n  反馈未被采纳，教案保持不变")
    
    def show_history(self):
        """显示会话历史"""
        self.print_header("会话历史")
        
        summary = self.skill.get_session_summary()
        
        if not summary["actions"]:
            print("  暂无操作记录")
            return
        
        print(f"\n  共 {summary['total_actions']} 次操作:")
        for i, action in enumerate(summary["actions"], 1):
            print(f"  {i}. {action['action']} - {action['timestamp']}")
        
        print(f"\n  服务调用统计:")
        print(f"    搜索API: {summary['search_api_stats']['call_count']} 次")
        print(f"    LLM服务: {summary['llm_service_stats']['call_count']} 次")
    
    def launch_assessment_module(self):
        """启动测试/讲解模块"""
        self.print_header("测试/讲解模块")
        print("\n  正在启动测试/讲解模块...")
        
        try:
            import cli_assessment
            assessment_cli = cli_assessment.AssessmentCLI()
            assessment_cli.run()
        except Exception as e:
            print(f"  启动失败: {e}")
            print("  请确保测试/讲解模块已正确安装")
    
    def run(self):
        """运行CLI"""
        while True:
            self.print_menu()
            choice = input("  请选择: ").strip()
            
            if choice == "1":
                self.create_lesson()
            elif choice == "2":
                self.print_header("当前教案")
                self.show_plan_summary()
            elif choice == "3":
                self.search_resources()
            elif choice == "4":
                self.submit_feedback()
            elif choice == "5":
                self.show_history()
            elif choice == "6":
                self.launch_assessment_module()
            elif choice == "0":
                print("\n  感谢使用，再见!")
                break
            else:
                print("\n  无效选择，请重试")
            
            input("\n  按回车继续...")


def main():
    """主函数"""
    print("\n" + "=" * 50)
    print("  欢迎使用AI教师Agent - 智能备课助手")
    print("=" * 50)
    
    cli = LessonPreparationCLI()
    
    # 询问是否使用演示模式
    print("\n  [1] 交互模式 - 手动输入课程信息")
    print("  [2] 演示模式 - 自动运行示例")
    mode = input("\n  请选择模式: ").strip()
    
    if mode == "2":
        # 运行演示
        print("\n  启动演示模式...")
        import extended_demo
        extended_demo.main()
    else:
        # 启动交互模式
        cli.run()


if __name__ == "__main__":
    main()
