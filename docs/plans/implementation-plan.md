# Python + React 重构实施计划

**项目：** BU2Ama Excel 颜色加色系统重构
**日期：** 2026-02-26
**状态：** 待执行

## 目标

将现有的 Node.js + HTML 项目重构为 Python (FastAPI) + React (TypeScript) 技术栈，采用渐进式迁移策略。

## 技术栈

### 后端
- **框架：** FastAPI
- **Excel 处理：** openpyxl
- **数据验证：** Pydantic
- **服务器：** Uvicorn

### 前端
- **框架：** React 18 + TypeScript
- **构建工具：** Vite
- **UI 组件：** shadcn/ui + Tailwind CSS
- **状态管理：** React Query + Zustand
- **HTTP 客户端：** Axios

### 开发环境
- **容器化：** Docker + Docker Compose
- **代码格式化：** Black (Python) + Prettier (TypeScript)

## 实施阶段

### 阶段 1：后端迁移（预计 1-2 天）

#### 任务 1.1：创建 FastAPI 项目结构
- [ ] 创建 `backend/` 目录结构
- [ ] 创建 `app/` 主应用目录
- [ ] 创建 `app/api/`、`app/core/`、`app/models/` 子目录
- [ ] 创建 `requirements.txt` 文件
- [ ] 创建 `app/__init__.py` 和 `app/main.py`

**依赖项：**
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6
openpyxl==3.1.2
pydantic==2.5.3
python-dateutil==2.8.2
```

#### 任务 1.2：实现颜色映射模块
- [ ] 创建 `app/models/mapping.py`（Pydantic 模型）
- [ ] 创建 `app/core/color_mapper.py`（业务逻辑）
  - [ ] `load_mappings()` - 从 JSON 加载映射
  - [ ] `save_mappings()` - 保存映射到 JSON
  - [ ] `get_all_mappings()` - 获取所有映射
  - [ ] `search_mappings()` - 搜索映射
  - [ ] `add_mapping()` - 添加/更新映射
  - [ ] `delete_mapping()` - 删除映射
- [ ] 创建 `app/api/mapping.py`（API 路由）
  - [ ] `GET /api/mapping` - 获取所有映射
  - [ ] `GET /api/mapping/search` - 搜索映射
  - [ ] `POST /api/mapping` - 添加/更新映射
  - [ ] `DELETE /api/mapping/{code}` - 删除映射

#### 任务 1.3：实现 Excel 处理模块
- [ ] 创建 `app/models/excel.py`（Pydantic 模型）
- [ ] 创建 `app/core/excel_processor.py`（业务逻辑）
  - [ ] `parse_sku()` - 解析 SKU 格式
  - [ ] `extract_color_from_sku()` - 提取颜色代码
  - [ ] `analyze_excel_file()` - 分析 Excel 文件
  - [ ] `get_color_map_value()` - 获取颜色分类
  - [ ] `calculate_launch_date()` - 计算上线日期
  - [ ] `process_excel()` - 生成新 Excel 文件
- [ ] 创建 `app/api/excel.py`（API 路由）
  - [ ] `GET /api/templates` - 列出可用模板
  - [ ] `POST /api/analyze` - 分析上传的文件
  - [ ] `POST /api/process` - 处理 Excel 文件
  - [ ] `GET /api/download/{filename}` - 下载生成的文件
  - [ ] `GET /api/files` - 列出已上传文件
  - [ ] `DELETE /api/files/{filename}` - 删除文件

#### 任务 1.4：配置和中间件
- [ ] 创建 `app/config.py`（配置管理）
- [ ] 在 `app/main.py` 中配置 CORS
- [ ] 添加错误处理中间件
- [ ] 配置静态文件服务（uploads/）

#### 任务 1.5：测试后端
- [ ] 使用现有前端（HTML）测试新后端 API
- [ ] 验证颜色映射 CRUD 功能
- [ ] 验证 Excel 分析功能
- [ ] 验证 Excel 处理功能
- [ ] 对比新旧系统输出结果

---

### 阶段 2：前端迁移（预计 2-3 天）

#### 任务 2.1：初始化 React 项目
- [ ] 创建 `frontend/` 目录
- [ ] 使用 Vite 初始化 React + TypeScript 项目
  ```bash
  npm create vite@latest frontend -- --template react-ts
  ```
- [ ] 安装依赖：
  ```bash
  npm install @tanstack/react-query zustand axios
  npm install -D tailwindcss postcss autoprefixer
  npm install lucide-react class-variance-authority clsx tailwind-merge
  ```
- [ ] 配置 Tailwind CSS
- [ ] 配置 TypeScript（strict mode）

#### 任务 2.2：安装和配置 shadcn/ui
- [ ] 初始化 shadcn/ui
  ```bash
  npx shadcn-ui@latest init
  ```
- [ ] 安装需要的组件：
  ```bash
  npx shadcn-ui@latest add button
  npx shadcn-ui@latest add input
  npx shadcn-ui@latest add table
  npx shadcn-ui@latest add dialog
  npx shadcn-ui@latest add form
  npx shadcn-ui@latest add toast
  npx shadcn-ui@latest add card
  npx shadcn-ui@latest add select
  npx shadcn-ui@latest add checkbox
  ```

#### 任务 2.3：创建基础架构
- [ ] 创建 `src/types/api.ts`（TypeScript 类型定义）
- [ ] 创建 `src/lib/axios.ts`（Axios 配置）
- [ ] 创建 `src/services/mappingApi.ts`（颜色映射 API）
- [ ] 创建 `src/services/excelApi.ts`（Excel 处理 API）
- [ ] 创建 `src/store/useUploadStore.ts`（Zustand store）
- [ ] 创建 `src/store/useProcessStore.ts`（Zustand store）
- [ ] 配置 React Query（`src/lib/queryClient.ts`）

#### 任务 2.4：实现颜色映射管理功能
- [ ] 创建 `src/components/ColorMapping/ColorMappingTable.tsx`
  - [ ] 显示所有映射（使用 shadcn Table）
  - [ ] 排序和筛选功能
  - [ ] 删除按钮
- [ ] 创建 `src/components/ColorMapping/ColorMappingForm.tsx`
  - [ ] 添加/编辑表单（使用 shadcn Form + Dialog）
  - [ ] 表单验证
- [ ] 创建 `src/components/ColorMapping/ColorSearch.tsx`
  - [ ] 搜索输入框（使用 shadcn Input）
  - [ ] 实时搜索
- [ ] 创建 `src/components/ColorMapping/index.tsx`（主组件）

#### 任务 2.5：实现 Excel 上传和处理功能
- [ ] 创建 `src/components/ExcelUpload/FileUploader.tsx`
  - [ ] 拖拽上传功能
  - [ ] 文件类型验证
  - [ ] 上传进度显示
- [ ] 创建 `src/components/ExcelUpload/FileList.tsx`
  - [ ] 显示已上传文件列表
  - [ ] 删除文件功能
- [ ] 创建 `src/components/ExcelUpload/AnalysisResult.tsx`
  - [ ] 显示 SKU 分布
  - [ ] 显示颜色统计
  - [ ] 显示未知颜色
- [ ] 创建 `src/components/ExcelProcess/TemplateSelector.tsx`
  - [ ] 选择模板类型（DaMaUS/EPUS）
- [ ] 创建 `src/components/ExcelProcess/PrefixSelector.tsx`
  - [ ] 多选 SKU 前缀
- [ ] 创建 `src/components/ExcelProcess/ProcessButton.tsx`
  - [ ] 处理按钮
  - [ ] 进度条显示
- [ ] 创建 `src/components/ExcelProcess/DownloadLink.tsx`
  - [ ] 下载生成的文件

#### 任务 2.6：创建主布局
- [ ] 创建 `src/components/Layout/Header.tsx`
- [ ] 创建 `src/components/Layout/MainLayout.tsx`
  - [ ] 左右分栏布局
  - [ ] 响应式设计
- [ ] 创建 `src/App.tsx`（主应用组件）
- [ ] 配置 Tailwind 渐变背景

#### 任务 2.7：测试前端
- [ ] 测试颜色映射 CRUD 功能
- [ ] 测试文件上传功能
- [ ] 测试 Excel 分析功能
- [ ] 测试 Excel 处理功能
- [ ] 测试响应式布局
- [ ] 测试错误处理和 Toast 提示

---

### 阶段 3：Docker 和部署（预计 1 天）

#### 任务 3.1：创建 Docker 配置
- [ ] 创建 `backend/Dockerfile`
  ```dockerfile
  FROM python:3.11-slim
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt
  COPY . .
  CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
  ```
- [ ] 创建 `frontend/Dockerfile`
  ```dockerfile
  FROM node:20-alpine
  WORKDIR /app
  COPY package*.json .
  RUN npm install
  COPY . .
  CMD ["npm", "run", "dev", "--", "--host"]
  ```
- [ ] 创建 `docker-compose.yml`
- [ ] 创建 `.dockerignore` 文件

#### 任务 3.2：配置开发环境
- [ ] 配置数据卷挂载（data/、uploads/、templates/）
- [ ] 配置环境变量
- [ ] 测试 `docker-compose up`
- [ ] 验证热重载功能

#### 任务 3.3：文档更新
- [ ] 更新 `CLAUDE.md`（添加新技术栈说明）
- [ ] 更新 `README.md`（添加启动指南）
- [ ] 创建 `docs/API.md`（API 文档）
- [ ] 创建 `docs/DEVELOPMENT.md`（开发指南）

#### 任务 3.4：代码清理
- [ ] 将现有 Node.js 代码移到 `legacy/` 目录
- [ ] 删除不需要的文件（node_modules/、package.json 等）
- [ ] 验证数据文件兼容性（colorMapping.json）

---

## 验收标准

### 功能验收
- [ ] 所有现有功能正常工作
- [ ] 颜色映射 CRUD 功能完整
- [ ] Excel 分析功能准确
- [ ] Excel 处理功能正确（输出与旧系统一致）
- [ ] 文件上传和下载功能正常

### 性能验收
- [ ] 大文件上传（>10MB）不卡顿
- [ ] Excel 处理速度与旧系统相当或更快
- [ ] 前端响应速度 <100ms

### 用户体验验收
- [ ] UI 美观现代
- [ ] 操作流程流畅
- [ ] 错误提示清晰
- [ ] 响应式布局在移动端正常

### 技术验收
- [ ] 代码符合最佳实践
- [ ] TypeScript 无类型错误
- [ ] Python 代码通过 Black 格式化
- [ ] 前端代码通过 ESLint 检查
- [ ] Docker 环境一键启动

---

## 风险和缓解措施

### 风险 1：Excel 处理结果不一致
**缓解措施：**
- 使用相同的测试数据对比新旧系统输出
- 逐个验证每个字段的生成逻辑
- 保留旧系统作为参考

### 风险 2：文件上传性能问题
**缓解措施：**
- 使用 FastAPI 的异步文件上传
- 实现分块上传（如果需要）
- 添加上传进度显示

### 风险 3：前端状态管理复杂
**缓解措施：**
- 使用 React Query 自动管理服务器状态
- 使用 Zustand 简化客户端状态
- 避免过度设计

### 风险 4：Docker 环境配置问题
**缓解措施：**
- 提供详细的启动文档
- 使用 docker-compose 简化配置
- 提供非 Docker 的启动方式作为备选

---

## 时间估算

| 阶段 | 任务数 | 预计时间 | 依赖 |
|------|--------|----------|------|
| 阶段 1：后端迁移 | 15 | 1-2 天 | 无 |
| 阶段 2：前端迁移 | 20 | 2-3 天 | 阶段 1 |
| 阶段 3：Docker 和部署 | 10 | 1 天 | 阶段 1, 2 |
| **总计** | **45** | **4-6 天** | - |

---

## 下一步行动

1. **立即开始：** 阶段 1 - 后端迁移
2. **第一个任务：** 创建 FastAPI 项目结构
3. **验证点：** 完成颜色映射模块后，使用现有前端测试

---

## 备注

- 本计划采用渐进式迁移策略，每个阶段都可以独立验证
- 如果遇到问题，可以随时回退到旧系统
- 数据文件（colorMapping.json）保持兼容，无需迁移
- 模板文件（.xlsm）保持不变，直接复用
