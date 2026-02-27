# 当前项目 vs 钉钉最新字段映射对比

> 对比日期：2026-02-26
>
> 参考文件：对比(1).xlsx - Sheet1
>
> 总字段数：87个

---

## 📊 总体对比结果

### 实现状态统计

| 状态 | 数量 | 百分比 |
|-----|------|--------|
| ✅ 已实现 | 45 | 51.7% |
| ⚠️ 部分实现 | 15 | 17.2% |
| ❌ 未实现 | 27 | 31.0% |

---

## ✅ 已正确实现的字段 (45个)

### 基础信息
- Product Type ← Product Type (保留 "dress")
- Seller SKU ← SKU (颜色/尺码变更) ✅
- Brand Name ← Brand Name (替换 "Ever-Pretty") ✅
- Update Delete ← 非映射 (保留 "Update") ✅
- Product Name ← Item Name (颜色/尺码变更) ✅
- Product Description ← Product Description (颜色/尺码变更) ✅
- Item Type Keyword ← Item Type Keyword (保留 "dresses") ✅
- Style Number ← SKU (颜色/尺码变更) ✅
- Manufacturer Part Number ← SKU (颜色/尺码变更) ✅

### 产品属性
- Closure Type ← Closure Type (替换) ✅
- Care instructions ← Care instructions (替换) ✅
- Outer Material Type ← Material (替换) ✅
- Target Gender ← Target Gender (保留 "Female") ✅
- Age Range Description ← Age Range Description (保留 "Adult") ✅

### 尺码系统
- Apparel Size System ← Apparel Size System (保留 "US") ✅
- Apparel Size Class ← Apparel Size Class (保留 "Numeric") ✅
- Apparel Size Value ← Apparel Size Value (替换) ✅
- Apparel Size Body Type ← Apparel Size Body Type (保留 "Regular") ✅
- Apparel Size Height Type ← Apparel Size Height Type (保留 "Regular") ✅
- Size ← Size (替换) ✅

### 图片 URL
- Main Image URL ← Main Image URL (已修复格式) ✅
- Other Image URL (5个) ← Other Image URL (已修复格式) ✅
- Swatch Image URL ← Swatch Image URL (已修复格式) ✅

### 变体关系
- Parentage ← 非映射 (固定 "Child") ✅
- Parent SKU ← Parent SKU (替换) ✅
- Relationship Type ← 非映射 (保留 "Variation") ✅
- Variation Theme ← Variation Theme Name (替换) ✅

### 产品特性
- Key Product Features (5个) ← Key Product Features (替换) ✅
- Generic Keyword ← Generic Keywords (剔除颜色) ✅

### 颜色相关
- Color ← Color (替换) ✅
- Colour Map ← 非映射 (加色用加的颜色) ✅

### 其他属性
- Pattern ← Pattern (保留) ✅
- Launch Date ← 非映射 (3pm前T-1，后T) ✅

---

## ⚠️ 部分实现/需要调整的字段 (15个)

### 1. Your Price ⚠️
- **钉钉要求**：← Your Price USD (替换) from All Listing Report
- **当前实现**：从输入表读取价格 + 10
- **问题**：应该直接替换，不是 +10
- **优先级**：🔴 高

### 2. Quantity ⚠️
- **钉钉要求**：← 非映射 (默认数字5)
- **当前实现**：固定值 20
- **问题**：应该是 5，不是 20
- **优先级**：🔴 高

### 3. 图片 URL 规则 ⚠️
- **钉钉要求**：根据店铺和后缀不同使用不同规则
  - EP店铺 + 非PH后缀：L1-5，尺码图：EG02088-S-US
  - EP店铺 + PH后缀：L101-5，尺码图：EG02088-S-US
  - PZ/DAMA店铺 + 非PH后缀：PL1-5，尺码图：EG02088-S-PLUS-US
  - PZ/DAMA店铺 + PH后缀：PL101-5，尺码图：EG02088-S-PLUS-US
- **当前实现**：简单的 L1-5 或 PL1-5
- **问题**：缺少 PH 后缀的特殊处理（L101-5 / PL101-5）
- **优先级**：🔴 高

### 4. List Price ⚠️
- **钉钉要求**：← List Price ("+10")
- **当前实现**：未实现
- **优先级**：🟡 中

### 5. Business Price ⚠️
- **钉钉要求**：← 非映射 (standard_price-1)
- **当前实现**：未实现
- **优先级**：🟡 中

### 6. Quantity Price (3个) ⚠️
- **钉钉要求**：
  - Quantity Price = Business Price * 0.95
  - Quantity Price 2 = Business Price * 0.92
  - Quantity Price 3 = Business Price * 0.90
- **当前实现**：未实现
- **优先级**：🟡 中

### 7-15. 其他部分实现的字段
- Style Name, Department, Height, Width, Length
- Package Weight Unit Of Measure
- Cpsia Warning, Battery相关字段
- Material/Fabric Regulations

---

## ❌ 未实现的字段 (27个)

### 产品属性
- Material type ← Material (保留)
- NeckStyle ← Neck Style (替换)
- Seasons ← Seasons (替换)
- Apparel Silhouette ← Apparel Silhouette (替换)
- Pattern Style ← Pattern (替换)
- Embellishment Feature ← Embellishment Feature (替换)
- Sleeve Type ← Sleeve Type (替换)
- Size Map ← Size (替换)
- item_length_description ← Item Length Description (替换)
- Fabric Type ← Fabric Type (替换)
- Import Designation ← Import Designation (保留)
- Waist Style ← Waist Style (替换)
- Back Style ← Back Style (替换)

### 场合类型
- Occasion Type (5个) ← Occasion Type (保留)
- Occasion Lifestyle (7个) ← Occasion Lifestyle (保留)

### 包装信息
- Package Length Unit Of Measure ← Package Length Unit Of Measure (保留)
- Package Weight ← Package Weight (保留)

### 合规性
- Dangerous Goods Regulations ← Dangerous Goods Regulations (保留)

---

## 🔴 关键差异和需要修复的问题

### 1. 价格逻辑错误 🔴 高优先级

**钉钉要求**：
```
Your Price = 从 All Listing Report 直接替换（不是 +10）
List Price = Your Price + 10
Business Price = Your Price - 1
Quantity Price = Business Price * 0.95
Quantity Price 2 = Business Price * 0.92
Quantity Price 3 = Business Price * 0.90
```

**当前实现**：
```python
base_price = price_map.get(info.sku, 79.99)
new_price = base_price + 10  # ❌ 错误：应该直接使用 base_price
ws.cell(row=row_idx, column=cols["price"] + 1, value=new_price)
```

**修复**：
```python
# Your Price (standard_price)
your_price = price_map.get(info.sku, 79.99)
ws.cell(row=row_idx, column=cols["price"] + 1, value=your_price)

# List Price = Your Price + 10
list_price = your_price + 10
ws.cell(row=row_idx, column=cols["list_price"] + 1, value=list_price)

# Business Price = Your Price - 1
business_price = your_price - 1
ws.cell(row=row_idx, column=cols["business_price"] + 1, value=business_price)

# Quantity Prices
ws.cell(row=row_idx, column=cols["quantity_price"] + 1, value=business_price * 0.95)
ws.cell(row=row_idx, column=cols["quantity_price_2"] + 1, value=business_price * 0.92)
ws.cell(row=row_idx, column=cols["quantity_price_3"] + 1, value=business_price * 0.90)
```

### 2. Quantity 默认值错误 🔴 高优先级

**钉钉要求**：默认值 5

**当前实现**：
```python
ws.cell(row=row_idx, column=cols["quantity"] + 1, value=20)  # ❌ 错误
```

**修复**：
```python
ws.cell(row=row_idx, column=cols["quantity"] + 1, value=5)  # ✅ 正确
```

### 3. 图片 URL 规则不完整 🔴 高优先级

**钉钉要求**：PH 后缀使用特殊格式

**当前实现**：
```python
# 只有简单的 L1-5 或 PL1-5
main_image_url = f"...{image_variant}1.jpg"
```

**修复**：
```python
# 根据后缀判断
if suffix == "-PH":
    # PH 后缀使用 L101-105 或 PL101-105
    main_image_url = f"...{image_variant}101.jpg"
    other_urls = [f"...{image_variant}10{i}.jpg" for i in range(2, 6)]
else:
    # 非 PH 后缀使用 L1-5 或 PL1-5
    main_image_url = f"...{image_variant}1.jpg"
    other_urls = [f"...{image_variant}{i}.jpg" for i in range(2, 6)]

# 尺码图也需要根据店铺类型添加
# EP: EG02088-S-US
# PZ/DAMA: EG02088-S-PLUS-US
```

### 4. 缺少大量字段 🟡 中优先级

需要添加的字段配置和实现：
- NeckStyle, Seasons, Apparel Silhouette
- Pattern Style, Embellishment Feature, Sleeve Type
- Size Map, item_length_description
- Fabric Type, Waist Style, Back Style
- Occasion Type (5个), Occasion Lifestyle (7个)
- 等等...

---

## 📝 字段映射规则总结

### 规则类型

1. **保留**：使用固定值或模板值，不变更
2. **替换**：从输入表对应字段复制
3. **颜色/尺码变更**：根据加色加码逻辑生成
4. **计算**：根据公式计算（价格、日期等）
5. **非映射**：使用固定值或默认值

### 特殊处理字段

| 字段 | 处理逻辑 |
|-----|---------|
| Seller SKU | 颜色/尺码变更 |
| Product Name | 颜色/尺码变更 |
| Product Description | 颜色/尺码变更 |
| Generic Keyword | 剔除与颜色不相关的部分 |
| Colour Map | 加色用加的颜色，加码映射 |
| 图片 URL | 根据店铺和后缀使用不同规则 |
| Your Price | 从 All Listing Report 替换 |
| List Price | Your Price + 10 |
| Business Price | Your Price - 1 |
| Quantity Price | Business Price * 0.95/0.92/0.90 |
| Launch Date | 3pm前T-1，后T |
| Quantity | 默认值 5 |

---

## 🎯 修复优先级

### 🔴 高优先级（立即修复）

1. **修复价格逻辑**
   - Your Price 不应该 +10
   - 添加 List Price, Business Price, Quantity Price 计算

2. **修复 Quantity 默认值**
   - 从 20 改为 5

3. **完善图片 URL 规则**
   - 添加 PH 后缀的特殊处理（L101-105）
   - 添加尺码图

### 🟡 中优先级（后续优化）

4. **添加缺失的字段**
   - NeckStyle, Seasons, Apparel Silhouette 等
   - Occasion Type, Occasion Lifestyle 等

5. **完善字段映射**
   - 确保所有 87 个字段都正确映射

---

## 📊 实现进度

| 类别 | 已实现 | 总数 | 完成度 |
|-----|--------|------|--------|
| 基础信息 | 9/9 | 9 | 100% |
| 产品属性 | 4/17 | 17 | 23.5% |
| 尺码系统 | 6/6 | 6 | 100% |
| 图片 URL | 7/7 | 7 | 100% (需调整) |
| 变体关系 | 4/4 | 4 | 100% |
| 产品特性 | 6/6 | 6 | 100% |
| 颜色相关 | 2/2 | 2 | 100% |
| 场合类型 | 0/12 | 12 | 0% |
| 价格相关 | 1/6 | 6 | 16.7% |
| 包装信息 | 0/5 | 5 | 0% |
| 合规性 | 0/6 | 6 | 0% |
| 其他 | 6/7 | 7 | 85.7% |
| **总计** | **45/87** | **87** | **51.7%** |

---

## 📝 建议

### 立即行动

1. 修复价格逻辑（Your Price, List Price, Business Price, Quantity Price）
2. 修复 Quantity 默认值（20 → 5）
3. 完善图片 URL 规则（PH 后缀特殊处理）

### 后续优化

4. 添加配置文件中缺失的字段索引
5. 实现所有 87 个字段的映射逻辑
6. 测试验证所有字段的正确性

---

**文档结束**
