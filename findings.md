# Findings & Decisions

## Requirements
- 历史记录必须是所有导出模块共用：`follow-sell` / `add-color` / `add-code`。
- 后端统一表 `export_history` 存储模块、模板、输入参数 JSON、文件信息、状态与时间。
- 提供通用历史列表、下载、删除 API，支持模块过滤与搜索。
- 每次新增记录后执行自动清理：90 天前或总数超过 1000 的旧记录。

## Research Findings
- 当前项目已有 `follow_sell_history.py` 与 `/api/follow-sell/history*`，仅覆盖跟卖模块。
- 导出入口在 `backend/app/api/excel.py`：
  - 跟卖：`process_skc`, `process_skc_batch`
  - 加色/加码：`process_excel`, `process_excel_async`（后台 `_run_process_job` 完成）
- 前端仅 `FollowSellUpload.tsx` 内部实现了跟卖历史 UI；Excel 处理页还未接入历史。

## Technical Decisions
| Decision | Rationale |
|----------|-----------|
| 新建通用 `ExportHistoryStore`，不复用跟卖专用 store | 字段结构不同，通用模块更清晰 |
| `input_data` 统一 JSON 存储并在查询时反序列化 | 满足跨模块展示与搜索需要 |
| 异步导出在任务完成时入库 | 避免未完成任务写入“成功”历史 |
| 历史写入失败不影响导出主流程 | 防止因日志故障导致导出失败 |

## Issues Encountered
| Issue | Resolution |
|-------|------------|
| 冒烟脚本导入失败（找不到 `app` 包） | 增加 `PYTHONPATH=backend` |

## Resources
- `backend/app/core/export_history.py`
- `backend/app/api/excel.py`
- `frontend/src/components/ExportHistory.tsx`
- `frontend/src/components/FollowSell/FollowSellUpload.tsx`
- `frontend/src/App.tsx`
