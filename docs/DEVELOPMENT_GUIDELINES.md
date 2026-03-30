# AI教师Agent项目开发准则

> 版本：v1.0
> 创建日期：2026-03-22
> 适用范围：AI教师Agent全项目开发

---

## 一、开发流程总则

### 1.1 核心原则

1. **需求先行**：所有功能必须有明确、细化的需求文档
2. **依赖追踪**：所有依赖必须显式声明，未就绪的依赖视为新需求
3. **数据驱动**：所有数据对象必须完整定义，包括结构、约束、生命周期
4. **测试先行**：每个函数必须有测试代码和测试数据，先于实现编写
5. **文档同步**：所有分析、设计、实现、测试结果必须实时记录
6. **渐进交付**：按任务计划逐个完成，每个任务必须通过测试

### 1.2 禁止事项

- ❌ 在没有需求文档的情况下开始编码
- ❌ 在没有测试用例的情况下实现功能
- ❌ 跳过文档直接提交代码
- ❌ 合并未通过测试的功能
- ❌ 隐瞒或延迟报告依赖问题

---

## 二、需求工程规范

### 2.1 需求层级

```
系统需求 (System Requirements)
    └── 模块需求 (Module Requirements)
            └── 功能需求 (Functional Requirements)
                    └── 功能点 (Function Points)
                            └── 函数规格 (Function Specifications)
```

### 2.2 需求文档模板

每个需求文档必须包含：

1. **需求标识**：ID、名称、优先级、状态
2. **需求描述**：业务背景、用户价值、验收标准
3. **输入输出**：数据对象、格式、约束
4. **依赖分析**：内部依赖、外部依赖、未就绪依赖
5. **数据对象**：涉及的所有数据结构定义
6. **功能分解**：细化到功能点级别

### 2.3 依赖管理

| 依赖类型 | 处理方式 |
|---------|---------|
| 已就绪依赖 | 直接引用，记录版本 |
| 未就绪内部依赖 | 添加为新需求，分配ID，排入计划 |
| 未就绪外部依赖 | 评估替代方案，记录风险，制定降级策略 |

---

## 三、数据对象规范

### 3.1 数据对象定义模板

```yaml
数据对象名称: [Name]
数据对象ID: [DO-XXX]
描述: [Description]

属性列表:
  - 属性名: [name]
    类型: [type]
    约束: [constraints]
    默认值: [default]
    说明: [description]

关系:
  - 关联对象: [RelatedObject]
    关系类型: [1:1|1:N|N:M]
    关联字段: [field]

生命周期:
  - 创建: [when]
  - 更新: [when]
  - 删除: [when]

验证规则:
  - [rule1]
  - [rule2]
```

### 3.2 数据字典维护

所有数据对象必须在 `docs/data_dictionary.md` 中登记，包括：
- 对象定义
- 使用位置
- 变更历史

---

## 四、功能点规范

### 4.1 功能点定义

每个功能点必须包含：

1. **基本信息**：ID、名称、所属模块、优先级
2. **功能描述**：做什么、为什么做、不做什么
3. **前置条件**：执行前必须满足的条件
4. **后置条件**：执行后保证的状态
5. **正常流程**：主成功场景（步骤编号）
6. **异常流程**：错误处理分支
7. **业务规则**：必须遵守的业务约束

### 4.2 功能点编号规则

```
[系统]-[模块]-[功能]-[序号]
示例：ATA-LP-PREP-001 (AI Teacher Agent - Lesson Preparation - Prepare - 001)
```

---

## 五、函数设计规范

### 5.1 函数规格模板

```python
"""
函数名称: [function_name]
函数ID: [FN-XXX]
所属功能点: [FP-XXX]

功能描述:
    [详细描述函数做什么]

输入参数:
    param1 (Type): 描述，约束条件
    param2 (Type): 描述，约束条件

返回值:
    ReturnType: 描述，可能的取值

异常:
    ExceptionType: 触发条件，处理方式

伪代码:
    1. [步骤1]
    2. [步骤2]
       IF [条件] THEN
           [处理A]
       ELSE
           [处理B]
    3. [步骤3]
       FOR [循环条件] DO
           [循环体]
       END FOR
    4. RETURN [结果]

调用关系:
    - 调用: [被调用的函数列表]
    - 被调用: [调用本函数的函数列表]

测试用例:
    TC-001: 正常情况，输入X，期望输出Y
    TC-002: 边界情况，输入Z，期望异常W
"""
```

### 5.2 函数实现要求

1. **单一职责**：每个函数只做一件事
2. **输入验证**：所有输入必须验证，失败立即抛出异常
3. **错误处理**：所有异常必须捕获并转换为业务异常
4. **日志记录**：关键步骤必须记录日志
5. **性能考虑**：复杂操作考虑异步和缓存

---

## 六、测试规范

### 6.1 测试先行原则

```
编写测试代码 → 编写测试数据 → 实现函数 → 运行测试 → 修复问题 → 通过测试
```

### 6.2 测试代码模板

```python
import pytest
from unittest.mock import Mock, patch

class TestFunctionName:
    """测试函数: [function_name]"""
    
    @pytest.fixture
    def test_data(self):
        """测试数据"""
        return {
            "valid_input": {...},
            "invalid_input": {...},
            "boundary_input": {...},
            "expected_output": {...}
        }
    
    def test_normal_case(self, test_data):
        """TC-001: 正常情况"""
        result = function_name(test_data["valid_input"])
        assert result == test_data["expected_output"]
    
    def test_invalid_input(self, test_data):
        """TC-002: 无效输入"""
        with pytest.raises(ValueError):
            function_name(test_data["invalid_input"])
    
    def test_boundary_case(self, test_data):
        """TC-003: 边界情况"""
        result = function_name(test_data["boundary_input"])
        assert result is not None
```

### 6.3 测试覆盖率要求

- 行覆盖率：≥ 90%
- 分支覆盖率：≥ 85%
- 所有异常路径必须测试

---

## 七、文档规范

### 7.1 文档清单

| 文档 | 位置 | 维护时机 |
|-----|------|---------|
| 需求规格说明书 | `docs/requirements/` | 需求确定时 |
| 数据字典 | `docs/data_dictionary.md` | 数据对象变更时 |
| 架构设计文档 | `docs/architecture/` | 设计评审后 |
| 接口文档 | `docs/api/` | 接口实现后 |
| 测试报告 | `docs/test_reports/` | 测试完成后 |
| 任务计划 | `docs/plans/` | 计划制定/调整时 |
| 开发日志 | `docs/logs/` | 每日更新 |

### 7.2 文档格式

- 所有文档使用 Markdown 格式
- 代码示例使用 Python 语法高亮
- 图表使用 Mermaid 或 ASCII 艺术

---

## 八、任务计划规范

### 8.1 任务定义

每个任务必须包含：

1. **任务标识**：ID、名称、类型（需求/设计/实现/测试）
2. **任务描述**：具体要做什么
3. **输入产物**：依赖的前置任务输出
4. **输出产物**：交付的文档/代码/测试结果
5. **验收标准**：完成的判定条件
6. **时间估算**：预计工时
7. **负责人**：执行人

### 8.2 任务状态流转

```
待启动 → 进行中 → 待测试 → 测试中 → 测试通过 → 已完成
              ↓           ↓           ↓
           阻塞中      修复中      测试失败
```

---

## 九、质量保证

### 9.1 代码审查清单

- [ ] 是否符合函数设计规范
- [ ] 是否有对应的测试代码
- [ ] 测试是否全部通过
- [ ] 文档是否同步更新
- [ ] 是否有未处理的依赖

### 9.2 完成标准

一个功能点完成的定义：
1. ✅ 代码实现通过审查
2. ✅ 测试代码完整，覆盖率达标
3. ✅ 所有测试用例通过
4. ✅ 文档已更新
5. ✅ 无已知缺陷

---

## 十、工具支持

### 10.1 推荐工具

| 用途 | 工具 |
|-----|------|
| 测试框架 | pytest |
| 覆盖率 | pytest-cov |
| 代码质量 | pylint, black |
| 类型检查 | mypy |
| 文档生成 | mkdocs |

### 10.2 自动化脚本

```bash
# 运行测试
python -m pytest tests/ --cov=src/ --cov-report=html

# 代码格式化
black src/ tests/

# 类型检查
mypy src/
```

---

## 附录：模板文件

### A. 需求文档模板

见 `docs/templates/requirement_template.md`

### B. 函数规格模板

见 `docs/templates/function_template.md`

### C. 测试代码模板

见 `docs/templates/test_template.py`

---

**准则维护**：本准则由项目技术负责人维护，变更需经评审通过。

**生效日期**：2026-03-22
