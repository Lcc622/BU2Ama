# Excel 加色加码功能重构实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 重构 Excel 加色加码功能，支持产品前缀输入、颜色/尺码范围输入、一色多码/一码多色模式，并添加 PZUS 模板支持。

**Architecture:** 保持后端逻辑不变，主要改动前端 UI。前端生成完整的 SKU 列表，通过现有 API 传递给后端处理。后端只需添加 PZUS 模板配置。

**Tech Stack:** React, TypeScript, Zustand, Python, FastAPI

---

## Task 1: 后端添加 PZUS 模板配置

**Files:**
- Modify: `backend/app/config.py:28-36`

**Step 1: 添加 PZUS 配置**

在 `TEMPLATES` 字典中添加 PZUS：

```python
TEMPLATES = {
    "DaMaUS": {
        "image_variant": "PL"  # 使用 -PL1.jpg, -PL2.jpg 等
    },
    "EPUS": {
        "image_variant": "L"   # 使用 -L1.jpg, -L2.jpg 等
    },
    "PZUS": {
        "image_variant": "PL"  # 使用 -PL1.jpg, -PL2.jpg 等（同 DaMaUS）
    }
}
```

**Step 2: 提交更改**

```bash
git add backend/app/config.py
git commit -m "feat: 添加 PZUS 模板配置"
```

---

## Task 2: 更新前端状态管理

**Files:**
- Modify: `frontend/src/store/useProcessStore.ts`

**Step 1: 更新状态接口**

```typescript
interface ProcessState {
  // 新增字段
  productPrefix: string;
  mode: 'add-color' | 'add-code';

  // 加色模式
  targetColor: string | null;
  startSize: string;
  endSize: string;
  sizeStep: number;

  // 加码模式
  targetSize: string;
  colorList: string;

  // 原有字段
  templateType: 'DaMaUS' | 'EPUS' | 'PZUS';
  selectedPrefixes: string[];

  // 新增方法
  setProductPrefix: (prefix: string) => void;
  setMode: (mode: 'add-color' | 'add-code') => void;
  setStartSize: (size: string) => void;
  setEndSize: (size: string) => void;
  setSizeStep: (step: number) => void;
  setColorList: (list: string) => void;
  generateSKUs: () => string[];
}
```

**Step 2: 实现 SKU 生成逻辑**

```typescript
generateSKUs: () => {
  const state = get();
  const { productPrefix, mode, targetColor, startSize, endSize, sizeStep, targetSize, colorList } = state;

  if (!productPrefix || productPrefix.length !== 7) return [];

  if (mode === 'add-color') {
    // 一色多码
    if (!targetColor || !startSize || !endSize) return [];
    const skus: string[] = [];
    for (let size = parseInt(startSize); size <= parseInt(endSize); size += sizeStep) {
      const sizeStr = size.toString().padStart(2, '0');
      skus.push(`${productPrefix}${targetColor}${sizeStr}`);
    }
    return skus;
  } else {
    // 一码多色
    if (!targetSize || !colorList) return [];
    const colors = colorList.split(',').map(c => c.trim().toUpperCase());
    return colors.map(color => `${productPrefix}${color}${targetSize}`);
  }
}
```

**Step 3: 提交更改**

```bash
git add frontend/src/store/useProcessStore.ts
git commit -m "feat: 更新状态管理支持新的加色加码逻辑"
```

---

## Task 3: 重构 ColorSelector 组件

**Files:**
- Modify: `frontend/src/components/ExcelProcess/ColorSelector.tsx`

**Step 1: 重写组件结构**

```typescript
export function ColorSelector() {
  const {
    productPrefix,
    setProductPrefix,
    mode,
    setMode,
    targetColor,
    setTargetColor,
    startSize,
    setStartSize,
    endSize,
    setEndSize,
    sizeStep,
    setSizeStep,
    targetSize,
    setTargetSize,
    colorList,
    setColorList,
    generateSKUs,
    setSelectedPrefixes
  } = useProcessStore();

  const { data: mappings } = useQuery({
    queryKey: ['mappings'],
    queryFn: mappingApi.getAll,
  });

  const [previewSKUs, setPreviewSKUs] = useState<string[]>([]);

  // 实时更新预览
  useEffect(() => {
    const skus = generateSKUs();
    setPreviewSKUs(skus);
    setSelectedPrefixes(skus);
  }, [productPrefix, mode, targetColor, startSize, endSize, sizeStep, targetSize, colorList]);

  return (
    <div className="space-y-4">
      {/* 产品前缀输入 */}
      <div>
        <label className="text-sm font-medium text-gray-700">产品前缀</label>
        <input
          type="text"
          value={productPrefix}
          onChange={(e) => setProductPrefix(e.target.value.toUpperCase())}
          placeholder="ES0128B"
          maxLength={7}
          className="w-full px-3 py-2 border rounded-md"
        />
        {productPrefix && productPrefix.length !== 7 && (
          <p className="text-xs text-red-600 mt-1">产品前缀必须是7位字符</p>
        )}
      </div>

      {/* 处理模式选择 */}
      <div>
        <label className="text-sm font-medium text-gray-700">处理模式</label>
        <div className="flex gap-4 mt-2">
          <label className="flex items-center">
            <input
              type="radio"
              checked={mode === 'add-color'}
              onChange={() => setMode('add-color')}
              className="mr-2"
            />
            加色（一色多码）
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              checked={mode === 'add-code'}
              onChange={() => setMode('add-code')}
              className="mr-2"
            />
            加码（一码多色）
          </label>
        </div>
      </div>

      {/* 加色模式 */}
      {mode === 'add-color' && (
        <>
          {/* 颜色选择 */}
          <div>
            <label className="text-sm font-medium text-gray-700">颜色</label>
            <input
              list="colors"
              value={targetColor || ''}
              onChange={(e) => setTargetColor(e.target.value.toUpperCase())}
              placeholder="输入或选择颜色代码"
              className="w-full px-3 py-2 border rounded-md"
            />
            <datalist id="colors">
              {Object.entries(mappings || {}).map(([code, name]) => (
                <option key={code} value={code}>{code} - {name}</option>
              ))}
            </datalist>
          </div>

          {/* 尺码范围 */}
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="text-sm font-medium text-gray-700">起始尺码</label>
              <input
                type="text"
                value={startSize}
                onChange={(e) => setStartSize(e.target.value)}
                placeholder="02"
                maxLength={2}
                className="w-full px-3 py-2 border rounded-md"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">结束尺码</label>
              <input
                type="text"
                value={endSize}
                onChange={(e) => setEndSize(e.target.value)}
                placeholder="08"
                maxLength={2}
                className="w-full px-3 py-2 border rounded-md"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">步长</label>
              <input
                type="number"
                value={sizeStep}
                onChange={(e) => setSizeStep(parseInt(e.target.value) || 2)}
                min={2}
                step={2}
                className="w-full px-3 py-2 border rounded-md"
              />
            </div>
          </div>
        </>
      )}

      {/* 加码模式 */}
      {mode === 'add-code' && (
        <>
          {/* 尺码选择 */}
          <div>
            <label className="text-sm font-medium text-gray-700">尺码</label>
            <input
              list="sizes"
              value={targetSize}
              onChange={(e) => setTargetSize(e.target.value)}
              placeholder="输入或选择尺码"
              maxLength={2}
              className="w-full px-3 py-2 border rounded-md"
            />
            <datalist id="sizes">
              {Array.from({ length: 15 }, (_, i) => {
                const size = ((i + 1) * 2).toString().padStart(2, '0');
                return <option key={size} value={size}>{size}</option>;
              })}
            </datalist>
          </div>

          {/* 颜色列表 */}
          <div>
            <label className="text-sm font-medium text-gray-700">颜色列表</label>
            <input
              type="text"
              value={colorList}
              onChange={(e) => setColorList(e.target.value)}
              placeholder="BE, BK, DG（逗号分隔）"
              className="w-full px-3 py-2 border rounded-md"
            />
            <p className="text-xs text-gray-500 mt-1">多个颜色用逗号分隔</p>
          </div>
        </>
      )}

      {/* SKU 预览 */}
      {previewSKUs.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded p-3">
          <p className="text-sm font-medium text-blue-900 mb-2">
            将生成 {previewSKUs.length} 个 SKU：
          </p>
          <p className="text-xs text-blue-700 font-mono">
            {previewSKUs.slice(0, 10).join(', ')}
            {previewSKUs.length > 10 && ` ... 等 ${previewSKUs.length} 个`}
          </p>
        </div>
      )}
    </div>
  );
}
```

**Step 2: 提交更改**

```bash
git add frontend/src/components/ExcelProcess/ColorSelector.tsx
git commit -m "feat: 重构 ColorSelector 支持新的交互方式"
```

---

## Task 4: 更新 TemplateSelector 添加 PZUS

**Files:**
- Modify: `frontend/src/components/ExcelProcess/TemplateSelector.tsx`

**Step 1: 添加 PZUS 选项**

在模板选择中添加 PZUS：

```typescript
<label className="flex items-center">
  <input
    type="radio"
    name="template"
    value="PZUS"
    checked={templateType === 'PZUS'}
    onChange={() => setTemplateType('PZUS')}
    className="mr-2"
  />
  PZUS
</label>
```

**Step 2: 提交更改**

```bash
git add frontend/src/components/ExcelProcess/TemplateSelector.tsx
git commit -m "feat: 添加 PZUS 模板选项"
```

---

## Task 5: 测试和验证

**Step 1: 测试加色模式**

1. 输入产品前缀：`ES0128B`
2. 选择"加色（一色多码）"
3. 输入颜色：`BE`
4. 输入尺码范围：起始 `02`，结束 `08`，步长 `2`
5. 验证预览显示：`ES0128BBE02, ES0128BBE04, ES0128BBE06, ES0128BBE08`
6. 上传文件并生成 Excel
7. 验证生成的文件包含正确的 SKU

**Step 2: 测试加码模式**

1. 输入产品前缀：`ES0128B`
2. 选择"加码（一码多色）"
3. 输入尺码：`02`
4. 输入颜色列表：`BE, BK, DG`
5. 验证预览显示：`ES0128BBE02, ES0128BBK02, ES0128BDG02`
6. 上传文件并生成 Excel
7. 验证生成的文件包含正确的 SKU

**Step 3: 测试 PZUS 模板**

1. 选择 PZUS 模板
2. 执行加色或加码操作
3. 验证生成的 Excel 使用 `-PL` 图片格式

**Step 4: 边界测试**

1. 测试产品前缀长度验证
2. 测试尺码范围无效情况（起始>结束）
3. 测试颜色代码格式验证
4. 测试生成大量 SKU（>100）的警告

---

## Task 6: 提交最终代码

**Step 1: 检查所有更改**

```bash
git status
git diff
```

**Step 2: 最终提交**

```bash
git add -A
git commit -m "feat: 完成 Excel 加色加码功能重构

- 支持产品前缀手动输入
- 支持颜色/尺码输入+下拉选择
- 支持一色多码和一码多色模式
- 添加 PZUS 模板支持
- 实时 SKU 预览
- 完善输入验证"
```

---

## 验收清单

- [ ] 产品前缀输入正常工作
- [ ] 颜色支持输入和下拉选择
- [ ] 尺码范围能正确生成尺码列表
- [ ] 加色模式生成正确的 SKU
- [ ] 加码模式生成正确的 SKU
- [ ] PZUS 模板正常工作
- [ ] 实时预览显示正确
- [ ] 输入验证完善
- [ ] 错误提示清晰
- [ ] 用户体验流畅
