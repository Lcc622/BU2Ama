# Task Plan: 通用导出历史（全模块）

## Goal
实现一套所有导出模块共用的历史记录系统（跟卖、加色、加码），含后端统一存储/API、导出自动记录、前端通用组件复用、下载删除与自动清理。

## Current Phase
Phase 6

## Phases
### Phase 1: Discovery & Scope Sync
- [x] 审核当前“跟卖专用历史”实现与导出入口
- [x] 明确通用表/API/组件的替换路径
- [x] 记录兼容风险（现有未提交改动）
- **Status:** complete

### Phase 2: Backend Unified History Core
- [x] 新建 `export_history.py`（SQLite 表、索引、CRUD、分页/过滤/搜索）
- [x] 实现事务安全、状态更新、自动清理（90天/1000条）
- [x] 在应用启动初始化通用表
- **Status:** complete

### Phase 3: Backend API & Export Integration
- [x] 新增 `/api/export-history` 列表/下载/删除接口
- [x] 在 `process_skc` / `process_skc_batch` 写入 follow-sell 历史
- [x] 在 `process_excel` / `process_excel_async` 写入 add-color/add-code 历史
- [x] 文件缺失更新 `file_missing` 且不抛错
- **Status:** complete

### Phase 4: Frontend Types/API/Component
- [x] 新增通用历史类型与 API
- [x] 新建 `ExportHistory.tsx`（折叠、过滤、搜索、分页、下载、删除）
- [x] 跟卖页与 Excel 处理页接入通用组件并设置默认过滤
- **Status:** complete

### Phase 5: Testing & Verification
- [x] 后端语法/导入检查
- [x] 前端构建检查
- [x] 历史模块与关键接口冒烟验证
- **Status:** complete

### Phase 6: Delivery
- [x] 汇总变更文件、验证结果、剩余风险
- **Status:** in_progress

## Key Questions
1. `ProcessRequest` 新增 `mode` 字段，默认 `add-color` 以兼容旧请求。
2. 异步导出历史在任务完成后写入，保证记录状态准确。

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| 新建通用 `export_history.py`，保留旧 `follow_sell_history.py` 但不再引用 | 最小侵入，避免影响现有未提交改动 |
| 统一历史写入封装到 `_record_export_history` | 同步/异步/跟卖入口复用并集中清理逻辑 |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| `ModuleNotFoundError: app`（冒烟脚本） | 1 | 增加 `PYTHONPATH=backend` 后通过 |

## 2026-03-09 CLI Task
- [x] Inspect current CLI style, processor interfaces, and upload/index behavior
- [x] Add shared CLI helpers and missing `FollowSellProcessor.process_skc()`
- [x] Implement `add_color_size.py`, `follow_sell.py`, and `upload_source.py`
- [x] Run CLI tests and capture JSON/exit code behavior

## 2026-03-09 Skill Packaging Task
- [x] Audit the stage-3 draft against the real CLI behavior
- [x] Create versioned skill source under `skills/bu2ama-listing-ops/`
- [x] Add wrapper scripts that dispatch to `backend/app/cli/*.py`
- [x] Write references for store rules, file contracts, troubleshooting, and Telegram flow
- [x] Install the skill into `~/.claude/skills/`

## 2026-03-09 Telegram Follow-Sell Alignment Task
- [x] Align CLI follow-sell query output with web UI detail columns
- [x] Add Excel export support to follow-sell CLI for Telegram/OpenClaw use
- [x] Update skill docs and examples for detailed query + export flow
