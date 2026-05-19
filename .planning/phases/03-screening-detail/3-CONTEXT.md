# Phase 3: 筛选与详情 - Context

**Gathered:** 2026-05-19
**Status:** Ready for planning
**Mode:** Auto (recommended defaults)

<domain>
## Phase Boundary

构建代码列表页和标的详情功能。管理员可在列表中通过搜索和多维筛选（趋势、比价、杠杆）定位目标标的，按字段排序分页浏览，点击标的打开侧边抽屉查看时序数据变化。这是市场概览模块的数据消费层——Phase 1 导入数据，Phase 2 概览全局，Phase 3 下钻分析。

依赖 Phase 1 的数据管道和 Phase 2 的 Dashboard 结构。

</domain>

<decisions>
## Implementation Decisions

### 页面结构
- **D-01:** 在现有双 tab 结构中增加第三 tab「代码列表」，三 tab 顺序：Dashboard → 数据上传 → 代码列表
- **D-02:** 代码列表 tab 包含：顶部筛选栏 + 数据表格 + 右侧抽屉详情

### 筛选交互
- **D-03:** 顶部筛选栏一行排列：搜索框（代码/名称）+ 趋势状态下拉 + 比价状态下拉 + 杠杆状态下拉 + 排序选择 + 重置按钮
- **D-04:** 趋势筛选支持日/周/月三个维度，默认筛选日级别（用一个下拉选维度 + 一个下拉选状态）
- **D-05:** 比价状态下拉选项：lead / Improving / Weakening / Lag / 全部
- **D-06:** 杠杆状态下拉选项：加杠杆 / 去杠杆 / 全部
- **D-07:** 排序选项：相对强度(降)、早期转折(降)、杠杆资金数值(降)、日趋势持续时间(升)、默认(相对强度降序)
- **D-08:** 筛选参数通过 URL query 传递，支持分享和刷新保持状态

### 列表表格
- **D-09:** 表格列：代码、名称、相对强度、早期转折、日/周/月趋势、比价状态、比价持续时间、杠杆状态、杠杆值、60日位置
- **D-10:** 表格支持分页（默认每页 50 条），后端分页
- **D-11:** 点击表格行打开右侧抽屉查看标的详情（非跳转页面）
- **D-12:** 表格行高亮持仓标的（浅蓝色背景），与 Dashboard 的持仓列表一致

### 详情抽屉
- **D-13:** 使用 a-drawer 右侧滑出，宽度 640px
- **D-14:** 抽屉顶部展示标的基础信息：代码、名称、最新日期核心指标
- **D-15:** 抽屉主体展示时序数据表格（按日期降序排列）
- **D-16:** 时序表格列：日期、D/W/M 趋势、比价状态、杠杆状态、杠杆值、杠杆变动、相对强度、60日位置
- **D-17:** 时序表格中的趋势字段用颜色标注（绿=上行、红=下行、黄=静默）
- **D-18:** 时序表格行与前一交易日对比，变化的字段高亮显示

### 日期范围筛选
- **D-19:** 详情抽屉顶部放置日期范围选择：快捷按钮（近7天、近30天、全部）+ a-range-picker
- **D-20:** 默认显示「近30天」数据

### API 设计
- **D-21:** `GET /api/market-overview/symbols` — 列表查询，支持 search/trend/trend_level/relative_price/leverage/sort/page/page_size 参数
- **D-22:** `GET /api/market-overview/symbols/:code/timeline` — 标的时序数据，支持 start_date/end_date 参数
- **D-23:** 列表 API 返回：`{ items: [...], total: N, page: N, page_size: N }`
- **D-24:** 时序 API 返回：`{ symbol, name, timeline: [...], date_range: {start, end} }`

### Claude's Discretion
- 表格列宽和默认可见列
- 筛选栏的响应式布局（窄屏折行）
- 抽屉内的空状态展示
- 分页组件样式
- 搜索的防抖时间

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase 1-2 已建基础设施
- `.planning/phases/01-data-pipeline-permissions/1-CONTEXT.md` — 数据库表结构
- `.planning/phases/02-dashboard/2-CONTEXT.md` — Dashboard 决策（四分类规则、持仓列表）
- `backend_api_python/app/services/market_overview_service.py` — 现有 Service 方法

### 数据字段定义
- `gversion/prds/multi-level-trend-screener.md` — 体系 B 字段定义
- `.planning/REQUIREMENTS.md` — LIST-01 ~ LIST-07, DTL-01 ~ DTL-04

### 前端代码参考
- `QuantDinger-Vue/src/views/market-overview/index.vue` — 现有三 tab 结构（需扩展）
- `QuantDinger-Vue/src/views/market-overview/DashboardTab.vue` — Dashboard 组件参考

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `MarketOverviewService.get_dashboard_data()` — 已有持仓查询和统计逻辑可参考
- `MarketOverviewService.HOLDINGS` — 持仓集合常量，用于列表高亮
- 三 tab 结构已在 `index.vue` 中建立，只需添加第三 tab

### Integration Points
- `backend_api_python/app/services/market_overview_service.py` — 新增 get_symbols + get_timeline
- `backend_api_python/app/routes/market_overview.py` — 新增 2 个端点
- `QuantDinger-Vue/src/views/market-overview/index.vue` — 添加第三 tab
- `QuantDinger-Vue/src/api/marketOverview.js` — 新增 2 个 API 函数

</code_context>

<deferred>
## Deferred Ideas

- 列表导出为 Excel/CSV — 后续版本
- 列表自定义列（显示/隐藏）— 后续版本
- 详情页 ECharts 图表 — 后续版本
- 详情页交易操作按钮 — 后续版本
- 多标的对比视图 — 后续版本

</deferred>

---

*Phase: 03-screening-detail*
*Context gathered: 2026-05-19 via auto mode (recommended defaults)*
