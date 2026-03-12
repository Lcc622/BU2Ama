# 重构计划：分店铺索引 + 输出目录分离 + CLAUDE.md 精简

## 任务 1：精简 CLAUDE.md

### 目标
- 删除过时/冗余内容（旧版 Node.js 架构、详细 API 文档等）
- 保留核心信息：项目概述、技术栈、命令、架构要点
- **必须保留**：用户添加的"codex 实现代码，你 review"规则

### 具体操作
1. 删除以下章节：
   - `## File Structure`（过时的 Node.js 结构）
   - `## Important Implementation Details`（实现细节应该在代码注释里）
   - `## API Endpoints`（详细 API 文档，可以从 FastAPI `/docs` 查看）
   - `## Common Development Patterns`（过于细节）

2. 保留并精简：
   - `## Project Overview`（保留核心功能描述）
   - `## Technology Stack`（保留技术栈列表）
   - `## Commands`（保留启动命令）
   - `## Architecture`（保留目录结构概览，删除详细说明）
   - 用户自定义规则（完整保留）

3. 新增简洁说明：
   - 数据源文件：支持 DM/PZ/EP 三店铺
   - 输出目录：`backend/results/`
   - 索引策略：按店铺分库

---

## 任务 2：输出目录分离

### 目标
将生成的 Excel 文件从 `backend/uploads/` 移到 `backend/results/`，避免与源文件混淆。

### 涉及文件
1. `backend/app/config.py` - 新增 `RESULTS_DIR` 配置
2. `backend/app/core/excel_processor.py` - 修改输出路径
3. `backend/app/core/follow_sell_processor.py` - 修改输出路径
4. `backend/app/api/excel.py` - 修改下载接口路径

### 具体操作
1. **config.py**
   ```python
   RESULTS_DIR = BASE_DIR / "results"
   RESULTS_DIR.mkdir(exist_ok=True)
   ```

2. **excel_processor.py**
   - 搜索所有 `UPLOADS_DIR / f"processed_` 替换为 `RESULTS_DIR / f"processed_`
   - 确保 `export_history.db` 记录的路径也更新

3. **follow_sell_processor.py**
   - 搜索所有 `UPLOADS_DIR / f"followsell_` 替换为 `RESULTS_DIR / f"followsell_`

4. **excel.py**
   - `/api/download/{filename}` 接口改为从 `RESULTS_DIR` 读取
   - 保持向后兼容：先查 `RESULTS_DIR`，找不到再查 `UPLOADS_DIR`（兼容旧文件）

5. **创建目录**
   ```bash
   mkdir -p backend/results
   ```

---

## 任务 3：分店铺索引

### 目标
将单一 `excel_index.db` 拆分为按店铺分库：
- `excel_index_EP.db`
- `excel_index_DM.db`
- `excel_index_PZ.db`

### 设计方案

#### 方案 A：多数据库文件（推荐）
- 优点：物理隔离，不会混淆；查询性能更好
- 缺点：需要根据文件名前缀判断用哪个库

#### 方案 B：单库多表
- 优点：管理简单
- 缺点：需要在所有查询加 `WHERE store_prefix='EP'`

**选择方案 A**

### 涉及文件
1. `backend/app/core/excel_processor.py` - 索引构建和查询逻辑

### 具体操作

1. **识别店铺前缀**
   ```python
   def get_store_prefix(filename: str) -> str:
       """从文件名提取店铺前缀 (EP/DM/PZ)"""
       match = re.match(r'^(EP|DM|PZ)-', filename, re.IGNORECASE)
       return match.group(1).upper() if match else 'EP'  # 默认 EP
   ```

2. **修改索引文件路径**
   ```python
   # 原来：excel_index.db
   # 改为：excel_index_{store}.db

   def get_index_db_path(store_prefix: str) -> Path:
       return UPLOADS_DIR / f"excel_index_{store_prefix}.db"
   ```

3. **修改索引构建逻辑**
   - `build_excel_index()` 函数：
     - 扫描 `backend/uploads/*.xlsm` 和 `*.xlsx`
     - 按文件名前缀分组（EP/DM/PZ）
     - 分别写入对应的 `excel_index_{store}.db`

4. **修改索引查询逻辑**
   - `_find_source_row_from_index()` 函数：
     - 根据请求的 SKU 前缀判断店铺（或从请求参数传入）
     - 打开对应的 `excel_index_{store}.db`
     - 执行查询

5. **处理跨店铺场景**
   - 如果 SKU 前缀无法判断店铺，按优先级查询：EP → DM → PZ
   - 或者要求前端传入 `store_prefix` 参数

6. **兼容性处理**
   - 如果旧的 `excel_index.db` 存在，提示用户重新上传数据源文件
   - 或者提供迁移脚本（可选）

---

## 实施顺序

1. **任务 1：精简 CLAUDE.md**（5 分钟，无风险）
2. **任务 2：输出目录分离**（15 分钟，低风险）
3. **任务 3：分店铺索引**（30 分钟，中风险，需要测试）

---

## 验证清单

### 任务 1
- [ ] CLAUDE.md 文件大小减少 50% 以上
- [ ] 用户自定义规则完整保留
- [ ] 核心信息（技术栈、命令）仍然存在

### 任务 2
- [ ] `backend/results/` 目录已创建
- [ ] 新生成的文件出现在 `results/` 而非 `uploads/`
- [ ] 下载接口能正常下载新文件
- [ ] 旧文件仍可下载（向后兼容）

### 任务 3
- [ ] `excel_index_EP.db`、`excel_index_DM.db`、`excel_index_PZ.db` 已生成
- [ ] 上传 EP 文件只更新 EP 索引
- [ ] 上传 DM 文件只更新 DM 索引
- [ ] 处理请求时能正确查询对应店铺索引
- [ ] 跨店铺场景有明确的回退逻辑

---

## 风险评估

| 任务 | 风险等级 | 潜在问题 | 缓解措施 |
|------|---------|---------|---------|
| 精简 CLAUDE.md | 低 | 误删重要信息 | 先备份，review 时仔细检查 |
| 输出目录分离 | 低 | 旧文件路径失效 | 下载接口保持向后兼容 |
| 分店铺索引 | 中 | 查询逻辑复杂化 | 充分测试三店铺场景 |

---

## 回滚方案

- **任务 1**：恢复 CLAUDE.md 备份
- **任务 2**：改回 `UPLOADS_DIR`，删除 `RESULTS_DIR` 配置
- **任务 3**：删除分店铺索引逻辑，恢复单一 `excel_index.db`
