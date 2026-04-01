# AGENTS.md - AI Teacher Agent Development Guide

> This file provides guidelines for agentic coding agents working in this repository.

---

## 1. Project Overview

AI Teacher Agent is a Python-based intelligent teaching assistant that helps teachers:
- Generate lesson plans aligned with curriculum standards
- Create exercises and test papers
- Provide teaching explanations and assessments
- Process user feedback for continuous improvement

**Tech Stack:**
- Python 3.8+ (dataclasses, pytest)
- Vue 3 + Element Plus (frontend in `web/frontend`)
- PyYAML for configuration
- MCP (Model Context Protocol) support

---

## 2. Build/Lint/Test Commands

### Python Backend

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests with coverage
python -m pytest tests/ --cov=src/ --cov-report=html

# Run all tests (verbose)
python -m pytest tests/ -v

# Run a single test file
python -m pytest tests/skills/test_search_standard.py -v

# Run a single test class
python -m pytest tests/skills/test_search_standard.py::TestSearchCurriculumStandard -v

# Run a single test method
python -m pytest tests/skills/test_search_standard.py::TestSearchCurriculumStandard::test_normal_search_success -v

# Code formatting
black src/ tests/

# Type checking
mypy src/
```

### Frontend (Vue.js)

```bash
# Navigate to frontend directory
cd web/frontend

# Install dependencies
npm install

# Development server
npm run dev

# Production build
npm run build

# Preview build
npm run preview
```

### Running Demos

```bash
# MVP demo
python mvp_demo.py

# Extended demo
python extended_demo.py

# Full demo
python full_demo.py

# Assessment module demo
python assessment_demo.py

# CLI
python cli.py
python cli_assessment.py
```

---

## 3. Code Style Guidelines

### 3.1 Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Classes | PascalCase | `CourseBasicInfo`, `LessonPlan` |
| Functions/Variables | snake_case | `search_curriculum_standard`, `valid_course_data` |
| Constants | UPPER_SNAKE_CASE | `VALID_EDUCATION_LEVELS`, `MAX_TOPIC_LENGTH` |
| Private methods | _snake_case | `_validate_and_normalize` |
| Dataclass fields | snake_case | `education_level`, `subject` |

### 3.2 Type Hints

Always use type hints for function parameters and return values:

```python
from typing import Optional, Dict, Any, List

def search_curriculum_standard(
    course_info: Dict[str, Any],
    search_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    ...
```

### 3.3 Dataclasses for Data Objects

Use `@dataclass` decorator for data models:

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class CourseBasicInfo:
    education_level: str
    subject: str
    topic: str
    grade: Optional[str] = None
    suggested_hours: int = 1
    input_timestamp: datetime = field(default_factory=datetime.now)
```

### 3.4 Import Organization

Order imports alphabetically within groups:

```python
# Standard library
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import uuid4

# Third-party
import pytest
from dataclasses import dataclass, field, asdict

# Project local
from src.models import CourseBasicInfo
from src.skills import LessonPreparationSkill
```

### 3.5 Function Design

Follow these principles:
- **Single responsibility**: One function does one thing
- **Input validation**: Validate all inputs, raise `ValueError` for invalid data
- **Error handling**: Catch exceptions and convert to business exceptions
- **Documentation**: Docstrings with Chinese descriptions

```python
def _validate_and_normalize(self):
    """验证并规范化数据"""
    if self.education_level not in self.VALID_EDUCATION_LEVELS:
        raise ValueError(
            f"education_level必须是{self.VALID_EDUCATION_LEVELS}之一，"
            f"当前值：{self.education_level}"
        )
```

### 3.6 Test Conventions

- Test files in `tests/` mirror `src/` structure
- Use `pytest` with fixtures
- Use `@pytest.mark.asyncio` for async tests
- Mock external dependencies with `unittest.mock`

```python
import pytest
from unittest.mock import Mock, patch, AsyncMock

class TestSearchCurriculumStandard:
    """测试类: search_curriculum_standard"""
    
    @pytest.fixture
    def valid_course_info(self):
        """有效的课程信息"""
        return {
            "education_level": "高中",
            "subject": "数学",
            "topic": "函数的概念"
        }
    
    @pytest.mark.asyncio
    async def test_normal_search_success(self, valid_course_info, mock_search_service):
        """TC-001: 正常搜索成功"""
        result = await search_curriculum_standard(valid_course_info)
        assert result is not None
```

### 3.7 Error Handling

- Use custom exception classes for business errors
- Provide meaningful error messages in Chinese
- Log errors with appropriate level

```python
class NoResultError(Exception):
    """搜索无结果异常"""
    pass

class ValidationError(Exception):
    """数据验证异常"""
    pass
```

### 3.8 Code Formatting

- Line length: 100 characters (black default)
- Use 4 spaces for indentation (no tabs)
- Trailing commas in multi-line structures

---

## 4. Project Structure

```
ai_teacher_agent/
├── src/
│   ├── models/           # Data objects (16 models)
│   ├── mocks/            # Mock services
│   └── skills/
│       ├── lesson_preparation/
│       └── teaching_assessment/
├── tests/                # Test code (mirrors src/)
│   ├── models/
│   └── skills/
├── config/               # Configuration files
├── docs/                 # Design documentation
├── web/frontend/         # Vue.js frontend
└── AGENTS.md            # This file
```

---

## 5. Key Development Principles

Based on `docs/DEVELOPMENT_GUIDELINES.md`:

1. **Requirements First**: No code without documented requirements
2. **Test-Driven**: Tests must exist before implementation
3. **Data-Driven**: All data objects must have complete definitions
4. **Documentation Sync**: Keep docs updated with code changes
5. **Incremental Delivery**: Complete one task at a time with passing tests

### Coverage Requirements
- Line coverage: ≥ 90%
- Branch coverage: ≥ 85%
- All exception paths must be tested

---

## 6. Configuration

Main configuration in `config/config.yaml`:
- LLM settings (provider, model, API keys)
- Agent configuration
- Tool settings (search, file, PPT)
- Knowledge base paths
- Pipeline workflows
- MCP server configuration

---

## 7. Common Tasks

### Adding a New Data Model
1. Create file in `src/models/`
2. Use `@dataclass` decorator
3. Add validation in `__post_init__`
4. Add serialization methods (`to_dict`, `from_dict`, `to_json`, `from_json`)
5. Add tests in `tests/models/`

### Adding a New Skill
1. Create module in `skills/` (Native Skill) or `skills/soft/skills/` (Soft Skill)
2. Define skill class with clear interface
3. Add comprehensive error handling
4. Add tests in `tests/skills/`
5. Update documentation

### Running a Single Test
```bash
python -m pytest path/to/test_file.py::TestClassName::test_method_name -v
```

---

## 8. API Development Rules

### 8.1 FastAPI URL 尾部斜杠规则

**问题描述**：
FastAPI 默认会对没有尾部斜杠的路由（如 `/lesson-plans`）返回 307 Temporary Redirect 重定向到带尾部斜杠的版本（如 `/lesson-plans/`）。

**关键问题**：
- 浏览器在发送 307/308 重定向请求时，**不会携带原始请求的 Authorization header**
- 这会导致已登录用户的请求在重定向后变成未授权（401 Unauthorized）

**解决方案**：

1. **方案一（推荐）**：前端 API 使用不同的路径格式，避免触发重定向
   ```javascript
   // 列表接口使用 /list 后缀
   request.get('/lesson-plans/list')
   
   // 详情接口直接用 ID
   request.get('/lesson-plans/123')
   
   // 创建接口
   request.post('/lesson-plans', data)
   ```

2. **方案二**：后端禁用重定向
   ```python
   # FastAPI 应用级别设置
   app = FastAPI(redirect_slashes=False)
   
   # 或路由组级别设置
   router = APIRouter(prefix="/lesson-plans", redirect_slashes=False)
   ```

**经验总结**：
- 前后端 URL 格式保持一致，避免 307 重定向
- 特别留意：所有需要认证的接口，重定向会导致 token 丢失
- 推荐使用方案一（前端使用不同路径），更简单可靠

---

## 9. References

- [Development Guidelines](docs/DEVELOPMENT_GUIDELINES.md)
- [Data Dictionary](docs/data_dictionary.md)
- [System Architecture](docs/system_architecture.md)
- README.md for feature overview
