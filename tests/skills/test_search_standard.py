"""
测试模块: 搜索课程标准功能
测试ID: TEST-FN-LP-001
创建日期: 2026-03-22
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

# 被测试的函数（待实现）
# from src.skills.lesson_preparation.search_standard import search_curriculum_standard


class TestSearchCurriculumStandard:
    """
    测试类: search_curriculum_standard
    
    测试范围:
    - 正常搜索成功
    - 缓存命中
    - 无搜索结果
    - 搜索超时
    - 部分来源失败
    - 无效输入
    """
    
    # =========================================================================
    # Fixtures
    # =========================================================================
    
    @pytest.fixture
    def valid_course_info(self):
        """有效的课程信息"""
        return {
            "education_level": "高中",
            "subject": "数学",
            "topic": "函数的概念",
            "grade": "高一"
        }
    
    @pytest.fixture
    def mock_search_config(self):
        """搜索配置"""
        return {
            "timeout": 30,
            "max_results": 3,
            "source_priority": ["国家", "地方", "校本"],
            "cache_enabled": True
        }
    
    @pytest.fixture
    def mock_standard_result(self):
        """模拟课标搜索结果"""
        return {
            "standard_id": "std-001",
            "standard_name": "普通高中数学课程标准（2017年版2020年修订）",
            "standard_type": "国家",
            "education_level": "高中",
            "subject": "数学",
            "topic": "函数的概念",
            "content_requirements": [
                "在初中用变量之间的依赖关系描述函数的基础上，用集合语言和对应关系刻画函数",
                "体会集合语言和对应关系在刻画函数概念中的作用"
            ],
            "competency_requirements": [
                "数学抽象：从具体实例中抽象出函数概念",
                "逻辑推理：理解函数定义的逻辑结构"
            ],
            "achievement_standards": [
                "能够理解函数的概念，用集合语言描述函数",
                "能够判断两个函数是否相同"
            ],
            "suggested_hours": 2,
            "relevance_score": 0.95,
            "source_url": "http://www.moe.gov.cn/...",
            "extracted_at": datetime.now()
        }
    
    @pytest.fixture
    def mock_search_service(self):
        """Mock搜索服务"""
        with patch('src.skills.lesson_preparation.search_standard.search_standard_database') as mock:
            yield mock
    
    @pytest.fixture
    def mock_cache(self):
        """Mock缓存服务"""
        with patch('src.skills.lesson_preparation.search_standard.CACHE_GET') as mock_get, \
             patch('src.skills.lesson_preparation.search_standard.CACHE_SET') as mock_set, \
             patch('src.skills.lesson_preparation.search_standard.CACHE_CONTAINS') as mock_contains:
            yield {
                "get": mock_get,
                "set": mock_set,
                "contains": mock_contains
            }
    
    # =========================================================================
    # 正常情况测试
    # =========================================================================
    
    @pytest.mark.asyncio
    async def test_normal_search_success(self, valid_course_info, mock_search_service, mock_standard_result):
        """
        TC-001: 正常搜索成功
        
        验证点:
        1. 返回结果非空
        2. 课标相关度≥0.5
        3. 包含内容要求和学业质量标准
        4. 搜索耗时<30秒
        """
        # Arrange
        mock_search_service.return_value = [mock_standard_result]
        
        # Act
        result = await search_curriculum_standard(valid_course_info)
        
        # Assert
        assert result is not None
        assert result["total_found"] > 0
        assert len(result["standards"]) > 0
        
        # 验证课标结构
        standard = result["standards"][0]
        assert standard["relevance_score"] >= 0.5
        assert "content_requirements" in standard
        assert "achievement_standards" in standard
        assert len(standard["content_requirements"]) > 0
        
        # 验证搜索耗时
        assert result["search_duration_ms"] < 30000
        
        # 验证搜索服务被调用
        mock_search_service.assert_called()
    
    @pytest.mark.asyncio
    async def test_search_with_multiple_results(self, valid_course_info, mock_search_service):
        """
        TC-002: 返回多个搜索结果
        
        验证点:
        1. 结果按相关度排序
        2. 不超过max_results限制
        """
        # Arrange
        mock_results = [
            {"standard_id": "std-001", "relevance_score": 0.95},
            {"standard_id": "std-002", "relevance_score": 0.85},
            {"standard_id": "std-003", "relevance_score": 0.75},
            {"standard_id": "std-004", "relevance_score": 0.65}
        ]
        mock_search_service.return_value = mock_results
        
        # Act
        result = await search_curriculum_standard(
            valid_course_info,
            search_config={"max_results": 3}
        )
        
        # Assert
        assert result["total_found"] == 3
        assert len(result["standards"]) == 3
        
        # 验证排序
        scores = [s["relevance_score"] for s in result["standards"]]
        assert scores == sorted(scores, reverse=True)
    
    @pytest.mark.asyncio
    async def test_search_query_building(self, valid_course_info, mock_search_service):
        """
        TC-003: 搜索查询构建
        
        验证点:
        1. 查询包含学段、学科、主题
        2. 包含"课程标准"关键词
        """
        # Arrange
        mock_search_service.return_value = []
        
        # Act
        try:
            await search_curriculum_standard(valid_course_info)
        except:
            pass  # 预期会抛出NoResultError
        
        # Assert
        call_args = mock_search_service.call_args
        query = call_args[1]["query"] if call_args else ""
        
        assert "高中" in query
        assert "数学" in query
        assert "函数的概念" in query
        assert "课程标准" in query
    
    # =========================================================================
    # 缓存测试
    # =========================================================================
    
    @pytest.mark.asyncio
    async def test_cache_hit(self, valid_course_info, mock_cache, mock_standard_result):
        """
        TC-004: 缓存命中
        
        验证点:
        1. 缓存命中时直接返回缓存数据
        2. 不调用搜索服务
        3. cache_hit标志为True
        4. 搜索耗时为0
        """
        # Arrange
        mock_cache["contains"].return_value = True
        mock_cache["get"].return_value = [mock_standard_result]
        
        with patch('src.skills.lesson_preparation.search_standard.search_standard_database') as mock_search:
            # Act
            result = await search_curriculum_standard(valid_course_info)
            
            # Assert
            assert result["cache_hit"] is True
            assert result["search_duration_ms"] == 0
            mock_search.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_cache_miss_and_store(self, valid_course_info, mock_cache, mock_search_service, mock_standard_result):
        """
        TC-005: 缓存未命中并存储
        
        验证点:
        1. 缓存未命中时调用搜索服务
        2. 搜索结果写入缓存
        """
        # Arrange
        mock_cache["contains"].return_value = False
        mock_search_service.return_value = [mock_standard_result]
        
        # Act
        result = await search_curriculum_standard(valid_course_info)
        
        # Assert
        assert result["cache_hit"] is False
        mock_search_service.assert_called_once()
        mock_cache["set"].assert_called_once()
    
    # =========================================================================
    # 异常情况测试
    # =========================================================================
    
    @pytest.mark.asyncio
    async def test_no_result_found(self, valid_course_info, mock_search_service):
        """
        TC-006: 无搜索结果
        
        验证点:
        1. 抛出NoResultError
        2. 错误信息包含搜索主题
        """
        # Arrange
        mock_search_service.return_value = []
        
        # Act & Assert
        with pytest.raises(NoResultError) as exc_info:
            await search_curriculum_standard(valid_course_info)
        
        assert "函数的概念" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_search_timeout(self, valid_course_info, mock_search_service):
        """
        TC-007: 搜索超时
        
        验证点:
        1. 抛出TimeoutError
        2. 错误信息包含超时时间
        """
        # Arrange
        import asyncio
        
        async def slow_search(*args, **kwargs):
            await asyncio.sleep(10)  # 模拟慢查询
            return []
        
        mock_search_service.side_effect = slow_search
        
        # Act & Assert
        with pytest.raises(TimeoutError) as exc_info:
            await search_curriculum_standard(
                valid_course_info,
                search_config={"timeout": 0.001}  # 1毫秒超时
            )
    
    @pytest.mark.asyncio
    async def test_partial_source_failure(self, valid_course_info, mock_search_service):
        """
        TC-008: 部分来源失败
        
        验证点:
        1. 失败的来源不中断搜索
        2. 返回其他来源的结果
        3. 记录错误日志
        """
        # Arrange
        # 第一次调用失败，第二次成功
        mock_search_service.side_effect = [
            Exception("国家课标库连接失败"),
            [{"standard_id": "std-local", "relevance_score": 0.8}]
        ]
        
        # Act
        result = await search_curriculum_standard(valid_course_info)
        
        # Assert
        assert result["total_found"] > 0
        assert result["source_breakdown"].get("地方", 0) > 0
    
    @pytest.mark.asyncio
    async def test_invalid_course_info(self):
        """
        TC-009: 无效输入
        
        验证点:
        1. 抛出ValueError
        2. 错误信息指明无效字段
        """
        # Arrange
        invalid_course_info = None
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await search_curriculum_standard(invalid_course_info)
        
        assert "course_info" in str(exc_info.value).lower()
    
    # =========================================================================
    # 边界情况测试
    # =========================================================================
    
    @pytest.mark.asyncio
    async def test_low_relevance_filtering(self, valid_course_info, mock_search_service):
        """
        TC-010: 低相关度结果过滤
        
        验证点:
        1. 相关度<0.5的结果被过滤
        2. 只返回高质量结果
        """
        # Arrange
        mock_results = [
            {"standard_id": "std-001", "relevance_score": 0.95},
            {"standard_id": "std-002", "relevance_score": 0.45},  # 低于阈值
            {"standard_id": "std-003", "relevance_score": 0.30}   # 低于阈值
        ]
        mock_search_service.return_value = mock_results
        
        # Act
        result = await search_curriculum_standard(valid_course_info)
        
        # Assert
        assert result["total_found"] == 1
        assert result["standards"][0]["standard_id"] == "std-001"
    
    @pytest.mark.asyncio
    async def test_cache_disabled(self, valid_course_info, mock_cache, mock_search_service, mock_standard_result):
        """
        TC-011: 禁用缓存
        
        验证点:
        1. 不检查缓存
        2. 不写入缓存
        """
        # Arrange
        mock_search_service.return_value = [mock_standard_result]
        
        # Act
        result = await search_curriculum_standard(
            valid_course_info,
            search_config={"cache_enabled": False}
        )
        
        # Assert
        mock_cache["contains"].assert_not_called()
        mock_cache["set"].assert_not_called()
    
    # =========================================================================
    # 集成测试
    # =========================================================================
    
    @pytest.mark.asyncio
    async def test_full_search_workflow(self, valid_course_info):
        """
        TC-012: 完整搜索流程
        
        验证点:
        1. 端到端流程正常
        2. 结果符合预期格式
        """
        # 这是一个集成测试，使用真实或完整的Mock服务
        # Arrange
        # ... 设置完整的Mock环境
        
        # Act
        # result = await search_curriculum_standard(valid_course_info)
        
        # Assert
        # ... 验证完整流程
        pass


class TestSearchQueryBuilding:
    """
    测试搜索查询构建逻辑
    """
    
    def test_build_query_with_all_fields(self):
        """
        TC-013: 使用所有字段构建查询
        """
        # Arrange
        course_info = {
            "education_level": "高中",
            "subject": "数学",
            "topic": "函数的概念",
            "grade": "高一"
        }
        
        # Act
        query = BUILD_SEARCH_QUERY(course_info)
        
        # Assert
        assert "高中" in query
        assert "高一" in query
        assert "数学" in query
        assert "函数的概念" in query
        assert "课程标准" in query
    
    def test_build_query_without_grade(self):
        """
        TC-014: 无年级字段构建查询
        """
        # Arrange
        course_info = {
            "education_level": "初中",
            "subject": "语文",
            "topic": "春"
        }
        
        # Act
        query = BUILD_SEARCH_QUERY(course_info)
        
        # Assert
        assert "初中" in query
        assert "语文" in query
        assert "春" in query
        # 不包含grade


class TestStandardParsing:
    """
    测试课标解析逻辑
    """
    
    def test_parse_standard_with_full_content(self):
        """
        TC-015: 解析完整课标内容
        """
        # Arrange
        raw_result = {
            "title": "普通高中数学课程标准",
            "source_type": "国家",
            "level": "高中",
            "subject": "数学",
            "content": """
            内容要求：
            1. 在初中用变量之间的依赖关系描述函数的基础上，用集合语言和对应关系刻画函数
            2. 体会集合语言和对应关系在刻画函数概念中的作用
            
            学业质量：
            能够理解函数的概念，用集合语言描述函数
            """,
            "url": "http://example.com"
        }
        
        # Act
        standard = PARSE_STANDARD(raw_result)
        
        # Assert
        assert standard["standard_name"] == "普通高中数学课程标准"
        assert standard["standard_type"] == "国家"
        assert len(standard["content_requirements"]) > 0
        assert len(standard["achievement_standards"]) > 0
    
    def test_extract_content_requirements(self):
        """
        TC-016: 提取内容要求
        """
        # Arrange
        content = """
        内容要求：
        1. 第一条要求
        2. 第二条要求
        3. 第三条要求
        
        学业质量：...
        """
        
        # Act
        requirements = EXTRACT_CONTENT_REQUIREMENTS(content)
        
        # Assert
        assert len(requirements) == 3
        assert "第一条要求" in requirements[0]


class TestRelevanceCalculation:
    """
    测试相关度计算
    """
    
    def test_exact_match_high_score(self):
        """
        TC-017: 精确匹配得高分
        """
        # Arrange
        standard = {
            "topic": "函数的概念",
            "subject": "数学",
            "education_level": "高中"
        }
        course_info = {
            "topic": "函数的概念",
            "subject": "数学",
            "education_level": "高中"
        }
        
        # Act
        score = CALCULATE_RELEVANCE(standard, course_info)
        
        # Assert
        assert score >= 0.9
    
    def test_partial_match_medium_score(self):
        """
        TC-018: 部分匹配得中分
        """
        # Arrange
        standard = {
            "topic": "函数的表示法",
            "subject": "数学",
            "education_level": "高中"
        }
        course_info = {
            "topic": "函数的概念",
            "subject": "数学",
            "education_level": "高中"
        }
        
        # Act
        score = CALCULATE_RELEVANCE(standard, course_info)
        
        # Assert
        assert 0.5 <= score < 0.9
    
    def test_no_match_low_score(self):
        """
        TC-019: 不匹配得低分
        """
        # Arrange
        standard = {
            "topic": "立体几何",
            "subject": "数学",
            "education_level": "高中"
        }
        course_info = {
            "topic": "函数的概念",
            "subject": "数学",
            "education_level": "高中"
        }
        
        # Act
        score = CALCULATE_RELEVANCE(standard, course_info)
        
        # Assert
        assert score < 0.5


# =========================================================================
# 测试数据
# =========================================================================

TEST_DATA_SEARCH_STANDARD = {
    "valid_courses": [
        {"education_level": "高中", "subject": "数学", "topic": "函数的概念"},
        {"education_level": "初中", "subject": "语文", "topic": "春"},
        {"education_level": "小学", "subject": "科学", "topic": "植物的生长"}
    ],
    "invalid_courses": [
        None,
        {},
        {"education_level": "", "subject": "", "topic": ""},
        {"education_level": "大学", "subject": "数学", "topic": "微积分"}
    ],
    "mock_standards": [
        {
            "standard_id": "std-001",
            "standard_name": "普通高中数学课程标准",
            "relevance_score": 0.95
        },
        {
            "standard_id": "std-002",
            "standard_name": "初中语文课程标准",
            "relevance_score": 0.88
        }
    ]
}


# =========================================================================
# 测试执行入口
# =========================================================================

if __name__ == "__main__":
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--cov=src/skills",
        "--cov-report=html"
    ])
