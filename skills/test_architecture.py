# -*- coding: utf-8 -*-
"""
skills.test_architecture - 双层 Skill 架构测试

测试 Native Skill 和 Soft Skill 的注册、发现和执行。
"""

import sys
import asyncio
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def test_imports():
    """测试导入"""
    print("\n" + "="*60)
    print("Test 1: Module Imports")
    print("="*60)
    
    try:
        # 测试核心框架导入
        from skills._base import (
            BaseSkill,
            SkillMetadata,
            SkillCategory,
            SkillType,
            SkillRegistry,
            SkillExecutor,
        )
        print("[OK] Core framework imports")
        
        # 测试 Native Skill 导入
        from skills.native import (
            LessonPreparationSkill,
            ExerciseGeneratorSkill,
        )
        print("[OK] Native Skills imports")
        
        # 测试 Soft Skill 相关导入
        from skills._base import SoftSkillLoader, SoftSkillExecutor
        print("[OK] Soft Skill module imports")
        
        # 测试顶层导入
        from skills import (
            init_skills,
            list_skills,
            get_skill,
            execute_skill,
        )
        print("[OK] Unified interface imports")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_metadata():
    """测试元数据"""
    print("\n" + "="*60)
    print("Test 2: Metadata Definition")
    print("="*60)
    
    try:
        from skills.native import (
            LESSON_PREPARATION_METADATA,
            EXERCISE_GENERATOR_METADATA,
        )
        from skills._base import SkillType
        
        # 验证元数据
        assert LESSON_PREPARATION_METADATA.name == "lesson_preparation"
        assert LESSON_PREPARATION_METADATA.skill_type == SkillType.NATIVE
        print(f"[OK] LessonPreparation metadata: {LESSON_PREPARATION_METADATA.name}")
        
        assert EXERCISE_GENERATOR_METADATA.name == "exercise_generator"
        assert EXERCISE_GENERATOR_METADATA.skill_type == SkillType.NATIVE
        print(f"[OK] ExerciseGenerator metadata: {EXERCISE_GENERATOR_METADATA.name}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Metadata test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_native_skill_registration():
    """测试 Native Skill 注册"""
    print("\n" + "="*60)
    print("Test 3: Native Skill Registration")
    print("="*60)
    
    try:
        from skills._base import SkillRegistry, SkillType
        
        # 清空注册表
        SkillRegistry.clear()
        
        # 导入并注册
        from skills.native import LessonPreparationSkill
        SkillRegistry.register_native(LessonPreparationSkill)
        
        # 验证注册
        natives = SkillRegistry.list_natives()
        print(f"[OK] Registered Native Skills: {list(natives.keys())}")
        
        assert "lesson_preparation" in natives
        print("[OK] lesson_preparation registered")
        
        # 获取并验证
        skill = SkillRegistry.get("lesson_preparation")
        assert skill is not None
        print(f"[OK] Got skill: {skill}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Native registration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_soft_skill_loading():
    """测试 Soft Skill 加载"""
    print("\n" + "="*60)
    print("Test 4: Soft Skill Loading")
    print("="*60)
    
    try:
        from skills._base import SoftSkillLoader, SkillRegistry
        
        # 清空注册表
        SkillRegistry.clear()
        
        # 创建加载器
        loader = SoftSkillLoader()
        
        # 加载 soft/skills 目录
        soft_dir = project_root / "skills" / "soft" / "skills"
        skills = loader.load_directory(str(soft_dir))
        
        print(f"[OK] Loaded Soft Skills: {list(skills.keys())}")
        
        # 注册到注册中心
        for name, skill_data in skills.items():
            SkillRegistry.register_soft(skill_data)
        
        # 验证
        softs = SkillRegistry.list_softs()
        print(f"[OK] Registered Soft Skills: {list(softs.keys())}")
        
        # 获取并验证
        quick_lesson = SkillRegistry.get_soft("quick-lesson")
        if quick_lesson:
            desc = quick_lesson.get('description', '')[:50]
            print(f"[OK] quick-lesson description: {desc}...")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Soft skill loading test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_init_skills():
    """测试 init_skills 函数"""
    print("\n" + "="*60)
    print("Test 5: init_skills Function")
    print("="*60)
    
    try:
        from skills import init_skills, SkillRegistry, list_skills
        
        # 清空并初始化
        SkillRegistry.clear()
        soft_dir = project_root / "skills" / "soft" / "skills"
        init_skills(soft_skills_dir=str(soft_dir))
        
        # 列出所有
        all_skills = list_skills()
        print(f"[OK] Total skills: {len(all_skills)}")
        
        # 按类型统计
        native_count = sum(1 for s in all_skills.values() if s.get("skill_type") == "native")
        soft_count = sum(1 for s in all_skills.values() if s.get("skill_type") == "soft")
        print(f"   - Native Skills: {native_count}")
        print(f"   - Soft Skills: {soft_count}")
        
        # 打印列表
        print("\nSkill List:")
        for name, info in sorted(all_skills.items()):
            skill_type = info.get("skill_type", "unknown")
            display = info.get("display_name", name)
            print(f"  [{skill_type:6}] {name}: {display}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] init_skills test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_native_skill_execution():
    """测试 Native Skill 执行"""
    print("\n" + "="*60)
    print("Test 6: Native Skill Execution (Template Mode)")
    print("="*60)
    
    try:
        from skills._base import SkillRegistry, SkillExecutor, SkillType
        
        # 确保已注册
        if not SkillRegistry.list_natives():
            SkillRegistry.clear()
            from skills.native import LessonPreparationSkill
            SkillRegistry.register_native(LessonPreparationSkill)
        
        # 创建 Mock LLM Service
        class MockLLMService:
            async def generate(self, prompt, system=None):
                return "Mock response: This is a test lesson plan."
        
        mock_llm = MockLLMService()
        executor = SkillExecutor(llm_service=mock_llm)
        
        # 执行
        context = {
            "course_name": "高中数学",
            "topic": "函数的概念",
            "teaching_hours": 2,
        }
        
        # 使用 asyncio.run() 替代
        result = asyncio.run(executor.execute("lesson_preparation", context))
        
        print(f"[OK] Execution status: {result.get('status')}")
        print(f"[OK] Execution metadata: {result.get('metadata', {})}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Native skill execution test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_soft_skill_parsing():
    """测试 Soft Skill SKILL.md 解析"""
    print("\n" + "="*60)
    print("Test 7: SKILL.md Parsing")
    print("="*60)
    
    try:
        from skills._base import SoftSkillLoader
        
        loader = SoftSkillLoader()
        
        # 测试解析 quick-lesson.SKILL.md
        skill_file = project_root / "skills" / "soft" / "skills" / "quick-lesson.SKILL.md"
        skill_data = loader.load_file(str(skill_file))
        
        print(f"[OK] Parsed fields:")
        print(f"   - name: {skill_data.get('name')}")
        print(f"   - display_name: {skill_data.get('display_name')}")
        print(f"   - version: {skill_data.get('version')}")
        print(f"   - category: {skill_data.get('category')}")
        print(f"   - triggers: {skill_data.get('triggers')}")
        print(f"   - parameters: {len(skill_data.get('parameters', []))} items")
        print(f"   - content length: {len(skill_data.get('content', ''))} chars")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] SKILL.md parsing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_metadata_to_openclaw():
    """测试元数据转 OpenClaw 格式"""
    print("\n" + "="*60)
    print("Test 8: Metadata to OpenClaw Format")
    print("="*60)
    
    try:
        from skills._base import SkillMetadata, SkillCategory
        
        metadata = SkillMetadata(
            name="test-skill",
            display_name="Test Skill",
            version="1.0.0",
            description="This is a test skill",
            category=SkillCategory.WORKFLOW,
            tags=["test", "example"],
            triggers=["test", "example"],
            parameters=[
                {"name": "input", "type": "string", "required": True},
                {"name": "count", "type": "number", "required": False, "default": 10},
            ],
            content="# Test Skill\n\nThis is test content..."
        )
        
        # 转换为 OpenClaw 格式
        skill_md = metadata.to_openclaw_format()
        
        print("[OK] Generated SKILL.md:")
        print("-" * 40)
        print(skill_md[:500] + "..." if len(skill_md) > 500 else skill_md)
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Metadata conversion test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "#"*60)
    print("# AI Teacher Agent - Dual-Layer Skill Architecture Test")
    print("#"*60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Metadata Definition", test_metadata),
        ("Native Skill Registration", test_native_skill_registration),
        ("Soft Skill Loading", test_soft_skill_loading),
        ("init_skills Function", test_init_skills),
        ("Native Skill Execution", test_native_skill_execution),
        ("SKILL.md Parsing", test_soft_skill_parsing),
        ("Metadata to OpenClaw", test_metadata_to_openclaw),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"[FAIL] {name} test exception: {e}")
            results.append((name, False))
    
    # 总结
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} passed")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed! Dual-layer Skill architecture is working.")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
