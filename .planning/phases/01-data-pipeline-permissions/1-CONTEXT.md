# Phase 1: 数据管道与权限 - Context

**Gathered:** 2026-05-19
**Status:** Ready for planning

<domain>
## Phase Boundary

管理员可以上传 Excel 数据文件（.xlsx）并自动入库，系统按日期和标的记录时序，非管理员无法访问。这是整个市场概览模块的基础——没有数据，后续 Dashboard 和筛选无从谈起。

</domain>

<decisions>
## Implementation Decisions

### 数据库设计
- **D-01:** 新建 `market_overview_data` 表存储时序数据，字段对应 Excel 25 列（体系 B）
- **D-02:** 新建 `market_overview_uploads` 表存储上传历史（文件名、日期、类型、行数、状态、admin_id、timestamp）
- **D-03:** `market_overview_data` 表以 (data_date, symbol) 为唯一索引，支持 UPSERT（重复覆盖更新）
- **D-04:** `data_type` 字段标识数据类型：`us_market`（美股市场）、`core`（核心数据集）、`betting_tool`（押注工具）

### Excel 解析
- **D-05:** 使用 openpyxl（非 pandas），按行读取，避免 NaN 类型问题（PRD 明确推荐）
- **D-06:** 从文件名自动提取日期和数据类型：正则匹配 `(\d{2})-(\d{2})-(\d{2})` 和括号内类型关键词
- **D-07:** 支持体系 B（中文列名，25 列），首期不兼容体系 A（英文编码）
- **D-08:** 解析时做空值兜底：趋势类字段 `None` → `无趋势`，数值类字段 `None` → `0`

### 上传交互
- **D-09:** 前端支持拖拽上传 + 点击上传，一次只上传一个文件
- **D-10:** 上传完成后显示导入摘要卡片（数据日期、数据类型、总行数、新增数、更新数）
- **D-11:** 上传失败时显示具体错误（行号 + 字段 + 原因），不笼统报错

### 文件存储
- **D-12:** 解析后保存原始文件到 `uploads/market_overview/` 目录，以 `{date}_{type}_{timestamp}.xlsx` 命名
- **D-13:** 保留文件用于审计和数据恢复，不自动清理

### 权限控制
- **D-14:** 后端使用现有 `@admin_required` 装饰器保护所有 API
- **D-15:** 前端路由 meta 添加 `permission: ['admin']`，非 admin 用户看不到 tab
- **D-16:** 新 tab 位于 AI 资产分析之上，图标用 `stock` 或 `fund`

### API 设计
- **D-17:** `POST /api/market-overview/upload` — 上传 Excel 文件（multipart/form-data）
- **D-18:** `GET /api/market-overview/uploads` — 获取上传历史列表
- **D-19:** `GET /api/market-overview/dates` — 获取可用日期列表（用于 Dashboard 日期切换）

### Claude's Discretion
- 数据库表的具体列定义和类型选择
- Excel 解析的错误处理细节（异常捕获粒度）
- 上传组件的 UI 样式和进度条实现
- 文件大小限制和超时设置

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### 数据字段定义与解析规则
- `gversion/prds/multi-level-trend-screener.md` — 体系 B 字段定义（25列中文编码）、空值处理、openpyxl 使用建议
- `gversion/prds/leverage-state-screener.md` — 杠杆状态数据字段（模糊匹配列名、排序规则）

### 现有系统架构
- `.planning/codebase/ARCHITECTURE.md` — Flask 分层架构、数据流、认证模式
- `.planning/codebase/STRUCTURE.md` — 目录结构、命名约定、路由注册方式
- `.planning/codebase/CONVENTIONS.md` — Python 编码风格、API 设计模式、数据库约定

### 数据样本
- `/Users/gankin/Downloads/26-05-18 数据总表（趋势识别＋相对比价＋资金监控）（美股市场）.xlsx` — 美股市场样本（1000行×25列）
- `/Users/gankin/Downloads/26-05-14 数据总表（趋势识别＋相对比价＋资金监控）（核心数据集）.xlsx` — 核心数据集样本（235行×25列）

### 前端代码参考
- `gversion/QuantDinger-Vue/src/config/router.config.js` — 路由配置方式（permission meta、icon、keepAlive）
- `gversion/QuantDinger-Vue/src/views/ai-asset-analysis/index.vue` — 现有 tab 页面参考

### 后端代码参考
- `backend_api_python/app/utils/auth.py` — `@admin_required` 装饰器实现
- `backend_api_python/app/routes/fast_analysis.py` — 现有路由模式参考
- `backend_api_python/migrations/init.sql` — 数据库表结构参考

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `@admin_required` 装饰器: 直接用于保护所有市场概览 API 端点
- `@login_required` 装饰器: 获取 user_id 和 role 信息
- `get_logger()`: 统一日志记录
- `get_db_connection()`: 数据库连接池管理

### Established Patterns
- Flask Blueprint 注册: `app/routes/__init__.py` 中统一注册新 Blueprint
- API 响应格式: `{'code': 1, 'msg': 'success', 'data': {...}}`
- 前端路由 permission 机制: `meta.permission` 数组控制可见性
- Vue 组件懒加载: `() => import('@/views/xxx')`

### Integration Points
- 后端: `backend_api_python/app/routes/__init__.py` — 注册新 Blueprint `market_overview_bp`
- 前端: `gversion/QuantDinger-Vue/src/config/router.config.js` — 在 AI 资产分析之前插入新路由
- 前端: `gversion/QuantDinger-Vue/src/api/` — 新增 `marketOverview.js` API 层
- 数据库: `backend_api_python/migrations/init.sql` 或独立的 migration 脚本

</code_context>

<deferred>
## Deferred Ideas

- 批量上传多个文件 — 首期仅支持单文件上传
- 上传进度实时显示（WebSocket） — 首期使用简单进度条
- Excel 模板下载功能 — 后续阶段考虑
- 数据自动校验和修复 — 后续阶段考虑

</deferred>

---

*Phase: 01-data-pipeline-permissions*
*Context gathered: 2026-05-19*
