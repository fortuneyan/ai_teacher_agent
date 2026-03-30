# AI教师Agent系统架构设计

> 基于《Agent开发指南》最佳实践的完整实现方案

---

## 一、系统总体架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AI教师Agent系统                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   教师端UI    │  │   学生端UI    │  │   管理后台    │  │   移动端APP   │   │
│  │  (Web/React) │  │  (Web/React) │  │   (Admin)    │  │  (Flutter)   │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
│         │                 │                 │                 │           │
│         └─────────────────┴─────────────────┴─────────────────┘           │
│                                    │                                       │
│                    ┌───────────────┴───────────────┐                       │
│                    │      API Gateway (FastAPI)    │                       │
│                    │    • 统一认证 • 限流 • 路由    │                       │
│                    └───────────────┬───────────────┘                       │
│                                    │                                       │
├────────────────────────────────────┼───────────────────────────────────────┤
│                                    ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                      AI教师Agent核心层                               │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  │  │
│  │  │  Context    │  │   Memory    │  │   Planner   │  │   Skills   │  │  │
│  │  │  Manager    │  │   System    │  │   (ReAct)   │  │   Engine   │  │  │
│  │  │  (第2章)    │  │  (第6-7章)  │  │   (第9章)   │  │  (第5章)   │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘  │  │
│  │                                                                       │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  │  │
│  │  │   Tools     │  │  Pipeline   │  │  Self-Evol  │  │   RAG      │  │  │
│  │  │  (第4章)    │  │  (第11章)   │  │  (第14章)   │  │  (第8章)   │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘  │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                    │                                       │
├────────────────────────────────────┼───────────────────────────────────────┤
│                                    ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                         技能层 (Skills)                              │  │
│  │                                                                       │  │
│  │  备课技能                    授课技能              评估技能          │  │
│  │  ├─ 课标搜索                 ├─ 实时问答          ├─ 智能出题       │  │
│  │  ├─ 教材获取                 ├─ 练习生成          ├─ 自动批改       │  │
│  │  ├─ 教案设计                 ├─ 理解度监测        ├─ 学情分析       │  │
│  │  ├─ 课件生成                 ├─ 智能板书          ├─ 反馈生成       │  │
│  │  └─ 计划编排                 └─ 课堂总结          └─ 报告生成       │  │
│  │                                                                       │  │
│  │  优化技能                    通用技能                                 │  │
│  │  ├─ 反思引导                 ├─ 内容搜索                              │  │
│  │  ├─ 数据分析                 ├─ 文件操作                              │  │
│  │  ├─ 教案优化                 ├─ 通知推送                              │  │
│  │  └─ 课件更新                 └─ 数据可视化                            │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                    │                                       │
├────────────────────────────────────┼───────────────────────────────────────┤
│                                    ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                        基础设施层                                     │  │
│  │                                                                       │  │
│  │  LLM服务        向量数据库       关系数据库       文件存储            │  │
│  │  ├─ OpenAI      ├─ Milvus       ├─ PostgreSQL    ├─ MinIO           │  │
│  │  ├─ Claude      ├─ Pinecone     ├─ MySQL         ├─ OSS             │  │
│  │  ├─ 本地模型     └─ Qdrant       └─ SQLite        └─ Local           │  │
│  │  └─ 多模型路由                                                        │  │
│  │                                                                       │  │
│  │  消息队列       缓存系统         搜索引擎         监控告警            │  │
│  │  ├─ Redis       ├─ Redis        ├─ Elasticsearch ├─ Prometheus       │  │
│  │  └─ RabbitMQ    └─ Memcached    └─ Meilisearch   └─ Grafana          │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 二、核心组件详解

### 2.1 Context管理器（第2章实践）

```python
class TeacherContextManager:
    """
    教师Agent的Context管理器
    整合四大要素：System + RAG + History + User
    """
    
    def __init__(self, config: TeacherConfig):
        self.system_prompt = self._build_teacher_system_prompt()
        self.rag_retriever = CourseMaterialRetriever()
        self.session_memory = SessionMemory()  # 短期记忆
        self.long_term_memory = LongTermMemory()  # 长期记忆
    
    def build_context(self, user_input: str, scene: str) -> List[Message]:
        """
        根据场景构建上下文
        
        scene: "备课" | "授课" | "评估" | "优化"
        """
        messages = []
        
        # 1. System Message - 宪法层
        messages.append(self._get_scene_system_prompt(scene))
        
        # 2. RAG Context - 知识层（课标、教材、教案）
        relevant_materials = self.rag_retriever.retrieve(user_input)
        messages.extend(self._format_rag_context(relevant_materials))
        
        # 3. Long-term Memory - 经验层（历史教学数据）
        similar_cases = self.long_term_memory.query_similar(user_input)
        messages.extend(self._format_memory_context(similar_cases))
        
        # 4. Session History - 对话层
        messages.extend(self.session_memory.get_recent(10))
        
        # 5. User Input - 触发层
        messages.append(Message(role="user", content=user_input))
        
        return messages
```

### 2.2 记忆系统设计（第6-7章实践）

```
┌─────────────────────────────────────────────────────────────┐
│                     教师Agent记忆系统                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  短期记忆 (Session)                  │   │
│  │  • 当前课堂对话历史                                   │   │
│  │  • 实时互动状态                                      │   │
│  │  • 临时计算结果                                      │   │
│  │  TTL: 会话结束清除                                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                            │                                │
│                            ▼                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              工作记忆 (Working)                      │   │
│  │  • 当前课程信息（课程名、班级、进度）                  │   │
│  │  • 当前学生列表和状态                                │   │
│  │  • 本次课的教学目标                                  │   │
│  │  TTL: 课程结束归档到长期记忆                          │   │
│  └─────────────────────────────────────────────────────┘   │
│                            │                                │
│                            ▼                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              长期记忆 (Long-term)                    │   │
│  │                                                      │   │
│  │  教师画像层:                                          │   │
│  │  • 教学风格偏好（严谨/活泼/互动型）                   │   │
│  │  • 常用教学方法                                      │   │
│  │  • 时间分配习惯                                      │   │
│  │                                                      │   │
│  │  课程知识层:                                          │   │
│  │  • 已授课程的历史数据                                │   │
│  │  • 各知识点的教学效果                                │   │
│  │  • 学生常见错误模式                                  │   │
│  │                                                      │   │
│  │  学生画像层:                                          │   │
│  │  • 每个学生的学习历史                                │   │
│  │  • 掌握程度追踪                                      │   │
│  │  • 个性化学习路径                                    │   │
│  │                                                      │   │
│  │  反思优化层:                                          │   │
│  │  • 课后反思记录                                      │   │
│  │  • 教案迭代历史                                      │   │
│  │  • 教学策略效果评估                                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                            │                                │
│                            ▼                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              向量记忆 (Vector Store)                 │   │
│  │  • 教案文档嵌入                                       │   │
│  │  • 课件内容嵌入                                       │   │
│  │  • 课标内容嵌入                                       │   │
│  │  • 相似性检索支持                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 技能体系设计（第5章实践）

```python
# 技能注册表
SKILL_REGISTRY = {
    # 备课技能
    "curriculum.search": {
        "name": "搜索课程标准",
        "description": "根据课程名称搜索并解析课程标准",
        "input": {"course_name": "str", "education_level": "str"},
        "output": {"standards": "List[Standard]"},
        "dependencies": [],
    },
    "material.collect": {
        "name": "收集教材内容",
        "description": "获取教材电子版并解析内容结构",
        "input": {"textbook_info": "TextbookInfo"},
        "output": {"chapters": "List[Chapter]"},
        "dependencies": [],
    },
    "lesson.design": {
        "name": "设计教案",
        "description": "基于课标和教材设计详细教案",
        "input": {"standards": "List[Standard]", "materials": "List[Chapter]"},
        "output": {"lesson_plan": "LessonPlan"},
        "dependencies": ["curriculum.search", "material.collect"],
    },
    "ppt.generate": {
        "name": "生成课件",
        "description": "将教案转化为PPT课件",
        "input": {"lesson_plan": "LessonPlan", "style": "StyleConfig"},
        "output": {"ppt_content": "PPTContent"},
        "dependencies": ["lesson.design"],
    },
    "schedule.plan": {
        "name": "编排教学计划",
        "description": "制定学期教学进度计划",
        "input": {"course_info": "CourseInfo", "constraints": "Constraints"},
        "output": {"schedule": "Schedule"},
        "dependencies": ["lesson.design"],
    },
    
    # 授课技能
    "classroom.qa": {
        "name": "实时问答",
        "description": "课堂实时问答互动",
        "input": {"question": "str", "context": "ClassContext"},
        "output": {"answer": "str", "follow_up": "List[str]"},
        "dependencies": [],
    },
    "classroom.exercise": {
        "name": "生成课堂练习",
        "description": "根据当前知识点生成针对性练习",
        "input": {"topic": "str", "difficulty": "str", "count": "int"},
        "output": {"exercises": "List[Exercise]"},
        "dependencies": [],
    },
    "classroom.monitor": {
        "name": "理解度监测",
        "description": "监测学生理解程度",
        "input": {"interactions": "List[Interaction]"},
        "output": {"understanding_level": "Dict[str, float]"},
        "dependencies": [],
    },
    
    # 评估技能
    "assessment.generate": {
        "name": "智能出题",
        "description": "生成符合要求的试题",
        "input": {"topics": "List[str]", "difficulty_dist": "Dict", "types": "List[str]"},
        "output": {"questions": "List[Question]"},
        "dependencies": [],
    },
    "assessment.grade": {
        "name": "自动批改",
        "description": "自动批改作业和试卷",
        "input": {"answers": "List[Answer]", "rubric": "Rubric"},
        "output": {"grades": "List[Grade]"},
        "dependencies": [],
    },
    "assessment.analyze": {
        "name": "学情分析",
        "description": "分析班级学习情况",
        "input": {"grades": "List[Grade]", "history": "List[History]"},
        "output": {"analysis": "LearningAnalysis"},
        "dependencies": ["assessment.grade"],
    },
    
    # 优化技能
    "reflection.guide": {
        "name": "反思引导",
        "description": "引导教师进行课后反思",
        "input": {"class_data": "ClassData"},
        "output": {"reflection_questions": "List[str]"},
        "dependencies": [],
    },
    "lesson.optimize": {
        "name": "优化教案",
        "description": "基于反思数据优化教案",
        "input": {"lesson_plan": "LessonPlan", "reflection": "Reflection"},
        "output": {"optimized_plan": "LessonPlan"},
        "dependencies": ["reflection.guide"],
    },
}
```

### 2.4 Pipeline编排（第11章实践）

```python
# 备课流程Pipeline
class LessonPreparationPipeline:
    """备课流程编排"""
    
    def __init__(self):
        self.pipeline = Pipeline("lesson_preparation")
        self._build_pipeline()
    
    def _build_pipeline(self):
        # 阶段1: 信息收集（并行）
        self.pipeline.add_parallel([
            Node("search_curriculum", skill="curriculum.search"),
            Node("collect_materials", skill="material.collect"),
        ])
        
        # 阶段2: 教案设计（依赖阶段1）
        self.pipeline.add_node(
            Node("design_lesson", skill="lesson.design"),
            dependencies=["search_curriculum", "collect_materials"]
        )
        
        # 阶段3: 资源生成（并行，依赖阶段2）
        self.pipeline.add_parallel([
            Node("generate_ppt", skill="ppt.generate"),
            Node("create_exercises", skill="assessment.generate"),
        ], dependencies=["design_lesson"])
        
        # 阶段4: 计划编排（依赖阶段2）
        self.pipeline.add_node(
            Node("plan_schedule", skill="schedule.plan"),
            dependencies=["design_lesson"]
        )
    
    async def execute(self, course_info: CourseInfo) -> PipelineResult:
        """执行备课流程"""
        context = {"course_info": course_info}
        return await self.pipeline.execute(context)


# 授课流程Pipeline（实时交互）
class ClassroomPipeline:
    """课堂实时交互流程"""
    
    async def handle_interaction(self, interaction: Interaction) -> Response:
        """处理课堂互动"""
        
        # 理解学生意图
        intent = await self.intent_classifier.classify(interaction)
        
        # 根据意图路由到不同处理流程
        if intent.type == "question":
            return await self._handle_question(intent)
        elif intent.type == "exercise_request":
            return await self._handle_exercise_request(intent)
        elif intent.type == "confusion_signal":
            return await self._handle_confusion(intent)
        elif intent.type == "summary_request":
            return await self._handle_summary(intent)
        
    async def _handle_question(self, intent: Intent) -> Response:
        """处理学生提问"""
        # 检索相关知识
        context = await self.rag_retriever.retrieve(intent.content)
        
        # 生成回答
        answer = await self.llm.generate(
            context=self.context_manager.build_context(intent.content, scene="授课"),
            question=intent.content
        )
        
        # 生成追问建议
        follow_ups = await self._generate_follow_up_questions(intent, answer)
        
        return Response(content=answer, follow_ups=follow_ups)
```

### 2.5 自我进化机制（第14章实践）

```python
class TeacherAgentEvolution:
    """教师Agent自我进化系统"""
    
    def __init__(self):
        self.reflection_engine = ReflectionEngine()
        self.optimization_engine = OptimizationEngine()
        self.knowledge_accumulator = KnowledgeAccumulator()
    
    async def post_class_evolution(self, class_data: ClassData):
        """课后自我进化流程"""
        
        # 1. 生成反思报告
        reflection = await self.reflection_engine.generate(
            class_data=class_data,
            teacher_feedback=class_data.teacher_feedback
        )
        
        # 2. 分析教学效果
        effectiveness = await self._analyze_teaching_effectiveness(
            lesson_plan=class_data.lesson_plan,
            student_performance=class_data.student_performance,
            interaction_data=class_data.interactions
        )
        
        # 3. 识别改进点
        improvements = await self._identify_improvements(
            reflection=reflection,
            effectiveness=effectiveness
        )
        
        # 4. 生成优化建议
        suggestions = await self.optimization_engine.generate_suggestions(
            lesson_plan=class_data.lesson_plan,
            improvements=improvements
        )
        
        # 5. 更新知识库
        await self.knowledge_accumulator.accumulate(
            lesson_id=class_data.lesson_id,
            reflection=reflection,
            effectiveness=effectiveness,
            suggestions=suggestions
        )
        
        # 6. 更新教师画像
        await self._update_teacher_profile(class_data.teacher_id, reflection)
        
        return EvolutionReport(
            reflection=reflection,
            suggestions=suggestions,
            updated_lesson_plan=await self._apply_suggestions(
                class_data.lesson_plan, suggestions
            )
        )
```

---

## 三、实时交互UI设计

### 3.1 教师端界面

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  AI教师助手 - 教师端                                    [课程: 高中数学-函数]  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐  ┌─────────────────────────────────────────────────────┐ │
│  │   功能导航    │  │              主工作区                               │ │
│  │              │  │                                                     │ │
│  │  📚 备课中心  │  │  ┌─────────────────────────────────────────────┐  │ │
│  │     • 教案设计│  │  │           智能备课助手                         │  │ │
│  │     • 课件生成│  │  │                                              │  │ │
│  │     • 计划编排│  │  │  [输入框] 请输入课程主题...                    │  │ │
│  │              │  │  │                                              │  │ │
│  │  🎓 授课助手  │  │  │  ┌─────────────────────────────────────────┐ │  │ │
│  │     • 实时问答│  │  │  │  🤖 AI: 我来帮您设计这节课。             │ │  │ │
│  │     • 练习生成│  │  │  │     首先，我需要了解：                    │ │  │ │
│  │     • 课堂监测│  │  │  │     1. 课程名称和年级                     │ │  │ │
│  │              │  │  │  │     2. 课时安排                           │ │  │ │
│  │  📊 学情分析  │  │  │  │     3. 学生基础水平                       │ │  │ │
│  │     • 成绩统计│  │  │  │                                          │ │  │ │
│  │     • 知识图谱│  │  │  │  [快速开始] [上传课标] [选择模板]         │ │  │ │
│  │     • 个性化  │  │  │  └─────────────────────────────────────────┘ │  │ │
│  │              │  │  │                                              │  │ │
│  │  🔄 优化中心  │  │  │  [流式输出区域 - 实时显示AI生成内容]          │  │ │
│  │     • 课后反思│  │  │                                              │  │ │
│  │     • 教案优化│  │  │  ▶ 正在生成教案...                           │  │ │
│  │     • 数据洞察│  │  │    [████████████████████░░░░░░░░] 65%       │  │ │
│  │              │  │  │                                              │  │ │
│  │  📁 资源库    │  │  └─────────────────────────────────────────────┘  │ │
│  │              │  │                                                     │ │
│  └──────────────┘  │  ┌─────────────────────────────────────────────────┐ │
│                    │  │              辅助面板                            │ │
│  ┌──────────────┐  │  │  ┌─────────────┐  ┌─────────────┐  ┌────────┐ │ │
│  │   快捷操作    │  │  │  │ 课标参考    │  │ 相似教案    │  │ 学生状态│ │ │
│  │              │  │  │  │ [查看详情]  │  │ [查看详情]  │  │ [查看] │ │ │
│  │  [快速出题]  │  │  │  └─────────────┘  └─────────────┘  └────────┘ │ │
│  │  [生成练习]  │  │  │                                                 │ │
│  │  [课堂总结]  │  │  │  最近使用:                                      │ │
│  │  [发布作业]  │  │  │  • 函数概念教案 v2.3                           │ │
│  └──────────────┘  │  │  • 指数函数课件                                │ │
│                    │  │  • 期中测试卷A                                │ │
│                    │  └─────────────────────────────────────────────────┘ │
│                    └─────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 学生端界面（课堂互动）

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         课堂互动 - 学生端                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        当前课程: 函数的概念                          │   │
│  │                        教师: 张老师                                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────┐  ┌─────────────────────────────────────┐  │
│  │        互动区域              │  │           学习辅助区                 │  │
│  │                              │  │                                     │  │
│  │  [🎤 举手提问]  [✋ 表示不懂] │  │  ┌─────────────────────────────┐   │  │
│  │                              │  │  │      当前知识点              │   │  │
│  │  ┌─────────────────────────┐ │  │  │                              │   │  │
│  │  │    实时问答              │ │  │  │  📌 函数的定义               │   │  │
│  │  │                         │ │  │  │                              │   │  │
│  │  │ 学生: 为什么x²是函数？  │ │  │  │  设A、B是非空数集...         │   │  │
│  │  │                         │ │  │  │                              │   │  │
│  │  │ AI助教: 因为对于每一个  │ │  │  │  [查看详细解释] [相关例题]   │   │  │
│  │  │ x值，都有唯一的y值对应  │ │  │  │                              │   │  │
│  │  │ ...                     │ │  │  └─────────────────────────────┘   │  │
│  │  │                         │ │  │                                     │  │
│  │  │ [👍 明白了] [❓ 还有疑问]│ │  │  ┌─────────────────────────────┐   │  │
│  │  └─────────────────────────┘ │  │  │      随堂练习                │   │  │
│  │                              │  │  │                              │   │  │
│  │  [📝 我要练习] [📊 我的理解度]│  │  │  1. 判断下列是否为函数...    │   │  │
│  │                              │  │  │                              │   │  │
│  └─────────────────────────────┘  │  │  [A] [B] [C] [D]            │   │  │
│                                   │  │                              │   │  │
│                                   │  │  [提交答案]                  │   │  │
│                                   │  │                              │   │  │
│                                   │  └─────────────────────────────┘   │  │
│                                   │                                     │  │
│                                   │  ┌─────────────────────────────┐   │  │
│                                   │  │      学习进度               │   │  │
│                                   │  │                              │   │  │
│                                   │  │  本节课掌握度: 75%           │   │  │
│                                   │  │  [████████████░░░░]          │   │  │
│                                   │  │                              │   │  │
│                                   │  │  待强化: 函数表示法          │   │  │
│                                   │  └─────────────────────────────┘   │  │
│                                   └─────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.3 实时交互流程

```
教师/学生输入
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│                    意图识别 (Intent Classifier)              │
│  • 问题类型: 概念性/计算性/应用性                             │
│  • 紧急程度: 立即回答/课后处理                               │
│  • 涉及知识点: 自动关联当前课程内容                           │
└─────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│                    上下文构建 (Context Builder)              │
│  • 检索相关课标内容                                          │
│  • 查询相似历史问题                                          │
│  • 获取学生个人学习历史                                      │
│  • 整合当前课堂进度                                          │
└─────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│                    LLM推理 (Streaming)                       │
│  • 流式输出回答                                              │
│  • 实时显示思考过程                                          │
│  • 支持打断和追问                                            │
└─────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│                    多模态输出                                │
│  • 文字回答                                                  │
│  • 公式渲染 (LaTeX)                                          │
│  • 图表生成                                                  │
│  • 语音播报 (可选)                                           │
└─────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│                    交互记录与学习                             │
│  • 记录问答到短期记忆                                        │
│  • 更新学生理解度模型                                        │
│  • 触发后续推荐 (相关练习/拓展阅读)                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 四、技术实现要点

### 4.1 实时通信方案

```python
# FastAPI + WebSocket 实现实时交互
from fastapi import FastAPI, WebSocket
from fastapi.responses import StreamingResponse

app = FastAPI()

@app.websocket("/ws/classroom/{class_id}")
async def classroom_websocket(websocket: WebSocket, class_id: str):
    """课堂实时WebSocket连接"""
    await websocket.accept()
    
    # 加入课堂房间
    await manager.join_class(class_id, websocket)
    
    try:
        while True:
            # 接收消息
            message = await websocket.receive_json()
            
            # 根据消息类型处理
            if message["type"] == "question":
                # 流式返回答案
                async for chunk in teacher_agent.answer_question(
                    question=message["content"],
                    student_id=message["student_id"],
                    class_context=await get_class_context(class_id)
                ):
                    await websocket.send_json({
                        "type": "answer_chunk",
                        "content": chunk
                    })
                    
            elif message["type"] == "exercise_request":
                # 生成练习
                exercises = await teacher_agent.generate_exercises(
                    topic=message["topic"],
                    difficulty=message["difficulty"],
                    student_level=await get_student_level(message["student_id"])
                )
                await websocket.send_json({
                    "type": "exercises",
                    "content": exercises
                })
                
    except Exception as e:
        await manager.leave_class(class_id, websocket)


# SSE 用于单向流式输出（适合AI生成内容）
@app.get("/api/lesson/generate")
async def generate_lesson_plan(params: LessonParams):
    """流式生成教案"""
    
    async def event_generator():
        async for chunk in teacher_agent.generate_lesson_plan_stream(
            course_name=params.course_name,
            hours=params.hours,
            audience=params.audience
        ):
            yield f"data: {json.dumps({'content': chunk})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

### 4.2 多模型路由

```python
class ModelRouter:
    """根据任务类型路由到不同模型"""
    
    ROUTING_RULES = {
        # 备课任务 -> 强模型（需要创造性）
        "lesson_design": {"model": "gpt-4", "temperature": 0.7},
        "ppt_generation": {"model": "claude-3-opus", "temperature": 0.8},
        
        # 授课任务 -> 快速模型（需要实时性）
        "classroom_qa": {"model": "gpt-4-turbo", "temperature": 0.3},
        "exercise_generation": {"model": "gpt-3.5-turbo", "temperature": 0.5},
        
        # 评估任务 -> 稳定模型（需要准确性）
        "grading": {"model": "gpt-4", "temperature": 0.0},
        "analysis": {"model": "claude-3-sonnet", "temperature": 0.2},
    }
    
    async def route(self, task_type: str, content: str) -> ModelResponse:
        config = self.ROUTING_RULES.get(task_type, self.DEFAULT_CONFIG)
        model = self.get_model(config["model"])
        return await model.generate(content, temperature=config["temperature"])
```

---

## 五、与现有项目的整合

基于现有 `ai_teacher_agent` 项目，需要增强的部分：

1. **新增技能模块**：
   - `classroom/` - 授课相关技能
   - `assessment/` - 评估相关技能
   - `optimization/` - 优化相关技能

2. **增强记忆系统**：
   - 实现长期记忆存储
   - 添加学生画像管理
   - 集成向量检索

3. **添加实时交互层**：
   - WebSocket 服务
   - 流式输出支持
   - 多模态输出

4. **构建UI层**：
   - 教师端 React 应用
   - 学生端轻量界面
   - 管理后台

---

**下一步**：开始实现核心技能模块。
