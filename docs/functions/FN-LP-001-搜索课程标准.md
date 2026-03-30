# 函数规格：搜索课程标准

## 函数标识

- **函数ID**: FN-LP-001
- **函数名称**: search_curriculum_standard
- **所属功能点**: FP-LP-001
- **所属模块**: lesson_preparation
- **创建日期**: 2026-03-22

---

## 1. 功能描述

### 1.1 功能概述
根据课程基本信息（学段、学科、主题）搜索对应的课程标准文档，提取相关的教学要求。

### 1.2 详细说明
1. 构建搜索查询（结合学段、学科、主题）
2. 优先搜索国家课程标准数据库
3. 如未找到，搜索地方课程标准
4. 提取课标中的内容要求、素养要求、学业质量标准
5. 计算相关度评分
6. 返回结构化的课标数据

### 1.3 业务规则
- BR-001: 优先搜索国家课程标准，其次地方标准
- BR-002: 如未找到精确匹配，返回最相关的章节
- BR-003: 提取的内容必须包含"内容要求"和"学业质量"两部分
- BR-004: 相关度评分低于0.5的结果应过滤

---

## 2. 接口定义

### 2.1 函数签名

```python
async def search_curriculum_standard(
    course_info: CourseBasicInfo,
    search_config: Optional[SearchConfig] = None
) -> SearchStandardResult:
    """
    搜索课程标准
    
    Args:
        course_info: 课程基本信息
        search_config: 搜索配置（可选）
        
    Returns:
        搜索结果，包含课标列表和搜索元数据
        
    Raises:
        ValueError: 输入参数无效
        SearchError: 搜索服务异常
        NoResultError: 未找到相关课标
    """
    pass
```

### 2.2 输入参数

| 参数名 | 类型 | 必填 | 默认值 | 约束 | 说明 |
|-------|------|-----|--------|------|------|
| course_info | CourseBasicInfo | 是 | - | 已验证 | 课程基本信息 |
| search_config | SearchConfig | 否 | None | - | 搜索配置 |

**SearchConfig 结构**:
```python
{
    "timeout": int,           # 搜索超时（秒），默认30
    "max_results": int,       # 最大结果数，默认5
    "source_priority": List[str],  # 来源优先级，默认["国家", "地方", "校本"]
    "include_full_text": bool,     # 是否包含全文，默认False
    "cache_enabled": bool          # 是否使用缓存，默认True
}
```

### 2.3 返回值

**SearchStandardResult 结构**:
```python
{
    "standards": List[CurriculumStandard],  # 课标列表
    "total_found": int,                     # 找到的总数
    "search_query": str,                    # 实际使用的搜索查询
    "search_duration_ms": int,              # 搜索耗时（毫秒）
    "source_breakdown": Dict[str, int],     # 各来源数量
    "cache_hit": bool                       # 是否命中缓存
}
```

### 2.4 异常定义

| 异常类型 | 触发条件 | 错误码 | 错误信息 |
|---------|---------|--------|---------|
| ValueError | course_info无效 | E001 | "Invalid course_info: {detail}" |
| SearchError | 搜索服务异常 | E002 | "Search service error: {detail}" |
| NoResultError | 未找到相关课标 | E003 | "No curriculum standard found for {topic}" |
| TimeoutError | 搜索超时 | E004 | "Search timeout after {timeout}s" |

---

## 3. 伪代码

```
FUNCTION search_curriculum_standard(course_info, search_config):
    
    // 1. 输入验证
    IF course_info IS NULL:
        RAISE ValueError("course_info cannot be null")
    
    IF NOT validate_course_basic_info(course_info):
        RAISE ValueError("course_info validation failed")
    
    // 2. 初始化配置
    config = search_config OR DEFAULT_SEARCH_CONFIG
    start_time = GET_CURRENT_TIME_MS()
    
    // 3. 检查缓存
    cache_key = GENERATE_CACHE_KEY(course_info)
    IF config.cache_enabled AND CACHE_CONTAINS(cache_key):
        cached_result = CACHE_GET(cache_key)
        RETURN SearchStandardResult(
            standards=cached_result,
            cache_hit=True,
            search_duration_ms=0
        )
    
    // 4. 构建搜索查询
    search_query = BUILD_SEARCH_QUERY(course_info)
    // 示例: "高中数学 函数的概念 课程标准 内容要求"
    
    // 5. 执行搜索（按优先级）
    all_standards = []
    
    FOR source_type IN config.source_priority:
        TRY:
            results = AWAIT search_standard_database(
                query=search_query,
                source_type=source_type,
                max_results=config.max_results,
                timeout=config.timeout
            )
            
            FOR raw_result IN results:
                standard = PARSE_STANDARD(raw_result)
                standard.relevance_score = CALCULATE_RELEVANCE(
                    standard, course_info
                )
                
                IF standard.relevance_score >= 0.5:
                    all_standards.APPEND(standard)
            
        CATCH TimeoutError:
            LOG_WARNING(f"Search timeout for source: {source_type}")
            CONTINUE
        CATCH Exception AS e:
            LOG_ERROR(f"Search error for {source_type}: {e}")
            CONTINUE
    
    // 6. 排序和过滤
    all_standards.SORT_BY(relevance_score, DESC)
    all_standards = all_standards[:config.max_results]
    
    // 7. 检查是否有结果
    IF all_standards IS EMPTY:
        RAISE NoResultError(
            f"No curriculum standard found for {course_info.topic}"
        )
    
    // 8. 缓存结果
    IF config.cache_enabled:
        CACHE_SET(cache_key, all_standards, TTL=3600)
    
    // 9. 构建返回结果
    search_duration = GET_CURRENT_TIME_MS() - start_time
    
    source_breakdown = COUNT_BY_SOURCE(all_standards)
    
    result = SearchStandardResult(
        standards=all_standards,
        total_found=LENGTH(all_standards),
        search_query=search_query,
        search_duration_ms=search_duration,
        source_breakdown=source_breakdown,
        cache_hit=False
    )
    
    // 10. 记录日志
    LOG_INFO(f"Found {result.total_found} standards for {course_info.topic}")
    
    RETURN result

END FUNCTION

// 辅助函数：构建搜索查询
FUNCTION BUILD_SEARCH_QUERY(course_info):
    query_parts = [
        course_info.education_level,
        course_info.subject,
        course_info.topic,
        "课程标准",
        "内容要求"
    ]
    
    IF course_info.grade IS NOT NULL:
        query_parts.INSERT(1, course_info.grade)
    
    RETURN JOIN(query_parts, " ")
END FUNCTION

// 辅助函数：解析课标数据
FUNCTION PARSE_STANDARD(raw_result):
    standard = CurriculumStandard()
    standard.standard_id = GENERATE_UUID()
    standard.standard_name = raw_result.title
    standard.standard_type = raw_result.source_type
    standard.education_level = raw_result.level
    standard.subject = raw_result.subject
    standard.topic = EXTRACT_TOPIC(raw_result.content)
    standard.content_requirements = EXTRACT_CONTENT_REQUIREMENTS(raw_result.content)
    standard.competency_requirements = EXTRACT_COMPETENCY_REQUIREMENTS(raw_result.content)
    standard.achievement_standards = EXTRACT_ACHIEVEMENT_STANDARDS(raw_result.content)
    standard.suggested_hours = EXTRACT_SUGGESTED_HOURS(raw_result.content) OR 1
    standard.source_url = raw_result.url
    standard.extracted_at = NOW()
    
    RETURN standard
END FUNCTION

// 辅助函数：计算相关度
FUNCTION CALCULATE_RELEVANCE(standard, course_info):
    scores = []
    
    // 主题匹配度
    topic_score = TEXT_SIMILARITY(standard.topic, course_info.topic)
    scores.APPEND(topic_score * 0.4)
    
    // 学科匹配度
    subject_score = 1.0 IF standard.subject == course_info.subject ELSE 0.0
    scores.APPEND(subject_score * 0.3)
    
    // 学段匹配度
    level_score = 1.0 IF standard.education_level == course_info.education_level ELSE 0.0
    scores.APPEND(level_score * 0.3)
    
    RETURN SUM(scores)
END FUNCTION
```

---

## 4. 调用关系

### 4.1 调用图

```
[prepare_lesson] ──> [search_curriculum_standard] ──┬──> [validate_course_basic_info]
                                                    ├──> [search_standard_database]
                                                    ├──> [PARSE_STANDARD]
                                                    └──> [CACHE_*]
```

### 4.2 被本函数调用的函数

| 函数ID | 函数名称 | 调用目的 | 调用次数 |
|-------|---------|---------|---------|
| FN-UTIL-001 | validate_course_basic_info | 验证输入 | 1次 |
| FN-SEARCH-001 | search_standard_database | 搜索课标数据库 | 1-3次 |
| FN-CACHE-001 | CACHE_GET | 读取缓存 | 0-1次 |
| FN-CACHE-002 | CACHE_SET | 写入缓存 | 0-1次 |

### 4.3 调用本函数的函数

| 函数ID | 函数名称 | 调用场景 |
|-------|---------|---------|
| FN-LP-MAIN-001 | prepare_lesson | 备课流程第一步 |

---

## 5. 算法复杂度

- **最优情况**: O(1) - 缓存命中
- **平均情况**: O(n) - n为搜索结果数
- **最坏情况**: O(n*m) - n为来源数，m为每个来源结果数

- **空间复杂度**: O(k) - k为返回的课标数量

---

## 6. 测试规格

### 6.1 测试用例清单

| 用例ID | 用例名称 | 测试类型 | 优先级 |
|-------|---------|---------|--------|
| TC-001 | 正常搜索成功 | 正向 | P0 |
| TC-002 | 缓存命中 | 正向 | P0 |
| TC-003 | 无搜索结果 | 异常 | P0 |
| TC-004 | 搜索超时 | 异常 | P0 |
| TC-005 | 部分来源失败 | 边界 | P0 |
| TC-006 | 无效输入 | 异常 | P0 |

### 6.2 测试用例详情

#### TC-001: 正常搜索成功

**输入**:
```python
course_info = CourseBasicInfo(
    education_level="高中",
    subject="数学",
    topic="函数的概念"
)
search_config = SearchConfig(max_results=3)
```

**期望输出**:
```python
{
    "standards": [
        {
            "standard_id": "std-001",
            "standard_name": "普通高中数学课程标准",
            "relevance_score": 0.95,
            ...
        }
    ],
    "total_found": 1,
    "search_query": "高中数学 函数的概念 课程标准 内容要求",
    "search_duration_ms": 1500,
    "source_breakdown": {"国家": 1},
    "cache_hit": False
}
```

**验证点**:
- 返回结果非空
- 课标相关度≥0.5
- 包含内容要求和学业质量标准
- 搜索耗时<30秒

#### TC-002: 缓存命中

**前置条件**: 已执行过相同搜索

**输入**: 同TC-001

**期望输出**:
```python
{
    "standards": [...],
    "cache_hit": True,
    "search_duration_ms": 0
}
```

#### TC-003: 无搜索结果

**输入**:
```python
course_info = CourseBasicInfo(
    education_level="高中",
    subject="不存在学科",
    topic="不存在主题"
)
```

**期望异常**: NoResultError

**期望错误信息**: "No curriculum standard found for 不存在主题"

#### TC-004: 搜索超时

**输入**:
```python
search_config = SearchConfig(timeout=0.001)  # 1毫秒超时
```

**期望异常**: TimeoutError

#### TC-005: 部分来源失败

**场景**: 国家课标库成功，地方课标库失败

**期望**: 返回国家课标结果，记录地方课标错误日志

#### TC-006: 无效输入

**输入**:
```python
course_info = None
```

**期望异常**: ValueError

---

## 7. 实现注意事项

### 7.1 性能考虑
- 使用异步并发搜索多个来源
- 缓存热点课标数据
- 设置合理的超时时间

### 7.2 并发考虑
- 搜索函数是线程安全的
- 缓存操作需要加锁

### 7.3 安全考虑
- 验证所有外部输入
- 防止SQL注入（如使用数据库）
- 敏感数据脱敏

---

## 8. 变更历史

| 版本 | 日期 | 变更内容 | 变更人 |
|-----|------|---------|--------|
| v0.1 | 2026-03-22 | 初始版本 | 开发团队 |
