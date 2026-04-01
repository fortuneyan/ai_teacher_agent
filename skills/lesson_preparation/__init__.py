"""
智能备课助手 - 资深教师级别的备课系统

核心能力：
1. 网络资源搜索与整合（教案、课件、课标）
2. 基于课程标准的内容审核
3. 生成符合要求的教学大纲、教案、课件
4. 用户审核与智能反馈处理

输入：课程名称
输出：完整的备课资源包 + 审核交互界面
"""

import json
import re
import uuid
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import asyncio


class ResourceType(Enum):
    """资源类型"""
    CURRICULUM_STANDARD = "课程标准"      # 国家/地方课程标准
    TEXTBOOK = "教材"                     # 官方教材
    LESSON_PLAN = "教案"                  # 现有教案资源
    PPT = "课件"                          # PPT课件资源
    EXERCISE = "习题"                     # 练习题资源
    VIDEO = "视频"                        # 教学视频


class ContentQuality(Enum):
    """内容质量评级"""
    EXCELLENT = "优秀"      # 符合标准，可直接使用
    GOOD = "良好"           # 基本符合，需少量调整
    NEEDS_MODIFICATION = "需修改"  # 有明显问题，需大幅调整
    REJECTED = "不合格"     # 不符合标准，不能使用


@dataclass
class CurriculumStandard:
    """课程标准"""
    source: str                              # 来源：国家/地方/校本
    version: str                             # 版本年份
    course_name: str                         # 课程名称
    education_level: str                     # 教育阶段
    knowledge_objectives: List[str]          # 知识目标
    ability_objectives: List[str]            # 能力目标
    quality_objectives: List[str]            # 素养目标
    key_points: List[str]                    # 教学重点
    difficult_points: List[str]              # 教学难点
    content_requirements: List[str]          # 内容要求
    implementation_suggestions: List[str]    # 实施建议
    evaluation_requirements: List[str]       # 评价要求


@dataclass
class TeachingResource:
    """教学资源"""
    id: str
    resource_type: ResourceType
    title: str
    source: str                              # URL或来源描述
    content: str                             # 内容摘要
    quality_score: float                     # 质量评分 0-1
    curriculum_alignment: float              # 与课标符合度 0-1
    download_url: Optional[str] = None
    file_format: Optional[str] = None        # pdf, docx, pptx等
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LessonPlan:
    """教案"""
    course_name: str
    topic: str                               # 课时主题
    duration: int                            # 课时（分钟）
    education_level: str                     # 适用年级
    
    # 教学目标（三维目标）
    knowledge_objectives: List[str]          # 知识与技能
    ability_objectives: List[str]            # 过程与方法
    emotion_objectives: List[str]            # 情感态度与价值观
    
    # 教学重难点
    key_points: List[str]                    # 重点
    difficult_points: List[str]              # 难点
    
    # 教学方法
    teaching_methods: List[str]              # 讲授法、讨论法等
    
    # 教学过程
    teaching_process: List[Dict[str, Any]]   # 导入、新授、练习、小结、作业
    
    # 板书设计
    blackboard_design: str
    
    # 教学资源
    resources_needed: List[str]
    
    # 课后作业
    homework: Dict[str, Any]
    
    # 教学反思预设
    reflection_questions: List[str]
    
    # 元数据
    version: str = "1.0"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    source_resources: List[str] = field(default_factory=list)  # 参考的资源ID


@dataclass
class Courseware:
    """课件"""
    course_name: str
    topic: str
    slides: List[Dict[str, Any]]             # 每页内容
    design_style: str                        # 设计风格
    interactive_elements: List[str]          # 互动元素
    estimated_duration: int                  # 预计使用时长


@dataclass
class UserFeedback:
    """用户反馈"""
    feedback_type: str                       # "approve", "reject", "modify"
    target_section: str                      # 反馈针对的部分
    content: str                             # 反馈内容
    suggested_change: Optional[str] = None   # 建议的修改
    priority: str = "normal"                 # "high", "normal", "low"


@dataclass
class FeedbackEvaluation:
    """反馈评估结果"""
    feedback: UserFeedback
    is_valid: bool                           # 是否合理
    relevance_score: float                   # 相关度 0-1
    feasibility: str                         # "easy", "medium", "hard"
    reason: str                              # 评估理由
    suggested_action: str                    # 建议操作


class CurriculumStandardFetcher:
    """课程标准获取器"""
    
    # 模拟课程标准数据库
    STANDARDS_DB = {
        "高中数学": {
            "函数": CurriculumStandard(
                source="国家课程标准",
                version="2020",
                course_name="高中数学",
                education_level="高中",
                knowledge_objectives=[
                    "理解函数的概念，掌握函数的表示方法",
                    "掌握基本初等函数的性质和图像",
                    "理解函数与方程、不等式的关系"
                ],
                ability_objectives=[
                    "能够运用函数思想分析和解决实际问题",
                    "能够进行函数的运算和变换",
                    "能够利用信息技术研究函数性质"
                ],
                quality_objectives=[
                    "发展数学抽象和逻辑推理素养",
                    "培养数学建模和数据分析能力",
                    "体会数学的应用价值"
                ],
                key_points=[
                    "函数的概念和性质",
                    "基本初等函数的图像和性质",
                    "函数的应用"
                ],
                difficult_points=[
                    "函数概念的理解",
                    "抽象函数的性质分析",
                    "函数模型的建立"
                ],
                content_requirements=[
                    "通过丰富的实例引入函数概念",
                    "注重数形结合思想的渗透",
                    "加强函数与实际生活的联系"
                ],
                implementation_suggestions=[
                    "采用问题驱动教学法",
                    "利用信息技术辅助教学",
                    "设计分层练习满足不同学生需求"
                ],
                evaluation_requirements=[
                    "关注学生对函数概念的理解深度",
                    "评价学生运用函数解决问题的能力",
                    "重视学生学习过程中的表现"
                ]
            )
        }
    }
    
    async def fetch(self, course_name: str, topic: str) -> Optional[CurriculumStandard]:
        """获取课程标准"""
        # 实际实现中应该调用API或搜索
        # 这里使用模拟数据
        course_standards = self.STANDARDS_DB.get(course_name, {})
        return course_standards.get(topic) or self._generate_generic_standard(course_name, topic)
    
    def _generate_generic_standard(self, course_name: str, topic: str) -> CurriculumStandard:
        """生成通用课程标准模板"""
        return CurriculumStandard(
            source="通用课程标准模板",
            version="2024",
            course_name=course_name,
            education_level="通用",
            knowledge_objectives=[f"掌握{topic}的基本概念和知识"],
            ability_objectives=[f"能够运用{topic}解决实际问题"],
            quality_objectives=["培养学科核心素养"],
            key_points=[f"{topic}的核心概念"],
            difficult_points=[f"{topic}的深入理解和应用"],
            content_requirements=["注重基础，联系实际"],
            implementation_suggestions=["采用启发式教学"],
            evaluation_requirements=["关注理解和应用能力"]
        )


class ResourceSearcher:
    """网络资源搜索器"""
    
    async def search_all(self, course_name: str, topic: str) -> Dict[ResourceType, List[TeachingResource]]:
        """搜索所有类型的资源"""
        results = {}
        
        # 并行搜索各类资源
        tasks = [
            self._search_curriculum_standards(course_name, topic),
            self._search_textbooks(course_name, topic),
            self._search_lesson_plans(course_name, topic),
            self._search_ppts(course_name, topic),
            self._search_exercises(course_name, topic),
        ]
        
        search_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        results[ResourceType.CURRICULUM_STANDARD] = search_results[0] if not isinstance(search_results[0], Exception) else []
        results[ResourceType.TEXTBOOK] = search_results[1] if not isinstance(search_results[1], Exception) else []
        results[ResourceType.LESSON_PLAN] = search_results[2] if not isinstance(search_results[2], Exception) else []
        results[ResourceType.PPT] = search_results[3] if not isinstance(search_results[3], Exception) else []
        results[ResourceType.EXERCISE] = search_results[4] if not isinstance(search_results[4], Exception) else []
        
        return results
    
    async def _search_curriculum_standards(self, course_name: str, topic: str) -> List[TeachingResource]:
        """搜索课程标准"""
        # 模拟搜索结果
        return [
            TeachingResource(
                id="std_001",
                resource_type=ResourceType.CURRICULUM_STANDARD,
                title=f"《{course_name}课程标准》",
                source="国家中小学智慧教育平台",
                content=f"包含{topic}的教学目标、内容要求、实施建议",
                quality_score=0.95,
                curriculum_alignment=1.0,
                download_url="https://example.com/standard.pdf",
                metadata={"year": "2020", "level": "national"}
            )
        ]
    
    async def _search_textbooks(self, course_name: str, topic: str) -> List[TeachingResource]:
        """搜索教材资源"""
        return [
            TeachingResource(
                id="txt_001",
                resource_type=ResourceType.TEXTBOOK,
                title=f"{course_name}（必修）",
                source="人民教育出版社",
                content=f"{topic}章节：概念引入、例题讲解、练习题",
                quality_score=0.92,
                curriculum_alignment=0.95,
                download_url="https://example.com/textbook.pdf",
                metadata={"publisher": "人教版", "year": "2024"}
            ),
            TeachingResource(
                id="txt_002",
                resource_type=ResourceType.TEXTBOOK,
                title=f"{course_name}（选修）",
                source="北京师范大学出版社",
                content=f"{topic}拓展内容",
                quality_score=0.88,
                curriculum_alignment=0.90,
                metadata={"publisher": "北师大版", "year": "2024"}
            )
        ]
    
    async def _search_lesson_plans(self, course_name: str, topic: str) -> List[TeachingResource]:
        """搜索教案资源"""
        return [
            TeachingResource(
                id="lp_001",
                resource_type=ResourceType.LESSON_PLAN,
                title=f"{topic}优秀教案",
                source="学科网",
                content="完整的教学设计，包含三维目标、教学过程、板书设计",
                quality_score=0.85,
                curriculum_alignment=0.88,
                download_url="https://example.com/lesson_plan.docx",
                metadata={"author": "特级教师", "downloads": 1250}
            ),
            TeachingResource(
                id="lp_002",
                resource_type=ResourceType.LESSON_PLAN,
                title=f"{topic}探究式教学设计",
                source="教研网",
                content="以问题为导向的探究式教学设计",
                quality_score=0.82,
                curriculum_alignment=0.85,
                metadata={"method": "探究式", "duration": "45分钟"}
            )
        ]
    
    async def _search_ppts(self, course_name: str, topic: str) -> List[TeachingResource]:
        """搜索课件资源"""
        return [
            TeachingResource(
                id="ppt_001",
                resource_type=ResourceType.PPT,
                title=f"{topic}精美课件",
                source="第一课件网",
                content="20页PPT，包含动画、图表、例题",
                quality_score=0.80,
                curriculum_alignment=0.82,
                download_url="https://example.com/courseware.pptx",
                file_format="pptx",
                metadata={"slides": 20, "has_animation": True}
            )
        ]
    
    async def _search_exercises(self, course_name: str, topic: str) -> List[TeachingResource]:
        """搜索习题资源"""
        return [
            TeachingResource(
                id="ex_001",
                resource_type=ResourceType.EXERCISE,
                title=f"{topic}分层练习题",
                source="菁优网",
                content="基础题、提高题、拓展题，附答案解析",
                quality_score=0.87,
                curriculum_alignment=0.90,
                metadata={"difficulty_levels": 3, "with_answer": True}
            )
        ]


class ContentGenerator:
    """内容生成器 - 资深教师级别"""
    
    def __init__(self, llm_service=None):
        self.llm_service = llm_service
    
    async def generate_lesson_plan(
        self,
        course_name: str,
        topic: str,
        standard: CurriculumStandard,
        resources: List[TeachingResource]
    ) -> LessonPlan:
        """生成符合课标的教案"""
        
        # 分析参考资源
        reference_lesson_plans = [r for r in resources if r.resource_type == ResourceType.LESSON_PLAN]
        
        # 构建生成提示
        prompt = self._build_lesson_plan_prompt(course_name, topic, standard, reference_lesson_plans)
        
        # 使用LLM生成或基于模板生成
        if self.llm_service:
            content = await self.llm_service.generate(prompt)
            lesson_plan_data = self._parse_lesson_plan(content)
        else:
            lesson_plan_data = self._generate_from_template(course_name, topic, standard)
        
        return LessonPlan(
            course_name=course_name,
            topic=topic,
            duration=45,
            education_level=standard.education_level,
            knowledge_objectives=lesson_plan_data["knowledge_objectives"],
            ability_objectives=lesson_plan_data["ability_objectives"],
            emotion_objectives=lesson_plan_data["emotion_objectives"],
            key_points=lesson_plan_data["key_points"],
            difficult_points=lesson_plan_data["difficult_points"],
            teaching_methods=lesson_plan_data["teaching_methods"],
            teaching_process=lesson_plan_data["teaching_process"],
            blackboard_design=lesson_plan_data["blackboard_design"],
            resources_needed=lesson_plan_data["resources_needed"],
            homework=lesson_plan_data["homework"],
            reflection_questions=lesson_plan_data["reflection_questions"],
            source_resources=[r.id for r in reference_lesson_plans]
        )
    
    def _build_lesson_plan_prompt(
        self,
        course_name: str,
        topic: str,
        standard: CurriculumStandard,
        references: List[TeachingResource]
    ) -> str:
        """构建教案生成提示"""
        return f"""你是一位资深的{course_name}教师，拥有20年教学经验。

请根据以下课程标准，设计一份高质量的《{topic}》教案。

## 课程标准要求

### 知识目标
{chr(10).join(f"- {obj}" for obj in standard.knowledge_objectives)}

### 能力目标
{chr(10).join(f"- {obj}" for obj in standard.ability_objectives)}

### 素养目标
{chr(10).join(f"- {obj}" for obj in standard.quality_objectives)}

### 教学重点
{chr(10).join(f"- {p}" for p in standard.key_points)}

### 教学难点
{chr(10).join(f"- {d}" for d in standard.difficult_points)}

### 实施建议
{chr(10).join(f"- {s}" for s in standard.implementation_suggestions)}

## 参考资源
{chr(10).join(f"- {r.title}: {r.content}" for r in references[:2])}

## 输出要求
请输出完整的教案，包含：
1. 三维教学目标（知识、能力、素养）
2. 教学重难点
3. 教学方法
4. 详细的教学过程（导入、新授、练习、小结、作业，每个环节注明时间）
5. 板书设计
6. 所需教学资源
7. 课后作业设计
8. 教学反思预设问题

教案要体现资深教师的教学智慧，注重学生思维培养，符合新课程理念。"""
    
    def _generate_from_template(
        self,
        course_name: str,
        topic: str,
        standard: CurriculumStandard
    ) -> Dict[str, Any]:
        """基于模板生成教案（无LLM时使用）"""
        return {
            "knowledge_objectives": standard.knowledge_objectives,
            "ability_objectives": standard.ability_objectives,
            "emotion_objectives": standard.quality_objectives,
            "key_points": standard.key_points,
            "difficult_points": standard.difficult_points,
            "teaching_methods": ["启发式教学法", "探究式学习", "小组合作学习", "多媒体辅助教学"],
            "teaching_process": [
                {
                    "stage": "导入新课",
                    "duration": 5,
                    "activities": ["复习旧知，引出新问题", "创设情境，激发兴趣"],
                    "methods": "提问法、情境导入"
                },
                {
                    "stage": "讲授新知",
                    "duration": 20,
                    "activities": ["概念讲解与建构", "例题分析与示范", "学生思考与讨论"],
                    "methods": "讲授法、讨论法"
                },
                {
                    "stage": "巩固练习",
                    "duration": 12,
                    "activities": ["基础练习", "变式训练", "小组展示"],
                    "methods": "练习法、合作学习"
                },
                {
                    "stage": "课堂小结",
                    "duration": 5,
                    "activities": ["知识梳理", "方法总结", "学生分享收获"],
                    "methods": "归纳法"
                },
                {
                    "stage": "布置作业",
                    "duration": 3,
                    "activities": ["分层作业布置", "下节课预习指导"],
                    "methods": "自主学习"
                }
            ],
            "blackboard_design": f"""
            主板书：{topic}
            ┌─────────────────────────────┐
            │  1. 概念：                   │
            │  2. 性质：                   │
            │  3. 应用：                   │
            └─────────────────────────────┘
            副板书：例题解答过程、学生疑问
            """,
            "resources_needed": ["多媒体课件", "教材", "练习册", "白板/黑板"],
            "homework": {
                "basic": f"完成教材{topic}相关练习题",
                "advanced": f"探究{topic}在实际生活中的应用",
                "preview": "预习下节内容"
            },
            "reflection_questions": [
                "学生对本节核心概念的理解程度如何？",
                "教学过程中的时间分配是否合理？",
                "哪些学生需要课后个别辅导？",
                "下次教学需要改进的地方？"
            ]
        }
    
    def _parse_lesson_plan(self, content: str) -> Dict[str, Any]:
        """解析LLM生成的教案内容"""
        # 实际实现中需要更复杂的解析逻辑
        # 这里简化处理
        return self._generate_from_template("", "", CurriculumStandard(
            source="", version="", course_name="", education_level="",
            knowledge_objectives=[], ability_objectives=[], quality_objectives=[],
            key_points=[], difficult_points=[], content_requirements=[],
            implementation_suggestions=[], evaluation_requirements=[]
        ))
    
    async def generate_courseware(
        self,
        lesson_plan: LessonPlan,
        resources: List[TeachingResource]
    ) -> Courseware:
        """生成课件"""
        
        # 参考现有课件资源
        reference_ppts = [r for r in resources if r.resource_type == ResourceType.PPT]
        
        # 基于教案生成课件结构
        slides = self._generate_slides_from_lesson_plan(lesson_plan)
        
        return Courseware(
            course_name=lesson_plan.course_name,
            topic=lesson_plan.topic,
            slides=slides,
            design_style="简洁专业，突出重点",
            interactive_elements=["动画演示", "互动问答", "实时练习"],
            estimated_duration=lesson_plan.duration
        )
    
    def _generate_slides_from_lesson_plan(self, lesson_plan: LessonPlan) -> List[Dict[str, Any]]:
        """根据教案生成课件页面"""
        slides = []
        
        # 封面
        slides.append({
            "number": 1,
            "type": "title",
            "title": lesson_plan.topic,
            "subtitle": lesson_plan.course_name,
            "content": f"{lesson_plan.education_level} {lesson_plan.duration}分钟"
        })
        
        # 教学目标
        slides.append({
            "number": 2,
            "type": "objectives",
            "title": "学习目标",
            "content": {
                "knowledge": lesson_plan.knowledge_objectives,
                "ability": lesson_plan.ability_objectives,
                "emotion": lesson_plan.emotion_objectives
            }
        })
        
        # 导入
        first_step = lesson_plan.teaching_process[0] if lesson_plan.teaching_process else {}
        slides.append({
            "number": 3,
            "type": "introduction",
            "title": "情境导入",
            "content": first_step.get("activities", first_step.get("teacher_activity", "")),
            "duration": first_step.get("duration", "5")
        })
        
        # 新知讲解（多页）
        slide_num = 4
        for point in lesson_plan.key_points:
            slides.append({
                "number": slide_num,
                "type": "content",
                "title": point,
                "content": f"详细讲解{point}",
                "animation": True
            })
            slide_num += 1
        
        # 例题
        slides.append({
            "number": slide_num,
            "type": "example",
            "title": "典型例题",
            "content": "例题解析与示范",
            "steps": ["分析", "解答", "总结"]
        })
        slide_num += 1
        
        # 练习
        slides.append({
            "number": slide_num,
            "type": "exercise",
            "title": "课堂练习",
            "content": "即时巩固训练"
        })
        slide_num += 1
        
        # 小结
        slides.append({
            "number": slide_num,
            "type": "summary",
            "title": "课堂小结",
            "content": lesson_plan.key_points
        })
        slide_num += 1
        
        # 作业
        slides.append({
            "number": slide_num,
            "type": "homework",
            "title": "课后作业",
            "content": lesson_plan.homework
        })
        
        return slides


class FeedbackProcessor:
    """用户反馈处理器 - 智能评估和过滤"""
    
    # 不合理反馈的模式
    INVALID_PATTERNS = [
        r"^[^\u4e00-\u9fa5a-zA-Z0-9]+$",  # 无意义字符
        r"(.)\1{5,}",  # 重复字符超过5次
        r"^.{1,3}$",  # 太短（少于3个字符）
    ]
    
    # 不相关关键词
    IRRELEVANT_KEYWORDS = [
        "广告", "推广", "销售", "购买", "优惠", "打折",
        " unrelated", "不相关", "无关", "随便", "乱写"
    ]
    
    async def evaluate_feedback(self, feedback: UserFeedback, lesson_plan: LessonPlan) -> FeedbackEvaluation:
        """评估用户反馈的合理性"""
        
        # 1. 基础有效性检查
        is_valid, validity_reason = self._check_basic_validity(feedback)
        if not is_valid:
            return FeedbackEvaluation(
                feedback=feedback,
                is_valid=False,
                relevance_score=0.0,
                feasibility="impossible",
                reason=validity_reason,
                suggested_action="reject"
            )
        
        # 2. 相关性评估
        relevance_score = self._evaluate_relevance(feedback, lesson_plan)
        
        # 3. 可行性评估
        feasibility = self._evaluate_feasibility(feedback)
        
        # 4. 综合判断
        if relevance_score < 0.3:
            return FeedbackEvaluation(
                feedback=feedback,
                is_valid=True,
                relevance_score=relevance_score,
                feasibility=feasibility,
                reason="反馈内容与教案主题关联度较低",
                suggested_action="clarify"  # 请求澄清
            )
        
        if relevance_score > 0.7 and feasibility in ["easy", "medium"]:
            return FeedbackEvaluation(
                feedback=feedback,
                is_valid=True,
                relevance_score=relevance_score,
                feasibility=feasibility,
                reason="反馈合理且可行",
                suggested_action="accept"
            )
        
        # 中间情况
        return FeedbackEvaluation(
            feedback=feedback,
            is_valid=True,
            relevance_score=relevance_score,
            feasibility=feasibility,
            reason="反馈有一定价值，但需要进一步评估",
            suggested_action="review"
        )
    
    def _check_basic_validity(self, feedback: UserFeedback) -> Tuple[bool, str]:
        """基础有效性检查"""
        content = feedback.content
        
        # 检查无意义模式
        for pattern in self.INVALID_PATTERNS:
            if re.match(pattern, content):
                return False, "反馈内容格式不符合要求"
        
        # 检查不相关关键词
        for keyword in self.IRRELEVANT_KEYWORDS:
            if keyword in content:
                return False, f"反馈包含不相关内容: {keyword}"
        
        return True, ""
    
    def _evaluate_relevance(self, feedback: UserFeedback, lesson_plan: LessonPlan) -> float:
        """评估反馈与教案的相关性"""
        content = feedback.content.lower()
        
        # 提取教案中的关键词
        keywords = set()
        keywords.update([w.lower() for w in lesson_plan.topic.split()])
        keywords.update([obj.lower() for obj in lesson_plan.knowledge_objectives])
        keywords.update([p.lower() for p in lesson_plan.key_points])
        
        # 计算匹配度
        matched = sum(1 for kw in keywords if kw in content)
        relevance = matched / max(len(keywords), 1)
        
        # 根据反馈类型调整
        if feedback.target_section in ["教学目标", "教学重难点", "教学过程"]:
            relevance *= 1.2  # 针对具体部分的反馈权重更高
        
        return min(relevance, 1.0)
    
    def _evaluate_feasibility(self, feedback: UserFeedback) -> str:
        """评估修改的可行性"""
        content = feedback.content
        
        # 简单的启发式判断
        if any(word in content for word in ["删除", "去掉", "减少"]):
            return "easy"
        
        if any(word in content for word in ["增加", "添加", "补充"]):
            return "medium"
        
        if any(word in content for word in ["重新设计", "重构", "彻底改变"]):
            return "hard"
        
        if feedback.suggested_change and len(feedback.suggested_change) > 100:
            return "hard"
        
        return "medium"
    
    async def apply_feedback(
        self,
        lesson_plan: LessonPlan,
        feedback: UserFeedback,
        evaluation: FeedbackEvaluation
    ) -> LessonPlan:
        """应用有效的反馈修改教案"""
        
        if evaluation.suggested_action != "accept":
            return lesson_plan
        
        # 创建副本进行修改
        updated_plan = self._copy_lesson_plan(lesson_plan)
        
        # 根据目标部分应用修改
        section = feedback.target_section
        
        if section == "教学目标":
            updated_plan = self._update_objectives(updated_plan, feedback)
        elif section == "教学重难点":
            updated_plan = self._update_key_points(updated_plan, feedback)
        elif section == "教学过程":
            updated_plan = self._update_teaching_process(updated_plan, feedback)
        elif section == "板书设计":
            updated_plan.blackboard_design = feedback.suggested_change or updated_plan.blackboard_design
        elif section == "课后作业":
            updated_plan = self._update_homework(updated_plan, feedback)
        
        # 更新版本信息
        updated_plan.version = self._increment_version(updated_plan.version)
        updated_plan.created_at = datetime.now().isoformat()
        
        return updated_plan
    
    def _copy_lesson_plan(self, plan: LessonPlan) -> LessonPlan:
        """深拷贝教案"""
        return LessonPlan(
            course_name=plan.course_name,
            topic=plan.topic,
            duration=plan.duration,
            education_level=plan.education_level,
            knowledge_objectives=plan.knowledge_objectives.copy(),
            ability_objectives=plan.ability_objectives.copy(),
            emotion_objectives=plan.emotion_objectives.copy(),
            key_points=plan.key_points.copy(),
            difficult_points=plan.difficult_points.copy(),
            teaching_methods=plan.teaching_methods.copy(),
            teaching_process=[step.copy() for step in plan.teaching_process],
            blackboard_design=plan.blackboard_design,
            resources_needed=plan.resources_needed.copy(),
            homework=plan.homework.copy(),
            reflection_questions=plan.reflection_questions.copy(),
            version=plan.version,
            created_at=plan.created_at,
            source_resources=plan.source_resources.copy()
        )
    
    def _update_objectives(self, plan: LessonPlan, feedback: UserFeedback) -> LessonPlan:
        """更新教学目标"""
        if feedback.suggested_change:
            # 解析建议的修改
            plan.knowledge_objectives.append(feedback.suggested_change)
        return plan
    
    def _update_key_points(self, plan: LessonPlan, feedback: UserFeedback) -> LessonPlan:
        """更新教学重难点"""
        if "重点" in feedback.content and feedback.suggested_change:
            plan.key_points.append(feedback.suggested_change)
        elif "难点" in feedback.content and feedback.suggested_change:
            plan.difficult_points.append(feedback.suggested_change)
        return plan
    
    def _update_teaching_process(self, plan: LessonPlan, feedback: UserFeedback) -> LessonPlan:
        """更新教学过程"""
        # 简化处理：在第一个环节添加备注
        if plan.teaching_process:
            plan.teaching_process[0]["note"] = f"用户反馈: {feedback.content}"
        return plan
    
    def _update_homework(self, plan: LessonPlan, feedback: UserFeedback) -> LessonPlan:
        """更新课后作业"""
        if feedback.suggested_change:
            plan.homework["custom"] = feedback.suggested_change
        return plan
    
    def _increment_version(self, version: str) -> str:
        """版本号递增"""
        try:
            parts = version.split(".")
            major = int(parts[0])
            minor = int(parts[1]) if len(parts) > 1 else 0
            return f"{major}.{minor + 1}"
        except:
            return "1.1"


class LessonPreparationAssistant:
    """
    智能备课助手 - 主类
    
    使用示例：
        assistant = LessonPreparationAssistant()
        result = await assistant.prepare_lesson("高中数学", "函数的概念")
        
        # 用户审核
        feedback = UserFeedback(
            feedback_type="modify",
            target_section="教学目标",
            content="需要增加实际应用的目标",
            suggested_change="能够运用函数概念解决实际问题"
        )
        
        updated_result = await assistant.process_feedback(result.lesson_plan, feedback)
    """
    
    def __init__(self, llm_service=None):
        self.standard_fetcher = CurriculumStandardFetcher()
        self.resource_searcher = ResourceSearcher()
        self.content_generator = ContentGenerator(llm_service)
        self.feedback_processor = FeedbackProcessor()
        self.llm_service = llm_service
    
    async def prepare_lesson(
        self,
        course_name: str,
        topic: str,
        education_level: str = "高中"
    ) -> Dict[str, Any]:
        """
        完整的备课流程
        
        Args:
            course_name: 课程名称（如"高中数学"）
            topic: 课时主题（如"函数的概念"）
            education_level: 教育阶段
            
        Returns:
            包含教案、课件、资源的完整备课包
        """
        print(f"\n{'='*60}")
        print(f"开始备课: {course_name} - {topic}")
        print(f"{'='*60}\n")
        
        # Step 1: 获取课程标准
        print("[1/5] 获取课程标准...")
        standard = await self.standard_fetcher.fetch(course_name, topic)
        print(f"      ✓ 获取到{standard.source}的标准")
        
        # Step 2: 搜索网络资源
        print("[2/5] 搜索教学资源...")
        resources = await self.resource_searcher.search_all(course_name, topic)
        total_resources = sum(len(r) for r in resources.values())
        print(f"      ✓ 找到 {total_resources} 个资源:")
        for res_type, res_list in resources.items():
            if res_list:
                print(f"        - {res_type.value}: {len(res_list)}个")
        
        # Step 3: 生成教案
        print("[3/5] 生成教案...")
        all_resources = []
        for res_list in resources.values():
            all_resources.extend(res_list)
        
        lesson_plan = await self.content_generator.generate_lesson_plan(
            course_name, topic, standard, all_resources
        )
        print(f"      ✓ 教案生成完成 (版本: {lesson_plan.version})")
        print(f"        - 教学目标: {len(lesson_plan.knowledge_objectives)}个")
        print(f"        - 教学环节: {len(lesson_plan.teaching_process)}个")
        
        # Step 4: 生成课件
        print("[4/5] 生成课件...")
        courseware = await self.content_generator.generate_courseware(lesson_plan, all_resources)
        print(f"      ✓ 课件生成完成 ({len(courseware.slides)}页)")
        
        # Step 5: 整合输出
        print("[5/5] 整合备课资源...")
        result = {
            "course_name": course_name,
            "topic": topic,
            "education_level": education_level,
            "curriculum_standard": asdict(standard),
            "lesson_plan": asdict(lesson_plan),
            "courseware": asdict(courseware),
            "resources": {
                res_type.value: [asdict(r) for r in res_list]
                for res_type, res_list in resources.items()
            },
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "version": lesson_plan.version,
                "status": "pending_review"  # 待审核
            }
        }
        
        print(f"\n{'='*60}")
        print("备课完成，等待用户审核")
        print(f"{'='*60}\n")
        
        return result
    
    async def process_feedback(
        self,
        lesson_plan: LessonPlan,
        feedback: UserFeedback
    ) -> Dict[str, Any]:
        """
        处理用户反馈
        
        Args:
            lesson_plan: 当前教案
            feedback: 用户反馈
            
        Returns:
            处理结果，包含是否采纳、修改后的教案、处理理由
        """
        print(f"\n处理用户反馈...")
        print(f"  反馈类型: {feedback.feedback_type}")
        print(f"  目标部分: {feedback.target_section}")
        print(f"  反馈内容: {feedback.content[:50]}...")
        
        # 评估反馈
        evaluation = await self.feedback_processor.evaluate_feedback(feedback, lesson_plan)
        
        print(f"\n评估结果:")
        print(f"  有效性: {'✓ 有效' if evaluation.is_valid else '✗ 无效'}")
        print(f"  相关度: {evaluation.relevance_score:.2f}")
        print(f"  可行性: {evaluation.feasibility}")
        print(f"  评估理由: {evaluation.reason}")
        print(f"  建议操作: {evaluation.suggested_action}")
        
        # 根据评估结果处理
        if evaluation.suggested_action == "accept":
            updated_plan = await self.feedback_processor.apply_feedback(
                lesson_plan, feedback, evaluation
            )
            print(f"\n✓ 反馈已采纳，教案已更新至版本 {updated_plan.version}")
            
            return {
                "status": "accepted",
                "original_plan": asdict(lesson_plan),
                "updated_plan": asdict(updated_plan),
                "evaluation": asdict(evaluation),
                "message": "反馈已采纳并应用"
            }
        
        elif evaluation.suggested_action == "clarify":
            print(f"\n? 反馈需要澄清")
            return {
                "status": "needs_clarification",
                "original_plan": asdict(lesson_plan),
                "evaluation": asdict(evaluation),
                "message": "反馈与教案关联度较低，请提供更具体的修改建议",
                "suggestion": f"请针对'{lesson_plan.topic}'的具体内容提供反馈"
            }
        
        elif evaluation.suggested_action == "reject":
            print(f"\n✗ 反馈未通过有效性检查")
            return {
                "status": "rejected",
                "original_plan": asdict(lesson_plan),
                "evaluation": asdict(evaluation),
                "message": f"反馈未通过审核: {evaluation.reason}"
            }
        
        else:  # review
            print(f"\n⚠ 反馈需要人工复核")
            return {
                "status": "pending_review",
                "original_plan": asdict(lesson_plan),
                "evaluation": asdict(evaluation),
                "message": "反馈已记录，建议人工复核后决定是否采纳"
            }
    
    def format_lesson_plan_for_display(self, lesson_plan: LessonPlan) -> str:
        """格式化教案用于展示"""
        output = []
        output.append(f"# {lesson_plan.topic} 教案")
        output.append(f"\n**课程**: {lesson_plan.course_name}")
        output.append(f"**课时**: {lesson_plan.duration}分钟")
        output.append(f"**版本**: {lesson_plan.version}")
        output.append(f"\n---\n")
        
        # 教学目标
        output.append("## 一、教学目标\n")
        output.append("### 知识与技能")
        for obj in lesson_plan.knowledge_objectives:
            output.append(f"- {obj}")
        output.append("\n### 过程与方法")
        for obj in lesson_plan.ability_objectives:
            output.append(f"- {obj}")
        output.append("\n### 情感态度与价值观")
        for obj in lesson_plan.emotion_objectives:
            output.append(f"- {obj}")
        
        # 教学重难点
        output.append("\n## 二、教学重难点\n")
        output.append("**重点**: " + "、".join(lesson_plan.key_points))
        output.append("**难点**: " + "、".join(lesson_plan.difficult_points))
        
        # 教学方法
        output.append("\n## 三、教学方法\n")
        output.append("、".join(lesson_plan.teaching_methods))
        
        # 教学过程
        output.append("\n## 四、教学过程\n")
        for step in lesson_plan.teaching_process:
            output.append(f"### {step['stage']} ({step['duration']}分钟)")
            output.append(f"**方法**: {step['methods']}")
            output.append("**活动**:")
            for activity in step['activities']:
                output.append(f"- {activity}")
            output.append("")
        
        # 板书设计
        output.append("## 五、板书设计\n")
        output.append("```")
        output.append(lesson_plan.blackboard_design)
        output.append("```")
        
        # 课后作业
        output.append("\n## 六、课后作业\n")
        for key, value in lesson_plan.homework.items():
            output.append(f"**{key}**: {value}")
        
        # 教学反思
        output.append("\n## 七、教学反思预设\n")
        for q in lesson_plan.reflection_questions:
            output.append(f"- {q}")
        
        return "\n".join(output)


# 便捷函数
async def prepare_lesson(course_name: str, topic: str) -> Dict[str, Any]:
    """便捷的备课函数"""
    assistant = LessonPreparationAssistant()
    return await assistant.prepare_lesson(course_name, topic)


async def process_user_feedback(
    lesson_plan: LessonPlan,
    feedback_type: str,
    target_section: str,
    content: str,
    suggested_change: str = None
) -> Dict[str, Any]:
    """便捷的处理反馈函数"""
    assistant = LessonPreparationAssistant()
    feedback = UserFeedback(
        feedback_type=feedback_type,
        target_section=target_section,
        content=content,
        suggested_change=suggested_change
    )
    return await assistant.process_feedback(lesson_plan, feedback)


# ==================== 扩展功能：细化教学目标生成 ====================

def generate_detailed_objectives(
    standards: List[CurriculumStandard],
    topic: str
) -> Dict[str, Any]:
    """
    生成细化的三维教学目标
    
    Args:
        standards: 课程标准列表
        topic: 教学主题
        
    Returns:
        教学目标字典
    """
    # 从课标中提取要求
    all_knowledge = []
    all_ability = []
    for std in standards:
        all_knowledge.extend(std.knowledge_objectives)
        all_ability.extend(std.ability_objectives)
    
    return {
        "knowledge_objectives": [
            f"理解{topic}的基本概念",
            f"掌握{topic}的核心原理",
            f"能够描述{topic}的主要特征"
        ] + (all_knowledge[:2] if all_knowledge else []),
        "skill_objectives": [
            f"能够运用{topic}解决简单问题",
            "培养分析和归纳能力",
            "提升逻辑推理能力"
        ] + (all_ability[:2] if all_ability else []),
        "emotion_objectives": [
            "激发学习兴趣和求知欲",
            "培养严谨的科学思维习惯"
        ],
        "competency_objectives": [
            "发展学科核心素养",
            "培养科学探究能力"
        ],
        "status": "confirmed"
    }


# ==================== 扩展功能：详细教学过程设计 ====================

def design_detailed_teaching_process(
    objectives: Dict[str, Any],
    suggested_hours: int,
    key_points: Optional[List[str]] = None,
    difficult_points: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    设计详细的教学过程
    
    Args:
        objectives: 教学目标
        suggested_hours: 建议课时
        key_points: 教学重点
        difficult_points: 教学难点
        
    Returns:
        教学步骤列表
    """
    # 计算总时间（每节课45分钟）
    minutes_per_lesson = 45
    total_minutes = suggested_hours * minutes_per_lesson
    
    return [
        {
            "step": 1,
            "phase": "导入",
            "duration": f"{int(total_minutes * 0.1)}分钟",
            "teacher_activity": "创设情境，提出问题",
            "student_activity": "观察思考，回答问题",
            "design_intent": "激发学习兴趣，建立知识联系",
            "key_points": ["引起注意", "激活旧知"]
        },
        {
            "step": 2,
            "phase": "新授",
            "duration": f"{int(total_minutes * 0.45)}分钟",
            "teacher_activity": "讲解概念，引导探究，示范例题",
            "student_activity": "认真听讲，参与探究，思考例题",
            "design_intent": "构建知识体系，理解核心概念",
            "key_points": key_points or ["概念理解", "原理掌握"]
        },
        {
            "step": 3,
            "phase": "练习",
            "duration": f"{int(total_minutes * 0.3)}分钟",
            "teacher_activity": "组织练习，巡视指导，点评纠错",
            "student_activity": "独立完成练习，小组讨论",
            "design_intent": "巩固知识，掌握方法",
            "key_points": ["技能训练", "方法应用"]
        },
        {
            "step": 4,
            "phase": "小结",
            "duration": f"{int(total_minutes * 0.1)}分钟",
            "teacher_activity": "引导总结，强调重点",
            "student_activity": "回顾反思，归纳整理",
            "design_intent": "梳理知识，形成网络",
            "key_points": ["知识梳理", "方法总结"]
        },
        {
            "step": 5,
            "phase": "作业",
            "duration": "课后",
            "teacher_activity": "布置分层作业",
            "student_activity": "完成作业，预习新知",
            "design_intent": "巩固拓展，培养能力",
            "key_points": ["基础巩固", "能力提升"]
        }
    ]


# ==================== 扩展功能：反馈评估与教案修改 ====================

class FeedbackEvaluator:
    """反馈评估器 - 简单规则版本"""
    
    RELEVANCE_KEYWORDS = ['增加', '删除', '修改', '调整', '添加', '优化']
    
    @staticmethod
    def evaluate_feedback(feedback: UserFeedback, lesson_plan: LessonPlan) -> Dict[str, Any]:
        """
        评估用户反馈
        
        Args:
            feedback: 用户反馈
            lesson_plan: 当前教案
            
        Returns:
            评估结果字典
        """
        content = feedback.content
        
        # 评估相关性
        relevance_score = 0.5
        for keyword in FeedbackEvaluator.RELEVANCE_KEYWORDS:
            if keyword in content:
                relevance_score += 0.1
        relevance_score = min(relevance_score, 0.95)
        
        # 评估可行性
        feasibility_score = 0.7
        if len(content) > 10:
            feasibility_score += 0.1
        if any(kw in content for kw in ['例子', '练习', '活动', '时间']):
            feasibility_score += 0.1
        feasibility_score = min(feasibility_score, 0.95)
        
        # 综合决策
        confidence = (relevance_score + feasibility_score) / 2
        if confidence > 0.7:
            decision = "accepted"
        elif confidence > 0.4:
            decision = "partial"
        else:
            decision = "rejected"
        
        reasoning = f"反馈相关性: {relevance_score:.2f}, 可行性: {feasibility_score:.2f}"
        
        return {
            "decision": decision,
            "confidence": confidence,
            "relevance_score": relevance_score,
            "feasibility_score": feasibility_score,
            "reasoning": reasoning
        }
    
    @staticmethod
    def modify_lesson_plan(
        lesson_plan: LessonPlan,
        feedback: UserFeedback,
        evaluation: Dict[str, Any]
    ) -> Tuple[LessonPlan, Dict[str, Any]]:
        """
        根据反馈修改教案
        
        Args:
            lesson_plan: 当前教案
            feedback: 用户反馈
            evaluation: 评估结果
            
        Returns:
            (修改后的教案, 更新记录)
        """
        if evaluation["decision"] == "rejected":
            return lesson_plan, {
                "update_id": f"UPD-{uuid.uuid4().hex[:8].upper()}",
                "status": "rejected",
                "description": f"反馈被拒绝: {feedback.content[:30]}..."
            }
        
        # 创建副本进行修改
        updated_plan = LessonPlan(
            course_name=lesson_plan.course_name,
            topic=lesson_plan.topic,
            duration=lesson_plan.duration,
            education_level=lesson_plan.education_level,
            knowledge_objectives=lesson_plan.knowledge_objectives.copy(),
            ability_objectives=lesson_plan.ability_objectives.copy(),
            emotion_objectives=lesson_plan.emotion_objectives.copy(),
            key_points=lesson_plan.key_points.copy(),
            difficult_points=lesson_plan.difficult_points.copy(),
            teaching_methods=lesson_plan.teaching_methods.copy(),
            teaching_process=[step.copy() for step in lesson_plan.teaching_process],
            blackboard_design=lesson_plan.blackboard_design,
            resources_needed=lesson_plan.resources_needed.copy(),
            homework=lesson_plan.homework.copy(),
            reflection_questions=lesson_plan.reflection_questions.copy(),
            version=lesson_plan.version,
            created_at=lesson_plan.created_at,
            source_resources=lesson_plan.source_resources.copy()
        )
        
        content = feedback.content
        
        # 简单的关键词匹配修改
        if "增加" in content or "添加" in content:
            if "例子" in content or "实例" in content:
                updated_plan.knowledge_objectives.append("能够运用实例理解概念")
            if "练习" in content and updated_plan.teaching_process:
                # 添加一个新的练习环节
                new_step = {
                    "stage": "巩固练习",
                    "duration": 10,
                    "activities": ["额外巩固练习", "学生展示"],
                    "methods": "练习法"
                }
                updated_plan.teaching_process.append(new_step)
        
        # 版本递增
        try:
            parts = updated_plan.version.split(".")
            major = int(parts[0])
            minor = int(parts[1]) + 1 if len(parts) > 1 else 1
            updated_plan.version = f"{major}.{minor}"
        except:
            updated_plan.version = "1.1"
        
        update_record = {
            "update_id": f"UPD-{uuid.uuid4().hex[:8].upper()}",
            "status": "applied",
            "description": f"根据反馈修改: {feedback.content[:50]}..."
        }
        
        return updated_plan, update_record


# ==================== 扩展功能：完整备课流程 ====================

async def complete_lesson_preparation(
    course_name: str,
    topic: str,
    education_level: str = "高中",
    suggested_hours: int = 2
) -> Dict[str, Any]:
    """
    执行完整的备课流程（6步）
    
    Args:
        course_name: 课程名称
        topic: 课时主题
        education_level: 教育阶段
        suggested_hours: 建议课时
        
    Returns:
        完整的备课结果
    """
    print(f"\n开始为《{topic}》备课...")
    
    assistant = LessonPreparationAssistant()
    
    # 1. 获取课程标准
    print("  [1/6] 获取课程标准...")
    standard = await assistant.standard_fetcher.fetch(course_name, topic)
    
    # 2. 搜索教学资源
    print("  [2/6] 搜索教学资源...")
    resources = await assistant.resource_searcher.search_all(course_name, topic)
    all_resources = []
    for res_list in resources.values():
        all_resources.extend(res_list)
    total_resources = sum(len(r) for r in resources.values())
    print(f"        找到 {total_resources} 个资源")
    
    # 3. 生成细化教学目标
    print("  [3/6] 生成教学目标...")
    standards_for_objectives = [standard] if standard else []
    objectives = generate_detailed_objectives(standards_for_objectives, topic)
    total_objectives = (
        len(objectives.get("knowledge_objectives", [])) +
        len(objectives.get("skill_objectives", [])) +
        len(objectives.get("emotion_objectives", []))
    )
    print(f"        生成 {total_objectives} 个目标")
    
    # 4. 生成教案
    print("  [4/6] 生成教案...")
    lesson_plan = await assistant.content_generator.generate_lesson_plan(
        course_name, topic, standard, all_resources
    )
    
    # 5. 设计详细教学过程
    print("  [5/6] 设计教学过程...")
    detailed_process = design_detailed_teaching_process(
        objectives, suggested_hours
    )
    lesson_plan.teaching_process = detailed_process
    print(f"        设计 {len(detailed_process)} 个教学环节")
    
    # 6. 生成课件大纲
    print("  [6/6] 生成课件...")
    courseware = await assistant.content_generator.generate_courseware(lesson_plan, all_resources)
    print(f"        生成 {len(courseware.slides)} 页课件")
    
    # 整合结果
    result = {
        "course_name": course_name,
        "topic": topic,
        "education_level": education_level,
        "curriculum_standard": asdict(standard) if standard else {},
        "objectives": objectives,
        "lesson_plan": asdict(lesson_plan),
        "courseware": asdict(courseware),
        "resources": {
            res_type.value: [asdict(r) for r in res_list]
            for res_type, res_list in resources.items()
        },
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "version": lesson_plan.version,
            "total_resources": total_resources,
            "total_slides": len(courseware.slides)
        }
    }
    
    print("\n备课完成!")
    return result
