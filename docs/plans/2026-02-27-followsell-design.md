# 亚马逊跟卖自动上新功能设计文档

## 文档信息
- **创建日期**: 2026-02-27
- **功能名称**: 亚马逊跟卖自动上新 (Amazon Follow-Sell Auto-Upload)
- **版本**: 1.0
- **状态**: 设计完成，待实现

## 一、功能概述

### 1.1 目标
在新版本 SKU 入库后，快速完成跟卖上新，实现：
1. 新老版本同时存在购物车
2. 新版本价格低于老版本 $0.1，优先出单
3. 用真实销售测试退货率变化
4. 降低人工制表错误，实现半自动化

### 1.2 核心概念
**跟卖 (Follow-Sell)**: 新 SKU 使用老 SKU 的 ASIN，在同一个产品页面下销售。通过价格差异实现新版本优先出单。

### 1.3 输入输出
- **输入**: 老版本 Excel 文件 + 新产品代码
- **输出**: 新版本 Excel 文件（跟卖上新表）

### 1.4 示例
- 老版本 SKU: `ES01840BD04-PH`
- 新版本 SKU: `ES01846BD04-PH`
- ASIN: `B0DSFV31FT` (保持不变)
- 价格: `79.99` → `79.89` (-0.1)

---

## 二、整体架构

### 2.1 功能定位
在现有 BU2Ama 系统中新增"跟卖上新"功能，作为第三个主要功能模块。

### 2.2 系统流程
```
用户上传老版本 Excel
    ↓
输入新产品代码（如 ES01846）
    ↓
系统处理（替换 SKU、调整价格、更新日期）
    ↓
生成新版本 Excel
    ↓
用户下载
```

### 2.3 技术架构
- **前端**: 新增 `FollowSell` 组件（React + TypeScript）
- **后端**: 新增 `followsell.py` API 路由 + `followsell_processor.py` 处理逻辑
- **复用**: 文件上传、下载、日期计算等现有功能

### 2.4 与现有功能的关系
- **颜色映射**: 独立功能，不相关
- **Excel 处理（加色加码）**: 类似的文件处理流程，可复用大部分代码
- **跟卖上新**: 新功能，独立的 UI 和 API

---

## 三、数据流和核心逻辑

### 3.1 输入数据
1. 老版本 Excel 文件（`.xlsm`/`.xlsx`）
2. 新产品代码（字符串，如 `"ES01846"`）

### 3.2 处理步骤

#### Step 1: 读取老版本 Excel
- 解析所有数据行（从第 4 行开始）
- 提取老产品代码（从第一个 SKU 中识别，如 `ES01840`）

#### Step 2: 字段更新规则（11 个必须修改的字段）

根据 SOP Step 4 的规则：

| # | 字段 | Excel 列名 | 列号 | 规则 |
|---|------|-----------|------|------|
| 1 | item SKU | Seller SKU | 2 | 替换产品代码（ES01840 → ES01846） |
| 2 | product ID | Product ID | 6 | **保持不变**（使用老版本 ASIN，这是跟卖的核心） |
| 3 | product ID type | Product ID Type | 7 | 固定填写 `ASIN` |
| 4 | model style number | Style Number | 10 | 替换产品代码 |
| 5 | part number | Manufacturer Part Number | 13 | 替换产品代码 |
| 6 | price | Your Price | 16 | `old_price - 0.1` |
| 7 | list price | （待确认列名） | TBD | `new_price + 10` |
| 8 | quantity | Quantity | 17 | 固定填写 `0` |
| 9 | image | （所有图片列） | TBD | 清空（设为空字符串） |
| 10 | Release date | Release Date | 521 | 按 3PM 规则计算 |
| 11 | launch date | Launch Date | 533 | 按 3PM 规则计算 |

#### Step 3: 3PM 日期规则
```python
beijing_time = datetime.now(timezone(timedelta(hours=8)))
if beijing_time.hour < 15:  # 15:00 = 3PM
    date = (beijing_time - timedelta(days=1)).date()
else:
    date = beijing_time.date()
```

#### Step 4: 其他所有字段
完全保持不变，包括：
- Product Name
- Brand Name
- Description
- Key Features
- Generic Keyword
- 等等

### 3.3 输出新 Excel
- 保持原有格式和结构
- 文件名：`{原文件名}-跟卖-{timestamp}.xlsx`

### 3.4 错误处理
- 文件格式不正确 → 提示用户
- 无法识别老产品代码 → 提示用户手动输入
- SKU 格式异常 → 跳过该行并记录警告

---

## 四、前端 UI 设计

### 4.1 页面布局
新增"跟卖上新"标签页，与"颜色映射"、"Excel 处理"并列。

### 4.2 UI 组件结构
```
┌─────────────────────────────────────┐
│  跟卖上新                            │
├─────────────────────────────────────┤
│                                     │
│  📤 上传老版本 Excel                 │
│  [选择文件] EP-ES01846-PH-rarity... │
│                                     │
│  ✏️ 输入新产品代码                   │
│  [ES01846        ]                  │
│                                     │
│  ℹ️ 系统将自动：                     │
│  • 识别老产品代码并替换              │
│  • 价格 -0.1 美元                   │
│  • 更新日期（3PM 规则）              │
│  • 清空图片字段                      │
│                                     │
│  [生成跟卖表]                        │
│                                     │
│  ✅ 处理完成！                       │
│  生成了 72 个 SKU                   │
│  [下载新版本 Excel]                  │
└─────────────────────────────────────┘
```

### 4.3 交互流程
1. 用户上传文件 → 显示文件名和 SKU 数量
2. 用户输入新产品代码 → 实时验证格式
3. 点击"生成跟卖表" → 显示加载状态
4. 处理完成 → 显示结果统计和下载按钮

### 4.4 状态管理（Zustand）
```typescript
interface FollowSellState {
  uploadedFile: File | null;
  newProductCode: string;
  processing: boolean;
  result: {
    totalSkus: number;
    outputFilename: string;
  } | null;
}
```

### 4.5 错误提示
- 文件格式错误
- 产品代码格式不正确（需要 7 位字符）
- 处理失败（显示具体错误信息）

---

## 五、后端 API 设计

### 5.1 新增 API 端点

#### `POST /api/followsell/process`

**请求参数**:
```typescript
{
  file: File,              // 老版本 Excel 文件
  newProductCode: string   // 新产品代码，如 "ES01846"
}
```

**响应数据**:
```typescript
{
  success: boolean,
  message: string,
  data: {
    totalSkus: number,           // 处理的 SKU 总数
    oldProductCode: string,      // 识别的老产品代码
    newProductCode: string,      // 新产品代码
    outputFilename: string,      // 生成的文件名
    priceAdjustment: number,     // 价格调整（-0.1）
    dateUsed: string            // 使用的日期
  }
}
```

### 5.2 核心处理函数

#### `app/core/followsell_processor.py`

```python
class FollowSellProcessor:
    def process(self, old_file_path: str, new_product_code: str) -> dict:
        """
        处理跟卖上新逻辑

        Args:
            old_file_path: 老版本 Excel 文件路径
            new_product_code: 新产品代码（如 "ES01846"）

        Returns:
            处理结果字典
        """
        # 1. 读取老版本 Excel
        # 2. 识别老产品代码
        # 3. 遍历所有行，更新字段
        # 4. 生成新 Excel
        # 5. 返回处理结果
```

### 5.3 字段映射配置
```python
FIELD_COLUMNS = {
    'seller_sku': 2,
    'product_id': 6,
    'product_id_type': 7,
    'style_number': 10,
    'manufacturer_part_number': 13,
    'your_price': 16,
    'quantity': 17,
    'release_date': 521,
    'launch_date': 533,
    # 图片列需要找到所有相关列
}
```

### 5.4 错误处理
- `FileNotFoundError`: 文件不存在
- `InvalidFileFormatError`: 文件格式错误
- `ProductCodeNotFoundError`: 无法识别老产品代码
- `ProcessingError`: 处理过程中的其他错误

---

## 六、测试策略

### 6.1 单元测试（后端）

```python
# tests/test_followsell_processor.py

def test_product_code_extraction():
    """测试从 SKU 中提取产品代码"""
    assert extract_product_code("ES01840BD04-PH") == "ES01840"

def test_sku_replacement():
    """测试 SKU 替换逻辑"""
    old_sku = "ES01840BD04-PH"
    new_sku = replace_product_code(old_sku, "ES01840", "ES01846")
    assert new_sku == "ES01846BD04-PH"

def test_price_calculation():
    """测试价格计算"""
    assert calculate_new_price(79.99) == 79.89
    assert calculate_list_price(79.89) == 89.89

def test_date_calculation_before_3pm():
    """测试 3PM 规则（15:00 之前）"""
    # Mock 时间为 14:00
    date = calculate_date(hour=14)
    assert date == yesterday

def test_date_calculation_after_3pm():
    """测试 3PM 规则（15:00 之后）"""
    # Mock 时间为 16:00
    date = calculate_date(hour=16)
    assert date == today
```

### 6.2 集成测试

```python
def test_full_process():
    """测试完整处理流程"""
    result = processor.process(
        old_file="test_old.xlsm",
        new_product_code="ES01846"
    )
    assert result['totalSkus'] == 72
    assert result['oldProductCode'] == "ES01840"

    # 验证生成的文件
    wb = openpyxl.load_workbook(result['outputFilename'])
    sheet = wb.active
    assert sheet.cell(4, 2).value == "ES01846BD04-PH"
    assert sheet.cell(4, 16).value == 79.89
```

### 6.3 手动测试清单
- [ ] 上传正确的 Excel 文件
- [ ] 输入正确的产品代码
- [ ] 验证生成的文件字段正确
- [ ] 测试错误文件格式
- [ ] 测试无效产品代码
- [ ] 测试不同时间的日期计算
- [ ] 验证所有 72 个 SKU 都正确处理

### 6.4 验证标准（对比示例文件）
- SKU 替换正确
- 价格 -0.1
- ASIN 保持不变
- 其他字段不变

---

## 七、实现细节和注意事项

### 7.1 关键实现细节

#### 1. 产品代码识别
```python
def extract_product_code(sku: str) -> str:
    """从 SKU 中提取产品代码（前7位）"""
    # ES01840BD04-PH → ES01840
    main_part = sku.split('-')[0]  # 去掉后缀
    if len(main_part) >= 7:
        return main_part[:7]
    raise ValueError(f"Invalid SKU format: {sku}")
```

#### 2. 图片字段清空
- 需要找到所有包含 "image" 或 "main_image" 的列
- 设置为空字符串或 None
- 可能有多个图片列（main_image_url, other_image_url1-8）

#### 3. list price 列查找
- 需要在 Excel 中找到 "list price" 或 "Suggested Retail Price" 列
- 如果找不到，记录警告但继续处理

#### 4. 日期格式
```python
# Excel 日期格式：2026-02-12 00:00:00
from datetime import datetime, timedelta, timezone

def calculate_launch_date() -> datetime:
    beijing_tz = timezone(timedelta(hours=8))
    now = datetime.now(beijing_tz)
    if now.hour < 15:
        return (now - timedelta(days=1)).replace(hour=0, minute=0, second=0)
    else:
        return now.replace(hour=0, minute=0, second=0)
```

### 7.2 注意事项

1. **文件大小限制**: 复用现有的上传限制（如 50MB）
2. **并发处理**: 使用异步处理，避免阻塞
3. **临时文件清理**: 处理完成后自动清理上传的文件
4. **日志记录**: 记录每次处理的详细信息
   - 处理时间
   - SKU 数量
   - 产品代码替换
   - 任何警告或错误
5. **向后兼容**: 为未来接入 BI 接口预留扩展点

### 7.3 性能考虑
- 72 行数据处理时间 < 2 秒
- 使用 openpyxl 的 `read_only=False` 模式以支持写入
- 避免重复读取文件

---

## 八、实现计划

### 8.1 开发阶段

#### Phase 1: 后端核心逻辑（2-3 小时）
- [ ] 创建 `app/core/followsell_processor.py`
- [ ] 实现产品代码提取和替换逻辑
- [ ] 实现 11 个字段的更新规则
- [ ] 实现 3PM 日期计算
- [ ] 单元测试

#### Phase 2: 后端 API（1 小时）
- [ ] 创建 `app/api/followsell.py`
- [ ] 实现 `/api/followsell/process` 端点
- [ ] 文件上传和下载逻辑
- [ ] 错误处理

#### Phase 3: 前端 UI（2-3 小时）
- [ ] 创建 `frontend/src/components/FollowSell/` 组件
- [ ] 实现文件上传界面
- [ ] 实现产品代码输入和验证
- [ ] 实现处理状态显示
- [ ] 实现下载功能

#### Phase 4: 集成和测试（1-2 小时）
- [ ] 前后端联调
- [ ] 使用示例文件测试
- [ ] 修复 bug
- [ ] 完善错误提示

### 8.2 总预计时间
**6-9 小时**

---

## 九、未来扩展

### 9.1 BI 接口集成
- 自动从 BI 系统获取新老 SKU 对照关系
- 减少人工输入

### 9.2 批量处理
- 支持一次处理多个产品代码
- 生成多个输出文件

### 9.3 历史记录
- 保存处理历史
- 支持重新下载之前生成的文件

---

## 十、参考文档

- [亚马逊跟卖自动上新SOP.md](../../亚马逊跟卖自动上新SOP.md)
- [README.md](../../README.md)
- 示例文件:
  - `EP-ES01846-PH-rarity-老版本表.xlsm`
  - `EP-ES01846-PH跟卖-rarity-新版本.xlsm`
