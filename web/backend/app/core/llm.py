"""
AI教师Agent - LLM服务

使用配置的LLM API生成内容
"""

import os
import json
from typing import Optional, Dict, Any, List
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
            return self._mock_generate(prompt)

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
            return self._mock_generate(prompt)

    def _mock_generate(self, prompt: str) -> str:
        """Mock生成（当没有配置LLM时使用）"""
        # 返回一个通用的教案模板
        return """
## 教学目标

### 知识与技能
- 理解本节课的基本概念
- 掌握相关核心原理

### 过程与方法
- 经历探究过程
- 培养分析能力

### 情感态度
- 激发学习兴趣

---

## 教学过程

### 导入（5分钟）
- 教师活动：创设情境
- 学生活动：思考回答

### 新授（25分钟）
- 教师活动：讲解概念
- 学生活动：认真听讲

### 练习（10分钟）
- 教师活动：巡视指导
- 学生活动：独立完成

### 小结（5分钟）
- 师生共同总结
"""

    async def generate_lesson_plan(
        self,
        subject: str,
        topic: str,
        grade: str,
        education_level: str,
        duration: int = 1,
    ) -> Dict[str, Any]:
        """生成教案"""
        print(f">>> generate_lesson_plan called: {subject} - {topic}")

        system_prompt = """你是一位资深的教育专家，擅长设计教案。
请根据提供的信息，生成一份完整的教案。
教案应该包含：教学目标、教学重难点、教学过程、板书设计、课后作业等部分。
请用Markdown格式输出。"""

        prompt = f"""请为{education_level}{grade}年级生成一份{subject}学科的教案。

课题：{topic}
课时：{duration}课时

请生成完整的教案内容，包括：
1. 教学目标（知识与技能、过程与方法、情感态度与价值观）
2. 教学重难点
3. 教学过程（导入、新授、练习、小结、作业）
4. 板书设计
5. 课后作业"""

        content = await self.generate(prompt, system_prompt)
        print(f">>> generate_lesson_plan completed, content length: {len(content)}")

        return {
            "content": content,
            "model": self.model if not self.use_mock else "mock",
        }


# 全局单例
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """获取LLM服务实例"""
    global _llm_service
    if _llm_service is None:
        print(">>> Creating new LLMService instance <<<")
        _llm_service = LLMService()
    return _llm_service
