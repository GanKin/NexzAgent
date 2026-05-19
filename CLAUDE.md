<!-- GSD:project-start source:PROJECT.md -->
## Project

**市场概览模块 (Market Overview)**

在 QuantDinger 现有系统中新增「市场概览」模块，位于前端导航栏「AI资产分析」tab 之上，仅对管理员开放。用户通过上传每日 Excel 数据表（趋势识别+相对比价+资金监控），系统自动解析入库并记录时序，提供 Dashboard 概览、代码列表筛选、标的详情时序查看等功能。

**Core Value:** 让管理员快速掌握全市场多维度状态（趋势、比价、杠杆资金），通过结构化筛选规则发现交易机会和风险标的，替代手动查看 Excel 的工作方式。

### Constraints

- **Tech Stack**: 必须使用现有技术栈（Vue 2 + Flask + PostgreSQL），不引入新框架
- **Permission**: 仅管理员可访问，利用现有 admin 角色判断
- **Data Format**: Excel 使用体系 B（中文列名），需兼容未来可能的体系 A
- **Performance**: 单次 Excel 约 1000 行 × 25 列，导入应在 5 秒内完成
- **Storage**: 时序数据保留至少 1 年，需考虑存储效率
<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->
## Technology Stack

## Languages
- Python 3.12 (Docker) / Python 3.10+ (本地部署) - 后端 API 和策略执行引擎
- JavaScript/TypeScript - 前端 Vue 应用 (独立仓库 QuantDinger-Vue)
- SQL - PostgreSQL 数据库模式和初始化脚本
- Shell - Docker 入口脚本和部署脚本
- YAML - Docker Compose 和 GitHub Actions 配置
## Runtime
- Python 3.12-slim-bookworm (Docker 基础镜像)
- 可选构建区域: cn (阿里云镜像) / global (官方源)
- pip (Python)
- Lockfile: 存在于 `backend_api_python/requirements.txt`
- Gunicorn 22.0+ (生产 WSGI 服务器)
- worker_class: gthread (单 worker 多线程)
- 默认配置: 1 worker, 4-8 threads
## Frameworks
- Flask 3.1.3 - Web 框架和 API 网关
- Flask-CORS 6.0.0 - 跨域资源共享
- Vue.js - SPA 前端框架
- Ant Design Vue - UI 组件库
- KLineCharts - K 线图表组件
- ECharts - 数据可视化
- Nginx - 前端静态文件服务
- pandas 1.5.0+ - 数据处理和分析
- numpy (隐式依赖) - 数值计算
- CCXT 4.0.0+ - 加密货币交易所集成 (100+ 交易所)
- yfinance 0.2.18+ - Yahoo Finance 数据
- finnhub-python 2.4.18+ - Finnhub API 集成
- akshare 1.12.0+ - 中国金融数据
- ib_insync 0.9.86+ - Interactive Brokers (IBKR) 集成
- alpaca-py 0.30.0+ - Alpaca 美股和加密货币集成
- MetaTrader5 5.0.45+ (可选) - MT5 外汇集成 (仅 Windows)
## Key Dependencies
- psycopg2-binary 2.9.9+ - PostgreSQL 驱动
- redis 5.0.0+ - Redis 缓存客户端
- PyJWT 2.12.0+ - JWT 令牌处理
- bcrypt 4.1.0+ - 密码哈希
- cryptography 43.0.0+ - 加密工具
- bip-utils 2.9.0+ - HD 钱包地址派生 (USDT 支付)
- requests 2.32.0+ - HTTP 客户端
- certifi 2024.2.2+ - SSL 证书
- PySocks 1.7.1+ - SOCKS 代理支持
- python-dotenv 1.0.1+ - 环境变量管理
## Configuration
- 主配置文件: `backend_api_python/.env`
- Docker Compose 覆盖: 项目根目录 `.env` (可选)
- 配置加载: `run.py` 自动加载 `.env` 文件
- 品牌和标识: `BRAND_*` 系列变量
- 认证: `SECRET_KEY`, `ADMIN_USER`, `ADMIN_PASSWORD`
- 数据库: `DATABASE_URL` (PostgreSQL 连接字符串)
- AI/LLM: `LLM_PROVIDER`, `*_API_KEY`, `*_MODEL`
- OAuth: `GOOGLE_CLIENT_ID`, `GITHUB_CLIENT_ID`
- 支付: `USDT_PAY_ENABLED`, `*_ADDRESS`, `*_API_KEY`
- 代理: `PROXY_URL` (中国大陆访问 Binance/Coinbase 必需)
- Dockerfile: `backend_api_python/Dockerfile`
- 构建参数: `BASE_IMAGE`, `BUILD_REGION`
- 多架构支持: amd64/arm64
## Platform Requirements
- Docker + Docker Compose v2
- Git
- Python 3.10+ (本地开发)
- 端口: 8888 (前端), 5000 (API), 5432 (PostgreSQL), 6379 (Redis)
- Docker 部署 (推荐) 或 bare-metal Python
- PostgreSQL 16
- Redis 7 (可选但推荐)
- 反向代理 (Nginx/Caddy) 用于 HTTPS
- 最小磁盘: 几 GB (用于数据和日志增长)
- Linux (推荐生产环境)
- macOS (开发和测试)
- Windows (支持，但 MT5 集成仅限 Windows)
- AWS Marketplace AMI (CentOS 9)
- Railway (支持)
- 任何支持 Docker 的云平台
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

## Naming Patterns
- 模块文件：使用小写字母和下划线（snake_case）- `auth.py`, `data_sources.py`, `trading_executor.py`
- 测试文件：以 `test_` 前缀开头 - `test_agent_v1.py`, `test_data_providers.py`
- 路由模块：按功能分组，如 `agent_v1/`, `services/`, `utils/`
- 公共函数：使用 snake_case - `generate_token()`, `verify_token()`, `get_db_connection()`
- 私有函数：以单下划线开头 - `_verify_token_version()`, `_apply_init_sql()`, `_sanitize()`
- 装饰器函数：使用描述性名称 - `login_required`, `admin_required`, `agent_required`
- 局部变量：snake_case - `user_id`, `token_version`, `db_connection`
- 常量：UPPER_SNAKE_CASE - `TIMEFRAME_SECONDS`, `_CRITICAL_TABLES`
- 类属性：snake_case - 对于公共属性，私有属性使用单下划线前缀
- 服务类：以 `Service` 后缀结尾 - `BacktestService`, `StrategyService`, `OAuthService`
- 数据源类：以 `DataSource` 后缀结尾 - `CryptoDataSource`, `USStockDataSource`, `BaseDataSource`
- 工作线程类：以 `Worker` 后缀结尾 - `PendingOrderWorker`, `ReflectionService`
- 异常类：以 `Error` 或 `Exception` 后缀结尾 - `DataSourceError`, `LiveTradingError`, `TimeoutError`
- 配置类：以 `Config` 后缀结尾 - `DataSourceConfig`, `MetaConfig`
## Code Style
- 使用标准 Python 格式（PEP 8 风格）
- 行长度：没有强制限制，但保持合理可读性
- 缩进：4 个空格
- CI/CD 中使用 Python 语法检查（`compileall`）
- 导入检查确保关键模块可加载
- 没有发现 pylint 或 flake8 配置
- 在新代码中部分使用类型提示
- 函数参数和返回值使用类型注解 - `def generate_token(user_id: int, username: str, role: str = 'user', token_version: int = 1) -> str:`
- 使用 `typing` 模块进行复杂类型 - `from typing import Dict, List, Any, Optional`
## Import Organization
- 没有使用路径别名
- 所有导入使用相对于 `app/` 的绝对路径
## Error Handling
- 使用自定义异常类进行领域特定错误 - `DataSourceError`, `UnsupportedMarketError`
- 函数在失败时返回 `None` 或空值而不是抛出异常（对于可预期的失败情况）
- 记录错误并继续执行而不是崩溃（特别是在启动时）
- 使用 `try-except` 块处理数据库操作和外部 API 调用
- 在关键路径上使用详细的错误日志记录
- 使用上下文管理器确保连接关闭
- 数据库初始化失败时记录警告而不是崩溃
- 权限检查收集所有失败而不是在第一个错误时中止
## Logging
- 全局日志设置在 `app/utils/logger.py` 中的 `setup_logger()`
- 日志格式：`'%(asctime)s - %(name)s - %(levelname)s - %(message)s'`
- 文件日志使用 `RotatingFileHandler`，最大 10MB，保留 5 个备份
- 日志目录：`logs/`
- 默认级别：`INFO`（可通过 `LOG_LEVEL` 环境变量配置）
- 特定模块覆盖：
- 使用 `caplog` fixture 捕获日志输出
- 使用 `caplog.at_level()` 设置临时日志级别
## Comments
- 复杂业务逻辑的解释
- 重要决策和权衡的说明
- 安全相关的注释
- 兼容性和迁移说明
- 每个模块以描述其用途的 docstring 开头
- 使用三重双引号 `"""` - `"""Database Connection Utility - PostgreSQL Only"""`
- 公共函数使用 Google 风格的 docstring
- 包含 Args、Returns 和 Raises 部分
- 示例：
- 中英文混合，中文用于业务逻辑说明
- 英文用于技术实现细节
- 使用 `#` 进行单行注释
## Function Design
- 没有强制的大小限制
- 倾向于保持函数简短和专注
- 复杂逻辑拆分为多个辅助函数
- 使用类型注解提高可读性
- 默认参数用于可选配置
- 关键参数使用关键字参数形式
- 成功时返回预期类型
- 失败时返回 `None` 或空容器
- API 路由返回 `(response, status_code)` 元组
- 错误情况返回标准化错误响应
## Module Design
- 使用 `__all__` 显式导出公共 API（在需要的地方）
- 大多数模块通过直接导入使用
- `app/routes/__init__.py` 注册所有蓝图
- `app/__init__.py` 作为应用工厂入口点
- `app/utils/db.py` 重新导出 PostgreSQL 特定函数
- 业务逻辑在 `app/services/` 中
- 服务类封装相关功能
- 单例模式用于全局服务（如 `TradingExecutor`）
- 数据源在 `app/data_sources/` 中
- 使用抽象基类定义接口
- 工厂模式创建数据源实例
## Configuration
- 所有配置通过环境变量读取
- 在 `app/config/settings.py` 中定义配置类
- 使用元类模式延迟加载配置
- 提供合理的默认值
- 关键配置有后备值
- 启动时验证配置有效性
## API Design
- 使用 Flask 蓝图组织路由
- URL 前缀按功能分组 - `/api/auth`, `/api/users`, `/api/agent/v1`
- HTTP 方法语义：GET（读取）、POST（创建）、PUT（更新）、DELETE（删除）
- Legacy API：`{"code": 1/0, "msg": "...", "data": {...}}`
- Agent Gateway API (v1)：`{"code": 0, "message": "ok", "data": {...}}`
- 错误响应包含详细信息：`{"code": int, "message": str, "details": any, "retriable": bool}`
- JWT Token 认证
- Bearer Token 格式：`Authorization: Bearer <token>`
- 装饰器保护端点：`@login_required`, `@admin_required`
## Database Conventions
- 表名前缀：`qd_`（QuantDinger）- `qd_users`, `qd_strategies_trading`, `qd_agent_tokens`
- 列名：snake_case - `user_id`, `created_at`, `token_version`
- 主键：`id SERIAL PRIMARY KEY`
- 外键：`<table>_id INTEGER REFERENCES <table>(id)`
- SQL 迁移文件在 `migrations/` 目录
- 使用 `CREATE TABLE IF NOT EXISTS` 确保幂等性
- 版本化迁移文件：`v3_1_0_agent_gateway.sql`
- 为常用查询创建索引
- 索引命名：`idx_<table>_<column>` - `idx_users_referred_by`
- 唯一索引：`idx_<table>_<column>_unique`
- 使用参数化查询防止 SQL 注入
- 使用上下文管理器管理连接
- 始终提交或回滚事务
## Concurrency
- 后台工作线程用于长时间运行的任务
- 使用 `threading.Lock` 保护共享状态
- 避免在 Flask 重载器中启动两次线程
- `ib_insync` 使用 asyncio
- 在启动时调用 `ib_insync.util.patchAsyncio()`
## Security
- 从不记录敏感信息（密码、token 值）
- 使用环境变量存储密钥
- `.env.example` 提供模板（不包含实际值）
- Token 版本控制实现单客户端登录
- Token 过期时间：7 天
- 使用 HS256 算法
- 使用 bcrypt 进行密码哈希
- 从不存储明文密码
## Testing Conventions
- 使用 `pytest` 框架
- 测试文件以 `test_` 开头
- 测试函数以 `test_` 开头
- 使用描述性测试名称
- 共享 fixtures 在 `conftest.py` 中
- 使用 `@pytest.fixture` 装饰器
- 支持 `autouse=True` 用于自动应用
- 使用 `monkeypatch` 修改环境变量和函数
- 使用 `unittest.mock` 进行复杂模拟
- 创建轻量级内存替代品以避免依赖
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

## Pattern Overview
- Flask-based REST API with service layer separation
- Strategy-driven trading architecture (IndicatorStrategy + ScriptStrategy)
- Multi-broker execution with unified pending order queue
- Agent Gateway for AI integration (versioned API surface)
- Postgres-backed state with Redis caching layer
- Background workers for async operations (orders, portfolio monitoring, USDT payments)
## Layers
- Purpose: HTTP endpoint definitions, request/response handling, authentication
- Location: `backend_api_python/app/routes/`
- Contains: 27 route modules (strategy, backtest, auth, billing, broker-specific, agent_v1)
- Depends on: Service layer for business logic
- Used by: Vue frontend (GHCR), mobile app, MCP server, external agents
- Purpose: Core business logic, trading execution, AI analysis, billing
- Location: `backend_api_python/app/services/`
- Contains: 45+ service modules (backtest, trading_executor, llm, billing_service, etc.)
- Depends on: Data sources, database, external APIs (exchanges, LLMs)
- Used by: Route layer, background workers
- Purpose: Market data abstraction with caching, rate limiting, circuit breaking
- Location: `backend_api_python/app/data_providers/`
- Contains: Crypto, forex, stocks, futures, sentiment, news, opportunities
- Depends on: External APIs (yfinance, CoinGecko, etc.), Redis cache
- Used by: Service layer, route layer
- Purpose: K-line data fetching with resilience patterns
- Location: `backend_api_python/app/data_sources/`
- Contains: Factory pattern, cache manager, circuit breaker, rate limiter
- Depends on: CCXT, yfinance, AkShare, IBKR, MT5, Alpaca
- Used by: Backtest service, trading executor, strategy runtime
- Purpose: Direct broker exchange execution (separate from data sources)
- Location: `backend_api_python/app/services/live_trading/`
- Contains: Per-exchange REST clients (Binance, OKX, Bybit, Bitget, etc.)
- Depends on: Exchange REST APIs
- Used by: PendingOrderWorker
- Purpose: Cross-cutting concerns (auth, DB, logging, config)
- Location: `backend_api_python/app/utils/`
- Contains: Authentication, database connections, logging, safe code execution
- Depends on: Flask, Postgres, Redis
- Used by: All layers
## Data Flow
- **Database:** PostgreSQL as single source of truth (users, strategies, trades, positions, orders)
- **Cache:** Redis for session data, price caching, single-flight request coalescing
- **In-Memory:** Strategy runtime state, signal deduplication, price cache (fallback)
## Key Abstractions
- Purpose: DataFrame-based signal generation (buy/sell columns)
- Examples: `docs/examples/dual_ma_with_params.py`
- Pattern: User code receives pandas DataFrame, adds boolean signal columns
- Runtime: Compiled and executed in sandboxed environment
- Purpose: Event-driven execution with explicit order control
- Examples: User code with `on_init(ctx)`, `on_bar(ctx, bar)` handlers
- Pattern: Direct context methods (`ctx.buy()`, `ctx.sell()`, `ctx.close_position()`)
- Runtime: Handlers compiled and called per bar by strategy thread
- Purpose: Market type → data source resolution
- Pattern: `get_kline(symbol, exchange, timeframe, limit)`
- Supported: Crypto (CCXT), Stocks (yfinance, Finnhub, Tiingo), Forex (OANDA), Futures
- Purpose: Decouple signal generation from execution (queue pattern)
- Pattern: Producer-consumer with polling loop
- Benefits: Rate limiting, retry logic, unified audit trail, multi-broker support
- Purpose: Versioned, scoped API surface for AI agents
- Pattern: Token-based auth with capability classes (R/W/B/N/C/T)
- Location: `backend_api_python/app/routes/agent_v1/`
- Security: Every call audited, scopes enforced, paper-only by default
## Entry Points
- Location: `backend_api_python/run.py`
- Triggers: `docker compose up`, `gunicorn`, direct Python execution
- Responsibilities: Flask app initialization, worker startup, strategy restoration
- Location: `mcp_server/src/quantdinger_mcp/server.py`
- Triggers: `uvx quantdinger-mcp`, stdio from Cursor/Claude Code
- Responsibilities: Thin wrapper around Agent Gateway, tool registration
- Location: `backend_api_python/migrations/init.sql`
- Triggers: Postgres container first start
- Responsibilities: Schema initialization, admin user creation
## Error Handling
- Exchange connection errors → strategy paused, notification sent
- Invalid strategy code → compile-time validation with hints
- Rate limit hits → circuit breaker opens, cached data served
- Database errors → connection pool retry, logged to fallback
- Framework: Custom `get_logger()` wrapper around Python logging
- Levels: DEBUG, INFO, WARNING, ERROR (configurable via LOG_LEVEL)
- Route level: Request schema validation
- Service level: Business logic validation
- Strategy level: Code safety checks, AST validation
- Web: `Authorization: Bearer <jwt>` header
- Agent: `Authorization: Bearer <agent_token>` header
- OAuth: Google, GitHub (optional, via `app/services/oauth_service.py`)
- Agent tokens enforce tenant isolation via allowlists
- Broker sessions isolated per-user via `BrokerSessionRegistry`
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

| Skill | Description | Path |
|-------|-------------|------|
| quantdinger-agent-workflow | >- QuantDinger repo workflow for coding agents: layered contracts, safety boundaries, and where backend, strategies, and Docker live. Use when editing Python API, strategies, deployment, or docs/agent. | `.cursor/skills/quantdinger-agent-workflow/SKILL.md` |
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
