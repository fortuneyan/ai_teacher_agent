"""
LLM服务 Mock

模拟大语言模型服务
"""
import time
import random
from typing import List, Dict, Any, Optional
from datetime import datetime


class MockLLMService:
    """
    模拟LLM服务
    
    提供教案生成、分析等功能的模拟实现
    """
    
    def __init__(self):
        self.call_count = 0
        self.last_call_time = None
    
    def generate_lesson_plan(
        self,
        course_info: Dict[str, Any],
        standards: List[Dict[str, Any]],
        requirements: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        模拟生成教案
        
        Args:
            course_info: 课程基本信息
            standards: 课程标准列表
            requirements: 额外要求
            
        Returns:
            生成的教案数据
        """
        # 模拟处理时间
        time.sleep(random.uniform(0.5, 1.5))
        
        subject = course_info.get("subject", "数学")
        topic = course_info.get("topic", "未知主题")
        education_level = course_info.get("education_level", "高中")
        
        # 生成教学目标
        objectives = self._generate_objectives(subject, topic, standards)
        
        # 生成教学流程
        procedure = self._generate_procedure(subject, topic, education_level)
        
        self.call_count += 1
        self.last_call_time = datetime.now()
        
        return {
            "title": f"{education_level}{subject}《{topic}》教学设计",
            "subject": subject,
            "education_level": education_level,
            "topic": topic,
            "teaching_objectives": objectives,
            "teaching_procedure": procedure,
            "generated_at": datetime.now().isoformat(),
            "model": "mock-llm-v1",
            "token_usage": {
                "prompt_tokens": random.randint(500, 1000),
                "completion_tokens": random.randint(800, 1500),
                "total_tokens": random.randint(1300, 2500)
            }
        }
    
    def _generate_objectives(
        self,
        subject: str,
        topic: str,
        standards: List[Dict[str, Any]]
    ) -> List[str]:
        """生成教学目标"""
        objectives = []
        
        # 知识目标
        objectives.append(f"理解{topic}的基本概念和原理")
        objectives.append(f"掌握{topic}的基本方法和应用")
        
        # 能力目标
        objectives.append(f"能够运用{topic}解决实际问题")
        objectives.append("培养分析和推理能力")
        
        # 素养目标
        if subject == "数学":
            objectives.append("发展数学抽象和逻辑推理素养")
        elif subject == "物理":
            objectives.append("培养科学思维和物理观念")
        
        return objectives
    
    def _generate_procedure(
        self,
        subject: str,
        topic: str,
        education_level: str
    ) -> List[Dict[str, Any]]:
        """生成教学流程"""
        return [
            {
                "step": 1,
                "phase": "导入",
                "duration": "5分钟",
                "activity": f"通过生活中的实例引入{topic}",
                "method": "情境导入法",
                "purpose": "激发学习兴趣，建立知识联系"
            },
            {
                "step": 2,
                "phase": "新授",
                "duration": "20分钟",
                "activity": f"讲解{topic}的核心概念和原理",
                "method": "讲授法与探究法结合",
                "purpose": "构建知识体系，理解核心概念"
            },
            {
                "step": 3,
                "phase": "练习",
                "duration": "15分钟",
                "activity": "典型例题讲解与学生练习",
                "method": "讲练结合",
                "purpose": "巩固知识，掌握方法"
            },
            {
                "step": 4,
                "phase": "小结",
                "duration": "5分钟",
                "activity": f"总结{topic}的重点和难点",
                "method": "师生共同归纳",
                "purpose": "梳理知识，形成网络"
            }
        ]
    
    def analyze_standards(
        self,
        standards: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        模拟分析课标要求
        
        Args:
            standards: 课程标准列表
            
        Returns:
            分析结果
        """
        time.sleep(random.uniform(0.3, 0.8))
        
        all_requirements = []
        all_competencies = []
        total_hours = 0
        
        for std in standards:
            all_requirements.extend(std.get("content_requirements", []))
            all_competencies.extend(std.get("competency_requirements", []))
            total_hours += std.get("suggested_hours", 0)
        
        self.call_count += 1
        self.last_call_time = datetime.now()
        
        return {
            "summary": f"共{len(standards)}条课标要求，建议{total_hours}课时",
            "key_points": all_requirements[:5] if all_requirements else ["掌握核心概念"],
            "competency_focus": list(set(all_competencies))[:3] if all_competencies else ["基础知识"],
            "difficulty_level": "中等",
            "prerequisite_knowledge": ["相关前置知识"],
            "analyzed_at": datetime.now().isoformat()
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """获取Mock服务统计信息"""
        return {
            "call_count": self.call_count,
            "last_call_time": self.last_call_time.isoformat() if self.last_call_time else None
        }
