# Testing Patterns

**Analysis Date:** 2026-05-19

## Test Framework

**Runner:**
- **pytest** (版本未在 requirements.txt 中明确，但测试代码广泛使用 pytest 特性)
- Config: 测试文件位于 `backend_api_python/tests/` 目录
- MCP 服务器使用 pytest（见 `mcp_server/pyproject.toml`）

**Assertion Library:**
- 使用标准 pytest 断言（不需要额外库）
- 使用 Python 内置 `assert` 语句

**Run Commands:**
```bash
# 从项目根目录运行后端测试
cd backend_api_python
pytest tests/              # 运行所有测试
pytest tests/ -v          # 详细模式
pytest tests/ -k "test_agent_v1"  # 运行特定测试
pytest tests/test_agent_v1.py -v  # 运行特定文件
```

**Coverage:**
- 当前没有配置代码覆盖率工具（pytest-cov 未配置）
- `.dockerignore` 文件中包含 `.coverage`，表明曾经考虑过覆盖率

## Test File Organization

**Location:**
- 主要测试目录：`backend_api_python/tests/`
- 测试与源代码分离（不在源代码目录中）
- MCP 服务器测试：`mcp_server/tests/`

**Naming:**
- 测试文件：`test_<module>.py` - `test_agent_v1.py`, `test_data_providers.py`
- 测试函数：`test_<feature>_<scenario>` - `test_health_is_public()`, `test_nan_becomes_null()`
- 测试类：较少使用，主要使用函数式测试

**Structure:**
```
backend_api_python/
├── tests/
│   ├── conftest.py                    # 共享 fixtures
│   ├── test_agent_v1.py               # Agent Gateway 路由测试
│   ├── test_agent_v1_saas_guard.py    # SaaS 模式防护测试
│   ├── test_agent_jobs_progress.py    # Agent 任务进度测试
│   ├── test_data_providers.py         # 数据提供者测试
│   ├── test_db_bootstrap.py           # 数据库启动行为测试
│   ├── test_experiment_services.py    # 实验服务测试
│   ├── test_json_encoder.py           # JSON 编码器测试
│   ├── test_usdt_payment_*.py         # USDT 支付相关测试（多个文件）
│   └── ...（其他测试文件）
```

## Test Structure

**Suite Organization:**
```python
"""模块 docstring 描述测试目的"""

import pytest
# 导入被测试的模块

# 可选：模块级别的 fixtures 或辅助函数

def test_feature_specific_behavior():
    """使用描述性名称"""
    # Arrange
    # 设置测试数据
    # Act
    # 执行被测试的代码
    # Assert
    # 验证结果
    assert expected == actual
```

**Patterns:**

**Setup Pattern:**
- 使用 `@pytest.fixture` 定义可重用的测试组件
- Session-scoped fixtures 用于昂贵的设置（如应用创建）
- Function-scoped fixtures 用于隔离测试
- Autouse fixtures 用于自动应用设置/清理

**Teardown Pattern:**
- 使用 `yield` 在 fixtures 中提供清理代码
- 上下文管理器用于资源管理
- 显式清理在 `monkeypatch` 回滚后

**Assertion Pattern:**
- 使用简单的 `assert` 语句
- pytest 自动提供详细的失败信息
- 对于复杂对象，比较特定的属性而不是整个对象

## Mocking

**Framework:** pytest 的 `monkeypatch` fixture 和 `unittest.mock`

**Patterns:**

**环境变量 Mock:**
```python
def test_with_custom_env(monkeypatch):
    monkeypatch.setenv("ADANOS_API_KEY", "test_key")
    # 测试代码
    monkeypatch.delenv("ADANOS_API_KEY", raising=False)  # 清理
```

**函数 Mock:**
```python
def test_with_mocked_function(monkeypatch):
    monkeypatch.setattr(agent_auth, "_lookup_token", lambda raw: None)
    # 调用使用 _lookup_token 的代码
```

**数据库 Mock:**
```python
class _FakeCursor:
    def execute(self, sql, *args, **kwargs):
        # 模拟数据库行为
        pass

def test_without_real_db(monkeypatch):
    monkeypatch.setattr(db_module, "get_db_connection", lambda: _FakeConn())
```

**HTTP Mock:**
```python
class FakeResponse:
    status_code = 200
    @staticmethod
    def json():
        return {"key": "value"}

class FakeSession:
    @staticmethod
    def get(url, **kwargs):
        return FakeResponse()

monkeypatch.setattr("module.Session", FakeSession)
```

**What to Mock:**
- 外部服务调用（数据库、HTTP API）
- 文件系统操作
- 时间/日期相关函数
- 环境变量
- 昂贵的资源

**What NOT to Mock:**
- 纯函数逻辑
- 简单的数据转换
- 被测试单元的核心逻辑

## Fixtures and Factories

**Test Data:**

**Helper Functions:**
```python
def _fake_token_row(scopes: str = "R", paper_only: bool = True,
                    status: str = "active", expires_at=None,
                    rate_limit_per_min: int = 60) -> dict:
    """创建模拟 token 行数据"""
    return {
        "id": 999,
        "user_id": 1,
        "name": "test-agent",
        "scopes": scopes,
        "markets": "*",
        "instruments": "*",
        "paper_only": paper_only,
        "rate_limit_per_min": rate_limit_per_min,
        "status": status,
        "expires_at": expires_at,
    }
```

**Common Fixtures (conftest.py):**
```python
@pytest.fixture(scope="session")
def app():
    """创建测试应用实例"""
    application = create_app("testing")
    application.config["TESTING"] = True
    return application

@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()
```

**Location:**
- 共享 fixtures：`backend_api_python/tests/conftest.py`
- 特定 fixtures：在测试文件中定义

## Coverage

**Requirements:** 没有强制执行的覆盖率目标

**View Coverage:**
- 未配置 pytest-cov，无法直接生成覆盖率报告
- 需要安装 pytest-cov 并配置才能查看覆盖率

**Status:**
- 代码中有一些注释提到覆盖率（如 `coverage for the lookup table`）
- `.dockerignore` 中排除 `.coverage` 文件
- 建议添加 pytest-cov 到 requirements.txt 并配置覆盖率目标

## Test Types

**Unit Tests:**
- **范围和途径：** 测试单个函数或类的行为
- **示例：**
  - `test_json_encoder.py` - 测试 NaN/Inf JSON 序列化
  - `test_safe_float_valid()` - 测试数据验证函数
  - `test_three_minute_timeframe_is_registered()` - 测试配置常量

**Integration Tests:**
- **范围和途径：** 测试多个组件协作
- **示例：**
  - `test_agent_v1.py` - 测试完整的 API 端点（包括认证、路由、响应）
  - `test_data_providers.py` - 测试数据提供者与外部 API 的集成
  - `test_experiment_services.py` - 测试实验服务组件交互

**E2E Tests:**
- **框架：** 未使用
- 系统级端到端测试当前不存在
- 主要依赖手动测试和集成测试

## Common Patterns

**Async Testing:**
```python
# 使用 pytest-asyncio（如果需要）
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None
```

**Error Testing:**
```python
def test_invalid_token_rejected(client, monkeypatch):
    """测试无效 token 被拒绝"""
    agent_auth._schema_ready = True
    monkeypatch.setattr(agent_auth, "_lookup_token", lambda raw: None)
    resp = client.get("/api/agent/v1/whoami", headers=_bearer())
    assert resp.status_code == 401
```

**Parametrized Testing:**
```python
@pytest.mark.parametrize("raw,expected", [
    ("saas", True),
    ("SaaS", True),
    ("SAAS", True),
    ("selfhost", False),
])
def test_is_saas_mode_recognizes_known_spellings(raw, expected):
    """参数化测试多种输入变体"""
    assert is_saas_mode(raw) == expected
```

**Database-less Testing:**
```python
# 使用内存替代品避免需要真实数据库
class _MemCursor:
    def execute(self, sql, params=()):
        # 模拟数据库行为
        pass

def test_without_db(monkeypatch):
    monkeypatch.setattr(db_module, "get_db_connection", lambda: _FakeConn())
    # 测试代码不需要真实数据库
```

## CI/CD Testing

**GitHub Actions:**
- 工作流文件：`.github/workflows/basic-ci.yml`
- 触发条件：推送到 main/master 分支，或 PR 到这些分支

**Current CI Tests:**
```yaml
# Python 语法检查
python -m py_compile run.py
python -m compileall -q app/ scripts/

# 导入检查（验证模块可加载）
python -c "from app import create_app; from app.config import settings"
```

**What CI Does:**
- ✓ 检查 Python 语法错误
- ✓ 验证关键模块可导入
- ✓ 验证 docker-compose 配置
- ✗ 不运行 pytest 测试套件（避免需要数据库等外部服务）

**What CI Does NOT Do:**
- 不运行单元测试
- 不生成覆盖率报告
- 不运行集成测试（需要数据库）

**Improvement Path:**
- 添加测试数据库到 CI 环境
- 配置 pytest 在 CI 中运行
- 添加覆盖率报告上传
- 添加测试结果报告

## Test Discovery

**Auto-Discovery:**
- pytest 自动发现 `test_*.py` 和 `*_test.py` 文件
- 自动发现 `test_*` 函数
- 使用 `--co`（collect only）查看将被运行的测试

**Running Specific Tests:**
```bash
# 按名称运行
pytest -k "test_health"

# 按模块运行
pytest tests/test_agent_v1.py

# 按标记运行（如果定义了标记）
pytest -m "not slow"
```

## Test Environment Setup

**Environment Variables:**
```python
# conftest.py 中设置最小环境
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-unit-tests")
os.environ.setdefault("ADMIN_USER", "testadmin")
os.environ.setdefault("ADMIN_PASSWORD", "testpass123")
os.environ.setdefault("TQDM_DISABLE", "1")
os.environ.setdefault("CACHE_ENABLED", "false")
```

**Test Configuration:**
- 应用创建时使用 `create_app("testing")`
- 设置 `app.config["TESTING"] = True`
- 避免 Flask 重载器干扰

## Test Data Management

**Factories:**
- 使用辅助函数创建测试数据
- 每个测试创建独立的数据
- 避免共享状态

**Cleanup:**
- 使用 `autouse` fixtures 自动清理
- 每个测试后重置状态
- 清理临时文件和环境变量

## Debugging Tests

**Verbose Output:**
```bash
pytest -v              # 详细输出
pytest -vv             # 更详细的输出
pytest -s              # 显示 print 输出
```

**Stopping on First Failure:**
```bash
pytest -x              # 第一个失败后停止
pytest --maxfail=3     # 3 个失败后停止
```

**Running Last Failed:**
```bash
pytest --lf            # 只运行上次失败的测试
pytest --ff            # 先运行失败的，再运行其他的
```

---

*Testing analysis: 2026-05-19*
