# 函数规格：评估用户反馈

## 函数标识

- **函数ID**: FN-LP-007
- **函数名称**: evaluate_user_feedback
- **所属功能点**: FP-LP-007
- **所属模块**: lesson_preparation
- **创建日期**: 2026-03-22

---

## 1. 功能描述

### 1.1 功能概述
智能评估用户反馈的合理性、相关性、可行性，决定如何处理（接受/拒绝/需要澄清）。

### 1.2 详细说明
1. 基础有效性检查（长度、格式、广告检测）
2. 相关性评估（反馈与教案内容的关联度）
3. 可行性评估（修改的技术难度）
4. 综合决策（接受/拒绝/需澄清）
5. 生成评估理由和替代建议

### 1.3 业务规则
- BR-019: 相关性阈值：≥0.5为相关，<0.5为不相关
- BR-020: 必须解释拒绝原因并提供替代建议
- BR-021: 模糊反馈必须要求澄清
- BR-025: 广告/垃圾内容直接拒绝
- BR-026: 恶意内容触发安全警告

---

## 2. 接口定义

### 2.1 函数签名

```python
async def evaluate_user_feedback(
    feedback: UserFeedback,
    current_lesson_plan: LessonPlan,
    evaluation_config: Optional[EvaluationConfig] = None
) -> FeedbackEvaluation:
    """
    评估用户反馈
    
    Args:
        feedback: 用户反馈对象
        current_lesson_plan: 当前教案
        evaluation_config: 评估配置（可选）
        
    Returns:
        反馈评估结果
        
    Raises:
        ValueError: 输入参数无效
        EvaluationError: 评估过程异常
    """
    pass
```

### 2.2 输入参数

| 参数名 | 类型 | 必填 | 默认值 | 约束 | 说明 |
|-------|------|-----|--------|------|------|
| feedback | UserFeedback | 是 | - | 已验证 | 用户反馈 |
| current_lesson_plan | LessonPlan | 是 | - | - | 当前教案 |
| evaluation_config | EvaluationConfig | 否 | None | - | 评估配置 |

**EvaluationConfig 结构**:
```python
{
    "relevance_threshold": float,      # 相关性阈值，默认0.5
    "feasibility_threshold": float,    # 可行性阈值，默认0.3
    "confidence_threshold": float,     # 置信度阈值，默认0.7
    "auto_accept_threshold": float,    # 自动接受阈值，默认0.8
    "auto_reject_threshold": float,    # 自动拒绝阈值，默认0.2
    "use_llm": bool,                   # 是否使用LLM增强，默认True
    "llm_model": str                   # LLM模型名称
}
```

### 2.3 返回值

**FeedbackEvaluation 结构**:
```python
{
    "evaluation_id": str,              # 评估标识
    "feedback_id": str,                # 关联反馈
    "decision": str,                   # 决策：accepted/rejected/needs_clarification
    "confidence": float,               # 置信度0-1
    "relevance_score": float,          # 相关性评分
    "feasibility_score": float,        # 可行性评分
    "reasoning": str,                  # 评估理由
    "alternative_suggestion": str,     # 替代建议（如拒绝时）
    "clarification_question": str,     # 澄清问题（如需澄清时）
    "evaluated_at": datetime,          # 评估时间
    "evaluated_by": str                # 评估者
}
```

### 2.4 异常定义

| 异常类型 | 触发条件 | 错误码 | 错误信息 |
|---------|---------|--------|---------|
| ValueError | feedback无效 | E101 | "Invalid feedback: {detail}" |
| ValueError | lesson_plan无效 | E102 | "Invalid lesson_plan" |
| EvaluationError | 评估失败 | E103 | "Evaluation failed: {detail}" |
| SafetyError | 检测到恶意内容 | E104 | "Safety violation detected" |

---

## 3. 伪代码

```
FUNCTION evaluate_user_feedback(feedback, current_lesson_plan, evaluation_config):
    
    // 1. 输入验证
    IF feedback IS NULL:
        RAISE ValueError("feedback cannot be null")
    
    IF current_lesson_plan IS NULL:
        RAISE ValueError("lesson_plan cannot be null")
    
    IF NOT validate_user_feedback(feedback):
        RAISE ValueError("feedback validation failed")
    
    // 2. 初始化配置
    config = evaluation_config OR DEFAULT_EVALUATION_CONFIG
    
    // 3. 基础有效性检查
    validity_result = CHECK_BASIC_VALIDITY(feedback.content)
    
    IF validity_result.is_spam:
        RETURN CREATE_EVALUATION(
            decision="rejected",
            confidence=0.95,
            relevance_score=0.0,
            feasibility_score=0.0,
            reasoning="检测到垃圾广告内容，不予处理",
            alternative_suggestion="请提供与教学相关的反馈"
        )
    
    IF validity_result.is_malicious:
        RAISE SafetyError("Detected malicious content in feedback")
    
    IF validity_result.is_too_short:
        RETURN CREATE_EVALUATION(
            decision="needs_clarification",
            confidence=0.9,
            reasoning="反馈内容过短，无法准确理解您的意图",
            clarification_question="请详细描述您的修改建议，包括具体章节和修改方向"
        )
    
    // 4. 相关性评估
    relevance_score = CALCULATE_RELEVANCE(feedback, current_lesson_plan)
    
    IF relevance_score < config.relevance_threshold:
        // 不相关，拒绝
        alternative = GENERATE_ALTERNATIVE_SUGGESTION(feedback, current_lesson_plan)
        RETURN CREATE_EVALUATION(
            decision="rejected",
            confidence=0.85,
            relevance_score=relevance_score,
            feasibility_score=0.0,
            reasoning=f"您的反馈与当前课程主题'{current_lesson_plan.course_info.topic}'关联度较低（{relevance_score:.2f}）",
            alternative_suggestion=alternative
        )
    
    // 5. 可行性评估
    feasibility_score = CALCULATE_FEASIBILITY(feedback, current_lesson_plan)
    
    IF feasibility_score < config.feasibility_threshold:
        // 难以实现，需要澄清
        clarification = GENERATE_CLARIFICATION_QUESTION(feedback)
        RETURN CREATE_EVALUATION(
            decision="needs_clarification",
            confidence=0.75,
            relevance_score=relevance_score,
            feasibility_score=feasibility_score,
            reasoning="您的建议实现难度较高，需要更多信息",
            clarification_question=clarification
        )
    
    // 6. 使用LLM增强评估（如启用）
    IF config.use_llm:
        llm_evaluation = AWAIT llm_enhanced_evaluation(
            feedback=feedback,
            lesson_plan=current_lesson_plan,
            initial_scores={
                "relevance": relevance_score,
                "feasibility": feasibility_score
            }
        )
        
        // 融合规则评估和LLM评估
        relevance_score = FUSE_SCORES(relevance_score, llm_evaluation.relevance)
        feasibility_score = FUSE_SCORES(feasibility_score, llm_evaluation.feasibility)
    
    // 7. 综合决策
    overall_score = CALCULATE_OVERALL_SCORE(relevance_score, feasibility_score)
    
    IF overall_score >= config.auto_accept_threshold:
        decision = "accepted"
        confidence = overall_score
        reasoning = GENERATE_ACCEPT_REASONING(feedback, relevance_score, feasibility_score)
        
    ELSE IF overall_score <= config.auto_reject_threshold:
        decision = "rejected"
        confidence = 1.0 - overall_score
        reasoning = GENERATE_REJECT_REASONING(feedback)
        alternative = GENERATE_ALTERNATIVE_SUGGESTION(feedback, current_lesson_plan)
        
    ELSE:
        decision = "needs_clarification"
        confidence = 0.6
        reasoning = "需要更多信息以确定如何处理您的反馈"
        clarification = GENERATE_CLARIFICATION_QUESTION(feedback)
    
    // 8. 构建评估结果
    evaluation = FeedbackEvaluation(
        evaluation_id=GENERATE_UUID(),
        feedback_id=feedback.feedback_id,
        decision=decision,
        confidence=confidence,
        relevance_score=relevance_score,
        feasibility_score=feasibility_score,
        reasoning=reasoning,
        alternative_suggestion=alternative IF decision == "rejected" ELSE None,
        clarification_question=clarification IF decision == "needs_clarification" ELSE None,
        evaluated_at=NOW(),
        evaluated_by="system"
    )
    
    // 9. 记录日志
    LOG_INFO(f"Feedback {feedback.feedback_id} evaluated: {decision} (confidence: {confidence:.2f})")
    
    RETURN evaluation

END FUNCTION

// 辅助函数：基础有效性检查
FUNCTION CHECK_BASIC_VALIDITY(content):
    result = ValidityResult()
    
    // 检查长度
    IF LENGTH(content) < 5:
        result.is_too_short = True
        RETURN result
    
    // 检查广告模式
    spam_patterns = [
        r"http[s]?://",           # URL
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # 邮箱
        r"加.*微信",              # 加微信
        r"扫码",                  # 扫码
        r"优惠.*购买",            # 优惠购买
        r"点击.*链接"             # 点击链接
    ]
    
    FOR pattern IN spam_patterns:
        IF REGEX_MATCH(content, pattern):
            result.is_spam = True
            RETURN result
    
    // 检查恶意内容（简化版，实际应使用内容安全API）
    malicious_keywords = ["垃圾", "废物", "去死"]  // 示例
    FOR keyword IN malicious_keywords:
        IF keyword IN content:
            result.is_malicious = True
            RETURN result
    
    result.is_valid = True
    RETURN result
END FUNCTION

// 辅助函数：计算相关性
FUNCTION CALCULATE_RELEVANCE(feedback, lesson_plan):
    scores = []
    
    // 与主题的文本相似度
    topic_similarity = TEXT_SIMILARITY(
        feedback.content,
        lesson_plan.course_info.topic
    )
    scores.APPEND(topic_similarity * 0.3)
    
    // 与目标章节的相关度
    IF feedback.target_section IS NOT NULL:
        section_content = GET_SECTION_CONTENT(
            lesson_plan,
            feedback.target_section
        )
        section_similarity = TEXT_SIMILARITY(
            feedback.content,
            section_content
        )
        scores.APPEND(section_similarity * 0.4)
    
    // 关键词匹配度
    keywords = EXTRACT_KEYWORDS(lesson_plan.course_info.topic)
    keyword_match = COUNT_MATCHING_KEYWORDS(feedback.content, keywords)
    scores.APPEND(keyword_match * 0.3)
    
    RETURN SUM(scores)
END FUNCTION

// 辅助函数：计算可行性
FUNCTION CALCULATE_FEASIBILITY(feedback, lesson_plan):
    scores = []
    
    // 修改类型难度
    type_difficulty = {
        "modify": 0.7,
        "add": 0.6,
        "delete": 0.8,
        "comment": 0.9,
        "approve": 1.0,
        "reject": 1.0
    }
    scores.APPEND(type_difficulty.get(feedback.feedback_type, 0.5))
    
    // 目标章节明确度
    IF feedback.target_section IS NOT NULL:
        scores.APPEND(0.9)
    ELSE:
        scores.APPEND(0.5)
    
    // 建议具体度
    IF feedback.suggested_change IS NOT NULL:
        scores.APPEND(0.9)
    ELSE:
        scores.APPEND(0.6)
    
    RETURN AVERAGE(scores)
END FUNCTION

// 辅助函数：生成替代建议
FUNCTION GENERATE_ALTERNATIVE_SUGGESTION(feedback, lesson_plan):
    // 基于当前教案主题，建议相关的修改方向
    topic = lesson_plan.course_info.topic
    
    suggestions = [
        f"聚焦{topic}的核心概念展开",
        f"增加{topic}的实际应用案例",
        f"优化{topic}的教学活动设计",
        f"调整{topic}的练习题难度"
    ]
    
    RETURN "建议您可以：" + JOIN(suggestions, "；")
END FUNCTION

// 辅助函数：生成澄清问题
FUNCTION GENERATE_CLARIFICATION_QUESTION(feedback):
    IF feedback.target_section IS NULL:
        RETURN "您希望修改教案的哪个部分？（如：教学目标、教学过程、课件等）"
    
    IF feedback.suggested_change IS NULL:
        RETURN "您希望如何修改？请提供具体的修改内容或方向"
    
    RETURN "请进一步说明您的需求，以便我更好地帮助您"
END FUNCTION
```

---

## 4. 调用关系

### 4.1 调用图

```
[process_feedback] ──> [evaluate_user_feedback] ──┬──> [validate_user_feedback]
                                                  ├──> [CHECK_BASIC_VALIDITY]
                                                  ├──> [CALCULATE_RELEVANCE]
                                                  ├──> [CALCULATE_FEASIBILITY]
                                                  ├──> [llm_enhanced_evaluation]
                                                  └──> [CREATE_EVALUATION]
```

### 4.2 被本函数调用的函数

| 函数ID | 函数名称 | 调用目的 | 调用次数 |
|-------|---------|---------|---------|
| FN-UTIL-002 | validate_user_feedback | 验证反馈 | 1次 |
| FN-LLM-001 | llm_enhanced_evaluation | LLM增强评估 | 0-1次 |
| FN-TEXT-001 | TEXT_SIMILARITY | 文本相似度 | 2-3次 |

### 4.3 调用本函数的函数

| 函数ID | 函数名称 | 调用场景 |
|-------|---------|---------|
| FN-LP-008 | process_feedback | 处理用户反馈时 |

---

## 5. 算法复杂度

- **时间复杂度**: O(n) - n为文本长度
- **空间复杂度**: O(1) - 常数空间

---

## 6. 测试规格

### 6.1 测试用例清单

| 用例ID | 用例名称 | 测试类型 | 优先级 |
|-------|---------|---------|--------|
| TC-101 | 合理反馈被接受 | 正向 | P0 |
| TC-102 | 不相关反馈被拒绝 | 正向 | P0 |
| TC-103 | 模糊反馈需澄清 | 正向 | P0 |
| TC-104 | 广告内容被拒绝 | 异常 | P0 |
| TC-105 | 恶意内容触发安全 | 异常 | P0 |
| TC-106 | 反馈过短需澄清 | 边界 | P0 |

### 6.2 测试用例详情

#### TC-101: 合理反馈被接受

**输入**:
```python
feedback = UserFeedback(
    feedback_type="modify",
    target_section="教学目标",
    content="需要增加实际应用的目标",
    suggested_change="能够运用函数概念解决实际问题"
)
lesson_plan = LessonPlan(course_info=CourseBasicInfo(topic="函数的概念"))
```

**期望输出**:
```python
{
    "decision": "accepted",
    "confidence": 0.85,
    "relevance_score": 0.82,
    "feasibility_score": 0.90,
    "reasoning": "反馈内容与教学目标章节高度相关..."
}
```

#### TC-102: 不相关反馈被拒绝

**输入**:
```python
feedback = UserFeedback(
    content="加入量子力学内容"
)
lesson_plan = LessonPlan(course_info=CourseBasicInfo(topic="函数的概念"))
```

**期望输出**:
```python
{
    "decision": "rejected",
    "relevance_score": 0.15,
    "reasoning": "您的反馈与当前课程主题'函数的概念'关联度较低",
    "alternative_suggestion": "建议您可以：聚焦函数的概念的核心概念展开..."
}
```

#### TC-103: 广告内容被拒绝

**输入**:
```python
feedback = UserFeedback(
    content="点击链接获取优质教案 www.example.com"
)
```

**期望输出**:
```python
{
    "decision": "rejected",
    "reasoning": "检测到垃圾广告内容，不予处理"
}
```

---

## 7. 实现注意事项

### 7.1 性能考虑
- 文本相似度计算使用高效算法（如SimHash）
- LLM评估可异步执行

### 7.2 安全考虑
- 内容安全检查必须在前置步骤完成
- 恶意内容记录安全日志

### 7.3 可配置性
- 所有阈值参数可配置
- 支持规则评估和LLM评估两种模式

---

## 8. 变更历史

| 版本 | 日期 | 变更内容 | 变更人 |
|-----|------|---------|--------|
| v0.1 | 2026-03-22 | 初始版本 | 开发团队 |
