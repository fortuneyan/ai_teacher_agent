"""
skills._base.soft_executor - Soft Skill 执行器

将 SKILL.md 转换为 LLM 可执行的提示并执行。
"""

import json
import logging
from typing import Dict, Any, Optional

from .metadata import SkillType
from .registry import SkillRegistry

logger = logging.getLogger(__name__)


class SoftSkillExecutor:
    """
    Soft Skill 执行器
    
    将 Soft Skill (SKILL.md) 转换为 LLM 提示并执行。
    
    使用方式:
    ```python
    executor = SoftSkillExecutor(llm_service=my_llm)
    
    result = await executor.execute("quick-lesson", {
        "topic": "光的折射",
        "duration": 40
    })
    ```
    """
    
    # 默认系统提示
    DEFAULT_SYSTEM_PROMPT = """你是一个专业的教学助手，擅长根据用户需求完成各种教学相关的任务。

执行技能时请遵循以下原则:
1. 仔细阅读技能说明，理解任务目标
2. 根据输入参数完成任务
3. 返回结构化的结果
4. 如果遇到无法完成的情况，明确说明原因

返回格式要求:
- 如果是文本内容，直接返回
- 如果是结构化数据，使用 JSON 格式
- 包含执行状态和结果
"""
    
    def __init__(self, llm_service):
        """
        初始化执行器
        
        Args:
            llm_service: LLM 服务实例，必须支持 generate() 方法
        """
        self.llm_service = llm_service
    
    async def execute(self, skill_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行 Soft Skill
        
        Args:
            skill_name: 技能名称
            context: 执行上下文
            
        Returns:
            执行结果
        """
        skill_data = SkillRegistry.get_soft(skill_name)
        
        if not skill_data:
            return {
                "status": "error",
                "message": f"Soft skill '{skill_name}' not found"
            }
        
        # 构建执行提示
        prompt = self._build_execution_prompt(skill_data, context)
        
        # 调用 LLM
        try:
            response = await self.llm_service.generate(
                prompt,
                system=self.DEFAULT_SYSTEM_PROMPT
            )
            
            # 解析结果
            result = self._parse_response(response, skill_data)
            return result
            
        except Exception as e:
            logger.exception(f"Error executing soft skill: {skill_name}")
            return {
                "status": "error",
                "message": str(e),
                "skill": skill_name
            }
    
    def _build_execution_prompt(self, skill_data: Dict[str, Any], context: Dict[str, Any]) -> str:
        """
        构建执行提示
        
        Args:
            skill_data: 技能数据
            context: 执行上下文
            
        Returns:
            构建好的提示文本
        """
        sections = []
        
        # 标题
        sections.append(f"# 执行技能: {skill_data.get('display_name', skill_data['name'])}")
        
        # 技能描述
        description = skill_data.get("description", "")
        if description:
            sections.append(f"\n## 技能描述\n{description}")
        
        # 参数说明
        parameters = skill_data.get("parameters", [])
        if parameters:
            sections.append("\n## 输入参数")
            for param in parameters:
                param_name = param.get("name", "")
                param_type = param.get("type", "string")
                required = param.get("required", False)
                default = param.get("default")
                param_desc = param.get("description", "")
                
                req_str = "必填" if required else "可选"
                default_str = f"，默认: {default}" if default is not None else ""
                
                sections.append(f"- **{param_name}** ({param_type}, {req_str}{default_str}): {param_desc}")
        
        # 用户提供的参数
        sections.append("\n## 当前任务参数")
        sections.append(f"```json\n{json.dumps(context, ensure_ascii=False, indent=2)}\n```")
        
        # 技能内容/指南
        content = skill_data.get("content", "")
        if content:
            sections.append(f"\n## 技能执行指南\n{content}")
        
        # 输出要求
        sections.append("\n---\n请根据以上信息执行任务，返回结果。")
        
        return "\n".join(sections)
    
    def _parse_response(self, response: str, skill_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析 LLM 响应
        
        尝试从响应中提取结构化数据。
        
        Args:
            response: LLM 原始响应
            skill_data: 技能数据
            
        Returns:
            解析后的结果
        """
        # 尝试解析 JSON
        if "```json" in response:
            json_match = response.split("```json")[1].split("```")[0].strip()
            try:
                data = json.loads(json_match)
                return {
                    "status": "success",
                    "data": data,
                    "raw_output": response
                }
            except json.JSONDecodeError:
                pass
        
        if response.strip().startswith("{"):
            try:
                data = json.loads(response.strip())
                return {
                    "status": "success",
                    "data": data,
                    "raw_output": response
                }
            except json.JSONDecodeError:
                pass
        
        # 返回原始文本
        return {
            "status": "success",
            "data": {
                "content": response,
                "format": "text"
            },
            "raw_output": response
        }


class SoftSkillTemplate:
    """
    Soft Skill 模板生成器
    
    用于创建新的 SKILL.md 文件。
    """
    
    @staticmethod
    def generate(
        name: str,
        display_name: str,
        description: str,
        parameters: list = None,
        triggers: list = None,
        content: str = None
    ) -> str:
        """
        生成 SKILL.md 内容
        
        Args:
            name: 技能名称 (kebab-case)
            display_name: 显示名称
            description: 简短描述
            parameters: 参数列表
            triggers: 触发词列表
            content: Markdown 正文
            
        Returns:
            SKILL.md 格式的字符串
        """
        lines = [
            "---",
            f'name: "{name}"',
            f'version: "1.0.0"',
            f'display_name: "{display_name}"',
            f'description: "{description}"',
            f'category: "custom"',
            f'author: "custom"',
        ]
        
        # 触发词
        if triggers:
            lines.append("triggers:")
            for trigger in triggers:
                lines.append(f'  - "{trigger}"')
        
        # 参数
        if parameters:
            lines.append("parameters:")
            for param in parameters:
                lines.append(f'  - name: {param.get("name")}')
                lines.append(f'    type: {param.get("type", "string")}')
                lines.append(f'    required: {str(param.get("required", False)).lower()}')
                if "default" in param:
                    lines.append(f'    default: {param["default"]}')
                if "description" in param:
                    lines.append(f'    description: "{param["description"]}"')
        
        lines.append("---")
        
        # 正文
        lines.append("")
        lines.append(f"# {display_name}")
        lines.append("")
        lines.append("## 能力描述")
        lines.append("")
        lines.append(description)
        
        if content:
            lines.append("")
            lines.append(content)
        
        return "\n".join(lines)
