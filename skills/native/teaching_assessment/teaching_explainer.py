"""
教学讲解器 - 提供多种类型的教学讲解

功能：
1. 概念讲解
2. 例题讲解
3. 方法讲解
4. 拓展讲解
"""

import uuid
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum


class ExplanationType(Enum):
    """讲解类型"""
    CONCEPT = "概念讲解"
    EXAMPLE = "例题讲解"
    METHOD = "方法讲解"
    EXTENSION = "拓展讲解"


class Difficulty(Enum):
    """难度等级"""
    EASY = "基础"
    MEDIUM = "中等"
    HARD = "提高"


@dataclass
class Explanation:
    """讲解内容"""
    explanation_id: str
    explanation_type: str
    title: str
    topic: str
    
    # 讲解内容
    content: str  # 主要讲解内容
    key_points: List[str] = field(default_factory=list)  # 关键点
    examples: List[Dict[str, str]] = field(default_factory=list)  # 例子
    common_mistakes: List[str] = field(default_factory=list)  # 常见错误
    tips: List[str] = field(default_factory=list)  # 技巧提示
    
    # 元数据
    difficulty: str = "中等"
    duration_minutes: int = 10
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class TeachingExplainer:
    """
    教学讲解器
    
    使用示例：
        explainer = TeachingExplainer()
        
        # 概念讲解
        concept = explainer.explain_concept(
            topic="函数",
            concept_name="函数的概念",
            difficulty=Difficulty.MEDIUM
        )
        
        # 例题讲解
        example = explainer.explain_example(
            topic="函数",
            example_problem="已知f(x)=2x+1，求f(3)",
            solution="代入计算即可"
        )
    """
    
    def __init__(self, llm_service=None):
        self.llm_service = llm_service
    
    # ==================== 概念讲解 ====================
    
    def explain_concept(
        self,
        topic: str,
        concept_name: str,
        difficulty: Difficulty = Difficulty.MEDIUM,
        related_concepts: Optional[List[str]] = None
    ) -> Explanation:
        """
        讲解概念
        
        Args:
            topic: 教学主题
            concept_name: 概念名称
            difficulty: 难度等级
            related_concepts: 相关概念列表
            
        Returns:
            Explanation对象
        """
        content = self._generate_concept_content(concept_name, topic, difficulty)
        
        examples = [
            {
                "example": f"{concept_name}的具体例子1",
                "explanation": "详细解释这个例子如何体现概念"
            },
            {
                "example": f"{concept_name}的具体例子2",
                "explanation": "从这个例子可以得出什么结论"
            }
        ]
        
        common_mistakes = self._generate_common_mistakes(concept_name)
        tips = self._generate_tips(concept_name, difficulty)
        
        return Explanation(
            explanation_id=f"EXP-{uuid.uuid4().hex[:8].upper()}",
            explanation_type=ExplanationType.CONCEPT.value,
            title=f"{concept_name}概念讲解",
            topic=topic,
            content=content,
            key_points=self._extract_key_points(content),
            examples=examples,
            common_mistakes=common_mistakes,
            tips=tips,
            difficulty=difficulty.value,
            duration_minutes=15
        )
    
    def _generate_concept_content(
        self,
        concept_name: str,
        topic: str,
        difficulty: Difficulty
    ) -> str:
        """生成概念讲解内容"""
        return f"""# {concept_name}

## 一、定义
{concept_name}是指...

## 二、基本特征
1. 特征一：...
2. 特征二：...
3. 特征三：...

## 三、核心要素
- 要素1：...
- 要素2：...
- 要素3：...

## 四、与{topic}的关系
{concept_name}是{topic}的核心组成部分，理解{concept_name}对于掌握{topic}至关重要。

## 五、注意事项
1. 注意区分{concept_name}与相似概念的差异
2. 理解{concept_name}的应用条件
3. 掌握{concept_name}的表示方法"""
    
    # ==================== 例题讲解 ====================
    
    def explain_example(
        self,
        topic: str,
        example_problem: str,
        solution: str,
        difficulty: Difficulty = Difficulty.MEDIUM,
        steps: Optional[List[str]] = None
    ) -> Explanation:
        """
        讲解例题
        
        Args:
            topic: 教学主题
            example_problem: 例题题目
            solution: 解答
            difficulty: 难度等级
            steps: 解题步骤
            
        Returns:
            Explanation对象
        """
        if steps is None:
            steps = ["审题", "分析", "解答", "检验"]
        
        content = self._generate_example_content(
            example_problem, solution, topic, steps
        )
        
        return Explanation(
            explanation_id=f"EXP-{uuid.uuid4().hex[:8].upper()}",
            explanation_type=ExplanationType.EXAMPLE.value,
            title="例题精讲",
            topic=topic,
            content=content,
            key_points=["解题思路", "关键步骤", "易错点"],
            examples=[{
                "example": example_problem,
                "explanation": solution
            }],
            common_mistakes=self._generate_solution_mistakes(topic),
            tips=self._generate_solution_tips(steps),
            difficulty=difficulty.value,
            duration_minutes=20
        )
    
    def _generate_example_content(
        self,
        problem: str,
        solution: str,
        topic: str,
        steps: List[str]
    ) -> str:
        """生成例题讲解内容"""
        steps_content = "\n".join(
            f"**{i+1}. {step}**：..." for i, step in enumerate(steps)
        )
        
        return f"""# 例题精讲

## 题目
{problem}

## 解题步骤
{steps_content}

## 完整解答
{solution}

## 解题要点
1. 理解题意，明确已知和未知
2. 分析问题，选择合适的方法
3. 规范书写，完整表达
4. 检验结果，确保正确

## 方法总结
本题运用了{topic}的基本方法，关键是... """
    
    # ==================== 方法讲解 ====================
    
    def explain_method(
        self,
        topic: str,
        method_name: str,
        application_scenarios: Optional[List[str]] = None,
        difficulty: Difficulty = Difficulty.MEDIUM
    ) -> Explanation:
        """
        讲解方法
        
        Args:
            topic: 教学主题
            method_name: 方法名称
            application_scenarios: 应用场景
            difficulty: 难度等级
            
        Returns:
            Explanation对象
        """
        if application_scenarios is None:
            application_scenarios = ["场景1", "场景2", "场景3"]
        
        content = self._generate_method_content(method_name, topic, application_scenarios)
        
        return Explanation(
            explanation_id=f"EXP-{uuid.uuid4().hex[:8].upper()}",
            explanation_type=ExplanationType.METHOD.value,
            title=f"{method_name}方法讲解",
            topic=topic,
            content=content,
            key_points=self._extract_key_points(content),
            examples=self._generate_method_examples(method_name, topic),
            common_mistakes=self._generate_method_mistakes(method_name),
            tips=self._generate_method_tips(method_name),
            difficulty=difficulty.value,
            duration_minutes=25
        )
    
    def _generate_method_content(
        self,
        method_name: str,
        topic: str,
        scenarios: List[str]
    ) -> str:
        """生成方法讲解内容"""
        scenarios_content = "\n".join(
            f"- {s}" for s in scenarios
        )
        
        return f"""# {method_name}

## 一、方法原理
{method_name}是基于...原理的一种解题方法。

## 二、适用条件
{scenarios_content}

## 三、操作步骤
1. 第一步：...
2. 第二步：...
3. 第三步：...
4. 第四步：...

## 四、方法优势
- 优势1：...
- 优势2：...
- 优势3：...

## 五、注意事项
1. 注意方法的使用条件
2. 避免常见的错误用法
3. 结合{topic}的特点灵活运用"""
    
    # ==================== 拓展讲解 ====================
    
    def explain_extension(
        self,
        topic: str,
        extension_name: str,
        base_knowledge: str,
        difficulty: Difficulty = Difficulty.HARD
    ) -> Explanation:
        """
        讲解拓展内容
        
        Args:
            topic: 教学主题
            extension_name: 拓展内容名称
            base_knowledge: 基础知识
            difficulty: 难度等级
            
        Returns:
            Explanation对象
        """
        content = self._generate_extension_content(
            extension_name, topic, base_knowledge
        )
        
        return Explanation(
            explanation_id=f"EXP-{uuid.uuid4().hex[:8].upper()}",
            explanation_type=ExplanationType.EXTENSION.value,
            title=f"{extension_name}拓展",
            topic=topic,
            content=content,
            key_points=["拓展点1", "拓展点2", "应用拓展"],
            examples=self._generate_extension_examples(extension_name, topic),
            common_mistakes=[],
            tips=self._generate_extension_tips(),
            difficulty=difficulty.value,
            duration_minutes=30
        )
    
    def _generate_extension_content(
        self,
        extension_name: str,
        topic: str,
        base: str
    ) -> str:
        """生成拓展讲解内容"""
        return f"""# {extension_name}

## 一、从{topic}到{extension_name}
{extension_name}是在{topic}基础上的进一步深化和拓展。

## 二、基础知识回顾
{base}

## 三、拓展内容
### 1. 新概念
{extension_name}引入了以下新概念...

### 2. 新性质
{extension_name}具有以下特殊性质...

### 3. 新应用
{extension_name}可以应用在以下场景...

## 四、学习建议
1. 先打好{topic}的基础
2. 理解{extension_name}与{topic}的联系
3. 多做练习，熟练掌握"""
    
    # ==================== 辅助方法 ====================
    
    def _extract_key_points(self, content: str) -> List[str]:
        """提取关键点"""
        points = []
        for line in content.split("\n"):
            if line.startswith("## "):
                points.append(line.replace("## ", "").replace("# ", ""))
        return points[:5]
    
    def _generate_common_mistakes(self, concept_name: str) -> List[str]:
        """生成常见错误"""
        return [
            f"混淆{concept_name}与相近概念的区别",
            f"忽略{concept_name}的适用条件",
            f"对{concept_name}的理解停留在表面"
        ]
    
    def _generate_tips(self, concept_name: str, difficulty: Difficulty) -> List[str]:
        """生成技巧提示"""
        tips = [f"理解{concept_name}的关键是把握其本质特征"]
        if difficulty == Difficulty.HARD:
            tips.append("可以通过具体例子加深理解")
            tips.append("注意与相关概念的对比")
        return tips
    
    def _generate_solution_mistakes(self, topic: str) -> List[str]:
        """生成解题常见错误"""
        return [
            "审题不仔细，漏掉关键信息",
            "方法选择不当",
            "计算出错",
            "书写不规范"
        ]
    
    def _generate_solution_tips(self, steps: List[str]) -> List[str]:
        """生成解题技巧"""
        return [
            f"按照「{'→'.join(steps)}」的步骤解题",
            "每一步都要认真检查",
            "注意书写规范"
        ]
    
    def _generate_method_examples(
        self,
        method_name: str,
        topic: str
    ) -> List[Dict[str, str]]:
        """生成方法示例"""
        return [
            {
                "example": f"例1：在{topic}中应用{method_name}",
                "explanation": f"使用{method_name}的步骤和技巧"
            },
            {
                "example": f"例2：变式训练",
                "explanation": "同一方法在不同场景的应用"
            }
        ]
    
    def _generate_method_mistakes(self, method_name: str) -> List[str]:
        """生成方法常见错误"""
        return [
            f"不恰当使用{method_name}",
            f"忽略{method_name}的适用条件",
            f"{method_name}使用不当导致错误"
        ]
    
    def _generate_method_tips(self, method_name: str) -> List[str]:
        """生成方法技巧"""
        return [
            f"熟练掌握{method_name}的基本步骤",
            "注意方法使用的时机",
            "灵活运用，举一反三"
        ]
    
    def _generate_extension_examples(
        self,
        extension_name: str,
        topic: str
    ) -> List[Dict[str, str]]:
        """生成拓展示例"""
        return [
            {
                "example": f"拓展实例1",
                "explanation": "在{topic}基础上的拓展应用"
            }
        ]
    
    def _generate_extension_tips(self) -> List[str]:
        """生成拓展学习技巧"""
        return [
            "打好基础后再学习拓展内容",
            "理解拓展内容与基础内容的联系",
            "多做综合性练习"
        ]
