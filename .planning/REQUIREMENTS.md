# Requirements: 市场概览模块 (Market Overview)

**Defined:** 2026-05-19
**Core Value:** 让管理员快速掌握全市场多维度状态（趋势、比价、杠杆资金），通过结构化筛选规则发现交易机会和风险标的

## v1 Requirements

### 数据导入 (Data Import)

- [ ] **DATA-01**: 管理员可以上传 Excel 文件（.xlsx），系统使用 openpyxl 解析并自动入库
- [ ] **DATA-02**: 系统从文件名自动识别数据类型（美股市场/核心数据集/押注工具）和日期（如 `26-05-18` → `2026-05-18`）
- [ ] **DATA-03**: 每次导入的数据按 (date, symbol) 唯一索引存储，重复导入自动覆盖更新
- [ ] **DATA-04**: 管理员可以补传历史日期的数据（上传日期早于当前日期的文件）
- [ ] **DATA-05**: 导入完成后显示导入摘要（导入行数、新增/更新数量、数据日期）

### 权限控制 (Permission)

- [ ] **PERM-01**: 「市场概览」tab 仅对 admin 角色用户可见和可操作
- [ ] **PERM-02**: 所有市场概览 API 端点需验证 admin 权限，非管理员返回 403

### Dashboard 概览 (Dashboard)

- [ ] **DASH-01**: Dashboard 展示宏观统计卡片：日/周/月级别趋势分布（上行/静默/下行占比）
- [ ] **DASH-02**: Dashboard 展示资金面统计：加杠杆/去杠杆占比
- [ ] **DASH-03**: Dashboard 展示比价状态分布（lead/Improving/Weakening/Lag 占比）
- [ ] **DASH-04**: Dashboard 展示筛选分类汇总卡片（主升浪、主升调整、新信号/反转、规避区标的数量）
- [ ] **DASH-05**: Dashboard 展示持仓快照表：当前持仓标的的 D/W/M 趋势、比价状态、杠杆状态、60日位置一览
- [ ] **DASH-06**: Dashboard 展示与前一天数据的变动对比（新增/消失的信号、状态变化标的）
- [ ] **DASH-07**: Dashboard 默认展示最新日期数据，可切换日期查看历史

### 代码列表 (Screener List)

- [ ] **LIST-01**: 展示全量导入标的列表，包含代码、名称、相对强度、早期转折、D/W/M 趋势、比价状态、杠杆状态等核心字段
- [ ] **LIST-02**: 支持按代码/名称搜索筛选
- [ ] **LIST-03**: 支持按趋势状态筛选（上行/静默/下行，日/周/月级别）
- [ ] **LIST-04**: 支持按比价状态筛选（lead/Improving/Weakening/Lag）
- [ ] **LIST-05**: 支持按杠杆状态筛选（加杠杆/去杠杆）
- [ ] **LIST-06**: 支持按相对强度、早期转折、持续时间等字段排序
- [ ] **LIST-07**: 列表支持分页

### 标的详情 (Symbol Detail)

- [ ] **DTL-01**: 点击列表中的标的可进入详情页，展示该标的所有时序数据
- [ ] **DTL-02**: 详情页展示标的基础信息（代码、名称）和最新一天的核心指标
- [ ] **DTL-03**: 详情页展示各字段的时序变化图表（趋势状态、比价状态、杠杆资金的变化趋势）
- [ ] **DTL-04**: 详情页支持按日期范围筛选历史数据

## v2 Requirements

### 高级功能

- **ADV-01**: 支持导出筛选结果为 Excel/CSV
- **ADV-02**: 支持 ETF 面板数据导入和持仓关键词匹配
- **ADV-03**: 支持自动定时获取 Excel 数据
- **ADV-04**: 支持多用户独立数据和 Watchlist

## Out of Scope

| Feature | Reason |
|---------|--------|
| Discord 消息推送 | PRD 中描述但本模块不涉及，由其他系统处理 |
| 非管理员访问 | 本模块仅管理员可用，避免数据暴露 |
| 实时行情数据接入 | 本模块基于每日 Excel 批量数据，不接入实时行情 |
| 策略回测集成 | 与现有 backtest 模块独立，不做联动 |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| DATA-01 | — | Pending |
| DATA-02 | — | Pending |
| DATA-03 | — | Pending |
| DATA-04 | — | Pending |
| DATA-05 | — | Pending |
| PERM-01 | — | Pending |
| PERM-02 | — | Pending |
| DASH-01 | — | Pending |
| DASH-02 | — | Pending |
| DASH-03 | — | Pending |
| DASH-04 | — | Pending |
| DASH-05 | — | Pending |
| DASH-06 | — | Pending |
| DASH-07 | — | Pending |
| LIST-01 | — | Pending |
| LIST-02 | — | Pending |
| LIST-03 | — | Pending |
| LIST-04 | — | Pending |
| LIST-05 | — | Pending |
| LIST-06 | — | Pending |
| LIST-07 | — | Pending |
| DTL-01 | — | Pending |
| DTL-02 | — | Pending |
| DTL-03 | — | Pending |
| DTL-04 | — | Pending |

**Coverage:**
- v1 requirements: 25 total
- Mapped to phases: 0
- Unmapped: 25 ⚠️

---
*Requirements defined: 2026-05-19*
*Last updated: 2026-05-19 after initial definition*
