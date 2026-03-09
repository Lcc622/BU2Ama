# BU2Ama Listing Operations Skill 设计方案

## 设计日期
2026-03-09

## 目标
将 BU2Ama 项目的"加色加码"和"跟卖"功能打包成 Claude Code skill，集成到 OpenClaw + Telegram 环境，支持对话式操作和文件上传。

## 用户需求
- **使用场景**：通过 Telegram 对话窗口与 Claude 交互
- **核心功能**：
  1. 加色加码：处理 SKU 数据与颜色映射，生成加色后的 Excel
  2. 跟卖：通过 SKC 查询尺码分布
  3. 源文件管理：上传/更新 EP/DM/PZ 数据源
- **交互方式**：自动化执行 + 开发指导
- **环境假设**：运行在 BU2Ama 项目目录下

## Codex 分析要点

### 可行性评估
✅ **适合做成 skill**
- 输入明确、流程重复、业务规则脆弱
- 依赖固定文件和索引
- 典型的"让 agent 少踩坑"场景

### 关键发现
1. **两个功能已部分耦合**：`excel_processor.py` 中有 `follow_sell_mode` 参数
2. **共享大量依赖**：店铺识别、索引规则、路径检查、文件契约
3. **配置已确认**：
   - 颜色映射：`backend/data/colorMapping.json` ✅
   - 跟卖映射：`backend/uploads/新老款映射信息(1).xlsx` ✅（实际使用位置）

### 推荐结构
- **一个伞形 skill**：`bu2ama-listing-ops`
- **混合模式**：70% 流程型 + 30% 工具型
- **不复制业务逻辑**：skill 调用现有项目代码

## 设计方案

### 1. Skill 结构

```
~/.claude/skills/bu2ama-listing-ops/
├── SKILL.md                          # 主 skill 说明（触发条件、流程指导）
├── scripts/
│   ├── check_env.py                  # 环境预检（路径、依赖、文件）
│   ├── add_color_size.py             # 加色加码 CLI 入口
│   ├── follow_sell.py                # 跟卖 CLI 入口
│   └── upload_source.py              # 源文件上传处理
├── references/
│   ├── store-rules.md                # 店铺规则（EP/DM/PZ 映射、前缀归一化）
│   ├── file-contracts.md             # 文件格式约定（模板、源文件、映射表）
│   ├── troubleshooting.md            # 常见问题排查（索引重建、路径错误）
│   └── telegram-integration.md       # Telegram 集成指南
└── examples/
    ├── add-color-example.md          # 加色加码对话示例
    └── follow-sell-example.md        # 跟卖对话示例
```

### 2. SKILL.md 核心内容

#### 触发条件（Triggers）
**加色加码**：
- "加色加码"
- "生成加色 Excel"
- "根据模板补 SKU"
- "按 EP/DM/PZ 模板出表"
- "颜色映射"、"SKU 批量处理"

**跟卖**：
- "跟卖"
- "查 SKC 尺码"
- "新老款映射"
- "按店铺查尺码分布"
- "follow sell"、"follow-sell"

**源文件管理**：
- "上传 EP 源"、"更新 DM 数据"
- "重建索引"
- "检查数据源"

#### 执行流程
```
1. 环境检查
   ├─ 确认当前目录是 BU2Ama 项目
   ├─ 检查 Python 环境和依赖（openpyxl）
   ├─ 验证必需文件存在
   └─ 检查店铺索引状态

2. 识别任务类型
   ├─ 加色加码 → 调用 add_color_size.py
   ├─ 跟卖 → 调用 follow_sell.py
   └─ 源文件管理 → 调用 upload_source.py

3. 参数收集
   ├─ 店铺类型（EP/DM/PZ）
   ├─ 输入文件（模板/SKC 列表）
   └─ 输出要求

4. 执行处理
   ├─ 调用对应脚本
   ├─ 监控执行状态
   └─ 捕获错误信息

5. 结果返回
   ├─ 生成结果文件路径
   ├─ 处理统计信息
   └─ 错误/警告提示
```

### 3. 脚本设计

#### check_env.py
```python
"""
环境预检脚本
返回 JSON 格式的检查结果
"""
{
    "valid": true/false,
    "project_root": "/path/to/BU2Ama",
    "python_version": "3.x.x",
    "dependencies": {
        "openpyxl": "installed",
        "fastapi": "installed"
    },
    "files": {
        "color_mapping": "exists",
        "follow_sell_mapping": "exists",
        "templates": ["EPUS", "DaMaUS", "PZUS"]
    },
    "indexes": {
        "EP": "exists",
        "DM": "exists",
        "PZ": "missing"
    },
    "warnings": [],
    "errors": []
}
```

#### add_color_size.py
```python
"""
加色加码 CLI 入口
调用 backend/app/core/excel_processor.py
"""
# 参数：
# --template: 模板文件名
# --store: 店铺类型（EP/DM/PZ）
# --sources: 源文件列表
# --price-report: 价格报告（可选）
# --output: 输出路径

# 返回 JSON：
{
    "success": true/false,
    "output_file": "/path/to/result.xlsx",
    "processed_count": 123,
    "skipped_count": 5,
    "errors": [],
    "warnings": []
}
```

#### follow_sell.py
```python
"""
跟卖 CLI 入口
调用 backend/app/core/follow_sell_processor.py
"""
# 参数：
# --skc-list: SKC 列表文件或直接输入
# --store: 店铺类型（EP/DM/PZ）
# --output: 输出路径

# 返回 JSON：
{
    "success": true/false,
    "results": [
        {
            "skc": "ES01819NT",
            "old_style": "ES01234",
            "sizes": ["S", "M", "L"],
            "source_files": ["EP-0.xlsm"]
        }
    ],
    "not_found": ["ES99999XX"],
    "errors": []
}
```

#### upload_source.py
```python
"""
源文件上传处理
支持从 Telegram 接收文件
"""
# 参数：
# --file: 上传的文件路径
# --store: 店铺类型（自动识别或手动指定）
# --rebuild-index: 是否重建索引

# 返回 JSON：
{
    "success": true/false,
    "file_saved": "/path/to/uploads/EP-3.xlsm",
    "store": "EP",
    "index_rebuilt": true,
    "sku_count": 1234,
    "errors": []
}
```

### 4. Telegram 集成要点

#### 文件上传流程
```
用户 → Telegram → OpenClaw → Claude Code → upload_source.py → backend/uploads/
```

#### 对话示例
```
用户: 帮我上传这个 EP 源文件
[上传 EP-3.xlsm]

Claude: 收到文件，正在处理...
- 文件类型：EP 店铺数据源
- 文件大小：2.3 MB
- 保存位置：backend/uploads/EP-3.xlsm
- 索引重建：完成
- SKU 数量：1,234

用户: 现在帮我生成加色 Excel，模板是 EPUS

Claude: 开始加色加码处理...
- 店铺：EP
- 模板：EPUS
- 数据源：EP-0.xlsm, EP-1.xlsm, EP-2.xlsm, EP-3.xlsm
- 处理完成：123 个 SKU
- 输出文件：backend/results/EPUS_colored_20260309_123456.xlsx

[返回文件]
```

### 5. 项目改造需求

#### 必需改造
1. **统一 CLI 入口**
   - 创建 `backend/app/cli/` 目录
   - 实现 `add_color_size.py`、`follow_sell.py`、`upload_source.py`
   - 统一 JSON 输出格式

2. **配置文件统一**
   - 确认 `colorMapping.json` vs `color_mapping.json`
   - 统一跟卖映射文件名（当前硬编码为 `新老款映射信息(1).xlsx`）

3. **提取共享店铺上下文**
   - 店铺归一化逻辑（DA → DM）
   - 索引路径生成
   - 源文件解析规则

#### 可选改造
1. **增强错误处理**
   - 统一异常类型
   - 详细错误信息

2. **日志记录**
   - 操作日志
   - 审计追踪

### 6. 实施步骤

#### 阶段 1：基础设施（1-2 天）
- [ ] 创建 skill 目录结构
- [ ] 编写 SKILL.md 草稿
- [ ] 实现 check_env.py

#### 阶段 2：CLI 封装（2-3 天）
- [ ] 创建 backend/app/cli/ 目录
- [ ] 实现 add_color_size.py CLI
- [ ] 实现 follow_sell.py CLI
- [ ] 实现 upload_source.py CLI
- [ ] 统一 JSON 输出格式

#### 阶段 3：Skill 完善（1-2 天）
- [ ] 完善 SKILL.md（触发条件、流程、示例）
- [ ] 编写 references/ 文档
- [ ] 创建 examples/ 示例

#### 阶段 4：集成测试（2-3 天）
- [ ] 本地测试 skill 调用
- [ ] OpenClaw 集成测试
- [ ] Telegram 端到端测试
- [ ] 文件上传/下载测试

#### 阶段 5：优化迭代（持续）
- [ ] 收集使用反馈
- [ ] 优化触发条件
- [ ] 补充常见问题
- [ ] 性能优化

## 技术决策

### 为什么是一个 skill 而不是两个？
- 共享依赖太多（店铺规则、索引规则、路径检查）
- 避免重复维护
- 两个功能已经在代码层面耦合（`follow_sell_mode`）

### 为什么是混合模式（流程型 + 工具型）？
- 关键风险在前置检查（路径、模板、索引、映射文件）
- Excel/SQLite 操作需要确定性，必须下沉到脚本
- Telegram 环境需要稳定的输入输出格式

### 为什么不把业务逻辑复制进 skill？
- Skill 不是源码镜像
- 业务逻辑变化频繁，维护成本高
- 应该依赖项目现有环境和代码

## 风险与对策

### 风险 1：配置文件不一致
**影响**：skill 无法找到正确的映射文件
**对策**：
- 先统一配置文件命名
- check_env.py 检查文件存在性
- 提供清晰的错误提示

### 风险 2：Telegram 文件传输限制
**影响**：大文件无法上传
**对策**：
- 检查文件大小限制
- 提供分片上传方案
- 支持云存储链接

### 风险 3：索引重建耗时
**影响**：用户等待时间长
**对策**：
- 异步处理 + 进度反馈
- 增量索引更新
- 缓存优化

### 风险 4：错误信息不友好
**影响**：用户无法自助排查
**对策**：
- 统一错误码和消息
- 提供 troubleshooting.md
- 常见问题自动诊断

## 成功标准

### 功能完整性
- ✅ 支持加色加码完整流程
- ✅ 支持跟卖查询完整流程
- ✅ 支持源文件上传和索引重建
- ✅ 支持三店铺（EP/DM/PZ）

### 易用性
- ✅ Telegram 对话触发成功率 > 90%
- ✅ 错误提示清晰易懂
- ✅ 平均响应时间 < 30 秒

### 可维护性
- ✅ 文档完整（SKILL.md + references/）
- ✅ 代码结构清晰（CLI 分离）
- ✅ 测试覆盖充分

## 下一步行动

1. **确认配置统一**：检查并统一 `colorMapping.json` 和跟卖映射文件名
2. **创建 CLI 目录**：`backend/app/cli/`
3. **实现环境检查**：`check_env.py`
4. **编写 SKILL.md 草稿**
5. **本地测试验证**

## 附录

### 参考文件
- `backend/app/core/excel_processor.py` - 加色加码核心逻辑
- `backend/app/core/follow_sell_processor.py` - 跟卖核心逻辑
- `backend/app/config.py` - 配置管理
- `backend/scripts/test_store_index_isolation.py` - 测试脚本

### 相关文档
- `docs/plans/2026-03-04-amazon-listing-automation-phase0.md` - P0 阶段计划
- `task_plan.md` - 当前任务计划
- `findings.md` - 技术发现
