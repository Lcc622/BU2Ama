# Legacy 项目字段映射分析报告

> 分析日期：2026-02-26
>
> 分析文件：/Users/melodylu/Downloads/BU2Ama/legacy/lib/excelProcessor.js

---

## 📋 发现的映射关系

### Legacy 项目的映射逻辑

Legacy 项目**没有使用传统的字段对字段映射**，而是采用了**基于模板的字段填充**方式。

### 核心逻辑

1. **读取模板文件**（加色模板.xlsm 或 EP新表.xlsm）
2. **复制模板的表头**（前3行）
3. **使用模板的第4行作为数据行模板**
4. **根据业务规则填充特定字段**

---

## 🔧 字段填充规则

### 1. 硬编码的列索引

Legacy 项目使用**硬编码的列索引**来定位字段：

#### DaMaUS 模板列索引
```javascript
{
    SKU: 1,                    // 列 B
    PRODUCT_NAME: 4,           // 列 E
    STYLE_NUMBER: 10,          // 列 K
    MPN: 18,                   // 列 S
    SIZE_VALUE: 27,            // 列 AB
    MAIN_IMAGE: 31,            // 列 AF
    OTHER_IMAGES: [32, 33, 34, 35],  // 列 AG-AJ
    SWATCH_IMAGE: 40,          // 列 AO
    PARENT_SKU: 42,            // 列 AQ
    COLOR: 56,                 // 列 BE
    COLOR_MAP: 57,             // 列 BF
    SIZE: 66,                  // 列 BO
    SIZE_MAP: 121,             // 列 DS
    KEY_FEATURES: [89, 90, 91, 92, 93],  // 列 CL-CP
    GENERIC_KEYWORD: 94,       // 列 CQ
    LAUNCH_DATE: 275           // 列 JW
}
```

#### EPUS 模板列索引
```javascript
{
    SKU: 1,                    // 列 B
    PRODUCT_NAME: 4,           // 列 E
    STYLE_NUMBER: 9,           // 列 J
    MPN: 12,                   // 列 M
    SIZE_VALUE: 29,            // 列 AD
    MAIN_IMAGE: 72,            // 列 BU
    OTHER_IMAGES: [73, 74, 75, 76, 77],  // 列 BV-BZ
    SWATCH_IMAGE: 81,          // 列 CD
    PARENT_SKU: 83,            // 列 CF
    KEY_FEATURES: [89, 90, 91, 92, 93],  // 列 CL-CP
    GENERIC_KEYWORD: 94,       // 列 CQ
    COLOR_MAP: 111,            // 列 DH
    COLOR: 135,                // 列 EF
    SIZE: 152,                 // 列 EW
    SIZE_MAP: 298,             // 列 KP
    LAUNCH_DATE: 531           // 列 TG
}
```

### 2. 字段填充逻辑

#### A. 直接生成的字段

| 字段 | 生成规则 | 代码位置 |
|-----|---------|---------|
| **Seller SKU** | `productCode + colorCode + size + suffix` | 行432 |
| **Style Number** | 与 SKU 相同 | 行437 |
| **Manufacturer Part Number** | 与 SKU 相同 | 行438 |
| **Parent SKU** | `productCode + suffix` | 行446 |
| **Apparel Size Value** | 从 SKU 提取的 size | 行441 |
| **Size** | 从 SKU 提取的 size | 行442 |
| **Size Map** | 从 SKU 提取的 size | 行443 |
| **Color** | 从颜色映射表获取颜色名称 | 行451 |
| **Colour Map** | 根据颜色名称分类（Purple/Blue/Green等） | 行452 |
| **Launch Date** | 根据北京时间3PM规则计算 | 行523 |

#### B. 从样例行复制的字段

| 字段 | 复制来源 | 处理方式 | 代码位置 |
|-----|---------|---------|---------|
| **Product Name** | 样例行的 Product Name | 替换颜色词和尺码 | 行457-486 |
| **Key Product Features** (5个) | 样例行的 Bullet Points | 直接复制 | 行489-495 |
| **Generic Keyword** | 样例行的 Generic Keyword | 直接复制 | 行498-500 |

**样例行选择规则**：
1. 优先选择：同产品代码 + 同后缀的行（`productCode + suffix`）
2. 备选：同后缀的任意行（`suffix`）
3. 目的：确保 Product Name、Key Features、Generic Keyword 与目标后缀一致

#### C. 根据规则生成的字段

| 字段 | 生成规则 | 代码位置 |
|-----|---------|---------|
| **Main Image URL** | `https://eppic.s3.amazonaws.com/{productCode}{colorCode}-L1.jpg` (EPUS) | 行507 |
| | `https://eppic.s3.amazonaws.com/{productCode}{colorCode}-PL10.jpg` (DaMaUS) | 行513 |
| **Other Image URL** (5个) | EPUS: `-L2.jpg`, `-L3.jpg`, `-L4.jpg`, `-L5.jpg`, `-L6.jpg` | 行508-510 |
| | DaMaUS: `-PL2.jpg`, `-PL3.jpg`, `-PL4.jpg`, `-PL5.jpg` | 行514-517 |
| **Swatch Image URL** | 与 Main Image URL 相同 | 行511/518 |

#### D. 从模板行复制的字段

**所有其他字段**都从模板的第4行复制：
```javascript
const newRow = templateRow.length > 0 ? [...templateRow] : new Array(600).fill('');
```

这意味着：
- Brand Name
- Product Type
- Update Delete
- Item Type Keyword
- Closure Type
- Care instructions
- Target Gender
- Age Range Description
- Apparel Size System
- Apparel Size Class
- Apparel Size Body Type
- Apparel Size Height Type
- Relationship Type
- Variation Theme
- 以及所有其他字段

都是**直接从模板文件的第4行复制**，不做任何修改。

---

## 🔍 关键发现

### 1. 没有输入表到输出表的字段映射

Legacy 项目**不从输入表复制字段值**，而是：
- 从输入表**只提取 SKU 信息**（产品代码、颜色代码、尺码、后缀）
- 从输入表**只复制样例行的特定字段**（Product Name、Key Features、Generic Keyword）
- 其他所有字段都**从模板文件复制**

### 2. 模板文件是数据源

模板文件（加色模板.xlsm 或 EP新表.xlsm）的**第4行**包含了所有字段的默认值：
- Brand Name = "Ever-Pretty"
- Product Type = "dress"
- Update Delete = "Update"
- Relationship Type = "Variation"
- 等等...

### 3. 跨后缀加色的实现

Legacy 项目通过**样例行选择**实现跨后缀加色：

```javascript
// 优先选择同产品代码+同后缀的样例行
const suffixKey = `${target.productCode}${suffix}`;
const sampleRow = suffixSampleRows.get(suffixKey) ||
                  suffixSampleRows.get(suffix) ||
                  [];
```

这样可以确保：
- Product Name 来自目标后缀的样例
- Key Features 来自目标后缀的样例
- Generic Keyword 来自目标后缀的样例

### 4. 价格字段缺失

Legacy 项目**没有处理价格字段**（Your Price、List Price等），这些字段：
- 要么从模板文件的第4行复制（可能是空值或示例值）
- 要么需要手动填充

---

## 📊 与对比表格的差异

### 对比表格的映射关系

对比表格（对比.xlsx）显示的是**输入表字段到输出表字段的映射**，例如：
- 输出表的 "Seller SKU" ← 输入表的 "Title"
- 输出表的 "Brand Name" ← 输入表的 "SKU"

### Legacy 项目的实际逻辑

Legacy 项目**不使用这种映射关系**，而是：
- Seller SKU = 根据规则生成（不从输入表的任何字段复制）
- Brand Name = 从模板文件的第4行复制（不从输入表复制）

### 结论

**对比表格的映射关系与 Legacy 项目的实际实现不一致**。

可能的原因：
1. 对比表格是**理想的映射关系**，但尚未实现
2. 对比表格是**另一个版本**的映射关系
3. 对比表格是**错误的**或**过时的**

---

## 💡 建议

### 1. 确认映射关系的来源

需要确认：
- 对比表格是否是最新的需求文档？
- Legacy 项目的实现是否符合业务需求？
- 是否需要按照对比表格重新实现映射逻辑？

### 2. 如果采用对比表格的映射

需要重写整个字段映射逻辑：
- 从输入表读取字段值
- 根据对比表格的映射关系填充输出表
- 处理特殊字段（固定值、计算字段）

### 3. 如果保持 Legacy 逻辑

需要：
- 确保模板文件的第4行包含正确的默认值
- 补充价格字段的处理逻辑
- 完善跨后缀加色的样例行选择逻辑

---

## 📝 总结

| 项目 | 映射方式 | 数据来源 |
|-----|---------|---------|
| **Legacy 项目** | 基于模板 + 规则生成 | 模板文件第4行 + 样例行 + 计算 |
| **对比表格** | 字段对字段映射 | 输入表字段 |

**两者完全不同！**

---

**文档结束**
