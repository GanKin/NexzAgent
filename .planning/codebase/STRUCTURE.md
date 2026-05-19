# Codebase Structure

**Analysis Date:** 2025-01-19

## Directory Layout

```
/Users/gankin/Documents/NexzAgent/
├── .planning/               # Generated codebase maps (this file)
├── .github/                 # GitHub workflows, issue templates
├── docs/                    # Product docs, strategy guides, examples
│   ├── agent/              # AI integration docs
│   ├── examples/           # Python strategy examples
│   └── screenshots/        # UI screenshots
├── scripts/                # Utility scripts (secret key generation, i18n)
├── backend_api_python/     # Main backend application
│   ├── app/               # Application source
│   ├── migrations/        # Database schema
│   ├── tests/             # Backend tests
│   ├── Dockerfile         # Backend container build
│   ├── run.py             # Application entry point
│   ├── gunicorn_config.py # Production WSGI config
│   └── env.example        # Environment template
├── mcp_server/             # Model Context Protocol server
│   ├── src/quantdinger_mcp/  # MCP implementation
│   ├── tests/             # MCP server tests
│   └── pyproject.toml     # Python package config
├── docker-compose.yml      # Local deployment stack
└── README.md              # Main documentation
```

## Directory Purposes

**`backend_api_python/`**:
- Purpose: Flask REST API, strategy engine, trading execution, AI services
- Contains: Routes, services, data providers, database migrations
- Key files: `run.py` (entry point), `app/__init__.py` (app factory), `env.example` (config)

**`backend_api_python/app/`**:
- Purpose: Application source code
- Contains: Routes (27 modules), Services (45+ modules), Data providers, Utils, Config

**`backend_api_python/app/routes/`**:
- Purpose: HTTP endpoint definitions
- Contains: Strategy, backtest, auth, billing, broker-specific routes, Agent Gateway v1
- Key files: `__init__.py` (route registration), `agent_v1/` (AI integration)

**`backend_api_python/app/services/`**:
- Purpose: Business logic layer
- Contains: BacktestService, TradingExecutor, LLMService, BillingService, etc.
- Subdirs: `live_trading/` (broker execution), `experiment/` (optimization), `usdt_payment/`

**`backend_api_python/app/data_providers/`**:
- Purpose: Market data abstraction (global markets, news, sentiment)
- Contains: Crypto, forex, stocks, futures, heatmap, news, opportunities
- Pattern: Cached data fetchers with single-flight coalescing

**`backend_api_python/app/data_sources/`**:
- Purpose: K-line data fetching with resilience
- Contains: Factory, cache manager, circuit breaker, rate limiter
- Pattern: Provider-specific implementations (CCXT, yfinance, AkShare)

**`backend_api_python/app/utils/`**:
- Purpose: Cross-cutting utilities
- Contains: Auth, database, logging, safe execution, config loading
- Key files: `db_postgres.py` (connection pool), `safe_exec.py` (code sandbox)

**`mcp_server/`**:
- Purpose: Model Context Protocol server for AI integration
- Contains: FastMCP-based tools wrapping Agent Gateway
- Published to PyPI as `quantdinger-mcp`

**`docs/`**:
- Purpose: Documentation and examples
- Contains: Strategy guides, deployment docs, AI integration design
- Key files: `examples/*.py` (strategy templates)

## Key File Locations

**Entry Points:**
- `backend_api_python/run.py`: Flask application entry point (development/debug)
- `backend_api_python/gunicorn_config.py`: Production WSGI config
- `mcp_server/src/quantdinger_mcp/server.py`: MCP server entry point

**Configuration:**
- `backend_api_python/env.example`: Environment variable template (copy to `.env`)
- `backend_api_python/app/config/settings.py`: Config class with metaclass
- `backend_api_python/migrations/init.sql`: Database schema (55KB, auto-applied)

**Core Logic:**
- `backend_api_python/app/services/backtest.py`: Backtest engine (5,149 lines)
- `backend_api_python/app/services/trading_executor.py`: Live strategy runner (4,260 lines)
- `backend_api_python/app/services/strategy.py`: Strategy CRUD (1,474 lines)
- `backend_api_python/app/services/pending_order_worker.py`: Order dispatcher (2,735 lines)

**Testing:**
- `backend_api_python/tests/`: Backend test files
- `mcp_server/tests/`: MCP server tests

## Naming Conventions

**Files:**
- Routes: `{feature}.py` (e.g., `strategy.py`, `backtest.py`, `auth.py`)
- Services: `{feature}.py` or `{feature}_service.py` (e.g., `llm.py`, `billing_service.py`)
- Data providers: `{market}.py` (e.g., `crypto.py`, `forex.py`)
- Utils: `{concern}.py` (e.g., `auth.py`, `db.py`, `logger.py`)

**Directories:**
- `routes/`: HTTP endpoint modules
- `services/`: Business logic modules
- `data_providers/`: Market data fetchers
- `data_sources/`: K-line data sources
- `utils/`: Utility modules
- `config/`: Configuration modules

**Classes:**
- Services: `{Feature}Service` (e.g., `BacktestService`, `LLMService`, `BillingService`)
- Exceptions: `{Error}Error` (e.g., `DataSourceError`, `LiveTradingError`)

**Functions:**
- Route handlers: `{verb}_{resource}` (e.g., `get_strategies()`, `submit_backtest()`)
- Service methods: `{action}_{entity}` (e.g., `get_user_credits()`, `place_order()`)

## Where to Add New Code

**New API Endpoint:**
- Primary code: `backend_api_python/app/routes/{feature}.py`
- Service logic: `backend_api_python/app/services/{feature}_service.py`
- Register: Add blueprint to `backend_api_python/app/routes/__init__.py`

**New Strategy Type:**
- Implementation: `backend_api_python/app/services/strategy.py`
- Runtime: `backend_api_python/app/services/strategy_script_runtime.py`
- Compiler: `backend_api_python/app/services/strategy_compiler.py`

**New Data Source:**
- Implementation: `backend_api_python/app/data_sources/{market}.py`
- Register: Add to `backend_api_python/app/data_sources/factory.py`

**New Market Data Provider:**
- Implementation: `backend_api_python/app/data_providers/{market}.py`
- Register: Import in `backend_api_python/app/data_providers/__init__.py`

**New Broker Integration:**
- Execution client: `backend_api_python/app/services/live_trading/{broker}.py`
- Routes: `backend_api_python/app/routes/{broker}.py`
- Factory: Register in `backend_api_python/app/services/live_trading/factory.py`

**Utilities:**
- Shared helpers: `backend_api_python/app/utils/{concern}.py`

**Tests:**
- Backend tests: `backend_api_python/tests/test_{feature}.py`
- MCP tests: `mcp_server/tests/test_{feature}.py`

## Special Directories

**`backend_api_python/migrations/`**:
- Purpose: Database schema definitions
- Contains: `init.sql` (main schema), `v3_1_0_agent_gateway.sql` (agent tokens)
- Generated: No (hand-written SQL)
- Committed: Yes

**`backend_api_python/app/data/`**:
- Purpose: Runtime data and seed data
- Contains: `market_symbols_seed.py`
- Generated: Partially (some seed data auto-generated)
- Committed: Yes

**`docs/examples/`**:
- Purpose: Strategy development examples and templates
- Contains: `dual_ma_with_params.py`, `multi_indicator_composite.py`, etc.
- Generated: No
- Committed: Yes

**`scripts/`**:
- Purpose: Development and deployment utilities
- Contains: `generate-secret-key.sh`, i18n helpers
- Generated: No
- Committed: Yes

**`backend_api_python/app/services/experiment/`**:
- Purpose: Strategy optimization and regime detection
- Contains: `runner.py`, `scoring.py`, `regime.py`, `evolution.py`
- Generated: No
- Committed: Yes

**`backend_api_python/app/services/live_trading/`**:
- Purpose: Direct broker execution (separate from CCXT data sources)
- Contains: Per-broker clients (binance.py, okx.py, bybit.py, etc.)
- Generated: No
- Committed: Yes

**`backend_api_python/app/services/usdt_payment/`**:
- Purpose: USDT payment processing (multi-chain)
- Contains: TronGrid watcher, payment service
- Generated: No
- Committed: Yes

---

*Structure analysis: 2025-01-19*
