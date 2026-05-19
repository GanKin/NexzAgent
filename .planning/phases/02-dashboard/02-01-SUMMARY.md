# Summary: Plan 02-01 — Dashboard 后端统计 API

**Status:** Completed
**Commit:** bad29ab

## What was built

### Service 层扩展
- `MarketOverviewService.get_dashboard_data(data_date)` — 单次调用返回全量 Dashboard 数据
- 聚合查询使用 `COUNT(*) FILTER (WHERE ...)` 一次获取趋势分布、资金面、比价统计
- 四分类汇总在 Python 端计算（主升浪/主升调整/新信号/规避区）
- 持仓快照查询 HOLDINGS 集合中的标的
- 变化对比：查找前一交易日，对比趋势升级/降级，统计 improved/worsened/new_symbols

### API 端点
- `GET /api/market-overview/dashboard?date={date}` — admin-only，返回 stats + holdings + changes_summary
- date 参数可选，默认取最新日期

## Decisions made during execution
- 使用单条聚合 SQL 获取全部统计，减少数据库往返
- 四分类用 Python 端逐行判断（条件复杂，SQL 不够直观）
- 持仓 HOLDINGS 使用 frozenset 类常量
- 变化对比基于日趋势排序（上行>静默>下行）

## Files modified
- `backend_api_python/app/services/market_overview_service.py` (extended)
- `backend_api_python/app/routes/market_overview.py` (extended)
