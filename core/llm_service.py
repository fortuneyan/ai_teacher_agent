"""
LLM 调用模块
支持 OpenAI、Anthropic 等多种 LLM 提供商
"""

import os
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class LLMConfig:
    """LLM配置类"""

    provider: str = "openai"
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 4096
    api_key: str = ""
    base_url: str = ""  # 支持自定义API地址（如本地部署或其他兼容API）


class LLMClient:
    """LLM客户端基类"""

    def __init__(self, config: LLMConfig):
        self.config = config

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """发送聊天请求"""
        raise NotImplementedError


class OpenAIClient(LLMClient):
    """OpenAI LLM客户端"""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.client = None

    def _get_client(self):
        """获取OpenAI客户端"""
        if self.client is None:
            try:
                from openai import OpenAI

                # 构建初始化参数
                init_kwargs = {
                    "api_key": self.config.api_key or os.getenv("OPENAI_API_KEY"),
                }

                # 如果配置了base_url，添加自定义API地址
                if self.config.base_url:
                    init_kwargs["base_url"] = self.config.base_url

                # 如果是本地部署，禁用安全检查
                if self.config.base_url and not self.config.api_key:
                    init_kwargs["api_key"] = "dummy"

                self.client = OpenAI(**init_kwargs)
            except ImportError:
                raise ImportError("请安装 openai 库: pip install openai")
        return self.client

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """发送聊天请求"""
        client = self._get_client()

        response = client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=kwargs.get("temperature", self.config.temperature),
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
        )

        return response.choices[0].message.content


class AnthropicClient(LLMClient):
    """Anthropic LLM客户端"""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.client = None

    def _get_client(self):
        """获取Anthropic客户端"""
        if self.client is None:
            try:
                import anthropic

                self.client = anthropic.Anthropic(
                    api_key=self.config.api_key or os.getenv("ANTHROPIC_API_KEY")
                )
            except ImportError:
                raise ImportError("请安装 anthropic 库: pip install anthropic")
        return self.client

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """发送聊天请求"""
        client = self._get_client()

        # 转换消息格式
        system_message = ""
        filtered_messages = []
        for msg in messages:
            if msg.get("role") == "system" and "参考知识" not in msg.get("content", ""):
                system_message = msg.get("content", "")
            else:
                filtered_messages.append(msg)

        response = client.messages.create(
            model=self.config.model,
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            temperature=kwargs.get("temperature", self.config.temperature),
            system=system_message,
            messages=filtered_messages,
        )

        return response.content[0].text


class MockLLMClient(LLMClient):
    """模拟LLM客户端（用于测试）"""

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """返回模拟响应"""
        last_message = messages[-1] if messages else {}
        user_input = last_message.get("content", "")

        return f"[模拟响应] 已处理: {user_input[:50]}..."


def create_llm_client(config: LLMConfig) -> LLMClient:
    """工厂函数：创建LLM客户端"""
    providers = {
        "openai": OpenAIClient,
        "anthropic": AnthropicClient,
        "mock": MockLLMClient,
    }

    client_class = providers.get(config.provider, MockLLMClient)
    return client_class(config)


class LLMService:
    """LLM服务类 - 封装LLM调用逻辑"""

    def __init__(self, config: LLMConfig):
        self.client = create_llm_client(config)
        self.config = config

    def generate(self, prompt: str, system_prompt: str = "", **kwargs) -> str:
        """生成内容"""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        try:
            return self.client.chat(messages, **kwargs)
        except Exception as e:
            print(f"LLM调用失败: {e}")
            return f"[LLM调用失败] {str(e)}"

    def generate_json(
        self, prompt: str, system_prompt: str = "", **kwargs
    ) -> Dict[str, Any]:
        """生成JSON格式内容"""
        json_prompt = f"{prompt}\n\n请以JSON格式返回结果，不要包含其他内容。"

        result = self.generate(json_prompt, system_prompt, **kwargs)

        # 尝试解析JSON
        try:
            # 尝试提取JSON
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]

            return json.loads(result)
        except json.JSONDecodeError:
            return {"error": "JSON解析失败", "raw": result}

    def generate_structured(
        self, prompt: str, schema: Dict[str, Any], system_prompt: str = "", **kwargs
    ) -> Dict[str, Any]:
        """生成结构化内容"""
        schema_prompt = f"{prompt}\n\n请按照以下JSON Schema返回结果:\n{json.dumps(schema, ensure_ascii=False, indent=2)}"

        return self.generate_json(schema_prompt, system_prompt, **kwargs)
