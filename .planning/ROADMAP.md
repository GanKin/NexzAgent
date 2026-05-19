# Roadmap: 市场概览模块 (Market Overview)

## Overview

为 QuantDinger 现有系统新增「市场概览」模块。从管理员上传 Excel 数据的管道开始，构建 Dashboard 宏观概览视图，最后完成筛选列表和标的详情的交互式分析能力。三个阶段覆盖完整的数据生命周期：导入 -> 概览 -> 下钻。

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: 数据管道与权限** - 数据库建表、Excel 导入解析、API 端点和管理员权限控制
- [ ] **Phase 2: Dashboard 概览** - 宏观统计卡片、筛选分类汇总、持仓快照、历史对比
- [ ] **Phase 3: 筛选与详情** - 代码列表多维度筛选排序、标的详情时序查看

## Phase Details

### Phase 1: 数据管道与权限
**Goal**: 管理员可以上传 Excel 数据文件并自动入库，系统按日期和标的记录时序，非管理员无法访问
**Depends on**: Nothing (first phase)
**Requirements**: DATA-01, DATA-02, DATA-03, DATA-04, DATA-05, PERM-01, PERM-02
**Success Criteria** (what must be TRUE):
  1. 管理员登录后可在前端上传 .xlsx 文件，系统在 5 秒内完成解析并显示导入摘要（行数、新增/更新数量、数据日期）
  2. 系统自动从文件名识别数据类型（美股市场/核心数据集/押注工具）和日期，无需手动指定
  3. 同一日期同一标的重复导入时自动覆盖更新，不会产生重复记录
  4. 管理员可上传历史日期的文件（补传），数据正确按对应日期入库
  5. 非管理员用户看不到「市场概览」tab，直接访问 API 端点返回 403
**Plans**: TBD

Plans:
- [ ] 01-01: 数据库建表与后端服务（market_overview_data、market_overview_uploads 表，Service 层）
- [ ] 01-02: Excel 解析与导入 API（openpyxl 解析、文件名识别、数据入库、导入摘要）
- [ ] 01-03: 前端集成与权限控制（导航 tab、上传组件、admin 权限守卫）

### Phase 2: Dashboard 概览
**Goal**: 管理员在 Dashboard 页一览全市场多维度状态，快速发现变化和异常
**Depends on**: Phase 1
**Requirements**: DASH-01, DASH-02, DASH-03, DASH-04, DASH-05, DASH-06, DASH-07
**Success Criteria** (what must be TRUE):
  1. Dashboard 展示日/周/月趋势分布卡片（上行/静默/下行占比），管理员可直观判断市场整体方向
  2. Dashboard 展示资金面统计（加杠杆/去杠杆占比）和比价状态分布（lead/Improving/Weakening/Lag），形成完整的资金面概览
  3. Dashboard 展示筛选分类汇总卡片（主升浪、主升调整、新信号/反转、规避区标的数量），管理员可一眼看到各分类有多少标的
  4. Dashboard 展示持仓快照表，列出当前持仓名单的所有标的的 D/W/M 趋势、比价状态、杠杆状态、60日位置
  5. Dashboard 展示与前一天数据的变动对比（新增/消失的信号、状态变化标的），管理员可快速定位变化
  6. Dashboard 默认展示最新日期数据，管理员可切换日期查看任意历史日期的 Dashboard
**Plans**: TBD
**UI hint**: yes

Plans:
- [ ] 02-01: Dashboard 后端统计 API（趋势分布、资金面、比价分布、筛选分类、持仓快照、历史对比）
- [ ] 02-02: Dashboard 前端视图（统计卡片、持仓快照表、日期切换、变动对比展示）

### Phase 3: 筛选与详情
**Goal**: 管理员可通过多维度筛选快速定位目标标的，并下钻查看单标的的时序变化趋势
**Depends on**: Phase 2
**Requirements**: LIST-01, LIST-02, LIST-03, LIST-04, LIST-05, LIST-06, LIST-07, DTL-01, DTL-02, DTL-03, DTL-04
**Success Criteria** (what must be TRUE):
  1. 列表页展示全量导入标的，包含代码、名称、相对强度、早期转折、D/W/M 趋势、比价状态、杠杆状态等核心字段
  2. 管理员可按代码/名称搜索，按趋势状态、比价状态、杠杆状态组合筛选，快速缩小范围
  3. 列表支持按相对强度、早期转折、持续时间等字段排序，支持分页浏览
  4. 点击列表中的标的进入详情页，展示该标的所有时序数据
  5. 详情页展示时序变化图表（趋势状态、比价状态、杠杆资金的变化趋势），管理员可按日期范围筛选
**Plans**: TBD
**UI hint**: yes

Plans:
- [ ] 03-01: 筛选列表后端 API（多条件查询、排序、分页）
- [ ] 03-02: 筛选列表前端视图（搜索、筛选控件、排序表格、分页）
- [ ] 03-03: 标的详情后端 API（时序数据查询、日期范围筛选）
- [ ] 03-04: 标的详情前端视图（基础信息、时序图表、日期范围选择器）

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. 数据管道与权限 | 0/3 | Not started | - |
| 2. Dashboard 概览 | 0/2 | Not started | - |
| 3. 筛选与详情 | 0/4 | Not started | - |
