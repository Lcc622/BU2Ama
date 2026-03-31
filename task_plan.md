# Task Plan: STORE_GROUP 双实例隔离

## Goal
在不拆仓库、不改现有 API 路径和 CLI 脚本的前提下，为后端增加基于 `STORE_GROUP` 的实例级隔离能力，并补齐双实例 `docker-compose` 部署配置，同时保持未设置 `STORE_GROUP` 时的现有行为完全兼容。

## Current Phase
Phase 5

## Phases
### Phase 1: Requirements & Discovery
- [x] Understand user intent
- [x] Identify constraints and requirements
- [x] Document findings in findings.md
- **Status:** complete

### Phase 2: Planning & Structure
- [x] Define technical approach
- [x] Confirm affected modules and compatibility points
- [x] Document decisions with rationale
- **Status:** complete

### Phase 3: Implementation
- [x] Add `STORE_GROUP` and directory override support in config
- [x] Enforce per-instance store whitelist in excel processor
- [x] Add or update root `docker-compose.yml`
- [x] Remove old followsell chain if unused
- **Status:** complete

### Phase 4: Testing & Verification
- [x] Verify backward compatibility when `STORE_GROUP` unset
- [x] Verify EP and DM/PZ isolation paths and store filters
- [x] Document test results in progress.md
- **Status:** complete

### Phase 5: Delivery
- [ ] Review touched files
- [ ] Summarize risks or follow-ups
- [ ] Deliver to user
- **Status:** in_progress

## Key Questions
1. 当前配置和模板字典的结构，最小侵入式过滤点在哪里？
2. `excel_processor` 中哪些路径会对跨组店铺做 fallback，需要在运行时切断？
3. 旧 followsell API/router 是否仍被其他代码引用？

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| 先读优先文件和启动入口，再决定是否删除旧 followsell 链路 | 避免误删仍在引用的模块 |
| `excel.py` 内部 fallback 一并调整为实例内默认模板 | 避免 `STORE_GROUP=DM_PZ` 下内部仍回退到被过滤掉的 `EPUS` |
| 旧 followsell 仅移除 API/router 注册 | 满足清理旧链路目标，同时不影响仍依赖处理器的 CLI |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
|       | 1       |            |

## Notes
- 不修改 `STORE_PRIORITY` 常量定义本身，只在运行时过滤。
- 不修改 CLI 脚本和现有 API URL。
