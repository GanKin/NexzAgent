# 市场概览模块 (Market Overview)

## What This Is

在 QuantDinger 现有系统中新增「市场概览」模块，位于前端导航栏「AI资产分析」tab 之上，仅对管理员开放。用户通过上传每日 Excel 数据表（趋势识别+相对比价+资金监控），系统自动解析入库并记录时序，提供 Dashboard 概览、代码列表筛选、标的详情时序查看等功能。

## Core Value

让管理员快速掌握全市场多维度状态（趋势、比价、杠杆资金），通过结构化筛选规则发现交易机会和风险标的，替代手动查看 Excel 的工作方式。

## Requirements

### Validated

- ✓ 用户认证与权限系统 — 现有 JWT + admin 角色体系
- ✓ Vue + Ant Design 前端框架 — QuantDinger-Vue
- ✓ Flask REST API 后端 — backend_api_python
- ✓ PostgreSQL 数据库 — 时序数据存储
- ✓ Excel 文件解析能力 — openpyxl + pandas

### Active

- [ ] 管理员可在前端「市场概览」tab 上传 Excel 数据文件
- [ ] 系统自动识别 Excel 类型（美股市场/核心数据集/押注工具）并解析入库
- [ ] 每次导入的数据按日期记录时序，支持补传历史数据
- [ ] Dashboard 概览页展示宏观统计（日/周/月趋势占比、加杠杆/去杠杆占比、比价状态分布）
- [ ] Dashboard 概览页展示筛选分类（主升浪、主升调整、新信号、规避等标的数量）
- [ ] Dashboard 概览页展示持仓快照（当前持仓的 D/W/M 趋势、比价、杠杆状态一览）
- [ ] Dashboard 概览页展示历史对比（与前一天数据的变动对比）
- [ ] 代码列表页展示全量导入标的，支持搜索筛选（按代码、趋势状态、比价状态、杠杆状态）
- [ ] 代码列表页支持按相对强度、早期转折、持续时间等字段排序
- [ ] 代码列表页点击某标的可进入详情页查看时序变化历史
- [ ] 「市场概览」模块仅对管理员角色可见和可操作

### Out of Scope

- Discord 消息推送功能 — PRD 中描述但本模块不涉及
- 自动定时获取 Excel 数据 — 首期仅支持手动上传
- 导出筛选结果为 Excel/CSV — 首期不实现
- 非管理员用户的数据看板 — 本模块仅管理员可用
- ETF 面板的持仓关键词匹配 — 首期仅处理个股面板数据

## Context

### 数据来源
每日 Excel 文件由外部量化系统生成，命名格式如 `26-05-18 数据总表（趋势识别＋相对比价＋资金监控）（美股市场）.xlsx`。数据包含 25 列、约 1000 行（美股市场）或 235 行（核心数据集）。

### 数据字段（体系 B，25 列）
- **基础信息**: 代码、标的名称
- **相对强度**: 相对强度、强度动量、早期转折
- **比价状态**: 当前/此前比价状态、持续时间、涨幅
- **多级趋势**: 日/周/月级别趋势及持续时间
- **杠杆资金**: 当前/此前杠杆资金状态、持续时间、涨幅、数值、日变动
- **价格位置**: 收盘价对比60日位置

### 分析规则（参考 PRD）
- `gversion/prds/multi-level-trend-screener.md` — 多级别趋势筛选（五阶段分类）
- `gversion/prds/leverage-state-screener.md` — 杠杆状态筛选（四分类法）
- 持仓名单: PYPL MSFT ALB IXC AEIS AMPX MU SNDK PLTR META TSM GOOG UNH BE TAN SOXS

### 技术环境
- **前端**: Vue 2 + Ant Design Vue，位于 `/gversion/QuantDinger-Vue/`
- **后端**: Python Flask，位于 `/backend_api_python/`
- **数据库**: PostgreSQL 16 + Redis 7
- **部署**: Docker Compose，前端为预构建镜像

## Constraints

- **Tech Stack**: 必须使用现有技术栈（Vue 2 + Flask + PostgreSQL），不引入新框架
- **Permission**: 仅管理员可访问，利用现有 admin 角色判断
- **Data Format**: Excel 使用体系 B（中文列名），需兼容未来可能的体系 A
- **Performance**: 单次 Excel 约 1000 行 × 25 列，导入应在 5 秒内完成
- **Storage**: 时序数据保留至少 1 年，需考虑存储效率

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| 新增独立路由模块 `market_overview` | 与现有 fast_analysis 解耦，独立维护 | — Pending |
| Excel 解析使用 openpyxl | 比 pandas 更可控，避免 NaN 类型问题（PRD 经验） | — Pending |
| 时序数据按 (date, symbol) 唯一索引 | 每天每标的一条记录，支持补传和覆盖更新 | — Pending |
| 前端 Tab 位于 AI 资产分析之上 | 用户明确要求的位置 | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-05-19 after initialization*
