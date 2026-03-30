#!/usr/bin/env python3
"""
快速测试脚本 - 验证数据对象实现
"""

import sys
sys.path.insert(0, 'src')

from models.course_basic_info import CourseBasicInfo, ValidationResult
from datetime import datetime

def test_course_basic_info():
    """测试CourseBasicInfo"""
    print("=" * 60)
    print("测试 CourseBasicInfo")
    print("=" * 60)
    
    # 测试1: 正常创建
    print("\n[测试1] 正常创建...")
    try:
        course = CourseBasicInfo(
            education_level="高中",
            subject="数学",
            topic="函数的概念",
            grade="高一",
            suggested_hours=2
        )
        print(f"[OK] 创建成功: {course}")
        print(f"   session_id: {course.session_id}")
        print(f"   timestamp: {course.input_timestamp}")
    except Exception as e:
        print(f"[FAIL] 创建失败: {e}")
        return False
    
    # 测试2: 最小数据创建
    print("\n[测试2] 最小数据创建...")
    try:
        course_min = CourseBasicInfo(
            education_level="初中",
            subject="语文",
            topic="春"
        )
        print(f"[OK] 创建成功: {course_min}")
        print(f"   默认课时: {course_min.suggested_hours}")
    except Exception as e:
        print(f"[FAIL] 创建失败: {e}")
        return False
    
    # 测试3: 无效education_level
    print("\n[测试3] 无效education_level...")
    try:
        course_invalid = CourseBasicInfo(
            education_level="大学",
            subject="数学",
            topic="微积分"
        )
        print(f"[FAIL] 应该抛出异常但没有")
        return False
    except ValueError as e:
        print(f"[OK] 正确抛出异常: {e}")
    
    # 测试4: 无效topic长度
    print("\n[测试4] 无效topic长度...")
    try:
        course_short = CourseBasicInfo(
            education_level="高中",
            subject="数学",
            topic="函"  # 太短
        )
        print(f"[FAIL] 应该抛出异常但没有")
        return False
    except ValueError as e:
        print(f"[OK] 正确抛出异常: {e}")
    
    # 测试5: 验证方法
    print("\n[测试5] 验证方法...")
    valid_data = {
        "education_level": "高中",
        "subject": "数学",
        "topic": "函数的概念"
    }
    result = CourseBasicInfo.validate(valid_data)
    print(f"[OK] 验证结果: is_valid={result.is_valid}, errors={result.errors}")
    
    invalid_data = {
        "education_level": "无效",
        "subject": "",
        "topic": "短"
    }
    result_invalid = CourseBasicInfo.validate(invalid_data)
    print(f"[OK] 验证结果: is_valid={result_invalid.is_valid}, errors={result_invalid.errors}")
    
    # 测试6: 序列化
    print("\n[测试6] 序列化...")
    try:
        course_dict = course.to_dict()
        print(f"[OK] to_dict成功")
        
        course_json = course.to_json()
        print(f"[OK] to_json成功 (长度: {len(course_json)})")
        
        course_restored = CourseBasicInfo.from_dict(course_dict)
        print(f"[OK] from_dict成功: {course_restored}")
        
        course_from_json = CourseBasicInfo.from_json(course_json)
        print(f"[OK] from_json成功: {course_from_json}")
    except Exception as e:
        print(f"[FAIL] 序列化失败: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("所有测试通过!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_course_basic_info()
    sys.exit(0 if success else 1)
