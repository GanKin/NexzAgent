# Summary: Plan 01-01 — 数据库建表与后端服务层

**Status:** Completed
**Commit:** 52d0f65

## What was built

### 数据库迁移脚本
- `backend_api_python/migrations/market_overview.sql` — 两张表的 CREATE TABLE 脚本
  - `market_overview_data` — 25 列时序数据表，(data_date, symbol) 唯一索引支持 UPSERT
  - `market_overview_uploads` — 上传历史表，记录文件名、状态、行数统计
- 迁移脚本已追加到 `init.sql`

### MarketOverviewService
- `backend_api_python/app/services/market_overview_service.py`
- `import_data()` — 批量 UPSERT，使用 xmax 区分新增/更新
- `get_uploads()` — 上传历史列表
- `get_available_dates()` — 可用日期列表
- `get_date_stats()` — 日期统计摘要
- `parse_filename()` — 从文件名提取日期和数据类型

## Decisions made during execution
- 使用 xmax 系统列追踪 INSERT vs UPDATE，避免额外 SELECT 查询
- 解析器放在独立文件（market_overview_parser.py），Service 层只处理数据库操作
- 所有数据库操作用 try/except 包裹，失败时自动更新 upload 状态

## Files created/modified
- `backend_api_python/migrations/market_overview.sql` (new)
- `backend_api_python/migrations/init.sql` (appended)
- `backend_api_python/app/services/market_overview_service.py` (new)

## Verification
- [x] SQL 语法有效（PostgreSQL CREATE TABLE IF NOT EXISTS）
- [x] Python 语法有效（ast.parse 通过）
- [x] UPSERT SQL 包含 ON CONFLICT (data_date, symbol) DO UPDATE
- [x] 唯一索引 idx_market_overview_data_date_symbol_unique 已创建
