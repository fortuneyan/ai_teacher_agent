"""
MCP (Model Context Protocol) 客户端模块
支持连接 MCP 服务器并将工具集成到 Agent 工具注册表中

参考 Agent开发指南 4.9节 MCP协议详解
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from pathlib import Path
import yaml
import sys


@dataclass
class MCPTool:
    """MCP工具定义"""

    name: str
    description: str
    input_schema: Dict[str, Any]
    original_name: Optional[str] = None  # MCP服务器原始工具名

    def to_function_call_format(self) -> Dict[str, Any]:
        """转换为 Function Calling 格式"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.input_schema,
            },
        }


@dataclass
class MCPServerConfig:
    """MCP服务器配置"""

    name: str
    command: str
    args: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    enabled: bool = True


class MCPClient:
    """
    MCP 客户端

    支持通过 stdio 连接 MCP 服务器，
    并将 MCP 工具转换为 Agent 可用的 Function Calling 格式
    """

    def __init__(self, server_name: str = "default"):
        self.server_name = server_name
        self.tools: Dict[str, MCPTool] = {}
        self._session = None
        self._server_process = None

    async def connect(self, config: MCPServerConfig) -> bool:
        """
        连接到 MCP 服务器

        Args:
            config: MCP服务器配置

        Returns:
            连接是否成功
        """
        try:
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client

            server_params = StdioServerParameters(
                command=config.command,
                args=config.args,
                env=config.env if config.env else None,
            )

            async with stdio_client(server_params) as (read, write):
                self._session = ClientSession(read, write)
                await self._session.initialize()

                # 获取可用工具列表
                await self._list_tools()

                print(f"[MCP] 成功连接到服务器: {config.name}")
                return True

        except ImportError:
            print("[MCP] 请安装 mcp 库: pip install mcp")
            return False
        except Exception as e:
            print(f"[MCP] 连接服务器失败: {e}")
            return False

    async def _list_tools(self) -> None:
        """列出 MCP 服务器提供的所有工具"""
        if self._session is None:
            return

        try:
            response = await self._session.list_tools()
            self.tools = {}

            for tool in response.tools:
                mcp_tool = MCPTool(
                    name=f"{self.server_name}_{tool.name}",
                    description=tool.description,
                    input_schema=tool.inputSchema,
                    original_name=tool.name,
                )
                self.tools[mcp_tool.name] = mcp_tool

        except Exception as e:
            print(f"[MCP] 获取工具列表失败: {e}")

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        调用 MCP 工具

        Args:
            tool_name: 工具名称（带服务器前缀）
            arguments: 工具参数

        Returns:
            工具执行结果
        """
        if self._session is None:
            return {"error": "MCP会话未初始化"}

        # 移除服务器前缀获取原始工具名
        original_name = tool_name
        for prefix, tools in [(f"{self.server_name}_", self.tools)]:
            if tool_name.startswith(prefix):
                original_name = (
                    self.tools.get(
                        tool_name,
                        MCPTool(name=tool_name, description="", input_schema={}),
                    ).original_name
                    or tool_name[len(prefix) :]
                )
                break

        try:
            response = await self._session.call_tool(original_name, arguments)

            # 解析响应
            if hasattr(response, "content"):
                results = []
                for content in response.content:
                    if hasattr(content, "text"):
                        results.append({"type": "text", "text": content.text})
                    elif hasattr(content, "data"):
                        results.append({"type": "data", "data": content.data})
                    elif hasattr(content, "resource"):
                        results.append(
                            {"type": "resource", "resource": content.resource}
                        )
                return results
            return {"result": str(response)}

        except Exception as e:
            return {"error": f"工具调用失败: {str(e)}"}

    def get_tools(self) -> Dict[str, MCPTool]:
        """获取所有已加载的工具"""
        return self.tools.copy()

    def get_tools_as_function_calls(self) -> List[Dict[str, Any]]:
        """获取所有工具的 Function Calling 格式"""
        return [tool.to_function_call_format() for tool in self.tools.values()]

    async def close(self) -> None:
        """关闭 MCP 连接"""
        if self._session:
            await self._session.close()
            self._session = None


class MCPManager:
    """
    MCP 管理器

    管理多个 MCP 服务器连接，提供统一的工具调用接口
    """

    def __init__(self):
        self.clients: Dict[str, MCPClient] = {}
        self._tool_registry: Dict[str, Callable] = {}

    def add_server(self, config: MCPServerConfig) -> MCPClient:
        """添加并连接 MCP 服务器"""
        client = MCPClient(server_name=config.name)
        self.clients[config.name] = client
        return client

    async def connect_all(self, configs: List[MCPServerConfig]) -> Dict[str, bool]:
        """连接所有配置的 MCP 服务器"""
        results = {}
        for config in configs:
            if config.enabled:
                client = self.add_server(config)
                results[config.name] = await client.connect(config)
        return results

    def register_tool_wrapper(
        self, server_name: str, tool_name: str, wrapper_func: Callable
    ) -> None:
        """注册工具包装器"""
        key = f"{server_name}_{tool_name}"
        self._tool_registry[key] = wrapper_func

    async def call_tool(self, full_tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        调用工具（自动路由到对应服务器）

        Args:
            full_tool_name: 完整工具名 (server_tool 格式)
            arguments: 工具参数
        """
        for server_name, client in self.clients.items():
            if full_tool_name.startswith(f"{server_name}_"):
                return await client.call_tool(full_tool_name, arguments)

        return {"error": f"未找到工具: {full_tool_name}"}

    def get_all_tools(self) -> List[MCPTool]:
        """获取所有服务器的工具"""
        all_tools = []
        for client in self.clients.values():
            all_tools.extend(client.tools.values())
        return all_tools

    def get_all_function_calls(self) -> List[Dict[str, Any]]:
        """获取所有工具的 Function Calling 格式"""
        all_calls = []
        for client in self.clients.values():
            all_calls.extend(client.get_tools_as_function_calls())
        return all_calls

    async def close_all(self) -> None:
        """关闭所有连接"""
        for client in self.clients.values():
            await client.close()


def load_mcp_config(config_path: str) -> List[MCPServerConfig]:
    """
    从配置文件加载 MCP 服务器配置

    支持 YAML 和 JSON 格式
    """
    configs = []

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            if config_path.endswith(".json"):
                data = json.load(f)
            else:
                data = yaml.safe_load(f)

        mcp_config = data.get("mcp", {}).get("servers", [])

        for server_data in mcp_config:
            config = MCPServerConfig(
                name=server_data.get("name", "unnamed"),
                command=server_data.get("command", ""),
                args=server_data.get("args", []),
                env=server_data.get("env", {}),
                enabled=server_data.get("enabled", True),
            )
            configs.append(config)

    except FileNotFoundError:
        print(f"[MCP] 配置文件不存在: {config_path}")
    except Exception as e:
        print(f"[MCP] 加载配置失败: {e}")

    return configs


def create_sync_wrapper(async_func: Callable) -> Callable:
    """
    创建同步包装器，用于在非异步环境中调用异步 MCP 函数

    Args:
        async_func: 异步函数

    Returns:
        同步包装函数
    """

    def wrapper(*args, **kwargs):
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(asyncio.run, async_func(*args, **kwargs))
                    return future.result()
            else:
                return loop.run_until_complete(async_func(*args, **kwargs))
        except RuntimeError:
            return asyncio.run(async_func(*args, **kwargs))

    return wrapper


class MCPToolExecutor:
    """
    MCP 工具执行器

    提供同步接口调用 MCP 工具
    """

    def __init__(self, manager: MCPManager):
        self.manager = manager
        self._sync_call_tool = create_sync_wrapper(manager.call_tool)

    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        执行 MCP 工具（同步接口）

        Args:
            tool_name: 工具名称
            arguments: 工具参数

        Returns:
            执行结果
        """
        return self._sync_call_tool(tool_name, arguments)


def create_mcp_manager_from_config(
    config_path: str,
) -> tuple[MCPManager, MCPToolExecutor]:
    """
    从配置文件创建 MCP 管理器

    Args:
        config_path: 配置文件路径

    Returns:
        (MCPManager, MCPToolExecutor) 元组
    """
    manager = MCPManager()
    configs = load_mcp_config(config_path)

    return manager, MCPToolExecutor(manager)


async def demo_mcp_usage():
    """MCP 使用示例"""
    print("=" * 50)
    print("MCP 客户端使用示例")
    print("=" * 50)

    # 示例1: 手动配置 MCP 服务器
    manager = MCPManager()

    # 添加文件系统服务器（示例）
    fs_config = MCPServerConfig(
        name="filesystem",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "./data"],
        enabled=True,
    )

    # 添加 Git 服务器（示例）
    git_config = MCPServerConfig(
        name="git",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-github"],
        env={"GITHUB_TOKEN": os.getenv("GITHUB_TOKEN", "")},
        enabled=True,
    )

    # 连接服务器
    results = await manager.connect_all([fs_config, git_config])
    print(f"\n连接结果: {results}")

    # 获取所有可用工具
    tools = manager.get_all_function_calls()
    print(f"\n可用工具数量: {len(tools)}")
    for tool in tools[:5]:
        print(
            f"  - {tool['function']['name']}: {tool['function']['description'][:50]}..."
        )

    # 关闭连接
    await manager.close_all()


if __name__ == "__main__":
    import os

    asyncio.run(demo_mcp_usage())
