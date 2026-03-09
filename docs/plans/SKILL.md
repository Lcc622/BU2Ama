---
name: bu2ama-listing-ops
description: BU2Ama 电商 SKU 运营工具集，支持加色加码（颜色映射和 SKU 批量处理）和跟卖（新老款映射和尺码查询）功能，适配 EP/DM/PZ 三店铺体系
version: "1.0.0"
triggers:
  - "加色加码"
  - "生成加色 Excel"
  - "根据模板补 SKU"
  - "按 EP/DM/PZ 模板出表"
  - "颜色映射"
  - "SKU 批量处理"
  - "跟卖"
  - "查 SKC 尺码"
  - "新老款映射"
  - "按店铺查尺码分布"
  - "follow sell"
  - "follow-sell"
  - "上传 EP 源"
  - "更新 DM 数据"
  - "重建索引"
  - "检查数据源"
---

# BU2Ama Listing Operations Skill

这个 skill 帮助你在 BU2Ama 项目中执行电商 SKU 运营任务，包括加色加码和跟卖两大核心功能。

## 何时使用这个 Skill

当用户提到以下任何场景时，使用这个 skill：

### 加色加码场景
- 需要根据模板生成加色后的 Excel 文件
- 批量处理 SKU 数据和颜色映射
- 按店铺（EP/DM/PZ）生成不同格式的输出表
- 需要从源文件中查找 SKU 数据并更新模板

### 跟卖场景
- 查询 SKC（7位款号+2位颜色）的尺码分布
- 通过新老款映射查找老款号
- 按店铺查询尺码信息
- 批量处理跟卖 SKC 列表

### 数据管理场景
- 上传或更新店铺源文件（EP-0.xlsm, DM-0.xlsm 等）
- 重建店铺索引
- 检查数据源状态

## 工作流程

### 第 1 步：环境检查

**始终先执行环境检查**，确保项目环境就绪：

```bash
cd /path/to/BU2Ama
python backend/app/cli/check_env.py
```

检查项包括：
- ✅ 当前目录是否是 BU2Ama 项目
- ✅ Python 依赖是否安装（openpyxl, fastapi, pydantic）
- ✅ 必需文件是否存在（颜色映射、跟卖映射）
- ✅ 店铺索引状态（EP/DM/PZ）

**如果检查失败**：
- 引导用户到正确的项目目录
- 提示安装缺失的依赖
- 提示上传缺失的配置文件

### 第 2 步：识别任务类型

根据用户输入，判断任务类型：

#### 加色加码任务
**触发词**：加色加码、生成加色 Excel、根据模板补 SKU、颜色映射

**需要收集的信息**：
1. 店铺类型（EP/DM/PZ）
2. 模板文件名（如 `EPUS模板.xlsx`）
3. 源文件列表（可选，默认自动查找）
4. 价格报告文件（可选）

**执行命令**：
```bash
python backend/app/cli/add_color_size.py \
  --template <模板文件名> \
  --store <EP|DM|PZ> \
  [--sources <源文件1> <源文件2> ...] \
  [--price-report <价格报告>] \
  --json
```

#### 跟卖任务
**触发词**：跟卖、查 SKC 尺码、新老款映射、follow sell

**需要收集的信息**：
1. SKC 列表（7位款号+2位颜色，如 `ES01819NT`）
2. 店铺类型（EP/DM/PZ）

**执行命令**：
```bash
python backend/app/cli/follow_sell.py \
  --skc <SKC1> <SKC2> ... \
  --store <EP|DM|PZ> \
  --json
```

或从文件读取：
```bash
python backend/app/cli/follow_sell.py \
  --skc-file <SKC列表文件> \
  --store <EP|DM|PZ> \
  --json
```

#### 文件上传任务
**触发词**：上传 EP 源、更新 DM 数据、重建索引

**需要收集的信息**：
1. 上传的文件路径
2. 店铺类型（可自动识别）
3. 是否重建索引

**执行命令**：
```bash
python backend/app/cli/upload_source.py \
  --file <文件路径> \
  [--store <EP|DM|PZ>] \
  [--rebuild-index] \
  --json
```

### 第 3 步：执行处理

调用对应的 CLI 脚本，使用 `--json` 参数获取结构化输出。

**监控执行状态**：
- 捕获标准输出（JSON 结果）
- 捕获标准错误（错误信息）
- 检查退出码（0 = 成功，非 0 = 失败）

### 第 4 步：结果处理

#### 成功情况
解析 JSON 输出，向用户报告：
- ✅ 处理完成
- 输出文件路径
- 处理统计（处理数量、跳过数量等）
- 警告信息（如有）

**对于加色加码**：
```json
{
  "success": true,
  "output_file": "/path/to/result.xlsx",
  "processed_count": 123,
  "skipped_count": 5,
  "errors": [],
  "warnings": ["某些 SKU 未找到价格信息"]
}
```

**对于跟卖**：
```json
{
  "success": true,
  "results": [
    {
      "skc": "ES01819NT",
      "old_style": "ES01234",
      "sizes": ["S", "M", "L", "XL"],
      "source_files": ["EP-0.xlsm"]
    }
  ],
  "not_found": ["ES99999XX"],
  "errors": []
}
```

**对于文件上传**：
```json
{
  "success": true,
  "file_saved": "/path/to/uploads/EP-3.xlsm",
  "store": "EP",
  "index_rebuilt": true,
  "sku_count": 1234,
  "errors": []
}
```

#### 失败情况
解析错误信息，提供排查建议：
- ❌ 处理失败
- 错误原因
- 排查步骤（参考 `references/troubleshooting.md`）

### 第 5 步：Telegram 集成特殊处理

当在 Telegram 环境中使用时：

#### 文件上传
1. 接收用户上传的文件
2. 保存到临时位置
3. 调用 `upload_source.py` 处理
4. 返回处理结果

#### 文件下载
1. 执行处理生成结果文件
2. 读取结果文件
3. 通过 Telegram 发送给用户

#### 进度反馈
对于耗时操作（如索引重建），提供进度反馈：
- "正在处理，请稍候..."
- "已处理 50%..."
- "处理完成！"

## 店铺规则

### 店铺前缀映射
- **EP**：EPUS 模板，源文件 `EP-0.xlsm`, `EP-1.xlsm`, `EP-2.xlsm`
- **DM**：DaMaUS 模板，源文件 `DM-0.xlsm`, `DM-1.xlsm`, `DM-2.xlsm` 或 `DA-0.xlsm`（归一化为 DM）
- **PZ**：PZUS 模板，源文件 `PZ-0.xlsm`, `PZ-1.xlsm`, `PZ-2.xlsm`

### 索引库命名
- 加色加码索引：`excel_index_EP.db`, `excel_index_DM.db`, `excel_index_PZ.db`
- 跟卖索引：`ep_index_EP.db`, `ep_index_DM.db`, `ep_index_PZ.db`

### 后缀规则
- EP: `-USA` / `-PH`
- DM: `-PL` / `-PLPH`
- PZ: `-DA` / `-DAPH`

详细规则见 `references/store-rules.md`

## 常见问题排查

### 问题 1：找不到源文件
**症状**：`未找到 EP 店铺的源文件`

**排查步骤**：
1. 检查 `backend/uploads/` 目录
2. 确认文件命名符合规范（`EP-0.xlsm`, `EP-1.xlsm` 等）
3. 如果文件不存在，引导用户上传

### 问题 2：索引库缺失或过期
**症状**：`索引库不存在` 或 `查询结果为空`

**排查步骤**：
1. 检查索引文件是否存在
2. 使用 `--rebuild-index` 重建索引
3. 确认源文件已上传

### 问题 3：颜色映射文件缺失
**症状**：`缺少文件: backend/data/colorMapping.json`

**排查步骤**：
1. 检查 `backend/data/colorMapping.json` 是否存在
2. 如果缺失，从备份恢复或重新创建
3. 确认文件格式正确（JSON）

### 问题 4：跟卖映射文件缺失
**症状**：`缺少文件: backend/data/新老款映射信息(1).xlsx`

**排查步骤**：
1. 检查文件是否存在
2. 确认文件名完全匹配（包括括号和数字）
3. 如果缺失，从备份恢复

更多问题见 `references/troubleshooting.md`

## 文件契约

### 输入文件格式

#### 模板文件
- 格式：`.xlsx` 或 `.xlsm`
- 必需列：SKU, Brand Name, Product Name 等
- 店铺特定：EPUS/DaMaUS/PZUS 模板格式不同

#### 源文件
- 格式：`.xlsm`
- 命名：`{EP|DM|DA|PZ}-{0|1|2}.xlsm`
- 必需列：SKU, Size, Color 等

#### 价格报告
- 格式：`.xlsx`
- 必需列：SKU, Price

#### SKC 列表文件
- 格式：`.txt` 或 `.csv`
- 每行一个 SKC（7位款号+2位颜色）

### 输出文件格式

#### 加色加码结果
- 格式：`.xlsx`
- 命名：`{模板名}_colored_{时间戳}.xlsx`
- 位置：`backend/results/`

#### 跟卖查询结果
- 格式：JSON 或文本
- 包含：SKC, 老款号, 尺码列表, 来源文件

详细格式见 `references/file-contracts.md`

## 示例对话

### 示例 1：加色加码

```
用户: 帮我生成 EPUS 加色表

Claude: 好的，我来帮你生成 EPUS 加色表。

[执行环境检查]
✅ 环境检查通过

请提供模板文件名（如 EPUS模板.xlsx）：

用户: EPUS模板.xlsx

Claude: 收到。正在处理...

[执行 add_color_size.py]

✅ 处理完成！
- 输出文件：backend/results/EPUS模板_colored_20260309_123456.xlsx
- 处理数量：123 个 SKU
- 跳过数量：5 个 SKU（未找到数据）

结果文件已生成，是否需要我发送给你？
```

### 示例 2：跟卖查询

```
用户: 查询 ES01819NT 的尺码

Claude: 好的，我来查询 ES01819NT 的尺码信息。

请选择店铺类型：
A. EP
B. DM
C. PZ

用户: A

Claude: 正在查询 EP 店铺...

[执行 follow_sell.py]

✅ 查询完成！

ES01819NT → ES01234
- 尺码：S, M, L, XL, 2XL
- 来源文件：EP-0.xlsm, EP-1.xlsm
- 老款号：ES01234
```

### 示例 3：文件上传

```
用户: 帮我上传这个 EP 源文件
[上传 EP-3.xlsm]

Claude: 收到文件，正在处理...

[执行 upload_source.py]

✅ 文件上传成功！
- 保存位置：backend/uploads/EP-3.xlsm
- 店铺类型：EP
- 文件大小：2.3 MB

是否需要重建索引？

用户: 是

Claude: 正在重建索引...

✅ 索引重建完成！
- SKU 数量：1,234
- 索引文件：excel_index_EP.db, ep_index_EP.db
```

更多示例见 `examples/` 目录

## 参考文档

- `references/store-rules.md` - 店铺规则详解
- `references/file-contracts.md` - 文件格式约定
- `references/troubleshooting.md` - 常见问题排查
- `references/telegram-integration.md` - Telegram 集成指南

## 维护说明

### 何时更新这个 Skill

- 店铺规则变化（新增店铺、前缀变更）
- 文件格式变化（模板列变更、源文件结构调整）
- 业务逻辑变化（颜色映射规则、SKU 解析规则）
- CLI 接口变化（参数调整、输出格式变更）

### 如何更新

1. 更新 `SKILL.md` 中的触发词和流程
2. 更新 `references/` 中的参考文档
3. 更新 `examples/` 中的示例
4. 测试验证更新后的 skill

## 技术细节

### 依赖的项目代码
- `backend/app/core/excel_processor.py` - 加色加码核心逻辑
- `backend/app/core/follow_sell_processor.py` - 跟卖核心逻辑
- `backend/app/core/color_mapper.py` - 颜色映射
- `backend/app/config.py` - 配置管理

### CLI 脚本位置
- `backend/app/cli/check_env.py` - 环境检查
- `backend/app/cli/add_color_size.py` - 加色加码
- `backend/app/cli/follow_sell.py` - 跟卖
- `backend/app/cli/upload_source.py` - 文件上传

### 数据文件位置
- `backend/data/colorMapping.json` - 颜色映射
- `backend/data/新老款映射信息(1).xlsx` - 跟卖映射
- `backend/uploads/` - 源文件和索引
- `backend/results/` - 输出结果

## 注意事项

1. **始终先执行环境检查**，避免在错误的目录或环境中执行
2. **使用 --json 参数**获取结构化输出，便于解析和处理
3. **捕获错误信息**，提供清晰的排查建议
4. **在 Telegram 环境中**，注意文件大小限制和传输超时
5. **索引重建耗时**，对于大文件提供进度反馈
6. **店铺前缀归一化**，DA 自动归一化为 DM
7. **文件命名规范**，确保符合 `{店铺}-{序号}.xlsm` 格式
