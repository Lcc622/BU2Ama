# Findings & Decisions

## Requirements
- 新增 `STORE_GROUP` 环境变量支持：
- `EP` 仅加载 `EPUS`
- `DM_PZ` 仅加载 `DaMaUS` 和 `PZUS`
- 未设置时保留当前全量加载行为
- `TEMPLATES` 和 `STORE_CONFIGS` 需要按组过滤
- `UPLOADS_DIR` / `RESULTS_DIR` 允许环境变量覆盖
- `excel_processor` 运行时必须拒绝非当前实例白名单的店铺请求
- 根目录需要双 service `docker-compose.yml`
- 不修改 CLI 脚本、不修改 API 路径、不动现有 Dockerfile
- 若旧 followsell 无引用，可删除对应 API/router 与处理器

## Research Findings
- 会话恢复脚本无未同步输出，可按当前仓库状态直接开始。
- `backend/app/config.py` 当前直接定义全量 `TEMPLATES` 和 `STORE_CONFIGS`，`UPLOADS_DIR` / `RESULTS_DIR` 仍为固定默认目录。
- `backend/app/core/excel_processor.py` 使用 `STORE_PRIORITY = ("EP", "DM", "PZ")` 做扫描和 fallback，需要在运行时过滤允许店铺。
- `backend/app/api/excel.py` 内部 helper 直接默认回退 `EPUS`，在 `STORE_GROUP=DM_PZ` 实例中会失效。
- `backend/app/main.py` 仍注册旧 `followsell` router。
- `backend/app/api/followsell.py` 只被 `main.py` 引用；但 `backend/app/core/followsell_processor.py` 仍被 CLI `upload_source.py` 和 `follow_sell.py` 使用，不能删。
- 根目录已存在 `docker-compose.yml`，当前只有单 backend service。

## Technical Decisions
| Decision | Rationale |
|----------|-----------|
| 先从 `config.py` 建立实例白名单，再在处理器层消费该白名单 | 把组隔离逻辑集中在配置层，降低散落判断 |
| 保留 `STORE_PRIORITY` 常量，新增运行时 allowed store 过滤 | 符合“不改常量本身，只在运行时过滤”的要求 |
| 仅移除旧 `followsell` API/router，不删除 `core/followsell_processor.py` | 处理器仍被现有 CLI 依赖，删除会破坏非目标功能 |

## Issues Encountered
| Issue | Resolution |
|-------|------------|
| `backend/app/api/__init__.py` 不存在 | 无需处理，路由由 `main.py` 直接导入 |

## Resources
- `/Users/melodylu/PycharmProjects/BU2Ama/backend/app/config.py`
- `/Users/melodylu/PycharmProjects/BU2Ama/backend/app/core/excel_processor.py`
- `/Users/melodylu/PycharmProjects/BU2Ama/backend/app/api/excel.py`
- `/Users/melodylu/PycharmProjects/BU2Ama/backend/app/main.py`
- `/Users/melodylu/PycharmProjects/BU2Ama/docker-compose.yml`

## Visual/Browser Findings
- 无
