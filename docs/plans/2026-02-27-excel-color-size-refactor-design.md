# Excel 加色加码功能重构设计文档

## 文档信息
- **创建日期**: 2026-02-27
- **功能名称**: Excel 加色加码功能重构
- **版本**: 1.0
- **状态**: 设计完成，待实现

## 一、需求概述

### 当前问题
1. 加色和加码是分开的两个独立操作
2. 产品前缀只能下拉选择，不能手动输入
3. 颜色和尺码只能下拉选择，不支持输入
4. 缺少 PZUS 模板支持

### 新需求
1. 支持同时加色加码（一色多码 / 一码多色）
2. 产品前缀改为手动输入
3. 颜色和尺码支持输入+下拉选择（Combobox）
4. 尺码支持范围输入（起始-结束+步长）
5. 加码模式支持多个颜色（逗号分隔）
6. 新增 PZUS 模板（规则同 DaMaUS）
7. 去掉颜色分布显示

## 二、实现方案

### 方案选择：方案 A - 最小改动方案

**核心思路**：在现有代码基础上扩展，保持后端逻辑不变，主要改动前端 UI

**改动范围**：
- 后端：只需在 `config.py` 添加 PZUS 配置
- 前端：重构 `ColorSelector.tsx`，更新状态管理

**优点**：
- 改动最小，风险低
- 复用现有的 Excel 处理逻辑
- 快速上线

## 三、整体架构

### 数据流
```
用户输入产品前缀 (ES0128B) + 颜色 (BE) + 尺码范围 (02-08, 步长2)
    ↓
前端生成目标 SKU 列表 (ES0128BBE02, ES0128BBE04, ES0128BBE06, ES0128BBE08)
    ↓
调用现有的 /api/process 接口
    ↓
后端使用现有逻辑处理
    ↓
返回生成的 Excel 文件
```

### 改动总结
**去掉**：
- 产品前缀下拉选择
- 颜色分布显示

**保留**：
- 模板类型选择（DaMaUS/EPUS/PZUS）
- 处理模式选择（加色/加码）

**改进**：
- 产品前缀改为输入框
- 颜色选择支持输入+下拉
- 尺码支持范围输入（起始-结束+步长）
- 加码模式支持多个颜色（逗号分隔）

## 四、前端 UI 设计

### ColorSelector 组件重构

**新的 UI 结构**：
```
产品前缀: [ES0128B        ] (输入框)

处理模式:
  ○ 加色（一色多码）  ○ 加码（一码多色）

模板类型:
  ○ DaMaUS  ○ EPUS  ○ PZUS

[如果选择"加色（一色多码）"]
  颜色: [BE ▼] (Combobox: 可输入或下拉选择)
  起始尺码: [02]  结束尺码: [08]  步长: [2]

  预览: 将生成 ES0128BBE02, ES0128BBE04, ES0128BBE06, ES0128BBE08

[如果选择"加码（一码多色）"]
  尺码: [02 ▼] (Combobox: 可输入或下拉选择)
  颜色列表: [BE, BK, DG] (输入框，逗号分隔，带提示)

  预览: 将生成 ES0128BBE02, ES0128BBK02, ES0128BDG02
```

### 关键交互
1. **产品前缀验证**：输入时实时验证长度（必须7位）
2. **颜色 Combobox**：支持输入颜色代码或从下拉选择，输入时自动匹配
3. **尺码范围计算**：输入起始/结束/步长后，实时显示将生成的尺码列表
4. **SKU 预览**：根据输入实时显示将生成的 SKU 列表（最多显示前 10 个）

## 五、状态管理

### useProcessStore 更新
```typescript
interface ProcessState {
  // 新增字段
  productPrefix: string;           // 产品前缀 (如 ES0128B)
  mode: 'add-color' | 'add-code';  // 处理模式

  // 加色模式
  targetColor: string | null;      // 目标颜色
  startSize: string;               // 起始尺码
  endSize: string;                 // 结束尺码
  sizeStep: number;                // 步长

  // 加码模式
  targetSize: string;              // 目标尺码
  colorList: string;               // 颜色列表 (逗号分隔)

  // 保持原有
  templateType: 'DaMaUS' | 'EPUS' | 'PZUS';
  selectedPrefixes: string[];      // 改为存储生成的 SKU 列表
}
```

### SKU 生成逻辑（前端）
```typescript
// 加色模式：一色多码
function generateAddColorSKUs(prefix, color, startSize, endSize, step) {
  const skus = [];
  for (let size = parseInt(startSize); size <= parseInt(endSize); size += step) {
    const sizeStr = size.toString().padStart(2, '0');
    skus.push(`${prefix}${color}${sizeStr}`);
  }
  return skus;
}

// 加码模式：一码多色
function generateAddCodeSKUs(prefix, size, colorList) {
  const colors = colorList.split(',').map(c => c.trim());
  return colors.map(color => `${prefix}${color}${size}`);
}
```

## 六、后端改动

### config.py
只需添加 PZUS 配置：
```python
TEMPLATES = {
    "DaMaUS": {"image_variant": "PL"},
    "EPUS": {"image_variant": "L"},
    "PZUS": {"image_variant": "PL"}  # 新增，规则同 DaMaUS
}
```

### 其他后端代码
完全保持不变，复用现有的 Excel 处理逻辑。

## 七、输入验证规则

1. **产品前缀**：必须7位字符，字母+数字组合
2. **颜色代码**：2位大写字母，自动转大写
3. **尺码**：2位数字，必须是偶数（02, 04, 06...）
4. **步长**：必须是偶数（2, 4, 6...）
5. **颜色列表**：逗号分隔，每个颜色2位字母

## 八、错误处理

- 产品前缀格式错误 → 红色提示
- 尺码范围无效（起始>结束）→ 禁用生成按钮
- 颜色代码不存在 → 黄色警告（仍可继续）
- 生成的 SKU 数量过多（>100）→ 警告提示

## 九、用户体验优化

1. **实时预览**：输入时立即显示将生成的 SKU
2. **智能提示**：颜色输入时显示匹配的颜色列表
3. **快捷操作**：常用尺码范围快捷按钮（02-08, 02-12, 02-16）
4. **历史记录**：记住上次使用的产品前缀和设置

## 十、兼容性

- 保持与现有 `/api/process` 接口完全兼容
- 生成的 SKU 列表通过 `selectedPrefixes` 参数传递
- 后端无需感知前端的改动

## 十一、实现步骤

1. 后端：添加 PZUS 配置
2. 前端：更新 useProcessStore 状态管理
3. 前端：重构 ColorSelector 组件
4. 前端：更新 TemplateSelector 添加 PZUS 选项
5. 测试：验证各种输入组合
6. 文档：更新用户使用说明

## 十二、风险和注意事项

### 技术风险
1. **输入验证复杂度**：需要处理多种输入格式和边界情况
2. **SKU 生成逻辑**：确保生成的 SKU 格式正确

### 解决方案
1. 完善的输入验证和错误提示
2. 充分的单元测试和集成测试
3. 实时预览帮助用户确认生成结果

## 十三、验收标准

### 功能验收
- [ ] 能正确输入产品前缀
- [ ] 颜色支持输入和下拉选择
- [ ] 尺码范围能正确生成尺码列表
- [ ] 加色模式能生成正确的 SKU
- [ ] 加码模式能生成正确的 SKU
- [ ] PZUS 模板能正常工作
- [ ] 实时预览显示正确

### 性能验收
- [ ] 输入响应流畅（< 100ms）
- [ ] SKU 生成快速（< 500ms）

### 代码质量验收
- [ ] 代码符合项目规范
- [ ] 类型提示完整
- [ ] 错误处理完善
- [ ] 用户体验流畅
