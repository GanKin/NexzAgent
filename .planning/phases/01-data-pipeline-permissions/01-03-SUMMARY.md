# Summary: Plan 01-03 — 前端集成与权限控制

**Status:** Completed
**Note:** 前端文件在 gversion/ 目录下，被 .gitignore 排除（前端有独立仓库）

## What was built

### 路由配置
- `gversion/QuantDinger-Vue/src/config/router.config.js`
- 新增 `/market-overview` 路由，位于 AI 资产分析之前
- `meta: { permission: ['admin'], icon: 'stock' }` 确保仅 admin 可见
- 组件懒加载 `() => import('@/views/market-overview')`

### API 层
- `gversion/QuantDinger-Vue/src/api/marketOverview.js`
- `uploadMarketData(file)` — FormData 上传，30 秒超时
- `getUploadHistory(parameter)` — 上传历史查询
- `getAvailableDates(parameter)` — 可用日期列表

### 前端页面
- `gversion/QuantDinger-Vue/src/views/market-overview/index.vue`
  - 主页面：上传区域 + 上传历史表格
  - 引用 UploadCard 组件
- `gversion/QuantDinger-Vue/src/views/market-overview/UploadCard.vue`
  - 拖拽+点击上传（a-upload-dragger）
  - 文件类型和大小校验
  - 上传成功显示导入摘要卡片
  - 上传失败显示具体错误

### 国际化
- `zh-CN.js`: `'menu.dashboard.marketOverview': '市场概览'`
- `en-US.js`: `'menu.dashboard.marketOverview': 'Market Overview'`

## Decisions made during execution
- gversion/ 目录被 .gitignore 排除，前端代码不在主仓库 git 追踪范围内
- 前端代码已写入磁盘，需要在独立的前端仓库中提交
- 使用 `custom-request` 替代 `action` 属性，手动调用 API 以便错误处理

## Files created/modified (disk only, not in main repo git)
- `gversion/QuantDinger-Vue/src/config/router.config.js` (modified)
- `gversion/QuantDinger-Vue/src/api/marketOverview.js` (new)
- `gversion/QuantDinger-Vue/src/views/market-overview/index.vue` (new)
- `gversion/QuantDinger-Vue/src/views/market-overview/UploadCard.vue` (new)
- `gversion/QuantDinger-Vue/src/locales/lang/zh-CN.js` (modified)
- `gversion/QuantDinger-Vue/src/locales/lang/en-US.js` (modified)

## Verification
- [x] 路由包含 `/market-overview`，permission: ['admin']
- [x] 路由位于 `/ai-asset-analysis` 之前
- [x] API 层包含 uploadMarketData, getUploadHistory, getAvailableDates
- [x] UploadCard 使用 a-upload-dragger，限制 .xlsx/.xls
- [x] i18n keys 已添加到 zh-CN 和 en-US
