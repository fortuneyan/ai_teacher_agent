"""
智能备课技能实现

MVP版本核心功能：
1. 搜索课程标准
2. 生成教案
"""
import uuid
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

# 添加src到路径
src_path = Path(__file__).parent.parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# 导入数据对象
from models import (
    CourseBasicInfo,
    CurriculumStandard,
    LessonPlan,
    LessonPlanStatus,
    SearchResult,
    UserFeedback,
    FeedbackEvaluation,
    LessonPlanUpdate,
    UpdateType,
    UpdateStatus,
    TeachingResource,
    ResourceType,
    ResourceSearchParams,
    ResourceSearchResult,
    TeachingObjectives,
    ObjectiveLevel,
    ObjectiveStatus,
    CoursewareOutline,
    SlideOutline,
    SlideType
)

# 导入Mock服务
from mocks import MockSearchAPI, MockLLMService


class LessonPreparationSkill:
    """
    智能备课技能
    
    提供完整的备课流程支持
    """
    
    def __init__(self):
        """初始化技能"""
        self.search_api = MockSearchAPI()
        self.llm_service = MockLLMService()
        self.session_history: List[Dict[str, Any]] = []
    
    # ==================== 核心功能1: 搜索课程标准 ====================
    
    def search_curriculum_standards(
        self,
        course_info: CourseBasicInfo,
        search_type: str = "comprehensive",
        limit: int = 10
    ) -> Tuple[SearchResult, List[CurriculumStandard]]:
        """
        搜索课程标准
        
        Args:
            course_info: 课程基本信息
            search_type: 搜索类型 (comprehensive/basic/detailed)
            limit: 返回结果数量限制
            
        Returns:
            (搜索结果, 课标对象列表)
        """
        # 构建搜索查询
        query = course_info.topic
        
        # 调用Mock搜索API
        search_result_dict = self.search_api.search(
            query=query,
            education_level=course_info.education_level,
            subject=course_info.subject,
            topic=course_info.topic,
            limit=limit
        )
        
        # 转换为SearchResult对象
        search_result = SearchResult.from_dict(search_result_dict)
        
        # 转换为CurriculumStandard对象列表
        standards = []
        for result in search_result.results:
            standard = CurriculumStandard(
                standard_id=result.get("standard_id", ""),
                standard_name=result.get("standard_name", ""),
                standard_type=result.get("standard_type", ""),
                education_level=result.get("education_level", ""),
                subject=result.get("subject", ""),
                topic=result.get("topic", ""),
                content_requirements=result.get("content_requirements", []),
                competency_requirements=result.get("competency_requirements", []),
                achievement_standards=result.get("achievement_standards", []),
                suggested_hours=result.get("suggested_hours", 0),
                extracted_at=datetime.now(),
                relevance_score=result.get("relevance_score", 0.0)
            )
            standards.append(standard)
        
        # 记录会话历史
        self._record_action("search_standards", {
            "course_info": course_info.to_dict(),
            "search_type": search_type,
            "result_count": len(standards)
        })
        
        return search_result, standards
    
    # ==================== 核心功能2: 生成教案 ====================
    
    def generate_lesson_plan(
        self,
        course_info: CourseBasicInfo,
        standards: List[CurriculumStandard],
        requirements: Optional[List[str]] = None
    ) -> LessonPlan:
        """
        生成完整教案
        
        Args:
            course_info: 课程基本信息
            standards: 课程标准列表
            requirements: 额外要求
            
        Returns:
            生成的教案对象
        """
        # 准备输入数据
        course_info_dict = course_info.to_dict()
        standards_dict = [s.to_dict() for s in standards]
        
        # 调用LLM服务生成教案
        generated = self.llm_service.generate_lesson_plan(
            course_info=course_info_dict,
            standards=standards_dict,
            requirements=requirements
        )
        
        # 创建教案对象
        lesson_plan = LessonPlan(
            plan_id=f"LP-{uuid.uuid4().hex[:8].upper()}",
            title=generated["title"],
            subject=generated["subject"],
            education_level=generated["education_level"],
            topic=generated["topic"],
            teaching_objectives=generated["teaching_objectives"],
            teaching_procedure=generated["teaching_procedure"],
            status=LessonPlanStatus.DRAFT,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by="ai_teacher_agent",
            version=1
        )
        
        # 记录会话历史
        self._record_action("generate_lesson_plan", {
            "course_info": course_info_dict,
            "standards_count": len(standards),
            "plan_id": lesson_plan.plan_id
        })
        
        return lesson_plan
    
    # ==================== 辅助功能 ====================
    
    def analyze_standards(
        self,
        standards: List[CurriculumStandard]
    ) -> Dict[str, Any]:
        """
        分析课标要求
        
        Args:
            standards: 课程标准列表
            
        Returns:
            分析结果
        """
        standards_dict = [s.to_dict() for s in standards]
        analysis = self.llm_service.analyze_standards(standards_dict)
        
        self._record_action("analyze_standards", {
            "standards_count": len(standards)
        })
        
        return analysis
    
    def get_session_summary(self) -> Dict[str, Any]:
        """获取会话摘要"""
        return {
            "total_actions": len(self.session_history),
            "actions": self.session_history,
            "search_api_stats": self.search_api.get_stats(),
            "llm_service_stats": self.llm_service.get_stats()
        }
    
    # ==================== 扩展功能1: 用户反馈处理 ====================
    
    def evaluate_feedback(
        self,
        feedback: UserFeedback,
        lesson_plan: LessonPlan
    ) -> FeedbackEvaluation:
        """
        评估用户反馈
        
        Args:
            feedback: 用户反馈
            lesson_plan: 当前教案
            
        Returns:
            反馈评估结果
        """
        # 简单的规则评估（实际应用中可以使用LLM）
        content = feedback.content
        
        # 评估相关性
        relevance_keywords = ['增加', '删除', '修改', '调整', '添加', '优化']
        relevance_score = 0.5
        for keyword in relevance_keywords:
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
        
        # 生成推理
        reasoning = f"反馈相关性: {relevance_score:.2f}, 可行性: {feasibility_score:.2f}"
        
        evaluation = FeedbackEvaluation(
            evaluation_id=f"EVAL-{uuid.uuid4().hex[:8].upper()}",
            feedback_id=feedback.feedback_id,
            decision=decision,
            confidence=confidence,
            relevance_score=relevance_score,
            feasibility_score=feasibility_score,
            reasoning=reasoning,
            evaluated_at=datetime.now(),
            evaluated_by="ai_teacher_agent"
        )
        
        self._record_action("evaluate_feedback", {
            "feedback_id": feedback.feedback_id,
            "decision": decision,
            "confidence": confidence
        })
        
        return evaluation
    
    # ==================== 扩展功能2: 教案修改 ====================
    
    def modify_lesson_plan(
        self,
        lesson_plan: LessonPlan,
        feedback: UserFeedback,
        evaluation: FeedbackEvaluation
    ) -> Tuple[LessonPlan, LessonPlanUpdate]:
        """
        根据反馈修改教案
        
        Args:
            lesson_plan: 当前教案
            feedback: 用户反馈
            evaluation: 反馈评估
            
        Returns:
            (修改后的教案, 更新记录)
        """
        if evaluation.decision == "rejected":
            # 拒绝的反馈不修改
            update = LessonPlanUpdate(
                update_id=f"UPD-{uuid.uuid4().hex[:8].upper()}",
                plan_id=lesson_plan.plan_id,
                update_type=UpdateType.MODIFY,
                description=f"反馈被拒绝: {feedback.content[:30]}...",
                source="feedback",
                triggered_by=feedback.submitted_by,
                status=UpdateStatus.REJECTED
            )
            return lesson_plan, update
        
        # 根据反馈内容修改教案
        old_objectives = lesson_plan.teaching_objectives.copy()
        old_procedure = lesson_plan.teaching_procedure.copy()
        
        content = feedback.content
        
        # 简单的关键词匹配修改
        if "增加" in content or "添加" in content:
            if "例子" in content or "实例" in content:
                lesson_plan.add_objective("能够运用实例理解概念")
            if "练习" in content:
                lesson_plan.add_procedure_step({
                    "step": len(lesson_plan.teaching_procedure) + 1,
                    "phase": "巩固练习",
                    "duration": "10分钟",
                    "activity": "增加额外的巩固练习",
                    "method": "练习法",
                    "purpose": "强化知识掌握"
                })
        
        if "删除" in content or "减少" in content:
            if lesson_plan.teaching_procedure and len(lesson_plan.teaching_procedure) > 2:
                lesson_plan.teaching_procedure.pop()
        
        # 创建更新记录
        update = LessonPlanUpdate(
            update_id=f"UPD-{uuid.uuid4().hex[:8].upper()}",
            plan_id=lesson_plan.plan_id,
            update_type=UpdateType.MODIFY,
            description=f"根据反馈修改: {feedback.content[:50]}...",
            source="feedback",
            triggered_by=feedback.submitted_by,
            status=UpdateStatus.APPLIED
        )
        update.applied_at = datetime.now()
        
        self._record_action("modify_lesson_plan", {
            "plan_id": lesson_plan.plan_id,
            "feedback_id": feedback.feedback_id,
            "update_id": update.update_id
        })
        
        return lesson_plan, update
    
    # ==================== 扩展功能3: 教学资源搜索 ====================
    
    def search_teaching_resources(
        self,
        params: ResourceSearchParams
    ) -> ResourceSearchResult:
        """
        搜索教学资源
        
        Args:
            params: 搜索参数
            
        Returns:
            资源搜索结果
        """
        # 模拟资源数据
        mock_resources = [
            {
                "resource_id": "res-001",
                "resource_name": "函数概念PPT",
                "resource_type": "ppt",
                "content": "函数的概念和基本性质",
                "subject": "数学",
                "education_level": "高中",
                "topic": "函数的概念",
                "tags": ["函数", "概念", "PPT"],
                "rating": 4.5,
                "usage_count": 128
            },
            {
                "resource_id": "res-002",
                "resource_name": "函数练习题集",
                "resource_type": "exercise",
                "content": "函数概念练习题50道",
                "subject": "数学",
                "education_level": "高中",
                "topic": "函数的概念",
                "tags": ["函数", "练习", "题目"],
                "rating": 4.2,
                "usage_count": 89
            },
            {
                "resource_id": "res-003",
                "resource_name": "函数教学视频",
                "resource_type": "video",
                "content": "函数概念讲解视频",
                "subject": "数学",
                "education_level": "高中",
                "topic": "函数的概念",
                "tags": ["函数", "视频", "讲解"],
                "rating": 4.8,
                "usage_count": 256
            }
        ]
        
        # 过滤资源
        filtered = mock_resources
        
        if params.subject:
            filtered = [r for r in filtered if r["subject"] == params.subject]
        
        if params.education_level:
            filtered = [r for r in filtered if r["education_level"] == params.education_level]
        
        if params.topic:
            filtered = [r for r in filtered if params.topic in r["topic"]]
        
        if params.keywords:
            filtered = [r for r in filtered if params.keywords.lower() in r["resource_name"].lower()]
        
        # 分页
        total = len(filtered)
        start = (params.page - 1) * params.page_size
        end = start + params.page_size
        page_resources = filtered[start:end]
        
        result = ResourceSearchResult(
            params=params.to_dict(),
            resources=page_resources,
            total_count=total,
            page=params.page,
            page_size=params.page_size,
            search_time_ms=50,
            source="mock_resource_db"
        )
        
        self._record_action("search_resources", {
            "keywords": params.keywords,
            "subject": params.subject,
            "result_count": total
        })
        
        return result
    
    # ==================== 扩展功能4: 完整反馈循环 ====================
    
    def process_feedback_loop(
        self,
        lesson_plan: LessonPlan,
        feedback_content: str,
        submitted_by: str = "user"
    ) -> Tuple[LessonPlan, FeedbackEvaluation, LessonPlanUpdate]:
        """
        处理完整的反馈循环
        
        Args:
            lesson_plan: 当前教案
            feedback_content: 反馈内容
            submitted_by: 提交者
            
        Returns:
            (修改后的教案, 评估结果, 更新记录)
        """
        # 1. 创建反馈对象
        feedback = UserFeedback(
            feedback_id=f"FB-{uuid.uuid4().hex[:8].upper()}",
            session_id=f"sess-{uuid.uuid4().hex[:8]}",
            lesson_plan_id=lesson_plan.plan_id,
            feedback_type="modify",
            content=feedback_content,
            submitted_at=datetime.now(),
            submitted_by=submitted_by
        )
        
        # 2. 评估反馈
        evaluation = self.evaluate_feedback(feedback, lesson_plan)
        
        # 3. 根据评估修改教案
        modified_plan, update = self.modify_lesson_plan(lesson_plan, feedback, evaluation)
        
        self._record_action("feedback_loop", {
            "plan_id": lesson_plan.plan_id,
            "feedback_id": feedback.feedback_id,
            "decision": evaluation.decision
        })
        
        return modified_plan, evaluation, update
    
    # ==================== 完整功能1: 细化教学目标生成 ====================
    
    def generate_detailed_objectives(
        self,
        standards: List[CurriculumStandard],
        topic: str
    ) -> TeachingObjectives:
        """
        生成细化的三维教学目标
        
        Args:
            standards: 课程标准列表
            topic: 教学主题
            
        Returns:
            教学目标对象
        """
        # 从课标中提取要求
        all_content_reqs = []
        all_competency_reqs = []
        for std in standards:
            all_content_reqs.extend(std.content_requirements)
            all_competency_reqs.extend(std.competency_requirements)
        
        # 创建教学目标对象
        objectives = TeachingObjectives(
            objectives_id=f"OBJ-{uuid.uuid4().hex[:8].upper()}",
            knowledge_objectives=[
                f"理解{topic}的基本概念",
                f"掌握{topic}的核心原理",
                f"能够描述{topic}的主要特征"
            ],
            skill_objectives=[
                f"能够运用{topic}解决简单问题",
                "培养分析和归纳能力",
                "提升逻辑推理能力"
            ],
            process_objectives=[
                "经历从具体到抽象的探究过程",
                "体验知识形成的过程和方法"
            ],
            emotion_objectives=[
                "激发学习兴趣和求知欲",
                "培养严谨的数学思维习惯"
            ],
            competency_objectives=all_competency_reqs[:3] if all_competency_reqs else [
                "发展数学抽象素养",
                "培养逻辑推理素养"
            ],
            status=ObjectiveStatus.CONFIRMED
        )
        
        self._record_action("generate_objectives", {
            "objectives_id": objectives.objectives_id,
            "topic": topic,
            "total_objectives": len(objectives.get_all_objectives())
        })
        
        return objectives
    
    # ==================== 完整功能2: 详细教学过程设计 ====================
    
    def design_detailed_teaching_process(
        self,
        objectives: TeachingObjectives,
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
        # 计算每节课的时间（假设每节课45分钟）
        minutes_per_lesson = 45
        total_minutes = suggested_hours * minutes_per_lesson
        
        # 设计5个基本环节
        process = [
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
        
        self._record_action("design_process", {
            "total_steps": len(process),
            "total_minutes": total_minutes
        })
        
        return process
    
    # ==================== 完整功能3: 课件结构生成 ====================
    
    def generate_courseware_outline(
        self,
        lesson_plan: LessonPlan,
        objectives: TeachingObjectives
    ) -> CoursewareOutline:
        """
        生成课件结构大纲
        
        Args:
            lesson_plan: 教案
            objectives: 教学目标
            
        Returns:
            课件大纲
        """
        slides = []
        slide_num = 1
        
        # 1. 标题页
        slides.append(SlideOutline(
            slide_number=slide_num,
            slide_type=SlideType.TITLE,
            title=lesson_plan.title,
            content_points=[f"{lesson_plan.education_level}{lesson_plan.subject}"],
            layout_suggestion="居中标题，简洁背景",
            materials_needed=[],
            speaker_notes="简要介绍本节课的学习目标和内容",
            duration_minutes=1
        ))
        slide_num += 1
        
        # 2. 学习目标页
        slides.append(SlideOutline(
            slide_number=slide_num,
            slide_type=SlideType.CONTENT,
            title="学习目标",
            content_points=objectives.get_all_objectives()[:5],
            layout_suggestion="列表布局，图标点缀",
            materials_needed=["图标素材"],
            speaker_notes="明确本节课的学习目标",
            duration_minutes=2
        ))
        slide_num += 1
        
        # 3. 导入页
        slides.append(SlideOutline(
            slide_number=slide_num,
            slide_type=SlideType.TRANSITION,
            title="情境导入",
            content_points=["生活中的实例", "引发思考的问题"],
            layout_suggestion="图片+文字",
            materials_needed=["生活场景图片"],
            speaker_notes="通过实例引入新课",
            duration_minutes=3
        ))
        slide_num += 1
        
        # 4. 新授内容页（根据教学流程）
        for i, proc in enumerate(lesson_plan.teaching_procedure[:3], 1):
            # 根据详细教学过程或简化教学流程选择字段
            if 'teacher_activity' in proc:
                content = proc['teacher_activity']
                method = proc.get('design_intent', '')
            else:
                content = proc.get('activity', '教学活动')
                method = f"方法: {proc.get('method', '')}"
            
            slides.append(SlideOutline(
                slide_number=slide_num,
                slide_type=SlideType.CONTENT,
                title=f"{proc['phase']} - {i}",
                content_points=[
                    content,
                    method,
                    f"时长: {proc.get('duration', '5分钟')}"
                ],
                layout_suggestion="标题+内容",
                materials_needed=["关键概念图表"] if i == 1 else [],
                speaker_notes=content,
                duration_minutes=5
            ))
            slide_num += 1
        
        # 5. 例题页
        slides.append(SlideOutline(
            slide_number=slide_num,
            slide_type=SlideType.EXERCISE,
            title="典型例题",
            content_points=["例题展示", "解题步骤", "方法总结"],
            layout_suggestion="分步展示",
            materials_needed=["例题配图"],
            speaker_notes="讲解典型例题，强调解题方法",
            duration_minutes=5
        ))
        slide_num += 1
        
        # 6. 练习页
        slides.append(SlideOutline(
            slide_number=slide_num,
            slide_type=SlideType.EXERCISE,
            title="课堂练习",
            content_points=["练习题", "答案提示"],
            layout_suggestion="题目+留白",
            materials_needed=[],
            speaker_notes="学生练习，教师巡视",
            duration_minutes=3
        ))
        slide_num += 1
        
        # 7. 小结页
        slides.append(SlideOutline(
            slide_number=slide_num,
            slide_type=SlideType.SUMMARY,
            title="课堂小结",
            content_points=lesson_plan.teaching_objectives[:3],
            layout_suggestion="思维导图或列表",
            materials_needed=["总结图表"],
            speaker_notes="总结本节课的重点内容",
            duration_minutes=2
        ))
        slide_num += 1
        
        # 8. 作业页
        slides.append(SlideOutline(
            slide_number=slide_num,
            slide_type=SlideType.CONTENT,
            title="课后作业",
            content_points=["基础题：巩固概念", "提高题：拓展应用"],
            layout_suggestion="分层展示",
            materials_needed=[],
            speaker_notes="布置分层作业",
            duration_minutes=1
        ))
        
        outline = CoursewareOutline(
            outline_id=f"CW-{uuid.uuid4().hex[:8].upper()}",
            plan_id=lesson_plan.plan_id,
            title=f"{lesson_plan.title}课件",
            slides=slides,
            design_theme="简洁教育风格",
            color_scheme="蓝色系",
            font_suggestion="微软雅黑"
        )
        
        self._record_action("generate_courseware", {
            "outline_id": outline.outline_id,
            "plan_id": lesson_plan.plan_id,
            "total_slides": outline.total_slides
        })
        
        return outline
    
    # ==================== 完整功能4: 完整备课流程 ====================
    
    def complete_lesson_preparation(
        self,
        course_info: CourseBasicInfo
    ) -> Dict[str, Any]:
        """
        执行完整的备课流程
        
        Args:
            course_info: 课程基本信息
            
        Returns:
            完整的备课结果
        """
        print(f"\n开始为《{course_info.topic}》备课...")
        
        # 1. 搜索课标
        print("  [1/6] 搜索课程标准...")
        _, standards = self.search_curriculum_standards(course_info)
        print(f"        找到 {len(standards)} 条相关课标")
        
        # 2. 分析课标
        print("  [2/6] 分析课标要求...")
        analysis = self.analyze_standards(standards)
        suggested_hours = standards[0].suggested_hours if standards else 2
        
        # 3. 生成教学目标
        print("  [3/6] 生成教学目标...")
        objectives = self.generate_detailed_objectives(standards, course_info.topic)
        print(f"        生成 {len(objectives.get_all_objectives())} 个目标")
        
        # 4. 生成教案
        print("  [4/6] 生成教案...")
        lesson_plan = self.generate_lesson_plan(course_info, standards)
        
        # 5. 设计详细教学过程
        print("  [5/6] 设计教学过程...")
        detailed_process = self.design_detailed_teaching_process(
            objectives,
            suggested_hours,
            key_points=analysis.get("key_points", []),
            difficult_points=analysis.get("difficult_points", [])
        )
        lesson_plan.teaching_procedure = detailed_process
        print(f"        设计 {len(detailed_process)} 个教学环节")
        
        # 6. 生成课件大纲
        print("  [6/6] 生成课件大纲...")
        courseware = self.generate_courseware_outline(lesson_plan, objectives)
        print(f"        生成 {courseware.total_slides} 页课件")
        
        # 搜索教学资源
        print("  [附加] 搜索教学资源...")
        resource_params = ResourceSearchParams(
            keywords=course_info.topic,
            subject=course_info.subject,
            education_level=course_info.education_level
        )
        resources = self.search_teaching_resources(resource_params)
        print(f"        找到 {resources.total_count} 个资源")
        
        result = {
            "course_info": course_info.to_dict(),
            "standards": [s.to_dict() for s in standards],
            "objectives": objectives.to_dict(),
            "lesson_plan": lesson_plan.to_dict(),
            "courseware": courseware.to_dict(),
            "resources": resources.to_dict(),
            "analysis": analysis
        }
        
        self._record_action("complete_preparation", {
            "topic": course_info.topic,
            "plan_id": lesson_plan.plan_id,
            "slides_count": courseware.total_slides
        })
        
        print("\n备课完成！")
        return result
    
    def _record_action(self, action_type: str, data: Dict[str, Any]) -> None:
        """记录操作历史"""
        self.session_history.append({
            "action": action_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        })
