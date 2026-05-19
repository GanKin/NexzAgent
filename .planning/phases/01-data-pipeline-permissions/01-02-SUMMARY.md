# Summary: Plan 01-02 — Excel 解析与导入 API

**Status:** Completed
**Commit:** 8d566b0

## What was built

### Excel 解析器
- `backend_api_python/app/services/market_overview_parser.py`
- `MarketOverviewParser` 类，使用 openpyxl 逐行读取
- COLUMN_MAPPING 字典映射 23 个体系 B 中文列名到数据库字段
- `_normalize_value()` 方法处理空值兜底：趋势→'无趋势'，数值→0
- 错误收集不中断解析（行号+字段+原因）
- `validate_header()` 检查体系 B 标识列

### API 路由
- `backend_api_python/app/routes/market_overview.py`
- 3 个 admin-only 端点：
  - `POST /api/market-overview/upload` — multipart 上传+解析+入库+摘要
  - `GET /api/market-overview/uploads` — 上传历史列表
  - `GET /api/market-overview/dates` — 可用日期列表
- 所有端点 `@login_required + @admin_required` 双重保护
- Blueprint 已注册到 `app/routes/__init__.py`

### 依赖
- `requirements.txt` 添加 `openpyxl>=3.1.0`

## Decisions made during execution
- upload 端点先读取整个文件到内存再保存，用于大小校验
- 使用 `secure_filename` 处理文件名，但用原始文件名做日期/类型解析
- 保存文件名格式：`{date}_{type}_{timestamp}_{uuid8}.xlsx`
- 解析有部分错误但 records 非空时，继续导入但返回 warnings

## Files created/modified
- `backend_api_python/app/services/market_overview_parser.py` (new)
- `backend_api_python/app/routes/market_overview.py` (new)
- `backend_api_python/app/routes/__init__.py` (modified)
- `backend_api_python/requirements.txt` (modified)

## Verification
- [x] Python 语法有效（ast.parse 通过）
- [x] Blueprint 注册到 __init__.py
- [x] 3 个端点均有 @admin_required 装饰器
- [x] upload 返回 total_rows, new_rows, updated_rows 摘要
