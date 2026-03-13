# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 用户自定义规则

让codex实现代码，你在review

## Skill 同步规则

每次项目业务逻辑变更后（包括 SKU 规则、后缀逻辑、store 映射、文件路径等），必须同步更新以下所有 skill 副本：

1. `skills/bu2ama-listing-ops/`（项目内，OpenClaw symlink 指向此处）
2. `/Users/melodylu/.claude/skills/bu2ama-listing-ops/`（Claude Code 本地副本）
3. `/Users/melodylu/PycharmProjects/deer-flow/skills/public/bu2ama-listing-ops/`（deer-flow 公开副本）

重点关注 `references/store-rules.md`，所有 SKU 后缀、size 阈值、store 规则的变更都需要在这里体现。

## Project Overview

Excel 颜色加色系统（Version 2.0），用于处理 SKU 数据与颜色映射：
- 维护颜色代码映射（如 `LV -> Lavender`）
- 分析 Excel 中 SKU 的颜色分布
- 基于模板生成加色后的 Excel 文件
- 面向电商 SKU 场景，支持标准 SKU 拆分（款号/颜色/尺码/后缀）

## Technology Stack

### Backend
- Python
- FastAPI
- openpyxl
- Pydantic
- Uvicorn

### Frontend
- React 18 + TypeScript
- Vite
- Tailwind CSS
- React Query
- Zustand
- Axios

## Commands

### Docker Compose（推荐）
```bash
docker-compose up
docker-compose down
```

### Backend
```bash
cd backend
pip install -r requirements.txt
python -m app.main
# or
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
npm run build
```

## Architecture（目录结构概览）

```text
backend/
  app/
    api/        # 路由层（mapping, excel）
    core/       # 核心业务（颜色映射、Excel 处理）
    models/     # Pydantic 模型
    main.py     # FastAPI 入口
frontend/
  src/
    components/ # 页面与业务组件
    services/   # API 调用
    store/      # Zustand 状态
    types/      # TS 类型
data/           # 映射等数据文件
templates/      # Excel 模板（如有）
backend/results/ # 处理结果输出
```

## Data Notes

- 数据源文件：支持 DM/PZ/EP 三店铺（`{EP|DM|PZ}-0/1/2.xlsm` 和价格报告）
- 输出目录：`backend/results/`
- 索引策略：按店铺分库（`excel_index_EP.db` / `excel_index_DM.db` / `excel_index_PZ.db`）
