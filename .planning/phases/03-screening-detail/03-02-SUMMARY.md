---
commit: ae5ae8e
files_modified:
  - QuantDinger-Vue/src/views/market-overview/SymbolList.vue
  - QuantDinger-Vue/src/views/market-overview/index.vue
  - QuantDinger-Vue/src/api/marketOverview.js
---

# Plan 03-02 Summary: 前端代码列表 Tab

## What was done

- **SymbolList.vue** — 筛选栏（搜索框、趋势级别/方向/比价/杠杆下拉、排序选择、重置按钮）+ a-table 列表 + a-drawer 侧滑面板
- **index.vue** — 新增第三个 tab「代码列表」，引入 SymbolList 组件
- **marketOverview.js** — 新增 `getSymbolList(params)` 和 `getSymbolTimeline(symbol, params)` API 函数

## Key decisions

- 持仓行高亮（浅蓝色背景）
- 点击行打开 640px 宽 drawer
- 表格 11 列：代码、名称、趋势、RP状态、杠杆、相对强度、早期反转、趋势持续、价格位置、持仓、日期
- 筛选参数组合传给后端 API
