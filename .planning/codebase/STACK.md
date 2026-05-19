# Technology Stack

**Analysis Date:** 2026-05-19

## Languages

**Primary:**
- Python 3.12 (Docker) / Python 3.10+ (本地部署) - 后端 API 和策略执行引擎
- JavaScript/TypeScript - 前端 Vue 应用 (独立仓库 QuantDinger-Vue)

**Secondary:**
- SQL - PostgreSQL 数据库模式和初始化脚本
- Shell - Docker 入口脚本和部署脚本
- YAML - Docker Compose 和 GitHub Actions 配置

## Runtime

**Environment:**
- Python 3.12-slim-bookworm (Docker 基础镜像)
- 可选构建区域: cn (阿里云镜像) / global (官方源)

**Package Manager:**
- pip (Python)
- Lockfile: 存在于 `backend_api_python/requirements.txt`

**Process Management:**
- Gunicorn 22.0+ (生产 WSGI 服务器)
- worker_class: gthread (单 worker 多线程)
- 默认配置: 1 worker, 4-8 threads

## Frameworks

**Core Backend:**
- Flask 3.1.3 - Web 框架和 API 网关
- Flask-CORS 6.0.0 - 跨域资源共享

**前端 (独立仓库):**
- Vue.js - SPA 前端框架
- Ant Design Vue - UI 组件库
- KLineCharts - K 线图表组件
- ECharts - 数据可视化
- Nginx - 前端静态文件服务

**数据科学:**
- pandas 1.5.0+ - 数据处理和分析
- numpy (隐式依赖) - 数值计算

**交易和金融数据:**
- CCXT 4.0.0+ - 加密货币交易所集成 (100+ 交易所)
- yfinance 0.2.18+ - Yahoo Finance 数据
- finnhub-python 2.4.18+ - Finnhub API 集成
- akshare 1.12.0+ - 中国金融数据

**经纪商集成:**
- ib_insync 0.9.86+ - Interactive Brokers (IBKR) 集成
- alpaca-py 0.30.0+ - Alpaca 美股和加密货币集成
- MetaTrader5 5.0.45+ (可选) - MT5 外汇集成 (仅 Windows)

## Key Dependencies

**数据库:**
- psycopg2-binary 2.9.9+ - PostgreSQL 驱动
- redis 5.0.0+ - Redis 缓存客户端

**认证和安全:**
- PyJWT 2.12.0+ - JWT 令牌处理
- bcrypt 4.1.0+ - 密码哈希
- cryptography 43.0.0+ - 加密工具
- bip-utils 2.9.0+ - HD 钱包地址派生 (USDT 支付)

**网络和代理:**
- requests 2.32.0+ - HTTP 客户端
- certifi 2024.2.2+ - SSL 证书
- PySocks 1.7.1+ - SOCKS 代理支持

**配置:**
- python-dotenv 1.0.1+ - 环境变量管理

## Configuration

**Environment:**
- 主配置文件: `backend_api_python/.env`
- Docker Compose 覆盖: 项目根目录 `.env` (可选)
- 配置加载: `run.py` 自动加载 `.env` 文件

**关键配置区域:**
- 品牌和标识: `BRAND_*` 系列变量
- 认证: `SECRET_KEY`, `ADMIN_USER`, `ADMIN_PASSWORD`
- 数据库: `DATABASE_URL` (PostgreSQL 连接字符串)
- AI/LLM: `LLM_PROVIDER`, `*_API_KEY`, `*_MODEL`
- OAuth: `GOOGLE_CLIENT_ID`, `GITHUB_CLIENT_ID`
- 支付: `USDT_PAY_ENABLED`, `*_ADDRESS`, `*_API_KEY`
- 代理: `PROXY_URL` (中国大陆访问 Binance/Coinbase 必需)

**Build:**
- Dockerfile: `backend_api_python/Dockerfile`
- 构建参数: `BASE_IMAGE`, `BUILD_REGION`
- 多架构支持: amd64/arm64

## Platform Requirements

**Development:**
- Docker + Docker Compose v2
- Git
- Python 3.10+ (本地开发)
- 端口: 8888 (前端), 5000 (API), 5432 (PostgreSQL), 6379 (Redis)

**Production:**
- Docker 部署 (推荐) 或 bare-metal Python
- PostgreSQL 16
- Redis 7 (可选但推荐)
- 反向代理 (Nginx/Caddy) 用于 HTTPS
- 最小磁盘: 几 GB (用于数据和日志增长)

**操作系统:**
- Linux (推荐生产环境)
- macOS (开发和测试)
- Windows (支持，但 MT5 集成仅限 Windows)

**云平台:**
- AWS Marketplace AMI (CentOS 9)
- Railway (支持)
- 任何支持 Docker 的云平台

---

*Stack analysis: 2026-05-19*
