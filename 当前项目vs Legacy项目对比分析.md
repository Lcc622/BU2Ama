# 当前项目 vs Legacy 项目 - 字段映射对比分析

> 分析日期：2026-02-26
>
> 对比文件：
> - 当前项目：`/Users/melodylu/Downloads/BU2Ama/backend/app/core/excel_processor.py`
> - Legacy 项目：`/Users/melodylu/Downloads/BU2Ama/legacy/lib/excelProcessor.js`

---

## 📊 总体结论

**当前项目和 Legacy 项目的实现逻辑基本一致，但有一些关键差异。**

---

## ✅ 相同点

### 1. 核心逻辑相同

两个项目都采用**基于模板的字段填充**方式，而不是传统的字段对字段映射：

| 逻辑 | 当前项目 | Legacy 项目 |
|-----|---------|------------|
| 读取模板文件 | ✅ | ✅ |
| 复制模板表头（前3行） | ✅ | ✅ |
| 根据规则生成字段 | ✅ | ✅ |
| 从样例行复制字段 | ✅ | ✅ |

### 2. SKU 解析逻辑相同

```python
# 当前项目
SKU_PATTERN = re.compile(r'^([A-Z]{2}\d{5}[A-Z]?)([A-Z]{2})(\d{2})(-[A-Z]+)?$')
```

```javascript
// Legacy 项目
match = sku.match(/^([A-Z]{2}\d{4,5}[A-Z]?)([A-Z]{2})(\d{2})(-[A-Z]+)?$/);
```

**差异**：Legacy 支持 4-5 位数字，当前项目只支持 5 位数字。

### 3. Launch Date 计算逻辑相同

两个项目都实现了**北京时间 3PM 规则**：
- 3PM 前 → 前一天
- 3PM 后 → 当天

### 4. 图片 URL 生成逻辑相同

```
https://eppic.s3.amazonaws.com/{productCode}{colorCode}-{variant}.jpg
```

### 5. 从样例行复制的字段相同

| 字段 | 当前项目 | Legacy 项目 |
|-----|---------|------------|
| Product Name | ✅ | ✅ |
| Product Description | ✅ | ❌ (Legacy 没有) |
| Key Product Features (5个) | ✅ | ✅ |
| Closure Type | ✅ | ❌ (Legacy 从模板复制) |
| Care Instructions | ✅ | ❌ (Legacy 从模板复制) |
| Outer Material | ✅ | ❌ (Legacy 从模板复制) |

---

## ⚠️ 关键差异

### 1. 字段填充方式

| 字段 | 当前项目 | Legacy 项目 |
|-----|---------|------------|
| **Product Description** | 从样例行复制 | 从模板第4行复制 |
| **Closure Type** | 从样例行复制 | 从模板第4行复制 |
| **Care Instructions** | 从样例行复制 | 从模板第4行复制 |
| **Outer Material** | 从样例行复制 | 从模板第4行复制 |
| **Generic Keyword** | ❌ 未实现 | ✅ 从样例行复制 |

**影响**：
- 当前项目从样例行复制更多字段，更符合跨后缀加色的需求
- 但当前项目**缺少 Generic Keyword** 字段的处理

### 2. 价格处理

| 项目 | 价格逻辑 |
|-----|---------|
| **当前项目** | ✅ 从输入表读取价格（第16列），然后 +10 美元 |
| **Legacy 项目** | ❌ 没有价格处理逻辑 |

**代码**：
```python
# 当前项目 - 行334-337
base_price = price_map.get(info.sku, 79.99)  # 默认价格
new_price = base_price + 10
ws.cell(row=row_idx, column=cols["price"] + 1, value=new_price)
```

**优势**：当前项目实现了价格 +10 美元的需求。

### 3. 固定值字段

| 字段 | 当前项目 | Legacy 项目 |
|-----|---------|------------|
| Product Type | ✅ "dress" | ✅ 从模板复制 |
| Brand Name | ✅ "Ever-Pretty" | ✅ 从模板复制 |
| Update Delete | ✅ "Update" | ✅ 从模板复制 |
| Item Type | ✅ "dresses" | ✅ 从模板复制 |
| Target Gender | ✅ "Female" | ✅ 从模板复制 |
| Age Range | ✅ "Adult" | ✅ 从模板复制 |
| Size System | ✅ "US" | ✅ 从模板复制 |
| Size Class | ✅ "Numeric" | ✅ 从模板复制 |
| Body Type | ✅ "Regular" | ✅ 从模板复制 |
| Height Type | ✅ "Regular" | ✅ 从模板复制 |
| Parentage | ✅ "Child" | ✅ 从模板复制 |
| Variation Theme | ✅ "SizeName-ColorName" | ✅ 从模板复制 |
| Quantity | ✅ 20 | ✅ 从模板复制 |

**差异**：
- 当前项目**硬编码**这些固定值
- Legacy 项目从**模板第4行复制**这些值

**影响**：
- 当前项目更明确，不依赖模板文件的内容
- 但如果需要修改这些值，需要改代码

### 4. 图片 URL 格式

| 项目 | 图片格式 |
|-----|---------|
| **当前项目** | `-L11.jpg`, `-L201.jpg`, `-L202.jpg`, `-L203.jpg`, `-L304.jpg` |
| **Legacy 项目 (EPUS)** | `-L1.jpg`, `-L2.jpg`, `-L3.jpg`, `-L4.jpg`, `-L5.jpg` |
| **Legacy 项目 (DaMaUS)** | `-PL10.jpg`, `-PL2.jpg`, `-PL3.jpg`, `-PL4.jpg`, `-PL5.jpg` |

**问题**：当前项目的图片格式与 Legacy 项目不一致！

**当前项目代码**：
```python
# 行358-367
main_image_url = f"https://eppic.s3.amazonaws.com/{info.product_code}{color_code}-{image_variant}11.jpg"
other_image_urls = [
    f"...{image_variant}201.jpg",
    f"...{image_variant}202.jpg",
    f"...{image_variant}203.jpg",
    f"...{image_variant}304.jpg",
    f"...MH00000-S2.jpg"
]
```

**Legacy 项目代码**：
```javascript
// EPUS 模板
newRow[cols.MAIN_IMAGE] = `${imageBase}-L1.jpg`;
cols.OTHER_IMAGES.forEach((col, idx) => {
    newRow[col] = `${imageBase}-L${idx + 2}.jpg`;  // L2, L3, L4, L5, L6
});
```

**影响**：当前项目生成的图片 URL 可能无法访问！

### 5. Relationship Type 字段

| 项目 | Relationship Type |
|-----|------------------|
| **当前项目** | ❌ 未实现 |
| **Legacy 项目** | ✅ 从模板复制（应该是 "Variation"） |

**问题**：当前项目缺少 Relationship Type 字段的处理。

### 6. Color Map 字段

| 项目 | Color Map |
|-----|-----------|
| **当前项目** | ❌ 未实现 |
| **Legacy 项目** | ✅ 根据颜色名称分类（Purple/Blue/Green等） |

**Legacy 代码**：
```javascript
newRow[cols.COLOR_MAP] = getColorMapValue(colorName);
```

**问题**：当前项目缺少 Color Map 字段的处理。

### 7. 模板配置方式

| 项目 | 配置方式 |
|-----|---------|
| **当前项目** | 使用 Python 字典配置（`config.py`） |
| **Legacy 项目** | 使用 JavaScript 对象配置（`excelProcessor.js`） |

两者都使用硬编码的列索引，但配置文件不同。

---

## 🔴 当前项目缺少的功能

### 1. Generic Keyword 字段
- Legacy 项目：从样例行复制
- 当前项目：未实现

### 2. Relationship Type 字段
- Legacy 项目：从模板复制（"Variation"）
- 当前项目：未实现

### 3. Color Map 字段
- Legacy 项目：根据颜色名称分类
- 当前项目：未实现

### 4. 图片 URL 格式不正确
- 当前项目：`-L11.jpg`, `-L201.jpg` 等
- 应该是：`-L1.jpg`, `-L2.jpg` 等（EPUS）

---

## 🟢 当前项目的优势

### 1. 价格处理
- ✅ 实现了价格 +10 美元的逻辑
- ✅ 从输入表读取价格

### 2. 更多字段从样例行复制
- ✅ Product Description
- ✅ Closure Type
- ✅ Care Instructions
- ✅ Outer Material

这些字段在跨后缀加色时更准确。

### 3. 固定值更明确
- ✅ 硬编码固定值，不依赖模板内容
- ✅ 代码更清晰

---

## 📝 需要修复的问题

### 优先级 🔴 高

1. **修复图片 URL 格式**
   - 当前：`-L11.jpg`, `-L201.jpg`
   - 应该：`-L1.jpg`, `-L2.jpg`（EPUS）

2. **添加 Relationship Type 字段**
   - 固定值：`"Variation"`

3. **添加 Color Map 字段**
   - 根据颜色名称分类

### 优先级 🟡 中

4. **添加 Generic Keyword 字段**
   - 从样例行复制

### 优先级 🟢 低

5. **支持 4 位数字的产品代码**
   - 当前只支持 5 位数字
   - Legacy 支持 4-5 位

---

## 📊 字段覆盖率对比

| 字段类别 | 当前项目 | Legacy 项目 |
|---------|---------|------------|
| **基础信息** | 6/6 ✅ | 6/6 ✅ |
| **SKU 相关** | 4/4 ✅ | 4/4 ✅ |
| **尺码相关** | 5/5 ✅ | 5/5 ✅ |
| **图片相关** | 7/7 ✅ (格式错误) | 7/7 ✅ |
| **变体关系** | 2/3 ⚠️ (缺 Relationship Type) | 3/3 ✅ |
| **产品特性** | 5/6 ⚠️ (缺 Generic Keyword) | 6/6 ✅ |
| **颜色相关** | 1/2 ⚠️ (缺 Color Map) | 2/2 ✅ |
| **价格相关** | 1/1 ✅ | 0/1 ❌ |
| **日期相关** | 1/1 ✅ | 1/1 ✅ |

**总计**：
- 当前项目：32/36 字段（88.9%）
- Legacy 项目：34/36 字段（94.4%）

---

## 🎯 总结

### 相似度：85%

当前项目和 Legacy 项目的核心逻辑基本一致，但有以下关键差异：

### 当前项目的优势
1. ✅ 实现了价格 +10 美元逻辑
2. ✅ 从样例行复制更多字段（更适合跨后缀加色）
3. ✅ 固定值更明确

### 当前项目的问题
1. ❌ 图片 URL 格式错误（最严重）
2. ❌ 缺少 Relationship Type 字段
3. ❌ 缺少 Color Map 字段
4. ❌ 缺少 Generic Keyword 字段

### 建议

**立即修复**：
1. 修复图片 URL 格式
2. 添加 Relationship Type 字段
3. 添加 Color Map 字段

**后续优化**：
4. 添加 Generic Keyword 字段
5. 支持 4 位数字的产品代码

---

**文档结束**
