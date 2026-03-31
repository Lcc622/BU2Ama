# Progress Log

## Session: 2026-03-30

### Phase 1: Requirements & Discovery
- **Status:** complete
- **Started:** 2026-03-30
- Actions taken:
  - 读取 `using-superpowers` 和 `planning-with-files` 技能说明。
  - 运行 session catchup 检查。
  - 创建落盘计划文件，记录目标、限制和阶段划分。
  - 阅读优先文件 `config.py`、`excel_processor.py`、`api/excel.py`、`main.py`。
  - 追踪旧 followsell API/router、CLI 依赖和现有 `docker-compose.yml`。
- Files created/modified:
  - `task_plan.md` (created)
  - `findings.md` (created)
  - `progress.md` (created)

### Phase 2: Planning & Structure
- **Status:** complete
- Actions taken:
  - 确认配置层需要暴露当前实例允许的模板类型和店铺前缀。
  - 确认 `excel_processor` 需要在扫描、索引构建和搜索顺序三个层面做运行时过滤。
  - 确认 `excel.py` 需修复默认 `EPUS` fallback，避免在 `DM_PZ` 实例内部失效。
  - 确认旧 `followsell` API 可移除，但旧处理器需保留给 CLI。
- Files created/modified:
  - `task_plan.md` (updated)
  - `findings.md` (updated)
  - `progress.md` (updated)

### Phase 3: Implementation
- **Status:** complete
- Actions taken:
  - 在 `backend/app/config.py` 增加 `STORE_GROUP`、`UPLOADS_DIR`、`RESULTS_DIR` 环境变量支持，并导出当前实例允许的模板/店铺集合。
  - 在 `backend/app/core/excel_processor.py` 增加运行时店铺白名单校验，阻断跨组扫描、搜索顺序和索引 fallback。
  - 在 `backend/app/api/excel.py` 将默认模板 fallback 改为当前实例默认模板，保持未设置 `STORE_GROUP` 时仍优先 `EPUS`。
  - 在 `backend/app/main.py` 移除旧 `followsell` router 注册，并删除 `backend/app/api/followsell.py`。
  - 将根目录 `docker-compose.yml` 改为 `bu2ama-ep` 与 `bu2ama-dmpz` 双后端实例，共用同一 image/build。
- Files created/modified:
  - `backend/app/config.py` (updated)
  - `backend/app/core/excel_processor.py` (updated)
  - `backend/app/api/excel.py` (updated)
  - `backend/app/main.py` (updated)
  - `docker-compose.yml` (updated)
  - `backend/app/api/followsell.py` (deleted)

### Phase 4: Testing & Verification
- **Status:** complete
- Actions taken:
  - 运行 `python3 -m compileall backend/app` 和针对修改文件的 `compileall`，确认语法通过。
  - 运行环境变量导入脚本，验证 `STORE_GROUP` 为未设置、`EP`、`DM_PZ` 三种模式下模板和店铺白名单正确。
  - 运行路径覆盖脚本，验证 `UPLOADS_DIR` 与 `RESULTS_DIR` 环境覆盖生效并自动建目录。
  - 运行处理器白名单检查脚本，验证跨组请求会抛出 `ValueError`。
  - 运行 `pytest -q test_store_isolation.py test_follow_sell_isolation.py`，确认失败原因是测试文件缺少 `store_config` fixture，而不是本次改动引起的运行错误。
- Files created/modified:
  - `task_plan.md` (updated)
  - `progress.md` (updated)

## Test Results
| Test | Input | Expected | Actual | Status |
|------|-------|----------|--------|--------|
| Session catchup | `python3 .../session-catchup.py /Users/melodylu/PycharmProjects/BU2Ama` | 无阻塞恢复项 | 无输出，无阻塞项 | ✓ |
| Compile backend app | `python3 -m compileall backend/app` | 修改后的 Python 模块可编译 | 通过 | ✓ |
| STORE_GROUP unset | 导入 `app.config` | 保持全量模板且默认 fallback 仍为 `EPUS` | `TEMPLATES=('DaMaUS','EPUS','PZUS')`，默认 `EPUS` | ✓ |
| STORE_GROUP=EP | 导入 `app.config` | 仅允许 `EPUS` / `EP` | `TEMPLATES=('EPUS',)`，允许店铺 `('EP',)` | ✓ |
| STORE_GROUP=DM_PZ | 导入 `app.config` | 仅允许 `DaMaUS`,`PZUS` / `DM`,`PZ` | `TEMPLATES=('DaMaUS','PZUS')`，允许店铺 `('DM','PZ')` | ✓ |
| Directory override | 设置 `UPLOADS_DIR=/tmp/bu2ama-test/uploads`、`RESULTS_DIR=custom-results` 后导入 | 使用覆盖路径并自动建目录 | `/tmp/bu2ama-test/uploads` 与 `backend/custom-results` 均存在 | ✓ |
| Cross-group rejection | `STORE_GROUP=EP` 请求 `DM`；`STORE_GROUP=DM_PZ` 请求 `EP` | 抛出白名单错误 | 两种情况均抛出 `ValueError` | ✓ |
| Legacy tests | `pytest -q test_store_isolation.py test_follow_sell_isolation.py` | 若测试规范正确，应执行隔离校验 | 测试文件自身缺少 `store_config` fixture，未进入业务断言 | ⚠ |

## Error Log
| Timestamp | Error | Attempt | Resolution |
|-----------|-------|---------|------------|
|           |       | 1       |            |

## 5-Question Reboot Check
| Question | Answer |
|----------|--------|
| Where am I? | Phase 5 |
| Where am I going? | 交付改动摘要、验证结果和剩余风险 |
| What's the goal? | 为同仓库双实例隔离增加配置、处理器白名单和部署编排，同时保持默认兼容 |
| What have I learned? | 见 findings.md |
| What have I done? | 已完成实现、静态验证、环境变量校验和遗留测试检查 |
