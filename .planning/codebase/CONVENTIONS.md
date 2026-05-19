# Coding Conventions

**Analysis Date:** 2026-05-19

## Naming Patterns

**Files:**
- 模块文件：使用小写字母和下划线（snake_case）- `auth.py`, `data_sources.py`, `trading_executor.py`
- 测试文件：以 `test_` 前缀开头 - `test_agent_v1.py`, `test_data_providers.py`
- 路由模块：按功能分组，如 `agent_v1/`, `services/`, `utils/`

**Functions:**
- 公共函数：使用 snake_case - `generate_token()`, `verify_token()`, `get_db_connection()`
- 私有函数：以单下划线开头 - `_verify_token_version()`, `_apply_init_sql()`, `_sanitize()`
- 装饰器函数：使用描述性名称 - `login_required`, `admin_required`, `agent_required`

**Variables:**
- 局部变量：snake_case - `user_id`, `token_version`, `db_connection`
- 常量：UPPER_SNAKE_CASE - `TIMEFRAME_SECONDS`, `_CRITICAL_TABLES`
- 类属性：snake_case - 对于公共属性，私有属性使用单下划线前缀

**Classes:**
- 服务类：以 `Service` 后缀结尾 - `BacktestService`, `StrategyService`, `OAuthService`
- 数据源类：以 `DataSource` 后缀结尾 - `CryptoDataSource`, `USStockDataSource`, `BaseDataSource`
- 工作线程类：以 `Worker` 后缀结尾 - `PendingOrderWorker`, `ReflectionService`
- 异常类：以 `Error` 或 `Exception` 后缀结尾 - `DataSourceError`, `LiveTradingError`, `TimeoutError`
- 配置类：以 `Config` 后缀结尾 - `DataSourceConfig`, `MetaConfig`

## Code Style

**Formatting:**
- 使用标准 Python 格式（PEP 8 风格）
- 行长度：没有强制限制，但保持合理可读性
- 缩进：4 个空格

**Linting:**
- CI/CD 中使用 Python 语法检查（`compileall`）
- 导入检查确保关键模块可加载
- 没有发现 pylint 或 flake8 配置

**Type Hints:**
- 在新代码中部分使用类型提示
- 函数参数和返回值使用类型注解 - `def generate_token(user_id: int, username: str, role: str = 'user', token_version: int = 1) -> str:`
- 使用 `typing` 模块进行复杂类型 - `from typing import Dict, List, Any, Optional`

## Import Organization

**Order:**
1. 标准库导入（`os`, `sys`, `logging`, `datetime`）
2. 第三方库导入（`flask`, `jwt`, `pandas`, `numpy`）
3. 本地应用导入（`from app.utils import ...`, `from app.services import ...`）

**Pattern:**
```python
# 标准库
import os
import sys
from datetime import datetime, timedelta

# 第三方库
from flask import Flask, jsonify
import jwt
import pandas as pd

# 本地导入
from app.utils.logger import get_logger
from app.utils.db import get_db_connection
from app.services.strategy import StrategyService
```

**Path Aliases:**
- 没有使用路径别名
- 所有导入使用相对于 `app/` 的绝对路径

## Error Handling

**Patterns:**
- 使用自定义异常类进行领域特定错误 - `DataSourceError`, `UnsupportedMarketError`
- 函数在失败时返回 `None` 或空值而不是抛出异常（对于可预期的失败情况）
- 记录错误并继续执行而不是崩溃（特别是在启动时）
- 使用 `try-except` 块处理数据库操作和外部 API 调用
- 在关键路径上使用详细的错误日志记录

**示例:**
```python
try:
    from app.services.portfolio_monitor import start_monitor_service
    start_monitor_service()
except Exception as e:
    logger.error(f"Failed to start portfolio monitor: {e}")
    # 不抛出异常，避免破坏应用启动
```

**Database Errors:**
- 使用上下文管理器确保连接关闭
- 数据库初始化失败时记录警告而不是崩溃
- 权限检查收集所有失败而不是在第一个错误时中止

## Logging

**Framework:** 使用标准 Python `logging` 模块

**Setup:**
- 全局日志设置在 `app/utils/logger.py` 中的 `setup_logger()`
- 日志格式：`'%(asctime)s - %(name)s - %(levelname)s - %(message)s'`
- 文件日志使用 `RotatingFileHandler`，最大 10MB，保留 5 个备份
- 日志目录：`logs/`

**Levels:**
- 默认级别：`INFO`（可通过 `LOG_LEVEL` 环境变量配置）
- 特定模块覆盖：
  - `werkzeug`: `WARNING`（减少请求日志噪音）
  - `app.routes.kline`: `WARNING`（减少 K线日志噪音）
  - `app.services.usdt_payment_service`: `INFO`（保留 USDT 对账日志）
  - `app.routes.billing`: `INFO`（保留计费日志）

**Patterns:**
```python
# 获取 logger
logger = get_logger(__name__)

# 记录不同级别
logger.info("Portfolio monitor is disabled")
logger.warning(f"[FAIL] {strategy_type_name} {strategy_id} restore failed")
logger.error(f"Failed to start USDT order worker: {e}", exc_info=True)
```

**Logging in Tests:**
- 使用 `caplog` fixture 捕获日志输出
- 使用 `caplog.at_level()` 设置临时日志级别

## Comments

**When to Comment:**
- 复杂业务逻辑的解释
- 重要决策和权衡的说明
- 安全相关的注释
- 兼容性和迁移说明

**Module Docstrings:**
- 每个模块以描述其用途的 docstring 开头
- 使用三重双引号 `"""` - `"""Database Connection Utility - PostgreSQL Only"""`

**Function Docstrings:**
- 公共函数使用 Google 风格的 docstring
- 包含 Args、Returns 和 Raises 部分
- 示例：
```python
def generate_token(user_id: int, username: str, role: str = 'user', token_version: int = 1) -> str:
    """
    Generate JWT token with user information.

    Args:
        user_id: User ID
        username: Username
        role: User role (admin/manager/user/viewer)
        token_version: Token version for single-client enforcement

    Returns:
        JWT token string
    """
```

**Inline Comments:**
- 中英文混合，中文用于业务逻辑说明
- 英文用于技术实现细节
- 使用 `#` 进行单行注释

## Function Design

**Size:**
- 没有强制的大小限制
- 倾向于保持函数简短和专注
- 复杂逻辑拆分为多个辅助函数

**Parameters:**
- 使用类型注解提高可读性
- 默认参数用于可选配置
- 关键参数使用关键字参数形式

**Return Values:**
- 成功时返回预期类型
- 失败时返回 `None` 或空容器
- API 路由返回 `(response, status_code)` 元组
- 错误情况返回标准化错误响应

## Module Design

**Exports:**
- 使用 `__all__` 显式导出公共 API（在需要的地方）
- 大多数模块通过直接导入使用

**Barrel Files:**
- `app/routes/__init__.py` 注册所有蓝图
- `app/__init__.py` 作为应用工厂入口点
- `app/utils/db.py` 重新导出 PostgreSQL 特定函数

**Service Layer:**
- 业务逻辑在 `app/services/` 中
- 服务类封装相关功能
- 单例模式用于全局服务（如 `TradingExecutor`）

**Data Layer:**
- 数据源在 `app/data_sources/` 中
- 使用抽象基类定义接口
- 工厂模式创建数据源实例

## Configuration

**Environment Variables:**
- 所有配置通过环境变量读取
- 在 `app/config/settings.py` 中定义配置类
- 使用元类模式延迟加载配置

**Pattern:**
```python
class MetaConfig(type):
    @property
    def HOST(cls):
        return os.getenv('PYTHON_API_HOST', '0.0.0.0')
```

**Required vs Optional:**
- 提供合理的默认值
- 关键配置有后备值
- 启动时验证配置有效性

## API Design

**REST Endpoints:**
- 使用 Flask 蓝图组织路由
- URL 前缀按功能分组 - `/api/auth`, `/api/users`, `/api/agent/v1`
- HTTP 方法语义：GET（读取）、POST（创建）、PUT（更新）、DELETE（删除）

**Response Format:**
- Legacy API：`{"code": 1/0, "msg": "...", "data": {...}}`
- Agent Gateway API (v1)：`{"code": 0, "message": "ok", "data": {...}}`
- 错误响应包含详细信息：`{"code": int, "message": str, "details": any, "retriable": bool}`

**Authentication:**
- JWT Token 认证
- Bearer Token 格式：`Authorization: Bearer <token>`
- 装饰器保护端点：`@login_required`, `@admin_required`

## Database Conventions

**Naming:**
- 表名前缀：`qd_`（QuantDinger）- `qd_users`, `qd_strategies_trading`, `qd_agent_tokens`
- 列名：snake_case - `user_id`, `created_at`, `token_version`
- 主键：`id SERIAL PRIMARY KEY`
- 外键：`<table>_id INTEGER REFERENCES <table>(id)`

**Migrations:**
- SQL 迁移文件在 `migrations/` 目录
- 使用 `CREATE TABLE IF NOT EXISTS` 确保幂等性
- 版本化迁移文件：`v3_1_0_agent_gateway.sql`

**Indexes:**
- 为常用查询创建索引
- 索引命名：`idx_<table>_<column>` - `idx_users_referred_by`
- 唯一索引：`idx_<table>_<column>_unique`

**Queries:**
- 使用参数化查询防止 SQL 注入
- 使用上下文管理器管理连接
- 始终提交或回滚事务

## Concurrency

**Threading:**
- 后台工作线程用于长时间运行的任务
- 使用 `threading.Lock` 保护共享状态
- 避免在 Flask 重载器中启动两次线程

**Asyncio:**
- `ib_insync` 使用 asyncio
- 在启动时调用 `ib_insync.util.patchAsyncio()`

## Security

**Sensitive Data:**
- 从不记录敏感信息（密码、token 值）
- 使用环境变量存储密钥
- `.env.example` 提供模板（不包含实际值）

**JWT:**
- Token 版本控制实现单客户端登录
- Token 过期时间：7 天
- 使用 HS256 算法

**Password Hashing:**
- 使用 bcrypt 进行密码哈希
- 从不存储明文密码

## Testing Conventions

**Test Structure:**
- 使用 `pytest` 框架
- 测试文件以 `test_` 开头
- 测试函数以 `test_` 开头
- 使用描述性测试名称

**Fixtures:**
- 共享 fixtures 在 `conftest.py` 中
- 使用 `@pytest.fixture` 装饰器
- 支持 `autouse=True` 用于自动应用

**Mocking:**
- 使用 `monkeypatch` 修改环境变量和函数
- 使用 `unittest.mock` 进行复杂模拟
- 创建轻量级内存替代品以避免依赖

---

*Convention analysis: 2026-05-19*
