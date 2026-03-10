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

## 2026-03-09 CLI Findings
- `backend/app/cli/check_env.py` 是新的 CLI 基准风格：小函数拆分、`main() -> int`、JSON 输出用 `ensure_ascii=False`
- `ExcelProcessor.process_excel_new(template_filename, source_filenames, price_report_filename=None)` 返回 `(output_filename, processed_count)`
- `FollowSellProcessor` 缺少面向 CLI 的 `process_skc()` 包装，需要新增以避免脚本重复实现查询逻辑
- 店铺映射需要统一为 `EP -> EPUS`、`DM -> DaMaUS`、`PZ -> PZUS`
- 处理器和模块级单例会向 stdout 打日志，CLI 的 `--json` 模式必须显式捕获这些输出

## 2026-03-09 Skill Packaging Findings
- `docs/plans/SKILL.md` 的主体可复用，但其中跟卖映射路径仍写成 `backend/data/...`，实际代码使用 `backend/uploads/新老款映射信息(1).xlsx`
- `add_color_size.py` 对 `--template` 和 `--price-report` 只使用 basename，因此文档必须明确这两个文件需要先落到 `backend/uploads/`
- 以 `~/.claude/skills/bu2ama-listing-ops` 为默认安装位置时，最稳妥的做法是提供 wrapper scripts，由 wrapper 自动定位 BU2Ama repo 再转发到 `backend/app/cli/*.py`
- DM 店铺存在 `DA-*` 和 `DM-*` 双命名现实，文档应明确 `DA -> DM` 归一化以及 follow-sell 对两种前缀的兼容

## 2026-03-09 Telegram Follow-Sell Findings
- 网页查询展示完整表格，是因为它使用 `find_sizes_for_skc()` 返回的 `size/suffix/sku` 明细；旧版 CLI 只保留了简化后的 `sizes` 列表
- Telegram/OpenClaw 要想和网页显示一致，不需要改底层跟卖逻辑，只需要在 CLI 层暴露 `size_details`
- 跟卖 Excel 导出逻辑已经存在于 API 层，CLI 可以直接复用同一套 `ExcelProcessor.process_excel(..., follow_sell_mode=True)` 生成文件
- 并行执行两次跟卖导出会竞争同一个临时 `processed_*.xlsx`，验证导出时应串行执行
- OpenClaw 对 Telegram/聊天附件的默认回传方式是回复中单独输出 `MEDIA:<absolute-path>`；不需要额外生成下载链接
