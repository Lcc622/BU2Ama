# BU2Ama Excel 颜色加色系统 v2.0

Excel SKU 颜色映射和处理系统 - Python (FastAPI) + React (TypeScript) 版本

## 技术栈

### 后端
- **Python 3.11+**
- **FastAPI** - 现代化的 Web 框架
- **openpyxl** - Excel 文件处理
- **Pydantic** - 数据验证
- **Uvicorn** - ASGI 服务器

### 前端
- **React 18** - UI 框架
- **TypeScript** - 类型安全
- **Vite** - 构建工具
- **Tailwind CSS** - 样式框架
- **React Query** - 服务器状态管理
- **Zustand** - 客户端状态管理
- **Axios** - HTTP 客户端

## 快速开始

### 方式 1：使用 Docker Compose（推荐）

```bash
# 启动所有服务
docker-compose up

# 访问应用
# 前端：http://localhost:5173
# 后端 API：http://localhost:8000
# API 文档：http://localhost:8000/docs
```

### 方式 2：手动启动

#### 启动后端

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动服务器
python -m app.main

# 或使用 uvicorn
uvicorn app.main:app --reload
```

后端将运行在 http://localhost:8000

#### 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将运行在 http://localhost:5173

## 项目结构

```
BU2Ama/
├── backend/                    # Python FastAPI 后端
│   ├── app/
│   │   ├── api/               # API 路由
│   │   │   ├── mapping.py     # 颜色映射 API
│   │   │   └── excel.py       # Excel 处理 API
│   │   ├── core/              # 核心业务逻辑
│   │   │   ├── color_mapper.py
│   │   │   └── excel_processor.py
│   │   ├── models/            # Pydantic 数据模型
│   │   ├── config.py          # 配置管理
│   │   └── main.py            # FastAPI 应用入口
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                   # React + TypeScript 前端
│   ├── src/
│   │   ├── components/        # React 组件
│   │   ├── services/          # API 调用
│   │   ├── store/             # Zustand 状态管理
│   │   ├── types/             # TypeScript 类型
│   │   ├── lib/               # 工具函数
│   │   └── App.tsx
│   ├── package.json
│   └── Dockerfile
│
├── data/                       # 数据文件
│   └── colorMapping.json      # 颜色映射数据
├── uploads/                    # 上传文件目录
├── 加色模板.xlsm               # DaMaUS 模板
├── EP-ES01840FL-加色-Coco-2.4新表.xlsm  # EPUS 模板
└── docker-compose.yml         # Docker 编排配置
```

## 功能说明

### 1. 颜色映射管理
- 查看所有颜色代码映射
- 搜索颜色映射
- 添加/编辑颜色映射
- 删除颜色映射
- 批量导入颜色映射

### 2. Excel 文件处理
- 上传 Excel 文件
- 分析 SKU 分布和颜色统计
- 识别未知颜色代码
- 选择 SKU 前缀进行过滤
- 选择模板类型（DaMaUS 或 EPUS）
- 生成新的 Excel 文件
- 下载处理后的文件

### 3. SKU 格式
系统支持以下 SKU 格式：
- `EG02230LV14-DA` - 标准格式
- `EE0164ABK10` - 无后缀格式

格式说明：
- 产品代码：7-8 个字符（如 `EG02230`）
- 颜色代码：2 个大写字母（如 `LV`）
- 尺码：2 位数字（如 `14`）
- 后缀：可选，以 `-` 开头（如 `-DA`）

## API 文档

启动后端后，访问 http://localhost:8000/docs 查看完整的 API 文档（Swagger UI）。

### 主要 API 端点

#### 颜色映射
- `GET /api/mapping` - 获取所有映射
- `GET /api/mapping/search?keyword=xxx` - 搜索映射
- `POST /api/mapping` - 添加/更新映射
- `DELETE /api/mapping/{code}` - 删除映射

#### Excel 处理
- `GET /api/templates` - 列出可用模板
- `POST /api/analyze` - 分析上传的文件
- `POST /api/process` - 处理 Excel 文件
- `GET /api/download/{filename}` - 下载生成的文件
- `GET /api/files` - 列出已上传文件
- `DELETE /api/files/{filename}` - 删除文件

## 开发指南

### 后端开发

```bash
cd backend

# 安装开发依赖
pip install -r requirements.txt

# 代码格式化
black app/
isort app/

# 运行测试（如果有）
pytest
```

### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器（热重载）
npm run dev

# 代码格式化
npm run format

# 类型检查
npm run type-check

# 构建生产版本
npm run build
```

## 环境变量

### 后端 (.env)
```
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:5173
```

### 前端 (.env)
```
VITE_API_URL=http://localhost:8000
```

## 数据迁移

从旧版本（Node.js）迁移到新版本：

1. **颜色映射数据**：`data/colorMapping.json` 文件格式保持不变，无需迁移
2. **模板文件**：直接使用现有的 `.xlsm` 模板文件
3. **上传文件**：`uploads/` 目录中的文件可以继续使用

## 故障排除

### 后端无法启动
- 检查 Python 版本（需要 3.11+）
- 确保所有依赖已安装：`pip install -r requirements.txt`
- 检查端口 8000 是否被占用

### 前端无法启动
- 检查 Node.js 版本（需要 18+）
- 删除 `node_modules` 并重新安装：`rm -rf node_modules && npm install`
- 检查端口 5173 是否被占用

### CORS 错误
- 确保后端的 `CORS_ORIGINS` 环境变量包含前端地址
- 检查前端的 `VITE_API_URL` 是否正确

### Excel 处理失败
- 确保模板文件存在且路径正确
- 检查上传的文件格式（支持 .xlsx, .xlsm, .xls）
- 查看后端日志获取详细错误信息

## 性能优化

- 后端使用异步文件处理，支持大文件上传
- 前端使用 React Query 自动缓存 API 响应
- 使用 Vite 构建，支持快速热重载
- Docker 镜像使用多阶段构建，减小体积

## 贡献指南

1. Fork 项目
2. 创建功能分支：`git checkout -b feature/new-feature`
3. 提交更改：`git commit -am 'Add new feature'`
4. 推送到分支：`git push origin feature/new-feature`
5. 提交 Pull Request

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue。
