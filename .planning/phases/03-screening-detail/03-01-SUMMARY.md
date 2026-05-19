---
commit: ef071d6
files_modified:
  - backend_api_python/app/services/market_overview_service.py
  - backend_api_python/app/routes/market_overview.py
---

# Plan 03-01 Summary: 筛选列表后端 API

## What was done

- **`get_symbols()`** — 多维筛选（search ILIKE, trend映射, relative_price, leverage）、白名单排序、分页查询，返回 items/total/page/page_size/data_date
- **`get_symbol_timeline()`** — 按日期范围查询单标的时序数据，返回 symbol/name/timeline/date_range
- **两个新路由端点**：`GET /symbols` 和 `GET /symbols/<symbol>/timeline`，均有 @admin_required 保护
- page_size 限制 1~200，page 最小为 1

## Key decisions

- 排序字段白名单 `SORT_COLUMNS` 防止 SQL 注入
- 趋势维度映射 `TREND_LEVEL_COLUMNS` (daily/weekly/monthly → 对应列名)
- HOLDINGS 集合在 Python 侧标记 `is_holding` 字段
- 不存在的 symbol timeline 返回 404
