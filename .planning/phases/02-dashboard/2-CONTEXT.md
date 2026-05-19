# Phase 2: Dashboard 概览 - Context

**Gathered:** 2026-05-19
**Status:** Ready for planning
**Mode:** Auto (recommended defaults)

<domain>
## Phase Boundary

在市场概览模块中构建 Dashboard 概览页，管理员上传数据后可一览全市场多维度状态（趋势分布、资金面、比价状态、筛选分类、持仓快照），并与前一天数据对比，快速发现变化和异常。

依赖 Phase 1 的数据管道（market_overview_data 表、API 端点、admin 权限控制）。

</domain>

<decisions>
## Implementation Decisions

### 页面布局
- **D-01:** 市场概览页面改为双 tab 结构：主 tab「Dashboard 概览」+ 子 tab「数据上传」（复用 Phase 1 上传页）
- **D-02:** Dashboard 使用卡片网格布局（a-row + a-col），从上到下依次为：日期选择器 → 统计卡片行 → 持仓快照表 → 变动对比区
- **D-03:** 统计卡片分为三行：第一行趋势分布（日/周/月）、第二行资金面和比价状态、第三行筛选分类汇总

### 趋势分布展示
- **D-04:** 趋势分布使用 Ant Design Vue 的 a-progress 堆叠进度条（非 ECharts 饼图），三种状态用不同颜色：上行=绿(#52c41a)、静默=黄(#faad14)、下行=红(#ff4d4f)
- **D-05:** 日/周/月三个趋势并排展示，每个堆叠条下方标注百分比数字

### 资金面与比价统计
- **D-06:** 资金面统计展示「加杠杆 / 去杠杆」占比，使用简单的数字卡片（大数字 + 百分比 + a-tag 颜色标签）
- **D-07:** 比价状态分布展示四种状态数量（lead / Improving / Weakening / Lag），使用 a-tag 组件，不同颜色区分

### 筛选分类汇总
- **D-08:** 筛选分类汇总展示四类标的数量：主升浪、主升调整、新信号/反转、规避区
- **D-09:** 分类逻辑复用 PRD 中定义的四分类筛选规则（基于 D/W/M 趋势 + 杠杆资金状态的组合条件）
- **D-10:** 后端在统计 API 中完成分类计算，前端只做展示

### 持仓快照表
- **D-11:** 持仓快照表展示持仓名单中所有标的的核心字段：代码、名称、D/W/M 趋势、比价状态、杠杆状态、60日位置
- **D-12:** 标的名称从 market_overview_data 表的 name 字段读取（Excel 已有此数据），前端不硬编码
- **D-13:** 持仓快照表仅只读展示，不支持排序和筛选（属于 Phase 3 范围）
- **D-14:** 持仓列表由后端维护：查询 market_overview_data 中特定日期 + 特定 symbol 集合的数据

### 历史对比
- **D-15:** 变动对比采用颜色标记模式：在持仓快照表中用颜色标注相对前一天的变化
- **D-16:** 颜色规则：绿色=改善（趋势升级、状态好转）、红色=恶化（趋势降级、状态恶化）、蓝色=新增（昨日不在数据中的标的）
- **D-17:** 趋势变化判定：前一天「无趋势」→ 今天「上行趋势」= 改善；前一天「上行趋势」→ 今天「下行趋势」= 恶化
- **D-18:** Dashboard 顶部单独展示变化摘要卡片：今日新增标的数、趋势改善数、趋势恶化数

### 日期切换
- **D-19:** Dashboard 顶部放置日期选择器（a-select 下拉框），列表为已有数据的日期（降序）
- **D-20:** 默认选中最新日期，切换日期时刷新所有卡片和表格数据
- **D-21:** 日期数据来源：调用 Phase 1 的 GET /api/market-overview/dates 端点

### API 设计
- **D-22:** 新增 `GET /api/market-overview/dashboard?date={date}` — 返回 Dashboard 所需的全部数据（一次请求）
- **D-23:** Dashboard API 返回结构：`{ stats: { trends, leverage, relative_price, categories }, holdings: [...], changes: { improved, worsened, new_symbols } }`
- **D-24:** 变化对比通过后端计算：查询 date 和 date-1（前一交易日）的数据对比

### Claude's Discretion
- 卡片的具体宽度和间距（响应式布局细节）
- 统计数据的颜色主题和图标选择
- 持仓快照表的列宽和排序默认值
- Dashboard API 的具体错误处理和空状态展示
- 空数据日期（周末/假期无数据）的前端提示

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### 数据字段定义与分类规则
- `gversion/prds/multi-level-trend-screener.md` — 体系 B 字段定义、四分类筛选规则（主升浪/主升调整/新信号/规避区）
- `gversion/prds/leverage-state-screener.md` — 杠杆状态数据字段

### Phase 1 已建基础设施
- `.planning/phases/01-data-pipeline-permissions/1-CONTEXT.md` — Phase 1 决策（数据库表结构、API 端点、权限控制）
- `.planning/phases/01-data-pipeline-permissions/01-01-SUMMARY.md` — 数据库表和服务层实现
- `.planning/phases/01-data-pipeline-permissions/01-02-SUMMARY.md` — API 端点实现

### 现有代码参考
- `backend_api_python/app/services/market_overview_service.py` — 现有 Service 方法（get_date_stats, get_available_dates）
- `backend_api_python/app/routes/market_overview.py` — 现有 API 路由（需扩展新端点）
- `QuantDinger-Vue/src/views/market-overview/index.vue` — 现有前端页面（需重构为双 tab）
- `QuantDinger-Vue/src/views/ai-asset-analysis/index.vue` — 现有 Dashboard 布局参考

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `MarketOverviewService.get_date_stats()` — 已有基础统计查询（D/W/M 趋势计数、杠杆状态计数）
- `MarketOverviewService.get_available_dates()` — 已有日期列表查询
- GET /api/market-overview/dates 端点 — 前端可直接调用获取日期列表

### Established Patterns
- 后端：Flask Blueprint + @admin_required 装饰器
- 前端：Vue 2 + Ant Design Vue（a-row/a-col 网格布局）
- API 响应格式：`{code: 1, msg: 'success', data: {...}}`

### Integration Points
- `backend_api_python/app/routes/market_overview.py` — 新增 dashboard 端点
- `backend_api_python/app/services/market_overview_service.py` — 新增 get_dashboard_data 方法
- `QuantDinger-Vue/src/views/market-overview/index.vue` — 重构为双 tab
- `QuantDinger-Vue/src/api/marketOverview.js` — 新增 dashboard API 函数

</code_context>

<deferred>
## Deferred Ideas

- Dashboard 数据缓存（Redis）— 首期每次请求实时计算
- 导出 Dashboard 报告为 PDF — 后续阶段考虑
- Dashboard 自动刷新（WebSocket）— 首期手动切换日期
- 移动端响应式适配 — 首期仅桌面端优化

</deferred>

---

*Phase: 02-dashboard*
*Context gathered: 2026-05-19 via auto mode (recommended defaults)*
