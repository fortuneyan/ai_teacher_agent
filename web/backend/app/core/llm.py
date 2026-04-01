"""
AI教师Agent - LLM服务

使用配置的LLM API生成内容
"""

import os
import json
from typing import Optional
from openai import AsyncOpenAI


class LLMService:
    """LLM服务类"""

    def __init__(self):
        from app.core.config import settings

        self.api_key = settings.LLM_API_KEY
        self.api_base = settings.LLM_API_BASE
        self.model = settings.LLM_MODEL

        print(f"========== LLM Config ==========")
        print(f"API_KEY: {self.api_key[:10] if self.api_key else 'None'}...")
        print(f"API_BASE: {self.api_base}")
        print(f"MODEL: {self.model}")
        print(f"================================")

        # 如果没有配置API，使用Mock
        if not self.api_key or self.api_key == "mock":
            self.use_mock = True
            print(">>> Using MOCK LLM Service <<<")
        else:
            self.use_mock = False
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.api_base,
            )
            print(">>> Using REAL LLM Service <<<")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """
        调用LLM生成内容

        Args:
            prompt: 用户提示
            system_prompt: 系统提示
            temperature: 温度参数
            max_tokens: 最大token数

        Returns:
            生成的内容
        """
        if self.use_mock:
            print("========== Using Mock LLM ==========")
            return f"[Mock回复] 你发送的prompt长度: {len(prompt)}字符"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        print(f"========== LLM API Request ==========")
        print(f"Model: {self.model}")
        print(f"API Base: {self.api_base}")
        print(f"Messages: {json.dumps(messages, ensure_ascii=False, indent=2)}")
        print(f"Temperature: {temperature}, Max Tokens: {max_tokens}")

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content
            print(f"========== LLM API Response ==========")
            print(f"Response length: {len(content)} characters")
            print(f"Response preview: {content[:300]}...")
            print(f"Usage: {response.usage}")
            print(f"======================================")
            return content
        except Exception as e:
            logger.error(f"LLM调用失败: {e}")
            return f"[Mock回复] 你发送的prompt长度: {len(prompt)}字符"


# 全局单例
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """获取LLM服务实例"""
    global _llm_service
    if _llm_service is None:
        print(">>> Creating new LLMService instance <<<")
        _llm_service = LLMService()
    return _llm_service
