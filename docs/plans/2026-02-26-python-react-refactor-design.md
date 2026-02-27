# Python + React 重构设计文档

**日期：** 2026-02-26
**作者：** Claude
**状态：** 已批准

## 概述

将现有的 Node.js + HTML 项目重构为 Python (FastAPI) + React (TypeScript) 技术栈，采用渐进式迁移策略，确保业务连续性。

## 技术选型

### 后端
- **框架：** FastAPI
- **Excel 处理：** openpyxl
- **数据验证：** Pydantic
- **异步支持：** asyncio + uvicorn

### 前端
- **框架：** React 18 + TypeScript
- **构建工具：** Vite
- **UI 组件：** shadcn/ui + Tailwind CSS
- **状态管理：** React Query (服务器状态) + Zustand (客户端状态)
- **HTTP 客户端：** axios

### 开发环境
- **容器化：** Docker + Docker Compose
- **代码格式化：** black/isort (Python), prettier/eslint (TypeScript)

## 项目结构

```
BU2Ama/
├── backend/                    # Python FastAPI 后端
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI 应用入口
│   │   ├── api/               # API 路由
│   │   │   ├── __init__.py
│   │   │   ├── mapping.py     # 颜色映射 API
│   │   │   └── excel.py       # Excel 处理 API
│   │   ├── core/              # 核心业务逻辑
│   │   │   ├── color_mapper.py
│   │   │   └── excel_processor.py
│   │   ├── models/            # Pydantic 数据模型
│   │   │   ├── mapping.py
│   │   │   └── excel.py
│   │   └── config.py          # 配置管理
│   ├── data/                  # 数据文件
│   ├── uploads/               # 上传文件目录
│   ├── templates/             # Excel 模板
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                   # React + TypeScript 前端
│   ├── src/
│   │   ├── components/        # React 组件
│   │   │   ├── ui/           # shadcn/ui 组件
│   │   │   ├── ColorMapping/ # 颜色映射管理
│   │   │   ├── ExcelUpload/  # 文件上传
│   │   │   └── ExcelProcess/ # Excel 处理
│   │   ├── hooks/            # 自定义 hooks
│   │   ├── lib/              # 工具函数
│   │   ├── services/         # API 调用
│   │   ├── store/            # Zustand 状态管理
│   │   ├── types/            # TypeScript 类型
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── Dockerfile
│
├── docker-compose.yml
├── CLAUDE.md
└── README.md
```

## 架构设计

### 后端架构

**API 层（app/api/）**
- 使用 FastAPI 路由装饰器定义端点
- 依赖注入管理共享资源
- 自动生成 OpenAPI 文档

**业务逻辑层（app/core/）**
- `color_mapper.py` - 颜色映射管理（读写 JSON、搜索、统计）
- `excel_processor.py` - Excel 处理核心逻辑
  - SKU 解析（正则表达式）
  - 文件分析（统计颜色分布）
  - 模板生成（openpyxl）
  - Launch Date 计算（北京时间）

**数据模型层（app/models/）**
- Pydantic 模型定义请求/响应结构
- 自动数据验证和类型检查
- 可导出为 TypeScript 类型

### 前端架构

**组件层（src/components/）**

**ColorMapping/** - 颜色映射管理
- `ColorMappingTable.tsx` - 显示所有映射
- `ColorMappingForm.tsx` - 添加/编辑映射
- `ColorSearch.tsx` - 搜索功能

**ExcelUpload/** - 文件上传
- `FileUploader.tsx` - 拖拽上传
- `FileList.tsx` - 已上传文件列表
- `AnalysisResult.tsx` - 分析结果展示

**ExcelProcess/** - Excel 处理
- `TemplateSelector.tsx` - 选择模板类型
- `PrefixSelector.tsx` - 选择 SKU 前缀
- `ProcessButton.tsx` - 处理按钮
- `DownloadLink.tsx` - 下载链接

**状态管理**
- React Query：管理服务器状态（API 调用、缓存）
- Zustand：管理客户端状态（UI 状态）

## API 设计

### 颜色映射管理
- `GET /api/mapping` - 获取所有映射
- `GET /api/mapping/search?keyword=xxx` - 搜索映射
- `POST /api/mapping` - 添加/更新映射
- `DELETE /api/mapping/{code}` - 删除映射

### Excel 处理
- `GET /api/templates` - 获取模板列表
- `POST /api/analyze` - 分析上传的文件
- `POST /api/process` - 处理 Excel 文件
- `GET /api/download/{filename}` - 下载生成的文件
- `GET /api/files` - 获取已上传文件列表
- `DELETE /api/files/{filename}` - 删除文件

## 数据流

**处理 Excel 的完整流程：**

1. 用户上传文件 → `FileUploader` 组件
2. 调用分析 API → `POST /api/analyze`（React Query mutation）
3. 显示分析结果 → `AnalysisResult` 组件
4. 用户选择前缀 → `PrefixSelector` 组件（更新 Zustand store）
5. 调用处理 API → `POST /api/process`（带进度条）
6. 后端处理 → FastAPI 后台任务（openpyxl 生成文件）
7. 返回下载链接 → 前端显示下载按钮
8. 用户下载 → `GET /api/download/{filename}`

## 迁移策略

### 阶段 1：后端迁移（1-2 天）
1. 创建 FastAPI 项目结构
2. 迁移 `color_mapper.py`
3. 迁移 `excel_processor.py`
4. 实现所有 API 端点
5. 测试：使用现有前端调用新后端

### 阶段 2：前端迁移（2-3 天）
1. 初始化 Vite + React + TypeScript 项目
2. 安装 shadcn/ui 和配置 Tailwind
3. 创建基础布局
4. 实现颜色映射管理功能
5. 实现 Excel 上传和处理功能
6. 完整功能测试

### 阶段 3：优化和部署（1 天）
1. Docker Compose 配置
2. 错误处理优化
3. 性能测试
4. 文档更新

## 测试策略

### 后端测试
- 单元测试：pytest 测试核心函数
- API 测试：pytest + httpx 测试所有端点
- 文件测试：使用现有 Excel 文件验证

### 前端测试
- 组件测试：Vitest + Testing Library
- 手动测试：完整用户流程

### 兼容性验证
- 使用相同测试数据
- 对比新旧系统输出
- 确保 Excel 文件格式一致

## 回滚计划

- 保留现有 Node.js 代码（重命名为 `legacy/`）
- 数据文件保持兼容
- 如有问题可快速切回

## 开发环境

### 启动开发环境
```bash
docker-compose up
```

- 后端：http://localhost:8000
- 前端：http://localhost:5173
- API 文档：http://localhost:8000/docs

### 安装依赖
```bash
# 后端
cd backend && pip install -r requirements.txt

# 前端
cd frontend && npm install
```

## 关键技术点

### 后端
- 异步文件上传（UploadFile）
- 后台任务处理大文件（BackgroundTasks）
- CORS 配置
- 统一错误处理
- 文件流式下载

### 前端
- TypeScript 严格模式
- React Query 的 useMutation 处理上传
- 文件上传进度显示
- Toast 通知
- 响应式设计

## 风险和缓解

**风险 1：openpyxl 性能**
- 缓解：使用后台任务处理大文件，避免阻塞 API

**风险 2：Excel 格式兼容性**
- 缓解：充分测试，对比新旧系统输出

**风险 3：学习曲线**
- 缓解：渐进式迁移，每个阶段都可以验证

## 后续优化（可选）

- 添加用户认证
- 数据库持久化（PostgreSQL）
- 任务队列（Celery/Redis）
- 更丰富的数据分析功能
- 批量处理优化
