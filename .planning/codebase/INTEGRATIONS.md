# External Integrations

**Analysis Date:** 2026-05-19

## APIs & External Services

**AI/LLM 提供商:**
- **OpenRouter** - 主要 LLM 提供商 (支持 GPT-4, Claude 等)
  - SDK/Client: 自定义 HTTP 客户端 (`app/services/llm.py`)
  - Auth: `OPENROUTER_API_KEY`
  - 配置: `OPENROUTER_MODEL`, `OPENROUTER_API_URL`

- **OpenAI** - 备用 LLM 提供商
  - Auth: `OPENAI_API_KEY`
  - 配置: `OPENAI_MODEL`, `OPENAI_BASE_URL`

- **Google Gemini** - Google LLM
  - Auth: `GOOGLE_API_KEY`
  - 配置: `GOOGLE_MODEL`

- **DeepSeek** - DeepSeek LLM
  - Auth: `DEEPSEEK_API_KEY`
  - 配置: `DEEPSEEK_MODEL`, `DEEPSEEK_BASE_URL`

- **Grok** - xAI Grok
  - Auth: `GROK_API_KEY`
  - 配置: `GROK_MODEL`, `GROK_BASE_URL`

- **MiniMax** - MiniMax LLM
  - Auth: `MINIMAX_API_KEY`
  - 配置: `MINIMAX_MODEL`, `MINIMAX_BASE_URL`

- **自定义 OpenAI 兼容 API** - 本地 Ollama 等
  - Auth: `CUSTOM_API_KEY` (可选)
  - 配置: `CUSTOM_API_URL`, `CUSTOM_MODEL`

**搜索服务:**
- **Google Search** - 新闻和资讯搜索
  - Auth: `SEARCH_GOOGLE_API_KEY`, `SEARCH_GOOGLE_CX`

- **Bing Search** - 备用搜索
  - Auth: `SEARCH_BING_API_KEY`

- **Tavily** - AI 优化搜索
  - Auth: `TAVILY_API_KEYS`

- **SerpAPI** - Google/Bing 搜索爬虫
  - Auth: `SERPAPI_KEYS`

**市场情绪和新闻:**
- **Adanos** - 美股情绪数据
  - Auth: `ADANOS_API_KEY`
  - 配置: `ADANOS_API_BASE_URL`, `ADANOS_SENTIMENT_SOURCE`

- **CoinGlass** - 加密货币衍生品数据
  - Auth: `COINGLASS_API_KEY`

- **CryptoQuant** - 链上数据
  - Auth: `CRYPTOQUANT_API_KEY`

## Data Storage

**数据库:**
- PostgreSQL 16
  - 连接: `DATABASE_URL` 环境变量
  - 客户端: psycopg2-binary
  - 连接池: ThreadedConnectionPool (可配置 `DB_POOL_MIN`, `DB_POOL_MAX`)
  - 模式: `migrations/init.sql` (自动应用)

**缓存:**
- Redis 7
  - 连接: `REDIS_HOST`, `REDIS_PORT`
  - 用途: 会话存储、数据缓存、分布式锁
  - 可选: `CACHE_ENABLED=true`

**文件存储:**
- 本地文件系统 (Docker volumes)
  - `backend_logs:/app/logs` - 日志文件
  - `backend_data:/app/data` - 运行时数据

**内存存储:**
- 进程内内存用于策略运行时状态
- `data/memory/` 目录用于持久化内存快照

## Authentication & Identity

**OAuth 提供商:**
- **Google OAuth**
  - 实现路径: `app/services/oauth_service.py`
  - Auth: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
  - 回调: `GOOGLE_REDIRECT_URI` (默认 `/api/auth/oauth/google/callback`)
  - 路由: `/api/auth/oauth/google`

- **GitHub OAuth**
  - 实现路径: `app/services/oauth_service.py`
  - Auth: `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`
  - 回调: `GITHUB_REDIRECT_URI`
  - 路由: `/api/auth/oauth/github`

**本地认证:**
- 用户名/密码 (bcrypt 哈希)
- JWT 令牌 (PyJWT)
- 邮箱验证码登录

**验证和安全:**
- **Cloudflare Turnstile** (可选)
  - Auth: `TURNSTILE_SITE_KEY`, `TURNSTILE_SECRET_KEY`

## Monitoring & Observability

**错误跟踪:**
- 内置日志记录 (`app/utils/logger.py`)
- Docker 日志: `docker-compose logs -f backend`

**日志:**
- 文件日志: `/app/logs/` 目录
- 控制台输出: Gunicorn access/error 日志
- 日志级别可配置: `GUNICORN_LOG_LEVEL`

**健康检查:**
- API 端点: `/api/health`
- Docker healthcheck: 所有服务配置

## CI/CD & Deployment

**托管:**
- Docker Hub (基础镜像)
- GHCR (前端镜像: `ghcr.io/brokermr810/quantdinger-frontend`)

**CI Pipeline:**
- GitHub Actions (`.github/workflows/`)
- 构建和推送 Docker 镜像
- 多架构支持 (amd64/arm64)

**部署方式:**
- Docker Compose (主要)
- AWS Marketplace AMI
- Railway (支持)
- 本地 Python 部署

## Environment Configuration

**必需环境变量:**
- `SECRET_KEY` - JWT 和加密密钥 (必须修改)
- `DATABASE_URL` - PostgreSQL 连接字符串
- `ADMIN_USER` / `ADMIN_PASSWORD` - 默认管理员凭据

**关键集成配置:**
- LLM: `LLM_PROVIDER` + 对应的 `*_API_KEY`
- OAuth: `GOOGLE_CLIENT_ID` / `GITHUB_CLIENT_ID`
- 支付: `USDT_PAY_ENABLED` + 链地址
- 代理: `PROXY_URL` (中国大陆必需)

**Secrets 位置:**
- `backend_api_python/.env` (运行时配置)
- Docker secrets (生产环境推荐)
- 环境变量注入

## Trading Platform Integrations

**加密货币交易所 (通过 CCXT):**
- **Binance** - Spot, Futures, Margin
  - 用途: 市场数据、订单执行
  - 配置: 用户 API 密钥存储在数据库中

- **OKX** - Spot, Perpetual, Options
  - 用途: 市场数据、订单执行

- **Bitget** - Spot, Futures, Copy Trading

- **Bybit** - Spot, Linear Futures

- **Coinbase** - Spot

- **Kraken** - Spot, Futures

- **KuCoin** - Spot, Futures

- **Gate.io** - Spot, Futures

- **Deepcoin** - 衍生品集成

- **HTX** - Spot, USDT 永续合约

**传统市场经纪商:**
- **Interactive Brokers (IBKR)**
  - 实现: `app/services/ibkr_trading/`
  - 依赖: ib_insync
  - 要求: 本地 TWS/IB Gateway
  - 路由: `/api/ibkr/*`
  - 用途: 美股交易、账户管理、订单执行

- **Alpaca**
  - 实现: `app/services/alpaca_trading/`
  - 依赖: alpaca-py
  - Auth: `ALPACA_API_KEY`, `ALPACA_SECRET_KEY`
  - 模式: 纸质交易 (`ALPACA_PAPER=true`) 或实盘
  - 路由: `/api/alpaca/*`
  - 用途: 美股/ETF/加密货币交易

- **MetaTrader 5 (MT5)**
  - 实现: `app/services/mt5_trading/`
  - 依赖: MetaTrader5 (仅 Windows)
  - 要求: 本地 MT5 终端
  - 路由: `/api/mt5/*`
  - 用途: 外汇交易

**市场数据提供商:**
- **Yahoo Finance** (yfinance) - 免费全球市场数据
- **Finnhub** - 美股实时数据
  - Auth: `FINNHUB_API_KEY`
- **Twelve Data** - 港股/中国 A 股 K 线
  - Auth: `TWELVE_DATA_API_KEY`
- **Tiingo** - 美股数据
  - Auth: `TIINGO_API_KEY`
- **AkShare** - 中国金融市场数据
- **Tencent 股票** - 港股/中概股数据

## Payment Systems

**USDT 加密货币支付:**
- 实现: `app/services/usdt_payment/`
- 支持链: TRC20, BEP20, ERC20, SOL
- 配置: 每个链的接收地址 (`USDT_*_ADDRESS`)
- 区块链集成:
  - TronGrid (TRC20)
  - BSC RPC (BEP20)
  - Etherscan V2 (ERC20)
  - Solana RPC (SOL)
- 金额后缀匹配机制: 每个订单有唯一的小数后缀

**积分系统:**
- 内置积分系统 (`qd_credits_log` 表)
- VIP 会员计划
- 配置: `BILLING_ENABLED`, `*_CREDITS_*`

## Webhooks & Callbacks

**传入 Webhooks:**
- 无通用传入 webhook 端点
- OAuth 回调: `/api/auth/oauth/*/callback`

**传出通知:**
- **Telegram** - 机器人通知
  - 配置: 用户在设置中配置 `telegram_chat_id`

- **Discord** - Webhook 通知
  - 配置: Discord webhook URL

- **Email** - SMTP 通知
  - 配置: `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD`

- **SMS** - Twilio 通知
  - 配置: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`

- **自定义 Webhook** - 通用 HTTP POST
  - 配置: 任意 webhook URL
  - 实现: `app/services/signal_notifier.py`

**Agent Gateway:**
- 端点: `/api/agent/v1/*`
- MCP 服务器: `quantdinger-mcp` PyPI 包
- 用途: AI 代理集成 (Cursor, Claude Code, Codex)
- Auth: Agent 令牌 (`qd_agent_*`)

---

*Integration audit: 2026-05-19*
