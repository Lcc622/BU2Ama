# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Workflow

- **Claude**: Responsible for code review, architecture decisions, task planning, and finalizing implementation approaches after discussing with Codex
- **Codex**: Responsible for code implementation and execution
- **Design discussion**: Claude proposes approaches, discusses and confirms with Codex via the Codex skill, then finalizes the implementation plan
- **Parallel development**: For independent tasks, Claude can open multiple Codex sessions in parallel using the `parallel-codex-sessions` or `subagent-driven-development` skill

> **Important**: Every time `/init` generates or updates a project CLAUDE.md, this Development Workflow section must be included verbatim.

## 用户自定义规则

让codex实现代码，你在review

## Skill 同步规则

每次项目业务逻辑变更后（包括 SKU 规则、后缀逻辑、store 映射、文件路径等），必须同步更新以下所有 skill 副本：

1. `skills/bu2ama-listing-ops/`（项目内，OpenClaw symlink 指向此处）
2. `/Users/melodylu/.claude/skills/bu2ama-listing-ops/`（Claude Code 本地副本）
3. `/Users/melodylu/PycharmProjects/deer-flow/skills/public/bu2ama-listing-ops/`（deer-flow 公开副本）

重点关注 `references/store-rules.md`，所有 SKU 后缀、size 阈值、store 规则的变更都需要在这里体现。

## Project Overview

Amazon 电商 SKU 加色/加码/跟卖系统，按店铺拆分为独立部署单元：
- **EP** (Ever-Pretty US) → `ep/` 目录，端口 8001/5173
- **DM** (DaMa US) + **PZ** (Pinzou US) → `dmpz/` 目录，端口 8003/5174

核心功能：
- 基于模板生成加色/加码后的 Amazon 上传 Excel
- 跟卖（follow-sell）：新款映射老款，生成带属性的上传文件
- SKU 拆分（款号7位 + 颜色2位 + 尺码2位 + 后缀）
- 颜色代码映射维护（如 `LV -> Lavender`）

## Technology Stack

- **Backend**: Python / FastAPI / openpyxl / Pydantic / Uvicorn
- **Frontend**: React 18 + TypeScript / Vite / Tailwind CSS / Zustand
- **部署**: Docker Compose（每店铺独立容器，volume mount + --reload 热更新）

## Commands

### 启动服务（Docker Compose）
```bash
# EP 店铺
cd ep && docker-compose up -d

# DM/PZ 店铺
cd dmpz && docker-compose up -d
```

### 本地开发
```bash
# EP 后端
cd ep/backend && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8001

# DM/PZ 后端
cd dmpz/backend && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8003

# 前端（EP 或 DM/PZ）
cd ep/frontend && npm install && npm run dev
cd dmpz/frontend && npm install && npm run dev
```

### CLI 工具（通过 skill 调用）
```bash
# 加色/加码
python3 ~/.claude/skills/bu2ama-listing-ops/scripts/add_color_size.py --store EP --prefix EE00466 --mode add-color --colors BD,WH --start-size 04 --end-size 26 --size-step 2 --json

# 跟卖查询
python3 ~/.claude/skills/bu2ama-listing-ops/scripts/follow_sell.py --skc EE00756WH --store EP --json

# 源文件上传
python3 ~/.claude/skills/bu2ama-listing-ops/scripts/upload_source.py --file <path> --store EP --rebuild-index --json
```

## Architecture

```
BU2Ama/
├── ep/                        # EP 店铺（独立部署）
│   ├── backend/app/
│   │   ├── api/excel.py       # API 路由（加色/跟卖/文件管理）
│   │   ├── core/
│   │   │   ├── excel_processor.py   # 核心处理引擎（~2700行）
│   │   │   ├── color_mapper.py      # 颜色代码映射
│   │   │   └── output_validator.py  # 输出校验
│   │   ├── models/            # Pydantic 请求/响应模型
│   │   ├── config.py          # EP 店铺配置（模板/前缀/路径）
│   │   └── cli/               # CLI 脚本入口
│   ├── frontend/src/          # React 前端
│   └── docker-compose.yml     # 端口 8001 / 5173
│
├── dmpz/                      # DM+PZ 店铺（独立部署）
│   ├── backend/app/           # 同 EP 结构，配置不同
│   │   └── config.py          # DaMaUS/PZUS 双模板配置
│   └── docker-compose.yml     # 端口 8003 / 5174
│
└── skills/bu2ama-listing-ops/ # Claude Code skill（CLI 封装）
```

### 核心处理流程 (excel_processor.py)

`process_excel()` 是核心函数，处理流程：
1. 加载源数据索引（SQLite 缓存 → `excel_index_{store}.db`）
2. 构建 SKU 查找表（sku_to_source / style_to_source / style_color_size_suffix_to_source）
3. 新老款映射（`新老款映射信息(1).xlsx`）
4. 模板加载（带内存缓存，按 mtime+size 签名）
5. 逐 SKU 处理：源数据匹配 → 原型行复制 → 映射规则覆盖 → 属性/价格/图片填充
6. 输出 Excel

### 处理模式

| 模式 | 用途 | 源数据来源 |
|------|------|-----------|
| add-color | 加色（新颜色） | 老款同款不同色 |
| add-code | 加码（新尺码） | 同款同色不同码 |
| follow-sell | 跟卖（新款跟老款） | 老款数据 + 新款物理属性 |

### 关键数据结构

- **source_rows**: `Dict[sku, List[Any]]` — 源文件每行数据
- **source_header_map_by_file**: `Dict[filename, Dict[normalized_header, List[col_idx]]]` — 按文件的表头索引
- **canonical_row_values**: 跟卖模式下同款同色第一条记录，用于属性一致性
- **display_source**: 加色模式下同款同体型第一条记录，用于展示属性

## Store Configuration

| 配置项 | EP | DM/PZ |
|--------|-----|-------|
| 模板 | EPUS | DaMaUS, PZUS |
| 源文件前缀 | EP-0.xlsm | DA-0.xlsm, PZ-0.xlsm |
| SKU 后缀 | -USA | -PL |
| 端口 | 8001/5173 | 8003/5174 |
| 跟卖模板 | 无独立模板 | DAMA跟卖模板.xlsm |

## Data Notes

- 数据源/模板/索引在各店铺的 `backend/uploads/` 目录
- 输出结果在各店铺的 `backend/results/` 目录
- 索引按店铺分库：`excel_index_EP.db` / `excel_index_DM.db` / `excel_index_PZ.db`
- Docker volume mount 使代码修改即时生效，无需重新 build

## Important Business Rules

- **SKU 格式**: 7位款号 + 2位颜色 + 2位尺码 + 后缀（如 `EE02960LV14-PL`）
- **material_type**: 优先从源数据 Material 字段读取，fallback 固定 `100%Polyester`
- **Restock Date**: 所有模式统一清空
- **跟卖物理属性**: NeckStyle/Sleeve Type 等从新款源数据读取（非老款）
- **跟卖文本内容**: Bullet Points/Description 从老款 canonical 源读取
- **价格逻辑**: 跟卖 = 老价格 - 0.1；list_price = price + 10；business_price = price - 1
