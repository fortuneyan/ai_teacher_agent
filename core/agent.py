"""
AI_Teacher Agent 核心模块
基于Agent开发指南的最佳实践设计
"""

import json
from typing import Dict, List, Any, Optional, TYPE_CHECKING
from dataclasses import dataclass, field
from datetime import datetime
import yaml
import os

if TYPE_CHECKING:
    from .mcp_client import MCPManager, MCPToolExecutor


@dataclass
class AgentConfig:
    """Agent配置类"""

    name: str
    version: str
    description: str
    role: str
    expertise: List[str]
    communication_style: str
    output_format: str

    @classmethod
    def from_yaml(cls, config_path: str) -> "AgentConfig":
        """从YAML文件加载配置"""
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        agent_config = config.get("agent", {})
        system_prompt = config.get("agent", {}).get("system_prompt", {})

        return cls(
            name=agent_config.get("name", "AI_Teacher"),
            version=agent_config.get("version", "1.0.0"),
            description=agent_config.get("description", ""),
            role=system_prompt.get("role", "AI教学专家"),
            expertise=system_prompt.get("expertise", []),
            communication_style=system_prompt.get("communication_style", ""),
            output_format=system_prompt.get("output_format", ""),
        )


class AgentState:
    """Agent状态管理 - 对应第11章 Pipeline编排中的状态管理"""

    def __init__(self):
        self._state: Dict[str, Any] = {
            "course_name": None,
            "course_type": None,
            "target_audience": None,
            "teaching_hours": None,
            "materials": [],
            "lesson_plan": None,
            "syllabus": None,
            "ppt_content": None,
            "schedule": None,
            "current_step": 0,
            "history": [],
            "errors": [],
            "created_at": datetime.now().isoformat(),
        }

    def update(self, key: str, value: Any) -> None:
        """更新状态"""
        self._state[key] = value
        self._state["history"].append(
            {"key": key, "value": value, "timestamp": datetime.now().isoformat()}
        )

    def get(self, key: str, default: Any = None) -> Any:
        """获取状态值"""
        return self._state.get(key, default)

    def get_all(self) -> Dict[str, Any]:
        """获取完整状态"""
        return self._state.copy()

    def clear(self) -> None:
        """清空状态"""
        self._state.clear()
        self._state["created_at"] = datetime.now().isoformat()


class ContextManager:
    """
    Context管理器 - 对应第2章 Context和Prompt管理
    负责构建和管理Agent的输入上下文
    """

    def __init__(self, config: AgentConfig):
        self.config = config
        self.system_message = self._build_system_message()
        self.rag_context = []
        self.history_messages = []

    def _build_system_message(self) -> str:
        """构建System Message - 对应2.2.1四大要素"""
        template = """# 角色定位
你是一名{role}，专注于{expertise}领域的教学专家。

# 能力范围
你可以提供以下帮助：
{expertise_list}

# 沟通风格
{communication_style}

# 输出格式要求
{output_format}

# 工作流程
1. 首先了解课程基本信息（课程名称、类型、目标受众、课时）
2. 收集相关教材内容和课程标准
3. 设计详细的教学方案
4. 归纳总结教学大纲
5. 生成PPT课件
6. 制定课程进度计划

# 输出文件规范
- 教案: Markdown格式
- 教学大纲: Markdown格式
- PPT课件: Markdown大纲（可转换为PPT）
- 进度计划: JSON格式
"""
        expertise_list = "\n".join(f"- {exp}" for exp in self.config.expertise)

        return template.format(
            role=self.config.role,
            expertise="、".join(self.config.expertise),
            expertise_list=expertise_list,
            communication_style=self.config.communication_style,
            output_format=self.config.output_format,
        )

    def add_rag_context(self, context: List[Dict[str, str]]) -> None:
        """添加RAG检索的上下文 - 对应2.2.1知识层"""
        self.rag_context = context

    def add_history(self, role: str, content: str) -> None:
        """添加历史消息 - 对应2.2.1记忆层"""
        self.history_messages.append({"role": role, "content": content})

    def build_context(self, user_message: str) -> List[Dict[str, str]]:
        """
        构建完整的Context - 对应2.2.1四大要素构建流程
        按信息层级顺序: System -> RAG -> History -> User
        """
        messages = []

        # 1. System Message - 宪法层
        messages.append({"role": "system", "content": self.system_message})

        # 2. RAG Context - 知识层
        for ctx in self.rag_context:
            messages.append(
                {"role": "system", "content": f"参考知识: {ctx.get('content', '')}"}
            )

        # 3. History Message - 记忆层
        messages.extend(self.history_messages)

        # 4. User Message - 触发层
        messages.append({"role": "user", "content": user_message})

        return messages

    def clear_history(self) -> None:
        """清空历史消息"""
        self.history_messages = []


class AITeacherAgent:
    """
    AI_Teacher Agent核心类
    整合Context管理、技能编排、工具调用
    支持 MCP (Model Context Protocol) 协议接入
    """

    def __init__(
        self, config_path: str = None, mcp_manager: Optional["MCPManager"] = None
    ):
        # 加载配置
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__), "..", "config", "config.yaml"
            )

        self.config = AgentConfig.from_yaml(config_path)

        # 初始化核心组件
        self.context_manager = ContextManager(self.config)
        self.state = AgentState()

        # 技能注册表
        self.skills = {}

        # 工具注册表
        self.tools = {}

        # MCP 相关
        self.mcp_manager = mcp_manager
        self.mcp_executor = None
        if mcp_manager:
            try:
                from .mcp_client import MCPToolExecutor

                self.mcp_executor = MCPToolExecutor(mcp_manager)
            except ImportError:
                print("[WARN] MCP客户端模块不可用")

    def register_skill(self, name: str, skill_config: Dict[str, Any], executor) -> None:
        """
        注册技能 - 对应第5章 AgentSkills定义和组织
        """
        self.skills[name] = {"config": skill_config, "executor": executor}

    def register_tool(self, name: str, tool_func) -> None:
        """
        注册工具 - 对应第4章 Function Calling
        """
        self.tools[name] = tool_func

    def register_mcp_tools(self) -> List[Dict[str, Any]]:
        """
        注册所有 MCP 工具到 Agent

        Returns:
            已注册的 MCP 工具列表 (Function Calling 格式)
        """
        if self.mcp_manager is None:
            return []

        mcp_tools = self.mcp_manager.get_all_function_calls()

        # 为每个 MCP 工具创建包装器并注册
        for tool in mcp_tools:
            tool_name = tool["function"]["name"]

            def create_mcp_wrapper(name: str):
                def wrapper(**kwargs):
                    if self.mcp_executor:
                        return self.mcp_executor.execute(name, kwargs)
                    return {"error": "MCP执行器未初始化"}

                return wrapper

            self.register_tool(tool_name, create_mcp_wrapper(tool_name))

        print(f"[Agent] 已注册 {len(mcp_tools)} 个 MCP 工具")
        return mcp_tools

    def get_all_function_tools(self) -> List[Dict[str, Any]]:
        """
        获取所有可用的 Function Calling 工具

        包含内置工具和 MCP 工具
        """
        all_tools = []

        # 内置工具
        for name, func in self.tools.items():
            all_tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": name,
                        "description": func.__doc__ or f"内置工具: {name}",
                        "parameters": {"type": "object", "properties": {}},
                    },
                }
            )

        # MCP 工具
        if self.mcp_manager:
            all_tools.extend(self.mcp_manager.get_all_function_calls())

        return all_tools

    def process(self, user_input: str) -> Dict[str, Any]:
        """
        处理用户输入 - 对应第9章 规划与推理
        ReAct循环: Thought -> Action -> Observation -> ...
        """
        # 更新状态
        self.state.update("current_input", user_input)

        # 构建Context
        context = self.context_manager.build_context(user_input)

        # 调用LLM（这里需要接入实际的LLM API）
        # response = llm_call(context)

        # 模拟响应
        response = {
            "status": "success",
            "message": "AI_Teacher Agent已启动，请提供课程名称",
            "state": self.state.get_all(),
        }

        return response

    def execute_workflow(
        self, workflow_name: str, course_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        执行工作流 - 对应第11章 Pipeline编排
        """
        # 更新课程信息
        self.state.update("course_name", course_info.get("course_name"))
        self.state.update("course_type", course_info.get("course_type"))
        self.state.update("target_audience", course_info.get("target_audience"))
        self.state.update("teaching_hours", course_info.get("teaching_hours"))

        results = {}

        # 顺序执行各个技能
        for skill_name in [
            "collect_materials",
            "design_lesson",
            "outline_summary",
            "generate_ppt",
            "schedule_plan",
        ]:
            if skill_name in self.skills:
                skill = self.skills[skill_name]
                result = skill["executor"](self.state, course_info)
                results[skill_name] = result

                # 更新状态
                self.state.update(f"{skill_name}_result", result)

        return results


def create_agent(config_path: str = None) -> AITeacherAgent:
    """工厂函数：创建AI_Teacher Agent实例"""
    return AITeacherAgent(config_path)
