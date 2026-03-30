"""
AI_Teacher Agent 主入口
使用示例
"""

import os
import sys
import argparse

# 获取项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="AI_Teacher Agent - 智能课程设计助手",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py --course-name "Python程序设计"
  python main.py --course-name "人工智能导论" --course-type "计算机" --hours 16
  python main.py --course-name "高等数学" --audience "大一" --weeks 8 --level "大学"
        """,
    )

    # 课程名称（必需）
    parser.add_argument(
        "--course-name", "-n", type=str, required=True, help="课程名称 (必需)"
    )

    # 课程类型
    parser.add_argument(
        "--course-type",
        "-t",
        type=str,
        default="通用",
        help="课程类型，如: 计算机基础、语言、数学等 (默认: 通用)",
    )

    # 目标受众
    parser.add_argument(
        "--target-audience",
        "-a",
        type=str,
        default="学生",
        help="目标受众，如: 大一学生、高中生、大学生等 (默认: 学生)",
    )

    # 总课时
    parser.add_argument(
        "--teaching-hours", type=int, default=16, help="总课时数 (默认: 16)"
    )

    # 周数
    parser.add_argument("--weeks", "-w", type=int, default=8, help="课程周数 (默认: 8)")

    # 教育阶段
    parser.add_argument(
        "--education-level",
        "-l",
        type=str,
        default="大学",
        choices=["小学", "初中", "高中", "大学", "研究生"],
        help="教育阶段 (默认: 大学)",
    )

    # 课程概述
    parser.add_argument("--overview", "-o", type=str, default="", help="课程概述/简介")

    # 教材版本/出版社
    parser.add_argument(
        "--textbook-edition",
        "-e",
        type=str,
        default="通用版",
        help="教材版本，如: 人教版、北师大版、2025版等 (默认: 通用版)",
    )

    # 教材出版社
    parser.add_argument(
        "--publisher",
        "-p",
        type=str,
        default="",
        help="出版社名称，如: 高等教育出版社、人民教育出版社等",
    )

    # 教材年份
    parser.add_argument(
        "--year",
        "-y",
        type=int,
        default=2025,
        help="教材年份，如: 2024、2025等 (默认: 2025)",
    )

    # 自定义搜索关键字
    parser.add_argument(
        "--search-queries",
        "-s",
        type=str,
        nargs="+",
        default=None,
        help="自定义搜索关键字（可选）",
    )

    # MCP 相关参数
    parser.add_argument(
        "--enable-mcp",
        action="store_true",
        help="启用 MCP 协议支持",
    )

    parser.add_argument(
        "--mcp-server",
        type=str,
        nargs="+",
        default=None,
        help="指定要启用的 MCP 服务器名称（默认全部）",
    )

    return parser.parse_args()


def main():
    """主函数 - 演示AI_Teacher Agent的使用"""

    # 解析命令行参数
    args = parse_args()

    # 构建课程信息
    textbook_name = f"{args.textbook_edition}"
    if args.publisher:
        textbook_name = f"{args.textbook_edition}_{args.publisher}"
    textbook_name = f"{textbook_name}_{args.year}版"

    course_info = {
        "course_name": args.course_name,
        "course_type": args.course_type,
        "target_audience": args.target_audience,
        "teaching_hours": args.teaching_hours,
        "weeks": args.weeks,
        "education_level": args.education_level,
        "overview": args.overview
        or f"本课程主要介绍{args.course_name}的基础知识和应用技巧...",
        "textbook_edition": args.textbook_edition,
        "publisher": args.publisher,
        "year": args.year,
        "textbook_name": textbook_name,
        "search_queries": args.search_queries,
    }

    print("=" * 50)
    print("AI_Teacher Agent 启动")
    print("=" * 50)

    # 1. 创建Agent实例
    from ai_teacher_agent.core.agent import create_agent

    config_path = os.path.join(
        project_root, "ai_teacher_agent", "config", "config.yaml"
    )

    # 1.1 初始化 MCP 管理器（如果启用）
    mcp_manager = None
    if args.enable_mcp:
        try:
            from ai_teacher_agent.core.mcp_client import MCPManager, load_mcp_config
            import asyncio

            mcp_configs = load_mcp_config(config_path)

            # 过滤启用的服务器
            enabled_configs = []
            for cfg in mcp_configs:
                if cfg.enabled and (
                    args.mcp_server is None or cfg.name in args.mcp_server
                ):
                    enabled_configs.append(cfg)

            if enabled_configs:
                mcp_manager = MCPManager()
                results = asyncio.run(mcp_manager.connect_all(enabled_configs))

                success_count = sum(1 for v in results.values() if v)
                print(
                    f"\n[MCP] 成功连接 {success_count}/{len(enabled_configs)} 个服务器"
                )

                for name, success in results.items():
                    status = "[OK]" if success else "[FAIL]"
                    print(f"     {status} {name}")
            else:
                print("\n[MCP] 没有可用的 MCP 服务器配置")

        except ImportError:
            print("\n[MCP] MCP 模块不可用，请安装: pip install mcp")
        except Exception as e:
            print(f"\n[MCP] 初始化失败: {e}")

    # 1.2 创建 Agent
    agent = create_agent(config_path)

    # 1.3 注册 MCP 工具（如果可用）
    if mcp_manager:
        agent.mcp_manager = mcp_manager
        try:
            from ai_teacher_agent.core.mcp_client import MCPToolExecutor

            agent.mcp_executor = MCPToolExecutor(mcp_manager)
            mcp_tools = agent.register_mcp_tools()
            if mcp_tools:
                print(f"     已注册 {len(mcp_tools)} 个 MCP 工具")
        except Exception as e:
            print(f"[WARN] MCP 工具注册失败: {e}")

    print(f"\nAgent名称: {agent.config.name}")
    print(f"Agent版本: {agent.config.version}")
    print(f"Agent描述: {agent.config.description}")

    # 2. 初始化LLM服务
    from ai_teacher_agent.core.llm_service import LLMService, LLMConfig

    # 从配置文件读取LLM配置
    import yaml

    with open(config_path, "r", encoding="utf-8") as f:
        yaml_config = yaml.safe_load(f)

    llm_config_data = yaml_config.get("llm", {})

    # 解析环境变量
    def parse_env_var(value):
        """解析环境变量格式 ${VAR_NAME}"""
        if value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]
            return os.getenv(env_var, "")
        return value

    api_key = parse_env_var(llm_config_data.get("api_key", ""))
    base_url = parse_env_var(llm_config_data.get("base_url", ""))

    llm_config = LLMConfig(
        provider=llm_config_data.get("provider", "openai"),
        model=llm_config_data.get("model", "gpt-4"),
        temperature=llm_config_data.get("temperature", 0.7),
        max_tokens=llm_config_data.get("max_tokens", 4096),
        api_key=api_key,
        base_url=base_url,
    )

    # 尝试创建LLM服务，如果API key不可用则使用mock
    try:
        llm_service = LLMService(llm_config)
        # 测试LLM连接
        test_result = llm_service.generate("你好")
        print(f"\n[OK] LLM服务已连接 (使用 {llm_config.provider}/{llm_config.model})")
        if llm_config.base_url:
            print(f"     API地址: {llm_config.base_url}")
    except Exception as e:
        print(f"\n[WARN] LLM服务不可用，将使用模拟数据: {str(e)[:50]}")
        llm_config.provider = "mock"
        llm_service = LLMService(llm_config)

    # 3. 注册技能
    from ai_teacher_agent.skills.collect_materials import CollectMaterialsSkill
    from ai_teacher_agent.skills.design_lesson import DesignLessonSkill
    from ai_teacher_agent.skills.outline_summary import OutlineSummarySkill
    from ai_teacher_agent.skills.generate_ppt import GeneratePPTSkill
    from ai_teacher_agent.skills.schedule_plan import SchedulePlanSkill

    # 创建技能实例（传入LLM服务）
    skills = {
        "collect_materials": CollectMaterialsSkill(),
        "design_lesson": DesignLessonSkill(llm_service=llm_service),
        "outline_summary": OutlineSummarySkill(llm_service=llm_service),
        "generate_ppt": GeneratePPTSkill(llm_service=llm_service),
        "schedule_plan": SchedulePlanSkill(llm_service=llm_service),
    }

    # 注册技能到Agent
    for name, skill in skills.items():
        agent.register_skill(
            name=name,
            skill_config={"metadata": skill.get_metadata().__dict__},
            executor=lambda ctx, p, s=skill: s.execute(None, ctx),
        )

    print(f"\n已注册技能: {', '.join(skills.keys())}")

    # 3. 显示课程信息
    print(f"\n课程信息:")
    print(f"  - 课程名称: {course_info['course_name']}")
    print(f"  - 课程类型: {course_info['course_type']}")
    print(f"  - 目标受众: {course_info['target_audience']}")
    print(f"  - 总课时: {course_info['teaching_hours']}")
    print(f"  - 周数: {course_info['weeks']}")
    print(f"  - 教育阶段: {course_info['education_level']}")
    print(f"  - 教材版本: {course_info['textbook_edition']}")
    print(f"  - 出版社: {course_info['publisher'] or '未指定'}")
    print(f"  - 教材年份: {course_info['year']}")
    print(f"  - 教材名称: {course_info['textbook_name']}")

    if course_info.get("search_queries"):
        print(f"  - 搜索关键字: {', '.join(course_info['search_queries'])}")

    # 4. 执行完整工作流
    print("\n" + "=" * 50)
    print("开始执行课程设计工作流")
    print("=" * 50)

    # 使用Pipeline执行
    from ai_teacher_agent.core.pipeline import Pipeline, PipelineNode

    pipeline = Pipeline("course_design")

    # 添加节点
    pipeline.add_node(
        PipelineNode(
            name="collect_materials",
            description="收集教材内容",
            skill_name="collect_materials",
            executor=lambda ctx, prev: skills["collect_materials"].execute(None, ctx),
        )
    )

    pipeline.add_node(
        PipelineNode(
            name="design_lesson",
            description="设计教案",
            skill_name="design_lesson",
            executor=lambda ctx, prev: skills["design_lesson"].execute(None, ctx),
            dependencies=["collect_materials"],
        )
    )

    pipeline.add_node(
        PipelineNode(
            name="outline_summary",
            description="归纳教学大纲",
            skill_name="outline_summary",
            executor=lambda ctx, prev: skills["outline_summary"].execute(None, ctx),
            dependencies=["design_lesson"],
        )
    )

    pipeline.add_node(
        PipelineNode(
            name="generate_ppt",
            description="生成PPT课件",
            skill_name="generate_ppt",
            executor=lambda ctx, prev: skills["generate_ppt"].execute(None, ctx),
            dependencies=["outline_summary"],
        )
    )

    pipeline.add_node(
        PipelineNode(
            name="schedule_plan",
            description="制定进度计划",
            skill_name="schedule_plan",
            executor=lambda ctx, prev: skills["schedule_plan"].execute(None, ctx),
            dependencies=["generate_ppt"],
        )
    )

    # 执行Pipeline
    result = pipeline.execute(course_info)

    # 5. 显示结果
    print("\n" + "=" * 50)
    print("工作流执行完成")
    print("=" * 50)

    print("\n生成的文件:")
    for node_name, status in result["status"].items():
        print(f"  - {node_name}: {status}")

    output_dir = (
        f"./output/{course_info['course_name']}/{course_info['textbook_name']}/"
    )
    print(f"\n输出文件目录: {output_dir}")
    print("  - textbooks/      : 教材内容")
    print("  - curriculum_standards/ : 课程标准")
    print("  - lesson_plans/   : 教案")
    print("  - syllabus/       : 教学大纲")
    print("  - ppt/            : PPT课件")
    print("  - schedules/      : 进度计划(JSON)")

    print("\n" + "=" * 50)
    print("AI_Teacher Agent 运行完成")
    print("=" * 50)

    # 清理 MCP 连接
    if mcp_manager:
        try:
            import asyncio

            asyncio.run(mcp_manager.close_all())
            print("\n[MCP] 已关闭所有连接")
        except Exception:
            pass

    return result


if __name__ == "__main__":
    main()
