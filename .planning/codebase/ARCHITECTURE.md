# Architecture

**Analysis Date:** 2025-01-19

## Pattern Overview

**Overall:** Monolithic backend with microservice-like internal organization, deployed as a Docker Compose stack

**Key Characteristics:**
- Flask-based REST API with service layer separation
- Strategy-driven trading architecture (IndicatorStrategy + ScriptStrategy)
- Multi-broker execution with unified pending order queue
- Agent Gateway for AI integration (versioned API surface)
- Postgres-backed state with Redis caching layer
- Background workers for async operations (orders, portfolio monitoring, USDT payments)

## Layers

**Presentation Layer (Routes):**
- Purpose: HTTP endpoint definitions, request/response handling, authentication
- Location: `backend_api_python/app/routes/`
- Contains: 27 route modules (strategy, backtest, auth, billing, broker-specific, agent_v1)
- Depends on: Service layer for business logic
- Used by: Vue frontend (GHCR), mobile app, MCP server, external agents

**Service Layer:**
- Purpose: Core business logic, trading execution, AI analysis, billing
- Location: `backend_api_python/app/services/`
- Contains: 45+ service modules (backtest, trading_executor, llm, billing_service, etc.)
- Depends on: Data sources, database, external APIs (exchanges, LLMs)
- Used by: Route layer, background workers

**Data Provider Layer:**
- Purpose: Market data abstraction with caching, rate limiting, circuit breaking
- Location: `backend_api_python/app/data_providers/`
- Contains: Crypto, forex, stocks, futures, sentiment, news, opportunities
- Depends on: External APIs (yfinance, CoinGecko, etc.), Redis cache
- Used by: Service layer, route layer

**Data Source Layer:**
- Purpose: K-line data fetching with resilience patterns
- Location: `backend_api_python/app/data_sources/`
- Contains: Factory pattern, cache manager, circuit breaker, rate limiter
- Depends on: CCXT, yfinance, AkShare, IBKR, MT5, Alpaca
- Used by: Backtest service, trading executor, strategy runtime

**Integration Layer:**
- Purpose: Direct broker exchange execution (separate from data sources)
- Location: `backend_api_python/app/services/live_trading/`
- Contains: Per-exchange REST clients (Binance, OKX, Bybit, Bitget, etc.)
- Depends on: Exchange REST APIs
- Used by: PendingOrderWorker

**Utility Layer:**
- Purpose: Cross-cutting concerns (auth, DB, logging, config)
- Location: `backend_api_python/app/utils/`
- Contains: Authentication, database connections, logging, safe code execution
- Depends on: Flask, Postgres, Redis
- Used by: All layers

## Data Flow

**Market Data Flow:**

1. Client requests K-line data via API (`/api/indicator/klines`)
2. Route handler forwards to KlineService
3. DataSourceFactory resolves appropriate data source based on market type
4. Data source applies rate limiting, caching, circuit breaker
5. Raw data fetched from CCXT/yfinance/AkShare/etc.
6. Data cached in Redis (if enabled) or in-memory cache
7. Formatted response returned to client

**Strategy Development Flow:**

1. User writes indicator/strategy code in Python (IndicatorStrategy or ScriptStrategy)
2. Strategy compiler validates syntax and extracts parameters
3. Backtest service runs historical simulation using cached K-line data
4. Results stored in database with performance metrics
5. AI hints generated from backtest results (optional)

**Live Trading Flow:**

1. Strategy started via API → TradingExecutor spawns thread
2. Strategy thread pulls K-line data periodically
3. Indicator calculations generate buy/sell signals
4. Signals written to `pending_orders` table (NOT direct to exchange)
5. PendingOrderWorker polls table and dispatches orders based on execution_mode:
   - signal: notifications only (Telegram, email, webhook)
   - live: actual exchange execution via live_trading clients
6. Fills recorded to `strategy_trades` and `strategy_positions`

**AI Agent Flow (via MCP):**

1. AI agent (Cursor, Claude Code) calls MCP server tools
2. MCP server forwards to Agent Gateway (`/api/agent/v1/*`)
3. Agent token validated with scopes/allowlists
4. Request audited to `qd_agent_audit` table
5. Business logic delegated to core services
6. Response returned (trading NOT exposed via MCP for safety)

**State Management:**

- **Database:** PostgreSQL as single source of truth (users, strategies, trades, positions, orders)
- **Cache:** Redis for session data, price caching, single-flight request coalescing
- **In-Memory:** Strategy runtime state, signal deduplication, price cache (fallback)

## Key Abstractions

**IndicatorStrategy:**
- Purpose: DataFrame-based signal generation (buy/sell columns)
- Examples: `docs/examples/dual_ma_with_params.py`
- Pattern: User code receives pandas DataFrame, adds boolean signal columns
- Runtime: Compiled and executed in sandboxed environment

**ScriptStrategy:**
- Purpose: Event-driven execution with explicit order control
- Examples: User code with `on_init(ctx)`, `on_bar(ctx, bar)` handlers
- Pattern: Direct context methods (`ctx.buy()`, `ctx.sell()`, `ctx.close_position()`)
- Runtime: Handlers compiled and called per bar by strategy thread

**DataSourceFactory:**
- Purpose: Market type → data source resolution
- Pattern: `get_kline(symbol, exchange, timeframe, limit)`
- Supported: Crypto (CCXT), Stocks (yfinance, Finnhub, Tiingo), Forex (OANDA), Futures

**PendingOrderWorker:**
- Purpose: Decouple signal generation from execution (queue pattern)
- Pattern: Producer-consumer with polling loop
- Benefits: Rate limiting, retry logic, unified audit trail, multi-broker support

**Agent Gateway:**
- Purpose: Versioned, scoped API surface for AI agents
- Pattern: Token-based auth with capability classes (R/W/B/N/C/T)
- Location: `backend_api_python/app/routes/agent_v1/`
- Security: Every call audited, scopes enforced, paper-only by default

## Entry Points

**Backend API:**
- Location: `backend_api_python/run.py`
- Triggers: `docker compose up`, `gunicorn`, direct Python execution
- Responsibilities: Flask app initialization, worker startup, strategy restoration

**MCP Server:**
- Location: `mcp_server/src/quantdinger_mcp/server.py`
- Triggers: `uvx quantdinger-mcp`, stdio from Cursor/Claude Code
- Responsibilities: Thin wrapper around Agent Gateway, tool registration

**Migration Scripts:**
- Location: `backend_api_python/migrations/init.sql`
- Triggers: Postgres container first start
- Responsibilities: Schema initialization, admin user creation

## Error Handling

**Strategy:** Graceful degradation with auto-stop on fatal errors

**Patterns:**
- Exchange connection errors → strategy paused, notification sent
- Invalid strategy code → compile-time validation with hints
- Rate limit hits → circuit breaker opens, cached data served
- Database errors → connection pool retry, logged to fallback

**Cross-Cutting Concerns:**

**Logging:** Structured logging to `logs/` directory with rotation
- Framework: Custom `get_logger()` wrapper around Python logging
- Levels: DEBUG, INFO, WARNING, ERROR (configurable via LOG_LEVEL)

**Validation:** Multi-layer approach
- Route level: Request schema validation
- Service level: Business logic validation
- Strategy level: Code safety checks, AST validation

**Authentication:** JWT tokens for web UI, agent tokens for AI integration
- Web: `Authorization: Bearer <jwt>` header
- Agent: `Authorization: Bearer <agent_token>` header
- OAuth: Google, GitHub (optional, via `app/services/oauth_service.py`)

**Multi-tenancy:** All queries scoped to `user_id`
- Agent tokens enforce tenant isolation via allowlists
- Broker sessions isolated per-user via `BrokerSessionRegistry`

---

*Architecture analysis: 2025-01-19*
