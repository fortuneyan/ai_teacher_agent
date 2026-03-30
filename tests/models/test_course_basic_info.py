"""
测试模块: CourseBasicInfo 数据对象
测试ID: TEST-DO-001
创建日期: 2026-03-22
"""

import pytest
from datetime import datetime
from uuid import UUID, uuid4

# 被测试的类（待实现）
# from src.models.course_basic_info import CourseBasicInfo


class TestCourseBasicInfo:
    """
    测试类: CourseBasicInfo
    
    测试范围:
    - 正常创建
    - 属性验证
    - 边界条件
    - 序列化/反序列化
    """
    
    # =========================================================================
    # Fixtures
    # =========================================================================
    
    @pytest.fixture
    def valid_course_data(self):
        """
        有效的课程基本信息数据
        
        Returns:
            dict: 包含所有必填字段的有效数据
        """
        return {
            "education_level": "高中",
            "subject": "数学",
            "topic": "函数的概念",
            "grade": "高一",
            "textbook_version": "人教版",
            "suggested_hours": 2,
            "input_timestamp": datetime(2026, 3, 22, 10, 30, 0),
            "session_id": str(uuid4())
        }
    
    @pytest.fixture
    def minimal_course_data(self):
        """
        最小有效数据（仅必填字段）
        """
        return {
            "education_level": "初中",
            "subject": "语文",
            "topic": "春"
        }
    
    @pytest.fixture
    def invalid_course_data_scenarios(self):
        """
        各种无效数据场景
        """
        return {
            "empty_education_level": {
                "education_level": "",
                "subject": "数学",
                "topic": "函数"
            },
            "invalid_education_level": {
                "education_level": "大学",  # 不在枚举中
                "subject": "数学",
                "topic": "函数"
            },
            "short_topic": {
                "education_level": "高中",
                "subject": "数学",
                "topic": "函"  # 少于2个字符
            },
            "long_topic": {
                "education_level": "高中",
                "subject": "数学",
                "topic": "函数" * 100  # 超过100字符
            },
            "zero_hours": {
                "education_level": "高中",
                "subject": "数学",
                "topic": "函数",
                "suggested_hours": 0  # 小于1
            },
            "too_many_hours": {
                "education_level": "高中",
                "subject": "数学",
                "topic": "函数",
                "suggested_hours": 15  # 超过10
            }
        }
    
    # =========================================================================
    # 正常情况测试
    # =========================================================================
    
    def test_create_with_valid_data(self, valid_course_data):
        """
        TC-DO001-001: 使用有效数据创建对象
        
        验证点:
        1. 对象成功创建
        2. 所有属性正确赋值
        3. 自动生成默认值（如未提供）
        """
        # Arrange & Act
        course = CourseBasicInfo(**valid_course_data)
        
        # Assert
        assert course.education_level == "高中"
        assert course.subject == "数学"
        assert course.topic == "函数的概念"
        assert course.grade == "高一"
        assert course.textbook_version == "人教版"
        assert course.suggested_hours == 2
        assert isinstance(course.input_timestamp, datetime)
        assert UUID(course.session_id)
    
    def test_create_with_minimal_data(self, minimal_course_data):
        """
        TC-DO001-002: 使用最小数据创建对象
        
        验证点:
        1. 对象成功创建
        2. 可选字段使用默认值
        """
        # Arrange & Act
        course = CourseBasicInfo(**minimal_course_data)
        
        # Assert
        assert course.education_level == "初中"
        assert course.subject == "语文"
        assert course.topic == "春"
        assert course.grade is None
        assert course.textbook_version is None
        assert course.suggested_hours == 1  # 默认值
        assert course.input_timestamp is not None
        assert course.session_id is not None
    
    def test_auto_generate_session_id(self, minimal_course_data):
        """
        TC-DO001-003: 自动生成session_id
        
        验证点:
        1. 未提供session_id时自动生成
        2. 生成的ID是有效的UUID
        """
        # Arrange & Act
        course = CourseBasicInfo(**minimal_course_data)
        
        # Assert
        assert course.session_id is not None
        assert len(course.session_id) == 36  # UUID字符串长度
        UUID(course.session_id)  # 验证是有效的UUID
    
    def test_auto_generate_timestamp(self, minimal_course_data):
        """
        TC-DO001-004: 自动生成时间戳
        
        验证点:
        1. 未提供input_timestamp时自动生成
        2. 时间戳是当前时间
        """
        # Arrange
        before_create = datetime.now()
        
        # Act
        course = CourseBasicInfo(**minimal_course_data)
        
        # Assert
        after_create = datetime.now()
        assert course.input_timestamp is not None
        assert before_create <= course.input_timestamp <= after_create
    
    # =========================================================================
    # 属性验证测试
    # =========================================================================
    
    def test_education_level_enum_validation(self):
        """
        TC-DO001-005: 学段枚举值验证
        
        验证点:
        1. 接受有效的枚举值
        2. 拒绝无效的枚举值
        """
        # 有效值
        for level in ["小学", "初中", "高中"]:
            course = CourseBasicInfo(
                education_level=level,
                subject="数学",
                topic="测试"
            )
            assert course.education_level == level
        
        # 无效值
        with pytest.raises(ValueError) as exc_info:
            CourseBasicInfo(
                education_level="幼儿园",  # 无效值
                subject="数学",
                topic="测试"
            )
        assert "education_level" in str(exc_info.value)
    
    def test_subject_length_validation(self):
        """
        TC-DO001-006: 学科名称长度验证
        
        验证点:
        1. 接受1-20字符的学科名
        2. 拒绝空字符串
        3. 拒绝超过20字符的学科名
        """
        # 边界值：1字符
        course = CourseBasicInfo(
            education_level="高中",
            subject="数",
            topic="测试"
        )
        assert course.subject == "数"
        
        # 边界值：20字符
        long_subject = "数学" * 10
        course = CourseBasicInfo(
            education_level="高中",
            subject=long_subject,
            topic="测试"
        )
        assert course.subject == long_subject
        
        # 无效：空字符串
        with pytest.raises(ValueError):
            CourseBasicInfo(
                education_level="高中",
                subject="",
                topic="测试"
            )
        
        # 无效：超过20字符
        with pytest.raises(ValueError):
            CourseBasicInfo(
                education_level="高中",
                subject="数学" * 15,
                topic="测试"
            )
    
    def test_topic_length_validation(self):
        """
        TC-DO001-007: 主题长度验证
        
        验证点:
        1. 接受2-100字符的主题
        2. 拒绝少于2字符
        3. 拒绝超过100字符
        """
        # 边界值：2字符
        course = CourseBasicInfo(
            education_level="高中",
            subject="数学",
            topic="函数"
        )
        assert course.topic == "函数"
        
        # 边界值：100字符
        long_topic = "函数的概念与性质及其在实际问题中的应用方法"
        long_topic = long_topic * 3  # 确保超过100字符
        long_topic = long_topic[:100]  # 截取100字符
        course = CourseBasicInfo(
            education_level="高中",
            subject="数学",
            topic=long_topic
        )
        assert course.topic == long_topic
        
        # 无效：1字符
        with pytest.raises(ValueError):
            CourseBasicInfo(
                education_level="高中",
                subject="数学",
                topic="函"
            )
        
        # 无效：超过100字符
        with pytest.raises(ValueError):
            CourseBasicInfo(
                education_level="高中",
                subject="数学",
                topic="函数" * 60
            )
    
    def test_suggested_hours_range_validation(self):
        """
        TC-DO001-008: 建议课时范围验证
        
        验证点:
        1. 接受1-10的课时数
        2. 拒绝小于1
        3. 拒绝大于10
        """
        # 边界值：1
        course = CourseBasicInfo(
            education_level="高中",
            subject="数学",
            topic="函数",
            suggested_hours=1
        )
        assert course.suggested_hours == 1
        
        # 边界值：10
        course = CourseBasicInfo(
            education_level="高中",
            subject="数学",
            topic="函数",
            suggested_hours=10
        )
        assert course.suggested_hours == 10
        
        # 无效：0
        with pytest.raises(ValueError):
            CourseBasicInfo(
                education_level="高中",
                subject="数学",
                topic="函数",
                suggested_hours=0
            )
        
        # 无效：11
        with pytest.raises(ValueError):
            CourseBasicInfo(
                education_level="高中",
                subject="数学",
                topic="函数",
                suggested_hours=11
            )
    
    # =========================================================================
    # 序列化测试
    # =========================================================================
    
    def test_to_dict(self, valid_course_data):
        """
        TC-DO001-009: 转换为字典
        
        验证点:
        1. 所有属性正确转换为字典
        2. datetime转换为ISO格式字符串
        """
        # Arrange
        course = CourseBasicInfo(**valid_course_data)
        
        # Act
        data = course.to_dict()
        
        # Assert
        assert data["education_level"] == "高中"
        assert data["subject"] == "数学"
        assert data["topic"] == "函数的概念"
        assert isinstance(data["input_timestamp"], str)  # ISO格式
    
    def test_from_dict(self, valid_course_data):
        """
        TC-DO001-010: 从字典创建
        
        验证点:
        1. 正确从字典解析
        2. 字符串时间戳正确解析为datetime
        """
        # Arrange
        original = CourseBasicInfo(**valid_course_data)
        data = original.to_dict()
        
        # Act
        restored = CourseBasicInfo.from_dict(data)
        
        # Assert
        assert restored.education_level == original.education_level
        assert restored.subject == original.subject
        assert restored.topic == original.topic
        assert restored.input_timestamp == original.input_timestamp
    
    def test_to_json(self, valid_course_data):
        """
        TC-DO001-011: 转换为JSON字符串
        
        验证点:
        1. 正确生成JSON字符串
        2. 包含所有字段
        """
        # Arrange
        course = CourseBasicInfo(**valid_course_data)
        
        # Act
        json_str = course.to_json()
        
        # Assert
        assert isinstance(json_str, str)
        assert "高中" in json_str
        assert "数学" in json_str
        assert "函数的概念" in json_str
    
    def test_from_json(self, valid_course_data):
        """
        TC-DO001-012: 从JSON字符串创建
        
        验证点:
        1. 正确解析JSON字符串
        2. 所有字段正确恢复
        """
        # Arrange
        original = CourseBasicInfo(**valid_course_data)
        json_str = original.to_json()
        
        # Act
        restored = CourseBasicInfo.from_json(json_str)
        
        # Assert
        assert restored.education_level == original.education_level
        assert restored.subject == original.subject
        assert restored.topic == original.topic
    
    # =========================================================================
    # 字符串表示测试
    # =========================================================================
    
    def test_str_representation(self, valid_course_data):
        """
        TC-DO001-013: 字符串表示
        
        验证点:
        1. __str__方法返回可读的字符串
        2. 包含关键信息
        """
        # Arrange
        course = CourseBasicInfo(**valid_course_data)
        
        # Act
        str_repr = str(course)
        
        # Assert
        assert "高中" in str_repr
        assert "数学" in str_repr
        assert "函数的概念" in str_repr
    
    def test_repr_representation(self, valid_course_data):
        """
        TC-DO001-014: 正式字符串表示
        
        验证点:
        1. __repr__方法返回可用于重建对象的字符串
        """
        # Arrange
        course = CourseBasicInfo(**valid_course_data)
        
        # Act
        repr_str = repr(course)
        
        # Assert
        assert "CourseBasicInfo" in repr_str
        assert course.session_id in repr_str


class TestCourseBasicInfoValidation:
    """
    专门测试验证逻辑的测试类
    """
    
    def test_validate_method_with_valid_data(self):
        """
        TC-DO001-015: 验证方法-有效数据
        """
        # Arrange
        data = {
            "education_level": "高中",
            "subject": "数学",
            "topic": "函数的概念"
        }
        
        # Act
        result = CourseBasicInfo.validate(data)
        
        # Assert
        assert result.is_valid is True
        assert result.errors == []
    
    def test_validate_method_with_invalid_data(self):
        """
        TC-DO001-016: 验证方法-无效数据
        """
        # Arrange
        data = {
            "education_level": "无效学段",
            "subject": "",
            "topic": "短"
        }
        
        # Act
        result = CourseBasicInfo.validate(data)
        
        # Assert
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("education_level" in e for e in result.errors)
        assert any("subject" in e for e in result.errors)
        assert any("topic" in e for e in result.errors)


# =========================================================================
# 测试数据生成辅助函数
# =========================================================================

def generate_course_basic_info_samples():
    """
    生成测试样本数据
    
    Returns:
        list: 多种场景的样本数据
    """
    return [
        {
            "name": "高中数学",
            "data": {
                "education_level": "高中",
                "subject": "数学",
                "topic": "函数的概念",
                "grade": "高一",
                "suggested_hours": 2
            }
        },
        {
            "name": "初中语文",
            "data": {
                "education_level": "初中",
                "subject": "语文",
                "topic": "春",
                "grade": "七年级",
                "suggested_hours": 1
            }
        },
        {
            "name": "小学科学",
            "data": {
                "education_level": "小学",
                "subject": "科学",
                "topic": "植物的生长",
                "grade": "三年级",
                "suggested_hours": 1
            }
        }
    ]


# =========================================================================
# 性能测试
# =========================================================================

class TestCourseBasicInfoPerformance:
    """
    性能测试类
    """
    
    @pytest.mark.performance
    def test_create_performance(self, benchmark):
        """
        TC-DO001-PERF-001: 创建性能测试
        
        验证点:
        1. 创建1000个对象的时间应在可接受范围内
        """
        data = {
            "education_level": "高中",
            "subject": "数学",
            "topic": "函数的概念"
        }
        
        def create_1000():
            for _ in range(1000):
                CourseBasicInfo(**data)
        
        benchmark(create_1000)


# =========================================================================
# 测试执行入口
# =========================================================================

if __name__ == "__main__":
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--cov=src/models",
        "--cov-report=html",
        "--cov-report=term-missing"
    ])
